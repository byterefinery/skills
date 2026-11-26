# Setup and Defaults

## Installation

```sh
npm i @tanstack/react-query        # or pnpm / yarn / bun / deno
```

Compatibility (per the package docs at this tag):

- React 18+ required (peer dependency `react: ^18 || ^19`; `@types/react` optional)
- Works with ReactDOM and React Native
- Optimized for modern browsers — Chrome >= 91, Firefox >= 90, Edge >= 91, Safari >= 15, iOS >= 15, Opera >= 77
- v5 requires TypeScript 4.7+; the library's types track the DefinitelyTyped support window (TypeScript 5.7+ at this release). Type changes are considered non-breaking and ship as patch releases, so lock the package to a specific patch.

No module bundler? It works via an ESM-compatible CDN (the docs use ESM.sh):

```html
<script type="module">
  import { QueryClient } from 'https://esm.sh/@tanstack/react-query'
</script>
```

## QueryClient and Provider

Create one `QueryClient` and provide it at the root of the tree:

```tsx
const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
    </QueryClientProvider>
  )
}
```

Access it anywhere with `useQueryClient()`. For microfrontends or multiple trees, pass a custom `queryClient` instance directly (the v4 `context` prop is gone; `QueryClientProvider`'s `contextSharing` prop is also removed).

### Global default options

Configure defaults once; every option can be overridden per-query:

```tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      gcTime: 5 * 60 * 1000,
      retry: 3,
      // refetchOnWindowFocus, refetchOnMount, refetchOnReconnect,
      // networkMode, structuralSharing, queryFn, ...
    },
    mutations: {
      // retry, ...
    },
  },
})
```

At runtime, `queryClient.setDefaultOptions(options)` replaces the defaults, and `queryClient.getDefaultOptions()` returns them. `queryClient.clear()` removes every query from the cache and cancels pending fetches and garbage collection timers.

## Default Query Function

You can set one `queryFn` for the whole app (key-driven data sources) via `defaultOptions.queries.queryFn`; the function receives the context (including `queryKey`), and any hook can still override it:

```tsx
const defaultQueryFn = async ({ queryKey }) => {
  const { data } = await axios.get(
    `https://jsonplaceholder.typicode.com${queryKey[0]}`,
  )
  return data
}

const queryClient = new QueryClient({
  defaultOptions: { queries: { queryFn: defaultQueryFn } },
})

// Later: no queryFn needed
useQuery({ queryKey: ['/posts'] })
```

## Important Defaults (full list)

- Cached data is **stale immediately** by default (`staleTime: 0`). A query with `staleTime` set is fresh until it elapses. `'static'` is stricter than `Infinity`: invalidation can override `Infinity` but not `'static'`; `"always"` values of `refetchOnMount` / `refetchOnWindowFocus` / `refetchOnReconnect` are also blocked by `'static'`. Use `'static'` for data that cannot change while the app runs (feature flags fetched at boot, permissions loaded at login, static reference tables).
- Stale queries refetch automatically in the background when new instances mount, the window is refocused, or the network reconnects.
- `refetchInterval` polling is independent of `staleTime` — it fires on its own clock regardless of freshness.
- Queries with no active observers become "inactive" and are garbage collected after **5 minutes** (`gcTime`); on the server the default is `Infinity`.
- Failed queries retry **3 times** with exponential backoff before the error surfaces (server default: `0`).
- Results are **structurally shared** — `data` keeps its reference when nothing changed, helping `useMemo` / `useCallback` stability. JSON-compatible values only; disable with `structuralSharing: false` or pass a custom function.

## Environment Managers

Singleton objects you can drive from app code (all exported from `@tanstack/react-query`):

- `focusManager` — window focus state. `focusManager.setFocused(true | undefined)` overrides or resets the focus state; `focusManager.setEventListener(handler)` replaces the default `visibilitychange` listener.
- `onlineManager` — connectivity state; `onlineManager.setEventListener(setOnline => ...)` wires up custom connectivity sources. Starts `online: true` and listens to `online` / `offline` events by default (`navigator.onLine` is not used).
- `environmentManager` / `isServer` — server detection, e.g. `environmentManager.isServer()`.
- `notifyManager` — `notifyManager.setBatchNotifyFunction(fn)` sets the notification batching function (React 18 no longer uses `unstable_batchedUpdates` automatically).
- `timeoutManager` — `timeoutManager.setTimeoutProvider(...)` customizes timer behavior (e.g. to lift the ~24-day `gcTime` cap).
- `defaultScheduler` — low-level scheduler used for garbage collection.

## Devtools

Separate package, included in bundles only when `NODE_ENV === 'development'`:

```sh
npm i @tanstack/react-query-devtools
```

- **Floating mode** — `<ReactQueryDevtools initialIsOpen={false} />` places as high in the tree as possible. Options: `initialIsOpen`, `buttonPosition` (default `bottom-right`), `position`, `client`, `errorTypes`, `hideDisabledQueries`, `theme`.
- **Embedded mode** — `<ReactQueryDevtoolsPanel onClose={...} />` inside your own panel; options `style`, `onClose`, `client`, etc.
- For Next 13+ App Router, install it as a **dev dependency** for it to work.
- To lazy-load devtools in production, import `@tanstack/react-query-devtools/production` (or `build/modern/production.js`) via `React.lazy`.
- Since v5 the devtools can also observe **mutations**.

## ESLint Plugin

Recommended alongside the library: `npm i -D @tanstack/eslint-plugin-query`. It provides rules like `exhaustive-deps` (all variables used in `queryFn` must be in `queryKey`) and `no-rest-destructuring` (rest-destructuring a query result disables property tracking).
