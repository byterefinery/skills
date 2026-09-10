# Performance

How React 18.3.1 renders, where the cost lives, and the official tools to measure and reduce it.

## Why components re-render

A component re-renders when:

1. Its own state changes (`useState`/`useReducer` setters).
2. A parent re-renders (children render with the parent by default).
3. A context it consumes changes (any consumer of that context re-renders, regardless of `memo`).
4. A class calls `forceUpdate`, or a key changes (key change is a **remount**, not a re-render — state resets, refs fire cleanup, effects re-run).

Everything else (unrelated state updates, other branches of the tree) does not re-render it. Reconciliation is the mechanism: React compares the previous and next element trees and only commits what changed.

## Memoization

```ts
memo(Component: ComponentType<P>, compare?: (prevProps: P, nextProps: P) => boolean): MemoExoticComponent<ComponentType<P>>
```

- `memo` skips re-rendering a component when its props are shallow-equal (`Object.is` per key); a custom `compare` replaces the check.
- It is a **filter on re-render triggers 1–3**, not a speedup of the render itself. Memoizing a cheap component costs more than it saves; memoize leaves whose render is expensive or whose identity matters (children wrapped in `useCallback`).
- Classic churn sources that defeat `memo`: fresh object/function/array props on every render. Stabilize them with `useMemo`/`useCallback`, or restructure so the child receives only primitive data.
- `useMemo`/`useCallback` are only worth it when (a) the computation is genuinely expensive, or (b) a stable identity is required (effect deps, `memo`d children, context values). Neither guarantees anything — React may recompute early.

## Keys and list performance

- Reconciliation matches children by key; **stable keys let React move DOM nodes instead of recreating them** and preserve state correctly.
- Index keys work for static, never-reordered lists; for dynamic lists they shift state between items when the list changes (the item at index 2 gets the state of whatever was at index 2 before).
- A changed key destroys and recreates the subtree — intentionally use this to "reset" a component (e.g. `<Chat key={userId} />`), not as a performance lever.

## Deferring expensive work

- `useDeferredValue` / `startTransition` (see 04) move expensive re-renders out of the input critical path — the input stays responsive and the heavy subtree catches up.
- Code-split with `lazy(() => import('./Heavy'))` + `Suspense` so first paint does not pay for unused screens.
- `unstable_Offscreen` can pre-render hidden subtrees in the background (unstable — see 04).

## StrictMode cost

`<StrictMode>` doubles render work and effects in **development only** (see 04). It is a correctness tool, not a performance feature; production builds contain none of it. If a component is slow *because of* StrictMode double-invocation, fix the impurity — the same cost (once) is what production would pay per render anyway.

## Profiler

```jsx
<Profiler id="SearchResults" onRender={onRender}>
  <SearchResults />
</Profiler>
```

`onRender` signature:

```ts
onRender(
  id: string,
  phase: 'mount' | 'update' | 'profile' | 'nested' | 'forced',
  actualDuration: number,      // ms spent rendering this subtree this time
  baseDuration: number,        // estimated ms to render with no cached memo
  startTime: number,           // ms since Profiler began rendering
  commitTime: number,          // ms since Profiler began when commit finished
  effectsDuration?: number,    // ms spent in this subtree's effects
  effectsStartTime?: number    // ms since Profiler began when effects started
): void
```

- `phase`: `mount` (first render), `update` (re-render from state/props/context), `nested` (re-render triggered by a child update, e.g. an effect calling a parent setter), `forced` (class `forceUpdate`), `profile` (render recorded while profiling was active).
- `actualDuration` is the time React spent in this subtree's render *in this pass*; `baseDuration` estimates the uncached cost — the gap tells you how much memoization saved.
- Profiling is a development feature; wrap subtrees, accumulate per-id samples, and look at commit vs render splits (effects time is separate from render time).

## Production build

- Production bundles strip all `__DEV__` warnings, validation (prop type checks, hook rules), and double-rendering. Build with the standard toolchain (`vite build`, `next build`, `webpack mode: production`) — running the development bundle in production is the single biggest avoidable cost.
- Minification and tree-shaking apply per package; import named exports (`import { useState } from 'react'`) rather than the default namespace to keep bundlers honest.
- Measure with the browser profiler and React DevTools (below), not with wall-clock guesses; concurrent features change *when* work happens, not how much.

## React DevTools

- **Components** tab: inspect props/state/refs of any fiber; highlights DOM elements on hover.
- **Profiler** tab: record interactions to see which components re-rendered, per-render duration, and a flame graph of the commit.
- "Why did this render?" (DevTools 5+/extension) annotates re-renders with the triggering update.
- DevTools auto-injects (see 03); in StrictMode the second render pass appears in grey — a visual reminder of double-invocation.

## Checklist

1. Add `<Profiler>` (or DevTools Profiler) around the slow screen; record an interaction.
2. Identify components re-rendering more often than their data changes; ask which trigger (state, parent, context) is responsible.
3. Push state down or split context so only affected consumers update.
4. `memo` the expensive leaves with stable props (`useCallback`/`useMemo` where identity matters).
5. Verify keys are stable; remounts are usually the hidden cost.
6. Defer the non-urgent: `useDeferredValue` for heavy subtrees, `startTransition` for navigation/data renders, `lazy` for screens.
7. Ship a production build; re-measure.
