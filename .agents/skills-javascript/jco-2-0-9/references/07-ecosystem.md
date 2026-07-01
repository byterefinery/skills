# Ecosystem Packages

## @bytecodealliance/jco

The main package providing the CLI and programmatic API.

- **Version:** 1.24.5
- **Install:** `pnpm add @bytecodealliance/jco`
- **Bin:** `jco` command
- **Main:** `src/jco.js` (CLI), `src/api.js` (library)
- **Browser:** `src/browser.js` (limited functionality)

### Dependencies

- `@bytecodealliance/componentize-js` — for `componentize` command
- `@bytecodealliance/jco-transpile` — transpilation engine
- `@bytecodealliance/preview2-shim` — WASI Preview2 for JS
- `@bytecodealliance/preview3-shim` — WASI Preview3 for Node.js
- `binaryen` — wasm-opt for optimization
- `commander` — CLI framework
- `terser` — JavaScript minification

### Exports

```js
// Main API
import { transpile, transpileComponent, opt, typesComponent } from "@bytecodealliance/jco";

// wasm-tools re-exports
import { print, parse, componentWit, componentNew, componentEmbed, metadataAdd, metadataShow } from "@bytecodealliance/jco";

// Adapter paths
import { preview1AdapterCommandPath, preview1AdapterReactorPath } from "@bytecodealliance/jco";
```

## @bytecodealliance/jco-transpile

The transpilation engine, separated for standalone use.

- **Version:** 0.3.8
- **Install:** `pnpm add @bytecodealliance/jco-transpile`

### Exports

```js
// Main
import { transpile, transpileBytes, generateHostTypes, generateGuestTypes, componentWitMetadataForWorld, writeFiles } from "@bytecodealliance/jco-transpile";

// Helpers
import { /* helper exports */ } from "@bytecodealliance/jco-transpile/helpers";

// wasm-tools
import { print, parse, componentWit, componentNew, componentEmbed, metadataAdd, metadataShow } from "@bytecodealliance/jco-transpile/wasm-tools";
```

### Vendor Files

The package includes transpiled Rust components:
- `vendor/js-component-bindgen-component.js` — the bindgen component
- `vendor/wasm-tools.js` — wasm-tools component
- `vendor/interfaces/` — interface definitions

## @bytecodealliance/preview2-shim

WASI Preview2 shim for JavaScript environments. Maps WASI Preview2 interfaces to Node.js and browser APIs.

- **Version:** 0.19.0
- **Install:** `pnpm add @bytecodealliance/preview2-shim`

### Exports

```js
// Main
import { /* WASI interfaces */ } from "@bytecodealliance/preview2-shim";

// Named sub-paths
import { /* specific interface */ } from "@bytecodealliance/preview2-shim/cli";
import { /* specific interface */ } from "@bytecodealliance/preview2-shim/exit";

// Type definitions
import type { /* types */ } from "@bytecodealliance/preview2-shim/interfaces/wasi-cli-environment";

// Instantiation helpers
import { /* instantiation */ } from "@bytecodealliance/preview2-shim/instantiation";
```

### HTTP Server

```js
import { HTTPServer } from "@bytecodealliance/preview2-shim/http";

const server = new HTTPServer(incomingHandler);
server.listen(3000, "localhost");
```

### Platform Support

- **Node.js:** Full WASI Preview2 mapping using Node.js APIs
- **Browser:** Limited WASI support (no filesystem, limited clocks)

## @bytecodealliance/preview3-shim

WASI Preview3 shim for Node.js.

- **Version:** 0.2.0
- **Install:** `pnpm add @bytecodealliance/preview3-shim`
- **Dependency:** `@bytecodealliance/preview2-shim`

### Exports

```js
import { /* WASI Preview3 interfaces */ } from "@bytecodealliance/preview3-shim";
import type { /* types */ } from "@bytecodealliance/preview3-shim/interfaces/wasi-cli-environment";
```

Node.js only (no browser support).

## @bytecodealliance/jco-std

Standard library for JS WebAssembly components. Provides integrations for popular frameworks and patterns.

- **Version:** 0.2.0
- **Install:** `pnpm add @bytecodealliance/jco-std`

### Hono Integration

jco-std provides Hono framework adapters for WASI HTTP servers:

```js
import { HonoServer } from "@bytecodealliance/jco-std/wasi/0.2.x/http/adapters/hono/server";
import { configMiddleware } from "@bytecodealliance/jco-std/wasi/0.2.x/http/adapters/hono/middleware/config";
import { envMiddleware } from "@bytecodealliance/jco-std/wasi/0.2.x/http/adapters/hono/middleware/env";
```

### WASI Versions

jco-std supports both WASI 0.2.3 and 0.2.6:

```js
// WASI 0.2.6 (recommended)
import { HonoServer } from "@bytecodealliance/jco-std/wasi/0.2.6/http/adapters/hono/server";

// WASI 0.2.3 (legacy)
import { HonoServer } from "@bytecodealliance/jco-std/wasi/0.2.3/http/adapters/hono/server";

// Version-agnostic (resolves to latest)
import { HonoServer } from "@bytecodealliance/jco-std/wasi/0.2.x/http/adapters/hono/server";
```

### Generated Types

jco-std includes generated TypeScript types for WASI interfaces:

```
src/wasi/0.2.x/
├── cli/environment.ts
├── config.ts
├── hono.ts
├── http/index.ts
├── http/types/request.ts
├── http/types/response.ts
└── logging.ts
```

### Supported WASI Interfaces

| Interface | Description |
|---|---|
| `wasi:cli/environment` | Environment variables and arguments |
| `wasi:clocks/monotonic-clock` | Monotonic clock |
| `wasi:config/runtime` | Runtime configuration |
| `wasi:config/store` | Configuration store |
| `wasi:http/incoming-handler` | HTTP request handler |
| `wasi:http/types` | HTTP types (request, response) |
| `wasi:io/error` | I/O error handling |
| `wasi:io/poll` | I/O polling |
| `wasi:io/streams` | I/O streams |
| `wasi:logging/logging` | Logging interface |

## jco (bare)

Redirect package for `@bytecodealliance/jco`. Provides the `jco` command under the plain `jco` package name.

- **Version:** 1.0.0
- **Install:** `pnpm add jco`
- **Use:** `jco` CLI command (same as `@bytecodealliance/jco`)

## @bytecodealliance/componentize-js

The underlying tool that compiles JS to Wasm components. Used by `jco componentize`.

- **Install:** `pnpm add @bytecodealliance/componentize-js`
- **Versions:** 0.21.0 (current), 0.19.3 (fallback for old WASI HTTP)

### API

```js
import { componentize } from "@bytecodealliance/componentize-js";

const result = await componentize(source, {
  witPath: "./wit/",
  worldName: "my-world",
  disableFeatures: ["http"],
  enableFeatures: ["clocks", "stdio"],
  enableAot: false,
  sourceName: "app.js",
});

// result: { component: Uint8Array, debug?: object }
```

## Installation Notes

### Package Manager

Use `pnpm` (recommended). npm < 11.3.0 has bugs with optional dependencies.

### Node 18.x

With componentize-js >= 0.18.3 on Node 18.x:

```bash
pnpm install oxc-parser --ignore-engines
pnpm install @oxc-parser/binding-linux-x64-gnu --ignore-engines
```

Replace the platform binding with the appropriate one for your system.

### Platform Bindings

componentize-js includes platform-specific native bindings. If installation fails, check that your platform is supported and install the matching binding package.
