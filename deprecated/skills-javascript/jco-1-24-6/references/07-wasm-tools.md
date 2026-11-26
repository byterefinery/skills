# Wasm Tools

jco provides JavaScript access to wasm-tools functionality via component builds.

## CLI Commands

### Print WAT

```bash
jco print component.wasm
```

Prints the WebAssembly text format (WAT) for a binary file.

```bash
jco print component.wasm -o output.wat
```

### Parse WAT

```bash
jco parse module.wat -o module.wasm
```

Parses WAT text format into a Wasm binary.

### Extract WIT

```bash
jco wit component.wasm
```

Extracts the WIT world definition from a component.

```bash
jco wit component.wasm -o world.wit
```

### Metadata

```bash
# Show producer metadata
jco metadata-show component.wasm

# Add producer metadata
jco metadata-add component.wasm -f processed-by -v my-tool/1.0 -o output.wasm
```

### Component Creation

```bash
# Create component from core Wasm
jco new core.wasm -o component.wasm

# With adapter modules
jco new core.wasm --adapter adapter1.wasm --adapter adapter2.wasm -o component.wasm
```

### Component Embedding

```bash
# Embed component types into core Wasm
jco embed core.wasm --wit wit/component.wit -o embedded.wasm
```

Advanced use case for component generation pipelines.

## Library API

```js
import {
  componentWit,
  print,
  metadataShow,
  parse,
  componentNew,
  componentEmbed,
  metadataAdd,
} from '@bytecodealliance/jco';

// Extract WIT
const wit = componentWit(componentBytes);

// Print WAT
const wat = print(componentBytes);

// Show metadata
const metadata = metadataShow(componentBytes);

// Parse WAT
const wasmBytes = parse(watString);

// Create component from core Wasm
const component = componentNew(coreWasmBytes, [
  ['adapter1', adapter1Bytes],
  ['adapter2', adapter2Bytes],
]);

// Embed component types
const embedded = componentEmbed(coreWasmBytes, witString, {
  stringEncoding: 'utf8',
  world: 'myworld',
});

// Add metadata
const withMetadata = metadataAdd(wasmBytes, {
  'processed-by': ['my-tool/1.0'],
});
```

## componentNew

Creates a WebAssembly component from a core Wasm module, optionally with named adapter modules:

```js
const component = componentNew(coreWasm, [
  ['wasi_snapshot_preview1', adapterBytes],
]);
```

Adapters bridge between core Wasm imports/exports and component interfaces.

## componentEmbed

Embeds component typing sections into a core Wasm module. Used as an advanced step in component generation:

```js
const embedded = componentEmbed(coreWasm, witString, {
  stringEncoding: 'utf8',  // or 'compact'
  dummy: true,              // use dummy imports
  world: 'myworld',         // target world name
  metadata: { 'tool': ['version'] },
});
```

## Gotchas

- **`jco new` needs adapters** — creating a component from core Wasm usually requires WASI adapter modules
- **`jco embed` is advanced** — typically used in build tooling, not day-to-day development
- **Metadata is additive** — `metadata-add` adds to existing metadata, doesn't replace
- **`componentWit` may need document name** — for multi-document WIT, specify the document: `componentWit(bytes, 'document-name')`
