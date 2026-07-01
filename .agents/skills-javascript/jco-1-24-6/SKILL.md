---
name: jco-1-24-6
description: >
  jco (JavaScript Component Object) toolchain for building, transpiling, running, and serving
  WebAssembly Components in JavaScript. Use when working with WebAssembly Component Model in JS:
  building components from JS/TS via `jco componentize` (ComponentizeJS), transpiling .wasm
  components to ES modules via `jco transpile`, extracting WIT via `jco wit`, generating
  TypeScript types via `jco guest-types` / `jco types`, running WASI Command components via
  `jco run`, serving WASI HTTP components via `jco serve`, optimizing via `jco opt`, and
  wasm-tools operations (`jco print`, `jco parse`, `jco metadata-add`, `jco metadata-show`,
  `jco new`, `jco embed`). Covers WIT type representations, WASI Preview 2 shims, import
  mapping, instantiation modes, resource handling, and host bindings.
metadata:
  tags:
    - webassembly
    - wasm-components
    - wasm-tools
    - wasi
    - componentize-js
---

# jco 1.24.6

## Overview

jco is the JavaScript-native toolchain for [WebAssembly Components](https://github.com/WebAssembly/component-model). It lets you build components from JavaScript/TypeScript, transpile any Wasm component to ES modules runnable in Node.js and browsers, extract WIT, generate types, run WASI Command/HTTP components, and access wasm-tools from JS.

Core subprojects in the `@bytecodealliance/jco` npm package:

- **`jco`** — CLI + library API (`@bytecodealliance/jco`)
- **`jco-transpile`** — transpilation engine
- **`jco-std`** — standard library with framework adapters (`@bytecodealliance/jco-std`)
- **`preview2-shim`** — WASI Preview 2 shims for Node.js & browsers (`@bytecodealliance/preview2-shim`)
- **`preview3-shim`** — WASI Preview 3 shims for Node.js (`@bytecodealliance/preview3-shim`)

Install:

```bash
pnpm install @bytecodealliance/jco
```

For building components, also install ComponentizeJS (dynamically imported):

```bash
pnpm install @bytecodealliance/componentize-js
```

## Usage

### CLI Commands

```bash
jco componentize app.js --wit wit/ -o component.wasm       # Build component from JS
jco transpile component.wasm -o dist/transpiled             # Transpile to ES modules
jco wit component.wasm                                      # Extract WIT world
jco guest-types wit/ -o generated/types                     # Generate guest TS types
jco run command.wasm arg1 arg2                               # Run WASI Command component
jco serve --port 8080 server.wasm                            # Serve WASI HTTP component
jco opt component.wasm -o optimized.wasm                     # Optimize with Binaryen
jco print component.wasm                                    # Print WAT text
jco parse module.wat -o module.wasm                          # Parse WAT to binary
jco metadata-show component.wasm                             # Show producer metadata
jco metadata-add component.wasm -f field -v value            # Add producer metadata
jco new core.wasm -o component.wasm                          # Create component from core Wasm
jco embed core.wasm --wit wit/                               # Embed component types
```

### Library API

```js
import { transpile, componentWit, opt, print, metadataShow, parse, componentNew, componentEmbed, metadataAdd } from '@bytecodealliance/jco';

// Transpile
const { files } = await transpile(componentBytes);

// Extract WIT
const wit = componentWit(componentBytes);

// Browser-compatible API (no Node.js deps)
import { transpile as transpileBrowser } from '@bytecodealliance/jco/component';
```

### Typical Workflow

1. **Define WIT** — write `wit/component.wit` with interfaces and world
2. **Generate types** — `jco guest-types wit/ -o generated/types`
3. **Implement in JS/TS** — export interfaces matching the WIT world
4. **Build** — `jco componentize src/component.js --wit wit/ -o component.wasm`
5. **Transpile** — `jco transpile component.wasm -o dist/transpiled`
6. **Run** — import the transpiled module or use `jco run` / `jco serve`

### Transpile Options

```bash
jco transpile component.wasm -o out-dir \
  --name custom-name \
  --minify \
  --optimize \
  --tla-compat \
  --js \
  --base64-cutoff=0 \
  --no-wasi-shim \
  --map 'wasi:cli/*=@bytecodealliance/preview2-shim/cli#*' \
  --no-nodejs-compat \
  --instantiation async \
  --tracing \
  --no-namespaced-exports \
  --async-mode jspi \
  --import-bindings hybrid
```

See references for full details on transpilation modes, import mapping, instantiation, and WASI.

## Gotchas

- **`--wit` path must resolve** — `jco componentize` needs the WIT directory or file to exist. Use `--wit wit/` for a directory or `--wit wit/component.wit` for a specific file.
- **`--world-name` is required when WIT has multiple worlds** — if the WIT file defines more than one `world`, specify `--world-name world-name` to pick one.
- **`--disable all` disables all WASI imports** — use with `jco componentize` when the component doesn't need any WASI interfaces. Without it, all available WASI interfaces are imported by default.
- **WASI shim is automatic** — `jco transpile` auto-maps `wasi:*` imports to `@bytecodealliance/preview2-shim`. Install it separately: `pnpm install @bytecodealliance/preview2-shim`. Use `--no-wasi-shim` to disable.
- **`package.json` needs `"type": "module"`** — transpiled output is ESM. Node.js requires this for `.js` files to be treated as modules.
- **`componentize-js` is dynamically imported** — it must be installed alongside jco. If missing, `jco componentize` will fail at runtime.
- **Old WASI versions force componentize-js fallback** — if WIT depends on WASI packages older than 0.2.10 (e.g., `wasi:http@0.2.3`), jco falls back to componentize-js 0.19.3 which has an isolate crash bug. Update WASI deps to 0.2.10+ or newer.
- **`--instantiation async` vs ESM mode** — default transpile mode outputs a direct ES module. Use `--instantiation async` or `--instantiation sync` to get an `instantiate()` function for dynamic import binding.
- **`--map` uses `#` for sub-exports** — `--map wasi:cli/*=@bytecodealliance/preview2-shim/cli#*` maps `wasi:cli/environment` to `{ environment }` from the shim package. The `#*` reads interfaces off named exports.
- **Resources use `Symbol.dispose`** — generated types include `[Symbol.dispose]()` for disposable resources. Use `using` declarations in TS or manual `.dispose()` calls.
- **`--no-namespaced-exports` for TypeScript compat** — default transpilation outputs string-keyed exports like `export { iface as 'my:pkg/iface' }` which TypeScript doesn't support. Use this flag to get plain named exports.
- **`--tla-compat` avoids top-level-await** — instead of relying on TLA, it exports an `$init` promise that must be awaited first. Use when targeting environments without TLA support.
- **`list<u8>` becomes `Uint8Array`** — all other `list<T>` become `T[]`. When implementing host functions, pass `Uint8Array` for byte lists.
- **`result<T, E>` as function return throws** — when `result` is a direct return type, throw for error case. When `result` is inside a container (record, tuple, parameter), use `{ tag: 'ok' | 'err', val }` form.
- **`u64`/`s64` use `BigInt`** — always use `BigInt` literals (`42n`) or `BigInt()` for 64-bit integer types.
- **`jco run` / `jco serve` are JS implementations** — they use preview2-shim, not Wasmtime. For production performance, use Wasmtime directly.
- **`jco serve` is not production-ready** — it's a convenience for development. Use Wasmtime, Cloudflare Workers, or a proper server for production.
- **Nested `option<option<T>>` uses tagged form** — single-level `option<T>` maps to `T | undefined`. Doubly-nested uses `{ tag: 'some' | 'none', val: T }` to distinguish missing from empty.
- **`--import-bindings` controls host binding strategy** — `js` (default, high-level), `hybrid` (checks `Symbol.for('cabiLower')`), `optimized` (low-level only), `direct-optimized` (assumes all imports are low-level). Use `hybrid` for performance-sensitive code with fallback.

## References

- [01-transpilation-modes](references/01-transpilation-modes.md) — ESM mode, instantiation (async/sync), map configuration, WASI shims
- [02-wit-type-representations](references/02-wit-type-representations.md) — WIT to JS type mappings: records, variants, options, results, tuples, lists, resources
- [03-componentize](references/03-componentize.md) — Building components from JS/TS, WIT worlds, guest types, bundling
- [04-wasi-and-shims](references/04-wasi-and-shims.md) — WASI Preview 2 shim, preview2-shim API, sandboxing, WASIShim class
- [05-run-and-serve](references/05-run-and-serve.md) — Running WASI Command components, serving HTTP components, manual instantiation
- [06-optimized-host-bindings](references/06-optimized-host-bindings.md) — Low-level bindgen, cabiLower, ResourceTable, performance
- [07-wasm-tools](references/07-wasm-tools.md) — jco wrapper around wasm-tools: print, parse, metadata, component new/embed
- [08-examples](references/08-examples.md) — Example components: adder, HTTP servers, resources, host logging, node compat
