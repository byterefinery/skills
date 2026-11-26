# Infinite Queries

`useInfiniteQuery` renders lists that additively load more data ("Load More" / infinite scroll). The differences from `useQuery`:

- `data` is an object: `data.pages` (fetched pages) and `data.pageParams` (params used to fetch them)
- `fetchNextPage` (required) and `fetchPreviousPage` functions
- `initialPageParam` option — **required**, the page param for the first page (v5 removed the old `pageParam` default-in-queryFn pattern because `undefined` is not serializable)
- `getNextPageParam(lastPage, pages, lastPageParam)` and `getPreviousPageParam(firstPage, pages, firstPageParam)` — determine whether more data exists **and** the param to fetch it. `getNextPageParam` is **required**; returning `null` (or `undefined`) means "no more pages" (v5 widened the check from `undefined` to include `null`)
- `hasNextPage` / `hasPreviousPage` booleans
- `isFetchingNextPage` / `isFetchingPreviousPage` — distinguish "loading more" from background refresh
- `maxPages` — limit how many pages are stored/refetched (see below)
- `initialData` / `placeholderData` must conform to the `{ pages, pageParams }` shape

## Example

API returning 3 projects per cursor step:

```tsx
function Projects() {
  const fetchProjects = async ({ pageParam }) => {
    const res = await fetch('/api/projects?cursor=' + pageParam)
    return res.json()
  }

  const { data, error, fetchNextPage, hasNextPage, isFetching,
    isFetchingNextPage, status } = useInfiniteQuery({
    queryKey: ['projects'],
    queryFn: fetchProjects,
    initialPageParam: 0,
    getNextPageParam: (lastPage, pages) => lastPage.nextCursor,
  })

  return status === 'pending' ? (
    <p>Loading...</p>
  ) : status === 'error' ? (
    <p>Error: {error.message}</p>
  ) : (
    <>
      {data.pages.map((group, i) => (
        <React.Fragment key={i}>
          {group.data.map((project) => (
            <p key={project.id}>{project.name}</p>
          ))}
        </React.Fragment>
      ))}
      <button
        onClick={() => fetchNextPage()}
        disabled={!hasNextPage || isFetching}>
        {isFetchingNextPage ? 'Loading more...'
          : hasNextPage ? 'Load More' : 'Nothing more to load'}
      </button>
      <div>{isFetching && !isFetchingNextPage ? 'Fetching...' : null}</div>
    </>
  )
}
```

## Single in-flight fetch

Only **one** fetch can be in flight per infinite query — a single cache entry is shared for all pages, and a concurrent `fetchNextPage` can overwrite an ongoing background refresh. Guard the call:

```jsx
<List onEndReached={() => hasNextPage && !isFetching && fetchNextPage()} />
```

If you intend simultaneous fetching, pass `{ cancelRefetch: false }` to `fetchNextPage` (default `cancelRefetch: true` cancels the refetch first).

## Refetch semantics

When an infinite query becomes stale and refetches, each page is fetched **sequentially from the first** — so cursors never go stale (no duplicates/skips). If the cache entry is ever removed, pagination restarts at the initial state with only the first page.

## Bi-directional lists

Add `getPreviousPageParam` and use `fetchPreviousPage` / `hasPreviousPage` / `isFetchingPreviousPage`:

```tsx
useInfiniteQuery({
  queryKey: ['projects'],
  queryFn: fetchProjects,
  initialPageParam: 0,
  getNextPageParam: (lastPage, pages) => lastPage.nextCursor,
  getPreviousPageParam: (firstPage, pages) => firstPage.prevCursor,
})
```

## Reversed page order

Use `select` to reverse pages for display (keep `pages` and `pageParams` aligned):

```tsx
useInfiniteQuery({
  queryKey: ['projects'],
  queryFn: fetchProjects,
  select: (data) => ({
    pages: [...data.pages].reverse(),
    pageParams: [...data.pageParams].reverse(),
  }),
})
```

## Manual cache updates

Always keep the `{ pages, pageParams }` structure intact:

```tsx
// remove the first page
queryClient.setQueryData(['projects'], (data) => ({
  pages: data.pages.slice(1),
  pageParams: data.pageParams.slice(1),
}))

// remove a single value from every page
queryClient.setQueryData(['projects'], (data) => ({
  pages: data.pages.map((page) => page.filter((val) => val.id !== updatedId)),
  pageParams: data.pageParams,
}))

// keep only the first page
queryClient.setQueryData(['projects'], (data) => ({
  pages: data.pages.slice(0, 1),
  pageParams: data.pageParams.slice(0, 1),
}))
```

## Limited infinite queries (`maxPages`)

`maxPages` limits the number of pages kept in the query data — useful when users can load many pages (memory) or refetching dozens of pages is expensive. With `maxPages: 3`, only 3 pages are kept and only 3 are refetched sequentially. The list must be bi-directional (both `getNextPageParam` and `getPreviousPageParam` defined) so pages can be fetched in both directions as needed.

## APIs without a cursor

When the API has no cursor, derive the next param arithmetically from the current `pageParam` (the third argument):

```tsx
useInfiniteQuery({
  queryKey: ['projects'],
  queryFn: fetchProjects,
  initialPageParam: 0,
  getNextPageParam: (lastPage, allPages, lastPageParam) => {
    if (lastPage.length === 0) return undefined
    return lastPageParam + 1
  },
  getPreviousPageParam: (firstPage, allPages, firstPageParam) => {
    if (firstPageParam <= 1) return undefined
    return firstPageParam - 1
  },
})
```

## Prefetching multiple pages

Use `queryClient.infiniteQuery` with the `pages` option (see 04):

```tsx
await queryClient
  .infiniteQuery({
    queryKey: ['projects'],
    queryFn: fetchProjects,
    initialPageParam: 0,
    getNextPageParam: (lastPage, pages) => lastPage.nextCursor,
    pages: 3, // prefetch the first 3 pages
  })
  .catch(noop)
```

## Scroll restoration

TanStack Query does not implement scroll restoration itself, but caching removes the main cause of broken restoration (refetch-induced UI resets): as long as the query is not garbage collected (default 5 minutes), navigating back renders instantly with a stable layout, so the router's scroll restoration works out of the box.
