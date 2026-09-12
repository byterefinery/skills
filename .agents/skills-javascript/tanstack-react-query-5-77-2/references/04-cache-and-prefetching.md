# Cache and Prefetching

## Contents

- [Cache lifecycle](#cache-lifecycle)
- [QueryClient methods](#queryclient-methods)
- [Filters](#filters)
- [Invalidation and matching](#invalidation-and-matching)
- [Prefetching](#prefetching)
- [Router integration](#router-integration)
- [Priming the cache manually](#priming-the-cache-manually)
- [Persistence](#persistence)

## Cache lifecycle

With defaults (`staleTime: 0`, `gcTime: 5 min`):

1. A `useQuery` mounts with no cached data → hard loading state, network request
2. The response is cached under the key; data is marked stale immediately (`staleTime: 0`)
3. A second instance with the same key mounts → cached data returned synchronously, background refetch triggered; both instances update when it finishes (identical `queryFn`s or not — same key, same cache entry)
4. All instances unmount → query becomes **inactive**, GC timer (`gcTime`) starts
5. A new instance mounts before the timer expires → cached data returned immediately, background refetch runs
6. No instances appear within `gcTime` → cache entry is deleted

Scroll restoration "just works" as long as data survives within `gcTime` — navigating back re-mounts the same key and gets the data synchronously.

## QueryClient methods

| Method | Purpose |
|---|---|
| `fetchQuery(options)` | Run a query and **return its data**; throws on error |
| `fetchInfiniteQuery(options)` | Same for infinite queries |
| `prefetchQuery(options)` | Fetch into the cache, return `Promise<void>`, never throws |
| `prefetchInfiniteQuery(options)` | Same for infinite queries (`pages` option to prefetch N pages) |
| `ensureQueryData(options)` | Like `prefetchQuery` but ignores `staleTime` — returns data if present |
| `ensureInfiniteQueryData(options)` | Same for infinite queries |
| `getQueryData(key)` | Read cached data (key-only argument in v5) |
| `getQueryState(key)` | Read the full state object (status, fetchStatus, timestamps, error...) |
| `getQueriesData(filters)` | Read data for all matching queries |
| `setQueryData(key, updater)` | Write/prime cache data (use the updater form for immutability) |
| `setQueriesData(filters, updater, options)` | Batch update; `exact` controls key matching |
| `invalidateQueries(filters, options)` | Mark stale (+ refetch active ones, default) |
| `refetchQueries(filters, options)` | Force refetch (ignores staleness) |
| `cancelQueries(filters, options)` | Abort in-flight fetches |
| `removeQueries(filters)` | Delete cache entries |
| `resetQueries(filters, options)` | Reset to initial state |
| `isFetching(filters)` / `isMutating(filters)` | Counts of in-flight queries/mutations |
| `getDefaultOptions()` / `setDefaultOptions()` | Global options |
| `getQueryDefaults(key)` / `setQueryDefaults(key, defaults)` | Per-key defaults |
| `getMutationDefaults(key)` / `setMutationDefaults(key, defaults)` | Per-mutation-key defaults |
| `getQueryCache()` / `getMutationCache()` | Direct access to caches (`find`, `findAll`, `build`, `update`, `remove`) |
| `clear()` | Remove everything from both caches |
| `resumePausedMutations()` | Continue mutations paused by `networkMode: 'online'` |

## Filters

Query filters (used by `invalidateQueries`, `refetchQueries`, `removeQueries`, `getQueriesData`, `cancelQueries`, `resetQueries`, `isFetching`):

- `queryKey: unknown[]` — prefix match by default
- `exact: boolean` — match the exact key only
- `type: 'active' | 'inactive' | 'all'` — default `all`
- `stale: boolean` — `true` matches stale, `false` matches fresh
- `fetchStatus: 'fetching' | 'paused' | 'idle'`
- `predicate: (query) => boolean` — final per-query check

Mutation filters (`useIsMutating`, `useMutationState`, `isMutating`): `mutationKey`, `exact`, `status`, `predicate`.

Utility helpers: `matchQuery(filters, query)` and `matchMutation(filters, mutation)` return booleans for the same matching logic.

## Invalidation and matching

`invalidateQueries` marks matching queries stale (overriding `staleTime`) and refetches those with active observers, in the background:

```tsx
queryClient.invalidateQueries()                      // everything
queryClient.invalidateQueries({ queryKey: ['todos'] }) // prefix — also hits ['todos', { page: 1 }]
queryClient.invalidateQueries({ queryKey: ['todos'], exact: true })  // only the bare key
queryClient.invalidateQueries({
  predicate: (q) => q.queryKey[0] === 'todos' && q.queryKey[1]?.version >= 10,
})
```

Design principle: TanStack Query prescribes **targeted invalidation + background refetch** instead of maintaining a normalized cache by hand.

## Prefetching

`prefetchQuery` / `prefetchInfiniteQuery` populate the cache ahead of time:

- They respect the client's default `staleTime` (or a per-call `staleTime` option — which only applies to the prefetch, not to later `useQuery` calls)
- They return `Promise<void>` and **never throw** — a later `useQuery` is the graceful retry. If you need the data or the error, use `fetchQuery`/`fetchInfiniteQuery` instead
- Prefetched data is garbage-collected after `gcTime` if no observer appears
- Infinite queries prefetch one page by default; pass `pages: N` (with `getNextPageParam`) for more
- On the server, set a non-zero default `staleTime` so prefetches are not instantly stale

Patterns:

1. **Event handlers** — prefetch on `onMouseEnter`/`onFocus` with an explicit `staleTime`:

```tsx
const prefetch = () =>
  queryClient.prefetchQuery({ queryKey: ['details'], queryFn: getDetailsData, staleTime: 60000 })
```

2. **In a parent component** — render an extra `useQuery` for data a descendant needs (flatten a request waterfall), optionally with `notifyOnChangeProps: []` to avoid parent re-renders:

```tsx
useQuery({ queryKey: ['article-comments', id], queryFn: getArticleCommentsById, notifyOnChangeProps: [] })
```

3. **In a query function** — for data that is *always* needed after this fetch (e.g. comments after the article), call `queryClient.prefetchQuery` inside the parent `queryFn`. For conditional prefetching (only when the response contains e.g. `GRAPH` items), loop over the result and prefetch matches.
4. **In an effect** — `useEffect(() => { queryClient.prefetchQuery(...) })`; note it runs after the first paint, and after the suspenseful query resolves if that is in the same component
5. **With Suspense** — use the `usePrefetchQuery` / `usePrefetchInfiniteQuery` hooks before the boundary (a plain `useQuery` would start too late; `useSuspenseQuery` would block)

## Router integration

Declare per-route data up front and prefetch in the router loader rather than in components. Example with TanStack Router:

```tsx
const articleRoute = new Route({
  getParentRoute: () => rootRoute,
  path: 'article',
  loader: async ({ context: { queryClient } }) => {
    queryClient.prefetchQuery({ queryKey: ['comments'], queryFn: fetchComments }) // start, don't block
    await queryClient.prefetchQuery({ queryKey: ['article'], queryFn: fetchArticle })  // block until done
  },
  component: ({ ... }) => {
    const articleQuery = useQuery({ queryKey: ['article'], queryFn: fetchArticle })
    const commentsQuery = useQuery({ queryKey: ['comments'], queryFn: fetchComments })
    return /* ... */
  },
})
```

Awaiting only critical data lets the route render sooner while secondary data loads in the background. The same pattern applies to other routers (react-router example in the repo) and to SSR loader functions.

## Priming the cache manually

When data is already available synchronously, skip fetching entirely:

```tsx
queryClient.setQueryData(['todos'], todos)
```

Use the updater form for derived writes: `setQueryData(['projects'], (data) => ({ ...data, pages: data.pages.slice(1) }))`.

## Persistence

Official plugins (separate installs, e.g. `@tanstack/query-persist-client-plugin`):

- `persistQueryClient({ client, maxAge, storage, predicate })` — persist the whole cache to a storage backend
- `createSyncStoragePersister({ storage })` — browser `localStorage`/`sessionStorage`
- `createAsyncStoragePersister({ storage })` — `AsyncStorage` (React Native)
- `broadcastQueryClient({ client, forwardMutations, permission })` — sync cache across tabs/windows (BroadcastChannel)

Storage must be JSON-serializable (errors and `undefined` need custom serialization — `dehydrate`'s `serializeData` helps).
