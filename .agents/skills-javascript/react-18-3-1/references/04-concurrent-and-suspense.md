# Concurrent rendering and Suspense

How React 18 schedules, interrupts, and prioritizes work, and how `Suspense` coordinates async UI.

## The model

React 18 renders **concurrently**: it can start a render, interrupt it, and resume it later, interleaving it with more urgent work. Concretely:

- **Urgent (synchronous) updates** — triggered by discrete events (click, keypress), `setState` in event handlers, and `flushSync` — render before the next paint and are not interrupted.
- **Transitions (non-urgent updates)** — wrapped in `startTransition` — are interruptible: React yields between components, keeps rendering in the background, and if input arrives mid-render, abandons the in-flight tree and starts the urgent one.
- **Work expiration** — if a transition render is still incomplete when new input arrives (or when React estimates it will miss the next frame), the pending work can be discarded and the user sees the *previous* UI until the new one is ready. There is no spinner unless you build one.
- **Double rendering** — interrupted renders are retried; components are pure, so rendering the same tree twice is safe. This is why impure renders (random values, side effects) break with concurrent features.
- All of this requires a `createRoot`/`hydrateRoot` root; legacy `ReactDOM.render` trees are synchronous.

## Automatic batching

Since 18, React batches multiple state updates triggered by the same event, `setTimeout`, promise, or XHR callback into **one render** (previously only React event handlers batched). `ReactDOM.unstable_batchedUpdates` forces this batching explicitly, and `flushSync` forces a synchronous break in it.

Practical consequences:

- `setA(1); setB(2);` in one handler renders once with both updates.
- Code that previously relied on a synchronous re-render between two `setState` calls (measuring DOM in between) must wrap the first in `flushSync`.
- Libraries that called `setState` from outside React events now batch too — usually a win, but it changes render counts.

## Transitions

```jsx
import { startTransition, useTransition } from 'react';

function Search({ query }) {
  const [isPending, startTransition] = useTransition();
  return (
    <>
      <input
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);                 // urgent — input stays responsive
          startTransition(() => {
            setResults(search(e.target.value));     // non-urgent — interruptible
          });
        }}
      />
      {isPending && <Spinner />}
      <Results results={results} />
    </>
  );
}
```

- `startTransition(fn)` runs `fn` synchronously; everything it enqueues becomes transition work.
- `useTransition` adds `isPending` — `true` from when a transition starts until it is painted (or interrupted). Do not treat it as a promise for "data is ready" — the UI is still showing stale content while pending.
- A transition update can be **interrupted** by a later urgent update; the interrupted state is simply not committed.
- In development, a transition containing more than 10 updates warns — usually a signal that a store subscription is being driven by `startTransition` instead of `useSyncExternalStore`.
- Transitions do **not** delay user input; they only affect how React schedules the resulting render. Typing in an input never waits for a transition.

## useDeferredValue

```jsx
const [query, setQuery] = useState('');
const deferredQuery = useDeferredValue(query);
return <ExpensiveList search={deferredQuery} />;
```

- Returns a value that follows `value` with a delay determined by scheduling, not a timer: children re-render with the *new* value only after the urgent render (the input) is painted.
- Unlike debouncing there is no fixed wait — React retries the deferred render immediately once the urgent one is done.
- Use it to keep an expensive subtree (search results, charts) from blocking fast input; it is the building block behind `useTransition` internally.

## Suspense

```jsx
<Suspense fallback={<Skeleton />}>
  <ExpensiveChild />
</Suspense>
```

- When a component **throws a promise** (the `lazy` pattern, or your own async component), the nearest `Suspense` boundary shows `fallback` until the promise resolves, then re-renders the content.
- If the tree suspends *before it is fully committed*, React discards the incomplete render and retries from scratch concurrently — effects of the suspended tree do not run until it is shown.
- **Layout effects** inside a boundary are cleaned up when the boundary reverts to its fallback and recreated when the content returns (this is how component libraries can measure layout correctly with Suspense).
- `fallback` may be `null` or `undefined` (since 18, `undefined` behaves like `null` rather than being ignored).
- Fallbacks are throttled: React avoids flashing fallbacks for very brief suspensions (the threshold is tuned internally, ~200 ms).
- Without a `Suspense` ancestor, a suspending component re-throws up to the root and the whole tree shows the root's fallback behavior — wrap every data-fetching subtree.

## lazy

```jsx
import { lazy, Suspense } from 'react';

const Chart = lazy(() => import('./Chart'));

<Suspense fallback={<Spinner />}>
  <Chart data={data} />
</Suspense>
```

- `lazy(() => import('./Component'))` returns a component that resolves a module's **default export** when first rendered; the promise suspends the boundary while loading.
- Since 18, two `lazy()` calls that resolve to the same module are considered equivalent — React can dedupe loads.
- Code-split whole feature components this way; the browser downloads the chunk only when the component first renders.

## SuspenseList

```jsx
<SuspenseList tag="nested" tail="hidden">
  <Suspense fallback={...}><Row key={1}/></Suspense>
  <Suspense fallback={...}><Row key={2}/></Suspense>
</SuspenseList>
```

- Coordinates multiple adjacent Suspense boundaries so they reveal in order:
  - `tag="nested"` — the next boundary only shows its fallback after the previous has revealed (staggered, sequential reveal).
  - `tag="revealed"` — all boundaries reveal at once (used with `tail`).
- `tail="collapsed"` collapses (hides) boundaries after the first N shown; `tail="hidden"` keeps them hidden until they load. Useful for infinite lists where later rows should not flash fallbacks.
- Keep it simple: plain `Suspense` boundaries are enough for most UIs; `SuspenseList` is for lists of boundaries.

## Offscreen and legacy hidden (unstable)

From `react` (experimental, behind feature flags in some builds):

```jsx
import { unstable_Offscreen, unstable_LegacyHidden } from 'react';

<unstable_Offscreen mode={isOpen ? 'visible' : 'hidden'}>
  <Panel />
</unstable_Offscreen>
```

- `unstable_Offscreen` lets a subtree render "offscreen" (hidden) so React can pre-render its content and state in the background and show it instantly when `mode` flips to `'visible'`. State is preserved while hidden.
- `unstable_LegacyHidden` is the older "hide without unmounting" component (predecessor concept).
- These are **unstable** and not part of the supported surface — do not build production features on them in 18.

## StrictMode

```jsx
<StrictMode>
  <App />
</StrictMode>
```

Development-only behavior, active when you render `<StrictMode>` (or set `unstable_strictMode` on the root options):

- Double-invokes component functions, `useState`/`useReducer` initializer functions, and `useMemo`/`useCallback` factories — to surface impure renders.
- Double-runs effects on mount: mount → cleanup → mount (same order), to verify cleanups.
- Ref callback functions run twice on mount (called with `null` then the node, or the node then `null` in the second pass).
- None of this happens in production builds — if StrictMode breaks your app, you have a real bug (side effects in render, missing cleanups), not a React bug.

## Common patterns

- **Search input** — urgent input state + `startTransition`/`useDeferredValue` for the results tree (example above).
- **Route/code splitting** — `lazy` + `Suspense` around a route's page component; put the `Suspense` above as many pages as reasonable to share one fallback.
- **Data fetching** — a component that throws a promise while loading (your own hook or a library) + `Suspense`; pair with `useSyncExternalStore` for external caches so cache hits never suspend.
- **Streaming SSR** — `renderToPipeableStream`/`renderToReadableStream` + client `hydrateRoot` (see 05); the server streams shells and Suspense fallbacks, the client hydrates progressively.
