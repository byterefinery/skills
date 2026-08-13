# Reactivity Primitives

Solid's reactivity system is built on fine-grained signals — getter/setter pairs that track dependencies automatically. The system is inspired by Adam Haile's S.js and uses a unidirectional dependency graph.

## createSignal

```ts
const [getter: Accessor<T>, setter: Setter<T>] = createSignal<T>(
  initialValue?: T,
  options?: { name?: string; equals?: false | ((prev: T, next: T) => boolean) }
)
```

- Getter is a function — always call with `()`
- Setter accepts a value or updater: `setCount(c => c + 1)`
- `equals` controls update suppression (default: strict `===`). Set `equals: false` to force every update
- `name` is for dev-mode debugging only

```ts
const [count, setCount] = createSignal(0);
const [obj, setObj] = createSignal({}, { equals: false }); // always updates
```

## createMemo

```ts
const memo: Accessor<T> = createMemo<T>(
  fn: (prev: T) => T,
  initialValue?: T,
  options?: { name?: string; equals?: false | ((prev: T, next: T) => boolean) }
)
```

- Derives a computed value from other signals
- Lazy — only recomputes when read after a dependency changes
- Narrows the dependency graph: downstream effects only track the memo, not inner signals
- Returns a read-only accessor (no setter)

```ts
const [firstName, setFirstName] = createSignal("John");
const [lastName, setLastName] = createSignal("Doe");

const fullName = createMemo(() => `${firstName()} ${lastName()}`);
// Effects reading fullName() only re-run when fullName changes,
// not when firstName or lastName change independently
```

## createEffect

```ts
createEffect<T>(
  fn: (prev: T) => T,
  initialValue?: T,
  options?: { name?: string; render?: boolean }
): void
```

- Runs after the render phase (DOM is updated)
- Tracks all signal reads inside the callback automatically
- Returns void — use for side effects (logging, DOM manipulation, subscriptions)
- Suspense-aware: effects inside `<Suspense>` pause while resources are pending

```ts
createEffect(() => {
  console.log("count is now", count());
});
```

## createComputed

```ts
createComputed<T>(
  fn: (prev: T) => T,
  initialValue?: T,
  options?: { name?: string }
): void
```

- Runs before render (during the computation phase)
- Use for writing to other signals or for computations that must complete before DOM updates
- Rarely needed directly — `createMemo` is usually the right choice

## createRenderEffect

```ts
createRenderEffect<T>(
  fn: (prev: T) => T,
  initialValue?: T,
  options?: { name?: string }
): void
```

- Runs during the render phase, as DOM elements are created/updated
- Use for DOM operations that need to happen synchronously with rendering
- Most side effects should use `createEffect` instead

## createReaction

```ts
const track: (fn: () => void) => void = createReaction(
  onInvalidate: () => void,
  options?: { name?: string }
)
```

- Creates a reactive computation with flexible tracking
- Returns a function to register what to track
- `onInvalidate` fires when the tracked function is invalidated
- Useful for integrating external reactive systems

## createDeferred

```ts
const deferred: Accessor<T> = createDeferred<T>(
  source: Accessor<T>,
  options?: { timeoutMs?: number; name?: string; equals?: false | ((a: T, b: T) => boolean) }
)
```

- Creates a deferred signal that updates on browser idle (via `requestIdleCallback`)
- `timeoutMs` forces update after the timeout even if not idle
- Useful for non-urgent UI updates (analytics, search suggestions)

## createSelector

```ts
const selector: (key: U) => boolean = createSelector<T, U>(
  source: Accessor<T>,
  fn?: (a: U, b: T) => boolean,
  options?: { name?: string }
)
```

- Creates a conditional signal optimized for O(2) lookups
- Designed for "is this item selected?" patterns with many consumers
- Each key registers independently; only the matching consumers update

```ts
const [selectedId, setSelectedId] = createSignal(1);
const isSelected = createSelector(selectedId);

// In a list of 1000 items, only the matching item's effect re-runs
<For each={items()}>
  {(item) => (
    <li classList={{ active: isSelected(item.id) }}>{item.name}</li>
  )}
</For>
```

## untrack

```ts
untrack<T>(fn: () => T): T
```

- Executes `fn` outside the reactive tracking context
- Signal reads inside `untrack` don't create dependencies
- Use for one-time reads, non-reactive comparisons, or breaking dependency chains

```ts
createEffect(() => {
  // Tracks `a`, but not `b`
  const aVal = a();
  const bVal = untrack(() => b());
  console.log(aVal, bVal);
});
```

## batch

```ts
batch<T>(fn: () => T): T
```

- Groups multiple signal updates; dependent effects fire once after all changes
- Prevents intermediate state from triggering effects
- Returns the value from `fn`

```ts
batch(() => {
  setA(a => a + 1);
  setB(b => b + 1);
  setC(c => c + 1);
});
// Effects depending on a, b, or c fire only once
```

## on

```ts
on<S, T>(
  deps: Accessor<S> | AccessorArray<S>,
  fn: (input: S, prevInput: S | undefined, prevValue: T | undefined) => T,
  options?: { defer?: boolean }
): EffectFunction<T | undefined, T>
```

- Makes reactive dependencies explicit
- Only `deps` are tracked; reads inside `fn` are untracked
- Returns an effect function (pass to `createEffect`, `createMemo`, etc.)
- `defer: true` skips the first run (useful for avoiding initial flicker)

```ts
// Tracks only `a`, ignores `b` changes
createEffect(on(a, v => console.log("a =", v, "b =", b())));

// Multiple dependencies
createEffect(on([a, b], ([aVal, bVal]) => console.log(aVal, bVal)));
```

## onMount

```ts
onMount(fn: () => void): void
```

- Runs once after initial render
- Equivalent to `createEffect(() => untrack(fn))`
- Use for DOM measurements, subscriptions, API calls

## onCleanup

```ts
onCleanup<T extends () => any>(fn: T): T
```

- Registers a cleanup function that runs when the reactive scope disposes
- Returns the same function (for convenience)
- Use for clearing timers, unsubscribing, releasing resources

```ts
onMount(() => {
  const id = setInterval(tick, 1000);
  onCleanup(() => clearInterval(id));
});
```

## catchError

```ts
catchError<T>(fn: () => T, handler: (err: Error) => void): T
```

- Runs `fn` with an error boundary; calls `handler` on error
- Errors re-thrown in the handler bubble to the next boundary
- Use for protecting reactive computations

## observable / from

```ts
// Convert a Solid signal to an Observable (compatible with RxJS)
const obs$ = observable(signal);

// Convert an Observable/Producer to a Solid accessor
const accessor = from(rxjsObservable, initialValue);
```

- `observable()` creates a `Symbol.observable`-compatible observable from a signal
- `from()` wraps external producers (RxJS observables, custom subscribe patterns) as Solid accessors

## createRoot

```ts
createRoot<T>(fn: (dispose: () => void) => T, detachedOwner?: Owner): T
```

- Creates an isolated reactive root that doesn't auto-dispose
- Pass `dispose` as a parameter to get manual disposal control
- Use for top-level reactive logic outside components

```ts
const result = createRoot((dispose) => {
  const [count, setCount] = createSignal(0);
  // ... use count ...
  return count();
});
// dispose() to clean up when done
```

## enableScheduling

```ts
enableScheduling(scheduler?: (fn: () => void) => any): void
```

- Enables custom scheduling of effects (defaults to `requestCallback`/`requestAnimationFrame`)
- Use for integrating with external scheduling systems

## startTransition / useTransition

```ts
// Imperative
startTransition(fn: () => void): Promise<void>

// Hook
const [pending, start] = useTransition(): [Accessor<boolean>, (fn: () => void) => Promise<void>]
```

- Defers state updates and effects until the browser is ready
- `pending` signal indicates whether a transition is in progress
- Works with `<Suspense>` for coordinated async UI
