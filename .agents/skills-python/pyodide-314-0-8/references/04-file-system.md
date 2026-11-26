# File system

## Contents

- The Emscripten FS (`pyodide.FS`)
- File system types
- Mounting examples
- NativeFS (browser, experimental)
- Persistence
- Accessing files quick reference
- Unpacking archives

## The Emscripten FS (`pyodide.FS`)

In JavaScript, the Pyodide file system is accessed through `pyodide.FS`, which
re-exports the Emscripten File System API. Python sees the same files through
normal POSIX paths.

```js
// Read
pyodide.runPython(`
  from pathlib import Path
  Path("/hello.txt").write_text("hello world!")
`);
let file = pyodide.FS.readFile("/hello.txt", { encoding: "utf8" }); // "hello world!"

// Write
pyodide.FS.writeFile("/hello.txt", "data", { encoding: "utf8" });
```

`pyodide.PATH` re-exports the Emscripten Path API (`dirname`, `normalize`,
`splitPath`, ...).

## File system types

| FS | Notes |
|---|---|
| `MEMFS` | Default. Virtual in-memory; data lost on page reload. Guaranteed to work in all runtime settings. |
| `IDBFS` | IndexedDB-backed persistence in the browser. **Asynchronous** — call `pyodide.FS.syncfs()` to persist. |
| `NODEFS` | Node.js host filesystem. Changes reflect immediately both ways. |
| `PROXYFS` | Proxy filesystem (Emscripten-provided). |
| `WORKERFS` | Worker filesystem (Emscripten-provided). |

Implementations are available as `pyodide.FS.filesystems` members
(`IDBFS`, `MEMFS`, `NODEFS`, `PROXYFS`, `WORKERFS`); some only work in
specific runtime environments (see the Emscripten File System API docs).

## Mounting examples

```js
// IDBFS — persist across page reloads
let mountDir = "/mnt";
pyodide.FS.mkdirTree(mountDir);
pyodide.FS.mount(pyodide.FS.filesystems.IDBFS, {}, mountDir);

// NODEFS — Node.js host directory
pyodide.FS.mkdirTree("/mnt");
pyodide.FS.mount(pyodide.FS.filesystems.NODEFS, { root: "." }, "/mnt");
```

Or the higher-level helpers:

```js
// Node.js host path (target dir must exist and be empty)
pyodide.mountNodeFS("my_package", "/path/to/my_package");
```

## NativeFS (browser, experimental)

Access the native file system in Chromium-based browsers (Chrome/Edge) via the
File System Access API. `pyodide.mountNativeFS` mounts a
`FileSystemDirectoryHandle` into the Pyodide FS.

```js
const dirHandle = await showDirectoryPicker();
const permissionStatus = await dirHandle.requestPermission({ mode: "readwrite" });
if (permissionStatus !== "granted") {
  throw new Error("readwrite access to directory not granted");
}
const { syncfs } = await pyodide.mountNativeFS("/mount_dir", dirHandle);

// ... write files via Python or FS ...
await syncfs(); // persist to the native file system
```

Changes are **not** synchronized to the native FS by default — `syncfs` (or
`pyodide.FS.syncfs(false, callback)`) is required to persist.

## Persistence summary

- MEMFS: nothing persists.
- IDBFS: call `pyodide.FS.syncfs()` — without it, IndexedDB changes are lost
  (the FAQ's "Why changes made to IndexedDB don't persist" is exactly this).
- NativeFS: call the returned `syncfs` after writes.
- NODEFS: immediate, no sync needed.

## Accessing files quick reference

- **Node.js development**: mount the development directory with
  `pyodide.mountNodeFS` — best experience, changes reflect both ways.
- **Browser development**: use Chrome NativeFS via a folder picker; store the
  directory handle in IndexedDB (e.g. with the `idb-keyval` package) so the
  picker is not needed again, then re-request permission and `mountNativeFS`.
- Browsers cannot read `file://` local paths directly (Same Origin Policy) —
  serve files with a local web server during development.

## Unpacking archives

```js
// From JS
let zipResponse = await fetch("myfiles.zip");
let zipBinary = await zipResponse.arrayBuffer();
pyodide.unpackArchive(zipBinary, "zip"); // formats: "zip", "gztar", ...
```

```python
# From Python
from pyodide.http import pyfetch
response = await pyfetch("https://some_url/myfiles.zip")
await response.unpack_archive()  # unpacks to the current directory by default
```

Prefer serving files as one archive over downloading each script individually.
Unpacking a `.whl` (a zip) works but does **no dependency resolution** — that
is `micropip`'s job.
