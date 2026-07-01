# Componentize Command

## Overview

`jco componentize` wraps `@bytecodealliance/componentize-js` to build WebAssembly components from JavaScript/TypeScript source files. It compiles JS to a Wasm component using the StarlingMonkey JS engine, with WASI capabilities controlled by feature flags.

## Basic Usage

```bash
jco componentize app.js --wit wit/ -o app.wasm
```

The JS source exports functions that match the WIT world's interface. The WIT file defines the component's imports and exports.

## WIT World Structure

```wit
package my:component;

world my-world {
  import wasi:cli/environment@0.2.3;
  import wasi:cli/stdout@0.2.3;
  import wasi:cli/stderr@0.2.3;

  export wasi:cli/run@0.2.3;
}
```

The JS source implements the exported interfaces:

```js
// app.js — implements wasi:cli/run
export function run() {
  // component entry point
}
```

## Feature Flags

Features control which WASI capabilities the component can use. They are compiled into the StarlingMonkey engine.

### Available Features

| Feature | Description |
|---|---|
| `clocks` | Monotonic and wall clock access |
| `http` | Outgoing HTTP requests (fetch) |
| `random` | Random number generation |
| `stdio` | Standard input, output, error |
| `fetch-event` | Fetch event handling for edge runtimes |

### Disabling Features

```bash
# Disable specific features
jco componentize app.js --wit wit/ -o app.wasm --disable http random

# Disable all features
jco componentize app.js --wit wit/ -o app.wasm --disable all

# Disable all, then re-enable specific ones
jco componentize app.js --wit wit/ -o app.wasm --disable all --enable stdio clocks
```

### Debug Mode

```bash
jco componentize app.js --wit wit/ -o app.wasm --debug
```

`--debug` is equivalent to `--disable all --enable stdio`. It strips all WASI capabilities except standard I/O, useful for testing components in isolation.

## AOT Compilation

```bash
jco componentize app.js --wit wit/ -o app.wasm --aot
```

Enables Ahead-Of-Time compilation using `weval` (Wasmtime's AOT compiler). Pre-compiles the JS engine bytecode, reducing startup time.

```bash
# Custom AOT settings
jco componentize app.js --wit wit/ -o app.wasm --aot --aot-min-stack-size-bytes 65536
```

### Custom weval Binary

```bash
jco componentize app.js --wit wit/ -o app.wasm --aot --weval-bin /path/to/weval
```

## Custom Preview2 Adapter

```bash
jco componentize app.js --wit wit/ -o app.wasm --preview2-adapter /path/to/adapter.wasm
```

Use a custom WASI Preview2 adapter instead of the bundled one.

## Custom Engine

```bash
jco componentize app.js --wit wit/ -o app.wasm --engine /path/to/starlingmonkey
```

Specify a particular StarlingMonkey build. Use `--debug-starlingmonkey-build` for a debug build with extra logging.

## Debug Options

### Debug Bindings

```bash
# Output bindings and metadata to stderr
jco componentize app.js --wit wit/ -o app.wasm --debug-bindings

# Output to a specific directory
jco componentize app.js --wit wit/ -o app.wasm --debug-bindings-dir ./debug/
```

### Debug Binary

```bash
# Output the raw binary (without component metadata)
jco componentize app.js --wit wit/ -o app.wasm --debug-binary

# Specify output path
jco componentize app.js --wit wit/ -o app.wasm --debug-binary-path ./debug/core.wasm
```

### Wizer Logging

```bash
jco componentize app.js --wit wit/ -o app.wasm --debug-enable-wizer-logging
```

Enables logging during the Wizer pre-initialization phase.

## World Name

When the WIT directory contains multiple worlds, specify which one to build:

```bash
jco componentize app.js --wit wit/ -n my-world -o app.wasm
```

## Old WASI HTTP Detection

jco automatically detects if the WIT uses old `wasi:http` (< 0.2.10) and falls back to `componentize-js@0.19.3`. This is because newer StarlingMonkey versions don't support old WASI HTTP for fetch.

To avoid the fallback:
1. Update WIT dependencies to `wasi:http@0.2.10` or later
2. Use `wkg update` to refresh the WIT lock file

The fallback emits a warning:
```
warning Falling back to componentize-js 0.19.3 because this component
requests Preview 2 WASI packages older than 0.2.10.
```

## WIT Path Gotchas

The `--wit` path must resolve to the enclosing WIT folder, not a single file:

```bash
# Correct — pass the folder
jco componentize app.js --wit wit/ -o app.wasm

# Wrong — passing a specific file
jco componentize app.js --wit wit/component.wit -o app.wasm
```

When a world has dependencies (in `wit/deps/`), the enclosing folder is required so the tool can resolve the dependency graph.

## Programmatic Componentize

```js
import { componentize } from "@bytecodealliance/componentize-js";

const result = await componentize(source, {
  witPath: "./wit/",
  worldName: "my-world",
  disableFeatures: ["http", "random"],
  enableFeatures: ["clocks", "stdio"],
  enableAot: false,
  aotMinStackSizeBytes: 65536,
  wevalBin: "/path/to/weval",
  sourceName: "app.js",
  preview2Adapter: "/path/to/adapter.wasm",
  debugBuild: false,
  engine: "/path/to/starlingmonkey",
  debug: {
    bindings: false,
    bindingsDir: null,
    binary: false,
    binaryPath: null,
    enableWizerLogging: false,
  },
});

// result: { component: Uint8Array, debug?: object }
```
