# Migration from Solid 1.x to 2.0

Quick rename/removal map, then behavior changes, then before/after for the patterns you'll hit most.

Table of contents: [imports](#import-paths) · [renames](#renames) · [removals](#removals) · [behavior changes](#behavior-changes) · [before/after](#beforeafter)

## Import paths

| 1.x | 2.0 |
|---|---|
| `solid-js/web` | `@solidjs/web` |
| `solid-js/store` | `solid-js` (store APIs moved into core) |
| `solid-js/h` | `@solidjs/h` |
| `solid-js/html` | `@solidjs/html` |
| `solid-js/universal` | `@solidjs/universal` |
| `solid-js/jsx-runtime` / `jsx-dev-runtime` | `@solidjs/web/jsx-runtime` / `@solidjs/web/jsx-dev-runtime` |
| `jsxImportSource: "solid-js"` | `"@solidjs/web"` for web JSX (`"@solidjs/h"` for hyperscript JSX) |
| `import type { JSX } from "solid-js"` | `import type { JSX } from "@solidjs/web"` |
| renderer-neutral `JSX.Element` | `Element` from `solid-js` |

## Renames

| 1.x | 2.0 |
|---|---|
| `Suspense` | `Loading` |
| `SuspenseList` | `Reveal` |
| `ErrorBoundary` | `Errored` |
| `mergeProps` | `merge` |
| `splitProps` | `omit` |
| `createSelector` | `createProjection` (or `createStore(fn)`) |
| `unwrap` | `snapshot` |
| `onMount` | `onSettled` |
| `equalFn` | `isEqual` |
| `getListener` | `getObserver` |
| `createDynamic(source, props)` | `dynamic(source)` factory (`<Dynamic>` JSX wrapper unchanged) |
| `Context.Provider` | `<Context value={...}>` (the context **is** the provider) |
| `classList={{...}}` | `class={{...}}` (object/array forms) |

## Removals

| Removed | Use instead |
|---|---|
| `batch` | Default microtask batching; `flush()` to apply now |
| `createComputed` | `createMemo` / split `createEffect` / function-form `createSignal` |
| `createResource` | Async computations + `<Loading>` |
| `startTransition` / `useTransition` | Built-in transitions; `isPending` / `<Loading>` / optimistic APIs |
| `on(...)` helper | Split effects (compute phase = explicit deps) |
| `onError` / `catchError` | `<Errored>` or effect `error` option |
| `produce` | Default — store setters are draft-first |
| `createMutable` / `modifyMutable` | `createStore` with draft setters |
| `from` / `observable` | Async iterables in computations / `createEffect` to push out |
| `createDeferred` | Removed; handle outside Solid |
| `Index` | `<For keyed={false}>` |
| `indexArray` | `mapArray` (handles non-keyed too) |
| `resetErrorBoundaries` | Boundaries heal automatically |
| `enableScheduling` | Removed |
| `writeSignal` | Removed (internal API that should not have been exported) |
| `use:foo={x}` directives | `ref={foo(x)}` (or array `ref={[a, b(x)]}`) |
| `attr:` / `bool:` namespaces | Standard attribute behavior |
| `on:` / `oncapture:` | `onClick` for Solid events; ref callbacks for native listener options |
| `/*@once*/` | Keep reactive reads reactive; DOM default props for initial state; `untrack` for rare one-time reads |
| `Suspense.Provider` | None — `Loading` composes directly |

## Behavior changes

- **`createEffect` takes two arguments** — `(compute, apply)`. The single-arg form is an error. Cleanup is returned from apply.
- **Setters don't update reads immediately** — values become visible after the microtask flush (or `flush()`).
- **No writes inside owned scope** — throws in dev. Move writes to event handlers, `onSettled`, actions, or `untrack`; `{ ownedWrite: true }` for narrow internal state.
- **No top-level reactive reads in component body** — warns in dev (includes destructuring props). Read inside JSX, a memo, or `untrack`.
- **Props are values, not accessors** — call accessors at the call site (`<X v={count()} />`); read via `props.x` in the child.
- **`<For>` callback shape follows keying** — default/identity: raw item + index accessor; `keyed={false}`: item accessor + stable number; custom key: both accessors.
- **`<Show>`/`<Match>` function children narrow values** — non-keyed children receive accessors; keyed children receive raw values.
- **Stores: draft-first setters** — mutate the draft in place; returning a value is a shallow replace/diff; keyed reconcile is a projection feature, not a setter feature.
- **`undefined` is a real value in `merge`** — it overrides rather than skipping.
- **Async lives in computations** — return a Promise/AsyncIterable from a computation; pending reads participate in `<Loading>`.
- **`isPending` ≠ 1.x `.loading`** — fires while a value *change* is in flight; a bare `refresh()` is silent. Pending-looking reload: `affects(x); refresh(x)`. "Saving…" affordances: co-written optimistic flag.
- **One error path** — async errors flow to `<Errored>` (or effect `error`); no inline `resource.error` branching.
- **`createRoot` is owned by its parent** — dispose with the parent; `runWithOwner(null, ...)` to detach.
- **Refs are functions**; compose with arrays. **Boolean attributes are presence/absence**. **Built-in attributes are lowercase** (events stay camelCase).
- **In tests, `flush()` before asserting** and wrap code in `createRoot(dispose => { ... })`.

## Before/after

### Batch → default batching + flush

```js
// 1.x
batch(() => { setA(1); setB(2); });

// 2.0 — just write; batching is automatic
setA(1); setB(2);
// Synchronous "apply now":
setA(1); setB(2); flush();
```

### createComputed → memo / split effect / writable signal

```js
// 1.x — readonly derivation
createComputed(() => setDoubled(count() * 2));
// 2.0
const doubled = createMemo(() => count() * 2);

// 1.x — side effect on change
createComputed(() => localStorage.setItem("input", input()));
// 2.0
createEffect(() => input(), val => localStorage.setItem("input", val));

// 1.x — derived with writeback
const [value, setValue] = createSignal(props.initial);
createComputed(() => setValue(props.initial));
// 2.0
const [value, setValue] = createSignal(() => props.initial);
```

### on() → split effects

```js
// 1.x
createEffect(on(count, (value, prev) => console.log(prev, value)));
createEffect(on([a, b], ([a, b]) => console.log(a, b)));
createEffect(on(count, v => log(v), { defer: true }));

// 2.0 — the compute phase is the explicit dependency declaration
createEffect(() => count(), (value, prev) => console.log(prev, value));
createEffect(() => [a(), b()], ([a, b]) => console.log(a, b));
createEffect(() => count(), v => log(v), { defer: true });
```

### onMount → onSettled

```js
// 1.x
onMount(() => {
  const id = setInterval(tick, 1000);
  onCleanup(() => clearInterval(id));
});

// 2.0 — cleanup returned from the callback
onSettled(() => {
  const id = setInterval(tick, 1000);
  return () => clearInterval(id);
});
```

### onError / catchError → Errored + effect error option

```jsx
// 1.x
<ErrorBoundary fallback={err => <p>{err.message}</p>}><Child /></ErrorBoundary>

// 2.0 — err is an accessor, reset is an action
<Errored fallback={(err, reset) => <button onClick={reset}>{String(err())}</button>}>
  <Child />
</Errored>
```

```js
// 1.x
catchError(() => { createEffect(() => riskyAsyncWork()); }, err => console.error(err));

// 2.0
createEffect(() => riskyAsyncWork(), {
  effect: value => { /* success */ },
  error: err => console.error(err)
});
```

### produce / createMutable → draft-first stores

```js
// 1.x
import { produce } from "solid-js/store";
setStore(produce(s => { s.user.name = "Alice"; s.list.push("item"); }));

const state = createMutable({ count: 0, items: [] });
state.count++;
state.items.push("a");

// 2.0 — draft-first is the default; writes go through the setter
setStore(s => { s.user.name = "Alice"; s.list.push("item"); });

const [state, setState] = createStore({ count: 0, items: [] });
setState(s => { s.count++; s.items.push("a"); });
```

1.x path-style setters survive via the opt-in helper: `setStore(storePath("user", "name", "Alice"))`.

### from / observable → async iterators / effects

```js
// 1.x — external → Solid
import { from } from "solid-js";
const signal = from(observable$);

// 2.0 — async iterables are first-class in computations
const value = createMemo(async function* () {
  for await (const val of observable$) yield val;
});

// 1.x — Solid → external
const obs$ = observable(signal);
obs$.subscribe(value => externalLib.update(value));

// 2.0 — push changes outward with an effect
createEffect(signal, value => externalLib.update(value));
```

### Index → For keyed={false}

```jsx
// 1.x
<Index each={items()}>{(item, i) => <Row item={item()} index={i} />}</Index>

// 2.0
<For each={items()} keyed={false}>{(item, i) => <Row item={item()} index={i} />}</For>
```

### classList → class

```jsx
// 1.x
<div class="card" classList={{ active: isActive() }} />

// 2.0
<div class={["card", { active: isActive() }]} />
```

### use: → ref directive factories

```jsx
// 1.x
<button use:tooltip={{ content: "Save" }} />

// 2.0
<button ref={tooltip({ content: "Save" })} />
<button ref={[autofocus, tooltip({ content: "Save" })]} />
```

### Context.Provider → context as provider

```jsx
// 1.x
const Theme = createContext("light");
<Theme.Provider value="dark">{props.children}</Theme.Provider>

// 2.0
<Theme value="dark">{props.children}</Theme>
```

Drop the `useX`-with-throw wrappers — default-less `createContext<T>()` types `useContext` as `T` and throws `ContextNotFoundError` itself.

### createResource → async computations + Loading

```js
// 1.x
const [user] = createResource(id, fetchUser);

// 2.0
const user = createMemo(() => fetchUser(id()));
```

```jsx
<Loading fallback={<Spinner />}>
  <Profile user={user()} />
</Loading>
```

### SuspenseList → Reveal

```jsx
// 1.x
<SuspenseList revealOrder="forwards">
  <Suspense fallback={<Skeleton />}><ProfileHeader /></Suspense>
  <Suspense fallback={<Skeleton />}><Posts /></Suspense>
</SuspenseList>

// 2.0 — default order is "sequential"
<Reveal>
  <Loading fallback={<Skeleton />}><ProfileHeader /></Loading>
  <Loading fallback={<Skeleton />}><Posts /></Loading>
</Reveal>
// order="together" reveals the group at once; order="natural" per-slot
```
