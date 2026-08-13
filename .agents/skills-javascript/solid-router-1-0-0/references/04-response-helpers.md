# Response Helpers

Response helpers are thrown from `query` functions or `action` functions to control navigation and data revalidation. They are `Response` objects with special headers that the router intercepts.

## `redirect`

Navigates to a new URL after a query or action completes.

```tsx
import { redirect } from "@solidjs/router";

// In a query — redirect unauthenticated users
const getUser = query(async () => {
  const user = await api.getCurrentUser();
  if (!user) throw redirect("/login");
  return user;
}, "currentUser");

// In an action — redirect after mutation
const createPost = action(async (formData) => {
  const post = await api.createPost(formData);
  throw redirect(`/posts/${post.id}`);
});

// With status code
throw redirect("/login", 301);

// With revalidation hint
throw redirect("/dashboard", { revalidate: getUser.key });
```

| Argument | Type | Description |
|----------|------|-------------|
| `url` | `string` | Target URL (relative or absolute) |
| `init` | `number` or `RouterResponseInit` | Status code (default 302) or options object |

For relative URLs, the router handles navigation. For absolute external URLs, `window.location.href` is set.

## `reload`

Reloads data on the current page without navigation.

```tsx
import { reload } from "@solidjs/router";

const updateTodo = action(async (todo) => {
  await api.updateTodo(todo.id, todo);
  throw reload({ revalidate: getTodo.keyFor(todo.id) });
});
```

Useful when a mutation completes but the user should stay on the same page with fresh data. The `revalidate` option triggers refetches for matching query keys.

## `json`

Returns typed JSON response with optional revalidation.

```tsx
import { json } from "@solidjs/router";

const myAction = action(async (data) => {
  const result = await api.doSomething(data);
  throw json(result, { revalidate: ["users", "posts"] });
});
```

Sets `Content-Type: application/json` and includes the data as a `customBody`. Use when you need to return structured data from an action without redirecting.

## `revalidate`

Invalidates cached query entries, triggering refetches.

```tsx
import { revalidate } from "@solidjs/router";

// Revalidate all entries with a key prefix
revalidate("users");

// Revalidate specific entry
revalidate("users[\"123\"]");

// Revalidate multiple keys
revalidate(["users", "posts"]);

// Revalidate everything
revalidate();

// Use query key helpers
revalidate(getUser.key);       // all "users" entries
revalidate(getUser.keyFor(5)); // specific entry
```

`revalidate` forces cache entries to miss synchronously, then triggers a reactive update via `startTransition`. All `createAsync`/`createResource` consumers of the invalidated queries will refetch.

### In response options

Pass `revalidate` in the options of `redirect()`, `reload()`, or `json()`:

```tsx
throw redirect("/dashboard", { revalidate: getUser.key });
throw reload({ revalidate: getTodo.keyFor(todo.id) });
throw json(data, { revalidate: ["users", "posts"] });
```

The `revalidate` option is sent as the `X-Revalidate` header and processed by the router after the response is handled.

## Cache behavior

The query cache has three tiers:

| Tier | Duration | Trigger |
|------|----------|---------|
| Preload cache | 5 seconds | Link hover, `usePreloadRoute()` |
| Back/forward cache | 3 minutes | Browser back/forward navigation |
| Server dedup | Request lifetime | Same request on server |

User-initiated navigation and link clicks bypass the back/forward cache. Revalidation or new fetches update the cache.

### Cache cleanup

Entries with no active subscribers are cleaned up after 3 minutes. Use `query.clear()` to manually clear everything, or `query.delete(key)` for specific entries.

### `query.get` / `query.set`

```tsx
import { query } from "@solidjs/router";

// Read a cached value
const cached = query.get("users[\"123\"]");

// Seed the cache (e.g., from server data)
query.set("users[\"123\"]", { id: "123", name: "Alice" });
```

`query.set` marks the entry as `"preload"` intent, so it will be refreshed on next actual navigation.
