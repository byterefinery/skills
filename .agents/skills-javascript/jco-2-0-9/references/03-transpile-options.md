# Transpilation Options Deep Dive

## Instantiation Mode

Controls whether importing the module auto-instantiates it.

### async (default)

```js
import mod from "./component.js";
// mod is already instantiated and ready to call
mod.myFunc();
```

### sync

```js
import { instantiate } from "./component.js";
const mod = await instantiate({
  // custom imports
});
mod.myFunc();
```

Use `sync` mode when you need to supply custom imports at instantiation time.

## Import Bindings Modes

Controls how host-to-component imports are handled.

| Mode | Description |
|---|---|
| `js` | Full JS validation layer. Most compatible, best error messages. |
| `optimized` | Skips validation, assumes well-formed inputs. Fastest. |
| `hybrid` | Validates on first call, then switches to optimized path. |
| `direct-optimized` | Direct optimized bindings without JS wrapper. |

**Recommendation:** Use `js` during development for error messages, switch to `optimized` or `hybrid` in production for performance.

## Async Modes

### sync (default)

All component calls are synchronous from the host perspective. Blocking WASI calls (like file I/O) will block the JS event loop.

### jspi (experimental)

Uses JavaScript Promise Integration (JSPI) to make component calls asynchronous. Requires an engine with JSPI support (StarlingMonkey). Available in `--async-mode jspi`.

```bash
jco transpile app.wasm -o dist/ --async-mode jspi \
  --async-imports "wasi:io/poll#poll" "wasi:io/streams#[method]input-stream.blocking-read" \
  --async-exports "wasi:cli/run#run"
```

### Async WASI Presets

Use `--async-wasi-imports` and `--async-wasi-exports` to automatically mark all known WASI blocking operations as async:

**Async WASI imports:**
- `wasi:io/poll#poll`
- `wasi:io/poll#[method]pollable.block`
- `wasi:io/streams#[method]input-stream.blocking-read`
- `wasi:io/streams#[method]input-stream.blocking-skip`
- `wasi:io/streams#[method]output-stream.blocking-flush`
- `wasi:io/streams#[method]output-stream.blocking-write-and-flush`
- `wasi:io/streams#[method]output-stream.blocking-write-zeroes-and-flush`
- `wasi:io/streams#[method]output-stream.blocking-splice`

**Async WASI exports:**
- `wasi:cli/run#run`
- `wasi:http/incoming-handler#handle`

## Map Option

Custom import mappings redirect component imports to specific JS modules.

```bash
jco transpile app.wasm -o dist/ \
  -M "wasi:cli/*=@bytecodealliance/preview2-shim/cli#*" \
  -M "my:custom/iface=./my-impl.js"
```

As a JS object:

```js
await transpile("app.wasm", {
  map: {
    "wasi:cli/*": "@bytecodealliance/preview2-shim/cli#*",
    "my:custom/iface": "./my-impl.js",
  },
});
```

Wildcard patterns use `*` as a placeholder. The `#*` suffix re-maps the interface name.

## TLA Compat

Top-Level Await compatibility. When enabled, the module exports an `$init` promise:

```js
import { $init } from "./component.js";
await $init; // resolves when component is ready
import mod from "./component.js";
mod.run();
```

Without TLA compat, the module uses top-level await directly:

```js
import mod from "./component.js"; // TLA happens during import
mod.run();
```

Use `--tla-compat` when targeting bundlers or environments without TLA support.

## Base64 Cutoff

Controls whether core Wasm binaries are inlined as base64 strings or written as separate files.

```bash
jco transpile app.wasm -o dist/ --base64-cutoff 4096
```

- Below cutoff: inlined as `Uint8Array.from(atob(...), ...)` — single file, no extra imports
- Above cutoff: separate `.wasm` file, imported via dynamic import

Default cutoff is tuned for reasonable bundle sizes. Set to `0` to always use separate files, or a large value to always inline.

## Strict Mode

```bash
jco transpile app.wasm -o dist/ --strict
```

Enables runtime type checking on all component calls. Catches type mismatches early with clear error messages. Adds overhead — disable in production.

## Multi-Memory

```bash
jco transpile app.wasm -o dist/ --multi-memory
```

Required for components that use multiple linear memories. Without this flag, multi-memory components will fail at runtime.

## No Node.js Compat

```bash
jco transpile app.wasm -o dist/ --no-nodejs-compat
```

Disables the polyfill for `fetch` in Node.js environments. Use when targeting environments that always have `fetch` (modern Node.js, browsers, Cloudflare Workers).

## No WASI Shim

```bash
jco transpile app.wasm -o dist/ --no-wasi-shim
```

Disables automatic rewriting of WASI imports to use `@bytecodealliance/preview2-shim`. You must provide your own WASI implementations. Useful when running in environments with native WASI support or when using a custom WASI provider.

## Stub Generation

```bash
jco transpile wit/my-world.wit -o dist/ --stub
```

Generates a stub component implementation directly from WIT. Useful for:
- Prototyping without implementing logic
- Type checking interfaces
- Testing host-side code

## Tracing

```bash
jco transpile app.wasm -o dist/ --tracing
```

Emits tracing calls on every function entry and exit. Useful for debugging component execution flow. Integrates with Node.js `tracing` module.

## Minification

```bash
jco transpile app.wasm -o dist/ --minify --optimize
```

Minifies the generated JavaScript using Terser. Requires `--optimize` to be set. Reduces output size significantly.

## Namespaced Exports

By default, exports are namespaced for TypeScript compatibility. Disable with `--no-namespaced-exports` when the consuming project has naming conflicts.

## JS Output

```bash
jco transpile app.wasm -o dist/ --js
```

Outputs pure JavaScript instead of core WebAssembly. The component logic is compiled to JS via asm.js. Useful for environments without Wasm support (rare).

## Valid Lifting Optimization

```bash
jco transpile app.wasm -o dist/ --valid-lifting-optimization
```

Skips validation when lifting values from core Wasm to component types. Assumes all lifted values are valid. Faster but unsafe if the component produces invalid values.
