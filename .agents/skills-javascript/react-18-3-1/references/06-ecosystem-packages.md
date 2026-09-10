# Ecosystem packages in the monorepo (18.3.1)

## Contents

- [react-is](#react-is)
- [react-refresh](#react-refresh)
- [use-sync-external-store](#use-sync-external-store)
- [scheduler](#scheduler)
- [eslint-plugin-react-hooks](#eslint-plugin-react-hooks)
- [Other packages](#other-packages)

## react-is

Classifies values against React element types — used by tools, DevTools, and snapshot serializers.

```js
import * as ReactIs from 'react-is';

ReactIs.typeOf(element)          // one of the symbols below, or REACT_ELEMENT_TYPE etc.
ReactIs.isValidElementType(x)    // string tag, component, Fragment, Portal, …
ReactIs.isElement(x)             // true for createElement/JSX output
ReactIs.isFragment(x); ReactIs.isPortal(x); ReactIs.isContextConsumer(x)
ReactIs.isContextProvider(x); ReactIs.isForwardRef(x); ReactIs.isLazy(x)
ReactIs.isMemo(x); ReactIs.isProfiler(x); ReactIs.isStrictMode(x)
ReactIs.isSuspense(x); ReactIs.isSuspenseList(x)
```

Exported symbols (compare with `typeOf`): `Element`, `Fragment`, `Portal`, `ContextConsumer`, `ContextProvider`, `ForwardRef`, `Lazy`, `Memo`, `Profiler`, `StrictMode`, `Suspense`, `SuspenseList`. `isAsyncMode`/`isConcurrentMode` still exist but are deprecated no-ops (always `false`).

## react-refresh

Fast Refresh: swap component implementations without remounting or losing state. Two halves:

- **`react-refresh/runtime`** — `register(type, id)` marks a value as a component (the Babel transform calls this per module), `setSignature(type, signature)`, `getFamilyByType`/`getFamilyByID`, `performReactRefresh()`, `injectIntoGlobalHook(globalObject)`, `isLikelyComponentType`, `createSignatureFunctionForTransform`, `hasUnrecoverableErrors`.
- **`react-refresh/babel`** — the Babel plugin (`ReactFreshBabelPlugin`) that injects the signatures and `register` calls; bundler plugins (Vite, webpack, Metro) wire it up.

Rules for Fast Refresh to preserve state: a module may export components and *anything else*, but non-component exports from a module whose components change force a remount of that module's components; keep custom hooks in the same file as the components that use them (or a separate module that never changes signature). Only functions, `memo`, `forwardRef`, and `lazy` results count as components.

## use-sync-external-store

Shim so libraries can use `useSyncExternalStore` on React < 18:

| Entry | Exports |
|---|---|
| `use-sync-external-store` | `useSyncExternalStore` (real hook on 18+, shim below) |
| `use-sync-external-store/shim` | `useSyncExternalStore` — always the shim implementation, safe on any hooks-capable React |
| `use-sync-external-store/shim/with-selector` | `useSyncExternalStoreWithSelector(subscribe, getSnapshot, getServerSnapshot?, selector, isEqual?)` — memoized selector variant |

`use-subscription` (also in the repo) is a thin deprecated wrapper over this shim; do not adopt it.

## scheduler

Cooperative scheduling library React uses internally. Public (all `unstable_`-prefixed, no stability guarantees):

- Priority levels: `unstable_ImmediatePriority` (1), `unstable_UserBlockingPriority` (2), `unstable_NormalPriority` (3), `unstable_LowPriority` (4), `unstable_IdlePriority` (5).
- API: `unstable_runWithPriority(level, fn)`, `unstable_scheduleCallback(level, fn, { delay, timeout })`, `unstable_cancelCallback`, `unstable_wrapCallback`, `unstable_next(fn)` (run at one level lower than current), `unstable_getCurrentPriorityLevel`, `unstable_shouldYield`, `unstable_requestPaint`, `unstable_continueExecution`, `unstable_pauseExecution`, `unstable_getFirstCallbackNode`, `unstable_now`, `unstable_forceFrameRate`.
- `unstable_mock` — a mock scheduler for framework tests.
- `unstable_post_task` — a `scheduler`-style API on top of `PostTask` (browsers with the task scheduler).
- Implementation notes: uses `MessageChannel` when available, `setImmediate` in Node, falls back to `setTimeout`; yields to the browser between tasks.

## eslint-plugin-react-hooks

The official Rules of Hooks linter (part of the Hooks API):

- `react-hooks/rules-of-hooks` — **error**: hooks called conditionally, inside loops/callbacks, or outside components/custom hooks.
- `react-hooks/exhaustive-deps` — **warns**: missing or unnecessary dependencies in `useEffect`/`useMemo`/`useCallback`; handles `setState` functions, refs, and values known to be stable.

```js
// .eslintrc (legacy)
{ "plugins": ["react-hooks"], "rules": { "react-hooks/rules-of-hooks": "error", "react-hooks/exhaustive-deps": "warn" } }
```

Disable selectively with inline comments when a dependency is intentionally stable (explain why in the comment).

## Other packages

| Package | What it is |
|---|---|
| `react-native-renderer` | The renderer shipping inside React Native (bridge + Fabric host configs). Not published from this repo's npm scope; RN apps get it via `react-native` |
| `react-test-renderer` | See 05-testing |
| `react-devtools`, `react-devtools-core`/`-extensions` | DevTools app and browser extensions (separate release trains); hooks into `transitionCallbacks` on `createRoot` for profiling |
| `react-reconciler` | The generic Fiber reconciler — for building custom renderers; API is experimental and not versioned with React |
| `react-noop-renderer`, `react-art`, `react-fs`, `react-pg`, `react-fetch` | Internal/test or legacy experimental renderers — not for application code |
| `dom-event-testing-library`, `jest-react`, `react-interactions`, `react-suspense-test-utils` | Internal testing infrastructure |
