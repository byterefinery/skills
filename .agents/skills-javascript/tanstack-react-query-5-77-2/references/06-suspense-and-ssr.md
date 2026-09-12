# Suspense and SSR

## Contents

- [Suspense](#suspense)
- [SSR fundamentals](#ssr-fundamentals)
- [Per-request QueryClient](#per-request-queryclient)
- [Quick start with initialData](#quick-start-with-initialdata)
- [Hydration with dehydrate and HydrationBoundary](#hydration-with-dehydrate-and-hydrationboundary)
- [Framework patterns](#framework-patterns)
- [Prefetching dependent queries](#prefetching-dependent-queries)
- [Error handling](#error-handling)
- [Caveats](#caveats)
- [Advanced SSR — Server Components and streaming](#advanced-ssr--server-components-and-streaming)
- [QueryErrorResetBoundary](#queryerrorresetboundary)

## Suspense

Suspense hooks return data synchronously (no `isPending` needed) and throw to the nearest `<Suspense>` boundary while loading:

- `useSuspenseQuery(options)` — like `useQuery` but suspends; `data` is always defined
- `useSuspenseInfiniteQuery(options)` — same for infinite queries
- `useSuspenseQueries({ queries })` — array of suspense queries; all must resolve before the boundary renders
- `usePrefetchQuery(options)` / `usePrefetchInfiniteQuery(options)` — start a prefetch from a component without blocking (the Suspense-friendly version of `queryClient.prefetchQuery`)

```tsx
<Suspense fallback="Loading article...">
  <Article id={id} />   // uses useSuspenseQuery internally
</Suspense>
```

Errors thrown by `queryFn` propagate to the boundary (or to a `QueryErrorResetBoundary` / React error boundary). In SSR, `useSuspenseQuery` is only safe when **all** used queries are prefetched — forgetting one causes a server/client markup mismatch.

## SSR fundamentals

Server rendering generates the initial HTML on the server. Client-side, this collapses the usual `Markup → JS → Query` waterfall into `Markup (with content + data) → JS`: step 3 (the client fetch) is skipped until the data goes stale.

Three steps, in order:

1. **Prefetch** data on the server before rendering (`queryClient.prefetchQuery` or `fetchQuery`)
2. **Dehydrate** the cache into a serializable payload embedded in the markup (`dehydrate(queryClient)`)
3. **Hydrate** it into a fresh client cache (`<HydrationBoundary state={...}>`)

## Per-request QueryClient

Create the client **inside the request scope** — in React state (or an instance ref), never at module level. A shared module-level client leaks data between users and bloats every dehydrated payload.

```tsx
// Next.js pages router — _app.tsx
import { QueryClient, QueryClientProvider, isServer } from '@tanstack/react-query'

function useClient() {
  const [client] = useState(
    () =>
      new QueryClient({
        // isServer is a helper: true on the server
        defaultOptions: { queries: { staleTime: isServer ? 60 * 1000 : 0 } },
      }),
  )
  return client
}

function App({ Component, pageProps }) {
  const queryClient = useClient()
  return (
    <QueryClientProvider client={queryClient}>
      <Component {...pageProps} />
    </QueryClientProvider>
  )
}
```

## Quick start with initialData

The minimal path — no `dehydrate`/`hydrate` at all: prefetch on the server with plain functions, pass raw data through the framework props as `initialData`:

```tsx
// getServerSideProps
const posts = await fetchPosts()
return { props: { posts } }

// component
useQuery({ queryKey: ['posts'], queryFn: fetchPosts, initialData: posts })
```

Good for a few queries; the dehydrate/hydrate pattern scales better (it carries the whole cache, including timestamps, so the client does not refetch until the real `staleTime` elapses).

## Hydration with dehydrate and HydrationBoundary

`dehydrate(queryClient, options)` produces a frozen, serializable snapshot. Defaults:

- Only **successful** queries are included (`shouldDehydrateQuery`)
- Only **paused** mutations (`shouldDehydrateMutation`)
- Errors are redacted from the payload by default (`shouldRedactErrors`)
- `serializeData?: (data) => any` for custom serialization

The client wraps the app (or a subtree) with `<HydrationBoundary state={dehydratedState}>`, which loads the state into the client `QueryClient` — no refetches until the data goes stale.

There are actually **three** clients involved in a framework SSR flow: the loader/prefetch client, the server-rendering client, and the client-rendering client — the dehydrated result seeds both renderings so markup matches.

## Framework patterns

Next.js pages router:

```tsx
// page
export async function getServerSideProps() {
  const queryClient = new QueryClient()
  await queryClient.prefetchQuery({ queryKey: ['posts'], queryFn: fetchPosts })
  return { props: { dehydratedState: dehydrate(queryClient) } }
}

export default function PostsPage({ dehydratedState }) {
  return (
    <HydrationBoundary state={dehydratedState}>
      <Posts />
    </HydrationBoundary>
  )
}
```

Remix:

```tsx
export async function loader() {
  const queryClient = new QueryClient()
  await queryClient.prefetchQuery({ queryKey: ['posts'], queryFn: fetchPosts })
  return json({ dehydratedState: dehydrate(queryClient) })
}

function PostsRoute() {
  const { dehydratedState } = useLoaderData<typeof loader>()
  return (
    <HydrationBoundary state={dehydratedState}>
      <Posts />
    </HydrationBoundary>
  )
}
```

## Prefetching dependent queries

When a second query depends on the first (e.g. `['post', id]` after `['posts']`), the loader is plain JavaScript — fetch the first, read the result, then prefetch the dependent:

```tsx
const posts = await queryClient.fetchQuery({ queryKey: ['posts'], queryFn: fetchPosts })
await queryClient.prefetchQuery({ queryKey: ['post', posts[0].id], queryFn: fetchPost })
```

## Error handling

Default strategy is **graceful degradation**: `prefetchQuery` never throws, and `dehydrate` includes only successful queries — so failed queries simply retry on the client and the SSR output shows a loading state instead of content.

When critical data must fail loudly (404/500 responses), use `fetchQuery` instead and handle the throw:

```tsx
try {
  const data = await queryClient.fetchQuery({ queryKey: ['post', id], queryFn: fetchPost })
} catch (error) {
  // respond with 404/500 per your framework
}
```

To include failed queries in the dehydrated state (avoid client retries), override `shouldDehydrateQuery` — and remember errors need custom serialization for JSON storage.

## Caveats

- **Staleness is measured from the server fetch time** — set `staleTime` accordingly (a common pattern: `staleTime: isServer ? 60 * 1000 : 0`) so the client does not instantly refetch what the server just fetched
- **Memory on the server** — per-request clients prevent unbounded cache growth, but a busy server still creates many clients; keep `gcTime` short or rely on request-scoped lifetimes
- **Next.js rewrites** — can cause server-side component remounts that refetch unexpectedly; verify with the devtools
- Data must be serializable — `undefined`, `Error`, and non-JSON values need custom `serializeData`

## Advanced SSR — Server Components and streaming

For the Next.js **app router** and Server Components: prefetch in a server component (or `loading` flow) and dehydrate for a client `providers` component that owns the `QueryClient`/provider. Key points:

- Move the client factory (e.g. `app/get-query-client.ts`) out of the client provider so both server and client code can use it
- Nesting server components each with their own Suspense boundary streams independently
- **Streaming data** (v5.40+): pending queries can be dehydrated too — configure `dehydrate: { shouldDehydrateQuery: (q) => defaultShouldDehydrateQuery(q) || q.state.status === 'pending' }` and kick off prefetches without awaiting all of them; Next.js streams finished Suspense chunks and the pending queries keep resolving on the client
- There is also an experimental streaming mode without explicit prefetching (the framework suspends and the `queryClient` fetches inside server components) — see the repo's `advanced-ssr` guide before relying on it

## QueryErrorResetBoundary

Wraps a tree to catch query errors thrown by suspense hooks, letting you show an error UI with a "retry" action that resets and refetches:

```tsx
<QueryErrorResetBoundary resetKeys={[...queryKeys]}>
  {({ reset }) => (
    <ErrorBoundary onReset={reset}>
      <Suspense fallback="Loading...">
        <App />
      </Suspense>
    </ErrorBoundary>
  )}
</QueryErrorResetBoundary>
```

`useQueryErrorResetBoundary()` exposes `{ isResetting, reset }` from inside the boundary.
