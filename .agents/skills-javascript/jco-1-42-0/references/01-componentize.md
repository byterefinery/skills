# Componentize — building components from JS/TS

Source material: jco book chapters *Creating new JavaScript and TypeScript components*, *StarlingMonkey backend*, *QuickJS backend*, *Perry backend*, *Script-only components* (docs at tag jco-v1.42.0).

## Backends

| Backend | Selection | Notes |
|---|---|---|
| StarlingMonkey (default) | omit `--backend`, or `--backend starlingmonkey` / `sm` | componentize-js embeds StarlingMonkey (SpiderMonkey-based). Builds against your WIT world. |
| QuickJS | `--backend quickjs` / `qjs` | componentize-qjs embeds QuickJS-NG. Builds against your WIT world. |
| Perry (experimental) | `--backend perry` | User-managed Perry compiler; produces a WASI P2 command; no custom WIT bindings. |

StarlingMonkey and QuickJS are regular jco dependencies — no separate install. Perry is **not** a jco dependency.

## Scaffold a project from WIT

```console
jco scaffold hello-component --wit path/to/wit
```

- `--wit` accepts a WIT file or directory, or a bundled builtin. Builtins: `builtin:wasi-command` (`wasi:cli/command` world), `builtin:wasi-reactor` (`wasi:cli/imports`), `builtin:wasi-proxy` (`wasi:http/service` in WASI 0.3, `wasi:http/proxy` in 0.2). `wasi:package@version` and `oci://registry/repository:tag` sources are also accepted. Without a version suffix the bundled WASI is 0.3; `@0.2.x` targets the latest bundled WASI 0.2 (0.2.12 at 1.42.0).
- `--world <world>` selects the world when the package contains multiple.
- `--language typescript|javascript` (default typescript), `--package-manager pnpm|npm|yarn`, `--target nodejs|web` (repeatable; default builds both targets).
- `--host` scaffolds the other side of the boundary: a host plugin implementing the world's imports in `src/plugin.ts`, whose default export is an imports object ready to pass to `instantiate`. The regular scaffold implements the world's exports in `src/component.ts`.
- Generated project: guest TypeScript declarations, implementation skeleton, Node.js & web check/test/build scripts, configuration files, README recording the selected world and commands. The selected WIT snapshot is copied into the project's `wit/` directory, so no registry client or network access is needed.

```console
cd hello-component
pnpm install
pnpm check
pnpm test
pnpm build
```

After changing the copied `wit/` package, regenerate declarations with `pnpm types` (or `npm run types`), then keep using `check`/`test`/`build`.

## Build source directly

```console
jco componentize -w wit -o dist/component.wasm component.js
jco componentize --backend qjs -w wit -o dist/component.wasm component.js
```

- TypeScript entry modules are transformed and bundled automatically (type erasure only; run `tsc --noEmit` separately for semantic checking). The nearest `tsconfig.json` from the entry project is discovered.
- JavaScript entries pass through to the backend by default. `--bundle` bundles the entry and local/npm dependencies into a single in-memory ES module before componentization. `wasi:*` imports remain external so they match component capabilities; unresolved imports (e.g. `wasi:http`) are treated as external by Rolldown.
- `--bundle-config <rolldown.config.mjs>` merges a Rolldown configuration module (plugins, aliases, external rules, transforms, output customization). Other settings stay fixed/overridden by jco. Config functions are supported (`{ bundle: true }` is provided as input); arrays and multi-output configs are rejected.
- `--world-name <world>` picks the world when the WIT has multiple.
- `--enable` / `--disable` toggle engine features `clocks`, `http`, `random`, `stdio`, `fetch-event`, or `all`. Only disable capabilities your source and WIT world do not require (e.g. `--disable all` for a pure function component); feature switches cannot remove imports explicitly required by the WIT world — inspect the result with `jco wit`. Disabling `stdio` removes guest console output; disabling `random` makes its values deterministic.
- `--script-only` — see below.

## StarlingMonkey-only options

Jco rejects these for QuickJS and Perry.

| Option | Purpose |
|---|---|
| `--engine <path>` | Supply a compatible custom ComponentizeJS engine Wasm build |
| `--aot` / `--aot-min-stack-size-bytes <n>` | Weval ahead-of-time compilation (+ min stack size) |
| `--weval-bin <path>` / `--wizer-bin <path>` | Custom tool binaries |
| `--preview2-adapter <path>` | Custom Preview 2 adapter |
| `--debug-starlingmonkey-build` | ComponentizeJS debug engine build |
| `--debug-bindings` / `--debug-bindings-dir <dir>` | Inspect generated bindings and metadata |
| `--debug-binary` / `--debug-binary-path <path>` | Inspect generated core Wasm binary |
| `--debug-enable-wizer-logging` | Wizer call diagnostics |

ComponentizeJS evaluates top-level module code while preparing the component's initial snapshot. Put work that must run on each invocation inside exported functions, not top-level code.

## Perry backend (experimental)

- Perry compiles the original module graph to a WASI Preview 2 command component; jco does not bundle, erase TypeScript, or inject Node adapters. Supported `node:` imports (e.g. `node:fs`) use Perry's WASI implementation.
- Install: `npm install --save-dev @perryts/perry@<version>`, or point at a build directly with `--backend-perry-cli-path /path/to/perry` (also accepts `.js`/`.cjs`/`.mjs` launchers; relative paths resolve from the invocation directory). The path and `--backend-perry-package` cannot be combined.
- The compiler must support `perry compile --target wasi` — the published `@perryts/perry@0.5.1520` predates that support. Follow Perry's standalone WASI build instructions (`target-wasi` Cargo feature, matching WASI runtime archive, wasi-sdk; upstream uses LLVM 22 + wasi-sdk 34). Configure `WASI_SDK_PATH` and, for an out-of-tree runtime, `PERRY_RUNTIME_DIR`; jco inherits the compiler environment.
- Omit `--wit` and `--world-name`: Perry owns the component's world and exports `wasi:cli/run@0.2.x`. WIT/world options, jco bundling/Node adapter options, and StarlingMonkey/QuickJS-specific options are rejected.

## Script-only components (`--script-only`)

```console
jco componentize --script-only \
  --wit ./wit-greeter --wit ./wit-calc \
  greet.js calc.ts \
  -o ./dist
```

- Output is a *directory*: `dist/engine.wasm` (engine componentized against the union of the given worlds plus `jco:script-engine/script-loader`), `dist/engine.wit` (the merged world), and one tiny script-only component per source that exports `jco:script/script`.
- `--wit` and `--world-name` are both repeatable; give no world names to use each package's only world, or one name per `--wit` in order.
- Scripts may be omitted to build only the engine. A script that imports an interface the engine world does not import fails the build; exporting something the world does not export warns.
- **Warning** — scripts loaded into the same engine instance share one JavaScript realm; anything a script leaves on `globalThis` is visible to the next script. This is engine reuse, **not** a sandbox between tenants. Instantiate a fresh engine per trust boundary.
- Node.js built-in compatibility (`--with-nodejs-*`) is not available in this mode (it rewrites the WIT world per script).
- To run: transpile the engine and script components, then load scripts through the engine's `scriptLoader` export. Loading another script replaces the previous one.
