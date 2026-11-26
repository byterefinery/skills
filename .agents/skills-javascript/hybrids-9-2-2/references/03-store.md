# Store

Global state management based on model definitions with support for external storage. Declarative: define the model, use it with `store()`. The same cache keeps model state up to date inside components, and communication is uniform across sync and async sources.

## Table of Contents

- [Ground rules](#ground-rules)
- [Model definitions](#model-definitions)
- [Primitives & validation](#primitives--validation)
- [Computed values](#computed-values)
- [Nested objects](#nested-objects)
- [Nested arrays](#nested-arrays)
- [Record & self references](#record--self-references)
- [Storage](#storage)
- [Factory](#factory)
- [Direct methods](#direct-methods)
- [Draft mode](#draft-mode)
- [Guards](#guards)

---

## Ground rules

The three principles unifying sync and async sources:

- `store.get()` always returns the current state **synchronously**
- `store.set()` always updates **asynchronously** (Promise)
- `store.get()` and `store.set()` always return an **object** (model instance, placeholder, or promise)

A **placeholder** is returned when there is no previous value (not found, pending, or errored). It protects property access so it cannot be used by mistake; the guards (`ready`/`pending`/`error`) describe the state.

## Model definitions

A model is a plain object with JSON-like default values. Each definition creates its own global data space, identified by reference — no registration step. Instances are **immutable**; updates produce new versions. Models can reference each other (bindings are immutable, not the values).

### Identifier

- **Singleton** — no `id` property; the store always returns the same instance:

```js
const Model = { value: "" };
```

- **Enumerables** — `id: true`; multiple instances with unique identifiers (a `string`, or an **object record** — a map of primitives normalized to a string):

```js
const Model = { id: true, value: "" };

const result = store.get(SearchResult, { query: "some", order: "desc" });
```

Client-generated identifiers default to UUIDv4 for memory-based models.

### Listing enumerables

Wrap a definition in an array to list it: `store.get([Model]) === store.get([Model])`. The listing has its own cache space and supports string/object identifiers (`store.get([Model], { query: "some" })`). For memory models it returns all instances; for external storage the result depends on the `list` storage action.

## Primitives & validation

Supported primitives: `string`, `number`, `boolean`. The default value defines the property type (with conversion on set, e.g., `String(value)`).

Client-side validation runs inside `store.set()` via `store.value()`:

```js
const Model = {
  firstName: store.value(""),
  count: store.value(0, (val) => val > 10, "Value must be bigger than 10"),
  termsAndConditions: store.value(false),
};
```

```js
store.value(defaultValue, validate?: fn | RegExp, errorMessage?: string)
```

- `validate(val, key, model)` should return `false`, an error message, or throw on failure; or pass a RegExp
- Omitted `validate` fails on falsy values (empty string, `0`, `false`)
- On failure the instance is not updated and an error is attached; the rejected `Error` carries an `err.errors` object keyed by property name

## Computed values

Function properties compute from other model properties, cached permanently after first access. They are non-enumerable (excluded from serialization, e.g., `JSON.stringify`):

```js
const Model = {
  firstName: "Great",
  lastName: "name!",
  fullName: ({ firstName, lastName }) => `${firstName} ${lastName}`,
};
```

## Nested objects

Two kinds, distinguished automatically:

### Internal (no `id`, no `[store.connect]`)

Stored inside the model instance; each instance has its own values. All model-definition rules apply recursively:

```js
const Model = {
  internal: { value: "test", number: 0 },
};
```

### External model reference (`id` or `[store.connect]` present)

Creates a one-way dynamic binding: the property becomes a getter asking the store for the instance by id (singletons use `undefined`). The related model knows nothing about the connection. Storage may provide full instance data or just a valid identifier — the store handles fetching across storages. Remove the relation with `null`/`undefined` (does not delete the related model; the property then resolves to `undefined`):

```js
const Model = {
  externalWithId: ModelWithId,          // { id: true, ... }
  externalSingleton: SingletonFromStorage, // { [store.connect]: { ... } }
};
```

## Nested arrays

The **first item** determines the structure:

### Internal (primitive or internal object first)

Content is unique per instance; extra default items are created from the first item's definition. Empty defaults use a primitive constructor:

```js
const Model = {
  domains: [String],
  numbers: [Number],
};
```

### External (enumerable model definition first)

A list of external model instances mapped by ids. Second item is an options object with `loose`:

```js
const Model = {
  items: [OtherModel, { loose: false }],
};
```

Updating a nested array must provide a new array version — no in-place item changes.

### Cache invalidation & loose

By default, changes to nested external models do not invalidate the parent's cached value (the binding reflects updates without a parent update). When list content depends on item state (e.g., pagination ordered by name), pass `{ loose: true }` — then `store.set()` on a nested model invalidates the parent's cached value. The `store.get` action never invalidates the parent (prevents fetch loops); lower the storage `cache` option for stricter freshness.

## Record & self references

- **`store.record(value)`** — variable-key map of any supported property types; defaults to an empty object. Set keys with `store.set(Settings, { flags: { a: true } })`, remove a key with `{ a: null }`, reset with `flags: null`.
- **`store.ref(fn)`** — resolves a property to `fn()` at definition time; use for self-references and import cycles (single: `store.ref(() => Model)`, list: `store.ref(() => [Model])`).

## Storage

Every model connects to storage. Default is memory. Custom storage via `[store.connect]`:

```js
const Model = {
  ...
  [store.connect]: {
    get?: (id) => object | null | Promise<object | null>,
    set?: (id, values, keys) => object | null | Promise<object | null>,
    list?: (id) => [object] | Promise<[object]>,
    observe?: (id, model, lastModel) => void,
    cache?: boolean | number /* ms */ = true,
    offline?: boolean | number /* ms */ = false,
    loose?: boolean = false,
  },
};
```

All fields optional, but `get` or `list` is required. A bare function value equals `{ get: fn }`.

- **`set(id, values, keys)`** — `id === undefined` means create (client-generated `id` is already in `values`); `values: null` deletes/resets; `keys` lists the actually updated properties (partial updates). Omitting `set` makes the model read-only.
- **`list(id)`** — for listings; supports string id or object record. Listing results cannot carry metadata (use a definition with a nested array for that).
- **`observe(id, model, lastModel)`** — synchronous side effects at the end of `get`/`set`, before the memory cache update. `lastModel` is `null` on first set; `model` is `null` on delete. Do **not** call `store.get`/`store.set` for the same model inside (stack overflow).
- **`cache`** — `true` (default) = persistent until manually invalidated; a number = TTL in ms (expired models refetched on next call, not automatically); `false`/`0` = fetch on every call.
- **`offline`** — persistent `localStorage` layer. Cached values are returned synchronously while the main source fetches, and used when the source fails (model ends up both `error` and `ready`). Keys are derived from the definition structure — identical structures across definitions share a key. `true` = 30-day default expiration, cleared only when the main source is available; a number = hard TTL after which the value is removed. `store.clear(Model)` also clears offline values.
- **`loose`** (storage) — invalidates listing cache whenever one of its instances changes (default off).
- **Memory storage** — singletons: `store.set(Globals, null)` resets values to defaults; enumerables: listing returns all client-created models.

## Factory

```js
store(Model: object, options?: { id?: any | (host) => any; draft?: boolean }): descriptor
```

- **Singleton** — no `id` option needed
- **Explicit `id`** — host property name or function of host: `user: store(User, { id: "userId" })`; object records via function: `store([User], { id: ({ order, query }) => ({ order, query }) })`
- **Without `id`** — the instance is set by the property itself: `el.user = "1"` (id), `el.user = someUser` (instance of the same definition), or the static attribute `user="1"`
- **Rendering in-between states** — with an `id` option, the factory **caches the last value** until the next value is ready (guards reflect the new pending state), so lists can keep old data visible while new data loads. Without the option, `store.get()`-style semantics always return the current state.
- Updating state is only possible via `store.set()` directly.

## Direct methods

### store.get

```js
store.get(Model, id?): Model
```

Synchronous; returns the instance or a placeholder.

### store.set

```js
store.set(Model, values): Promise<Model>            // create/update by definition
store.set(modelInstance, values | null): Promise<Model> // update/delete by instance
```

Always a Promise; model values update in the next microtask, but the current instance state updates instantly and `store.pending()` is truthy until settled. Supports **partial values** (nested objects merge). `values: null` deletes — resolves with an errored placeholder.

### store.resolve

```js
store.resolve(modelOrDefinition, id?): Promise<Model>
```

Resolves with the **latest** instance regardless of pending state; supports chained `set` calls. Use before reading a possibly-pending instance (e.g., right before a POST).

### store.sync

```js
store.sync(modelOrDefinition, values | null): Model
```

Updates the **memory cache only**, bypassing all `[store.connect]` methods. For server-pushed updates (WebSocket, extension messages) where calling storage `set()` would loop. Does not replace `store.set()` — use with caution.

### store.clear

```js
store.clear(model, clearValue = true)
```

Invalidates a specific instance or all instances of a definition. `clearValue: false` keeps the cached value but forces a refetch (refresh buttons); `true` also permanently deletes instances not attached to any component (garbage collection). With `offline`, also clears `localStorage` values.

### store.observe

```js
store.observe(Model, callback: (id, model, lastModel) => void): () => void
```

Dynamic observation outside the model definition (service workers, extension background scripts). Fires only for `get`/`set` calls **after** registration — not for pre-existing instances. Returns the unobserve function.

## Draft mode

`store(Model, { draft: true })` returns a **memory-based copy** of the model (or a new one with defaults) — ideal for forms. The draft is deleted from memory when the component disconnects. Commit with:

```js
store.submit(draft: Model, values?: object): Promise<Model>
```

`values` are merged on top of the draft before creating/updating the primary instance. Combine `store.value()` validation with `html.set(model, "propertyPath")` and read per-property errors via `store.error(model, "property")`.

## Guards

Return values are not mutually exclusive — several guards can be truthy at once (e.g., resolved model being updated → `ready` and `pending`).

### store.ready

```js
store.ready(model, ...): boolean
```

`true` only when **all** instances are resolved (AND). While an update is in flight or failed, the last valid state is returned and `ready` stays `true` — combine with `pending` to show dirty state.

### store.pending

```js
store.pending(model, ...): boolean | Promise
```

Promise instance (resolving with the next value) when **any** instance is being fetched or set (OR); `false` in a stable state.

### store.error

```js
store.error(model, propertyName?: string | null): boolean | Error | any
```

The caught error when the instance is in an error state. With `propertyName` (a `store.value()` property) returns `err.errors[propertyName]` — for validation errors in forms. Works with any API error carrying an `err.errors` object.
