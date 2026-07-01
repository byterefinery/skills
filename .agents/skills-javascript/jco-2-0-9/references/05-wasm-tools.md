# wasm-tools Commands

Jco wraps `wasm-tools` functionality through transpiled Rust components. These commands work with both core Wasm modules and Wasm components.

## parse

Convert WAT (WebAssembly Text) to Wasm binary.

```bash
jco parse input.wat -o output.wasm
```

```js
import { parse } from "@bytecodealliance/jco";
const bytes = await parse(watText);
```

## print

Convert Wasm binary to WAT text.

```bash
jco print input.wasm            # stdout
jco print input.wasm -o out.wat # file
```

```js
import { print } from "@bytecodealliance/jco";
const wat = await print(bytes);
```

## component-wit

Extract WIT from a Wasm component.

```bash
jco wit component.wasm                        # stdout
jco wit component.wasm -o extracted.wit       # file
jco wit component.wasm -d wasi:cli/run        # specific document
```

```js
import { componentWit } from "@bytecodealliance/jco";
const wit = await componentWit(bytes, "wasi:cli/run"); // optional document name
```

## component-new

Create a Wasm component from a core module by applying adapters.

```bash
jco new core.wasm -o component.wasm --wasi-command
jco new core.wasm -o component.wasm --wasi-reactor
jco new core.wasm -o component.wasm --adapt my-adapter.wasm
```

### Adapters

Adapters bridge core Wasm imports/exports to component interfaces.

| Flag | Description |
|---|---|
| `--wasi-command` | WASI Command adapter (for CLI apps) |
| `--wasi-reactor` | WASI Reactor adapter (for servers) |
| `--adapt <adapter>` | Custom adapter file |
| `--adapt <NAME=adapter>` | Named adapter |

Cannot combine `--wasi-command` and `--wasi-reactor`.

### Programmatic

```js
import { componentNew, readFile } from "@bytecodealliance/jco";
import { readFile } from "node:fs/promises";

const coreBytes = await readFile("core.wasm");
const adapterBytes = await readFile("adapter.wasm");

const component = await componentNew(coreBytes, [
  ["wasi_snapshot_preview1", adapterBytes],
]);
```

## component-embed

Embed component typing information into a core Wasm module.

```bash
jco embed core.wasm --wit wit/world.wit -o embedded.wasm
jco embed --wit wit/world.wit -o dummy.wasm --dummy
```

### Options

| Option | Description |
|---|---|
| `--wit <path>` | WIT world path (required) |
| `--dummy` | Generate a dummy component (no core module) |
| `--string-encoding <enc>` | String encoding: `utf8`, `utf16`, `compact-utf16` |
| `-n, --world-name <name>` | Specific world to embed |
| `-m, --metadata <meta...>` | Producer metadata (`field=name[@version]`) |

### Full Pipeline

The typical component creation pipeline:

```bash
# 1. Embed component typing into core module
jco embed core.wasm --wit wit/world.wit -n my-world -o embedded.wasm

# 2. Adapt to create component
jco new embedded.wasm --wasi-command -o component.wasm
```

Or in one step (when the core module already has the right imports):

```bash
jco new core.wasm --wasi-command -o component.wasm
```

### Programmatic

```js
import { componentEmbed, componentNew } from "@bytecodealliance/jco";
import { readFile } from "node:fs/promises";

// Embed
const embedded = await componentEmbed({
  binary: await readFile("core.wasm"),
  witPath: "./wit/",
  worldName: "my-world",
  dummy: false,
  stringEncoding: "utf8",
  metadata: [["processed-by", [["my-tool", "1.0"]]]],
});

// Adapt
const adapter = await readFile("wasi_snapshot_preview1.command.wasm");
const component = await componentNew(embedded, [
  ["wasi_snapshot_preview1", adapter],
]);
```

## metadata-add

Add producer metadata to a Wasm binary.

```bash
jco metadata-add module.wasm \
  -m "processed-by=my-tool@1.0" \
  -m "language=rust@1.75.0" \
  -o output.wasm
```

### Programmatic

```js
import { metadataAdd } from "@bytecodealliance/jco";

const output = await metadataAdd(bytes, [
  ["processed-by", [["my-tool", "1.0"]]],
  ["language", [["rust", "1.75.0"]]],
]);
```

Metadata format: `[field, [[name, version], ...]]` per field.

## metadata-show

Display producer metadata from a Wasm binary.

```bash
jco metadata-show module.wasm        # human-readable
jco metadata-show module.wasm --json # JSON output
```

### Programmatic

```js
import { metadataShow } from "@bytecodealliance/jco";

const meta = await metadataShow(bytes);
// [
//   {
//     name: string | null,
//     metaType: { tag: "module" | "component", val: number },
//     producers: [field, [[name, version], ...]][],
//     range: [number, number]
//   }
// ]
```

## Adapter Paths

Get paths to bundled Preview1 adapters:

```js
import {
  preview1AdapterCommandPath,
  preview1AdapterReactorPath,
} from "@bytecodealliance/jco";

const commandUrl = preview1AdapterCommandPath();  // file://...wasi_snapshot_preview1.command.wasm
const reactorUrl = preview1AdapterReactorPath();  // file://...wasi_snapshot_preview1.reactor.wasm
```

Use these with `componentNew` to adapt core modules to WASI components.

## WIT Path Resolution

For commands that accept WIT paths (`embed`, `types`), the path must be the enclosing folder when dependencies exist:

```
wit/
├── component.wit        # your interfaces
├── world.wit            # your world definition
└── deps/
    ├── wasi-cli-0.2.3/
    │   └── package.wit
    ├── wasi-io-0.2.3/
    │   └── package.wit
    └── ...
```

Pass `wit/`, not `wit/world.wit`. The tool resolves the dependency graph from the folder.
