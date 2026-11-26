# jco-std and Node.js built-in compatibility

Source material: jco book chapters *JavaScript ecosystem interoperability*, *jco-std*, *Express* (docs at tag jco-v1.42.0).

## What jco-std is

`@bytecodealliance/jco-std` is Jco's library of reusable JS/TS building blocks for component authors: portable implementations and ecosystem adapters that do not belong in generated WIT bindings or one application. The WIT world remains the source of truth for host capabilities — importing a helper does not grant filesystem, network, or environment access.

```console
pnpm add @bytecodealliance/jco-std
```

It is ordinary ESM, so `jco componentize` bundles explicit imports with the rest of the component.

## Node.js built-in compatibility (experimental)

Application code imports supported Node.js APIs exactly as under Node.js — do **not** rewrite `node:*` imports to internal jco-std exports:

```ts
import assert from 'node:assert/strict';
```

Componentize with the built-in support (TypeScript bundles automatically; JavaScript needs `--bundle`):

```console
jco componentize app.ts --wit wit -o app.wasm
jco componentize app.js --bundle --wit wit -o app.wasm
```

Jco consumes selected jco-std implementations internally and redirects supported `node:` specifiers while bundling; the app does not need `jco-std` as a direct dependency for built-in compatibility.

**Warning** — this is experimental: APIs, behavior, and generated component interfaces may change incompatibly without a semver-major release.

Implementations jco-std currently owns:

- `node:assert` (+ `/strict`), adapted from Node.js 24
- `node:util` (+ `/types`) — equality, console formatting, scheduling, validation, MIME utilities
- `node:path` (+ `/posix`, `/win32`) — portable algorithms plus a `wasi:cli/environment` provider for cwd-dependent ops
- sync `node:child_process` — over the explicit `jco:node/child-process@0.1.0` capability; **default provider denies access**, opt-in Node host provider delegates to the real API
- `node:fs` (+ `/promises`) — over the explicit `jco:node/fs@0.1.0` capability; **default provider denies access**
- `node:http` client/server — over selectable direct `jco:node/http@0.1.0` (denied by default), `wasi:sockets`, or `wasi:http` (rejects server construction)
- `node:http2` — direct provider delegates after explicit host mapping; `wasi-sockets` implements cleartext HTTP/2 clients and TCP servers
- `node:readline` (+ `/promises`), `node:repl`, `node:tty` (over `jco:node/tty@0.1.0`, denied by default), `node:stream/consumers`, experimental `node:stream/iter`
- Buffer and querystring cores come from `unenv`, wrapped by Jco during bundling

An opt-in capability with a denying default means the host must explicitly map a provider (e.g. via `--map`) to grant access — this is the sandbox boundary for `fs`, `child_process`, `tty`, and direct `http`.

## Hono and WASI HTTP

The Hono adapter connects a normal Hono app to a `wasi:http/incoming-handler` component export:

```ts
import { Hono } from 'hono';
import { fire, incomingHandler } from '@bytecodealliance/jco-std/wasi/0.2.x/http/adapters/hono/server';

const app = new Hono();
app.get('/', (context) => context.text('Hello from a component'));

fire(app);
export { incomingHandler };
```

The package also exports Hono middleware adapters for WASI configuration and environment access. The target WIT world must still import/export the required WASI interfaces.

### WASI version selection in package paths

- `wasi/0.2.x` selects the newest WASI 0.2 adapter verified with the ComponentizeJS version jco uses; it can advance in a jco-std release.
- Use a fully versioned export (`wasi/0.2.12`, `wasi/0.2.6`, ...) when the component must stay aligned with a particular WIT world. The package export version and the world's imported versions must agree.

jco-std adapters and Node built-in compatibility are complementary — both can be bundled into the same component (e.g. a Hono adapter plus `node:assert` and `node:buffer`).

## Express (fixture-validated)

Express 5.2.1 runs as an ordinary npm dependency; jco does not replace the router or middleware. Componentize with `jco componentize --bundle --with-nodejs-http-via direct`; keep the WIT world limited to application exports (jco discovers and adds required Node interfaces plus `wasi:cli/environment` while bundling). On the host, register the HTTP provider per component (`createHttpHost(() => instance.httpCallbacks)` pattern). Create the Express app inside an exported function — `express()` reads the working directory through WASI, unavailable during module pre-initialization. The direct transport buffers request/response bodies; this is not a claim that every Express extension or streaming workload is supported.

## Component tests

The versioned `wasi/0.2.x/node/24.x.x/test` and `test/reporters` entry points reuse jco-std's assertion, error, path, and stream implementations. Prefer ordinary `node:test` and `node:test/reporters` imports through `jco componentize`; direct jco-std imports can coexist in the same component.
