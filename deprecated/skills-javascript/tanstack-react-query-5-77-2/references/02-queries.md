# Queries

## Contents

- [useQuery](#usequery)
- [Query results and states](#query-results-and-states)
- [Query keys](#query-keys)
- [Query functions](#query-functions)
- [Retries](#retries)
- [Disabling and lazy queries](#disabling-and-lazy-queries)
- [Initial data](#initial-data)
- [Placeholder data](#placeholder-data)
- [Select and other per-query options](#select-and-other-per-query-options)
- [v5 object-only signatures](#v5-object-only-signatures)

## useQuery

```tsx
const result = useQuery({ queryKey, queryFn, ...options }, queryClient?)
```

A query is a declarative dependency on an async data source tied to a unique key. Works with any promise-based method (GET or POST) — for data modification prefer mutations.

Full options (all optional except where noted):

- `queryKey: unknown[]` — **required**; the cache identity
- `queryFn: (context: QueryFunctionContext) => Promise<TData>` — required unless a default query function is configured; must resolve data (never `undefined`) or throw
- `enabled: boolean | (query) => boolean` — `false` disables auto-fetching (see lazy queries)
- `retry: boolean | number | (failureCount, error) => boolean` — `false` off, `true` infinite, number = attempts; default `3` client / `0` server
- `retryOnMount: boolean` — default `true`; whether a query with a cached error retries on mount
- `retryDelay: number | (attempt, error) => number` — default doubles from 1000ms, capped at 30s
- `staleTime: number | (query) => number` — default `0`; ms before data is stale; `Infinity` = never stale
- `gcTime: number | Infinity` — default `5 * 60 * 1000`; ms an inactive cache entry survives; max ~24 days
- `refetchOnMount: boolean | 'always' | (query) => ...` — default `true`; refetch on mount if stale
- `refetchOnWindowFocus: boolean | (query) => ...` — default `true`
- `refetchOnReconnect: boolean | (query) => ...` — default `true`
- `refetchInterval: number | false | (query) => number | false | undefined` — continuous polling
- `refetchIntervalInBackground: boolean` — keep polling while the tab is in the background
- `initialData` / `initialDataUpdatedAt` — seed the cache (persisted, see below)
- `placeholderData` — non-persisted stand-in data
- `select: (data) => TSelected` — derive a stable subset for rendering
- `structuralSharing: boolean | (oldData, newData) => TData` — default on
- `notifyOnChangeProps` — customize tracked properties (`'all'` disables tracking)
- `queryKeyHashFn: (queryKey) => string` — custom key hashing
- `networkMode: 'online' | 'always' | 'offlineFirst'` — default `'online'`
- `throwOnError: boolean | (error, query) => boolean` — rethrow to the nearest error boundary/Suspense boundary
- `meta: Record<string, unknown>` — arbitrary per-query metadata (typed via Register)
- `subscribed: boolean` — default `true`; `false` lets the cache entry skip fetching for this observer
- `scope: { id: string }` — distinguishes observers that share a query

## Query results and states

`status` describes the **data**, `fetchStatus` describes the **queryFn**. Both are always defined; every combination of `status`/`fetchStatus` is possible because of background refetching and stale-while-revalidate.

| Field | Values |
|---|---|
| `status` | `pending` (no data) · `error` · `success` |
| `fetchStatus` | `fetching` (in flight) · `paused` (wanted to fetch, no network) · `idle` |

Result fields: `data`, `error`, `status`, `fetchStatus`, `isPending`, `isError`, `isSuccess`, `isFetching`, `isRefetching` (fetching while already having data), `isStale`, `isPaused`, `isLoading` (= `isPending && isFetching`), `isFetched`, `isFetchedAfterMount`, `isPlaceholderData`, `isInitialLoading` (deprecated, use `isLoading`), `isLoadingError`, `isRefetchError`, `failureCount`, `failureReason`, `dataUpdatedAt`, `errorUpdatedAt`, `promise`, `refetch()`.

Standard pattern:

```tsx
const { isPending, isError, data, error } = useQuery({ queryKey: ['todos'], queryFn: fetchTodoList })
if (isPending) return <span>Loading...</span>
if (isError) return <span>Error: {error.message}</span>
return <ul>{data.map((t) => <li key={t.id}>{t.title}</li>)}</ul>
```

TypeScript narrows `data` to defined once you check `isPending`/`isError` (or `status === 'success'`).

Watch out: a query can be `status: 'pending'` while `fetchStatus: 'paused'` (mounted with no data and no network) — do not show a spinner on `isPending` alone if you support offline.

## Query keys

Keys must be arrays and uniquely describe the data:

```ts
['todos']                      // generic list
['todo', 5]                    // hierarchical — an individual item
['todo', 5, { preview: true }] // plus an options object
['todos', { type: 'done' }]    // parameterized list
```

- Keys are **hashed deterministically**: `['todos', { status, page }]` === `['todos', { page, status }]` === `['todos', { page, status, other: undefined }]`. Array item order, however, matters: `['todos', status, page]` ≠ `['todos', page, status]`.
- Include **every variable** the `queryFn` depends on. Keys act like dependencies — changing them re-caches and auto-refetches (subject to `staleTime`).
- For large apps, organize keys hierarchically (e.g. `['todos', { filter }]`, `['todo', id]`) so prefix matching for invalidation works; key-factory patterns help keep them consistent.

## Query functions

Any function returning a promise. The promise must resolve data or throw/reject — returning an error body without throwing makes the query "succeed" with that error.

The `QueryFunctionContext` passed to `queryFn`:

- `queryKey: QueryKey` — read variables straight from the key instead of closing over them
- `client: QueryClient`
- `signal: AbortSignal` — for cancellation
- `meta: Record<string, unknown> | undefined`
- Infinite queries additionally get `pageParam` and `direction` (deprecated — encode direction into the `pageParam` via `getNextPageParam`/`getPreviousPageParam`)

```tsx
useQuery({ queryKey: ['todos', todoId], queryFn: fetchTodoById })
useQuery({ queryKey: ['todos', todoId], queryFn: () => fetchTodoById(todoId) })
useQuery({ queryKey: ['todos', todoId], queryFn: ({ queryKey }) => fetchTodoById(queryKey[1]) })
```

`fetch` does not throw on HTTP errors — handle it yourself:

```tsx
queryFn: async () => {
  const response = await fetch('/todos/' + todoId)
  if (!response.ok) throw new Error('Network response was not ok')
  return response.json()
}
```

`axios` and similar clients throw by default.

## Retries

- `retry: false` disables, `retry: 6` allows 6 attempts, `retry: true` retries forever, `retry: (failureCount, error) => boolean` for custom logic (e.g. never retry 4xx)
- Default `retryDelay` doubles from 1000ms, capped at 30s: `attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000)`
- While retries are in flight, the thrown error is exposed as `failureReason` (with `failureCount`); it only moves to `error` after the last attempt
- On the server, retries default to `0` to keep SSR fast

## Disabling and lazy queries

`enabled: false` (or a callback) stops automatic fetching. Behavior:

- With cached data → starts `isSuccess`; without data → `pending` + `fetchStatus: 'idle'`
- No fetch on mount, no background refetch, and **invalidation/refetch calls are ignored**
- `refetch()` still works (except with `skipToken`)

Permanently disabling is an anti-pattern — it takes you from declarative to imperative mode. The idiomatic use is a **lazy query** that enables once a dependency exists:

```tsx
const [filter, setFilter] = React.useState('')
const { data } = useQuery({
  queryKey: ['todos', filter],
  queryFn: () => fetchTodos(filter),
  enabled: !!filter,               // off until a filter value exists
})
```

For TypeScript, `skipToken` keeps the options type-safe:

```tsx
import { skipToken, useQuery } from '@tanstack/react-query'

const { data } = useQuery({
  queryKey: ['todos', filter],
  queryFn: filter ? () => fetchTodos(filter) : skipToken,
})
```

Use `isLoading` (= `isPending && isFetching`) for lazy-query spinners — a lazy query is `pending` but not `fetching` before it enables.

## Initial data

`initialData` prepopulates the cache and skips the initial loading state. **It is persisted to the cache**, so only pass complete, real data:

```tsx
const result = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  initialData: initialTodos,
  initialDataUpdatedAt: () => Date.now(), // control freshness
})
```

`initialData` counts as just-fetched, so with the default `staleTime: 0` the query refetches immediately on mount (showing `initialData` while it does). Set `staleTime` accordingly, or `initialDataUpdatedAt`/`staleTime` together to encode the true age.

## Placeholder data

`placeholderData` behaves like `initialData` but is **not persisted to the cache** — ideal for partial or fake data (e.g. list preview items while the full object loads). The query starts in `success` state with `isPlaceholderData: true`:

```tsx
const { data, isPlaceholderData, isFetching } = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  placeholderData: keepPreviousData,      // or a value, or a function (prevData, query) => data
})
```

- As a function, it receives previous data and the query — the common pattern `placeholderData: keepPreviousData` (exported helper) avoids flicker between pages of a list
- Memoize expensive placeholder computation with `useMemo`
- For infinite queries, placeholders must match the `{ pages, pageParams }` shape

## Select and other per-query options

- `select: (data) => TSelected` — derives a subset; the component only re-renders when the selected value changes. It operates on cached successful data — **do not throw in `select`** (a thrown select yields `data === undefined` with `isSuccess === true`). Memoize it (`useCallback` or a stable extracted function) or it re-runs every render
- `notifyOnChangeProps` — the result object is a Proxy that re-renders only when *used* properties change; object rest destructuring defeats this. `notifyOnChangeProps: 'all'` disables the optimization
- `throwOnError` — rethrows query errors to the nearest React error boundary or `<Suspense>` boundary (with `useSuspenseQuery`); useful for full-screen error UI
- `subscribed: false` — the observer does not trigger fetches (useful for read-only cache access)
- `queryKeyHashFn` — custom deterministic hashing for unusual key types

## v5 object-only signatures

All hooks and client methods accept one options object:

```tsx
useQuery({ queryKey, queryFn, ...options })
useInfiniteQuery({ queryKey, queryFn, ...options })
useMutation({ mutationFn, ...options })
useIsFetching({ queryKey, ...filters })
useIsMutating({ mutationKey, ...filters })

queryClient.fetchQuery({ queryKey, queryFn, ...options })
queryClient.prefetchQuery({ queryKey, queryFn, ...options })
queryClient.invalidateQueries({ queryKey, ...filters })
queryClient.refetchQueries({ queryKey, ...filters })
queryClient.removeQueries({ queryKey, ...filters })
queryClient.getQueriesData({ queryKey, ...filters })
queryClient.setQueriesData({ queryKey, ...filters }, updater, options)
// ... and the rest of the QueryClient API
```

`queryClient.getQueryData(key)` and `getQueryState(key)` now take only the key. A codemod exists for the mechanical migration (see the v5 migration notes in the package).
