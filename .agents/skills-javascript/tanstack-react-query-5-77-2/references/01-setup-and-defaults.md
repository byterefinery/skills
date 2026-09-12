# Setup and Defaults

## Contents

- [Installation](#installation)
- [QueryClient and Provider](#queryclient-and-provider)
- [Global default options](#global-default-options)
- [Per-key defaults](#per-key-defaults)
- [The important defaults](#the-important-defaults)
- [Devtools](#devtools)
- [ESLint plugin](#eslint-plugin)

## Installation

```bash
npm i @tanstack/react-query        # or pnpm add / yarn add / bun add
```

- Requires **React 18+**; works with ReactDOM and React Native
- Browsers — Chrome ≥ 91, Firefox ≥ 90, Edge ≥ 91, Safari ≥ 15, iOS ≥ 15, Opera ≥ 77 (older browsers need self-transpilation)
- Without a bundler, load via ESM.sh in a `<script type="module">` tag

## QueryClient and Provider

One `QueryClient` per app is the typical setup; wrap the tree in `<QueryClientProvider>`:

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

- Inside components, get the client with `useQueryClient()`
- Hooks accept an optional second argument `queryClient` to override the context client — useful for multiple independent caches (e.g. separate user sessions)
- In SSR, the client must be created **inside the request scope**, never at module level (see 06-suspense-and-ssr)

## Global default options

Configure sane defaults once on the client:

```tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60,           // data is fresh for 1 minute
      gcTime: 1000 * 60 * 60,          // keep inactive data 1 hour
      retry: 3,
      refetchOnWindowFocus: false,
      // queryFn: defaultQueryFn,       // a shared default query function
    },
    mutations: {
      // mutationFn, retry, networkMode, ...
    },
  },
})
```

- `queryClient.setQueryDefaults(['todos'], { staleTime: ... })` — set defaults for a query key prefix; per-query options still win
- `queryClient.setMutationDefaults(['todos'], {...})` — same for mutation keys
- `queryClient.getDefaultOptions()` / `setDefaultOptions()` — read/replace the whole object
- A **default query function** set in `defaultOptions.queries.queryFn` receives the `QueryFunctionContext`, so you can drive an entire app from query keys alone (`useQuery({ queryKey: ['/posts'] })` with no `queryFn`)

## Per-key defaults

`setQueryDefaults`/`getMutationDefaults`/`getQueryDefaults` let you scope options to key prefixes without touching every call site.

## The important defaults

Out of the box, TanStack Query is configured with **aggressive but sane** defaults that can trip up debugging:

- **Cached data is considered stale immediately** (`staleTime: 0`). Stale queries refetch automatically in the background when a new instance mounts, the window refocuses, the network reconnects, or a `refetchInterval` is configured.
- **Inactive queries** (no active `useQuery`/observer instances) remain in the cache and are **garbage collected after 5 minutes** (`gcTime: 5 * 60 * 1000`).
- **Failed queries retry 3 times** with exponential backoff before the error surfaces to the UI. On the server, `retry` defaults to `0`.
- **Structural sharing** keeps the `data` reference stable when the response value is deeply equal (JSON-compatible values only). Disable with `structuralSharing: false` or supply a custom function.

Rule of thumb: if data looks "stuck" or refetches more than expected, the first things to check are `staleTime` and the three `refetchOn*` flags.

## Devtools

Separate package: `npm i @tanstack/react-query-devtools`. Renders are excluded from production bundles automatically (only active when `NODE_ENV === 'development'`). Since v5 the devtools also observe mutations.

```tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

<QueryClientProvider client={queryClient}>
  {/* app */}
  <ReactQueryDevtools initialIsOpen={false} />
</QueryClientProvider>
```

- Floating mode mounts a toggle in the corner; state persists in localStorage
- Options — `initialIsOpen`, `buttonPosition` (`top-left`/`top-right`/`bottom-left`/`bottom-right`/`relative`), `position` (`top`/`bottom`/`left`/`right`), `client`
- The panel shows paused queries and has a "Mock offline behavior" toggle (flips the `onlineManager`, does not touch the real network)
- For React Native, a third-party native macOS app (`rn-better-dev-tools`) can monitor queries across devices

## ESLint plugin

`npm i -D @tanstack/eslint-plugin-query` catches inconsistencies while coding. Notable rules:

- `exhaustive-deps` — warns when a `queryFn` depends on variables missing from the `queryKey`
- `no-rest-destructuring` — warns against `const { ...rest } = useQuery(...)`, which disables tracked-property re-render optimization
