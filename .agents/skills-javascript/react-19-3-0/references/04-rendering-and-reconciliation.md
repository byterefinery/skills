# Rendering and Reconciliation

Contents

- [The rendering model](#the-rendering-model)
- [What triggers a re-render](#what-triggers-a-re-render)
- [Reconciliation](#reconciliation)
- [Keys](#keys)
- [Skipping work](#skipping-work)
- [Purity and the Rules of React](#purity-and-the-rules-of-react)
- [StrictMode](#strictmode)
- [Concurrent rendering](#concurrent-rendering)
- [Error boundaries](#error-boundaries)

## The rendering model

A component's render returns a **tree of elements** — lightweight descriptors, not DOM nodes. React keeps the current tree in memory and, on every update, compares (reconciles) the new tree against the old one, then mutates the DOM (commits) only where they differ. Rendering is JavaScript you can interrupt; committing is DOM work.

## What triggers a re-render

A component re-renders when:

- it calls `setState` (or `dispatch`) with a value that differs from the previous state,
- a `useSyncExternalStore` snapshot it reads changes,
- the value of a `Context` it consumes changes (by reference),
- its parent re-renders (children re-render with their parent by default, unless `memo` skips them).

`setState` with the same value (`Object.is`) skips the re-render.

## Reconciliation

For each element, React compares the new type with the old:

- same type → the element is updated in place (props diffed),
- different type → the old subtree is torn down and the new one built,
- lists → children are matched by **key**; unmatched children are created or destroyed.

Type here means the tag name for DOM elements, or the function/class identity for components — swapping `<MyList>` for `<OtherList>` replaces the whole subtree, including any DOM React created for it.

## Keys

Keys tell React which items in a list are the same across renders. Use stable, unique IDs (database IDs, slugs) — never array indices for lists that reorder, insert, or delete, because index keys map the wrong state to the wrong item. Keys only need to be unique among siblings.

## Skipping work

- `memo(Component, compare?)` — skip the component's re-render when props are shallow-equal.
- `useMemo(fn, deps)` / `useCallback(fn, deps)` — keep computed values and function references stable so children' `memo` comparisons succeed.
- Splitting context into smaller providers so only relevant consumers re-render.
- Passing stable props — avoid inline objects, arrays, and arrow functions in JSX when the child is memoized.

Measure before adding any of these — the comparison cost and cognitive overhead are real. The React Compiler (see [09-react-compiler](09-react-compiler.md)) removes most of the manual need.

## Purity and the Rules of React

Render and hook bodies must be **pure** functions of their inputs — this is what lets React interrupt, retry, and reorder work. The Rules of React:

1. **Don't mutate props or state during render.** Read them, return new values; no `push`/`delete`/assignment onto them.
2. **Don't read or write props or state in a non-deterministic way during render.** No `Date.now()`, `Math.random()`, or reading globals that change between renders.
3. **Don't change hook dependencies between renders** — pass stable values (or derive them stably).
4. **Follow the Rules of Hooks** — no conditional or out-of-order hook calls.

Violations don't just break the React Compiler's optimizations; they break concurrent rendering itself (interrupted renders may observe half-mutated state). Enforced by `eslint-plugin-react-compiler`.

## StrictMode

`<StrictMode>` (dev only) double-invokes to surface impurity:

- component render functions run twice,
- effects mount, cleanup, and re-mount on initial mount,
- ref callbacks run twice on initial mount,
- `useMemo`/`useCallback` reuse the first render's result on the second render (19 behavior).

If your code works in StrictMode, it's very likely impurity-free. Keep it around in development builds.

## Concurrent rendering

React 18+ schedules work in two lanes:

- **Urgent updates** — user input and most `setState` calls; interrupt the current render and take priority.
- **Transitions** — work wrapped in `startTransition`; React may pause, finish other work, and resume them in the background, keeping the old UI interactive. `isPending` (from `useTransition`) tracks in-flight transitions.

`flushSync` opts out for a synchronous update. Time-slicing means long renders no longer block input — but only when the work is inside transitions; urgent updates still render to completion.

## Error boundaries

Error boundaries are class components (function components can't catch render errors):

```jsx
class ErrorBoundary extends Component {
  state = { hasError: false };
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  componentDidCatch(error, errorInfo) {
    logErrorToMyService(error, errorInfo);
  }
  render() {
    return this.state.hasError ? <h1>Something went wrong.</h1> : this.props.children;
  }
}
```

In 19, errors in render that are **not** caught by an error boundary are no longer re-thrown; they are reported to `window.reportError`. Custom handling: `createRoot(..., { onUncaughtError, onCaughtError })`. Errors thrown during effects or event handlers are not caught by error boundaries at all.
