# Advanced APIs and companion packages

Deep dives on context and refs, the catalog of `unstable_*` APIs in 18.3.1, and the packages that ship alongside `react`.

## Context in depth

```ts
createContext<T>(defaultValue: T): Context<T>
// Context.Provider — render <Ctx.Provider value={v}>
// Context.Consumer — render function (value) => ReactNode (legacy pattern; useContext is preferred)
```

- The provider chain walks **up** from the consumer to the nearest provider of the *same context object*. Context is identity-based: two separate `createContext` calls never see each other, and re-creating a context in a module (HMR) splits it.
- A consumer re-renders when the provided value changes by `Object.is` — so **do not pass fresh objects as values**:

```jsx
// bad — new object every render of Provider forces all consumers to re-render
<Ctx.Provider value={{ user, prefs }}>
// good
const value = useMemo(() => ({ user, prefs }), [user, prefs]);
<Ctx.Provider value={value}>
```

- `memo` does **not** stop context-driven re-renders — a memoized consumer still re-renders when its context changes. Split contexts by update frequency (one context for rarely-changing data, another for fast-changing data).
- Nested contexts and multiple providers per context are fine; the nearest wins per branch.
- `useContext` reads the value; a component that does not consume a context is unaffected by its updates.
- Context works identically in SSR and in RSC (see 06 for the separate `createServerContext`).

## Refs in depth

```ts
createRef<T>(): RefObject<T>        // { current: null } until attached
// callback ref: ref={(node) => { elRef = node; }}
forwardRef<T, P>(render: (props: P, ref: ForwardedRef<T>) => ReactNode, compare?)
```

- Refs are **synchronous**: `ref.current` is set during the commit phase, before `useLayoutEffect` and `componentDidMount`. Never read a ref during render (except the classic "previous value" pattern `prev = ref.current; ref.current = value` at render top — a known idiom, but do the mutation after the read).
- Callback refs receive `null` on unmount and again when a node is swapped; they run every commit where the ref value changes (store the callback in a `useCallback` if it is inline, or it re-fires every render).
- `forwardRef` is required in 18 for function components to receive external refs; `useImperativeHandle` shapes what the ref exposes.
- `ref` on a **class** component gives the instance (use sparingly — it is an imperative escape hatch); on a **DOM** element the DOM node; on a **function** component without `forwardRef`, `ref` is ignored with a warning.
- String refs and `findDOMNode` are dead ends (the latter deprecated in 18.3 — see 03).

## Fragment, Suspense, and structural components

- `Fragment` (and the `<>` shorthand) groups children without a DOM node; it is the only element type that can take a `key` among the built-ins (needed for keyed fragment lists).
- `Suspense` — see 04/05. `SuspenseList` — see 04. `StrictMode` — see 04. `Profiler` — see 07.
- `unstable_Scope` — groups a subtree so it can be measured/annotated as a unit (profiler-related, experimental).
- `unstable_TracingMarker` — dev-only tracing annotation for concurrent work (feature-flagged).
- `unstable_LegacyHidden` / `unstable_Offscreen` — see 04.

## Unstable API catalog (18.3.1)

Everything below carries `unstable_` and may change or disappear without notice. Do not use in production code.

| API | Package | Purpose |
|---|---|---|
| `unstable_batchedUpdates` | react-dom | Force explicit batching |
| `unstable_flushControlled` | react-dom | Synchronously flush controlled-input updates |
| `unstable_createEventHandle` | react-dom | Access the native event handle (internal) |
| `unstable_runWithPriority` | react-dom | Temporarily exposed Scheduler bridge — do not use |
| `unstable_isNewReconciler` | react-dom | Feature-flag probe |
| `unstable_testing` entry | react-dom | Selector engine for custom test utilities (see 03) |
| `unstable_Offscreen`, `unstable_LegacyHidden` | react | Background/hidden rendering (see 04) |
| `unstable_Scope`, `unstable_TracingMarker`, `unstable_DebugTracingMode` | react | Profiling/tracing annotations |
| `createMutableSource` / `useMutableSource` | react | Legacy external-data API, superseded by `useSyncExternalStore` |
| `unstable_Cache`, `createServerContext`, `unstable_getCacheForType`, `unstable_getCacheSignal`, `unstable_useCacheRefresh` | react | RSC request-scoped cache and server contexts (see 06) |
| `unstable_act` → `act` | react | `act` is stable in 18.3.1; `unstable_act` remains as an alias |
| `unstable_mock`, `unstable_post_task` entries | scheduler | Testing and scheduler-task APIs |
| `unstable_batchedUpdates` | react-test-renderer | Batching in the test renderer |

## scheduler

ForkJoin scheduler that React (and libraries) use to time-slice work. `import { ... } from 'scheduler'`:

```ts
unstable_scheduleCallback(priorityLevel, callback, options?: { delay?: number }): CallbackNode
unstable_cancelCallback(callbackNode: CallbackNode): void
unstable_runWithPriority(priorityLevel: number, callback: () => void, options?): any
unstable_next<T>(callback: () => T): T      // run callback at the next priority lane
unstable_continueExecution(): void
unstable_pauseExecution(): void
unstable_shouldYield(): boolean
unstable_requestPaint(): void
unstable_getCurrentTime(): number
unstable_Profiling                        // profiler instrumentation object
// priority levels: unstable_ImmediatePriority, unstable_UserBlockingPriority,
// unstable_NormalPriority, unstable_LowPriority, unstable_IdlePriority
```

- This is the API React uses internally (`NormalPriority` ≈ default work, `UserBlockingPriority` ≈ discrete input, `ImmediatePriority` ≈ `flushSync`). Libraries (React Native, React Three Fiber, data-fetching layers) use it directly.
- Use it for scheduling non-UI work (parsing, prefetching) around React's rendering; do not reimplement priority with `setTimeout` when this exists.
- `scheduler/unstable_mock` exposes a mock clock for tests; `scheduler/unstable_post_task` integrates with the browser task scheduler API.

## react-is

Runtime type guards for element objects:

```ts
typeOf(object): symbol | null    // the element type symbol
isValidElementType(object): boolean
isElement, isFragment, isPortal, isContextConsumer, isContextProvider,
isForwardRef, isLazy, isMemo, isProfiler, isStrictMode, isSuspense, isSuspenseList,
isConcurrentMode(object): boolean   // true for <Suspense> in concurrent context
isAsyncMode(object): boolean        // legacy alias, deprecated
```

Plus exported type symbols (`Element`, `Fragment`, `Portal`, `ContextConsumer`, `ContextProvider`, `ForwardRef`, `Lazy`, `Memo`, `Profiler`, `StrictMode`, `Suspense`, `SuspenseList`, `ConcurrentMode`, `AsyncMode`). Use it for devtools-style introspection and debugging; application code rarely needs it.

## react-refresh

Fast Refresh (component state-preserving HMR):

- `react-refresh/babel.js` — the Babel plugin (`babel-plugin-react-refresh`) that tags components so the runtime can identify them.
- `react-refresh/runtime.js` — `signatureInDev(Component)`, `getFamilyByType(type)`, `register(type, familyId)`, `shouldReset(type)`; the bundler's HMR pipeline calls it to decide "update in place with state preserved" vs "remount".
- Vite (`@vitejs/plugin-react`) and webpack (`react-refresh/webpack` via the plugin) wire this up. If component state vanishes on edit, the babel plugin is missing or the component is exported with extra values (a file with mixed exports can break Refresh).

## use-sync-external-store

Standalone `useSyncExternalStore` for libraries that support React 16.8–18 without depending on `react`:

```ts
// 'use-sync-external-store'
useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot?)
// 'use-sync-external-store/with-selector'
useSyncExternalStoreWithSelector(subscribe, getSnapshot, getServerSnapshot?, selector, isEqual?)
// 'use-sync-external-store/shim' (and /shim/with-selector)
// auto-selects the React-provided hook on React 18+, falls back to the shim below
```

- Store libraries (Redux, Zustand, Jotai) ship their React bindings through the **shim** so one codebase works on 16.8 through 19.
- In your own app code just use the `react` export; use these packages when *writing* a store binding.

## use-subscription

```ts
// 'use-subscription'
useSubscription<Value>({
  getCurrentValue: () => Value,                       // synchronous read
  subscribe: (callback: (value: Value) => void) => () => void,  // returns unsubscribe
}): Value
```

- A higher-level convenience over `useSyncExternalStore` for data subscriptions (e.g. WebSocket feeds, live query results): pass the current value getter plus a subscribe function, and the hook keeps the component in sync, safely, across concurrent rendering.
- The params object should be referentially stable (memoize it) — it is read on every render.

## eslint-plugin-react-hooks

```json
{ "plugins": ["react-hooks"], "rules": { "react-hooks/rules-of-hooks": "error", "react-hooks/exhaustive-deps": "warn" } }
```

- `rules-of-hooks` — enforces the two hook rules (top-level only, same order, only from React/custom hooks). Errors are usually real bugs.
- `exhaustive-deps` — checks `useEffect`/`useMemo`/`useCallback` dependency arrays; it understands that `setState` functions are stable and that hook return values from the same hook are stable. Treat its warnings as a checklist, not gospel, but fix them deliberately.

## JSX runtime entry points

- `react/jsx-runtime` — `jsx`, `jsxs`, `Fragment` (production automatic runtime).
- `react/jsx-dev-runtime` — development variants that attach source info (`_debugSource`, `_self`) for better error stacks.
- Babel: `@babel/preset-react` with `{ runtime: 'automatic' }` (or `automatic-importSource`/`development` options); TypeScript: `"jsx": "react-jsx"` / `"react-jsxdev"`; esbuild: `jsx: 'automatic'`.
