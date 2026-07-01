# CLI Commands

## componentize

Create a WebAssembly component from a JavaScript module.

```
jco componentize <js-source> --wit <wit-path> -o <output.wasm>
```

| Option | Description |
|---|---|
| `-w, --wit <path>` | WIT path (required) |
| `-n, --world-name <name>` | WIT world to build |
| `--aot` | Enable Weval AOT compilation of JS |
| `--aot-min-stack-size-bytes <n>` | Min stack size for AOT |
| `--weval-bin <path>` | Custom weval binary |
| `-d, --disable <feature...>` | Disable WASI features: `clocks`, `http`, `random`, `stdio`, `fetch-event`, `all` |
| `--enable <feature...>` | Enable WASI features |
| `--debug` | Debug mode (disables all features except stdio) |
| `--preview2-adapter <path>` | Custom Preview2 adapter |
| `--debug-starlingmonkey-build` | Use debug StarlingMonkey build |
| `--engine <path>` | Specific StarlingMonkey engine |
| `-o, --out <path>` | Output component file (required) |
| `--debug-bindings` | Output debug bindings to stderr |
| `--debug-bindings-dir <dir>` | Directory for debug bindings |
| `--debug-binary` | Output binary without component metadata |
| `--debug-binary-path <path>` | Path for debug binary |
| `--debug-enable-wizer-logging` | Enable wizer debugging |

### Feature Flags

Features control which WASI capabilities are available to the component:

- `clocks` — monotonic and wall clock access
- `http` — HTTP outgoing requests
- `random` — random number generation
- `stdio` — standard input/output/error
- `fetch-event` — fetch event handling

Use `--disable all` to lock down a component, then selectively enable features.

### Old WASI HTTP Fallback

If the WIT references `wasi:http` older than 0.2.10, jco automatically falls back to `componentize-js@0.19.3`. This is because newer StarlingMonkey versions don't support old WASI HTTP. Upgrade your WIT dependencies to avoid the fallback.

## transpile

Transpile a Wasm component to ES modules for JavaScript execution.

```
jco transpile <component.wasm> -o <out-dir>
```

| Option | Description |
|---|---|
| `--name <name>` | Custom output name |
| `-o, --out-dir <dir>` | Output directory (required) |
| `-m, --minify` | Minify JS output (requires `--optimize`) |
| `-O, --optimize` | Optimize component first (pass wasm-opt args after `--`) |
| `--no-typescript` | Skip TypeScript `.d.ts` generation |
| `--valid-lifting-optimization` | Skip validation on lifted values |
| `--import-bindings [mode]` | `js` (default), `optimized`, `hybrid`, `direct-optimized` |
| `--async-mode [mode]` | `sync` (default), `jspi` (experimental) |
| `--async-wasi-imports` | Mark WASI imports as async |
| `--async-wasi-exports` | Mark WASI exports as async |
| `--async-imports <imports...>` | Specific async imports (e.g., `wasi:io/poll@0.2.0#poll`) |
| `--async-exports <exports...>` | Specific async exports (e.g., `wasi:cli/run@#run`) |
| `--tracing` | Emit tracing calls on function entry/exit |
| `-b, --base64-cutoff <bytes>` | Threshold for inlining core Wasm as base64 |
| `--tla-compat` | Async `$init` export for no-TLA environments |
| `--no-nodejs-compat` | Disable Node.js fetch compatibility |
| `-M, --map <mappings...>` | Custom import mappings (`specifier=./output`) |
| `--no-wasi-shim` | Disable automatic WASI import rewriting |
| `--stub` | Generate stub from WIT directly |
| `--js` | Output JS instead of core WebAssembly |
| `-I, --instantiation [mode]` | `async` (default), `sync` |
| `-q, --quiet` | Suppress output summary |
| `--no-namespaced-exports` | Disable namespaced exports |
| `--multi-memory` | Optimize for multi-memory components |
| `--strict` | Strict runtime type checking |

### wasm-opt Arguments

Pass arguments to wasm-opt after `--` with `--optimize`:

```bash
jco transpile app.wasm -o dist/ --optimize -- -Oz --asyncify
```

## types

Generate host-side TypeScript types from WIT.

```
jco types <wit-path> -o <out-dir>
```

| Option | Description |
|---|---|
| `--name <name>` | Custom output name |
| `-n, --world-name <world>` | WIT world name |
| `-o, --out-dir <dir>` | Output directory |
| `--tla-compat` | Types for TLA compat output |
| `-I, --instantiation [mode]` | `async` (default), `sync` |
| `--async-mode [mode]` | `sync` (default), `jspi` |
| `--async-wasi-imports` | Async WASI imports |
| `--async-wasi-exports` | Async WASI exports |
| `--async-imports <imports...>` | Specific async imports |
| `--async-exports <exports...>` | Specific async exports |
| `-q, --quiet` | Suppress output summary |
| `--feature <feature>` | Enable specific WIT feature (repeatable) |
| `--all-features` | Enable all features |
| `--wasm-opt-bin <path>` | wasm-opt binary path |
| `--strict` | Strict type checking |

Default output: `./types/generated/wit/host/`

## guest-types

Generate guest-side TypeScript types from WIT (experimental).

```
jco guest-types <wit-path> -o <out-dir>
```

Same options as `types` plus `--async-exports` and `--async-mode`. Default output: `./types/generated/wit/guest/`

## run

Execute a WASI Command component.

```
jco run <command.wasm> [args...]
```

| Option | Description |
|---|---|
| `--jco-dir <dir>` | Persist transpiled output (default: temp dir) |
| `--jco-trace` | Enable call tracing |
| `--jco-import <module>` | Custom module imported before execution |
| `--jco-map <mappings...>` | Custom import mappings |
| `--jco-import-bindings [mode]` | `js`, `optimized`, `hybrid`, `direct-optimized` |

Pass `--help` or `-h` as the first argument for help. All other arguments are forwarded to the component.

## serve

Serve a WASI HTTP component.

```
jco serve <server.wasm> [args...]
```

| Option | Description |
|---|---|
| `--port <number>` | Port (default: 8000, auto-increment on conflict) |
| `--host <host>` | Host (default: `localhost`) |
| `--jco-dir <dir>` | Persist transpiled output |
| `--jco-trace` | Enable call tracing |
| `--jco-import <module>` | Custom pre-execution module |
| `--jco-import-bindings [mode]` | Import bindings mode |
| `--jco-map <mappings...>` | Custom import mappings |

## opt

Optimize a Wasm component using Binaryen.

```
jco opt <component.wasm> -o <output.wasm> -- [wasm-opt args]
```

| Option | Description |
|---|---|
| `-o, --output <file>` | Output file (required) |
| `--asyncify` | Run Asyncify pass |
| `-q, --quiet` | Suppress output |
| `--wasm-opt-bin <path>` | wasm-opt binary path |

Default wasm-opt args: `-Oz --low-memory-unused --enable-bulk-memory --strip-debug`.

## wit

Extract WIT from a Wasm component.

```
jco wit <component.wasm> [-o output.wit]
```

| Option | Description |
|---|---|
| `-d, --document <name>` | Specific WIT document/package |
| `-o, --output <file>` | Output file (default: stdout) |

## parse

Parse WAT text format to Wasm binary.

```
jco parse <input.wat> -o <output.wasm>
```

| Option | Description |
|---|---|
| `-o, --output <file>` | Output binary (required) |

## print

Print WAT text for a Wasm binary.

```
jco print <input.wasm> [-o output.wat]
```

| Option | Description |
|---|---|
| `-o, --output <file>` | Output file (default: stdout) |

## new

Create a component from a core module with adapters.

```
jco new <core-module.wasm> -o <output.wasm> [--wasi-command|--wasi-reactor]
```

| Option | Description |
|---|---|
| `-o, --output <file>` | Output component (required) |
| `--name <name>` | Custom output name |
| `--adapt <[NAME=]adapter...>` | Component adapters |
| `--wasi-reactor` | WASI Reactor adapter |
| `--wasi-command` | WASI Command adapter |

Cannot use both `--wasi-reactor` and `--wasi-command` together.

## embed

Embed component typing into a core module.

```
jco embed [core-module.wasm] --wit <wit-world> -o <output.wasm>
```

| Option | Description |
|---|---|
| `-o, --output <file>` | Output file (required) |
| `--wit <wit-world>` | WIT world path (required) |
| `--dummy` | Generate dummy component |
| `--string-encoding <enc>` | `utf8`, `utf16`, `compact-utf16` |
| `-n, --world-name <name>` | World name to embed |
| `-m, --metadata <meta...>` | Producer metadata (`field=name[@version]`) |

## metadata-add

Add producer metadata to a Wasm binary.

```
jco metadata-add <module.wasm> -m <metadata> -o <output.wasm>
```

| Option | Description |
|---|---|
| `-m, --metadata <meta...>` | Metadata entries (repeatable, `field=name[@version]`) |
| `-o, --output <file>` | Output file (required) |

## metadata-show

Show producer metadata from a Wasm binary.

```
jco metadata-show [module.wasm] [--json]
```

| Option | Description |
|---|---|
| `--json` | Output as JSON |
