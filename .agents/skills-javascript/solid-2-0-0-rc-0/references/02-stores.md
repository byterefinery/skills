# Stores

Store APIs moved from `solid-js/store` into `solid-js` core. Setters are **draft-first** (produce-style) by default.

## Basic store — draft-first setters

```ts
import { createStore } from "solid-js";

const [store, setStore] = createStore({ user: { name: "A" }, list: [] });

// Canonical form: mutate the draft in place
setStore(s => {
  s.user.name = "B";
  s.list.push("x");
});
```

`produce` is not an import — it is the default setter behavior. The 1.x `createMutable`/`modifyMutable` pair is replaced by stores: direct proxy mutation can't participate in batching, transitions, or optimistic rollback, so writes go through `setStore`.

### Returning a value — shallow replacement

```ts
// Arrays replace by index + length; objects shallow-diff at the top level.
// No keyed reconciliation — for that use projections / reconcile.
setStore(s => s.list.filter(x => x !== "x"));
setStore(s => ({ ...s, list: [] }));
```

### storePath — 1.x path-style compat (opt-in)

```ts
setStore(storePath("user", "address", "city", "Paris"));
setStore(storePath("items", { from: 1, to: 4, by: 2 }, 99)); // range patterns
setStore(storePath("nickname", storePath.DELETE));            // delete sentinel
```

## reconcile — keyed diffing into a store

`reconcile(value, key?)` returns a diffing function; call it **inside the setter callback** targeting the part of the draft to reconcile. Key defaults to `"id"`; `null` is positional matching (index N into index N — the 1.x `{ key: null, merge: true }` pattern; merge semantics are always on in 2.0).

```ts
setStore(s => {
  reconcile(serverTodos, "id")(s.todos);
});
```

## Derived stores — projections

Mirrors the signal/memo split:

| Signals | Stores |
|---|---|
| `createMemo(fn)` — readonly derived value | `createProjection(fn, seed)` — readonly derived store |
| `createSignal(fn)` — writable derived value | `createStore(fn, seed)` — writable derived store |

```ts
// Readonly derived store: fn receives a draft to mutate; a returned value is
// reconciled into the output (keyed by options.key, default "id")
const selected = createProjection(s => {
  const id = selectedId();
  s[id] = true;
  if (s._prev != null) delete s[s._prev];
  s._prev = id;
}, {});

// Async-derived, keyed reconciliation (replaces createSelector)
const users = createProjection(async () => await api.listUsers(), [], { key: "id" });

// Writable derived store
const [cache, setCache] = createStore(draft => { draft.value = expensive(selector()); }, { value: 0 });
setCache(s => { s.override = true; }); // imperative writes still work
```

`createSelector` is removed — projections are the general replacement (selection, derived caches, async-derived store values).

## Shallow stores (perf opt-in)

`createStore(value, { shallow: true })` creates a **single-layer** store: root keys are fully reactive, but values under them are **plain records replaced by reference** — no proxies, no deep diffing. The contract: **records are replaced, never edited.**

```ts
const [rows, setRows] = createStore(initialRows, { shallow: true });
onPoll(fresh => setRows(reconcile(fresh, null))); // positional at the boundary

<For each={rows} keyed={(row) => row.id}>{row => <tr>{row().name}</tr>}</For>
```

Reach for it only when profiling shows ingestion cost on record-granularity data (polling dashboards, wholesale server collections). Don't use it for field-by-field state (forms, editors) — that's what deep stores are optimal for. `shallow` is also accepted by `createProjection` and `createOptimisticStore`.

## snapshot and deep

Both return plain (non-proxy) objects:

```ts
// snapshot — plain copy, NO tracking. For serialization/interop.
const plain = snapshot(store);
JSON.stringify(plain);

// deep — subscribes to every nested property. For effects that must react to any change.
createEffect(() => deep(store), snapshot => persist(JSON.stringify(snapshot)));
```

`unwrap` (1.x) is replaced by `snapshot`.

## merge and omit

```ts
const merged = merge(defaults, props, overrides); // replaces mergeProps
const rest = omit(props, "class", "style");       // replaces splitProps
```

**`undefined` is a real value** — it overrides rather than skipping:

```ts
const merged = merge({ a: 1, b: 2 }, { b: undefined });
// merged.b is undefined
```
