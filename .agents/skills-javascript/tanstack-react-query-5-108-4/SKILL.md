---
name: tanstack-react-query-5-108-4
description: TanStack Query 5.108.4 for React — the server-state management library (formerly React Query). Covers useQuery, useMutation, useInfiniteQuery, useQueries, query keys, caching and invalidation, the queryClient.query prefetch API (replacing the deprecated fetchQuery and prefetchQuery methods), staleTime 'static', Suspense, SSR hydration, retries, optimistic updates, and TypeScript typing. Use when fetching, caching, or syncing server state in a React app, or when migrating code to the object-only API.
license: MIT
compatibility: Requires React 18+ (peer react ^18 || ^19) and @tanstack/react-query 5.108.4. TypeScript 4.7+ required; library types track the DefinitelyTyped support window (5.7+ at this release). Works with ReactDOM and React Native. Optional extras — @tanstack/react-query-devtools, @tanstack/react-query-persist-client, @tanstack/eslint-plugin-query.
metadata:
  tags:
    - javascript
    - react
    - data-fetching
    - server-state
    - caching
---

# tanstack-react-query 5.108.4

## Overview

TanStack Query (formerly React Query) manages **server state** — fetching, caching, synchronizing and updating data that lives on a server. Server state is persisted remotely, shared, and can change underneath your app, so the library handles caching, request deduping, background refetching, garbage collection and structural sharing out of the box. It is transport-agnostic — REST, GraphQL, or any Promise.

The three pillars:

1. **Queries** — declarative, keyed subscriptions to async data (`useQuery`)
2. **Mutations** — writes and server side-effects (`useMutation`)
3. **Invalidation** — marking cached queries stale after mutations (`queryClient.invalidateQueries`)

API rules in this version:

- Every hook and client method takes a **single options object** — the v4 positional `(key, fn, options)` overloads are gone.
- Prefetching/fetching uses the new `queryClient.query(options)` and `queryClient.infiniteQuery(options)` methods. The older `fetchQuery`, `prefetchQuery`, `ensureQueryData`, `fetchInfiniteQuery`, `prefetchInfiniteQuery`, `ensureInfiniteQueryData` are **deprecated** and will be removed in the next major version.
- `staleTime` accepts a new value `'static'` — never refetch, even on `invalidateQueries()`.

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
    queryFn: async () => {
      const response = await fetch('https://api.github.com/repos/TanStack/query')
      if (!response.ok) throw new Error('Failed to fetch repo data')
      return response.json()
    },
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
      <button
        onClick={() => mutation.mutate({ id: Date.now(), title: 'Do laundry' })}>
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
- Infinite lists — `useInfiniteQuery` with `initialPageParam` (required) + `getNextPageParam`
- Parallel/dynamic lists — `useQueries({ queries: [...] })` returns an array of results
- Sharing options between hooks and client methods — the `queryOptions()` / `infiniteQueryOptions()` / `mutationOptions()` helpers (also restore TS inference)
- Prefetching — `queryClient.query({ queryKey, queryFn, ... }).catch(noop)` (`noop` is exported by the package); for Suspense flows use the `usePrefetchQuery` / `usePrefetchInfiniteQuery` hooks
- Suspense — `useSuspenseQuery` / `useSuspenseQueries` / `useSuspenseInfiniteQuery` inside `<Suspense>` boundaries; `data` is guaranteed defined
- SSR — prefetch in the loader with `await queryClient.query(...)`, pass `dehydrate(queryClient)` to the client, wrap with `<HydrationBoundary state={...}>`

Full details per topic in References below.

## Important Defaults

These catch new users off guard:

| Default | Value | Effect |
|---|---|---|
| `staleTime` | `0` | Cached data is stale immediately; stale queries refetch in the background on mount, window focus, and network reconnect |
| `staleTime: 'static'` | — | Never refetch, even if `invalidateQueries()` targets the query; also blocks `refetchOn*` set to `"always"` |
| `staleTime: Infinity` | — | No staleness-based refetches, but `invalidateQueries()` can still invalidate it |
| `gcTime` | `5 min` (client), `Infinity` (server) | Inactive (no active observers) cache entries are garbage collected after 5 minutes |
| `retry` | `3` (client), `0` (server) | Failed queries retry silently with exponential backoff (doubles from 1000ms, capped at 30s) |
| `refetchOnMount` | `true` | Stale data refetches when a new observer mounts |
| `refetchOnWindowFocus` | `true` | Stale data refetches in the background when the window regains focus (via `visibilitychange` only) |
| `refetchOnReconnect` | `true` | Stale data refetches when the network reconnects |
| `networkMode` | `'online'` | Queries pause (`fetchStatus: 'paused'`) when offline instead of failing |
| `structuralSharing` | on | `data` keeps its reference when the value did not actually change (JSON-compatible values only) |

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
- Derived booleans — `isPending`, `isError`, `isSuccess`, `isFetching`, `isRefetching`, `isStale`, `isPaused`, `isPlaceholderData`, `isLoading` (= `isPending && isFetching`, the right flag for lazy queries)

Standard render pattern — check `isPending`, then `isError`, then render `data`. `data` is `undefined` until success. A query can be `pending` while `fetchStatus` is `paused` (offline), so a loading spinner on `isPending` alone can be misleading.

## Gotchas

- **v5 takes one object only** — `useQuery(key, fn)`, `queryClient.invalidateQueries(key)`, `useQueries([ ... ])` are all gone. A jscodeshift codemod ships in the package (`@tanstack/react-query/build/codemods/v5/remove-overloads/remove-overloads.cjs`); run it, then reformat.
- **`prefetchQuery` / `fetchQuery` / `ensureQueryData` are deprecated** — replaced by `queryClient.query(options)` and `queryClient.infiniteQuery(options)` (removed in the next major). `ensureQueryData` maps to `query({ ...options, staleTime: 'static' })`; fire-and-forget prefetches swallow errors with `.catch(noop)`.
- **Query callbacks were removed** — `onSuccess` / `onError` / `onSettled` no longer exist on `useQuery` (they remain on `useMutation`). Use `select`, `throwOnError`, or component logic.
- **`fetch` does not reject on 4xx/5xx** — the docs' own examples check `response.ok` and throw; without that, the query "succeeds" with an error body.
- **Permanently disabling queries is an anti-pattern** — `enabled: false` opts out of background refetches and ignores `invalidateQueries`. Use it for lazy queries (deferring the first fetch until a dependency exists). `refetch()` does not work with `skipToken` — it throws `Missing queryFn`; use `enabled: false` if you need manual `refetch()`.
- **`initialData` is persisted to the cache** — for partial or fake data use `placeholderData` (not persisted, flagged by `isPlaceholderData`). `keepPreviousData` is now a function you pass to `placeholderData`, not an option.
- **`select` is not for errors** — throwing in `select` leaves `data` undefined with `isSuccess` true. Throw in `queryFn` instead. An inline `select` re-runs every render; memoize it.
- **Rest-destructuring the result breaks render optimization** — `const { ...rest } = useQuery(...)` disables property tracking (the proxy get trap fires for every property). Destructure only the properties you actually use.
- **Infinite queries allow a single in-flight fetch** — guard `fetchNextPage` with `!isFetching` or pass `{ cancelRefetch: false }`. `initialPageParam` is required, and returning `null` from `getNextPageParam` means "no more pages".
- **Mutations do not retry by default** — only queries do. Paused (offline) mutations are retried in order on reconnect; `scope: { id }` serializes mutations sharing the same id.
- **SSR — create the `QueryClient` per request** — a module-level client shares (and leaks) data between users. On the server `gcTime` defaults to `Infinity`; a finite `gcTime` schedules timers that keep the whole request (AsyncLocalStorage) in memory, and `gcTime: 0` can cause hydration errors.
- **Dehydration only includes successful queries by default**, and the dehydrated state is JSON-shaped — `undefined`, `Date`, `Map`, `Error` etc. do not survive framework serialization (use superjson), and custom SSR embedding must escape output (serialize-javascript / devalue) to avoid XSS.
- **Structural sharing only works on JSON-compatible data** — anything else is always considered changed.
- **`refetchInterval` / `refetchOn*` callbacks receive the `query`, not `data`** — access `query.state.data` (untransformed by `select`).
- **`queryClient.getQueryData` / `getQueryState` accept only the `queryKey`** — the old second filter argument is gone.
- **Renames from v4** — `cacheTime` → `gcTime`, `useErrorBoundary` → `throwOnError`, `status: 'loading'` → `'pending'`, `isInitialLoading` → `isLoading` (now `isPending && isFetching`), `hashQueryKey` → `hashKey`, `Hydrate` → `HydrationBoundary`, `useHydrate` removed.

## References

- [01-setup-and-defaults](references/01-setup-and-defaults.md) — installation, QueryClient, provider, global options, default query function, devtools, managers
- [02-queries](references/02-queries.md) — useQuery options, query keys, query functions, states, retries, lazy queries (enabled/skipToken), initial and placeholder data
- [03-mutations](references/03-mutations.md) — useMutation, lifecycle callbacks, mutation scopes, invalidation and updates from mutation responses, optimistic updates, offline/persisted mutations
- [04-cache-and-prefetching](references/04-cache-and-prefetching.md) — cache lifecycle, queryClient.query/infiniteQuery, filters, QueryClient methods, prefetching patterns, router integration, persistence plugins
- [05-infinite-queries](references/05-infinite-queries.md) — pagination and infinite scroll, maxPages, no-cursor and bi-directional lists, manual cache updates
- [06-suspense-and-ssr](references/06-suspense-and-ssr.md) — Suspense hooks, error reset boundaries, SSR, dehydrate/hydrate, HydrationBoundary, streaming, serialization, server caveats
- [07-typescript](references/07-typescript.md) — type inference, Register augmentation, queryOptions/mutationOptions/infiniteQueryOptions, skipToken
- [08-performance-testing-network](references/08-performance-testing-network.md) — request waterfalls, render optimizations, network modes, polling, query cancellation, window focus, React Native, testing
