# Cache and Prefetching

## Cache lifecycle

Assuming defaults (`staleTime: 0`, `gcTime: 5 min`):

1. First `useQuery({ queryKey: ['todos'], queryFn })` mounts → no cache entry → hard loading state, network request; data cached under `['todos']`, marked stale after `staleTime`.
2. A second instance with the same key mounts elsewhere → cached data returned immediately, plus a new background request; both instances share state updates (`isFetching`, `isPending`, ...) because they share the key.
3. Both unmount → no active instances → the query is "inactive"; a `gcTime` timer starts.
4. Another instance mounts before gc → cached data returned immediately while `queryFn` runs in the background.
5. No instances for 5 minutes → the cached data is deleted.

Targeted invalidation + background refetching + atomic updates replace normalized-cache bookkeeping — the library intentionally has no schema inference or normalized updates.

## The new fetching API: queryClient.query / infiniteQuery

In this version, `queryClient.query(options)` is the unified imperative fetch:

- Runs the `queryFn`, caches the result, resolves with the data, and **rejects** on error
- Honors the default `staleTime` to decide whether cached data is fresh; pass a specific `staleTime` for that call only (it does not affect `useQuery` calls) — pass `staleTime: 'static'` to always return cached data when available
- Prefetched queries with no observers are garbage collected after `gcTime`
- For non-critical prefetches, swallow errors — the query will retry in `useQuery` anyway:

```tsx
import { noop } from '@tanstack/react-query'

const prefetchTodos = async () => {
  await queryClient
    .query({
      queryKey: ['todos'],
      queryFn: fetchTodos,
      staleTime: 60 * 1000,
    })
    .catch(noop)
}
```

`queryClient.infiniteQuery(options)` is the infinite variant — same semantics, plus `initialPageParam`, `getNextPageParam`, and a `pages` option:

- On an empty cache it fetches the first page; `pages: 3` prefetches the first 3 pages
- If the cache already contains stale pages and you omit `pages`, it refetches up to the number of cached pages

The deprecated methods and their replacements (deprecated at this tag; removed in the next major version):

| Deprecated | Replacement |
|---|---|
| `queryClient.fetchQuery(options)` | `queryClient.query(options)` |
| `queryClient.prefetchQuery(options)` | `queryClient.query(options).catch(noop)` |
| `queryClient.ensureQueryData(options)` | `queryClient.query({ ...options, staleTime: 'static' })` |
| `queryClient.fetchInfiniteQuery(options)` | `queryClient.infiniteQuery(options)` |
| `queryClient.prefetchInfiniteQuery(options)` | `queryClient.infiniteQuery(options).catch(noop)` |
| `queryClient.ensureInfiniteQueryData(options)` | `queryClient.infiniteQuery({ ...options, staleTime: 'static' })` |

`queryOptions()`-built option objects work with `queryClient.query(...)` and typed `getQueryData(options.queryKey)` (see 07).

## QueryFilters and MutationFilters

Methods like `invalidateQueries`, `removeQueries`, `refetchQueries`, `cancelQueries`, `getQueriesData`, `isFetching`, `useIsFetching` accept a filter object:

**QueryFilters**

- `queryKey` — key to match (prefix match by default)
- `exact` — only the exact key
- `type` — `'active' | 'inactive' | 'all'` (default `all`)
- `stale` — `true` matches stale queries, `false` fresh ones
- `fetchStatus` — `'fetching' | 'paused' | 'idle'`
- `predicate` — final `(query) => boolean` filter

```tsx
queryClient.removeQueries({ queryKey: ['posts'], type: 'inactive' })
await queryClient.refetchQueries({ type: 'active' })
```

**MutationFilters** — `mutationKey`, `exact`, `status`, `predicate`.

Utilities `matchQuery(filters, query)` and `matchMutation(filters, mutation)` return the match result manually.

## QueryClient method overview

- Read: `getQueryData(queryKey)`, `getQueryState(queryKey)` (both accept **only** the queryKey now — the old filter argument is gone), `getQueriesData(filters)`, `getQueriesData` returns `[key, data | undefined]` tuples
- Write: `setQueryData(queryKey, updater?)`, `setQueriesData(updater, filters)` — updates must be immutable
- Fetch: `query(options)`, `infiniteQuery(options)` (see above)
- Control: `cancelQueries(filters, options?)` (options: `silent`, `revert`), `invalidateQueries(filters, options?)`, `refetchQueries(filters, options?)`, `resetQueries(filters, options?)`, `removeQueries(filters)`
- Counts: `isFetching(filters?)`, `isMutating(filters?)` return numbers of matching queries/mutations
- Defaults: `setQueryDefaults(queryKey, options)`, `setMutationDefaults(mutationKey, options)` — register **from most generic key to least generic** (v5 merges all matching registrations); `getDefaultOptions()` / `setDefaultOptions(options)`
- Caches: `getQueryCache()`, `getMutationCache()`; `clear()` empties the query cache and cancels timers
- `resumePausedMutations()` resumes mutations paused offline (see 03)

The v4 `query.remove()` method is gone — use `queryClient.removeQueries({ queryKey })`.

## Prefetching patterns

1. **In event handlers** — on `onMouseEnter` / `onFocus`, start `queryClient.query(...)`; set `staleTime` so re-hovers don't refetch; swallow errors with `.catch(noop)`.
2. **In components** — hoist a second `useQuery` into the parent and ignore its result (add `notifyOnChangeProps: []` to avoid rerenders when the prefetched data changes). For request waterfalls this flattens dependent fetches.
3. **Inside a query function** — fire `void queryClient.query(...).catch(noop)` for likely-follow-up data (e.g. prefetch comments while the article loads).
4. **In an effect** — `useEffect(() => { void queryClient.query(...).catch(noop) }, [...])`; note the effect runs after render, and with `useSuspenseQuery` in the same component it only runs after the suspenseful query finishes.
5. **With Suspense** — use the dedicated `usePrefetchQuery` / `usePrefetchInfiniteQuery` hooks before the suspense boundary (a plain `useQuery` would only start fetching after the suspenseful data resolved; `useSuspenseQueries` would block rendering). Optionally wrap the consuming component in its own `<Suspense>` boundary.
6. **Router integration** — declare per-route data in loaders. In TanStack Router, `beforeLoad` returns query options (stored in route context) and `loader` decides what to await: critical data `await queryClient.query({ ...articleQueryOptions, staleTime: 'static' })` (no `noop` — let the router's `errorComponent` handle failures), secondary data `void queryClient.query(commentsQueryOptions).catch(noop)`. Components then call `useQuery(articleQueryOptions)`.
7. **Manual priming** — if you already have the data synchronously, just `queryClient.setQueryData(['todos'], todos)`.

## Persistence plugins

- **`@tanstack/react-query-persist-client`** — `persistQueryClient({ queryClient, persister, maxAge?, buster? })` / `persistQueryClientSave` / `persistQueryClientRestore`, plus the `PersistQueryClientProvider` component. Persisters: `createSyncStoragePersister({ storage })`, `createAsyncStoragePersister({ storage })` (e.g. `window.localStorage`), or a custom object.
  - Set `gcTime` on the `QueryClient` to at least the persister `maxAge` (default 24h), or the stored cache is garbage collected sooner; `Infinity` disables GC.
  - `buster` (e.g. a build hash) discards incompatible stored caches.
  - `useIsRestoring()` (hook) / `IsRestoringProvider` tell you when the initial restore is in flight.
  - Paused mutations resume via `queryClient.resumePausedMutations()` in the provider's `onSuccess` (with `setMutationDefaults` to supply missing `mutationFn`s).
- **`createPersister` / `createSyncStoragePersister` / `createAsyncStoragePersister`** (experimental fine-grained storage persister) — persist selected queries individually rather than the whole client.
- **`@tanstack/query-broadcast-client-experimental`** — `broadcastQueryClient({ queryClient, broadcastChannel? })` syncs cache state between same-origin tabs/windows. Experimental: breaking changes possible in minor/patch releases; lock to a patch version.
