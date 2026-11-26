---
name: tanstack-react-query-5-77-2
description: TanStack Query 5.77.2 for React — the server-state management library (formerly React Query). Covers useQuery, useMutation, useInfiniteQuery, query keys, caching and invalidation, prefetching, Suspense, SSR hydration, retries, optimistic updates, and TypeScript typing. Use when fetching, caching, or syncing server state in a React app, or when migrating code to the v5 object-only API.
license: MIT
compatibility: Requires React 18+ and @tanstack/react-query 5.77.2. TypeScript 4.7+ recommended for full type inference. Works with ReactDOM and React Native.
metadata:
  tags:
    - javascript
    - react
    - data-fetching
    - server-state
    - caching
---

# tanstack-react-query 5.77.2

## Overview

TanStack Query (formerly React Query) manages **server state** — fetching, caching, synchronizing and updating data that lives on a server. Server state is persisted remotely, shared, and can change underneath your app, so the library handles caching, request deduping, background refetching, garbage collection and structural sharing out of the box.

The three pillars:

1. **Queries** — declarative, keyed subscriptions to async data (`useQuery`)
2. **Mutations** — writes and server side-effects (`useMutation`)
3. **Invalidation** — marking cached queries stale after mutations (`queryClient.invalidateQueries`)

v5 rule: every hook and client method takes a **single options object**. The v4 `(key, fn, options)` overloads are gone.

Minimal setup:

```tsx
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Example />
    </QueryClientProvider>
  )
}

function Example() {
  const { isPending, isError, data, error } = useQuery({
    queryKey: ['repoData'],
    queryFn: () =>
      fetch('https://api.github.com/repos/TanStack/query').then((r) => r.json()),
  })
  if (isPending) return <p>Loading...</p>
  if (isError) return <p>Error: {error.message}</p>
  return <h1>{data.name}</h1>
}
```

## Usage

Core loop — fetch, mutate, invalidate:

```tsx
function Todos() {
  const queryClient = useQueryClient()
  const query = useQuery({ queryKey: ['todos'], queryFn: getTodos })
  const mutation = useMutation({
    mutationFn: postTodo,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['todos'] }),
  })

  return (
    <div>
      <ul>{query.data?.map((todo) => <li key={todo.id}>{todo.title}</li>)}</ul>
      <button onClick={() => mutation.mutate({ id: Date.now(), title: 'Do laundry' })}>
        Add
      </button>
    </div>
  )
}
```

- `useQuery({ queryKey, queryFn })` — subscribe to cached data; `queryFn` returns a promise that resolves data or throws
- `useMutation({ mutationFn })` — returns `mutate` / `mutateAsync` plus `isIdle` / `isPending` / `isSuccess` / `isError`
- After any write, invalidate the affected keys so reads refetch in the background
- Lazy or conditional fetch — `enabled: !!userId`, or type-safe `queryFn: cond ? fn : skipToken`
- Infinite lists — `useInfiniteQuery` with `initialPageParam` + `getNextPageParam`
- Sharing options between hooks and client methods — the `queryOptions()` helper (also restores TS inference)
- Suspense — `useSuspenseQuery` / `useSuspenseQueries` / `useSuspenseInfiniteQuery` inside `<Suspense>` boundaries
- SSR — prefetch on the server, pass `dehydrate(queryClient)` to the client, wrap with `<HydrationBoundary state={...}>`

Full details per topic in References below.

## Important Defaults

These catch new users off guard:

| Default | Value | Effect |
|---|---|---|
| `staleTime` | `0` | Cached data is stale immediately; stale queries refetch in the background on mount, window focus, and network reconnect |
| `gcTime` | `5 min` | Inactive (no active observers) cache entries are garbage collected after 5 minutes |
| `retry` | `3` (client), `0` (server) | Failed queries retry silently with exponential backoff (doubles from 1000ms, capped at 30s) |
| `refetchOnMount` | `true` | Stale data refetches when a new observer mounts |
| `refetchOnWindowFocus` | `true` | Stale data refetches in the background when the window regains focus |
| `refetchOnReconnect` | `true` | Stale data refetches when the network reconnects |
| `structuralSharing` | on | `data` keeps its reference when the value did not actually change |

All are configurable globally via `new QueryClient({ defaultOptions: { queries: {...} } })` or per-query.

## Query Keys

Keys are arrays, hashed deterministically. Object property order inside a key does not matter; array item order does.

```ts
['todos']                        // a list
['todo', 5]                      // a single item
['todos', { type: 'done' }]      // filtered list; object props are order-insensitive
['todos', { status, page }]      // equal to { page, status }; undefined props are ignored
['todos', status, page]          // NOT equal to ['todos', page, status] — array order matters
```

Every variable your `queryFn` depends on must be in the key. The key is the cache identity and the refetch trigger — when a key element changes, the query refetches (subject to `staleTime`).

## Query States

`status` is about the **data**, `fetchStatus` is about the **queryFn**:

- `status` — `pending` (no data yet) | `error` | `success`
- `fetchStatus` — `fetching` (in flight) | `paused` (offline) | `idle`
- Derived booleans — `isPending`, `isError`, `isSuccess`, `isFetching`, `isRefetching`, `isStale`, `isPaused`, `isLoading` (= `isPending && isFetching`, the right flag for lazy queries)

Standard render pattern — check `isPending`, then `isError`, then render `data`. `data` is `undefined` until success. A query can be `pending` while `fetchStatus` is `paused` (offline), so a loading spinner on `isPending` alone can be misleading.

## Gotchas

- **v5 takes one object only** — `useQuery(key, fn)`, `queryClient.invalidateQueries(key)`, `fetchQuery(key, fn, options)` are all gone. A jscodeshift codemod ships in the package (`@tanstack/react-query/build/codemods/src/v5/remove-overloads/remove-overloads.cjs`).
- **Query callbacks were removed** — `onSuccess` / `onError` / `onSettled` no longer exist on `useQuery` (they remain on `useMutation`). Use `select`, `throwOnError`, or component logic.
- **`fetch` does not throw on 4xx/5xx** — check `response.ok` and throw yourself, or the query "succeeds" with an error body.
- **Permanently disabling queries is an anti-pattern** — `enabled: false` opts out of background refetches and ignores invalidation. Use it for lazy queries (deferring the first fetch until a dependency exists), not as a permanent off switch. `refetch()` does not work with `skipToken`.
- **`initialData` is persisted to the cache** — for partial or fake data use `placeholderData` (not persisted, flagged by `isPlaceholderData`).
- **`select` is not for errors** — throwing in `select` leaves `data` undefined with `isSuccess` true. Throw in `queryFn` instead.
- **Rest-destructuring the result breaks render optimization** — `const { ...rest } = useQuery(...)` disables property tracking. Destructure only the properties you actually use.
- **Infinite queries allow a single in-flight fetch** — guard `fetchNextPage` with `!isFetching` or pass `{ cancelRefetch: false }`.
- **SSR — create the `QueryClient` per request** — a module-level client shares (and leaks) data between users.
- **Cache writes must be immutable** — use the `setQueryData(key, updater)` pattern; never mutate cached objects in place.
- **Structural sharing only works on JSON-compatible data** — anything else is always considered changed.
- **`refetchInterval` callbacks receive the `query`, not `data`** — access `query.state.data` (untransformed by `select`).

## References

- [01-setup-and-defaults](references/01-setup-and-defaults.md) — installation, QueryClient, provider, global options, devtools
- [02-queries](references/02-queries.md) — useQuery options, query keys, query functions, states, retries, lazy queries, initial and placeholder data
- [03-mutations](references/03-mutations.md) — useMutation, lifecycle callbacks, invalidation and updates from mutation responses, optimistic updates
- [04-cache-and-prefetching](references/04-cache-and-prefetching.md) — cache lifecycle, QueryClient methods, filters, prefetching patterns, router integration, persistence
- [05-infinite-queries](references/05-infinite-queries.md) — pagination and infinite scroll, maxPages, no-cursor and bi-directional lists
- [06-suspense-and-ssr](references/06-suspense-and-ssr.md) — Suspense hooks, SSR, dehydrate/hydrate, HydrationBoundary, streaming, error handling
- [07-typescript](references/07-typescript.md) — type inference, Register augmentation, queryOptions, typing errors and meta
- [08-performance-testing-network](references/08-performance-testing-network.md) — render optimizations, request waterfalls, network modes, query cancellation, testing
