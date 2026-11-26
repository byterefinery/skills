# Performance, Testing, Network

## Request waterfalls

A waterfall happens when a request only starts after another finishes — each level is at least one server roundtrip, so total time grows with latency. Spot them in the browser Network tab.

Common patterns and fixes:

- **Single component / serial queries** — a dependent query (`enabled: !!userId`) that needs the first query's data. Fix by restructuring the API to fetch both in parallel, or by prefetching (see 04).
- **Nested component waterfalls** — a child component fetches data the parent already depends on. Fix by hoisting the query to the parent and passing data down, or by prefetching in the parent.
- **Code splitting** — `React.lazy` chunks load after the parent query, and the child's query starts after the chunk. Fix with conditional prefetching (e.g. fire `queryClient.query(...)` from within the parent's `queryFn` for likely items) — tradeoff: the fetcher code moves into the parent bundle.
- **SSR** — turns the client-side data roundtrips into server-side ones (lower, more stable latency) and lets JS chunks load in parallel; see 06.

## Render optimizations

The library applies these automatically:

- **Structural sharing** — if nothing changed in the fetched JSON, the `data` reference is kept; only changed parts are replaced. JSON-compatible data only; disable with `structuralSharing: false` or pass a custom `(old, new) => data` function.
- **Tracked properties** — a component re-renders only when a property it actually **reads** changes (Proxy get-trap based). Customize with `notifyOnChangeProps` (`'all'` turns tracking off); the prefetched-query pattern in 04 uses `notifyOnChangeProps: []` to avoid rerenders.
- **Referential identity** — the top-level result object from `useQuery` / `useInfiniteQuery` / `useMutation` (and the array from `useQueries`) is **not** referentially stable across renders; the `data` inside is as stable as possible.

`select` subscribes the component to a subset of the data:

```js
export const useTodoCount = () => {
  return useTodos(useCallback((data) => data.length, []))
}
// component re-renders only when todos.length changes
```

- `select` runs only when the `select` reference or `data` changes — an **inline** `select` runs every render; wrap in `useCallback` or extract to a stable function
- `select` operates on cached data and is **not** the place to throw errors — a throwing `select` leaves `data` undefined with `isSuccess` true. Fail in the `queryFn` instead.
- **Never rest-destructure** the query result (`const { ...rest } = useQuery(...)`) — the proxy get trap fires for every property and property tracking is disabled (the ESLint plugin has a rule for this). Destructure only the properties you use.

## Polling

`refetchInterval` (ms) refetches on a timer while at least one active observer exists, independent of `staleTime`:

```tsx
useQuery({ queryKey: ['prices'], queryFn: fetchPrices, refetchInterval: 5 * 1000 })
```

- Function form receives the **`query`** object: `refetchInterval: (query) => query.state.data?.status === 'complete' ? false : 2000` — returning `false` stops polling; a later positive value resumes it automatically
- Polling pauses when the tab loses focus unless `refetchIntervalInBackground: true`
- Pause polling conditionally by closing over component state in the function form
- In Electron/embedded WebViews where `online`/`offline` events are unreliable, `networkMode: 'always'` skips the connectivity check
- **Dedup note** — each observer runs its own timer, but concurrent in-flight fetches for the same query are deduplicated (one network request)
- **Rerender note** — if the polled data is unchanged, components reading only `data` do not rerender (structural sharing + tracked properties). Reading `isFetching` rerenders every cycle, and render-time calculations (e.g. a "taking longer than expected" message) won't update while data is unchanged — drive time-dependent UI from a separate timer.

## Network modes

`networkMode` controls behavior without a connection:

- `'online'` (default) — queries/mutations do not fire offline; a would-be fetch is **paused** (`fetchStatus: 'paused'`, `isPaused`) and continues on reconnect (this is a continue, independent of `refetchOnReconnect`). Retries also pause while offline.
- `'always'` — ignore connectivity entirely (for `queryFn`s that don't need the network, e.g. AsyncStorage). Queries are never paused; failures go to `error`; `refetchOnReconnect` defaults to `false` in this mode.
- `'offlineFirst'` — run the `queryFn` once even offline (service worker / HTTP cache may serve it), but pause retries on failure. Applies to queries and mutations, settable globally or per query/mutation.

Devtools can mock offline behavior via a toggle (sets `OnlineManager` offline without touching the real connection).

## Query cancellation

Every `queryFn` receives an `AbortSignal` (`context.signal`), aborted when the query is cancelled:

```tsx
const query = useQuery({
  queryKey: ['todos'],
  queryFn: async ({ signal }) => {
    const resp = await fetch('/todos', { signal })
    return resp.json()
  },
})
```

- Default behavior: unmounting before resolution does **not** cancel — data lands in the cache. Consuming the `signal` (passing it to fetch/axios/XHR) makes the promise cancellable; the query state then **reverts** to its previous value.
- `axios`: pass `signal` directly (v0.22+; older versions need a `CancelToken` wired to `signal.addEventListener('abort', ...)`)
- Manual: `queryClient.cancelQueries({ queryKey })` — cancels and reverts; cancel options are `silent` (suppress `CancelledError` propagation, return the retry promise) and `revert` (restore pre-fetch state, default `true`)
- `isCancelledError(error)` helper identifies cancellations
- Cancellation does **not** work with suspense hooks (`useSuspenseQuery`, `useSuspenseQueries`, `useSuspenseInfiniteQuery`)

## Window focus refetching

Stale queries refetch in the background when the window regains focus (`visibilitychange` only — the `focus` event is no longer listened to). Disable globally (`defaultOptions.queries.refetchOnWindowFocus: false`) or per-query.

- Custom focus source: `focusManager.setEventListener((handleFocus) => { ... })` — the handler receives a callback and must return an unsubscribe function (the default listens to `visibilitychange`)
- `focusManager.setFocused(true | undefined)` overrides / resets focus state
- Troubleshooting: Chrome DevTools "Emulate a focused page" keeps `visibilityState` visible and blocks these refetches

## React Native

Works out of the box, except connectivity/focus signals:

- **Connectivity** — wire `onlineManager.setEventListener` to NetInfo or expo-network state
- **App focus** — subscribe to `AppState` "change" and call `focusManager.setFocused(status === 'active')` (skip on web)
- **Screen focus refetch** — a `useFocusEffect` hook that calls `queryClient.refetchQueries({ queryKey, stale: true, type: 'active' })`, skipping the first (mount) focus
- **Unsubscribe off-screen queries** — `useQuery({ ..., subscribed: isFocused })` with React Navigation's `useIsFocused`; `subscribed: false` stops updates and fetches for that screen

Devtools for RN: third-party Rozenite / Flipper / Reactotron plugins and the macOS `rn-better-dev-tools` app (see the react-native docs page).

## Testing

Use React Testing Library's `renderHook` with an isolated `QueryClient` per test:

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

- **Turn off retries in tests** — the default 3 retries with backoff will time out error tests: `new QueryClient({ defaultOptions: { queries: { retry: false } } })`. Explicit per-query `retry` still wins over the default.
- **Jest** — set `gcTime: Infinity` to avoid "Jest did not exit one second after the test run completed" (only needed if you set a finite `gcTime`; that is the server default).
- **Network calls** — mock with nock (`expectation.done()` to assert the call happened); assert with `waitFor` on the query status.
- **Infinite scroll** — mock per-page responses (nock `.persist()` + query-string parsing), then `fetchNextPage()` and `waitFor` the second page to appear.
