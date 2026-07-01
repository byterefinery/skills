---
name: pyodide-314-0-2
description: >
  Pyodide 314.0.2 — Python in the browser via WebAssembly (WASM/Emscripten).
  Use when running Python code in a browser, Node.js, Deno, or Bun environment.
  Covers: loadPyodide, runPython/runPythonAsync, package management (micropip,
  loadPackage), file system (MEMFS, IDBFS, NODEFS, NativeFS), type conversions
  between JS and Python (JsProxy, PyProxy, toJs, toPy), HTTP (pyfetch, pyxhr),
  console (Console, PyodideConsole), webloop (WebLoop, PyodideFuture),
  streams (setStdin/setStdout/setStderr), web workers, sockets (Node only),
  SDL/canvas, keyboard interrupts, and wasm constraints.
metadata:
  tags:
    - python
    - webassembly
    - browser
    - runtime
---

# pyodide 314.0.2

## Overview

Pyodide is a Python distribution for the browser and Node.js based on CPython
compiled to WebAssembly via Emscripten. It runs Python 3.14 in a WASM sandbox
with full access to JavaScript APIs and the browser DOM. This skill documents
the complete Pyodide 314.0.2 API.

Key capabilities:

- Run Python code from JavaScript via `runPython` / `runPythonAsync`
- Call JavaScript from Python via the `js` module and `pyodide_js`
- Install packages via `micropip` (from PyPI) or `loadPackage` (bundled)
- Virtual file system (MEMFS by default) with mountable alternatives
- Bidirectional type conversion between Python and JavaScript objects
- Async event loop integrated with the browser (`WebLoop`)
- HTTP clients: `pyfetch` (async, Fetch API) and `pyxhr` (sync, XMLHttpRequest)

## Usage

### Loading Pyodide

```html
<script type="module">
  import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v0.27.1/full/pyodide.mjs";
  // or: import { loadPyodide } from "pyodide.mjs"; (npm package)
  const pyodide = await loadPyodide();
</script>
```

Legacy (non-module):

```html
<script src="https://cdn.jsdelivr.net/pyodide/v0.27.1/full/pyodide.js"></script>
<script>
  const pyodide = await loadPyodide();
</script>
```

### Running Python

```js
// Sync — returns last expression value as JS
const result = pyodide.runPython("1 + 2");

// Async — supports top-level await
const result = await pyodide.runPythonAsync(`
  from pyodide.http import pyfetch
  resp = await pyfetch("https://example.com/data.json")
  await resp.json()
`);

// Custom namespace
const ns = pyodide.toPy({ x: 10 });
pyodide.runPython("y = x * 2", { globals: ns });
ns.get("y"); // 20
```

### Loading Packages

```js
// Bundled packages (from Pyodide distribution)
await pyodide.loadPackage("numpy");

// Multiple packages
await pyodide.loadPackage(["numpy", "pandas"]);

// Auto-load from imports (bundled only)
await pyodide.loadPackagesFromImports("import numpy as np\nnp.array([1,2,3])");

// From Python (micropip — supports PyPI)
await pyodide.runPythonAsync(`
  import micropip
  await micropip.install("requests")
`);
```

### File System

```js
// Write from JS
pyodide.FS.writeFile("/hello.txt", "hello world", { encoding: "utf8" });

// Read from JS
const data = pyodide.FS.readFile("/hello.txt", { encoding: "utf8" });

// From Python
pyodide.runPython(`
  from pathlib import Path
  Path("/data.txt").write_text("from python")
`);

// Mount Node host filesystem (Node.js only)
pyodide.mountNodeFS("/mnt", "/path/on/host");

// Mount browser NativeFS (Chrome only)
const dirHandle = await showDirectoryPicker();
const { syncfs } = await pyodide.mountNativeFS("/mnt", dirHandle);
await syncfs(); // persist changes
```

### Type Conversion

```js
// Python → JS: runPython returns auto-converted values
const list = pyodide.runPython("[1, 2, 3]"); // JS array [1, 2, 3]

// Proxy (mutable objects stay as PyProxy)
const proxy = pyodide.globals.get("my_dict");
const jsObj = proxy.toJs(); // deep convert
proxy.destroy(); // prevent memory leak

// JS → Python
pyodide.globals.set("js_data", { key: "value" });
pyodide.runPython("from js_data import key"); // won't work, use:
pyodide.runPython(`
  import js
  data = js.js_data
`);
```

## Gotchas

- **No threading or multiprocessing** — WASM has no pthreads. `threading.Thread.start()` raises `RuntimeError`. Use `asyncio` with `await` instead.
- **No raw sockets in browsers** — sockets only work in Node.js via `pyodide.useNodeSockFS()`.
- **MEMFS is in-memory** — data is lost on page reload. Use IDBFS (with `syncfs`) or NativeFS for persistence.
- **PyProxy memory leaks** — every Python object returned to JS creates a `PyProxy`. Call `.destroy()` when done, or use `using` keyword: `using proxy = pyodide.globals.get("x");`.
- **`toJs()` creates nested proxies** — use `{ pyproxies: [] }` option to collect and destroy them, or `{ create_pyproxies: false }` to fail instead of proxying.
- **`None` → `undefined`, not `null`** — use `pyodide.ffi.jsnull` for JS `null`.
- **JS `null` → `jsnull`, not `None`** — JavaScript `null` becomes `pyodide.ffi.jsnull` in Python.
- **Python keywords on JS objects** — `Array.from` becomes `Array.from_`, `obj.global` becomes `obj.global_`. Use `getattr(Array, "from")` as alternative.
- **`create_proxy` for event handlers** — passing a Python function directly to `addEventListener` leaks. Use `create_proxy(fn)` and call `.destroy()` on removal.
- **`create_once_callable` for one-shot callbacks** — use for `setTimeout` callbacks that fire once.
- **`importlib.invalidate_caches()`** needed after writing `.py` files to MEMFS before importing.
- **`pyfetch` is async** — use `await pyfetch(...)`. For sync, use `pyxhr.get()` (XMLHttpRequest, browser only).
- **Infinite loops block the browser** — use `await asyncio.sleep(0)` to yield control in game loops and animations.
- **CORS matters** — fetching from other origins requires proper CORS headers.
- **`runPython` vs `runPythonAsync`** — `runPython` cannot handle top-level `await`. Use `runPythonAsync` for async code.
- **`eval_code` return behavior** — if last statement is an expression (no trailing semicolon), its value is returned. Statements return `None`.
- **`micropip` needs loading first** — `await pyodide.loadPackage("micropip")` before using from JS, or `import micropip` from Python (auto-loads).
- **`sys.platform == "emscripten"`** to detect Pyodide at runtime.
- **`"pyodide" in sys.modules`** to detect Pyodide specifically.
- **`"PYODIDE" in os.environ`** to detect at build time.
- **`requests` / `urllib3` streaming** only works in web workers on cross-origin isolated pages.
- **`ssl` module is a stub** — OpenSSL-dependent methods raise `NotImplementedError`.
- **`hashlib`** — OpenSSL-dependent algorithms are unavailable.
- **`zoneinfo`** requires `tzdata` package.
- **`pydoc`** requires `pydoc_data` package for help messages.

## References

- [01-javascript-api](references/01-javascript-api.md) — loadPyodide, runPython, runPythonAsync, loadPackage, pyimport, globals, FS, PATH, unpackArchive, mountNativeFS, mountNodeFS, setStdin/Stdout/Stderr, setInterruptBuffer, checkInterrupt, registerJsModule, toPy, pyimport
- [02-python-api](references/02-python-api.md) — pyodide.code, pyodide.ffi, pyodide.http, pyodide.console, pyodide.webloop, js module, pyodide_js module
- [03-type-conversions](references/03-type-conversions.md) — Implicit conversions, proxying (JsProxy, PyProxy), explicit conversion (toJs, toPy), buffers, memory management
- [04-file-system](references/04-file-system.md) — MEMFS, IDBFS, NODEFS, NativeFS, PROXYFS, WORKERFS, FS API, unpackArchive, mounting, persistence
- [05-packages](references/05-packages.md) — micropip, loadPackage, loadPackagesFromImports, package index, custom URLs, dependency resolution
- [06-advanced](references/06-advanced.md) — Web workers, streams, keyboard interrupts, sockets, SDL/canvas, wasm constraints, FAQ
