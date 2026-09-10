# `react` package — API in 19.3.0

Export list verified from `packages/react/index.js` at tag v19.3.0.

## Entry points

- `react` — main entry; resolves to the client or server implementation via the `react-server` export condition
- `react/jsx-runtime`, `react/jsx-dev-runtime` — automatic JSX transform (the classic `import React` transform is not supported in 19)
- `react/compiler-runtime` — runtime helpers emitted by React Compiler

## Hooks

| Hook | Notes |
|---|---|
| `useState` | Local state; setter accepts a value or an updater function |
| `useReducer` | Complex state machines |
| `use` | 19.0 — read a promise or Context during render; suspends while the promise is pending. The only hook-like API that may be called conditionally, and only in render |
| `useEffect` | Post-paint side effect; may return a cleanup |
| `useEffectEvent` | 19.2 — wrap non-reactive event logic; the returned function has a stable identity and can be shared with effects without adding dependencies |
| `useLayoutEffect` | Synchronous DOM effect after mutation, before paint |
| `useInsertionEffect` | For CSS-in-JS style insertion |
| `useMemo` / `useCallback` | Manual memoization; unnecessary when React Compiler is enabled |
| `useRef` | Mutable value that persists across renders; the ref object identity is stable |
| `useImperativeHandle` | Expose an imperative API through a ref |
| `useId` | Unique opaque string for `id`/`aria-*`; format changed across versions, never parse it |
| `useContext` | Read a Context (or pass the Context itself to `use`) |
| `useDebugValue` | Labels a custom hook in the DevTools |
| `useDeferredValue` | Defer a non-urgent state update; 19.0 added an optional initial value argument |
| `useTransition` | Returns `[isPending, startTransition]`; 19.0 Actions may be async |
| `useSyncExternalStore` | Subscribe to an external store |
| `useActionState` | 19.0 — pair an Action with a form; returns `[state, formAction, isPending]` (also takes an optional permalink string for progressive enhancement) |
| `useOptimistic` | 19.0 — `useOptimistic(passthrough, reducer)`; shows the expected state immediately while the transition completes in the background |

## Components and values

- `Suspense` — fallback boundary; can be used anywhere in 19.1+ (client, server, hydration)
- `Activity` — 19.2+, hides and restores a subtree while keeping its UI and internal state
- `ViewTransition` — present in the 19.3 tree (feature-flagged); animates changes between renders, see the react.dev reference for props
- `StrictMode`, `Fragment` (`<>`), `Profiler`, `PureComponent`, `Component`
- Unstable, avoid in product code: `unstable_LegacyHidden`, `unstable_Scope`, `unstable_SuspenseList`, `unstable_TracingMarker`

## Functions

- `createContext` — in 19 `<Context>` can be rendered directly as a provider (no `.Provider` needed)
- `createElement` / `cloneElement` / `createRef` / `isValidElement`
- `forwardRef` — legacy; ref-as-prop is the 19 way
- `lazy` — async component loading; combine with `use()` to read the loading promise
- `memo` — manual re-render guard; unnecessary with the compiler
- `cache` — RSC: memoize a function's results per request
- `cacheSignal` — 19.2+ (RSC): signal that fires when the current `cache()` lifetime ends
- `startTransition` — run an update in the background; in 19 the callback may be async (an Action)
- `addTransitionType` — 19.3 tree (feature-flagged): tag the transition currently running with a string type (e.g., "route", "tab"); must be called inside a `startTransition` callback
- `unstable_getCacheForType`, `unstable_useCacheRefresh` — unstable RSC cache APIs
- `Children` — `map`, `forEach`, `count`, `toArray`, `only`
- `version`
