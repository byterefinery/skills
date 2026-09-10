# `react-dom` — entry points and APIs in 19.3.0

Verified from `packages/react-dom/` package exports and entry files at tag v19.3.0.

## Entry points

- `react-dom` — shared exports (`version`, hooks, form helpers, preload helpers)
- `react-dom/client` — browser: `createRoot`, `hydrateRoot`, `version`
- `react-dom/server` (+ `.node`, `.browser`, `.edge`, `.bun`) — streaming SSR
- `react-dom/static` (+ `.node`, `.browser`, `.edge`) — static prerendering
- `react-dom/profiling` — profiling build of the client
- `react-dom/test-utils` — legacy test helpers; `React.act` (from `react`) is the 19 way
- `react-dom/unstable_testing` — unstable testing internals
- `react-dom/unstable_server-external-runtime` — external runtime helpers for server builds

## Browser

- `createRoot(container, options)` — `options` accepts `onCaughtError` and `onUncaughtError` (19.0: uncaught render errors go to `window.reportError` by default). Returns a root with `render()` and `unmount()`.
- `hydrateRoot(container, initialChildren, options)` — hydrate server-rendered HTML; same error options.
- `flushSync(callback)` — force a synchronous flush of pending updates.
- `createPortal(children, container)` — render into a different DOM subtree.
- `unstable_batchedUpdates` — unstable batching escape hatch.

### Resource hints (19.0)

- `preinit(href, options)` — preload a stylesheet or script and register it for the app shell
- `preinitModule(href, options)` — same, for modules
- `preload(href, options)` — preload an asset (e.g., an image)
- `preloadModule(href)` — prefetch a JS module
- `preconnect(href, options)` — early connection to a domain
- `prefetchDNS(href)` — early DNS lookup

### Forms and status (19.0)

- `<form action={fn}>` and `<button|input formAction={fn}>` — Actions; on success React auto-resets uncontrolled inputs
- `requestFormReset(form)` — manually reset a form
- `useFormStatus()` — from `react-dom`: `{ pending, data, method, action }` of the nearest enclosing form's action
- `useFormState(action, initialState, permalink?)` — from `react-dom`: pair an Action with a form and get `[state, formAction, isPending]`

## Document metadata (19.0)

Render `<title>`, `<meta>`, `<link>`, `<style>`, `<script>` anywhere in the component tree; React hoists them into `<head>` and dedupes them. Stylesheets gate the reveal of Suspense boundaries that depend on them; async `<script>` tags are ordered and deduplicated.

## Server (`react-dom/server`)

- `renderToPipeableStream(element, options)` — Node SSR. Options callbacks: `onShellReady`, `onShellError`, `onAllReady`, `onError`, `onFatalError` (plus `identifierPrefix`, `progressiveChunkSize`).
- `renderToReadableStream(element, options)` — Web Streams SSR for Node and edge runtimes.
- `resume(children, postponedState, options)` / `resumeToPipeableStream(...)` — 19.2: resume a partially prerendered shell to a stream (element first, then the `postponed` state from `prerender`).
- `renderToString` / `renderToStaticMarkup` — legacy, non-suspending, blocking; avoid for new code.

## Static (`react-dom/static`)

- `prerender(element, options)` — 19.2 (experimental in 19.1 as `unstable_prerender`). Waits for data; resolves to `{ postponed, prelude }` where `prelude` is a stream of completed HTML and `postponed` is `null` (fully prerendered) or state to pass to the resume APIs.
- `prerenderToNodeStream(element, options)` — streaming variant for Node.
- `resumeAndPrerender(element, postponed, options)` / `resumeAndPrerenderToNodeStream(...)` — 19.2: complete a postponed prerender into HTML.
