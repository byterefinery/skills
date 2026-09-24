# Async data and actions

Async is a first-class capability of computations: any memo/store can return a **Promise** or **AsyncIterable**. `createResource` no longer exists — pending reads follow the `Loading` boundary path, and mutations are structured `action(...)` generators with optimistic primitives.

## Async in computations

```ts
const user = createMemo(() => fetchUser(id())); // pending until resolved

function Profile() {
  return <div>{user().name}</div>; // reading user() is not ready at first
}

<Loading fallback={<Spinner />}>
  <Profile />
</Loading>
```

Collections: `createStore(async () => api.list(), [])` or `createProjection(async () => api.list(), [], { key: "id" })`. Async iterables work directly (the 1.x `from()` replacement):

```ts
const value = createMemo(async function* () {
  for await (const val of source$) yield val;
});
```

Reading pending async **outside a tracking scope throws** (`PENDING_ASYNC_UNTRACKED_READ`). Async errors propagate through the reactive graph — one path, caught by `<Errored>` or an effect's `error` option. There is no inline `.error` branching (1.x's `resource.error` path is gone).

## isPending / latest / refresh / affects / resolve

| API | Answers |
|---|---|
| `isPending(fn)` | "Is a value **change** in flight for this read?" — true while a tracked input changed and the new answer hasn't landed, or while in-flight work declared it via `affects`. A bare `refresh()`/poll re-asking the same question is **silent** (stays false). |
| `latest(fn)` | Peek at the in-flight value during a transition (may be stale until it lands). |
| `refresh(target)` | Explicitly recompute a derived source after a server write. Call from handlers/effects/actions — it is an action, not a UI flag. Quiet: the fresh value reveals silently. |
| `affects(target, key?)` | Declare that in-flight work **will change** the data — the marked record/slot reads pending until the transaction settles. Additive only. One key per call; keys don't form paths. |
| `resolve(fn)` | Promise that settles when the expression is no longer pending (imperative code/tests; not inside reactive scopes). |

`isPending` actively **reads** the expression you pass — its placement matters. Put it under the `Loading` boundary that owns the async read (it participates in that boundary's readiness); it may live outside the boundary when it only reads upstream state that can't be not-ready.

```jsx
const listPending = () => isPending(() => users() || posts());

<Loading fallback={<Spinner />}>
  <Show when={listPending()}>{/* subtle "updating…" while a new query loads */}</Show>
  <List users={users()} posts={posts()} />
</Loading>;

// Guarding an interactive control that reads async data:
<Loading fallback={<button disabled>Loading...</button>}>
  <button disabled={isPending(user)}>Save</button>
</Loading>;
```

To make a reload read as pending: `affects(user); refresh(user)`. For process affordances ("saving…"), co-write an optimistic flag — don't fake it with pending state.

## Transitions

Built-in, multiple in flight, no `startTransition`/`useTransition` to wrap. The user-facing pieces are `isPending`, `Loading`, and the optimistic APIs below.

## Actions and optimistic updates

`action(fn)` wraps a generator (or async generator) mutation and returns an async function to call from handlers. Inside: optimistic writes, `yield` async work, `refresh` at the end.

```ts
const [todos, setTodos] = createOptimisticStore(() => api.getTodos(), []);

const addTodo = action(function* (todo) {
  setTodos(t => { t.push(todo); });   // optimistic — shows immediately, reverts on failure
  yield api.addTodo(todo);            // async work in the transition
  refresh(todos);                     // reconcile with the source of truth
});

// Async generator form:
const save = action(async function* (todo) {
  setTodos(t => { t.push(todo); });
  const res = await api.addTodo(todo);
  yield;                              // resume in the same transition context
  refresh(todos);
  return res;
});
```

- **`createOptimistic(value)`** — signal surface; writes are optimistic and revert when the transition completes.
- **`createOptimisticStore(fnOrValue, seed)`** — store analogue (the derived-store form); the seed is the backing host array/object.

Division of labor: optimistic writes **show** the expected value (they are verdict-inert — they don't pend their own slot), `affects` **pends** data you know is changing but can't show yet, and process affordances are co-written optimistic state.

```ts
const rename = action(function* (todo, text) {
  setTodos(() => { todo.text = text; });
  affects(todo, "updatedAt"); // server changes this slot too — pend it
  yield api.rename(todo.id, text);
  refresh(todos);
});
```

### Layered state pattern (todos example)

The canonical app shape is three lifetime layers composed in one primitive chain:

```
3. Optimistic  (transition-scoped) — setTodos writes inside action generators, auto-revert
2. Ephemeral   (UI-scoped)         — side-channel (errors, drafts, toasts) applied inside the projection fn
1. Persistent (durable)            — api.getTodos() inside the projection fn (server / localStorage / URL)
```

Consumers read the topmost store; ordering is enforced by composition, not convention.

## createResource migration

| 1.x | 2.0 |
|---|---|
| `const [user] = createResource(id, fetchUser)` | `const user = createMemo(() => fetchUser(id()))` + `<Loading>` |
| `resource.loading` (initial) | `<Loading>` boundary |
| `resource.loading` (refetch in flight) | `isPending(() => user())`; for a pending-looking reload: `affects(user); refresh(user)` |
| `resource.error` | `<Errored>` boundary or effect `error` option |
| `resource.latest` | `latest(user)` |
| `refetch()` | `refresh(user)` |
| `mutate()` | `createOptimisticStore` + `action` |

## SSR/hydration policy per primitive

Accepted on memos, function-form signals/stores, projections, optimistic variants, and effects:

- **`ssrSource`** — `"server"` (default): client seeds from the serialized server value, no re-run (no duplicate fetch). `"hybrid"`: seed then re-run (mixes server data with client-only signals). `"client"`: server value skipped entirely; compute runs only after hydration (server renders whatever you declare in its place, or a `Loading` fallback).
- **`deferStream: true`** (server-only) — holds the SSR stream flush until this primitive's first value resolves, instead of letting the enclosing `<Loading>` fallback into the HTML.
- **`loadingValue` / `seedLoadingValue`** — declared first paint: the computation is born committed with a provisional value; the first flight never suspends readers and is quiet (`isPending` false). The placeholder must be shaped like the real answer. Store-family sources declare `seedLoadingValue: true` (the seed renders).
- **`transparent: true`** (integration tier) — makes a client-only reactive node invisible to hydration (inherits the parent's id, runs live during hydration). For nodes the server never rendered; SSR ignores the option.
