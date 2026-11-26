# Data APIs

Solid Router provides a data fetching and mutation layer built on top of its preload mechanism. These APIs are optional but enable powerful patterns like parallel data fetching, deduplication, caching, and revalidation.

## `query`

Creates a cached, deduplicated async function.

```tsx
import { query } from "@solidjs/router";

const getUser = query(async (id: string) => {
  return (await fetch(`/api/users/${id}`)).json();
}, "users");
```

The second argument is the cache key prefix. `query` provides:

- **Server-side deduplication** — for the lifetime of the request
- **Preload cache** — 5 seconds in the browser (from hover/preload)
- **Back/forward cache** — up to 3 minutes for browser navigation
- **Reactive revalidation** — trigger refetches by key

### Key helpers

```tsx
getUser.key;              // "users" — the base key
getUser.keyFor("123");    // "users[\"123\"]" — key for specific args

// Revalidate all "users" entries
revalidate(getUser.key);

// Revalidate specific entry
revalidate(getUser.keyFor("123"));
```

### Cache management

```tsx
import { query } from "@solidjs/router";

query.get("users[\"123\"]");   // Get cached value by key
query.set("users[\"123\"]", { id: "123", name: "Alice" }); // Set cached value
query.delete("users[\"123\"]"); // Delete specific entry
query.clear(); // Clear all cache
```

### Using in preload functions

```tsx
function preloadUser({ params, location, intent }) {
  // Fire the fetch; void to not block
  void getUser(params.id);
}

<Route path="/users/:id" component={User} preload={preloadUser} />;
```

### Using in components with `createAsync`

```tsx
import { createAsync } from "@solidjs/router";

function User(props) {
  const user = createAsync(() => getUser(props.params.id));

  return (
    <Suspense fallback={<Spinner />}>
      <h1>{user()?.name}</h1>
    </Suspense>
  );
}
```

`createAsync` tracks reactively like `createMemo` — when `props.params.id` changes, the query re-runs. Reading the result before resolution triggers `<Suspense>`.

## `createAsync`

A reactive async primitive (preview of Solid 2.0 API).

```tsx
import { createAsync } from "@solidjs/router";

// Basic usage
const user = createAsync(() => fetchUser(params.id));

// With options
const user = createAsync(
  () => fetchUser(params.id),
  { name: "user", initialValue: null }
);

// Access current value (suspends if not ready)
user();

// Access latest resolved value (no suspend)
user.latest; // will be removed in future
```

`createAsync` is a wrapper over `createResource` with simpler API:
- Function tracks like `createMemo` — reactive dependencies auto-update
- Reading before resolution triggers `<Suspense>` / transitions
- Returns `AccessorWithLatest<T>` with `.latest` for non-suspending access

## `createAsyncStore`

Like `createAsync` but with a deeply reactive store.

```tsx
import { createAsyncStore } from "@solidjs/router";

const todos = createAsyncStore(() => fetchTodos());

// Fine-grained reactivity on nested properties
todos()[0].title; // tracks only this property
todos().length;   // tracks only length
```

Useful for large models where you need fine-grained updates. Supports `reconcile` options from `solid-js/store`.

```tsx
const data = createAsyncStore(
  () => fetchData(),
  { reconcile: { spreadArrays: true } }
);
```

## `action`

Creates a data mutation function with revalidation support.

```tsx
import { action, redirect } from "@solidjs/router";

const updateTodo = action(async (formData: FormData) => {
  const id = Number(formData.get("id"));
  await fetch(`/api/todos/${id}`, {
    method: "PUT",
    body: JSON.stringify({ done: true }),
  });
  throw redirect(`/todos/${id}`);
});
```

### Form integration

```tsx
<form action={updateTodo} method="post">
  <input type="hidden" name="id" value={todo.id} />
  <button type="submit">Complete</button>
</form>
```

Always use `method="post"`. Actions only work with POST requests.

### Binding arguments with `.with()`

```tsx
const deleteTodo = action(async (id: number) => {
  await fetch(`/api/todos/${id}`, { method: "DELETE" });
});

<form action={deleteTodo.with(todo.id)} method="post">
  <button type="submit">Delete</button>
</form>
```

`.with()` pre-binds arguments, avoiding hidden form fields.

### Programmatic invocation

```tsx
import { useAction } from "@solidjs/router";

const submit = useAction(deleteTodo);
submit(todo.id); // calls the action directly
```

`useAction` wraps the action with router context. Works outside of form contexts.

### Named actions (SSR)

```tsx
const myAction = action(async (args) => { /* ... */ }, "my-action");
```

Provide a name for stable serialization across SSR. Required when actions are serialized as form attributes.

### Action options

```tsx
const myAction = action(async (args) => { /* ... */ }, {
  name: "my-action",
  onComplete: (submission) => {
    if (submission.error) {
      console.error("Action failed:", submission.error);
    }
  },
});
```

`onComplete` fires when the action resolves (doesn't work without JavaScript).

## `useSubmission` / `useSubmissions`

Track action state for optimistic updates.

```tsx
import { useSubmission, useSubmissions } from "@solidjs/router";

const submission = useSubmission(deleteTodo);
const submissions = useSubmissions(deleteTodo, (input) => input.type === "urgent");

// Single submission (latest)
submission.pending;  // boolean
submission.input;    // arguments passed
submission.result;   // resolved value
submission.clear();  // clear submission state
submission.retry();  // re-run the action

// All submissions
submissions.length;
submissions.pending; // true if any are pending
```

Use for optimistic UI, loading indicators, or retry logic.

## Throwing response helpers

Actions and queries can throw response helpers to control navigation:

```tsx
const myAction = action(async (data) => {
  await doMutation(data);

  // Redirect after mutation
  throw redirect("/success");

  // Or reload current page data
  throw reload({ revalidate: getUser.keyFor(data.id) });

  // Or return typed JSON
  throw json({ success: true }, { revalidate: ["users"] });
});
```

Throwing is intentional — it signals that the function ends execution at that point and avoids type interference.
