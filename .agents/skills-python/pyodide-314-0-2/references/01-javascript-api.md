# JavaScript API Reference

## loadPyodide

```js
import { loadPyodide } from "pyodide.mjs";
// or: <script src="pyodide.js"> (places loadPyodide on globalThis)

const pyodide = await loadPyodide(options);
```

### Options (PyodideConfig)

| Option | Type | Default | Description |
|---|---|---|---|
| `indexURL` | string | auto-detected | Base URL for runtime and packages |
| `packageCacheDir` | string | indexURL | Package cache directory (Node only) |
| `lockFileURL` | string | `${indexURL}/pyodide-lock.json` | Lock file URL |
| `lockFileContents` | Lockfile \| string | — | Inline lock file (JSON string or object) |
| `packageBaseUrl` | string | derived | Base URL for relative package paths |
| `stdLibURL` | string | `${indexURL}/python_stdlib.zip` | Standard library URL |
| `stdin` | `() => string \| null` | `prompt()` | Stdin callback (use `setStdin` for more control) |
| `stdout` | `(msg) => void` | — | Stdout callback (use `setStdout` for more control) |
| `stderr` | `(msg) => void` | — | Stderr callback (use `setStderr` for more control) |
| `jsglobals` | object | `globalThis` | Object used as the `js` module |
| `args` | string[] | `[]` | Python command-line arguments |
| `env` | `{ [key: string]: string }` | `{}` | Environment variables. `HOME` defaults to `/home/pyodide` |
| `packages` | string[] | `[]` | Packages to pre-load during initialization |
| `enableRunUntilComplete` | boolean | `true` | Enable `loop.run_until_complete()` via stack switching |
| `checkAPIVersion` | boolean | `true` | Error on version mismatch between core and JS |
| `fsInit` | `(FS, info) => Promise<void>` | — | Hook to modify filesystem before interpreter starts |

### Deprecated options

- `fullStdLib` — no effect
- `pyproxyToStringRepr` — old `toString()` behavior
- `convertNullToNone` — old null→None conversion
- `toJsLiteralMap` — old dict→LiteralMap conversion

## pyodide.runPython

```js
pyodide.runPython(code, options);
```

Execute Python code synchronously. If the last statement is an expression (no trailing semicolon), its value is returned as a JavaScript value.

**Options:**

| Option | Type | Default | Description |
|---|---|---|---|
| `globals` | PyProxy | `pyodide.globals` | Python dict for globals namespace |
| `locals` | PyProxy | same as globals | Python dict for locals namespace |
| `filename` | string | `"<exec>"` | File name for tracebacks |

```js
const result = pyodide.runPython("1 + 2"); // 3

const ns = pyodide.toPy({ x: 3 });
const result = pyodide.runPython("x + 1", { globals: ns }); // 4
ns.destroy();
```

## pyodide.runPythonAsync

```js
await pyodide.runPythonAsync(code, options);
```

Execute Python code with top-level `await` support. Same options as `runPython`.

```js
const result = await pyodide.runPythonAsync(`
  from pyodide.http import pyfetch
  resp = await pyfetch("https://httpbin.org/get")
  await resp.json()
`);
```

## pyodide.loadPackage

```js
await pyodide.loadPackage(packageOrPackages, options);
```

Load one or more packages from the Pyodide distribution. Returns Promise resolving when all packages are loaded.

```js
await pyodide.loadPackage("numpy");
await pyodide.loadPackage(["numpy", "pandas"]);

// Custom URL (no dependency resolution)
await pyodide.loadPackage("https://example.com/mypackage-1.0-cp314-cp314-emscripten_3_1_59_wasm32.whl");
```

**Options:**

| Option | Type | Default | Description |
|---|---|---|---|
| `messageCallback` | `(msg) => void` | — | Progress messages |
| `errorCallback` | `(msg) => void` | — | Error/warning messages |
| `checkIntegrity` | boolean | `true` | Verify package integrity |

## pyodide.loadPackagesFromImports

```js
await pyodide.loadPackagesFromImports(code, options);
```

Inspect Python code for import statements and auto-load required packages. Only loads bundled packages (not PyPI). Used by the REPL.

```js
await pyodide.loadPackagesFromImports(`
  import numpy as np
  x = np.array([1, 2, 3])
`);
```

## pyodide.loadedPackages

```js
pyodide.loadedPackages; // Map<string, string>
```

Map of loaded package names to their version strings.

## pyodide.pyimport

```js
const module = pyodide.pyimport("module_name");
```

Import a Python module and return it. For dotted names, imports the final component:

```js
const sys = pyodide.pyimport("sys");
const comb = pyodide.pyimport("math.comb"); // from math import comb
comb(4, 2); // 6
```

## pyodide.globals

Access the Python `__main__` global namespace.

```js
// Get variable
const x = pyodide.globals.get("x");

// Set variable
pyodide.globals.set("x", 42);

// Delete variable
pyodide.globals.delete("x");

// Check existence
pyodide.globals.has("x");

// Iterate
for (const [key, value] of pyodide.globals) {
  console.log(key, value);
}
```

## pyodide.toPy

```js
pyodide.toPy(obj, options);
```

Convert a JavaScript object to Python. Immutables pass through unchanged.

```js
const py_dict = pyodide.toPy({ key: "value", num: 42 });
pyodide.runPython("print(key)"); // "value"
py_dict.destroy();
```

**Options:**

| Option | Type | Description |
|---|---|---|
| `depth` | number | Conversion depth limit (default: -1 = unlimited) |
| `defaultConverter` | function | Custom converter for unhandled types |

## pyodide.FS

Re-export of the [Emscripten File System API](https://emscripten.org/docs/api_reference/Filesystem-API.html).

```js
// Read file
const data = pyodide.FS.readFile("/path", { encoding: "utf8" });

// Write file
pyodide.FS.writeFile("/path", data, { encoding: "utf8" });

// Create directory tree
pyodide.FS.mkdirTree("/a/b/c");

// List directory
const entries = pyodide.FS.readdir("/path");

// Stat
const stat = pyodide.FS.stat("/path");

// Available filesystem types
pyodide.FS.filesystems.MEMFS;
pyodide.FS.filesystems.IDBFS;
pyodide.FS.filesystems.NODEFS; // Node only
pyodide.FS.filesystems.PROXYFS;
pyodide.FS.filesystems.WORKERFS;

// Mount filesystem
pyodide.FS.mkdirTree("/mnt");
pyodide.FS.mount(pyodide.FS.filesystems.IDBFS, {}, "/mnt");
```

## pyodide.PATH

Re-export of the [Emscripten Path API](https://github.com/emscripten-core/emscripten/blob/main/src/library_path.js).

Provides `dirname`, `normalize`, `splitPath`, `join`, etc.

## pyodide.unpackArchive

```js
pyodide.unpackArchive(buffer, format, options);
```

Unpack an archive into the virtual filesystem.

```js
const response = await fetch("data.zip");
const buffer = await response.arrayBuffer();
pyodide.unpackArchive(buffer, "zip");

// Options
pyodide.unpackArchive(buffer, "gztar", { extractDir: "/data" });
```

**Formats:** `zip`, `tar`, `gztar`, `bztar`, `wheel` (and synonyms like `.tar.gz`, `.tgz`).

## pyodide.mountNativeFS

```js
const { syncfs } = await pyodide.mountNativeFS(path, fileSystemHandle);
```

Mount a browser `FileSystemDirectoryHandle` (Chrome only). Returns object with `syncfs()` method to persist changes.

```js
const dirHandle = await showDirectoryPicker();
const permission = await dirHandle.requestPermission({ mode: "readwrite" });
if (permission !== "granted") throw new Error("Permission denied");

const { syncfs } = await pyodide.mountNativeFS("/mnt", dirHandle);
// ... do file operations ...
await syncfs(); // persist to native filesystem
```

## pyodide.mountNodeFS

```js
pyodide.mountNodeFS(emscriptenPath, hostPath);
```

Mount a host directory into Pyodide (Node.js only). Changes are reflected immediately in both directions.

```js
pyodide.mountNodeFS("/src", "/path/to/project/src");
pyodide.runPython("import src.mymodule");
```

## pyodide.useNodeSockFS

```js
await pyodide.useNodeSockFS();
```

Enable Node.js native socket support (experimental, Node.js only). Must be called before importing socket-using modules. Requires `--experimental-wasm-stack-switching` on Node ≤ 24.

## pyodide.setStdin / setStdout / setStderr

### setStdin

```js
pyodide.setStdin(options);
```

| Option | Type | Description |
|---|---|---|
| `error` | boolean | If true, all reads raise I/O error |
| `stdin` | `() => string \| ArrayBuffer \| Uint8Array \| number \| undefined` | Callback returning input data |
| `read` | `(Uint8Array) => number` | Low-level read handler, returns bytes read |
| `isatty` | boolean | Whether `sys.stdin.isatty()` returns true |

```js
// Replay input
class InputHandler {
  constructor(lines) { this.lines = lines; this.idx = 0; }
  stdin() { return this.lines[this.idx++]; }
}
pyodide.setStdin(new InputHandler(["hello", "world"]));
```

### setStdout / setStderr

```js
pyodide.setStdout(options);
pyodide.setStderr(options);
```

| Option | Type | Description |
|---|---|---|
| `batched` | `(string) => void` | Receives complete lines or flushed partial lines |
| `raw` | `(charCode) => void` | Receives one byte at a time |
| `write` | `(Uint8Array) => number` | Low-level write handler, returns bytes written |
| `isatty` | boolean | Whether `sys.stdout.isatty()` returns true |

```js
pyodide.setStdout({ batched: (line) => console.log("Py:", line) });
```

## pyodide.setInterruptBuffer

```js
pyodide.setInterruptBuffer(sharedArrayBuffer);
```

Set a `SharedArrayBuffer` for signaling interrupts from another thread. Write signal number (e.g., `2` for SIGINT) into the buffer. Only works in web workers.

```js
const buffer = new Uint8Array(new SharedArrayBuffer(1));
pyodide.setInterruptBuffer(buffer);
// From another thread:
buffer[0] = 2; // triggers KeyboardInterrupt
```

## pyodide.checkInterrupt

```js
pyodide.checkInterrupt();
```

Check for pending interrupt and raise `KeyboardInterrupt` if signaled. Call periodically in long-running JS code called from Python.

## pyodide.registerJsModule / unregisterJsModule

```js
pyodide.registerJsModule("module_name", object);
pyodide.unregisterJsModule("module_name");
```

Register a JavaScript object as an importable Python module. Sub-objects become submodules.

```js
pyodide.registerJsModule("my_api", {
  greet: (name) => `Hello, ${name}!`,
  utils: { add: (a, b) => a + b }
});
pyodide.runPython(`
  from my_api import greet
  from my_api.utils import add
  print(greet("World"))
  print(add(1, 2))
`);
```

## pyodide.ERRNO_CODES

```js
pyodide.ERRNO_CODES.EIO;   // 5
pyodide.ERRNO_CODES.ENOENT; // 44
```

Map of POSIX error names to numeric codes.

## pyodide.canvas

```js
pyodide.canvas.setCanvas2D(canvasElement);
pyodide.canvas.setCanvasWebGL(canvasElement, attributes);
```

Set the canvas for SDL-based packages (pygame, etc.). Canvas must have `id="canvas"`.

## pyodide.pyodide_py

```js
pyodide.pyodide_py; // PyProxy of the pyodide Python package
```

Direct access to the `pyodide` Python package from JavaScript.

## pyodide.lockfile / lockfileBaseUrl

```js
pyodide.lockfile;         // Lockfile object
pyodide.lockfileBaseUrl;  // Base URL for relative paths
```

## pyodide.registerComlink

```js
pyodide.registerComlink(Comlink);
```

Tell Pyodide about Comlink to enable importing Comlink proxies into Python.

## pyodide.setDebug

```js
const old = pyodide.setDebug(true);
// ... debug mode active ...
pyodide.setDebug(old);
```

Toggle debug mode for improved error messages at performance cost.
