---
name: pyodide-314-0-8
description: >
  Pyodide 314.0.8 — Python 3.14 in the browser and Node.js via WebAssembly
  (Emscripten). Use when running Python code in a web page, web worker, service
  worker, or Node.js environment. Covers loadPyodide and its config options,
  runPython/runPythonAsync, package management (micropip, loadPackage,
  loadPackagesFromImports), the virtual file system (MEMFS, IDBFS, NODEFS,
  NativeFS), JS-Python type conversions (JsProxy, PyProxy, toJs, to_py, jsnull),
  HTTP (pyfetch, pyxhr), console and webloop, streams (setStdin/setStdout/
  setStderr), web workers, service workers, sockets (Node-only
  useNodeSockFS), SDL/canvas, keyboard interrupts, the Pyodide Python CLI, and
  WebAssembly constraints.
metadata:
  tags:
    - python
    - webassembly
    - browser
    - runtime
---

# pyodide 314.0.8

## Overview

Pyodide is a Python distribution for the browser and Node.js based on
WebAssembly. It is a port of CPython (3.14) to WebAssembly via Emscripten. The
version number follows the Python version (PEP 440): 314.0.x means Python
3.14-based.

Key capabilities:

- Run Python from JavaScript via `runPython` / `runPythonAsync`; call JavaScript from Python via the `js` and `pyodide_js` modules
- Install packages with `micropip` (pure Python wheels from PyPI, plus Pyodide-built binary wheels) or `pyodide.loadPackage` (bundled packages)
- Virtual file system (in-memory MEMFS by default) with mountable alternatives (IDBFS, NODEFS, PROXYFS, WORKERFS, experimental NativeFS)
- Bidirectional JS-Python foreign function interface with full error handling and async/await support
- Async event loop integrated with the host environment (`WebLoop`)
- HTTP clients: `pyfetch` (async, wraps `fetch`) and `pyxhr` (synchronous, XMLHttpRequest)
- A `python` CLI entrypoint (drop-in replacement for the native CLI, mainly for testing)

## Usage

### Loading Pyodide (browser)

```html
<script type="module">
  // CDN pattern (JsDelivr); v0.27-style numbers are old — use the real version
  import { loadPyodide, version } from "https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.mjs";
  const pyodide = await loadPyodide();
  console.log(pyodide.runPython("1 + 2")); // 3
</script>
```

`pyodide.mjs` exports `loadPyodide` and `version`. The legacy `pyodide.js` puts
`loadPyodide` on `globalThis` but exposes no other top-level exports. Full
`loadPyodide` config options are in [01-javascript-api](references/01-javascript-api.md).

### Loading Pyodide (Node.js)

```bash
npm install pyodide
```

```js
// hello_python.mjs
import { loadPyodide } from "pyodide";
const pyodide = await loadPyodide();
console.log("Python says that 1+1 =", await pyodide.runPythonAsync("1+1"));
```

Node.js >= 18 is supported (>= 0.25.0). The Python CLI requires Node.js >= 20.

### Running Python

```js
// Sync — returns the last expression's value translated to JavaScript
const result = pyodide.runPython("1 + 2");

// Async — supports top-level await
const data = await pyodide.runPythonAsync(`
  from pyodide.http import pyfetch
  resp = await pyfetch("https://example.com/data.json")
  await resp.json()
`);

// Custom namespace (must be a Python dict, e.g. made with pyodide.toPy)
const ns = pyodide.toPy({ x: 3 });
console.log(pyodide.runPython("x + 1", { globals: ns })); // 4
```

`runPython` options: `globals`, `locals` (Python dicts), `filename`, `dedent`
(default true). If the last statement is an expression (no trailing
semicolon), its value is returned; statements return `None`.

### Python ↔ JavaScript

```js
// JS → Python globals
pyodide.globals.set("square", (x) => x * x);
pyodide.runPython("square(3)"); // 9

// Python globals → JS
const x = pyodide.globals.get("x"); // PyProxy — destroy() when done
x.toJs();
x.destroy();
```

```python
# Python → JS global scope
import js
div = js.document.createElement("div")
div.innerHTML = "<h1>Created from Python</h1>"
js.document.body.prepend(div)
```

### Packages

```js
// Bundled Pyodide packages (JS, lower overhead)
await pyodide.loadPackage("numpy");
await pyodide.loadPackage(["cycler", "pytz"]);

// Auto-load bundled packages that a code chunk imports (REPL use)
await pyodide.loadPackagesFromImports("import numpy as np\nnp.array([1,2,3])");
```

```python
# PyPI packages (pure Python wheels) or Pyodide binary wheels — async
import micropip
await micropip.install("snowballstemmer")
```

Prefer `micropip.install` for everything except loading micropip itself or when
you need to minimize size and do not need PyPI dependency resolution.

### File system

```js
// pyodide.FS re-exports the Emscripten File System API
pyodide.FS.writeFile("/hello.txt", "hello world!", { encoding: "utf8" });
const file = pyodide.FS.readFile("/hello.txt", { encoding: "utf8" });

// Mount the Node host filesystem (Node.js)
pyodide.mountNodeFS("my_package", "/path/to/my_package");
```

The default MEMFS is in-memory and lost on page reload. See
[04-file-system](references/04-file-system.md) for IDBFS/NativeFS persistence.

### Python CLI

```bash
# Install via uv (wasm32 Python build)
uv python install cpython-3.14.2-emscripten-wasm32-musl
uv venv .venv-pyodide -p cpython-3.14.2-emscripten-wasm32-musl
# Install Pyodide packages for the venv:
uv pip install --no-build --extra-index-url https://index.pyodide.org/314.0.0/ --index-strategy unsafe-best-match <package>
```

## Gotchas

- **No threading, multiprocessing, or subprocess** — fork/pthreads do not work in Pyodide; starting a thread raises `RuntimeError`. `multiprocessing`, `threading`, `sockets` import but are non-functional. Work around with `asyncio` and force `n_threads = 1` in packages that probe for threads.
- **Sockets: Node.js only (experimental)** — in browsers, socket code raises errors. In Node, call `await pyodide.useNodeSockFS()` before importing any module that uses sockets. On Node <= 24 also run with `--experimental-wasm-stack-switching`; Node >= 25 has Promise Integration on by default.
- **`pty` and `tty` cannot be imported** — they depend on `termios`, which is removed. Also removed: `curses`, `dbm`, `ensurepip`, `fcntl`, `grp`, `idlelib`, `lib2to3`, `msvcrt`, `pwd`, `resource`, `syslog`, `termios`, `tkinter`, `turtle.py`, `turtledemo`, `venv`, `winreg`, `winsound`.
- **Stdlib stubs / limits** — `ssl` is a non-OpenSSL stub (methods raise `NotImplementedError`); `hashlib` lacks OpenSSL-dependent algorithms; `zoneinfo` needs the `tzdata` package; `pydoc` builtin help needs the `pydoc_data` package; `decimal` only has the C implementation; `webbrowser` is a browser-API stub.
- **MEMFS is in-memory** — data is lost on reload. For persistence use IDBFS (call `pyodide.FS.syncfs()` to persist — IDBFS is asynchronous) or NativeFS (`await nativefs.syncfs()` after `mountNativeFS`).
- **PyProxy memory leaks** — every Python→JS translation may create a `PyProxy`. Call `.destroy()` when done, use the `using` keyword (`using proxy = pyodide.globals.get("x");`), or return `to_js(value)` from Python so JS callers don't need cleanup.
- **`toJs()` creates nested proxies** — pass `{ pyproxies: [] }` to collect them for later destruction, or `{ create_pyproxies: false }` to raise `ConversionError` instead of proxying.
- **`None` → `undefined`, not `null`** — use `pyodide.ffi.jsnull` to represent JS `null`. JS `null` → `pyodide.ffi.jsnull` in Python (not `None`); JS `undefined` → `None`.
- **Python keywords on JS objects** — `Array.from` → `Array.from_`, `people.global` → `people.global_` (a real trailing underscore needs `o.from__`). Alternatively use `getattr(obj, "from")` / `setattr` / `getattr(js, "lambda")`.
- **Event handlers need `create_proxy`** — passing a Python function directly to `addEventListener` breaks on each call. Use `pyodide.ffi.create_proxy(fn)` (recurring, destroy on removal) or `create_once_callable(fn)` (one-shot, e.g. `setTimeout`).
- **Calling JS functions with keyword args** — Python kwargs are combined into a single JS object passed as the *last* argument. So `js.fetch(url, {method: ...})` as a plain dict silently loses options; use `to_js({...}, dict_converter=Object.fromEntries)` or pass kwargs so they land as the final object.
- **Importing files you just wrote** — after writing `mymodule.py` to the FS, call `importlib.invalidate_caches()` before importing it.
- **Infinite loops block the browser** — game/animation loops must yield: `await asyncio.sleep(1 / fps)` each iteration.
- **`runPython` cannot run top-level `await`** — use `runPythonAsync` for async code.
- **Web workers must be module type** — `pyodide.asm.mjs` is an ES module; classic workers with `importScripts()` are not supported.
- **Service workers forbid dynamic `import()`** — statically import `pyodide.asm.mjs` and pass its default export to `loadPyodide` as `createPyodideModule`.
- **`loadPackagesFromImports` only loads distribution packages** — it never downloads from PyPI; use `micropip` for PyPI.
- **`micropip` needs a pure Python wheel on PyPI** — packages without a `*py3-none-any.whl` must either be a Pyodide-built package or installed from an explicit wheel URL (`micropip` decides by the `.whl` suffix). `unpackArchive` on a wheel does no dependency resolution.
- **Detecting Pyodide** — runtime: `sys.platform == "emscripten"` (any Emscripten build) or `"pyodide" in sys.modules` (Pyodide specifically). Build time (setup.py): `"PYODIDE" in os.environ` (the `pyodide` module check does not work at build time).
- **CORS and network** — all network goes through the browser/Node fetch stack; you control no certificates/timeouts/proxies. Remote wheel servers must set CORS headers. `requests`/`urllib3` streaming downloads work only in a web worker on a cross-origin isolated page; otherwise requests are non-streaming.
- **Pickle from a server** — pickles are portable between amd64 and wasm32 when Python versions match exactly; unpickling client-supplied data is like `eval`, use JSON instead on public servers.
- **Browsers tested against** — Firefox 112, Chrome 112, Safari 16.4 (use newer); use the latest browsers whenever possible.
- **Version mismatch check** — `checkAPIVersion` (default true) throws if Pyodide core and the JS package versions differ; if you pin files from different versions, keep `indexURL` in sync.

## References

- [01-javascript-api](references/01-javascript-api.md) — loadPyodide config options, the full pyodide object API (runPython, pyimport, toPy, FS, unpackArchive, mounts, interrupts, debug), pyodide.ffi namespace
- [02-python-api](references/02-python-api.md) — pyodide.code, pyodide.ffi, pyodide.http (pyfetch, pyxhr), pyodide.console, pyodide.webloop, js / pyodide_js modules, the Pyodide Python CLI
- [03-type-conversions](references/03-type-conversions.md) — implicit conversion tables, JsProxy/PyProxy operations, explicit conversion (toJs, to_py), buffers, error translation
- [04-file-system](references/04-file-system.md) — MEMFS, IDBFS, NODEFS, PROXYFS, WORKERFS, NativeFS, unpackArchive, persistence and dev workflows
- [05-packages](references/05-packages.md) — micropip vs loadPackage vs loadPackagesFromImports, custom URLs, lockfiles, dependency resolution, CORS
- [06-advanced](references/06-advanced.md) — web workers, service workers, streams, keyboard interrupts, sockets, SDL/canvas, stdlib compatibility, deployment, bundlers, FAQ patterns
