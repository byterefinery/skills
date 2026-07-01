# File System

Pyodide uses Emscripten's virtual file system. Access from JavaScript via `pyodide.FS` and from Python via standard `open()`, `pathlib`, `os`, etc.

## Filesystem Types

| Type | Environment | Persistence | Description |
|---|---|---|---|
| **MEMFS** | All | No (in-memory) | Default. Fast, volatile. Lost on reload. |
| **IDBFS** | Browser | Yes (IndexedDB) | Persistent via IndexedDB. Requires `syncfs()`. |
| **NODEFS** | Node.js | Yes (host FS) | Direct host filesystem access. Bidirectional. |
| **NATIVEFS_ASYNC** | Browser (Chrome) | Yes (File System Access API) | Native browser filesystem. Requires `syncfs()`. |
| **PROXYFS** | All | Depends on backing | Proxy to another mounted filesystem. |
| **WORKERFS** | Browser | No | For sharing files with web workers. |

## MEMFS (Default)

The root filesystem. All Python file operations use MEMFS by default.

```python
# Python
from pathlib import Path
Path("/hello.txt").write_text("hello world!")
content = Path("/hello.txt").read_text()

import os
os.mkdir("/mydir")
os.listdir("/mydir")
```

```js
// JavaScript
pyodide.FS.writeFile("/hello.txt", "hello world", { encoding: "utf8" });
const data = pyodide.FS.readFile("/hello.txt", { encoding: "utf8" });
pyodide.FS.mkdirTree("/a/b/c");
const entries = pyodide.FS.readdir("/");
const stat = pyodide.FS.stat("/hello.txt");
```

## IDBFS (Browser Persistence)

Mount IndexedDB-backed filesystem for persistence across page reloads.

```js
// Mount
const mountDir = "/mnt";
pyodide.FS.mkdirTree(mountDir);
pyodide.FS.mount(pyodide.FS.filesystems.IDBFS, {}, mountDir);

// Sync from IndexedDB to MEMFS (load data)
pyodide.FS.syncfs(true, (err) => {
  if (err) throw err;
  // data loaded
});

// Use the filesystem
pyodide.runPython(`
  with open("/mnt/data.txt", "w") as f:
      f.write("persistent data")
`);

// Sync from MEMFS to IndexedDB (save data)
pyodide.FS.syncfs(false, (err) => {
  if (err) throw err;
  // data persisted
});
```

**Important:** IDBFS is asynchronous. Changes are not persisted until `syncfs(false, callback)` is called. Without it, data is lost on reload.

## NODEFS (Node.js Host Access)

Mount a host directory for immediate bidirectional access.

```js
// Via pyodide API
pyodide.mountNodeFS("/src", "/path/on/host");

// Via FS API directly
const mountDir = "/mnt";
pyodide.FS.mkdirTree(mountDir);
pyodide.FS.mount(pyodide.FS.filesystems.NODEFS, { root: "." }, mountDir);
```

All changes are immediately reflected in both directions. No sync needed.

## NativeFS (Browser — Chrome Only)

Mount a native directory using the File System Access API.

```js
// Acquire directory handle (user picks folder)
const dirHandle = await showDirectoryPicker();

// Request permission
const permission = await dirHandle.requestPermission({ mode: "readwrite" });
if (permission !== "granted") {
  throw new Error("Permission denied");
}

// Mount
const { syncfs } = await pyodide.mountNativeFS("/mnt", dirHandle);

// Use from Python
pyodide.runPython(`
  import os
  print(os.listdir("/mnt"))
`);

// Persist changes
await syncfs();
```

### Persisting Directory Handles

Store handles in IndexedDB to avoid repeated folder picker prompts:

```js
// Using idb-keyval
const { get, set } = await import("https://unpkg.com/idb-keyval@6/dist/esm/index.js");

async function mountDirectory(pyodideDir, key) {
  let handle = await get(key);
  if (!handle) {
    handle = await showDirectoryPicker({ id: "mountdir", mode: "readwrite" });
    await set(key, handle);
  }
  const perm = await handle.requestPermission({ mode: "readwrite" });
  if (perm !== "granted") throw new Error("Permission denied");
  return await pyodide.mountNativeFS(pyodideDir, handle);
}
```

## Unpacking Archives

### From JavaScript

```js
// Fetch and unpack
const response = await fetch("data.zip");
const buffer = await response.arrayBuffer();
pyodide.unpackArchive(buffer, "zip");

// With extract directory
pyodide.unpackArchive(buffer, "gztar", { extractDir: "/data" });
```

**Formats:** `zip`, `tar`, `gztar` (`.tar.gz`, `.tgz`), `bztar`, `wheel`.

### From Python

```python
from pyodide.http import pyfetch

# Download and unpack archive
resp = await pyfetch("https://example.com/data.zip")
await resp.unpack_archive(extract_dir="/data", format="zip")

# Download single file
resp = await pyfetch("https://example.com/script.py")
with open("script.py", "wb") as f:
    f.write(await resp.bytes())
```

## Important Notes

### Importing New Modules

After writing a `.py` file to MEMFS, call `importlib.invalidate_caches()` before importing:

```python
from pathlib import Path
Path("mymodule.py").write_text("def hello(): print('hi')")

import importlib
importlib.invalidate_caches()

from mymodule import hello
hello()
```

### Working Directory

The default working directory is `/home/pyodide`. Python's `os.getcwd()` and relative paths use this.

### File System API Reference

Key `pyodide.FS` methods:

| Method | Description |
|---|---|
| `FS.readFile(path, opts)` | Read file contents |
| `FS.writeFile(path, data, opts)` | Write file |
| `FS.mkdirTree(path)` | Create directory tree |
| `FS.readdir(path)` | List directory |
| `FS.stat(path)` | File stats |
| `FS.unlink(path)` | Delete file |
| `FS.rmdir(path)` | Remove directory |
| `FS.rename(old, new)` | Rename/move |
| `FS.mount(type, opts, mountpoint)` | Mount filesystem |
| `FS.syncfs(fetch, callback)` | Sync IDBFS |
| `FS.lookupPath(path)` | Resolve path |
| `FS.analyzePath(path)` | Check path existence |

Options for read/write: `{ encoding: "utf8" }` for text, omit for binary (returns `Uint8Array`).

## pyodide.PATH

Emscripten path utilities:

```js
pyodide.PATH.dirname("/a/b/c.txt");   // "/a/b"
pyodide.PATH.basename("/a/b/c.txt");  // "c.txt"
pyodide.PATH.normalize("/a//b/./c");  // "/a/b/c"
pyodide.PATH.join("/a", "b", "c");    // "/a/b/c"
pyodide.PATH.splitPath("/a/b/c.txt"); // { dirty: ["a", "b"], root: "", ext: ".txt", base: "c.txt" }
```
