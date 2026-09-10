# Server rendering — `react-dom/server` (18.3.1)

Entry resolution: `react-dom/server` picks the Node implementation by default; the `browser`, `worker`, and `deno` conditions resolve to the browser/edge build (`renderToReadableStream` instead of `renderToPipeableStream`). Explicit entries `react-dom/server.node` and `react-dom/server.browser` always exist.

## Contents

- [String renderers](#string-renderers)
- [Streaming renderers](#streaming-renderers)
- [Streaming options](#streaming-options)
- [Hydration](#hydration)
- [SSR rules of thumb](#ssr-rules-of-thumb)

## String renderers

| Function | Purpose |
|---|---|
| `renderToString(element, { identifierPrefix }?)` | Full SSR markup including hydration attributes. **Suspense**: 18 emits the closest `<Suspense>` fallback markup and re-renders that boundary on the client — it never throws on the server |
| `renderToStaticMarkup(element, { identifierPrefix }?)` | Markup without hydration bookkeeping (no `data-*` markers) — for static email/newsletter-style content |
| `renderToNodeStream`, `renderToStaticNodeStream` | **Deprecated** — legacy streams with no Suspense support; use `renderToPipeableStream` |

`renderToString` is fine for small pages and tests; for pages with `Suspense` data fetching use the streaming APIs.

## Streaming renderers

### Node — `renderToPipeableStream`

```js
import { renderToPipeableStream } from 'react-dom/server';

const { pipe, abort, allReady } = renderToPipeableStream(<App />, options);
pipe(res); // one writable destination only — a second pipe() throws
```

Returned `PipeableStream`:

| Member | Purpose |
|---|---|
| `pipe(destination)` | Start flowing into a Node `Writable` (call once, typically from `onShellReady`) |
| `abort(reason?)` | Cancel pending I/O, flush remaining work, and mark the stream aborted |
| `allReady` | Promise that resolves when every Suspense boundary has finished |

### Edge — `renderToReadableStream`

```js
import { renderToReadableStream } from 'react-dom/server';

const stream = renderToReadableStream(<App />, options);
return new Response(stream); // ReadableStream
```

Returns a `ReadableStream` with an extra `allReady` promise (same meaning as above). No `pipe`/`abort` members — cancel with the `signal` option.

## Streaming options

Both renderers accept (from the 18.3.1 source):

| Option | Meaning |
|---|---|
| `identifierPrefix` | Prefix for `useId`; keep identical to the client `createRoot` option |
| `namespaceURI` | SVG namespace for the root (default: HTML) |
| `nonce` | CSP nonce applied to injected hydration/bootstrap scripts |
| `bootstrapScriptContent` | Inline script content executed at hydration start (must be CSP-safe; 18.1 fixed escaping) |
| `bootstrapScripts` | `Array<string>` of script URLs the client must load before hydration |
| `bootstrapModules` | `Array<string>` of ES module URLs (loaded with `type="module"`) |
| `progressiveChunkSize` | Bytes of inline work per chunk — tune to trade latency against main-thread stalls (default ~2048) |
| `onError(error)` | Required for robust streaming; return a **digest string** (or null) — React embeds digests in the stream for RSC recovery |
| `signal` (Readable) | `AbortSignal` to cancel rendering |
| `onShellReady` (Pipeable) | Shell (everything outside Suspense fallbacks) is ready — set headers and `pipe()` now |
| `onShellError(error)` (Pipeable) | Shell failed before it was sent — abort the response |
| `onAllReady` (Pipeable) | All content resolved — send late content or log metrics |

Streaming mechanics: React sends the **shell** (static content + Suspense fallback placeholders), then resolves boundaries in the background, emitting small inline scripts that swap in finished chunks. Client-side **selective hydration** attaches event handlers to hydrated subtrees as the user interacts with them, prioritizing what the user touches.

## Hydration

```js
import { hydrateRoot } from 'react-dom/client';
hydrateRoot(document.getElementById('root'), <App />, options);
```

- `hydrateRoot` reuses the server DOM where it matches; on mismatch it recovers by **client-rendering the subtree up to the nearest `<Suspense>` boundary**.
- **Text mismatches are errors in 18** (17 warned and patched individual nodes). Server-only text (timestamps, random IDs without `useId`) is the usual cause — make server output deterministic or suppress per element.
- `suppressHydrationWarning` silences a mismatch on a single element (dev and prod).
- Hydration is concurrent: while the shell streams in, user interactions can hydrate subtrees early (selective hydration); `unstable_scheduleHydration(node)` on the hydration root requests hydration of a specific node.
- Effects (`useEffect`) of hydrated subtrees run at hydration time; `useLayoutEffect` does not run on the server (dev warning) and runs when the subtree hydrates.
- `onRecoverableError` on `createRoot`/`hydrateRoot` receives errors React recovers from during hydration.

## SSR rules of thumb

- No `window`/`document`/`localStorage` access during render — the server has no DOM; guard in effects or `typeof window !== 'undefined'`.
- `useSyncExternalStore` must provide `getServerSnapshot` (a constant is usually right) so SSR and the first client render agree.
- `useRef`/`useState` initializers run on the server too — keep them pure.
- Context values and props that cross to the client must be serializable in RSC setups; plain SSR (createRoot + hydrateRoot) only needs the *rendered HTML* to match, not the props.
- Keep `identifierPrefix` identical on server and client, or `useId`-based markup will mismatch.
- Log `onError` digests server-side; without an `onError` the stream hard-fails on uncaught errors.
