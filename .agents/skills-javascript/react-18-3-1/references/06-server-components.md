# Server Components (experimental in 18.3.1)

React 18.3.1 ships an **experimental** React Server Components (RSC) implementation: a separate runtime (`react-server`) and a wire protocol ("Flight", via `react-server-dom-webpack`). Nothing here is stable — APIs are `unstable_*`-named, move between releases, and the supported path to production RSC in this era is React 19 behind a framework (Next.js App Router, Remix). Treat this file as reference for what 18.3.1 actually contains.

## Model

- **Server components** run only on the server: they fetch data directly, can import server-only packages (databases, filesystem), and send their *rendered output* over the wire — zero JavaScript for their code.
- **Client components** (`"use client"` directive at the top of the file) run in the browser and have state, effects, and event handlers.
- The boundary is the `import` graph: a server component can import a client component (passing serializable props), but a client component can only receive serializable data or function references from the server.
- The wire protocol serializes the component tree — including **promises, functions (as references), and cycles** — into a JSON-ish "Flight" stream the client resolves into live React elements.

## The `"use client"` / `"use server"` directives

```jsx
// cart-button.jsx — everything in this module (and everything it imports) is client-side
'use client';
import { useState } from 'react';

export function CartButton() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count} in cart</button>;
}
```

- `"use client"` marks the file as the root of a client component subtree; the bundler (via the RSC plugin) compiles client modules separately and references them by ID from the server output.
- `"use server"` marks exported functions as **server actions** — serializable function references the client can invoke, which execute on the server. In 18.3.1 the Flight client exposes action invocation through the decoded model; there is no stable `useActionState`-style API in `react` itself (that arrived in 19).

## react-server package

The server-side React runtime, selected by the `react-server` export condition in `package.json` (`"exports": { "react-server": "./react-server.js" }`). A module resolved under this condition gets server-only behavior (server contexts, the RSC cache).

Key exports in 18.3.1:

```ts
createServerContext<T>(globalName: string, defaultValue: T): ServerContext<T>
unstable_Cache                       // component that scopes the request cache
unstable_getCacheForType(type: any): any     // per-type request-scoped cache slot
unstable_getCacheSignal(): AbortSignal        // signal that aborts when the request ends
unstable_useCacheRefresh(): () => void        // hook: invalidate the current cache scope
```

- **`createServerContext`** creates a lazily-evaluated, request-scoped global for server components — e.g. a database connection or session object that is created once per request and shared across all components that read that context:

```js
// server-only module
const dbContext = createServerContext('db', null);
export const db = dbContext.createConnection(() => createDb());
// in any server component:
const row = await db.query('...');
```

- **The cache** (`unstable_Cache` + `unstable_getCacheForType`) dedupes work per request: `getCacheForType(MyFetcher)` returns a map; components store computed promises by key so N components fetching the same row trigger one fetch. Wrap the tree in `<unstable_Cache>` to establish a scope; `useCacheRefresh` invalidates it.
- **`unstable_getCacheSignal`** is the request's `AbortSignal` — pass it to `fetch({ signal })` so work stops when the client goes away.

## react-server-dom-webpack (Flight)

The wire protocol implementation. Two sides:

### Client (browser)

```ts
// from 'react-server-dom-webpack'
createFromFetch(promiseForResponse: Promise<Response>, options?: { moduleMap?: Record<string, any> }): Promise<ReactNode>
createFromReadableStream(stream: ReadableStream, options?: { moduleMap?: Record<string, any> }): ReactNode
createFromXHR(xhr: XMLHttpRequest, options?: { moduleMap?: Record<string, any> }): Promise<ReactNode>
```

- Decode a Flight payload (from a server fetch) into a React element tree; client component modules are resolved through `options.moduleMap` (a map of module ID → module — in 18.3.1 this is named `moduleMap`; it was renamed `webpackMap` in 19).
- The returned tree is rendered inside a normal `createRoot`, typically inside `<Suspense>`; unresolved promises in the payload suspend.

### Server (writer)

- The writer entry (`react-server-dom-webpack/server`) exports `renderToPipeableStream(model: ReactNode, webpackMap: BundlerConfig, options?: { onError?, context?, identifierPrefix? })` and returns `{ pipe, abort }`.
- It only loads **inside a `react-server` environment**: the package's `writer.js` throws `The React Server Writer cannot be used outside a react-server environment. You must configure Node.js using the --conditions react-server flag.` — start Node with `node --conditions react-server server.js`.
- `webpackMap` maps module IDs to client modules (the same map the client uses) and the server's bundler config; the serialized output references client components by ID.

### Webpack integration

- `react-server-dom-webpack/plugin.js` — the webpack plugin that assigns stable module IDs to client modules so server and client agree on references.
- `react-server-dom-webpack/node-register.js` — a `require` hook that resolves `react` under the `react-server` condition in Node; `require('react-server-dom-webpack/node-register')` at the top of a server entry.
- A full RSC setup therefore needs: a bundler config that compiles the client entry normally, compiles the server entry with the `react-server` condition, and wires the plugin/register for module-ID agreement. This is exactly the machinery Next.js/Remix abstract away.

## Serialization rules

Data crossing the server → client boundary must be **serializable**:

- Allowed: JSON values (primitives, objects, arrays, dates as serialized), `Promise`s (resolved on the client as real promises), components (by reference), server function references (`"use server"`).
- Not allowed: arbitrary functions (except server actions), class instances, DOM nodes, `Symbol`s, `Map`/`Set` (not JSON), anything with a circular *non-reference* structure.
- Server → client prop passing: pass data (or promises of data), never functions except server actions. Client → server (action arguments): the same JSON rules apply to the arguments.
- A component's *props* are the contract: if a server component passes `props` to a client component, everything in `props` must survive Flight serialization.

## Gotchas

- **Everything is unstable.** `unstable_Cache`, `unstable_getCacheForType`, `unstable_getCacheSignal`, `unstable_useCacheRefresh`, the Flight entry points, and the `moduleMap` option all changed names/semantics by React 19. Do not lock app architecture to 18-era Flight details.
- **No `use()` in 18.3.1.** Reading promises in render via `use()` is a React 19 API; on 18 the Flight client materializes promises in the decoded tree, and client code awaits them in effects or renders them behind `Suspense`.
- **No `useActionState`/`useOptimistic` in 18.3.1** — form-state handling for server actions is hand-rolled or framework-provided on 18.
- **Two Reacts problem**: the client bundle and the server bundle each contain a React; the `react-server` condition is what makes the server copy a *different* module. Misconfigured bundlers that share one React copy across the boundary break context and hooks.
- **`"use client"` is a file-level boundary, not a component-level one** — everything the file imports (including third-party UI libraries using hooks) is pulled to the client side. Keep client subtrees small.
- If you are not already inside a framework (Next.js, Remix) that implements all of this, building RSC on raw 18.3.1 is a research project, not a production choice.
