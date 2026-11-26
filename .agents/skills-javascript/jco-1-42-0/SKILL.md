---
name: jco-1-42-0
description: >
  jco (JavaScript Component Object) toolchain for building, transpiling, running, and serving
  WebAssembly components in JavaScript. Use when working with the WebAssembly Component Model in JS —
  scaffold JS/TS component or host-plugin projects from WIT via `jco scaffold`, build components from
  JS/TS via `jco componentize` (StarlingMonkey, QuickJS, or experimental Perry backends), transpile
  .wasm components to ES modules via `jco transpile`, extract WIT via `jco wit`, generate host or
  guest TypeScript types via `jco types` / `jco guest-types`, run WASI Command components via
  `jco run`, serve WASI HTTP components via `jco serve`, optimize via `jco opt`, and wasm-tools
  operations (`jco print`, `jco parse`, `jco metadata-show`, `jco metadata-add`, `jco new`,
  `jco embed`). Covers WASI 0.2/0.3 shims, import mapping, instantiation modes, WIT type
  representations, resources, error wrapping, jco-std Node.js built-in compatibility, and the
  @bytecodealliance/jco-transpile library API.
metadata:
  tags:
    - webassembly
    - wasm-components
    - wasm-tools
    - wasi
    - componentize-js
---

# jco 1.42.0

## Overview

jco is the JavaScript-native toolchain for [WebAssembly Components](https://component-model.bytecodealliance.org/). It builds components from JS/TS, "transpiles" components into ES modules runnable in Node.js and browsers, runs WASI Command/HTTP components, and exposes wasm-tools from JS. It is an experimental project — breaking changes may be made without notice.

Key packages:

| Package | Purpose |
|---|---|
| `@bytecodealliance/jco` | `jco` CLI (usable as a library) |
| `@bytecodealliance/jco-transpile` | Transpilation engine, type generation, lower-level API |
| `@bytecodealliance/jco-std` | Standard library — Node.js built-in compatibility, WASI HTTP framework adapters |
| `@bytecodealliance/preview2-shim` | WASI 0.2 implementation for Node.js and browsers |
| `@bytecodealliance/preview3-shim` | WASI 0.3 implementation (experimental) |
| `@bytecodealliance/rolldown-plugin-jco` | Rolldown/Rollup plugin for importing components in bundles |

Install (tested against the current stable even-numbered Node.js release and two versions before):

```bash
pnpm install @bytecodealliance/jco
pnpm exec jco --version
```

ComponentizeJS (StarlingMonkey) and componentize-qjs ship as jco dependencies, so `jco componentize` works out of the box. Commit the lockfile to keep backend versions pinned.

## Usage

### CLI commands

```bash
jco scaffold my-command --wit builtin:wasi-command        # Scaffold project from WIT world
jco componentize app.js --wit wit -o component.wasm      # Build component from JS/TS
jco transpile component.wasm -o out                       # Transpile to ES modules
jco wit component.wasm                                    # Extract WIT from component
jco types wit/ -o host-types                             # Host-side TS declarations
jco guest-types wit/ --world-name myworld -o guest-types # Guest-side TS declarations
jco run command.wasm arg1 arg2                            # Run WASI Command component
jco serve --port 8080 server.wasm                         # Serve WASI HTTP component
jco opt component.wasm -o out.wasm                        # Optimize with Binaryen
jco print component.wasm                                  # Component/binary -> WAT text
jco parse module.wat -o module.wasm                       # WAT text -> binary
jco metadata-show component.wasm --json                   # Show producer metadata
jco metadata-add core.wasm -m field=name -o out.wasm      # Add producer metadata
jco new core.wasm -o component.wasm                       # Core Wasm -> component
jco embed core.wasm --wit wit/ -o component.wasm          # Embed component types
```

Bundled WIT starting points for `scaffold` (default WASI 0.3; append `@0.2.x` for WASI 0.2): `builtin:wasi-command` (`wasi:cli/command`), `builtin:wasi-reactor` (`wasi:cli/imports`), `builtin:wasi-proxy` (`wasi:http/service` in 0.3, `wasi:http/proxy` in 0.2). A WIT file or package directory also works for `--wit`.

### Typical workflow (component from JS/TS)

1. **Define WIT** — world with interfaces, e.g. `world myworld { export add: func(x: u32, y: u32) -> u32; }`
2. **Generate guest types** — `jco guest-types wit/ --world-name myworld -o types`
3. **Implement in JS/TS** — export objects named after WIT interfaces
4. **Build** — `jco componentize src/component.js --wit wit -o component.wasm`
5. **Transpile** — `jco transpile component.wasm -o dist/transpiled`
6. **Run** — import the transpiled ESM module, or `jco run` / `jco serve` for WASI components

### Library API

```js
import { transpile, writeFiles } from '@bytecodealliance/jco-transpile';

const { files, imports, exports } = await transpile('component.wasm', {
  outDir: 'generated',
  instantiation: 'async',
});
await writeFiles(files);
```

Browser-compatible API (no Node.js deps): `import { transpile } from '@bytecodealliance/jco/component';`

## Gotchas

- **Treat `jco <command> --help` as the source of truth** — jco evolves quickly; flags differ between releases. Verify any flag you have not confirmed for the installed version.
- **`--wit` for scaffold is a file, directory, or builtin** — builtins are `builtin:wasi-command`, `builtin:wasi-reactor`, `builtin:wasi-proxy`; `wasi:package@version` and `oci://registry/repository:tag` sources are also accepted. `--world` selects the world when the WIT package has multiple.
- **TypeScript is bundled but not type-checked** — componentize erases types with Rolldown's transform; run `tsc --noEmit` separately for semantic checking.
- **`--bundle` is only needed for JavaScript entries** — TypeScript entries bundle automatically. For JS entries, `--bundle` bundles local/npm dependencies into one in-memory ES module; `wasi:*` imports stay external.
- **`--disable all` strips the engine's optional WASI features** — `--enable`/`--disable` take `clocks`, `http`, `random`, `stdio`, `fetch-event`, or `all`. Feature switches cannot remove imports required by the WIT world; inspect with `jco wit`.
- **WASI shims are mapped automatically** — `jco transpile` maps `wasi:*` imports to `@bytecodealliance/preview2-shim` (0.2.x) or `@bytecodealliance/preview3-shim` (0.3.x). Install the shim package for runtime use; `--no-wasi-shim` treats WASI like any other import.
- **Transpiled output is ESM** — Node.js needs `"type": "module"` in the nearest package.json.
- **`--instantiation async|sync` changes the output shape** — the default emits a direct ES module with implicit imports; instantiation mode emits a single `instantiate(getCoreModule, imports, ...)` function. Jco's default Node capability map is not applied to instantiation output — supply or map every import.
- **`--map` syntax** — `--map my:pkg/iface@1.2.3=./impl.js`; a `#` selects a named export (`=./impl.js#iface`); `*` wildcards work like package.json exports. Quote mappings in shells.
- **Top-level `result` returns throw in JS** — a `result` in a container (record field, parameter) is `{ tag: 'ok' | 'err', val }`. `u64`/`s64` are `BigInt`; `list<u8>` is `Uint8Array`, other `list<T>` are `T[]`.
- **`jco run` / `jco serve` are not a sandbox** — the default shims expose host environment, network, and (with preopens) filesystem unless explicitly sandboxed. Do not run untrusted components with ambient host access.
- **`jco serve` is for development and JS integration** — prefer Wasmtime when peak runtime performance matters.
- **Traps are not ComponentErrors** — declared WIT errors are wrapped by default in jco CLI/API output and recognized via `_util.isComponentError()`; traps are `WebAssembly.RuntimeError` and the predicate returns false for them.
- **Dispose resources explicitly** — generated resource classes implement `[Symbol.dispose]`; use `using` declarations or manual `.dispose()`, and never use a resource after passing it as `own<T>`.
- **`--script-only` scripts share one JS realm** — scripts loaded into the same engine instance see each other's `globalThis`; it is engine reuse, not a tenant sandbox.
- **Perry backend is experimental** — no custom WIT bindings; omit `--wit` and `--world-name`; the user-supplied Perry CLI must support `perry compile --target wasi`.
- **Do not install the unscoped `jco` npm package** — it is a placeholder directing users to `@bytecodealliance/jco`.
- **Node 18 quirk** — with componentize-js 0.18.3+ on Node 18 you may need to install `oxc-parser` and the platform binding manually (`--ignore-engines`).

## References

- [01-componentize](references/01-componentize.md) — scaffolding, building components from JS/TS, backends, bundling, script-only mode
- [02-transpilation](references/02-transpilation.md) — transpilation modes, all transpile options, import mapping, instantiation
- [03-wit-type-representations](references/03-wit-type-representations.md) — WIT to JS type mappings: records, variants, options, results, resources
- [04-wasi-and-shims](references/04-wasi-and-shims.md) — WASI 0.2/0.3 shims, WASIShim sandboxing, jco run/serve
- [05-errors-and-lifecycle](references/05-errors-and-lifecycle.md) — error wrapping, isComponentError, traps, stopping instances, whenIdle
- [06-jco-std-and-node-builtins](references/06-jco-std-and-node-builtins.md) — Node.js built-in compatibility, Hono/Express adapters, WASI version selection
- [07-wasm-tools](references/07-wasm-tools.md) — wit, print, parse, metadata-show/add, new, embed, opt
- [08-library-api](references/08-library-api.md) — @bytecodealliance/jco-transpile, /component subpath, rolldown-plugin-jco
