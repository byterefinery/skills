# Reactivity core — signals, memos, effects, ownership

Solid 2.0's reactivity model: pushes are batched (microtask), reads update only after flush, writes are forbidden under owned scope, and effects are split into a tracking compute phase and a side-effecting apply phase.

## Signals

```ts
const [count, setCount] = createSignal(0);
count();              // read — always call
setCount(1);          // queues; count() still 0 until the microtask flush
setCount(c => c + 1); // updater form
flush();              // count() is now 1
```

Options:

```ts
createSignal(0, { equals: (a, b) => a.id === b.id }); // custom equality (isEqual is the default)
createSignal(null, { ownedWrite: true });   // allow writes from inside owned scope (internal state only)
createSignal(0, { unobserved: () => cleanup() }); // fires when the last subscriber is gone
```

### Writable derived signal (function form)

`createSignal(fn)` creates a writable memo — derived state with a setter. It replaces the 1.x `createComputed` write-back pattern.

```ts
const [count, setCount] = createSignal(0);

// value derives from count; setValue overrides like a normal signal
const [doubled, setDoubled] = createSignal(() => count() * 2);
```

## Memos

```ts
const doubled = createMemo(() => count() * 2); // readonly derivation
doubled();
```

The second argument is now `options` (the 1.x `initialValue` parameter is gone; compute receives `prev`, `undefined` on first run).

```ts
createMemo(() => expensive(source()), { lazy: true });
```

- `lazy: true` defers the initial computation until first read — inert until something reads it. A lazy memo inside a branch that never renders never pays the cost.
- `lazy` also opts the memo into **autodisposal**: it is torn down when its last subscriber goes away and recomputes from scratch on the next read. Non-lazy owned memos live for their owner's lifetime and keep their cache. Unowned memos autodispose too.
- `unobserved` callback (as on signals) for cleanup when a memo loses all subscribers. Combined with `lazy`, this yields demand-driven computations that spin up on read and tear down on idle.

## Split effects

The two-argument form is the **only** form. The 1.x single-callback effect is an error.

```ts
createEffect(
  () => count(),           // compute: reactive reads only; dependencies recorded; receives prev
  (value, prev) => {       // apply: untracked side effects; runs after all computes in the batch
    el.title = value;
    return () => { /* cleanup runs before the next apply and on disposal */ };
  }
);

// prev defaults: (prev = 0) => count()
// Skip the initial run:
createEffect(() => count(), v => log(v), { defer: true });
```

All compute phases in a batch run before any apply phase, giving a consistent dependency picture before side effects — this is what makes async and `Loading`/`Errored` boundaries work.

### Stores in the compute phase

The apply half runs **untracked**. Passing a store proxy through and reading it in apply triggers `STRICT_READ_UNTRACKED` warnings and won't re-run the effect. Extract plain values in compute:

```ts
// ❌ proxy through, reads in untracked scope
createEffect(() => store.user, user => sendAnalytics(user.name, user.age));

// ✅ read in compute, hand plain values to apply
createEffect(
  () => ({ name: store.user.name, age: store.user.age }),
  value => sendAnalytics(value.name, value.age)
);

// ✅ deep observation: subscribes to every nested property, returns a plain snapshot
createEffect(() => deep(store), snapshot => save(JSON.stringify(snapshot)));
```

### Error handling

`createEffect` accepts an `EffectBundle` — `{ effect, error }` — instead of a bare apply function:

```ts
createEffect(
  () => fetchData(id()),
  {
    effect: data => render(data),
    error: (err, cleanup) => console.error(err)
  }
);
```

### Render-phase and tracked variants

```ts
// Synchronous, during render — for DOM-level bindings; app code should use createEffect
createRenderEffect(
  () => props.title,
  (value) => { el.title = value; return () => { el.title = ""; }; }
);

// Single-callback form; may re-run in async situations — special cases only
createTrackedEffect(() => log(count()));

// One-shot tracked callback (advanced patterns)
const track = createReaction(() => doWork());
track(() => count());
```

Neither `createTrackedEffect` nor `onSettled` may create nested reactive primitives, may not call `onCleanup` (return cleanup instead), and may not call `flush()`.

## Batching and flush

`batch` is removed. **All writes are batched by default** (microtask).

```ts
setA(1);
setB(2);       // no intermediate renders — the batch drains on the microtask

// Synchronous "apply now" (tests, imperative interop):
setA(1); setB(2);
flush();

// Drains queued updates before returning; writes inside the callback are
// applied before flush returns (no normal microtask scheduled)
flush(() => { setA(1); setB(2); });
```

Use `flush()` when you need to read reactive values or the DOM immediately after a write (e.g. focus after a state change).

## Lifecycle — onSettled

`onMount` is replaced by `onSettled`: run logic once the current activity has settled. It works in component bodies (after first reactive settle) and in event handlers (defers work until the triggered transition settles).

```ts
onSettled(() => {
  const id = setInterval(tick, 1000);
  window.addEventListener("resize", onResize);
  return () => { clearInterval(id); window.removeEventListener("resize", onResize); };
});
```

- Returns a cleanup function (instead of the previous value); `onCleanup` inside is an error — return the cleanup.
- In an **owned** scope (component body), the returned cleanup is tied to owner disposal.
- Fired **out of band** (from an event handler with no owner, a tracked effect, or another `onSettled`), a returned cleanup is a dev error (`SETTLED_CLEANUP_UNOWNED`) — out-of-band fires are fine for one-shot work only.
- No nested primitives inside.

`onCleanup` remains for reactive cleanup inside computations (tied to a reactive run, not a component lifecycle).

## Ownership

- `createRoot(fn)` is **owned by its parent** by default — a root created inside a component is disposed when the component is disposed. You still get the `dispose` callback.
- Detach explicitly for module singletons / external integrations:

```ts
export const singleton = runWithOwner(null, () => {
  const [value, setValue] = createSignal(0);
  return { value, setValue };
});

// Capture/restore an owner across an async boundary (library code)
const owner = getOwner();
runWithOwner(owner, () => { /* ... */ });
```

- `untrack(() => x())` reads without subscribing — the explicit opt-out for one-time reads (also silences the strict top-level read warning).
- `resolve(() => expr)` returns a Promise that settles when a reactive expression is no longer pending (imperative code / tests; cannot be called inside a reactive scope).

## No writes under owned scope

Writing to signals/stores (or calling `refresh`) inside a reactive scope **throws in dev** (`REACTIVE_WRITE_IN_OWNED_SCOPE`). Fixes:

```ts
// ❌ feedback loop
createMemo(() => setDoubled(count() * 2));

// ✅ derive without writing back
const doubled = createMemo(() => count() * 2);

// ✅ write from an event / onSettled / untracked block
button.onclick = () => setCount(c => c + 1);
```

`ownedWrite: true` is a narrow opt-in for internal state (e.g. a ref slot), not an escape hatch to silence app-state errors.

## Dev diagnostics quick reference

| Code | Severity | Trigger |
|---|---|---|
| `REACTIVE_WRITE_IN_OWNED_SCOPE` | error | Reactive write/invalidation inside component/computation |
| `PENDING_ASYNC_UNTRACKED_READ` | error | Reading pending async outside a tracking scope |
| `CLEANUP_IN_FORBIDDEN_SCOPE` | error | `onCleanup` inside trackedEffect/onSettled |
| `SETTLED_CLEANUP_UNOWNED` | error | `onSettled` returned a cleanup in an out-of-band scope |
| `STRICT_READ_UNTRACKED` | warn | Untracked reactive read in component/effect body |
| `ASYNC_OUTSIDE_LOADING_BOUNDARY` | warn | Async read with no `Loading` ancestor (mount deferred until it settles) |
| `PENDING_ASYNC_FORBIDDEN_SCOPE` | warn | Pending async read in trackedEffect/onSettled |
| `NO_OWNER_EFFECT` / `NO_OWNER_CLEANUP` / `NO_OWNER_BOUNDARY` | warn | Primitive created without an owner — will never be disposed |
| `RUN_WITH_DISPOSED_OWNER` | warn | `runWithOwner` with an already-disposed owner |

Programmatic access (dev only): `DEV.diagnostics.subscribe(listener)` and `DEV.diagnostics.capture()` (scoped event collection for tests).
