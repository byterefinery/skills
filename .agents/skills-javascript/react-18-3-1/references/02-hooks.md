# Hooks

The complete hook API of `react` 18.3.1 with signatures and behavior notes. Hooks are the only sanctioned way to manage state and side effects in function components.

## Calling rules

- Call hooks **only at the top level** of a React function component or custom hook — never inside loops, conditions, or nested functions.
- Call them in the **same order every render** — React matches hooks to their state by call position.
- Only call hooks from **React or from your own custom hooks** (a custom hook is a function whose name starts with `use` that calls other hooks).
- The rules above are enforced by `eslint-plugin-react-hooks` (`react-hooks/rules-of-hooks`); `react-hooks/exhaustive-deps` checks dependency arrays.

`act` (see 03) is exported from `react` in 18.3.1 but is a testing utility, not a hook.

## State

```ts
useState<S>(initialState: S | (() => S)): [S, Dispatch<SetStateAction<S>>]
useReducer<R extends Reducer<any, any>>(
  reducer: R,
  initialArg: any,
  init?: (arg: any) => ReducerState<R>
): [ReducerState<R>, Dispatch<ReducerAction<R>>]
```

- `useState` returns the current state and a setter. The initial value may be a function (lazy init — the function is called once, and its *return value* becomes the state).
- `setState` accepts a value or an updater `prev => next`; updaters run in order and are the only safe way to update based on the previous state.
- Setting the same value (by `Object.is`) bails out of re-rendering, but React may still re-render once before bailing — do not rely on equality for correctness.
- `useReducer` holds structured state: `reducer(state, action) => nextState`. `init` lazily computes the initial state. Prefer it over several `useState`s when values change in lockstep.

## Refs

```ts
useRef<T>(initialValue: T): MutableRefObject<T>
```

- Returns a stable object `{ current }` for the lifetime of the component. Not state — mutating `ref.current` does not re-render.
- Use for DOM nodes (`ref={elRef}`), mutable values that survive renders without triggering renders (subscription handles, previous props), or values that should persist across renders (e.g. a ref to the latest callback used by a long-lived subscription).
- A ref passed to a class component yields the instance; to forward an imperative handle from a function component use `forwardRef` + `useImperativeHandle` (or just accept `ref` as a prop — see 01/08; in 18 function components must use `forwardRef` for external refs).

## Rendering

```ts
useMemo<T>(create: () => T, dependencies: readonly any[]): T
useCallback<T extends Function>(callback: T, dependencies: readonly any[]): T
```

- `useMemo` caches the computed value until dependencies change (shallow `Object.is` compare). It is an optimization, not a correctness tool — React may discard and recompute at any time.
- `useCallback(fn, deps)` is `useMemo(() => fn, deps)` — it stabilizes a function's identity. The main real use is passing stable callbacks into memoized children or as effect dependencies.
- Both are meaningless for cheap values; wrapping a primitive or a small object in `useMemo` usually costs more than it saves.

## Context

```ts
useContext(Context: Context<T>): T
```

- Returns the current context value for the nearest `<Context.Provider>` above; defaults to `Context._default` (the value passed to `createContext`) when no provider exists.
- A component re-renders when the context value it consumes changes (by `Object.is`). `memo` does not protect from context changes.
- In 18.3.1 context is the primary cross-tree data channel for server-side data as well — see 08 for context deep-dives and 06 for `createServerContext` (RSC).

## Effects

```ts
useEffect(effect: () => void | (() => void), dependencies?: readonly any[] | null): void
useLayoutEffect(effect: () => void | (() => void), dependencies?: readonly any[] | null): void
useInsertionEffect(effect: () => void | (() => void), dependencies?: readonly any[] | null): void
```

- **`useEffect`** runs **after the browser has painted**. Use for subscriptions, data loading, timers, logging. It returns an optional cleanup function run before the next effect and on unmount.
- **`useLayoutEffect`** runs synchronously **after DOM mutations, before paint**. Use for DOM measurements and mutations that must not flash. It blocks painting — use sparingly and never on the server (it warns in SSR).
- **`useInsertionEffect`** runs after DOM mutations but **before layout effects**; it exists so CSS-in-JS libraries can inject styles before layout reads happen. Do not use it for anything else; setting state inside it warns.
- Dependencies array: omit it to run after every render, pass `[]` to run once on mount (and clean up on unmount), otherwise list every reactive value read inside. `exhaustive-deps` catches omissions.
- With 18's StrictMode, effects mount → cleanup → mount in development to verify cleanup correctness.
- An effect that schedules an update must gate on the dependency values, or it loops.

## Imperative handles and debugging

```ts
useImperativeHandle(
  ref: Ref<T> | undefined,
  createHandle: () => T,
  dependencies?: readonly any[]
): void
useDebugValue(value: any, format?: (value: any) => any): void
```

- `useImperativeHandle` customizes what a `ref` points to when a parent renders `<MyComponent ref={ref} />` (with `forwardRef`). Call it once with the handle factory.
- `useDebugValue` labels a derived value in DevTools with an optional formatter; development-only, zero cost in production.

## IDs

```ts
useId(): string
```

- Returns a unique, stable string ID (client `:r0:`, server-rendered/hydrated `:R0:`; format is colon + counter — do not parse it).
- Designed for `id`/`htmlFor`, `aria-describedby`, `aria-labelledby` pairs in component libraries so SSR output and client hydration agree.
- Escape IDs if you interpolate them into CSS selectors or `url()` references.

## Concurrent

```ts
useTransition(): [boolean, (callback: () => void) => void]
useDeferredValue<T>(value: T): T
startTransition(callback: () => void, options?: { name?: string }): void
```

- **`startTransition`** (imported from `react`) wraps state updates as non-urgent: urgent updates (typing, clicks) can interrupt them. `options.name` labels the transition for tracing (Profiling) when `enableTransitionTracing` is on. In development it warns if a transition contains more than 10 updates (usually a misused subscription).
- **`useTransition`** is `startTransition` plus an `isPending` boolean: `const [isPending, start] = useTransition()` — show a spinner while the transition render is in flight.
- **`useDeferredValue`** returns a value that lags behind updates: `const deferredQuery = useDeferredValue(query)` re-renders children with the old query until the urgent render (the input) completes. No fixed delay — React retries the deferred render as soon as the urgent one is painted.
- See 04 for the full concurrent model and patterns.

## External stores

```ts
useSyncExternalStore<T>(
  subscribe: (onStoreChange: () => void) => () => void,
  getSnapshot: () => T,
  getServerSnapshot?: () => T
): T
```

- Subscribes the component to an external store and reads it **synchronously and consistently** with concurrent rendering — the recommended way to wrap Redux, Zustand, MobX-style stores, or any external signal.
- `getSnapshot` must be a pure, referentially stable read: returning a fresh object each call causes infinite loops (React compares with `Object.is`). If the store's state is an object you derive, memoize it in `getSnapshot` or use `useSyncExternalStoreWithSelector`.
- `getServerSnapshot` (optional) is used during SSR to avoid mismatching server/client values (typically returns the store's initial state).
- `useSyncExternalStoreWithSelector(subscribe, getSnapshot, getServerSnapshot?, selector, isEqual?)` is **not** exported from `react` in 18 — import it from `use-sync-external-store/with-selector`.

## Unstable (do not use in production code)

- `useMutableSource(source, getSnapshot, subscribe)` — legacy pre-concurrent-API for external mutable data; superseded by `useSyncExternalStore`.
- `unstable_useCacheRefresh()` — refreshes the RSC `cache()` for the current scope; only meaningful inside `unstable_Cache`/Server Components (see 06).
- `createMutableSource()` — the companion constructor for `useMutableSource`.

## Custom hooks

```jsx
function useLocalStorage(key, initial) {
  const [value, setValue] = useState(() => {
    try { return JSON.parse(localStorage.getItem(key)) ?? initial; }
    catch { return initial; }
  });
  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);
  return [value, setValue];
}
```

- Name them `useSomething`; they may call other hooks and compose them for components.
- A custom hook's state belongs to the *calling component*, not to the hook function — the same hook called by two components keeps separate state.
- Document the dependencies your hook takes; hooks are a library contract, and `exhaustive-deps` checks across the boundary only warn.
