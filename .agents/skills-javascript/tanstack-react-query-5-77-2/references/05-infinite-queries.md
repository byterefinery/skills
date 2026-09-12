# Infinite Queries

## Contents

- [useInfiniteQuery](#useinfinitequery)
- [Data shape](#data-shape)
- [Refetching behavior](#refetching-behavior)
- [Bi-directional lists](#bi-directional-lists)
- [Reversed display](#reversed-display)
- [Manual cache updates](#manual-cache-updates)
- [Limiting pages (maxPages)](#limiting-pages-maxpages)
- [APIs without a cursor](#apis-without-a-cursor)
- [Prefetching and options helpers](#prefetching-and-options-helpers)

## useInfiniteQuery

`useInfiniteQuery` is the `useQuery` variant for additive "load more" / infinite-scroll lists.

```tsx
const {
  data, error, status, isFetching, isFetchingNextPage, isFetchingPreviousPage,
  fetchNextPage, fetchPreviousPage, hasNextPage, hasPreviousPage,
} = useInfiniteQuery({
  queryKey: ['projects'],
  queryFn: fetchProjects,          // receives ({ pageParam, direction, ... })
  initialPageParam: 0,              // required
  getNextPageParam: (lastPage, pages) => lastPage.nextCursor,  // required in practice
  getPreviousPageParam: (firstPage, pages) => firstPage.prevCursor,
  maxPages: 3,
  ...allRegularQueryOptions,
})
```

- `fetchNextPage` — fetch the next page; `hasNextPage` is `true` when `getNextPageParam` returns a value other than `null`/`undefined`
- `fetchPreviousPage` — the reverse; `hasPreviousPage` follows `getPreviousPageParam`
- `isFetchingNextPage` / `isFetchingPreviousPage` distinguish "loading more" from a background refresh
- `direction` in the context is **deprecated** — encode direction into the page param via the `getNextPageParam`/`getPreviousPageParam` functions
- `initialData` / `placeholderData` must conform to the infinite data shape

Typical UI:

```tsx
{data.pages.map((group, i) => (
  <Fragment key={i}>
    {group.data.map((project) => <p key={project.id}>{project.name}</p>)}
  </Fragment>
))}
<button onClick={() => fetchNextPage()} disabled={!hasNextPage || isFetching}>
  {isFetchingNextPage ? 'Loading more...' : hasNextPage ? 'Load More' : 'Nothing more'}
</button>
```

**Only one fetch can be in flight per infinite query** — the cache entry is shared across all pages. Guard user-triggered fetches: `onEndReached={() => hasNextPage && !isFetching && fetchNextPage()}`, or pass `{ cancelRefetch: false }` to `fetchNextPage` if you deliberately want concurrent fetching.

## Data shape

`data` is an object, not the page payload:

```ts
{
  pages: TPage[],      // fetched page payloads, in order
  pageParams: TPageParam[], // the param used for each page
}
```

## Refetching behavior

When an infinite query becomes stale and refetches, **every page is refetched sequentially from the first one** — this prevents stale cursors causing duplicates or gaps after underlying data mutates. If the cache entry is removed, pagination restarts from `initialPageParam`.

## Bi-directional lists

Add `getPreviousPageParam`, then `fetchPreviousPage` / `hasPreviousPage` / `isFetchingPreviousPage` become available (used by infinite-scroll lists that prepend, e.g. feeds).

## Reversed display

To render newest-first from an oldest-fetched list, transform with `select`:

```tsx
select: (data) => ({
  pages: [...data.pages].reverse(),
  pageParams: [...data.pageParams].reverse(),
})
```

## Manual cache updates

Update via `setQueryData` — always preserve the `{ pages, pageParams }` structure:

```tsx
// drop the first page
queryClient.setQueryData(['projects'], (data) => ({
  pages: data.pages.slice(1),
  pageParams: data.pageParams.slice(1),
}))

// remove one item from every page
queryClient.setQueryData(['projects'], (data) => ({
  pages: data.pages.map((page) => page.filter((val) => val.id !== updatedId)),
  pageParams: data.pageParams,
}))
```

## Limiting pages (maxPages)

`maxPages` caps how many pages are kept in the cache — useful when users can load dozens of pages (memory) and a full sequential refetch is expensive. Combined with `getPreviousPageParam`, pages can still be fetched in both directions on demand:

```tsx
useInfiniteQuery({
  queryKey: ['projects'],
  queryFn: fetchProjects,
  initialPageParam: 0,
  getNextPageParam: (lastPage, pages) => lastPage.nextCursor,
  getPreviousPageParam: (firstPage, pages) => firstPage.prevCursor,
  maxPages: 3,
})
```

## APIs without a cursor

Use the `pageParam` itself as the cursor — the `*PageParam` callbacks also receive the current page's param:

```tsx
getNextPageParam: (lastPage, allPages, lastPageParam) =>
  lastPage.length === 0 ? undefined : lastPageParam + 1,
getPreviousPageParam: (firstPage, allPages, firstPageParam) =>
  firstPageParam <= 1 ? undefined : firstPageParam - 1,
```

## Prefetching and options helpers

- `queryClient.prefetchInfiniteQuery({ ..., pages: 3 })` — prefetch N pages; by default only the first page is prefetched
- `queryClient.fetchInfiniteQuery(options)` — awaitable variant returning the infinite data
- `queryClient.ensureInfiniteQueryData(options)` — `ensureQueryData` equivalent
- `infiniteQueryOptions(...)` — the `queryOptions` helper for infinite queries (type-safe sharing between `useInfiniteQuery`, `prefetchInfiniteQuery`, etc.)
