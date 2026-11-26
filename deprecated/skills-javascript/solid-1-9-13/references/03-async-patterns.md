# Async Patterns

Solid handles async data through `createResource`, `<Suspense>`, `<SuspenseList>`, `lazy()`, and transitions. Resources are the primary mechanism — they wrap promises in reactive state and integrate with Suspense for automatic pending UI.

## createResource

```ts
// Without source — runs once
const [data, { mutate, refetch }] = createResource(
  fetcher: (k: true, info: ResourceFetcherInfo) => T | Promise<T>,
  options?: ResourceOptions
);

// With source — re-runs when source changes
const [data, { mutate, refetch }] = createResource(
  source: Accessor<S> | S,
  fetcher: (k: S, info: ResourceFetcherInfo) => T | Promise<T>,
  options?: ResourceOptions
);
```

### Resource Return

```ts
type Resource<T> = Unresolved | Pending | Ready<T> | Refreshing<T> | Errored;

// Accessor — returns current value (throws on error, returns latest during refresh)
data(): T | undefined

// State properties
data.state    // "unresolved" | "pending" | "ready" | "refreshing" | "errored"
data.loading  // true during "pending" or "refreshing"
data.error    // error if in "errored" state
data.latest   // latest value (ignores loading state)
```

### Resource Actions

```ts
mutate(value: T)           // Override value without calling fetcher
refetch(info?: R)          // Re-run fetcher; optional info passed to fetcher's refetching param
```

### Resource Options

```ts
interface ResourceOptions<T, S> {
  initialValue?: T;           // Pre-fill the resource
  name?: string;              // Dev debugging
  deferStream?: boolean;      // Don't stream in SSR (wait for resolution)
  ssrLoadFrom?: "initial" | "server";  // SSR hydration strategy
  storage?: (init) => Signal; // Custom signal storage
  onHydrated?: (key, info) => void;     // Callback after hydration
}
```

### Fetcher Info

```ts
type ResourceFetcherInfo<T, R> = {
  value: T | undefined;    // Previous value
  refetching: R | boolean; // true on refetch, or the value passed to refetch()
};
```

### Examples

```tsx
// Simple fetch
const [user] = createResource(() =>
  fetch("/api/user").then(r => r.json())
);

// With source — re-fetches when ID changes
const [user] = createResource(
  () => userId(),
  id => fetch(`/api/users/${id}`).then(r => r.json())
);

// With initial value
const [settings] = createResource(
  fetchSettings,
  { initialValue: defaultSettings }
);

// Cancel by returning false/null/undefined from source
const [data] = createResource(
  () => shouldFetch() ? query() : null,
  q => fetchData(q)
);

// Manual refetch with info
const [data, { refetch }] = createResource(
  () => searchQuery(),
  (q, { refetching }) => search(q, { fresh: refetching })
);
refetch("force-fresh"); // passes "force-fresh" as refetching
```

### Gotchas

- Source returning `false`, `null`, or `undefined` cancels the fetch
- Multiple source changes during a pending fetch: the last one wins (auto-cancelled)
- Reading `data()` inside `<Suspense>` triggers suspension; reading outside does not
- `data.latest` returns the last known value even during refresh (useful for optimistic UI)

## Suspense

```tsx
import { Suspense } from "solid-js";

<Suspense fallback={<LoadingSpinner />}>
  <ComponentUsingResource />
</Suspense>
```

- Tracks all resources and lazy components inside its tree
- Shows `fallback` while any resource is pending
- Resumes child effects when all resources resolve
- Can be nested — inner Suspense resolves independently

### SSR Streaming

In SSR, `<Suspense>` boundaries become streaming boundaries. Content outside Suspense renders immediately; content inside streams when resources resolve.

```tsx
// Server
<Suspense>
  <HeavyDataComponent />  // Streams when ready
</Suspense>
<Header />               // Renders immediately
```

## SuspenseList

```tsx
import { SuspenseList } from "solid-js";

<SuspenseList revealOrder="forwards" tail="collapsed">
  <Suspense fallback={<Skeleton />}>
    <Item1 />
  </Suspense>
  <Suspense fallback={<Skeleton />}>
    <Item2 />
  </Suspense>
  <Suspense fallback={<Skeleton />}>
    <Item3 />
  </Suspense>
</SuspenseList>
```

- `revealOrder`: `"forwards"` | `"backwards"` | `"together"` — controls render order
- `tail`: `"collapsed"` | `"hidden"` — controls how pending items are shown
- Coordinates multiple Suspense boundaries for list-like loading patterns

## lazy()

```tsx
import { lazy, Suspense } from "solid-js";

const AsyncComponent = lazy(() => import("./AsyncComponent"));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <AsyncComponent prop="value" />
    </Suspense>
  );
}

// Prefetch
AsyncComponent.preload();
```

- Wraps dynamic `import()` in a suspending component
- `.preload()` returns a Promise for prefetching
- Integrates with `<Suspense>` for pending UI
- In SSR, uses `createResource` internally for streaming

## startTransition / useTransition

```tsx
import { startTransition, useTransition } from "solid-js";

// Hook form
function Component() {
  const [pending, start] = useTransition();

  return (
    <>
      <button onClick={() => start(() => setPage(p => p + 1))}>
        Next
      </button>
      {pending() && <Spinner />}
    </>
  );
}

// Imperative form
startTransition(() => {
  setA(a => a + 1);
  setB(b => b + 1);
}).then(() => console.log("transition complete"));
```

- Defers state updates and their effects
- `pending` signal tracks transition state
- Works with Suspense: transitions wait for resources to resolve
- Returns a Promise that resolves when the transition completes

## createDeferred

```tsx
import { createDeferred } from "solid-js";

const [search, setSearch] = createSignal("");
const deferredSearch = createDeferred(search, { timeoutMs: 500 });

// deferredSearch() updates on idle or after 500ms
// Useful for search suggestions, analytics, etc.
```

- Defers signal updates to browser idle time
- `timeoutMs` forces update after the timeout
- Uses `requestIdleCallback` internally

## Pattern: Data Fetching with Loading States

```tsx
function UserPage({ id }: { id: string }) {
  const [user, { refetch }] = createResource(
    () => id,
    id => fetch(`/api/users/${id}`).then(r => {
      if (!r.ok) throw new Error("Not found");
      return r.json();
    })
  );

  return (
    <Suspense fallback={<Spinner />}>
      <Show when={user.error} keyed>
        {(err) => <ErrorMessage error={err} onRetry={refetch} />}
      </Show>
      <Show when={user()} keyed>
        {(user) => (
          <div>
            <h1>{user.name}</h1>
            <p>{user.email}</p>
          </div>
        )}
      </Show>
    </Suspense>
  );
}
```

## Pattern: Dependent Resources

```tsx
function Dashboard() {
  const [user] = createResource(fetchUser);
  const [posts] = createResource(
    () => user()?.id,
    userId => fetch(`/api/users/${userId}/posts`).then(r => r.json())
  );

  // posts automatically fetches when user resolves with an id
  // If user returns null/undefined, posts is cancelled
}
```

## Pattern: Optimistic Updates

```tsx
function CommentList() {
  const [comments, { mutate }] = createResource(fetchComments);

  const addComment = (text: string) => {
    const optimistic = { id: "temp", text, createdAt: Date.now() };
    mutate([...(comments.latest || []), optimistic]);

    fetch("/api/comments", { method: "POST", body: JSON.stringify({ text }) })
      .then(r => r.json())
      .then(saved => {
        mutate(c => (c || []).map(c => c.id === "temp" ? saved : c));
      })
      .catch(() => {
        mutate(c => (c || []).filter(c => c.id !== "temp"));
      });
  };
}
```

## Pattern: Polling

```tsx
function LiveData() {
  const [, { refetch }] = createResource(
    () => true,
    async () => {
      const data = await fetchLatest();
      setTimeout(() => refetch(), 5000);
      return data;
    }
  );
}
```
