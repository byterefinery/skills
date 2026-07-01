# File System API — Emscripten 6.0.1

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Packaging Files at Compile Time](#packaging-files-at-compile-time)
- [MEMFS (Default In-Memory)](#memfs-default-in-memory)
- [IDBFS (IndexedDB Persistence)](#idbfs-indexeddb-persistence)
- [NODEFS (Node.js Host Filesystem)](#nodefs-nodejs-host-filesystem)
- [NODERAWFS (Direct Node.js FS)](#noderawfs-direct-nodejs-fs)
- [WORKERFS (Worker Read-Only)](#workerfs-worker-read-only)
- [PROXYFS (Cross-Module FS Sharing)](#proxyfs-cross-module-fs-sharing)
- [OPFS (Origin Private Filesystem)](#opfs-origin-private-filesystem)
- [FetchFS (HTTP Cache)](#fetchfs-http-cache)
- [WasmFS (New Wasm-Based Filesystem)](#wasmfs-new-wasm-based-filesystem)
- [JS FS API Reference](#js-fs-api-reference)
- [C/C++ Async File API](#cc-async-file-api)
- [Standard I/O Devices](#standard-io-devices)
- [File System Gotchas](#file-system-gotchas)

## Architecture Overview

Emscripten provides a virtual file system that simulates POSIX file operations for compiled C/C++ code. The architecture:

```
C/C++ libc/libcxx file APIs (fopen, fread, std::ifstream, etc.)
    ↓
Emscripten FS API (JS layer)
    ↓
Mounted filesystem backends:
    ├── MEMFS (default, in-memory, mounted at /)
    ├── IDBFS (IndexedDB persistence)
    ├── NODEFS (Node.js host filesystem)
    ├── WORKERFS (worker read-only)
    ├── PROXYFS (share another module's FS)
    ├── OPFS (Origin Private Filesystem)
    └── FetchFS (HTTP-cached files)
```

MEMFS is automatically mounted at `/` at runtime startup. `/home/web_user` and `/tmp` directories are created automatically. Special devices like `/dev/null`, `/dev/random`, `/dev/stdin`, `/dev/stdout`, `/dev/stderr` are also created.

**WasmFS** is the new Wasm-based filesystem replacing the JS implementation. It provides full multithreading support and better performance.

## Packaging Files at Compile Time

### `--preload-file`

Preloads files into a separate `.data` file, loaded via XHR at runtime:

```bash
# Preload a single file
emcc app.c --preload-file config.json -o app.js

# Preload a directory (preserves structure)
emcc app.c --preload-file assets/ -o app.js

# Map to different virtual path using @
emcc app.c --preload-file ../shared/data@/data -o app.js

# Preload with auto-decoding of images/audio
emcc app.c --preload-file images/ --use-preload-plugins -o app.js
```

Produces `app.js`, `app.wasm`, and `app.data`. The `.data` file must be served alongside the JS.

### `--embed-file`

Embeds files directly into the Wasm module (no separate `.data` file):

```bash
# Embed a file
emcc app.c --embed-file config.json -o app.js

# Embed a directory
emcc app.c --embed-file assets/ -o app.js

# Map to different virtual path
emcc app.c --embed-file ../shared/data@/data -o app.js
```

More efficient than preloading (no runtime copy), but increases Wasm binary size.

### `--exclude-file`

Exclude files from preload/embed:

```bash
emcc app.c --preload-file assets/ --exclude-file "*.psd" "*.tmp" -o app.js
```

### Preload Plugins

With `--use-preload-plugins`, files are auto-decoded based on extension:
- **Images** (`.jpg`, `.jpeg`, `.png`, `.bmp`): Decoded via browser image decoder for `IMG_Load`
- **Audio** (`.ogg`, `.wav`, `.mp3`): Decoded via browser audio decoder for `Mix_LoadWAV`
- **Dynamic libraries** (`.so`): Precompiled via `WebAssembly.instantiate` for synchronous `dlopen`

Disable specific decoding: `Module.noImageDecoding = true`, `Module.noAudioDecoding = true`, `Module.noWasmDecoding = true`.

## MEMFS (Default In-Memory)

- **Included by default** — no extra flags needed
- All files exist strictly in memory
- Data written is **lost on page reload**
- Mounted at `/` automatically

```javascript
// MEMFS operations from JS
FS.mkdir('/data');
FS.writeFile('/data/config.json', JSON.stringify({key: 'value'}));
var contents = FS.readFile('/data/config.json', { encoding: 'utf8' });
FS.unlink('/data/config.json');
```

## IDBFS (IndexedDB Persistence)

- **Browser only** — requires `-lidbfs.js`
- Persists data to IndexedDB
- Requires explicit `FS.syncfs()` calls to sync

```bash
emcc app.c -lidbfs.js -o app.js
```

```javascript
// Mount IDBFS
FS.mkdir('/persistent');
FS.mount(IDBFS, {}, '/persistent');

// Load from IndexedDB on startup (populate=true)
FS.syncfs(true, (err) => {
  if (err) console.error('Sync failed:', err);
  else console.log('Loaded from IndexedDB');
});

// Save to IndexedDB on shutdown (populate=false)
FS.syncfs(false, (err) => {
  if (err) console.error('Save failed:', err);
  else console.log('Saved to IndexedDB');
});
```

**autoPersist option**: Pass `{ autoPersist: true }` to `FS.mount()` to automatically persist every change without manual `syncfs` calls.

## NODEFS (Node.js Host Filesystem)

- **Node.js only** — requires `-lnodefs.js`
- Maps host directories to virtual FS
- Changes persist immediately to disk

```bash
emcc app.c -lnodefs.js -o app.js
```

```javascript
// Mount host directory into virtual FS
FS.mkdir('/host');
FS.mount(NODEFS, { root: '.' }, '/host');

// Now /host maps to the current working directory on disk
// All reads/writes go directly to the host filesystem
```

## NODERAWFS (Direct Node.js FS)

- **Node.js only**
- Replaces all filesystem access with direct Node.js operations
- No `FS.mount()` needed — initial working directory is `process.cwd()`
- Not portable between OSes (behaves like a Node.js program)

```bash
emcc app.c -sNODERAWFS -o app.js
```

## WORKERFS (Worker Read-Only)

- **Web Workers only** — requires `-lworkerfs.js`
- Read-only access to `File` and `Blob` objects
- No data copy into memory — suitable for huge files

```bash
emcc app.c -lworkerfs.js -o app.js
```

```javascript
// Mount Blobs as read-only files
var blob = new Blob(['blob data']);
FS.mkdir('/blobs');
FS.mount(WORKERFS, {
  blobs: [{ name: 'data.txt', data: blob }],
  files: fileArray  // Array of File objects or FileList
}, '/blobs');
```

## PROXYFS (Cross-Module FS Sharing)

- Requires `-lproxyfs.js`
- Mount another module's filesystem for shared access

```bash
emcc app.c -lproxyfs.js -o app.js
```

```javascript
// Module 2 mounts Module 1's filesystem
module2.FS.mkdir('/fs1');
module2.FS.mount(module2.PROXYFS, {
  root: '/',
  fs: module1.FS
}, '/fs1');
```

## OPFS (Origin Private Filesystem)

- Browser API for persistent, origin-scoped storage
- Replaces IDBFS for new projects (better performance)
- Use `-sOPFS` or include the OPFS library

## FetchFS (HTTP Cache)

- Caches files fetched over HTTP
- Files are fetched on first access and cached
- Useful for large assets that shouldn't be preloaded

## WasmFS (New Wasm-Based Filesystem)

WasmFS is the new high-performance, fully-multithreaded filesystem that replaces the JS implementation.

### Key Differences from JS FS

- Compiled to Wasm with full multithreading support
- Does **not** include JS FS API by default (use `-sFORCE_FILESYSTEM` for JS access)
- Requires `malloc` internally (cannot use `-sMALLOC=none`)
- MEMFS backend uses `wasmfs_create_memory_backend()`

```bash
# Use WasmFS (may be default in newer versions)
emcc app.c -sWASMFS -o app.js

# Include full JS FS API with WasmFS
emcc app.c -sWASMFS -sFORCE_FILESYSTEM -o app.js
```

### WasmFS Backends

WasmFS supports the same backend types as the JS FS:
- Memory backend (replaces MEMFS)
- OPFS backend
- Node.js backend
- Fetch backend
- JS implementation fallback (`wasmfs_create_jsimpl_backend`)

## JS FS API Reference

### File Operations

```javascript
// Create directory
FS.mkdir('/path/to/dir', 0o777);

// Create directory and all parents
FS.mkdirTree('/path/to/deep/dir', 0o777);

// Create symlink
FS.symlink('target_file', 'link_name');

// Read symlink target
FS.readlink('link_name');

// Rename
FS.rename('/old/path', '/new/path');

// Remove directory (must be empty)
FS.rmdir('/path/to/dir');

// Unlink (delete file)
FS.unlink('/path/to/file');

// Truncate file
FS.truncate('/path/to/file', 100);

// Change permissions
FS.chmod('/path/to/file', 0o644);

// Change timestamps (milliseconds since epoch)
FS.utime('/path/to/file', atime, mtime);
```

### File I/O

```javascript
// Read entire file
var data = FS.readFile('/path/to/file', { encoding: 'binary' });  // Uint8Array
var text = FS.readFile('/path/to/file', { encoding: 'utf8' });    // String

// Write entire file
FS.writeFile('/path/to/file', 'text content');
FS.writeFile('/path/to/file', new Uint8Array([1, 2, 3]));

// Open, read/write, close (stream-based)
var stream = FS.open('/path/to/file', 'r');           // read
var stream = FS.open('/path/to/file', 'w');           // write (truncate)
var stream = FS.open('/path/to/file', 'w+');          // read+write (truncate)
var stream = FS.open('/path/to/file', 'a');           // append
var stream = FS.open('/path/to/file', 'r+');          // read+write

var buf = new Uint8Array(1024);
FS.read(stream, buf, 0, 1024);        // read into buffer
FS.write(stream, buf, 0, buf.length); // write from buffer
FS.llseek(stream, 0, 0);              // seek to beginning (SEEK_SET=0, SEEK_CUR=1, SEEK_END=2)
FS.close(stream);
```

### Path Operations

```javascript
// Current working directory
var cwd = FS.cwd();
FS.chdir('/new/dir');

// List directory
var entries = FS.readdir('/path/to/dir');  // includes '.' and '..'

// Lookup path (resolve to node)
var result = FS.lookupPath('/path/to/file', { parent: false, follow: true });
// Returns: { path: resolved_path, node: resolved_node }

// Analyze path (more detailed)
var info = FS.analyzePath('/path/to/file', false);
// Returns: { isRoot, exists, error, name, path, object, parentExists, parentPath, parentObject }

// Get absolute path of a node
var absPath = FS.getPath(node);
```

### File Statistics

```javascript
var stats = FS.stat('/path/to/file');
// Returns: { dev, ino, mode, nlink, uid, gid, rdev, size, atime, mtime, ctime, blksize, blocks }

var linkStats = FS.lstat('/path/to/symlink');  // stats for the link itself, not target
```

### File Type Checks

```javascript
FS.isFile(mode);    // Regular file
FS.isDir(mode);     // Directory
FS.isLink(mode);    // Symlink
FS.isChrdev(mode);  // Character device
FS.isBlkdev(mode);  // Block device
FS.isSocket(mode);  // Socket
```

### Mounting Filesystems

```javascript
FS.mount(type, opts, mountpoint);
FS.unmount(mountpoint);

// Examples:
FS.mkdir('/data');
FS.mount(MEMFS, {}, '/data');

FS.mkdir('/persistent');
FS.mount(IDBFS, { autoPersist: true }, '/persistent');

FS.mkdir('/host');
FS.mount(NODEFS, { root: '.' }, '/host');
```

### SyncFS

```javascript
// Only meaningful for IDBFS (and other persistent filesystems)
FS.syncfs(true, (err) => { /* load from persistent storage */ });
FS.syncfs(false, (err) => { /* save to persistent storage */ });
```

### Lazy and Preloaded Files

```javascript
// Lazy-loaded file (loaded on first access)
FS.createLazyFile('/', 'foo.txt', 'http://example.com/foo.txt', true, false);

// Preloaded file (async, uses preload plugins)
// Call in preRun to delay main() until ready
FS.createPreloadedFile('/', 'bar.png', 'http://example.com/bar.png', true, false);
```

### Device Nodes

```javascript
// Create custom device
var devId = FS.makedev(64, 0);
FS.registerDevice(devId, {
  open: function(stream) { /* ... */ },
  close: function(stream) { /* ... */ },
  read: function(stream, buffer, offset, length, position) { /* ... */ },
  write: function(stream, buffer, offset, length, position) { /* ... */ },
});
FS.mkdev('/mydevice', 0o666, devId);
```

### Tracking Delegate (requires `-sFS_DEBUG`)

```javascript
FS.trackingDelegate['willMovePath'] = function(oldpath, newpath) { /* ... */ };
FS.trackingDelegate['onMovePath'] = function(oldpath, newpath) { /* ... */ };
FS.trackingDelegate['willDeletePath'] = function(path) { /* ... */ };
FS.trackingDelegate['onDeletePath'] = function(path) { /* ... */ };
FS.trackingDelegate['onOpenFile'] = function(path, flags) { /* ... */ };
FS.trackingDelegate['onReadFile'] = function(path, bytesRead) { /* ... */ };
FS.trackingDelegate['onWriteToFile'] = function(path, bytesWritten) { /* ... */ };
FS.trackingDelegate['onSeekFile'] = function(path, position, whence) { /* ... */ };
FS.trackingDelegate['onCloseFile'] = function(path) { /* ... */ };
FS.trackingDelegate['onMakeDirectory'] = function(path, mode) { /* ... */ };
FS.trackingDelegate['onMakeSymlink'] = function(oldpath, newpath) { /* ... */ };
```

### FS.init (Custom stdio)

```javascript
// Override stdin/stdout/stderr
FS.init(
  function() { /* stdin: return char code or null */ },
  function(charCode) { /* stdout: charCode or null to flush */ },
  function(charCode) { /* stderr: charCode or null to flush */ }
);
```

## C/C++ Async File API

### `emscripten_async_wget` — Load File from URL

```c
#include <emscripten.h>

void on_load(const char* file) {
    FILE* f = fopen(file, "r");
    // use file
    fclose(f);
}

void on_error(const char* file) {
    printf("Failed to load: %s\n", file);
}

// Load URL into virtual filesystem
emscripten_async_wget("http://example.com/data.json", "/data.json", on_load, on_error);
```

### `emscripten_async_wget_data` — Load into Memory Buffer

```c
void data_onload(void* arg, void* buffer, int size) {
    // buffer lives only during callback — copy if needed
    printf("Loaded %d bytes\n", size);
}

emscripten_async_wget_data("http://example.com/data.bin", NULL, data_onload, on_error);
```

### `emscripten_wget` — Synchronous (requires Asyncify)

```c
#include <emscripten.h>

// Requires -sASYNCIFY
int result = emscripten_wget("http://example.com/data.json", "/data.json");
if (result == 0) {
    FILE* f = fopen("/data.json", "r");
    // use file
    fclose(f);
}
```

### Async IndexedDB API

```c
// Load from IndexedDB
emscripten_idb_async_load("mydb", "file_id", arg, onload, onerror);

// Store to IndexedDB
emscripten_idb_async_store("mydb", "file_id", buffer, num_bytes, arg, onstore, onerror);

// Delete from IndexedDB
emscripten_idb_async_delete("mydb", "file_id", arg, ondelete, onerror);

// Check existence
emscripten_idb_async_exists("mydb", "file_id", arg, oncheck, onerror);

// Clear all
emscripten_idb_async_clear("mydb", arg, onclear, onerror);
```

### Synchronous IndexedDB (requires Asyncify)

```c
void* buffer;
int size, error;

emscripten_idb_load("mydb", "file_id", &buffer, &size, &error);
if (!error) {
    // use buffer
    free(buffer);  // Must free!
}
```

## Standard I/O Devices

Emscripten routes stdin/stdout/stderr through virtual devices:

- `/dev/stdin` — Reads from terminal (CLI) or `window.prompt()` (browser)
- `/dev/stdout` — Prints to terminal (CLI) or browser console
- `/dev/stderr` — Same as stdout by default

Override via `FS.init()` or `Module.print`/`Module.printErr`:

```javascript
var Module = {
  print: function(text) { /* handle stdout */ },
  printErr: function(text) { /* handle stderr */ }
};
```

## File System Gotchas

- **`FS` not included if C/C++ doesn't use files**: Use `-sFORCE_FILESYSTEM` to force inclusion when accessing FS from JS only.
- **WasmFS doesn't include JS FS API by default**: Use `-sFORCE_FILESYSTEM` with `-sWASMFS` to get `FS.mkdir()`, `FS.writeFile()`, etc.
- **Permissions are ignored**: User/group permissions are defined but not enforced. The caller is always treated as owner.
- **`FS.syncfs` is async**: Only IDBFS (and similar persistent FS) support syncfs. Other filesystems are fully synchronous.
- **`@` in filenames must be escaped**: Use `@@` for literal `@` in filenames with `--preload-file`/`--embed-file`.
- **`/`, `\`, `:` not allowed in filenames**: These characters cannot be used in packaged filenames.
- **MEMFS data is lost on reload**: Use IDBFS, OPFS, or NODEFS for persistence.
- **NODEFS is Node.js only**: Will not work in browser environments.
- **`createLazyFile` uses sync XHR**: Disabled in Chrome/Firefox for main thread. Works in Web Workers.
- **`FS.readFiles` tracks accessed files**: Use `Module.logReadFiles` or inspect `FS.readFiles` to see which preloaded files are actually used at runtime.
- **`FS.createPreloadedFile` delays `main()`**: Call in `preRun` to ensure files are ready before the program starts.
- **Memory growth invalidates `HEAP*` views**: With `-sALLOW_MEMORY_GROWTH`, recreate any `subarray()` views after memory might grow.
