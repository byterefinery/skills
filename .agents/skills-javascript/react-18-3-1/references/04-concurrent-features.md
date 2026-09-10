# Concurrent features (18.3.1)

React 18 renders as an *interruptible job*: it can pause rendering to handle urgent input and resume. You opt in per update, not per app. The building blocks are priorities, transitions, deferred values, automatic batching, and Suspense.

## Contents

- [Priorities](#priorities)
- [Transitions](#transitions)
- [useDeferredValue](#usedeferredvalue)
- [Automatic batching](#automatic-batching)
- [Strict Mode](#strict-mode)
- [Suspense and data fetching](#suspense-and-data-fetching)
- [useSyncExternalStore](#usesyncexternalstore)
- [useId](#useid)
- [Unstable offscreen primitives](#unstable-offscreen-primitives)

## Priorities

The scheduler maps work to five priorities (values 1–5): `ImmediatePriority` (error recovery), `UserBlockingPriority` (discrete input: click, keydown), `NormalPriority` (continuous input, timeouts), `LowPriority` (background), `IdlePriority`.

- **Urgent updates** (default) — user input must reflect immediately; they preempt transitions.
- **Transitions** — everything else: state changes that re-render larger subtrees (search results, tab content, list filtering).
- `startTransition` and `useTransition` schedule their updates at transition priority; rendering a transition can be interrupted and restarted.

## Transitions

```jsx
const [isPending, startTransition] = useTransition();

startTransition(() => {
  setTab(nextTab);
  setQuery(value);
}, { timeout: 5000 }); // give up after 5s — updates stay pending, no throw
```

- Updates inside `startTransition` are **interruptible**: a newer urgent update (typing) preempts them, and a newer transition supersedes an older one of the same "lane".
- `isPending` is true while any transition from that hook is in flight — drive spinners/skeletons from it.
- `useTransition` must be called in every component that needs the pending state; one `startTransition` can trigger updates in several places, but pending tracking is per-hook.
- Use transitions for: list/search filters, route/tab switches, theme changes, anything that re-renders much of the tree but is not directly tied to a keystroke.
- Don't wrap *urgent* updates (the input's own `setQuery` on a controlled input) in a transition — the input would lag.

## useDeferredValue

```jsx
const deferredQuery = useDeferredValue(query, { timeout: 300 });
const results = useMemo(() => filter(items, deferredQuery), [items, deferredQuery]);
```

- Returns `query` on the first render, then the *previous* value while React works through the urgent render; the deferred render runs right after, interruptible.
- No fixed debounce delay — better than `setTimeout` for keeping the UI responsive.
- Pass `{ timeout }` to bound how long the old value is kept.
- Memoize the expensive consumer, otherwise the deferred value buys nothing (the 18.1 fix for the `useDeferredValue` infinite loop with unmemoized values is in this line).

## Automatic batching

React 18 batches `setState` calls inside: React event handlers, **timeouts, intervals, promises, and native event handlers** (17 only batched React handlers).

- A click handler that calls three `setState`s renders once.
- `flushSync(() => setX())` opts a single update out of batching when the next line reads the DOM.
- Consequence for libraries: code that relied on "one setState per flush" may now see fewer, larger updates — `useSyncExternalStore` (below) is the supported way to read external state.

## Strict Mode

`<StrictMode>` (or `unstable_strictMode` on the root) is **development-only**. In 18 it:

1. Calls each component's render function twice and checks for impurity (same inputs → same output).
2. Runs effect setup → cleanup → setup once on mount, to find missing cleanups.
3. **Unmounts and remounts every component once**, restoring state, to prepare for future state-preservation across unmounts (new in 18.0).

Fixes are always the same: make renders pure, make effect setup idempotent and cleanup thorough, don't cache derived values outside `useMemo`. If the double-mount breaks a component, fix the component — removing StrictMode hides bugs. Console output is no longer suppressed for the second render (18 change); DevTools can grey it out.

## Suspense and data fetching

```jsx
function UserPosts({ user }) {
  const posts = usePosts(user.id); // throws a promise while loading
  return <PostList posts={posts} />;
}

<Suspense fallback={<Skeleton />}>
  <UserPosts user={user} />
</Suspense>
```

- A component "suspends" by throwing a promise; the nearest `<Suspense>` shows its `fallback` (no promise required at the boundary itself).
- 18 semantics: if a tree suspends **before it is fully mounted**, React discards the in-progress tree, waits, and re-renders from scratch — a Suspense boundary is never left in an inconsistent state.
- When content re-appears after re-suspension, **layout effects are cleaned up and re-created** (18 fix) — safe for measurement.
- `fallback={undefined}` behaves like `null` (18 change, not "ignored").
- Multiple boundaries resolve independently; the outer boundary's fallback covers its entire subtree.
- **SuspenseList** coordinates lists of suspending children: `revealOrder="forwards" | "backwards" | "together"` controls reveal order; `tail="collapsed" | "hidden"` hides not-yet-revealed tail items. Only useful when the items share a loading source.
- Fetching pattern without a data library: cache the promise per resource outside the component, `throw` it until resolved, resolve with a stable value. There is no built-in cache in stable 18 (see 07 for experimental RSC caching).

## useSyncExternalStore

```js
const value = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
// subscribe(cb) returns an unsubscribe
```

- The correct way to read external stores (Redux-style, DOM events, WebSockets) without tearing: React forces synchronous reads and re-renders on change.
- `getSnapshot` must return a cached value when nothing changed (`Object.is` compare) or React loops.
- `getServerSnapshot` is required when the component renders on the server; omitting it causes SSR/hydration mismatches.
- Library authors: publish with the `use-sync-external-store` shim for pre-18 React (see 06-ecosystem-packages).
- `useMutableSource` (also exported) is its predecessor and unsupported in stable builds — don't use it.

## useId

`useId()` returns a stable unique string usable for `id`/`aria-*` attributes, matching between server and client. 18.3 fixes `useId` for nested components rendered during streaming SSR (18.0–18.2 could produce collisions/mismatches in that case). Set `identifierPrefix` identically on server and client roots.

## Unstable offscreen primitives

Exported behind the `unstable_` prefix: `unstable_Offscreen` (`mode="hidden"`) keeps a subtree rendered but inert/hidden; `unstable_LegacyHidden` is the legacy equivalent. Both are development/experimental — do not build production logic on them.
