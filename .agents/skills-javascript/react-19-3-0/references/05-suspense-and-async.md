# Suspense and Async

Contents

- [Suspense boundaries](#suspense-boundaries)
- [Code splitting with lazy](#code-splitting-with-lazy)
- [use and data fetching](#use-and-data-fetching)
- [Transitions and pending UI](#transitions-and-pending-ui)
- [useDeferredValue](#usedeferredvalue)
- [useOptimistic](#useoptimistic)
- [Activity](#activity-192)
- [SuspenseList](#unstable_suspenselist)

## Suspense boundaries

`<Suspense fallback={...}>` defines a boundary: when a descendant suspends (throws a Promise), the nearest boundary shows its fallback and React resumes the rest of the tree when the Promise resolves.

```jsx
<Suspense fallback={<PageSpinner />}>
  <ProfileDetails />
</Suspense>
```

- Nest boundaries to load UI incrementally — an inner boundary shows its own fallback while outer content stays visible.
- When one sibling suspends, React 19 commits the nearest fallback **immediately** without waiting for the sibling tree to finish ("sibling pre-warming"), then pre-warms the suspended siblings in the background.
- A re-suspend while already revealed hides the content again (e.g., navigating to a new item that needs new data).
- Fallbacks should be small; avoid heavy fallback trees.
- Suspense does not catch rejected Promises — errors go to error boundaries.

## Code splitting with lazy

```jsx
import { lazy, Suspense } from 'react';

const Chat = lazy(() => import('./Chat.js'));

export default function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <Chat />
    </Suspense>
  );
}
```

The `import()` Promise is cached — the module loads once. `lazy` works with `use(promise)` too (`const Component = use(import('./X.js'))` style, inside render).

## `use` and data fetching

`use(promise)` reads a resource during render: pending → suspends the component; resolved → returns the value; rejected → throws to the nearest error boundary.

```jsx
function Tweet({ tweetId }) {
  const tweet = use(fetchTweet(tweetId)); // fetchTweet must memoize per id
  return <div>{tweet.body}</div>;
}
```

React has **no built-in client-side data fetching**. The canonical patterns:

- **Server** (with React Server Components) — components are async and `await` data directly; no client JS for fetching. This is the primary model in 19.
- **Client** — pair `use()` with a module-level cache (same Promise per resource) or a third-party library (React Query, SWR) that you hand to `use()`.

`use()` may be called conditionally and in `lazy`, and it works with Context (`use(MyContext)` suspends if the context provider is still loading).

## Transitions and pending UI

```jsx
function FilterableList() {
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();
  return (
    <>
      <input value={query} onChange={e => {
        const next = e.target.value;
        startTransition(() => setQuery(next)); // filtering doesn't block typing
      }} />
      {isPending ? <Spinner /> : null}
      <FilterItems query={query} />
    </>
  );
}
```

Transitions keep the previous UI visible and interactive while the new render happens in the background; a newer urgent update interrupts them. Use for search/filter, routing, and anything non-urgent.

## `useDeferredValue`

`deferredQuery = useDeferredValue(query)` — the deferred value lags behind the latest one during urgent updates, so expensive derived work (large list filtering, tree expansion) yields to typing. Combine with a transition or `useOptimistic` for the pending indicator.

## `useOptimistic`

`[optimisticCount, add] = useOptimistic(count, (n, delta) => n + delta)` — inside a transition, `add(1)` shows the incremented count immediately; when the real state commits, the value reconciles. Use for counters, cart badges, and anything with long round-trips.

## `<Activity>` (19.2+)

```jsx
<Activity hidden={isOpen === false}>
  <SettingsPanel />
</Activity>
```

Hides its children (and any DOM they own) **without unmounting** — state, effects that were already set up, and DOM refs persist — and restores them when `hidden` flips back. Pair with `<ViewTransition>` (see [07-view-transitions](07-view-transitions.md)) to animate hide/show, and with `startTransition` so the hidden/unhidden commit is interruptible.

## `unstable_SuspenseList`

```jsx
<SuspenseList revealOrder="together" tail="collapsed">
  {rows.map(row => (
    <Suspense key={row.id} fallback={<RowSkeleton />}>
      <Row data={row} />
    </Suspense>
  ))}
</SuspenseList>
```

Coordinates how a set of sibling Suspense boundaries reveal: `revealOrder` — `together` (wait for the first batch), `combined` (reveal in completion order), `closure` (reveal per component closure); `tail` — `collapsed` keeps the trailing boundaries' fallback visible until everything is loaded. Still `unstable_` — pin usage behind a feature check.
