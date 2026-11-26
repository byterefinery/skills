# JavaScript API

## Contents

- Top-level exports
- `loadPyodide` config options (`PyodideConfig`)
- The `pyodide` object — attributes
- The `pyodide` object — methods
- `pyodide.ffi`
- `pyodide.canvas`

## Top-level exports

Importable via `import { name } from "pyodide.mjs"`. The `version` export is
the Pyodide version string (PEP 440, i.e. Python-based, e.g. `"314.0.8"`).

If you cannot use ES modules, `pyodide.js` places `loadPyodide` on
`globalThis`; the other top-level exports are not accessible from `pyodide.js`.

```js
import { loadPyodide, version as pyodideVersion } from "pyodide";
// or from CDN:
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.mjs";
```

## `loadPyodide` config options (`PyodideConfig`)

`loadPyodide(config?)` is the single async entrypoint; it returns the
`pyodide` API object.

| Option | Default | Meaning |
|---|---|---|
| `indexURL` | URL `pyodide.js`/`pyodide.mjs` was loaded from, file name removed | Where to load the main runtime and packages. Leave unchanged unless self-hosting. |
| `packageCacheDir` | same as `indexURL` | Directory where packages are cached in Node; ignored in browsers. |
| `lockFileURL` | `${indexURL}/pyodide-lock.json` | Where to load the lockfile. Custom lockfiles can be produced with `micropip.freeze`. |
| `lockFileContents` | — | Lockfile contents directly (object, JSON string, or promise of either). |
| `packageBaseUrl` | derived from `lockFileURL` | Base URL for relative `file_name` entries in the lockfile. Must be set explicitly if `lockFileContents` is used and packages have relative paths. |
| `stdLibURL` | `${indexURL}/python_stdlib.zip` | Where to load the standard library zip. |
| `fullStdLib` | — | **Deprecated, no effect.** |
| `stdin` | — | `() => string \| null` one-line input callback. Prefer `pyodide.setStdin`. |
| `stdout` | — | `(msg: string) => void`. Prefer `pyodide.setStdout`, but startup output can only be controlled here. |
| `stderr` | — | `(msg: string) => void`. Same notes as `stdout`. |
| `jsglobals` | `globalThis` | The object exposed as the Python `js` module. |
| `args` | `[]` | Command-line arguments passed to Python on startup. |
| `env` | `{}` (HOME defaults to `/home/pyodide` if unset) | Environment variables, visible via `os.environ` in Python. |
| `packages` | — | Packages to load during initialization (downloaded while Pyodide bootstraps, more efficient than loading after). |
| `enableRunUntilComplete` | `true` | Makes `loop.run_until_complete()` work correctly using stack switching. |
| `checkAPIVersion` | `true` | Throw if Pyodide core and JS package versions mismatch. |
| `fsInit` | — | **Experimental.** Hook to modify the file system before `main()` runs; guaranteed empty `site-packages`. |
| `pyproxyToStringRepr` | — | **Deprecated.** Old behavior where `PyProxy.toString()` calls `repr`. |
| `convertNullToNone` | — | **Deprecated.** Old behavior where JS `null` converts to `None`. |
| `toJsLiteralMap` | — | **Deprecated.** Old behavior where dicts convert to `LiteralMap`. |
| `createPyodideModule` | — | **Experimental.** Constructor function for the Pyodide module, importable from `pyodide.asm.mjs`. Used because service workers forbid dynamic `import()`; not intended for other cases. |

## The `pyodide` object — attributes

| Attribute | Meaning |
|---|---|
| `version` | Pyodide version string. |
| `globals` | Alias to the global Python namespace (`__main__`). `pyodide.globals.get("foo")`, `.set(...)`, `.delete(...)`. |
| `FS` | Emscripten File System API (`writeFile`, `readFile`, `mkdirTree`, `mount`, `syncfs`, `filesystems` = `{ IDBFS, MEMFS, NODEFS, PROXYFS, WORKERFS }`, ...). Only MEMFS is guaranteed in all settings. |
| `PATH` | Emscripten Path API (`dirname`, `normalize`, `splitPath`, ...). |
| `canvas` | APIs to set a canvas for graphics rendering (needed for SDL). |
| `ERRNO_CODES` | Map from POSIX error names to codes. |
| `pyodide_py` | The Python `pyodide` package as a PyProxy (call `pyodide.code.*` etc. from JS). |
| `ffi` | FFI classes (for TypeScript type annotations or `instanceof` checks). |
| `loadedPackages` | Packages currently loaded. |
| `lockfile` | The loaded lockfile. |
| `lockfileBaseUrl` | Base URL used for lockfile-relative paths. |

## The `pyodide` object — methods

### Running code

- `runPython(code, options?)` — run code synchronously via `pyodide.code.eval_code`. Options:
  - `globals?: PyProxy` — Python dict, defaults to `pyodide.globals`
  - `locals?: PyProxy` — Python dict, defaults to `globals`
  - `filename?: string` — default `"<exec>"`; custom names show source lines in tracebacks unless wrapped in `<>`
  - `dedent?: boolean` — default `true`
  - Returns the last statement's value translated to JS: if the last statement is an expression (code doesn't end with a semicolon) that expression's value; otherwise `None` (arriving in JS as `undefined`).
- `runPythonAsync(code, options?)` — same options; supports top-level `await` via `eval_code_async`; returns a promise.

### Objects and modules

- `pyimport(mod_name)` — import a Python module/object from JS. Without a dot: `import <name>; <name>`; with a dot: `from <path> import <name>`.
- `toPy(obj, options?)` — convert a JS object to Python (explicit conversion, JS→Python direction).
- `registerJsModule(name, module)` — expose a JS object as a Python module (import it normally, incl. `from name.submodule import x`).
- `unregisterJsModule(name)` — remove a registered module.

### Packages

- `loadPackage(nameOrUrl | namesOrUrls, options?)` — load bundled package(s) or a wheel from a custom URL (file name must be a valid wheel name). Returns a promise. Dependencies load automatically only for official-repo packages.
- `loadPackagesFromImports(code, options?)` — inspect code with `pyodide.code.find_imports` and load the distribution packages it imports. Never downloads from PyPI. To change which packages are detected, monkey-patch `pyodide.code.find_imports`.

### File system and archives

- `unpackArchive(buffer, format)` — unpack an archive into the FS (formats like `"zip"`, `"gztar"`).
- `mountNodeFS(emscriptenPath, hostPath)` — mount the host directory `hostPath` at `emscriptenPath` (Node.js only). The target must be an existing, empty directory.
- `mountNativeFS(dirPath, dirHandle)` — **experimental, Chromium-only** (File System Access API). Mounts a `FileSystemDirectoryHandle`; returns `{ syncfs }` — call `await syncfs()` to persist changes to the native FS.

### Node.js sockets

- `useNodeSockFS()` — **experimental, Node.js only.** Enable an experimental socket API. Must be awaited before importing any Python module that uses sockets. Requires JavaScript Promise Integration (Node <= 24: run with `--experimental-wasm-stack-switching`; Node >= 25: default).

### Streams

- `setStdin(options?)` — `{ error: true }`, no args (default behavior), `{ stdin, isatty }` handler (stdin returns a line string, utf8 bytes/Uint8Array, a byte 0-255, or `undefined`/`null` for EOF), or a `{ read(buf), isatty }` read handler (returns bytes read; useful with Node file descriptors).
- `setStdout(options?)` / `setStderr(options?)` — batched handler `(line) => void` (browser default is batched `console.log`), raw char-code handler, or `{ write(buf), isatty }` write handler (Node file descriptors). `isatty: true` cannot be combined with a batched handler.

### Interrupts, debugging, snapshots

- `setInterruptBuffer(buffer)` — set a `SharedArrayBuffer`-backed TypedArray; write `2` (SIGINT) to signal an interrupt. Requires a web worker setup.
- `checkInterrupt()` — call from JS (e.g. inside `Atomics.wait` loops or stdin/read handlers) to raise a `KeyboardInterrupt` if the buffer is set.
- `setDebug(debug: boolean)` — toggle debug mode; returns previous state.
- `makeMemorySnapshot(...)` — create memory snapshots (pair with `_loadSnapshot`/`_makeSnapshot` config for reuse; snapshots are build-specific via BUILD_ID).
- `registerComlink(Comlink)` — integrate with the Comlink RPC library.

## `pyodide.ffi`

FFI classes exposed for TypeScript annotations or runtime `instanceof` checks
(e.g. `pyodide.ffi.PyProxy`, `PyProxyWithGet`, `PyProxyWithSet`,
`PyBuffer`, `PyMutableSequence`, ...). For type imports in TS:

```ts
import type { PyProxy } from "pyodide/ffi";
```

At runtime use the instance from `loadPyodide`:

```js
const pyodide = await loadPyodide();
if (result instanceof pyodide.ffi.PyProxy) { /* ... */ }
```

## `pyodide.canvas`

APIs to set a canvas for rendering graphics; required before using SDL-based
packages (see [06-advanced](06-advanced.md)). Set an `HTMLCanvasElement` whose
`id` is `"canvas"`:

```js
const c = document.createElement("canvas");
c.id = "canvas";
pyodide.canvas.setCanvas2D(c);
```
