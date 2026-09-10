# React Server Components — experimental status in 18.3.1

RSC was **experimental** throughout the 18 line. Nothing here is a stable API: signatures changed frequently during 18.3.x and again in 19. Treat this file as an architecture map, not a contract. Do not build production systems on it in 18.

## Contents

- [How it works](#how-it-works)
- [The `react-server` export condition](#the-react-server-export-condition)
- [react-server-dom-webpack (0.1.0)](#react-server-dom-webpack-010)
- [Server context](#server-context)
- [Experimental cache APIs](#experimental-cache-apis)
- [Limitations](#limitations)

## How it works

Server components render on the server; their output (elements and serializable data) streams to the client over the **Flight** protocol — a custom text-based format — and client components hydrate around it. The client receives a module map (the "webpack map") that tells it which client modules to load.

Packages involved:

| Package | Role |
|---|---|
| `react-server` (internal, not published) | Fizz/Flight streaming renderer: `createRequest`, `startWork`, `startFlowing`, server context implementation, `ReactFlightServerConfig*` |
| `react-client` (internal, not published) | Marker package for client-component module resolution |
| `react-server-dom-webpack` (published, 0.1.0) | Webpack wiring: plugin, writer, client entry, Node module registration |

## The `react-server` export condition

`react`'s `package.json` has a `react-server` condition on its `.` export: bundlers compiling **server components** resolve `react` to `react.shared-subset.js` instead of the full build. The subset (18.3.1) keeps elements, `Fragment`/`Profiler`/`StrictMode`/`Suspense`/`SuspenseList`, `cloneElement`, `createRef`, `forwardRef`, `isValidElement`, `lazy`, `memo`, `startTransition`, `useId`, `useCallback`, `useContext`, `useDebugValue`, `useDeferredValue`, `useMemo`, `useTransition`, and adds the unstable server APIs `unstable_createMutableSource`, `unstable_useMutableSource`, `unstable_getCacheForType`, `unstable_getCacheSignal`. It omits DOM-facing hooks (`useState`, `useEffect`, `useRef`, …) — server components cannot use them.

In Node, the condition activates with `node --conditions react-server`; webpack/parcel/turbopack plugins configure it per compilation target.

## react-server-dom-webpack (0.1.0)

Export map (verified in the 18.3.1 tag):

| Entry | Exports | Side |
|---|---|---|
| `react-server-dom-webpack` | `createFromReadableStream(stream)`, `createFromXHR(xhr)`, `createFromFetch(fetchResult)` | Client — turn a Flight stream into a React element tree |
| `react-server-dom-webpack/writer` | Node: `renderToPipeableStream(model, webpackMap, options)`; browser: `renderToReadableStream(model, webpackMap, options)` | Server — stream an RSC tree |
| `react-server-dom-webpack/plugin` | `ReactFlightWebpackPlugin` (webpack 5) | Build — emits the module map, applies `react-server` condition, registers shared chunks |
| `react-server-dom-webpack/node-register` | Registers Node `require` interception for Flight modules | Runtime (Node) |
| `react-server-dom-webpack/node-loader` | ESM loader equivalent | Runtime (Node, ESM) |

Sketch of the 18.3 wiring:

```js
// server (Node)
import { renderToPipeableStream } from 'react-server-dom-webpack/writer';
const { pipe } = renderToPipeableStream(<App />, webpackMap, {
  onError(err) { return 'FATAL'; },
  context: [[themeContext, dark]], // serializable server context pairs
  identifierPrefix: 'R',
});

// client
import { createFromReadableStream } from 'react-server-dom-webpack';
const app = await createFromReadableStream(await res.arrayBuffer());
createRoot(document.getElementById('root')).render(<AppShell app={app} />);
```

Server options: `onError`, `context` (array of `[ServerContext, value]` pairs), `identifierPrefix`. The webpack plugin (`new ReactFlightWebpackPlugin({ webpack: require('webpack') })`) must be applied to the server compilation with the `react-server` target so module IDs match between the two compilations.

**Server references** (client invoking a server function) are *not* part of the public 18.3.1 API — `registerServerReference` and friends landed later. Anything you read about "server actions" is post-18.

## Server context

`createServerContext(displayName?)` from `react` creates a context that works across the server/client RSC boundary. Values must be serializable (primitives, JSON-able objects). On the server, values are set via the writer's `context` option or nested provider elements; on the client, plain `useContext` reads them. Client-rendered values must match what the server sent, or you get a mismatch — same discipline as `identifierPrefix`.

## Experimental cache APIs

Exported from `react` (stable-channel build, behind feature flags internally):

- `unstable_Cache` — a `<Cache>` element wrapping a subtree that shares one cache per render pass.
- `unstable_getCacheForType(() => new Map())` — memoize an instance per type for the current render (replaces the `react-cache` LRU pattern; the private `react-cache` package in the repo is the 17-era predecessor and is not published).
- `unstable_getCacheSignal()` — an `AbortSignal` aborting when the render is discarded (interrupted by a new update).
- `unstable_useCacheRefresh()` — returns a `refresh` function that invalidates the cache for the current subtree (used with `Cache` for "this cache went stale" logic).

These are the seeds of what became 19's `cache()`/`react.cache`; do not rely on them in 18.

## Limitations

- No DOM APIs, no event handlers, no client hooks in server components.
- Props flowing client → server must be serializable; module/function identity must travel through the webpack map.
- The Flight protocol format is unstable — it changed within the 18.3.x line.
- Edge support: the writer's browser entry targets Web Streams; Node entry targets `stream.Writable`.
- For production RSC in this era, frameworks (Next.js 13.4+, with Turbopack/webpack) wrapped this experimental layer — use the framework, not these packages directly.
