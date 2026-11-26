# Performance, Testing, and Network

## Contents

- [Render optimizations](#render-optimizations)
- [Request waterfalls](#request-waterfalls)
- [Network modes](#network-modes)
- [Query cancellation](#query-cancellation)
- [Testing](#testing)
- [Scroll restoration](#scroll-restoration)
- [Client state vs server state](#client-state-vs-server-state)
- [Background fetch indicators](#background-fetch-indicators)

## Render optimizations

React Query re-renders only when necessary, via three mechanisms:

**Structural sharing** — after a fetch, the new (JSON-parsed) data is compared deeply with the old; unchanged subtrees keep their references, so `useMemo`/`useCallback` downstream stay stable. Works only for JSON-compatible values; disable with `structuralSharing: false` or supply a custom `(oldData, newData) => TData` function.

**Referential identity** — the top-level object from `useQuery`/`useInfiniteQuery`/`useMutation` (and the array from `useQueries`) is a **new reference every render**. Only `data` (and friends) are stabilized. Do not put the whole result in a `useMemo` dependency list.

**Tracked properties** — the result is a Proxy; re-renders happen only when a property the component *actually reads* changes (`isFetching`/`isStale` churn does not matter if unused). Customizable via `notifyOnChangeProps` (`'all'` disables tracking). Pitfall: **object rest destructuring** (`const { ...rest } = useQuery(...)`) reads every property and disables the optimization — destructure explicitly.

**select + memoization** — `select: (data) => ...` narrows the subscription; the component re-renders only when the selected value changes. `select` re-runs when the select function or `data` changes referentially, so inline arrows run every render — memoize with `useCallback` or hoist to a stable function:

```tsx
const selectTodoCount = (data: Todo[]) => data.length
export const useTodoCount = () => useTodos(selectTodoCount)
```

## Request waterfalls

A waterfall is a chain where each fetch waits on the previous one (`getFeed → getGraphDataById → ...`). Each hop adds a full round trip. Fixes, in order of preference:

1. **Restructure the API** so one request returns the needed data (best — removes the hop entirely)
2. **Prefetch in the router/loader** (see 04) so data arrives before the component mounts
3. **Hoist** the child query to the parent and pass data down as props
4. **`enabled`-chained dependent queries** when the dependency is a runtime value (a serial query by definition; accept the latency)
5. **Conditional prefetch inside `queryFn`** — after fetching a feed, loop its items and `prefetchQuery` the likely ones; code-split components (`React.lazy`) then load code and data in parallel. Tradeoff: the prefetch code moves into the parent bundle
6. **`usePrefetchQuery` before a Suspense boundary** for secondary data that should not block primary rendering

## Network modes

Per-query/mutation or global (`defaultOptions`):

- **`'online'`** (default) — fetches do not start without a connection; a query that would fetch goes to `fetchStatus: 'paused'` (flag `isPaused`). Paused retries resume on reconnect (independent of `refetchOnReconnect`). Mutations pause and can be resumed with `queryClient.resumePausedMutations()`
- **`'always'`** — ignores connectivity entirely (local `AsyncStorage` reads, `Promise.resolve` fns); `refetchOnReconnect` defaults to `false` here
- **`'offlineFirst'`** — runs `queryFn` once, then pauses retries; the right mode when a service worker or HTTP cache can satisfy the first request (offline-first PWAs)

Connectivity detection is pluggable via `onlineManager.setEventListener((setOnline) => {...})` (defaults to `online`/`offline` browser events); window focus events are likewise pluggable via `focusManager.setEventListener`.

Do not show a loading spinner on `isPending` alone in offline-capable apps — check `isPaused` too.

## Query cancellation

In-flight queries are aborted automatically when the component unmounts (last observer) or the key changes. The `AbortSignal` arrives in the `QueryFunctionContext`:

- `fetch` — pass `signal` to it
- `axios` — pass `signal` in the request config
- `XMLHttpRequest` — wire `signal` to `xhr.abort()`
- `graphql-request` — pass `signal`

Manual cancellation: `queryClient.cancelQueries(filters)` (optionally `{ graceful: true }` waits for in-flight fetches to settle before rejecting). Limitation: once aborted, the fetch cannot be resumed — a new one is started on demand.

## Testing

Use `renderHook` from `@testing-library/react` (React 18+; `@testing-library/react-hooks` for ≤ 17) with a wrapper that owns a **fresh `QueryClient` per test** for isolation:

```tsx
import { renderHook, waitFor } from '@testing-library/react'

const queryClient = new QueryClient()
const wrapper = ({ children }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
)

const { result } = renderHook(() => useCustomHook(), { wrapper })
await waitFor(() => expect(result.current.isSuccess).toBe(true))
expect(result.current.data).toEqual('Hello')
```

- If sharing one client across tests, `queryClient.clear()` in `beforeEach` and avoid parallel test execution
- Mock the `queryFn` (e.g. `vi.fn(fetchTodos)`) rather than the HTTP layer when possible; assert on `data`, `error`, and state transitions
- For mutations, `await mutation.mutateAsync(...)` and then assert `result.current.isSuccess` / cache effects (`queryClient.getQueryData`)

## Scroll restoration

Works out of the box for all query types: going back re-mounts the same key and reads the cached data synchronously, so scroll position can be restored immediately. Requires the data to still be in cache (default `gcTime` of 5 minutes is usually enough).

## Client state vs server state

TanStack Query does **not** replace client state. UI state (open modals, selected tabs, form drafts) belongs in React state / context / a client-state library; data owned by the server belongs in TanStack Query. The two compose — e.g. keep a `filter` in `useState` and feed it into the `queryKey`.

## Background fetch indicators

Distinguish "first load" from "refreshing in the background":

- `isPending` — no data yet (hard loading)
- `isFetching` — any in-flight fetch, including background refetches
- `isRefetching` — fetching while already having data (`isFetching && !isPending`)
- `useIsFetching(filters?)` — global (or filtered) count of in-flight queries; `useIsMutating(filters?)` the mutation equivalent. Typical use: a top-bar spinner that shows whenever *anything* is silently refreshing

```tsx
const isFetching = useIsFetching()
const isMutating = useIsMutating()
{isFetching > 0 && <Spinner small />}
```
