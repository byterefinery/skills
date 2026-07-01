---
name: emscripten-6-0-1
description: >
  Compile C/C++ to WebAssembly and JavaScript using Emscripten 6.0.1. Use for
  emcc compilation, file-system API (MEMFS, IDBFS, NODEFS, WasmFS), Embind
  C++/JS bindings, Asyncify, pthreads, ccall/cwrap, EM_ASM/EM_JS, val,
  Module lifecycle, --preload-file/--embed-file, --js-library, and all
  Emscripten toolchain tasks. Covers browser and Node.js targets.
metadata:
  tags:
    - webassembly
    - compilation
    - c-plus-plus
    - javascript
    - browser
---

# emscripten 6.0.1

## Overview

Emscripten 6.0.1 compiles C/C++ code to WebAssembly (`.wasm`) and JavaScript (`.js`) for execution in browsers and Node.js. The toolchain wraps Clang/LLVM and Binaryen, providing a complete libc/libcxx implementation, a virtual file system, browser API bindings, and C++/JavaScript interop via Embind.

Key capabilities:
- Compile C/C++ to WebAssembly with full standard library support
- Virtual file system (MEMFS default; IDBFS, NODEFS, WORKERFS, PROXYFS, OPFS, FetchFS, WasmFS)
- C++/JS interop via Embind (`EMSCRIPTEN_BINDINGS`), `ccall`/`cwrap`, `EM_ASM`/`EM_JS`, and `emscripten::val`
- Asyncify for synchronous-looking async calls from C/C++
- Pthreads (Web Workers with SharedArrayBuffer) for multithreading
- Dynamic linking, side modules, and module splitting

## Usage

### Basic Compilation

```bash
# Compile C/C++ to HTML + JS + WASM
emcc hello.c -o hello.html

# Compile to JS + WASM only (no HTML)
emcc hello.c -o hello.js

# Compile with optimization
emcc hello.c -O3 -o hello.js

# Export functions for JS calling
emcc hello.c -O3 -sEXPORTED_FUNCTIONS='["_main","_my_func"]' -o hello.js

# Embed or preload files
emcc app.c --embed-file assets/ -o app.js
emcc app.c --preload-file assets/ -o app.js  # produces app.data
```

### Key Compiler Flags

| Flag | Purpose |
|------|---------|
| `-O0` `-O1` `-O2` `-O3` `-Os` `-Oz` | Optimization levels |
| `-g` `-gsource-map` | Debug info / source maps |
| `-pthread` | Enable pthreads (SharedArrayBuffer) |
| `-lembind` | Include Embind for C++/JS bindings |
| `-sEXPORTED_FUNCTIONS` | List of C/C++ functions to export |
| `-sEXPORTED_RUNTIME_METHODS` | Runtime methods to export (ccall, cwrap, etc.) |
| `-sMODULARIZE` | Wrap output as a factory function |
| `-sALLOW_MEMORY_GROWTH` | Allow Wasm memory to grow at runtime |
| `-sINITIAL_MEMORY` | Set initial Wasm memory size |
| `-sASYNCIFY` | Enable Asyncify for pseudo-sync async |
| `-sPROXY_TO_PTHREAD` | Run main() on a worker thread |
| `-sPTHREAD_POOL_SIZE` | Pre-create worker pool |
| `-sSIDE_MODULE` | Compile as a dynamic library (side module) |
| `-sMAIN_MODULE` | Compile as a main module (can dlopen side modules) |
| `-sFORCE_FILESYSTEM` | Include full FS API even if C/C++ doesn't use files |
| `-sFILESYSTEM=0` | Disable filesystem entirely |
| `-sWASMFS` | Use WasmFS (new Wasm-based filesystem) |
| `-lidbfs.js` | Include IDBFS (IndexedDB persistence) |
| `-lnodefs.js` | Include NODEFS (Node.js host FS access) |
| `-lworkerfs.js` | Include WORKERFS (worker read-only FS) |
| `-lproxyfs.js` | Include PROXYFS (share another module's FS) |
| `--preload-file path` | Preload file/dir into virtual FS (produces .data file) |
| `--embed-file path` | Embed file/dir directly into Wasm module |
| `--js-library file.js` | Include a custom JS library file |
| `--pre-js file.js` | Inject JS before emitted code (optimized together) |
| `--post-js file.js` | Inject JS after emitted code (optimized together) |
| `--shell-file file.html` | Custom HTML shell template |
| `--closure 1` | Run Closure Compiler on output JS |
| `-sENVIRONMENT` | Target: `web`, `node`, `worker`, or `web,worker` |

### Calling C from JavaScript

After compilation, call exported functions via `Module`:

```javascript
// Using ccall (one-shot)
var result = Module.ccall('my_func', 'number', ['number', 'string'], [42, 'hello']);

// Using cwrap (creates reusable wrapper)
var my_func = Module.cwrap('my_func', 'number', ['number']);
my_func(100);

// Direct call (faster, uses underscore-prefixed name)
Module._my_func(100);
```

### Calling JavaScript from C/C++

```c
#include <emscripten.h>

// Inline JS (no return)
EM_ASM(alert('hello from JS'));

// Inline JS with arguments
EM_ASM(console.log('value: ' + $0), 42);

// Inline JS with return value
int x = EM_ASM_INT({ return $0 + 1; }, 100);

// Declare a JS function callable from C
EM_JS(void, js_alert, (const char* msg), {
  alert(UTF8ToString(msg));
});
```

### Embind (C++ to JavaScript)

```cpp
#include <emscripten/bind.h>

using namespace emscripten;

float lerp(float a, float b, float t) {
    return (1 - t) * a + t * b;
}

EMSCRIPTEN_BINDINGS(my_module) {
    function("lerp", &lerp);
}
```

Compile with `-lembind`. Access from JS via `Module.lerp(1, 2, 0.5)`.

## Gotchas

- **`--preload-file` vs `--embed-file`**: Preload produces a separate `.data` file loaded via XHR at runtime. Embed stores data directly in the Wasm module. Embed is more efficient (no copy at runtime) but increases Wasm size. Preload enables separate hosting/CDN for data.
- **`EXPORTED_FUNCTIONS` needs underscore prefix**: Use `["_main", "_my_func"]` not `["main", "my_func"]`. Without exporting, functions are eliminated as dead code.
- **`main()` runs automatically**: By default `main()` is called at startup. Set `Module.noInitialRun = true` to control when it runs.
- **Runtime stays alive after `main()`**: By default the runtime does NOT shut down when `main()` returns. Use `-sEXIT_RUNTIME` if you want it to shut down, or call `emscripten_force_exit()`.
- **`EM_ASM` single quotes only**: Inside `EM_ASM` blocks, use single quotes for strings. Double quotes cause C preprocessor issues that the compiler won't catch — they only appear as runtime JS errors.
- **`FS` API not included by default**: If C/C++ code doesn't use files, the `FS` object won't be in output. Use `-sFORCE_FILESYSTEM` to force inclusion when you need `FS` from JavaScript only.
- **WasmFS requires `-sFORCE_FILESYSTEM` for JS FS API**: WasmFS is the new default filesystem backend. The JS `FS.mkdir()`, `FS.writeFile()` etc. are not included by default with WasmFS. Add `-sFORCE_FILESYSTEM` to get the full JS API.
- **`--pre-js` vs `--post-js` vs `--extern-pre-js`**: `--pre-js` and `--post-js` are optimized together with the output. `--extern-pre-js` is prepended after all optimization (use for code that must not be modified).
- **Pthreads requires COOP/COEP headers**: For SharedArrayBuffer in browsers, set `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: require-corp` headers. Without these, SharedArrayBuffer is unavailable.
- **Memory growth invalidates JS views**: With `-sALLOW_MEMORY_GROWTH`, `HEAPU8`, `HEAPF32` etc. are refreshed automatically, but any `subarray()` views you hold become stale. Re-create views after operations that might grow memory.
- **`stringToNewUTF8` allocates — must `free`**: When passing JS strings to C as `char*`, `stringToNewUTF8()` allocates heap memory. Always call `_free(ptr)` afterward or memory leaks.
- **`Module` properties must be set before runtime starts**: Changing `Module.print`, `Module.arguments`, etc. after the runtime initializes has no effect. Set them via `--pre-js` or before loading the script.
- **Asyncify dramatically increases code size**: Only use `-sASYNCIFY` when needed. Always build with `-O3` when using Asyncify — unoptimized Asyncify builds are extremely large.
- **`-pthread` and `-sBUILD_AS_WORKER` are incompatible**: The old Worker API (`emscripten_create_worker`) cannot be used with pthreads. Use pthreads for multithreading.
- **`FS.syncfs` is async and only works with IDBFS**: Call `FS.syncfs(populate, callback)` to persist. `populate=true` loads from IndexedDB, `false` saves to IndexedDB. Other filesystems are fully synchronous and don't need sync.
- **`@` symbol in preload/embed paths**: Use `--preload-file src@dst` to map a local path to a different virtual FS path. Escape literal `@` in filenames as `@@`.
- **`clang-format` breaks `EM_ASM`**: The `=>` arrow can be split to `= >`. Add `EM_ASM`, `EM_JS`, etc. to `WhitespaceSensitiveMacros` in `.clang-format` or use `// clang-format off/on` guards.

## References

- [01-compilation-basics](references/01-compilation-basics.md) — emcc flags, optimization, output formats, CMake integration
- [02-file-system-api](references/02-file-system-api.md) — Virtual FS (MEMFS, IDBFS, NODEFS, WasmFS, OPFS, FetchFS), packaging, FS API
- [03-cpp-js-interop](references/03-cpp-js-interop.md) — Embind, ccall/cwrap, EM_ASM/EM_JS, val, JS libraries, memory access
- [04-asyncify-and-pthreads](references/04-asyncify-and-pthreads.md) — Asyncify, JSPI, pthreads, workers, proxying
- [05-runtime-and-module](references/05-runtime-and-module.md) — Module object, lifecycle hooks, environment, dynamic linking
