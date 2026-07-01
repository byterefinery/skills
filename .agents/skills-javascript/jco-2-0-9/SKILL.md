---
name: jco-2-0-9
description: >
  Jco (jco) v2.0.9 — JavaScript-native toolchain for WebAssembly Components.
  Use when building, transpiling, running, optimizing, or inspecting Wasm
  components from JavaScript/TypeScript. Covers CLI commands (componentize,
  transpile, run, serve, types, opt, wit, parse, print, embed, new, metadata),
  programmatic API (@bytecodealliance/jco, @bytecodealliance/jco-transpile),
  WASI Preview2/Preview3 shims, and the jco-std standard library.
  Apply for .wasm/.wit/.wasm-component workflows, componentize-js integration,
  and WASI HTTP server setups.
metadata:
  tags:
    - javascript
    - webassembly
    - wasm
    - component-model
    - wasi
    - bytecodealliance
---

# jco 2.0.9

## Overview

Jco is the Bytecode Alliance's JavaScript-native toolchain for [WebAssembly Components](https://component-model.bytecodealliance.org/). It bridges the Wasm component model with the JS ecosystem, enabling you to build, transpile, run, and optimize components entirely from JavaScript.

The `js-component-bindgen-v2.0.9` branch corresponds to the v2.0.9 era of `js-component-bindgen`. The published npm packages are `@bytecodealliance/jco@1.24.5` (CLI + API), `@bytecodealliance/jco-transpile@0.3.8` (transpilation library), `@bytecodealliance/jco-std@0.2.0` (standard library), `@bytecodealliance/preview2-shim@0.19.0` (WASI Preview2 for JS), and `@bytecodealliance/preview3-shim@0.2.0` (WASI Preview3 for Node.js).

### Core Capabilities

- **`componentize`** — Build Wasm components from JS/TS source using `componentize-js`
- **`transpile`** — Convert Wasm components to ES modules runnable in Node.js and browsers
- **`run`** — Execute WASI Command components directly
- **`serve`** — Serve WASI HTTP components as web servers
- **`types`** / **`guest-types`** — Generate TypeScript declarations from WIT files
- **`opt`** — Optimize component internals with Binaryen (wasm-opt)
- **`wit`** / **`print`** / **`parse`** — Wasm text/binary conversion and WIT extraction
- **`new`** / **`embed`** — Component creation from core modules with adapter wiring
- **`metadata-add`** / **`metadata-show`** — Producer metadata manipulation

### Architecture

Jco uses transpiled Rust crates (`js-component-bindgen`, `wasm-tools`) as Wasm components, loaded at runtime into the JS process. This avoids a native binary dependency while reusing the mature Rust Wasm ecosystem.

## Usage

### Installation

```bash
pnpm add @bytecodealliance/jco
# For building components from JS:
pnpm add @bytecodealliance/componentize-js
```

Install with `pnpm` (recommended). npm < 11.3.0 has optional dependency bugs. On Node 18.x with componentize-js >= 0.18.3, install `oxc-parser` and its platform binding manually with `--ignore-engines`.

### CLI

```bash
# Build a component from JS source
jco componentize app.js --wit wit/ -o app.wasm

# Transpile a component to JS
jco transpile app.wasm -o dist/

# Run a WASI command component
jco run app.wasm -- arg1 arg2

# Serve a WASI HTTP component
jco serve server.wasm --port 3000

# Generate TypeScript types from WIT
jco types wit/ -o ./types/

# Optimize a component
jco opt app.wasm -o app.opt.wasm

# Extract WIT from a component
jco wit app.wasm

# Convert WAT to WASM
jco parse module.wat -o module.wasm

# Convert WASM to WAT
jco print module.wasm
```

### Programmatic API

```js
import { transpile, transpileComponent, opt, typesComponent } from "@bytecodealliance/jco";

// Transpile from a file path
const result = await transpile("app.wasm", { outDir: "./dist" });

// Transpile from bytes
const result = await transpileComponent(bytes, { minify: true });

// Optimize a component
const { component: optimized } = await opt(bytes, { optArgs: ["-Oz"] });

// Generate types
const files = await typesComponent("wit/", { outDir: "./types" });
```

## Gotchas

- **`componentize` dynamically imports `componentize-js`** — it must be installed as a dependency. If the WIT uses old WASI HTTP (< 0.2.10), jco falls back to `componentize-js@0.19.3` automatically, but you should upgrade your WIT dependencies instead.
- **`transpile` requires `@bytecodealliance/preview2-shim`** at runtime for WASI imports unless `--no-wasi-shim` is used. The shim is auto-symlinked by `jco run`/`jco serve` but must be installed manually for library usage.
- **`--import-bindings` modes matter for performance** — `js` (default) is most compatible; `optimized` and `direct-optimized` skip validation for speed but require well-formed inputs; `hybrid` balances both.
- **`--async-mode jspi` requires JSPI support** — only available in engines with JavaScript Promise Integration (StarlingMonkey). Use `sync` (default) for Node.js.
- **`--tla-compat` produces `$init` promise export** — needed for bundlers or environments without top-level await. Without it, the module uses TLA directly.
- **`--multi-memory` is required for components with multiple memories** — omitting it causes runtime errors on multi-memory components.
- **`--strict` enables runtime type checking** — adds overhead but catches misuse early. Disable in production for performance.
- **`jco run` transpiles to a temp dir** — use `--jco-dir` to persist the output for debugging. The temp dir is cleaned up on exit.
- **`jco serve` auto-increments port on EADDRINUSE** — unless `--port` is explicitly set, it tries 8000 then increments.
- **`--map` uses `specifier=output` format** — wildcards work (`wasi:cli/*` maps to `@bytecodealliance/preview2-shim/cli#*`).
- **`--base64-cutoff` controls inline vs file** — core Wasm binaries smaller than the cutoff are inlined as base64 strings; larger ones are separate files. Default is reasonable for most use cases.
- **WIT path must be the enclosing folder** — when a world has dependencies, pass `wit/` not `wit/component.wit`. The error "no known packages" usually means a wrong WIT path.
- **`componentNew` vs `componentEmbed`** — `new` adapts an existing core module; `embed` bakes the component typing section into a core module. Use `embed` before `new` for the full pipeline.
- **`--no-namespaced-exports` for TypeScript** — disable when the consuming TS project has naming conflicts with the generated namespace exports.
- **`--stub` generates from WIT directly** — produces a stub component implementation without actual logic, useful for prototyping and type checking.

## References

- [01-cli-commands](references/01-cli-commands.md) — All CLI commands with full option lists
- [02-programmatic-api](references/02-programmatic-api.md) — Library API reference for `@bytecodealliance/jco` and `jco-transpile`
- [03-transpile-options](references/03-transpile-options.md) — Deep dive into transpilation options and modes
- [04-componentize](references/04-componentize.md) — Componentize command, features, and debug options
- [05-wasm-tools](references/05-wasm-tools.md) — wasm-tools commands (parse, print, wit, new, embed, metadata)
- [06-run-serve](references/06-run-serve.md) — Run and serve commands for executing components
- [07-ecosystem](references/07-ecosystem.md) — Ecosystem packages (preview2-shim, preview3-shim, jco-std, bare-jco)
