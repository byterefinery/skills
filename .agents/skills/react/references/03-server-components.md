# React Server Components (RSC) in React 19.3.0

Verified from `packages/react-server/README.md`, the `react-server-dom-*` packages, and the CHANGELOG at tag v19.3.0.

## Architecture: two renderers in `react-server`

- **Fizz** — server-side rendering to HTML (the `react-dom/server` and `react-dom/static` front ends).
- **Flight** — the React Server Components renderer. Serializes a React tree (a superset of `structuredClone()`, plus promises, symbols, iterators) into a protocol the client can load. Server Components never ship to the client; only their rendered output does.

Flight core API (for implementing a custom bundler): `createRequest(model, clientManifest, options)`, `createPrerenderRequest(...)`, `startWork(request)`, `startFlowing(request, destination)`, `stopFlowing(request)`, `abort(request)`. Prerendering differs from realtime rendering in error handling — errored parts are omitted from the output rather than embedded, so a prerender can be discarded or resumed dynamically.

## Directives

- `'use client'` — marks a module (and everything it imports) as client code. Must be the first statement in the file, before imports.
- `'use server'` — marks a module or a single function as a Server Action. File-level it must be the first statement; placed directly on an exported function body it scopes the action to that function (closures allowed).

The bundler is responsible for registering references: client exports become **client references** (`registerClientReference`) and server functions become **server references** (`registerServerReference`). Anything can be a client reference, not just components.

## Rules

- Server Components run only on the server and may be `async` — they can await data directly.
- Server Components cannot use state, effects, or event handlers, and cannot receive functions as props.
- Data crosses the boundary as serializable values (props) or via Server Actions.
- Server Actions are callable from the client (e.g., a form's `action` prop); the client sends the call, the server runs it, and state updates flow back.

## Caching

- `cache(fn)` — memoizes `fn`'s result per RSC request (de-dupes repeated calls to the same function with the same args).
- `cacheSignal` (19.2+) — exposes when the current `cache()` lifetime is over, so long-lived work (e.g., fetch subscriptions) can be torn down.

## Prerendering and resume

- `prerender` (19.1 as `unstable_prerender`, 19.2 stable) — produces static output ahead of time; errors postpone the affected parts instead of failing.
- 19.2 resume APIs complete a postponed prerender:
  - Web Streams: `resume`, `resumeAndPrerender`
  - Node Streams: `resumeToPipeableStream`, `resumeAndPrerenderToNodeStream`
- `prerender` returns `postponed` state that the resume APIs consume.

## Bundler adapters (experimental — do not use directly in app code)

Each adapter exposes `./server`, `./client`, and `./static` entry points (plus runtime-specific `.node`, `.browser`, `.edge` variants) that wrap Flight with that bundler's module system:

- `react-server-dom-webpack` — also ships `./plugin` (webpack plugin) and `./node-register`
- `react-server-dom-turbopack`
- `react-server-dom-parcel` (added 19.1)
- `react-server-dom-esm` — plus `./node-loader` for Node's ESM loader
- `react-server-dom-unbundled` — private, extracted from `*.unbundled` subpaths in 19.2.2

These packages are explicitly experimental ("use at your own risk") and are meant for framework authors, not application developers.

## `react-markup`

Renders standalone HTML from Server Components for embedded contexts such as e-mails and RSS/Atom feeds. It cannot use Client Components and does not hydrate. `experimental_renderToHTML` is async and must be awaited — unlike legacy `renderToString`.

## `react-cache`

A basic request-scoped cache and reference implementation for advanced caching. Marked unstable and "do not use in a real application" — it exists to demonstrate the API, not to ship.
