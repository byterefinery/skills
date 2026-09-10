# Server rendering

Rendering React to HTML on the server: string renderers, streaming renderers, and client hydration. All from `react-dom/server`.

## Choosing a renderer

| API | Environment | Suspense | Notes |
|---|---|---|---|
| `renderToString` | Any | No (emits fallback) | Simple; discouraged for dynamic pages |
| `renderToStaticMarkup` | Any | No (emits fallback) | No React hydration attributes |
| `renderToNodeStream` | Node | No | Deprecated since 18 |
| `renderToStaticNodeStream` | Node | No | Deprecated in 18.3 (logs a warning) |
| `renderToPipeableStream` | Node | Yes | The Node streaming renderer |
| `renderToReadableStream` | Node, Deno, Cloudflare, … | Yes | The edge-runtime renderer |

## renderToString / renderToStaticMarkup

```ts
renderToString(children: ReactNodeList, options?: { namespaceURI?: string, identifierPrefix?: string }): string
renderToStaticMarkup(children: ReactNodeList): string
```

- Synchronous; returns a string. `renderToStaticMarkup` omits React-specific attributes (`data-reactroot` on the root, `data-did-hide` on hidden Suspense content) — for static exports, not for hydration.
- **Suspense**: since 18 these no longer throw when the tree suspends — they emit the nearest boundary's fallback HTML and the client retries the content after hydration. That is exactly why you should move to the streaming renderers for real pages.
- `identifierPrefix` feeds `useId` (see 05.4 hydration and 02 for the hook).

## renderToPipeableStream (Node)

```ts
renderToPipeableStream(
  children: ReactNodeList,
  options?: {
    identifierPrefix?: string;
    nonce?: string;                    // CSP nonce for injected scripts
    bootstrapScriptContent?: string;   // inline <script> run before hydration
    bootstrapScripts?: string[];       // classic <script src> tags
    bootstrapModules?: string[];       // <script type=module> tags
    namespaceURI?: string;             // e.g. 'http://www.w3.org/2000/svg'
    progressiveChunkSize?: number;     // bytes per chunk before yielding (default 2048)
    onError?: (error: unknown) => ?string;  // return an HTML string to emit on error
    onShellReady?: () => void;         // the outer shell (no pending suspense) is ready
    onAllReady?: () => void;           // the whole tree is ready
    onShellError?: (error: unknown) => void;
  }
): { pipe<T extends Writable>(destination: T): T; abort(): void }
```

Canonical usage:

```js
import { renderToPipeableStream } from 'react-dom/server';
import { createElement } from 'react';
import { App } from './App';

const shellStream = renderToPipeableStream(createElement(App), {
  bootstrapScripts: ['/main.js'],
  onShellReady() {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'text/html');
    shellStream.pipe(res);        // send the shell as soon as it is ready
  },
  onShellError(err) {
    res.statusCode = 500;
    res.end('Internal Server Error');
  },
});
```

- The stream emits HTML **progressively**: the "shell" (everything outside pending Suspense boundaries) first, then each boundary's content as its async work resolves, with script tags that flip `data-did-hide` content visible.
- Pipe in `onShellReady` (typical — fast Time to First Byte) or immediately if you want to buffer until fully ready. `abort()` cancels pending I/O and switches the rest to client-rendered mode (e.g. when the client disconnects).
- `onError` lets you return an HTML fragment to emit instead of the default error; `onShellError` fires for fatal shell failures.
- Do not set headers or write the status code before the shell is ready, or you defeat streaming.

## renderToReadableStream (Node + edge runtimes)

```ts
renderToReadableStream(
  children: ReactNodeList,
  options?: { /* same as pipeable, plus: */
    onFatalError?: (error: unknown) => void;
  }
): ReadableStream<Uint8Array> & { allReady: Promise<void> }
```

- Same options and progressive behavior as the pipeable stream, but returns a WHATWG `ReadableStream` for runtimes without Node `stream` (Deno, Cloudflare Workers) — and works on Node too.
- `allReady` resolves when the entire tree (all Suspense boundaries) is emitted; `onFatalError` replaces `onShellError`'s role for unrecoverable errors.
- In an edge worker: `return new Response(renderToReadableStream(<App/>, { bootstrapModules: ['/main.js'] }), { headers: { 'Content-Type': 'text/html' } })`.

## Bootstrap scripts

Both streaming renderers inject, in order, `bootstrapScriptContent` (inline), `bootstrapScripts` (`<script src>`), and `bootstrapModules` (`<script type=module src>`), plus their own hidden hydration bookkeeping. Give inline content a `nonce` for strict CSP. The bootstrap is the earliest code the client can run — use it for `globalThis.__APP__` payloads or to start the `hydrateRoot` bootstrap earlier.

## Hydration

The client adopts the server HTML:

```jsx
import { hydrateRoot } from 'react-dom/client';
hydrateRoot(document.getElementById('root'), <App />, {
  onRecoverableError: (error) => report(error),
  onHydrated: () => track('hydrated'),
});
```

- React verifies the client tree matches the server markup. On a **mismatch** (text, missing/extra nodes), React 18 no longer patches individual nodes — it logs the error and **reverts to client rendering up to the closest `<Suspense>` boundary**, re-rendering that subtree from scratch. This is deliberate: silently patching could expose server-only data to the wrong client (privacy) or create an inconsistent tree (security).
- `suppressHydrationWarning={true}` on a server-rendered element tells React to skip the mismatch warning for that element and its direct text children — the standard tool for timezones, user names, or any content that legitimately differs between server and client. Since 18.1 it works in production too.
- Suspense boundaries stream in on the client as their promises resolve, and `data-did-hide` content is revealed by the injected scripts; `onHydrated`/`onDeleted` (hydrateRoot options) fire per boundary.
- Rules for a clean hydration:
  - Render the same tree — same components, same props, same order.
  - Never read browser-only globals (`window`, `localStorage`, `Date.now()` of the client, random values) during the first render unless guarded — guard them with an effect or pass them as props from the server.
  - Initial state must match what the server rendered; derive it from props/URL, not from local clocks.
  - `useId` output matches between server and client (server IDs are `:R…`); set `identifierPrefix` identically on both sides if you have multiple roots.

## Server-side constraints

- No event handlers (`onClick` is ignored server-side), no browser APIs, no `useLayoutEffect` (it warns), no refs (they resolve to nothing).
- Class components and hooks both work in SSR; `renderToString` executes the render synchronously, so any promise thrown during it becomes a Suspense fallback (see above).
- Context works in SSR — providers on the server apply to the whole tree.
- For RSC (server components that serialize over the wire rather than HTML), see 06 — that is a different pipeline (`react-server-dom-webpack`), not `react-dom/server`.
