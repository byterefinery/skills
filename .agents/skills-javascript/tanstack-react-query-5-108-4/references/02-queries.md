# Queries

## useQuery Basics

A query is a declarative dependency on an asynchronous source of data tied to a **unique key**. Subscribe with `useQuery`, passing at least `queryKey` and a `queryFn` that returns a promise resolving data or throwing an error:

```tsx
const info = useQuery({ queryKey: ['todos'], queryFn: fetchTodoList })
```

The key is used for refetching, caching, and sharing the query across the app. Any promise-based method works (GET, POST, GraphQL). For operations that modify server data, use `useMutation` instead.

### Result states and the standard render pattern

A query is in exactly one `status`: `pending` (no data yet), `error`, or `success`. `error` is available on error, `data` on success, `isFetching` is `true` whenever a fetch is in flight (including background refetches).

```tsx
function Todos() {
  const { isPending, isError, data, error } = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodoList,
  })

  if (isPending) return <span>Loading...</span>
  if (isError) return <span>Error: {error.message}</span>
  return (
    <ul>
      {data.map((todo) => <li key={todo.id}>{todo.title}</li>)}
    </ul>
  )
}
```

TypeScript narrows `data` to defined after the pending/error checks.

### fetchStatus

`status` describes the **data**; `fetchStatus` describes the **queryFn**:

- `fetchStatus: 'fetching'` — the queryFn is running
- `fetchStatus: 'paused'` — wanted to fetch but is paused (offline; see Network Mode)
- `fetchStatus: 'idle'` — not fetching

All combinations are possible because of background refetches: a `success` query can be `fetching`, and a `pending` query can be `paused` (no network). Check `isFetching` (not just `isPending`) for refresh indicators, and `isLoading` (`isPending && isFetching`) for the true initial load.

## Query Keys

Keys must be arrays, JSON-serializable, and **unique to the query's data**:

```tsx
useQuery({ queryKey: ['todos'], ... })                  // a list
useQuery({ queryKey: ['todo', 5], ... })                // an item by id
useQuery({ queryKey: ['todo', 5, { preview: true }], ... }) // with options
useQuery({ queryKey: ['todos', { type: 'done' }], ... }) // filtered list
```

Keys are **hashed deterministically** — object property order does not matter (`{ status, page }` === `{ page, status }`, and `undefined` properties are ignored), but array item order does (`['todos', status, page]` !== `['todos', page, status]`).

If your query function depends on a variable, include it in the key. Keys act as dependencies: when a variable changes, the query refetches automatically (subject to `staleTime`).

## Query Functions

`queryFn` receives a context object:

```tsx
const { data } = useQuery({
  queryKey: ['todos'],
  queryFn: async ({ signal, meta, client }) => {
    // signal — AbortSignal; aborted when the query is cancelled
    // meta   — value passed via the `meta` option
    // client — the QueryClient
    const res = await fetch('/todos', { signal })
    return res.json()
  },
})
```

- Pass `signal` to `fetch` / `axios` / XHR to make requests cancellable (see 08).
- By default, queries that unmount before resolving are **not** cancelled — the data lands in the cache. Consuming the `signal` changes that: the promise is cancelled and the query reverts to its previous state.
- A `meta` option can attach arbitrary metadata to the query, readable from the context.
- `meta` types and global error types can be registered via the `Register` interface (see 07).

## Retries

When a `queryFn` throws, the query retries automatically (default `3`, server `0`) with a backoff delay (default: doubles from 1000ms, capped at 30000ms):

- `retry: false` disables retries; `retry: 6` sets a count; `retry: true` retries forever
- `retry: (failureCount, error) => boolean` — custom logic; `failureCount` starts at `0` for the first retry
- `retryDelay: number | (attemptIndex) => number` — override the delay (integer = constant delay)
- While retries are in flight, the error is exposed via the `failureReason` property; it moves to `error` only after the last attempt fails
- Retries pause when offline (network mode `online`) and when the tab is inactive with `refetchIntervalInBackground` off — background retry behavior is covered in 08

For continuous background error recovery, a documented pattern is `retry: false` plus a `refetchInterval` function that returns a shorter interval while `query.state.status === 'error'`, with `refetchIntervalInBackground: true`.

## Lazy / Disabled Queries

`enabled` accepts a boolean or a callback returning a boolean:

- `enabled: false` with cached data → starts `success`; without cached data → starts `pending` + `fetchStatus: 'idle'`
- No automatic fetch on mount, no background refetches, and the query **ignores** `invalidateQueries` / `refetchQueries` calls
- `refetch()` from the result still works (it does not work with `skipToken` — see below)

Permanently disabling a query is an anti-pattern — it opts out of background refetches and moves you into imperative mode. The idiomatic use is a **lazy query** that defers the first fetch until a dependency exists:

```tsx
const [filter, setFilter] = React.useState('')

const { data } = useQuery({
  queryKey: ['todos', filter],
  queryFn: () => fetchTodos(filter),
  enabled: !!filter, // disabled until the filter is applied
})
```

Because a disabled query is `pending` without fetching, `isPending` is true while it is idle — use `isLoading` (`isPending && isFetching`) to show a loading spinner.

### Type-safe disabling with skipToken

In TypeScript, `skipToken` (exported from the package) disables a query while keeping types safe:

```tsx
import { skipToken, useQuery } from '@tanstack/react-query'

const { data } = useQuery({
  queryKey: ['todos', filter],
  queryFn: filter ? () => fetchTodos(filter) : skipToken,
})
```

**Important**: `refetch()` from `useQuery` does not work with `skipToken` — it throws `Missing queryFn` because there is no query function to execute. If you need manual triggering, use `enabled: false` instead.

## Initial Data (`initialData`)

`initialData` prepopulates the cache if empty so the query skips the loading state. It is **persisted to the cache** — do not use it for partial or fake data (use `placeholderData`).

- Treated as totally fresh by default; combined with `staleTime: 0` it refetches immediately on mount
- `initialDataUpdatedAt` — a JS timestamp (ms) of when the initial data was last updated, so `staleTime` can decide whether to refetch. With cache-derived initial data, pass the source query's `dataUpdatedAt`:

```tsx
const result = useQuery({
  queryKey: ['todo', todoId],
  queryFn: () => fetch(`/todos/${todoId}`),
  initialData: () => queryClient.getQueryData(['todos'])?.find((d) => d.id === todoId),
  initialDataUpdatedAt: () => queryClient.getQueryState(['todos'])?.dataUpdatedAt,
})
```

- Can be a **function** (executed once at query initialization) to avoid recomputing expensive lookups every render
- Conditional seeding — read `queryClient.getQueryState(['todos'])` and only return data fresher than your cutoff; return `undefined` to fall through to a hard loading fetch
- If data already exists in the cache, `initialData` **never overwrites it**, even if the new data is fresher

If you want to treat the data as prefetched rather than initial, use `queryClient.query(...)` to populate the cache beforehand.

## Placeholder Data (`placeholderData`)

`placeholderData` makes the query behave as if it already has data (starts in `success` state, `isPlaceholderData: true`), but **the data is not persisted to the cache**. Useful for partial/fake data while the real fetch runs.

- Value form: `placeholderData: placeholderTodos`
- Function form receives the **previous query's** data and query — the classic pattern for pagination (see `keepPreviousData`):

```tsx
useQuery({
  queryKey: ['todos', id],
  queryFn: () => fetch(`/todos/${id}`),
  placeholderData: (previousData, previousQuery) => previousData, // identity
})
```

- Cache lookup form: derive the placeholder from another cached query (e.g. a preview list entry for a detail view)
- For pagination, the package exports a ready-made `keepPreviousData` function to pass as `placeholderData` (replaces the removed `keepPreviousData: true` option and `isPreviousData` flag — use `isPlaceholderData` instead)

Caveats vs old `keepPreviousData`: placeholder data puts the query in `success` state (even if the previous query errored) and `dataUpdatedAt` stays `0` while showing placeholder data.

For infinite queries, `initialData` / `placeholderData` must conform to the `{ pages, pageParams }` shape.
