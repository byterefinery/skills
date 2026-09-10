# Core API — `react` package (18.3.1)

The `react` package defines components and holds no DOM or platform knowledge. Named imports are the standard form; a default export exists for UMD/class interop.

## Contents

- [Entry points](#entry-points)
- [Element creation](#element-creation)
- [Children](#children)
- [Components](#components)
- [Hooks](#hooks)
- [Special elements](#special-elements)
- [Unstable exports](#unstable-exports)

## Entry points

| Export | Notes |
|---|---|
| `react` | Full API below |
| `react/jsx-runtime` | Automatic JSX runtime (`jsx`, `jsxs`, `Fragment`) — used by `react/jsx-dev-runtime` in dev; set `runtime: 'automatic'` in Babel/TypeScript instead of importing `React` for JSX |
| `react/jsx-dev-runtime` | Dev variant with better error positions |
| `react` with the `react-server` export condition | Restricted subset used by RSC bundlers: components and hooks minus DOM-facing ones; adds `unstable_createMutableSource`, `unstable_useMutableSource`, `unstable_getCacheForType`, `unstable_getCacheSignal` |

## Element creation

```js
createElement(type, props, ...children)   // builds an element descriptor
cloneElement(element, props, ...children) // copies with merged props/children
isValidElement(object)                    // true for React elements
Fragment                                   // <>...</> as a value
createFactory(type)                       // DEPRECATED — emits a warning; use createElement/JSX
```

- `type` is a string tag (`'div'`), a component function/class, `Fragment`, or a special element (`Suspense`, `Profiler`, `StrictMode`, …).
- `key` and `ref` are pulled out of `props` and not visible to the component; `key` drives list reconciliation, `ref` is passed to the DOM node or wrapped component.
- Elements are immutable descriptors — never mutate them.
- Components may return `undefined` in 18 (renders nothing) — this was a 18.0 change; treat it as a linter target to catch missing `return`.

## Children

```js
Children.map(children, fn)        // fn(child, index) — indexes restart per nesting level; add keys
Children.forEach(children, fn)    // no return value
Children.count(children)
Children.toArray(children)        // flat array, always with keys
Children.only(children)           // throws unless exactly one child
```

`toArray` re-keys nested arrays with `.{index}` prefixes, so a `key` you set on a child is preserved but nested arrays get synthetic prefixes.

## Components

### Function components

```js
function TodoItem(props) { return <li>{props.label}</li>; }
```

- Re-render when their props change (by `Object.is`) or an ancestor re-renders, unless wrapped in `memo`.
- Must not throw outside of intentional Suspense (throwing a promise) — uncaught errors go to the nearest error boundary (class component implementing `static getDerivedStateFromError` or `componentDidCatch`).
- Rules of Hooks: call hooks unconditionally, only at the top level, only inside React function components or custom hooks. Enforced by `eslint-plugin-react-hooks/rules-of-hooks`.

### Class components

`Component` and `PureComponent` (shallow-props comparison in `shouldComponentUpdate`) remain first-class in 18; error boundaries and `componentDidCatch` require a class.

Lifecycle order (stable 18 — `UNSAFE_` methods are legacy and must not be used):

1. `constructor` → `static getDerivedStateFromProps(props, state)` → `render`
2. Mount: `componentDidMount`
3. Update: `shouldComponentUpdate` (default true) → `static getDerivedStateFromProps` → `render` → `getSnapshotBeforeUpdate(prevProps, prevState)` (returns a value or null) → `componentDidUpdate(prevProps, prevState, snapshot)`
4. Unmount: `componentWillUnmount` — run cleanups (subscriptions, timers) here; refs are already nulled.

### Higher-order wrappers

```js
forwardRef((props, ref) => <input ref={ref} {...props} />)  // pass ref through to a wrapped component
memo(Component, (prevProps, nextProps) => boolean)          // skip re-render when the comparator returns true
lazy(() => import('./Component'))                            // module must default-export the component; pairs with Suspense
```

- `memo` compares with `Object.is` per prop by default; provide a custom comparator for reference-changing props.
- `lazy` suspends until the module resolves; if a lazy component suspends, the nearest `Suspense` shows its `fallback`.

## Context

```js
const ThemeContext = createContext(defaultValue);
ThemeContext.Provider    // <ThemeContext.Provider value={x}>…</ThemeContext.Provider>
ThemeContext.Consumer    // classless callback form — prefer useContext
useContext(ThemeContext)
```

- A context update re-renders every consuming component, **not** the provider's children. Nest providers to override values in subtrees.
- `createContext` takes no display name; for DevTools readability use `displayName` on the provider or wrap it.
- Server-rendered context values must be serializable across the RSC boundary (see 07-experimental-rsc); `createServerContext` (unstable) exists for RSC-only contexts.

## Hooks

All hooks must be called in the same order every render. Signatures as in the 18.3.1 source:

### State

| Hook | Signature | Notes |
|---|---|---|
| `useState` | `useState(initialState \| () => initialState)` → `[state, setState]` | `setState(next \| (prev) => next)`; updater functions are pure and may be called twice in StrictMode dev |
| `useReducer` | `useReducer(reducer, initialArg, init?)` → `[state, dispatch]` | `init(initialArg)` runs lazily; 18 removed the eager bailout — `dispatch` always sees current state |
| `useRef` | `useRef(initialValue)` → `{ current }` | Persists across renders; mutating `.current` does not trigger a render. `useRef(null)` for DOM refs |
| `useImperativeHandle` | `useImperativeHandle(ref, createHandle, deps?)` | Exposes a subset of the instance to a parent's `ref` (forwardRef components) |

### Effects

| Hook | Signature | Timing |
|---|---|---|
| `useEffect` | `useEffect(fn, deps?)` → `cleanup?` | After paint; `fn` runs on mount and after matching renders; return a cleanup |
| `useLayoutEffect` | `useLayoutEffect(fn, deps?)` | Synchronously after DOM mutations, before paint; warn during SSR; use for DOM measurements |
| `useInsertionEffect` | `useInsertionEffect(fn, deps?)` | After DOM mutation, before layout effects read layout; for CSS-in-JS style injection — "we don't expect you to ever use this" |

- Effects run in definition order; cleanups run before the next effect and on unmount.
- `deps` comparison is `Object.is`; omit the array to run every render, pass `[]` to run once.
- In 18, effects from **discrete events** (click, keydown) flush synchronously after the event handler; other updates flush before the next paint.
- In dev StrictMode: effect → cleanup → effect, and components are double-mounted. Cleanups must be correct for real unmounts.

### Memory

| Hook | Signature | Notes |
|---|---|---|
| `useMemo` | `useMemo(fn, deps)` | Recomputes only when deps change; a performance hint, not a guarantee — React may discard |
| `useCallback` | `useCallback(fn, deps)` | `useMemo(fn, deps)` that returns the function itself |

### Context and identity

| Hook | Signature | Notes |
|---|---|---|
| `useContext` | `useContext(context)` | Re-renders when the context value changes (by `Object.is`) |
| `useId` | `useId()` → `string` | Stable, unique, SSR-compatible ID (`aria-labelledby`, radio groups). Server and client forms interop; do not cache across renders in a way that skips the hook |

### Concurrent

| Hook / function | Signature | Notes |
|---|---|---|
| `useTransition` | `useTransition()` → `[isPending, startTransition]` | `isPending` true while any transition started by this hook is pending |
| `startTransition` | `startTransition(fn, { timeout }?)` | Marks updates inside `fn` as interruptible transitions |
| `useDeferredValue` | `useDeferredValue(value, { timeout }?)` → `deferred` | Returns `value` after the urgent render settles — a smarter debounce |
| `useSyncExternalStore` | `useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot?)` → `T` | External stores; see 04-concurrent-features |
| `act` | `act(callback)` → `Thenable` | Test-only; flushes scheduled work. **New in 18.3** — import from `react` |

### Debugging

`useDebugValue(value, format?)` — labels the next hook in DevTools; no-ops in production.

## Special elements

| Element | Props | Purpose |
|---|---|---|
| `<StrictMode>` | none | Dev-only: double-invokes renders and effects, double-mounts components (18), surfaces unsafe lifecycles |
| `<Suspense>` | `fallback` | When a child throws a promise, show `fallback` and keep the rest of the tree intact; `fallback={undefined}` behaves like `null` in 18 |
| `<SuspenseList>` | `revealOrder?: 'forwards' \| 'backwards' \| 'together'`, `tail?: 'collapsed' \| 'hidden'` | Coordinates reveal of a list of suspending items (see 04) |
| `<Profiler>` | `id`, `onRender` | Measures render cost; `onRender(id, phase, actualDuration, baseDuration, startTime, commitDuration)` — 6 args in 18, `phase` is `'mount' \| 'update'` |
| `<Fragment>` | `key` only | `<>…</>` grouping without a DOM node |

## Unstable exports

Exported from `react` in 18.3.1 but experimental — expect breaking changes or removal:

- `createServerContext()` — RSC server-side context factory (values must serialize)
- `unstable_DebugTracingMode` — traces transitions for DevTools
- `unstable_LegacyHidden`, `unstable_Offscreen` — offscreen rendering primitives, dev-only
- `unstable_Scope`, `unstable_TracingMarker` — scope/tracing primitives
- `unstable_Cache` — per-render cache element (RSC)
- `unstable_getCacheForType(() => instance)`, `unstable_getCacheSignal()` (`AbortSignal`), `unstable_useCacheRefresh()` — RSC cache APIs
- `createMutableSource(source)` + `useMutableSource(source, getSnapshot, subscribe)` — exported but **not supported** in stable builds; use `useSyncExternalStore`

`__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED` is an internal export — never use it.
