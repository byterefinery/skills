# Suspense and SSR

## Suspense hooks

Dedicated hooks make loading/error handling Suspense's job (fallback + error boundaries), so `status` checks and `error` handling are not needed:

- `useSuspenseQuery(options)`
- `useSuspenseQueries({ queries: [...] })` — for parallel suspenseful queries (plain `useSuspenseQuery` hooks in one component would fetch serially)
- `useSuspenseInfiniteQuery(options)`

```tsx
const { data } = useSuspenseQuery({ queryKey, queryFn })
// data is guaranteed defined — TypeScript knows it
```

Consequences:

- You **cannot** conditionally enable/disable a suspense query
- There is **no `placeholderData`** for suspense queries — to prevent the fallback from flashing on query-key changes, wrap the key change in `startTransition`
- `throwOnError` **defaults to** `(error, query) => typeof query.state.data === 'undefined'` — errors are thrown to the nearest error boundary only when there is no cached data to show. You cannot change `throwOnError` (it would make `data` potentially undefined); to route all errors to boundaries, throw manually:

```tsx
const { data, error, isFetching } = useSuspenseQuery({ queryKey, queryFn })
if (error && !isFetching) throw error
// continue rendering data
```

- Mutations can also propagate errors to the nearest error boundary by setting `throwOnError: true`
- Cancellation does not work with suspense hooks (`useSuspenseQuery`, `useSuspenseQueries`, `useSuspenseInfiniteQuery`)

## Resetting error boundaries

Pair error boundaries with `QueryErrorResetBoundary` (component) or `useQueryErrorResetBoundary` (hook) so "try again" re-attempts failed queries:

```tsx
<QueryErrorResetBoundary>
  {({ reset }) => (
    <ErrorBoundary
      onReset={reset}
      fallbackRender={({ resetErrorBoundary }) => (
        <div>
          There was an error!
          <button onClick={() => resetErrorBoundary()}>Try again</button>
        </div>
      )}
    >
      <Page />
    </ErrorBoundary>
  )}
</QueryErrorResetBoundary>
```

The hook resets errors within the closest boundary (globally if none is defined).

## Fetch-on-render vs render-as-you-fetch

Out of the box, suspense mode is **fetch-on-render**: components trigger fetching as they mount and suspend. For **render-as-you-fetch**, prefetch on routing callbacks or user interactions (see 04) so data arrives before the component mounts — using `usePrefetchQuery` / `usePrefetchInfiniteQuery` before the boundary.

## Server Rendering & Hydration

The SSR flow has three parts: **prefetch** on the server, **dehydrate** into a serializable format, **hydrate** on the client.

### Per-request QueryClient (critical)

Create the client **inside** the app (React state or a per-request factory) — never at module scope:

```tsx
// NEVER: const queryClient = new QueryClient()  // at file root —
// the cache is shared between all requests and leaks data between users

const [queryClient] = React.useState(
  () =>
    new QueryClient({
      defaultOptions: { queries: { staleTime: 60 * 1000 } },
    }),
)
```

For app router / Server Components setups, the documented factory pattern:

```tsx
import { environmentManager, QueryClient } from '@tanstack/react-query'

function makeQueryClient() {
  return new QueryClient({
    defaultOptions: { queries: { staleTime: 60 * 1000 } },
  })
}

let browserQueryClient: QueryClient | undefined = undefined

function getQueryClient() {
  if (environmentManager.isServer()) {
    return makeQueryClient() // server: new client per request
  }
  if (!browserQueryClient) browserQueryClient = makeQueryClient()
  return browserQueryClient // browser: stable singleton
}
```

Avoid `useState` for the client unless a suspense boundary sits between it and suspending code (React would discard the client created during a suspended initial render).

### Prefetch, dehydrate, hydrate (pages-router / Remix style)

```tsx
// loader / getStaticProps / getServerSideProps
export async function getStaticProps() {
  const queryClient = new QueryClient()

  await queryClient
    .query({ queryKey: ['posts'], queryFn: getPosts })
    .catch(noop) // non-critical: swallow; retry client-side
  // Use `await Promise.all([...])` to prefetch several queries in parallel
  // Unprefetched queries are simply not server rendered — they fetch on the client

  return { props: { dehydratedState: dehydrate(queryClient) } }
}

function Posts() {
  const { data } = useQuery({ queryKey: ['posts'], queryFn: getPosts })
  return /* render */
}

export default function PostsRoute({ dehydratedState }) {
  return (
    <HydrationBoundary state={dehydratedState}>
      <Posts />
    </HydrationBoundary>
  )
}
```

Notes:

- Three `queryClient`s are involved: the loader's (prefetch), the server rendering client, and the client rendering client. The dehydrated state seeds the latter two with identical data.
- **Error handling** — the default is graceful degradation: `dehydrate` includes only **successful** queries, and non-critical prefetches use `.catch(noop)`. For critical content, `await queryClient.query(...)` **without** the noop and handle the thrown error (404/500, router error component). To include failed queries in the dehydrated state, pass `dehydrate(queryClient, { shouldDehydrateQuery: () => true })` (or a custom function); `shouldDehydrateMutation` does the same for mutations.
- `useSuspenseQuery` works for SSR **only if you always prefetch** every suspenseful query — a missed prefetch can cause server/client markup mismatches.

### Quick start with `initialData`

The minimal path is passing raw loader data as `initialData` to `useQuery` (no dehydrate/hydrate). Tradeoffs: you must thread the data down to every `useQuery`; it never overwrites existing cache data (even fresher server data is ignored); and there is no server fetch timestamp, so `dataUpdatedAt` is based on page load.

### Serialization caveats

Frameworks only serialize safe values — `undefined`, `Error`, `Date`, `Map`, `Set`, `BigInt`, `Infinity`, `NaN`, `-0`, regexes do not survive. Use superjson or similar to return such values. For **custom SSR setups**, never `JSON.stringify(dehydratedState)` straight into markup — it is not XSS-safe (superjson alone is also unsafe); use serialize-javascript or devalue, which escape out of the script context.

### Server-side caveats

- Staleness is measured from when the query was fetched **on the server** (UTC); the server clock must be correct.
- With `staleTime: 0`, queries refetch in the background on page load — set a higher `staleTime` to avoid the double fetch (a CDN-cached markup + low `staleTime` combo gives fresh data with cached HTML).
- On the server, `gcTime` defaults to **`Infinity`** (no timers; the cache dies with the request). A **finite** `gcTime` schedules a timer per query that keeps the `AsyncLocalStorage` request context alive after the response is sent — a common memory leak. Keep `Infinity` on the server if you customize `gcTime`: `gcTime: environmentManager.isServer() ? Infinity : 1000 * 60`.
- Avoid `gcTime: 0` (hydration errors — the GC can remove data before `HydrationBoundary` finishes).
- If you must use a finite server `gcTime`, call `queryClient.clear()` once done (after dehydrating/rendering).
- Next.js **rewrites** + automatic static optimization cause a second React Query hydration (missing referential equality of hydration data).

## Streaming (experimental)

`@tanstack/react-query-next-experimental` streams suspense results from the server for Next.js: wrap the app in `<ReactQueryStreamedHydration>` (inside `QueryClientProvider`, `'use client'` file) and call `useSuspenseQuery` in client components; each resolved suspense boundary streams to the client. Note: `useSuspenseQuery` without a `<Suspense>` boundary holds up the whole HTML response until the fetch resolves (hurts TTFB). The package also exposes an `experimental_streamedQuery` helper for server-side promise creation (see the advanced SSR guide in the repo docs).

## Advanced SSR (Server Components)

Treat Server Components as "just another framework loader": they run on the server for the initial view **and** page transitions, fetch with `queryClient.query(...)`, and the client picks up the promises/data via `useSuspenseQuery` (or `useQuery` — but then Next.js won't suspend and the component renders in `pending`, opting out of server rendering the content). See the `advanced-ssr` guide in the repo docs for the full app-router walkthrough.
