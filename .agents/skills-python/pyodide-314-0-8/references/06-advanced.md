# Advanced topics

## Contents

- Web workers
- Service workers
- Standard streams
- Interrupting execution (keyboard interrupts)
- Sockets (Node.js, experimental)
- SDL-based packages (canvas, games)
- Python standard library compatibility
- Downloading and deploying
- Working with bundlers
- Loading custom Python code
- FAQ patterns

## Web workers

WebAssembly runs in the main thread by default and blocks the UI for
long-running computations. Run Pyodide in a **module-type web worker**
(required — `pyodide.asm.mjs` is an ES module; classic workers with
`importScripts()` are not supported). Workers cannot manipulate the DOM;
communicate via `postMessage`.

Pattern (condensed from the docs' three-party example: consumer, worker API,
worker):

```js
// webworker.mjs — the worker
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.mjs";
let pyodideReadyPromise = loadPyodide();
self.onmessage = async (event) => {
  const pyodide = await pyodideReadyPromise;
  const { id, python, context } = event.data;
  await pyodide.loadPackagesFromImports(python);
  const dict = pyodide.globals.get("dict");
  const globals = dict(Object.entries(context));
  try {
    const result = await pyodide.runPythonAsync(python, { globals });
    self.postMessage({ result, id });
  } catch (error) {
    self.postMessage({ error: error.message, id });
  }
};
```

```js
// main thread — create a module worker
const pyodideWorker = new Worker("./webworker.mjs", { type: "module" });
```

Give each message a unique `id` and match responses by id (the docs'
`requestResponse` helper wraps this in a promise).

## Service workers

Service workers (network proxy / background / caching use cases) work with
Pyodide but:

- only on **https or localhost**,
- **forbid dynamic `import()`** — statically import `pyodide.asm.mjs` and pass
  its default export to `loadPyodide` as `createPyodideModule`:

```js
// sw.js
import createPyodideModule from "./pyodide.asm.mjs";
import { loadPyodide } from "./pyodide.mjs";
loadPyodide({ createPyodideModule }).then((_pyodide) => { /* ... */ });
```

The docs' example intercepts `fetch` events, transforms JSON with a Python
function, and responds with a new `Response`.

## Standard streams

`pyodide.setStdin` / `setStdout` / `setStderr` (or the equivalent
`loadPyodide` options, which only matter for startup output).

**stdin** modes:
- `{ error: true }` — any read raises an I/O error.
- no arguments — default (Node: read Node stdin; browser: `prompt()`).
- `{ stdin, isatty }` — `stdin()` returns one of: a full line string, an
  array buffer/Uint8Array of utf8, a number 0-255 (one byte), or
  `undefined`/`null` (EOF). `input()` strips trailing newlines;
  `sys.stdin.read()` shows them appended to lines missing a newline.
- `{ read(buf), isatty }` — read handler places data into `buf`, returns bytes
  read (Node file descriptor pattern).
- Throw `new pyodide.FS.ErrnoError(pyodide.ERRNO_CODES.EIO)` for I/O errors.
- `isatty` controls `sys.stdin.isatty()`.
- Handle interrupts by calling `pyodide.checkInterrupt()` periodically.

**stdout/stderr** modes:
- no arguments — default (Node: `process.stdout`; browser: batched
  `console.log`).
- batched handler `(line) => void` — complete line (newline removed) or a
  flushed partial line; no flag distinguishes the two.
- raw handler — one character code at a time.
- write handler `{ write(buf), isatty }` — Node file descriptor pattern.
- `isatty: true` cannot be combined with a batched handler.

Temporary redirection in Python works like native Python: overwrite
`sys.stdout`/`stderr`, or use `contextlib.redirect_stdout` /
`redirect_stderr` (and `pyodide.console.redirect_stdin` for stdin).

## Interrupting execution

WASM has no preemptive multitasking, so interrupts need a **web worker** plus
a **`SharedArrayBuffer`** (server must send the appropriate security headers).

- Create the SharedArrayBuffer on one thread, share it, and call
  `pyodide.setInterruptBuffer(buffer)` on the Pyodide thread.
- To interrupt, write `2` (SIGINT) into the buffer; Pyodide resets it to `0`
  after processing. Default behavior raises `KeyboardInterrupt`; register a
  custom handler with the `signal` module (`signal.SIGINT`).
- Clear the buffer (`buffer[0] = 0`) before running new code in case a
  previous run left it set.
- JavaScript called from Python can also cooperate: call
  `pyodide.checkInterrupt()` periodically, e.g. in `Atomics.wait(..., 50)`
  polling loops or stdin read handlers, to make blocking JS interruptible.

## Sockets (Node.js, experimental)

- Browsers: no low-level socket API — socket code raises errors.
- Node.js: `await pyodide.useNodeSockFS()` **before** importing any module
  that uses sockets. Requires JavaScript Promise Integration:
  - Node <= 24: run with `--experimental-wasm-stack-switching`.
  - Node >= 25: enabled by default.
- Then `import socket` works normally (connect, sendall, recv, ...), and
  socket-based drivers (e.g. `pymysql`) work too.

## SDL-based packages (canvas, games)

Experimental; relies on undocumented Emscripten/SDL behavior and requires
opting in with `pyodide._api._skip_unwind_fatal_error = true` (can cause
stack-unwinding issues).

1. Set the canvas before using SDL packages — the element must have
   `id="canvas"`:

   ```js
   const c = document.createElement("canvas");
   c.id = "canvas";
   pyodide.canvas.setCanvas2D(c);
   ```

2. Infinite game loops block the main thread and the canvas never updates.
   Use an async loop that yields:

   ```python
   import asyncio
   async def run_game():
       while True:
           do_something()
           draw_canvas()
           await asyncio.sleep(1 / fps)
   ```

## Python standard library compatibility

**Limited functionality:**

- `decimal` — only the C (`_decimal`) implementation; the pure-Python one is unavailable.
- `pydoc` — builtin help messages unavailable until you load `pydoc_data` (`loadPackage`/`micropip.install`).
- `webbrowser` — stubs based on browser APIs (`open`, `open_new`, `open_new_tab`).
- `zoneinfo` — needs the `tzdata` package.
- `hashlib` — OpenSSL-dependent algorithms unavailable.
- `ssl` — stub without OpenSSL; OpenSSL-dependent methods raise `NotImplementedError`.

**Synchronous HTTP**: `urllib3` and `requests` packages are included. In
browsers they work roughly like elsewhere, but streaming downloads work only
when Pyodide runs in a web worker **and** the page is cross-origin isolated —
otherwise requests are non-streaming. All calls go through the browser network
stack (CORS applies; no control over certificates/timeouts/proxies). In Node
they are untested (would need a sync XHR polyfill and a web worker).

**Removed modules**: `curses`, `dbm`, `ensurepip`, `fcntl`, `grp`, `idlelib`,
`lib2to3`, `msvcrt`, `pwd`, `resource`, `syslog`, `termios`, `tkinter`,
`turtle.py`, `turtledemo`, `venv`, `winreg`, `winsound`.

**Present but not functional**: `multiprocessing`, `threading`, `sockets`
(and anything built on them). `pty` and `tty` cannot be imported (depend on
removed `termios`).

Thread-probing pattern used by packages (force single-threaded when no
pthreads):

```python
def _can_start_thread() -> bool:
    if sys.platform == "emscripten":
        return sys._emscripten_info.pthreads
    return platform.machine() not in ("wasm32", "wasm64")

can_start_thread = _can_start_thread()
if not can_start_thread:
    n_threads = 1
```

## Downloading and deploying

- **CDN (JsDelivr)** — latest release channel (recommended, browser-cached)
  and dev channel `https://cdn.jsdelivr.net/pyodide/dev/full/` (per-commit,
  uncached, testing only). Build variants: `<version>/full/` (default) and
  `<version>/debug/` (unminified `pyodide.asm.mjs`).
- **GitHub releases** — `pyodide-<VERSION>.tar.bz2` (full distribution, 200+
  MB, all vendored packages) and `pyodide-core-<VERSION>.tar.bz2` (minimal
  files, intended for Node, same set as `npm install pyodide`).
- **Serving locally** — `python -m http.server` from the distribution folder
  (console at `http://localhost:8000/console.html`).
- **Remote** — any static host that sets the WASM MIME type and CORS headers
  (GitHub Pages etc.). See Emscripten deployment docs for size/load-time
  optimization.

`pyodide-core` contents: `pyodide.asm.mjs` (JS half of the runtime),
`pyodide.asm.wasm` (WASM half), `pyodide.js` (legacy loader, puts
`loadPyodide` on globalThis), `pyodide.mjs` (module loader exporting
`loadPyodide`), `python_stdlib.zip`, `package.json`, `pyodide-lock.json`
(required in all cases), `python` + `python_cli_entry.mjs` (CLI). The full
distribution additionally has `fonts/`, `ffi.d.ts`, `pyodide.d.ts`, `*.whl`,
`*.metadata` (PEP 658 package metadata), `*.zip` shared libraries, source
maps, vendored tests, and `console.html`.

## Working with bundlers

**Simplest: CDN** — `import { loadPyodide, version } from "pyodide"` and set
`indexURL` to `https://cdn.jsdelivr.net/pyodide/v${version}/full/`. Works with
most bundlers without extra config.

**Bundling the files** (offline/self-hosting):

- **Webpack** — use the Pyodide Webpack plugin.
- **Vite** — `npm install pyodide vite-plugin-static-copy`;
  `optimizeDeps.exclude: ["pyodide"]`; copy the pyodide dir into
  `assets` (exclude `*.md/html/d.ts/whl` and `node_modules`); then either
  `packageBaseUrl` to the CDN for packages, or copy specific `.whl` files
  (exact filenames, not globs) and a transformed `pyodide-lock.json` filtered
  to just those packages. Set `indexURL` to the bundled path if needed.
  Verify both `npx vite` and `npx vite build && npx vite preview`.

## Loading custom Python code

Best practice for larger code: make a wheel and `micropip.install` it (C
extensions must first be built for Pyodide via pyodide-build). Otherwise:

```js
// archive from JS
let buffer = await (await fetch("https://.../your_package.tar.gz")).arrayBuffer();
await pyodide.unpackArchive(buffer, "gztar"); // unpacks to the current dir
pyodide.pyimport("your_package");

// single script
pyodide.runPython(await (await fetch("https://.../code.py")).text());
```

```python
# archive from Python
from pyodide.http import pyfetch
response = await pyfetch("https://.../your_package.tar.gz")
await response.unpack_archive()
```

Unpacking a wheel with `unpackArchive` does not resolve dependencies — install
them separately or use micropip.

## FAQ patterns

- **Custom namespace** — `runPython(code, { globals })` where `globals` is a
  Python dict (make with `pyodide.globals.get("dict")()` or
  `pyodide.toPy({...})`); read back with `namespace.get("y")`.
- **Custom Python packages from JS** — `pyodide.registerJsModule("name", obj)`;
  then `import name` / `from name.submodule import x` in Python.
- **Server → client objects** — pickle works when Python versions match
  exactly (and package versions for pickled package objects); never unpickle
  client-supplied data on a public server (use JSON).
- **Python function as event handler** — `create_proxy` (see
  [03-type-conversions](03-type-conversions.md)).
- **`fetch` with optional arguments from Python** — kwargs become a single
  final JS object; build options with `to_js({...},
  dict_converter=Object.fromEntries)` or use keyword args so they land as the
  final argument.
- **Controlling stdin/stdout/stderr** — `loadPyodide` options,
  `pyodide.setStdin/Stdout/Stderr`, or `sys.*` / `contextlib.redirect_*`.
- **Why can't I import a file I just wrote?** — `importlib.invalidate_caches()`
  first.
- **Why don't IndexedDB changes persist?** — call `pyodide.FS.syncfs()`.
- **JS names that are Python keywords** — trailing-underscore mangling
  (`from_`) or `getattr`/`setattr`/`delattr` with the real name.
- **Detecting Pyodide** — `sys.platform == "emscripten"` (any Emscripten
  build), `"pyodide" in sys.modules` (Pyodide, runtime only),
  `"PYODIDE" in os.environ` (build time, e.g. setup.py).
