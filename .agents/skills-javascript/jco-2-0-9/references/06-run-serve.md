# Run and Serve Commands

## run

Execute a WASI Command component directly from the CLI.

```bash
jco run my-command.wasm -- arg1 arg2
```

### How It Works

1. Transpiles the component to JS in a temporary directory
2. Symlinks `@bytecodealliance/preview2-shim` into the temp dir's node_modules
3. Creates a runner script that imports and calls `mod.run.run()`
4. Spawns a Node.js process to execute the runner
5. Cleans up the temp directory on exit

### Options

| Option | Description |
|---|---|
| `--jco-dir <dir>` | Persist transpiled output instead of using temp dir |
| `--jco-trace` | Enable call tracing on the transpiled component |
| `--jco-import <module>` | Import a custom module before execution |
| `--jco-map <mappings...>` | Custom import mappings (`specifier=output`) |
| `--jco-import-bindings [mode]` | `js`, `optimized`, `hybrid`, `direct-optimized` |

### Persisting Output

```bash
jco run my-command.wasm --jco-dir ./run-output -- arg1
```

This saves the transpiled JS, making it available for debugging or inspection.

### Custom Import Module

```bash
jco run my-command.wasm --jco-import ./setup.js
```

The setup module runs before the component executes, allowing environment preparation:

```js
// setup.js
globalThis.MY_CONFIG = { apiUrl: "https://api.example.com" };
```

### Argument Forwarding

All arguments after the component path are forwarded to the component's `run` function as CLI arguments, accessible via `wasi:cli/environment#get-args`.

```bash
jco run my-command.wasm -- --verbose --output result.json
```

### Requirements

- `@bytecodealliance/preview2-shim` must be installed (resolved from the current project)
- Node.js with ES module support
- The component must export `wasi:cli/run#run`

## serve

Serve a WASI HTTP component as a web server.

```bash
jco serve my-server.wasm
```

### How It Works

1. Transpiles the component to JS in a temporary directory
2. Creates a runner that instantiates an `HTTPServer` from `@bytecodealliance/preview2-shim/http`
3. The server listens on the specified port (or auto-selects from 8000)
4. Requests are forwarded to the component's `wasi:http/incoming-handler#handle`

### Options

| Option | Description |
|---|---|
| `--port <number>` | Port number (default: 8000, auto-increment on conflict) |
| `--host <host>` | Bind host (default: `localhost`) |
| `--jco-dir <dir>` | Persist transpiled output |
| `--jco-trace` | Enable call tracing |
| `--jco-import <module>` | Custom pre-execution module |
| `--jco-import-bindings [mode]` | Import bindings mode |
| `--jco-map <mappings...>` | Custom import mappings |

### Port Auto-Increment

Without `--port`, the server tries 8000, then increments until it finds an available port:

```bash
jco serve my-server.wasm
# Server listening @ localhost:8001...  (if 8000 is in use)
```

### Requirements

- `@bytecodealliance/preview2-shim` must be installed
- Node.js with ES module support
- The component must export `wasi:http/incoming-handler#handle`

## Environment Variables

### JCO_RUN_PATH

Override the Node.js binary used to run components:

```bash
JCO_RUN_PATH=/usr/bin/node jco run my-command.wasm
```

### JCO_RUN_ARGS

Pass additional arguments to the Node.js process:

```bash
JCO_RUN_ARGS="--max-old-space-size=4096" jco run my-command.wasm
```

## Custom WASI Implementations

Use `--jco-map` to redirect WASI imports to custom implementations:

```bash
jco run my-command.wasm \
  --jco-map "wasi:cli/environment=./my-env.js" \
  --jco-map "wasi:filesystem/types=./my-fs.js"
```

## Debugging

### Persist Transpiled Output

```bash
jco run my-command.wasm --jco-dir ./debug-run/
```

Then inspect the generated files:

```
./debug-run/
├── my-command.js      # Transpiled component
├── my-command.wasm    # Core Wasm binary
├── _run.js            # Runner script
└── node_modules/
    └── @bytecodealliance/
        └── preview2-shim  # Symlink to installed shim
```

### Tracing

```bash
jco run my-command.wasm --jco-trace
```

Emits tracing calls on every function entry/exit, visible in the Node.js inspector.

## Programmatic Execution

For programmatic component execution, transpile manually and import:

```js
import { transpile, writeFiles } from "@bytecodealliance/jco";

// Transpile
const { files } = await transpile("my-command.wasm", {
  outDir: "./dist",
  wasiShim: true,
});

// Import and run
const mod = await import("./dist/my-command.js");
mod.run.run();
```

Or for HTTP servers:

```js
import { HTTPServer } from "@bytecodealliance/preview2-shim/http";

const mod = await import("./dist/my-server.js");
const server = new HTTPServer(mod.incomingHandler);
server.listen(3000, "localhost");
```
