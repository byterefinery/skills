# Hooks (19.3.0)

Contents

- [Rules of hooks](#rules-of-hooks)
- [State hooks](#state-hooks)
- [Effect hooks](#effect-hooks)
- [Effect events](#effect-events)
- [Optimization hooks](#optimization-hooks)
- [Async and transition hooks](#async-and-transition-hooks)
- [Misc](#misc)

## Rules of hooks

- Call hooks only at the top level of a component or custom hook — never in conditions, loops, or after early returns.
- Call hooks only from React function components or custom hooks — not from plain functions or event handlers.
- The same hooks in the same order on every render — React relies on call order to track state.
- Custom hooks follow the same rules; name them `use*` so linters enforce them.
- Enforced by `eslint-plugin-react-hooks` (rules-of-hooks) and validated by the React Compiler.

## State hooks

### `useState`

`[state, setState] = useState(0)` — lazy init with `useState(() => expensive())`. Pass a function `(prev) => next` to `setState` when the next state depends on the previous value. `setState` is stable across renders and safe to capture in closures and effects.

### `useReducer`

`[state, dispatch] = useReducer(reducer, initialArg, init?)` — for state with several sub-values or where the next state depends on the previous action. `dispatch` is stable; actions should be plain objects. `init` runs lazily once.

### `useRef`

`ref = useRef(initialValue)` — a stable `{ current }` object that persists across renders without triggering re-renders. Use for DOM nodes, timers, and "latest value" storage (assign in render, read in effects). The initial argument is required in 19; ref objects are always mutable.

### `useSyncExternalStore`

`value = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot?)` — safely read external mutable stores (Zustand, Redux, WebStorage) in concurrent React. This is the primitive third-party state libraries build on; provide `getServerSnapshot` for SSR consistency.

### `useContext`

`value = useContext(Context)` — read the nearest provider value in render. Re-renders when the provider value changes by reference.

## Effect hooks

### `useEffect`

`useEffect(create, deps?)` — runs after the browser paints the update. Return a cleanup function; it runs before the next effect and on unmount. `deps` uses shallow `Object.is` comparison; omit to run every render, pass `[]` to run once.

```jsx
useEffect(() => {
  const id = setInterval(tick, 1000);
  return () => clearInterval(id);
}, []);
```

Use `AbortController` for long-running work so cleanup can cancel in-flight requests.

### `useLayoutEffect`

Runs synchronously after DOM mutations and **before** paint — for measuring DOM and making DOM changes that would cause a visible flash if delayed (e.g., positioning a tooltip). Prefer `useEffect` unless you need this; `useLayoutEffect` blocks painting.

### `useInsertionEffect`

Runs before `useLayoutEffect`, in insertion order — for CSS-in-JS libraries that must insert styles before the components using them render.

### `useImperativeHandle`

`useImperativeHandle(ref, createHandle?, deps?)` — exposes a custom API through a ref from a child component. Rarely needed; prefer composition and callbacks.

### `useDebugValue`

`useDebugValue(value?, format?)` — names a value in DevTools for custom hooks only.

## Effect events

### `useEffectEvent` (19.2+)

`onFetch = useEffectEvent(() => { fetch(urlRef.current) })` — wraps a function so it always sees the latest state and props when called from an effect, without needing those values in `deps`. The returned function is stable. Calling it outside an effect (e.g., during render) throws — use it for subscriptions, listeners, and other non-reactive logic.

## Optimization hooks

### `useMemo` / `useCallback`

`value = useMemo(() => compute(a, b), [a, b])` — skips recomputation when deps are unchanged (shallow `Object.is` per item). `useCallback(fn, deps)` is `useMemo(() => fn, deps)` — a stable function reference. Not required for correctness; measure first. In dev, StrictMode reuses the first render's memoized result on the second render.

### `useId`

`id = useId()` — stable unique string for `id`/`htmlFor`/`aria-*` pairs. Since 19.2 the IDs are underscore-based (e.g. `_r_1x`) instead of colon-based; never parse them, and CSS-escape them if used in selectors.

## Async and transition hooks

### `use`

`data = use(promise)` / `value = use(Context)` — read a resource in render. If the Promise is pending, `use` throws it, suspending the nearest `Suspense` boundary. Unlike hooks it may be called **conditionally**, and it works in components, render-phase hooks, and `lazy`. On reject, the error goes to the nearest error boundary.

### `useTransition`

`[isPending, startTransition] = useTransition()` — `startTransition(() => setItems(filter(query)))` marks the update as interruptible: the old UI stays interactive while the new one renders in the background. `isPending` drives spinner UI.

### `startTransition` (standalone, from `react`)

`startTransition(() => {...})` — same as the hook's `startTransition` without the pending state. Since 19 it accepts async functions ("Actions"); see [03-state-and-events](03-state-and-events.md).

### `useActionState`

`[state, formAction, isPending] = useActionState(reducer, initialState, permalink?)` — pair an Action (sync or async function) with state and pending status. The reducer form `(state, payload) => next` runs after the action completes; the third argument is an optional string for progressive enhancement when the form's `action` falls back to a server URL. `useFormState` (imported from `react-dom`) is the deprecated 18-name alias.

### `useOptimistic`

`[optimistic, add] = useOptimistic(realState, (state, payload) => next)` — `add(payload)` inside a transition immediately shows the expected result; when the transition commits, the value snaps to the real state.

## Misc

### `useDeferredValue`

`deferred = useDeferredValue(value, initialValue?)` — returns a copy of `value` that lags behind during urgent updates, so expensive derived UI (filtering, trees) doesn't block typing. `initialValue` (19) is what the component shows on the very first render.
