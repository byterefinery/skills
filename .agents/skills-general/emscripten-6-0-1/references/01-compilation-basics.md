# Compilation Basics — Emscripten 6.0.1

## Table of Contents

- [emcc Command-Line Reference](#emcc-command-line-reference)
- [Output Formats](#output-formats)
- [Optimization Levels](#optimization-levels)
- [Debug and Source Maps](#debug-and-source-maps)
- [Exporting Functions](#exporting-functions)
- [MODULARIZE](#modularize)
- [Memory Settings](#memory-settings)
- [CMake Integration](#cmake-integration)
- [Important Settings Reference](#important-settings-reference)

## emcc Command-Line Reference

`emcc` is the Emscripten compiler frontend, a drop-in replacement for `gcc`/`clang`.

```bash
# Basic compilation
emcc source.c -o output.html          # HTML + JS + WASM
emcc source.c -o output.js            # JS + WASM only
emcc source.c -o output.wasm          # WASM only (no JS glue)
emcc source.c -c -o source.o          # Compile to object file

# C++ compilation
emcc source.cpp -o output.js
em++ source.cpp -o output.js          # Same as emcc for C++

# Cross-compilation helpers
emconfigure ./configure               # Wrapper for autoconf
emmake make                           # Wrapper for make
emcmake cmake ..                      # Wrapper for cmake
```

### Key Link-Time Flags

| Flag | Description |
|------|-------------|
| `-sEXPORTED_FUNCTIONS='["_main","_foo"]'` | Functions to keep alive and export |
| `-sEXPORTED_RUNTIME_METHODS='["ccall","cwrap","UTF8ToString"]'` | Runtime methods to export |
| `-sMODULARIZE=1` | Wrap output as a factory function returning Promise |
| `-sENVIRONMENT='web'` | Target environment: `web`, `node`, `worker`, `web,worker` |
| `-sASSERTIONS=1` | Include runtime assertions (default at -O0) |
| `-sSTACK_OVERFLOW_CHECK=1` | Check for stack overflow (default at -O0) |
| `-sSAFE_HEAP=1` | Runtime bounds checking on all memory accesses |
| `-sLTO=1` | Enable link-time optimization |
| `-sWASM_BIGINT=1` | Use BigInt for 64-bit integer handling |
| `-sEXIT_RUNTIME=1` | Allow runtime shutdown when main() completes |
| `-sINVOKE_RUN=0` | Don't auto-call main() at startup |
| `-sNO_EXIT_RUNTIME=1` | Keep runtime alive after main() (default) |
| `-sERROR_ON_MISSING_LIB_deps=1` | Error if library deps are missing |
| `-sRETAIN_COMPILER_SETTINGS=1` | Allow runtime access to compiler settings |
| `-sSTRICT=1` | Enable strict mode in output JS |

## Output Formats

### HTML Output (`-o app.html`)

Generates three files: `app.html`, `app.js`, `app.wasm`. The HTML shell includes a `<canvas>` element and loads the JS. Use `--shell-file` to provide a custom HTML template.

### JavaScript Output (`-o app.js`)

Generates `app.js` and `app.wasm`. No HTML is produced — you must create your own page that loads the JS and handles the `Module` object.

### WASM-Only Output (`-o app.wasm`)

Generates only the WebAssembly binary. No JavaScript glue code is produced. Useful for embedding in custom runtimes or for use with WASI.

### Modularize (`-sMODULARIZE=1`)

Wraps the output in a factory function. The JS file exports a function that returns a Promise resolving to the `Module` instance:

```javascript
// In browser
const createModule = require('./app.js');
createModule({
  print: (text) => console.log(text),
  onRuntimeInitialized: () => {
    console.log('Runtime ready');
    Module._my_function();
  }
}).then(Module => {
  Module.ccall('my_function', 'number', [], []);
});

// In Node.js
const createModule = require('./app.js');
createModule().then(Module => {
  // use Module
});
```

## Optimization Levels

| Level | Description |
|-------|-------------|
| `-O0` | No optimizations. Default. Includes assertions. Use for initial porting. |
| `-O1` | Simple optimizations. Removes some assertions. |
| `-O2` | More optimizations. JavaScript optimization enabled. Good balance. |
| `-O3` | Aggressive optimizations. Best for release builds. |
| `-Os` | Optimize for size. Trades speed for smaller output. |
| `-Oz` | Aggressive size optimization. Maximum size reduction. |
| `-Og` | Like `-O1` but preserves variable liveness for debugging. |

Optimization applies to both LLVM compilation and Binaryen (Wasm) + JS optimization at link time.

## Debug and Source Maps

```bash
# Basic debug info
emcc -g source.c -o app.js

# Source maps (requires -g on source files too)
emcc -gsource-map source.c -o app.js    # produces app.wasm.map

# Inline sources in source map (larger but self-contained)
emcc -gsource-map=inline source.c -o app.js

# Separate DWARF debug file
emcc -gseparate-dwarf source.c -o app.js  # produces app.debug.wasm

# Profiling (function names in output)
emcc --profiling -O3 source.c -o app.js

# Profiling but minified (names only, no whitespace)
emcc --profiling-funcs -O3 source.c -o app.js
```

## Exporting Functions

Functions must be explicitly exported, or they are eliminated as dead code.

```bash
# Export specific functions (underscore prefix required)
emcc app.c -sEXPORTED_FUNCTIONS='["_main","_process","_render"]' -o app.js

# Export runtime methods needed by your JS code
emcc app.c -sEXPORTED_RUNTIME_METHODS='["ccall","cwrap","UTF8ToString","setValue","getValue"]' -o app.js

# Use EMSCRIPTEN_KEEPALIVE in source to auto-export
```

In C/C++ source:
```c
#include <emscripten.h>

// Auto-export without command-line flag
EMSCRIPTEN_KEEPALIVE
void my_function() {
    // ...
}
```

## MODULARIZE

When `-sMODULARIZE=1` is used, the output becomes a factory function:

```javascript
// app.js exports a function
var moduleFactory = function(moduleOverrides) {
  // ... initialization ...
  return instance; // Promise or direct Module
};
```

This prevents global namespace pollution and allows multiple instances. Always use MODULARIZE with Closure Compiler (`--closure 1`).

## Memory Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `INITIAL_MEMORY` | 16MB | Initial Wasm linear memory size |
| `MAXIMUM_MEMORY` | 4GB | Maximum Wasm memory (must be power of 2, max 4GB in 32-bit) |
| `ALLOW_MEMORY_GROWTH` | 0 | Allow memory to grow beyond INITIAL_MEMORY |
| `MEMORY64` | 0 | Use 64-bit addresses (experimental) |
| `GLOBAL_BASE` | 0 | Base address for global data |
| `STACK_SIZE` | 5MB | Size of the C/C++ stack |

```bash
# Set initial memory to 64MB
emcc app.c -sINITIAL_MEMORY=67108864 -o app.js

# Allow memory growth (enables dynamic memory resizing)
emcc app.c -sALLOW_MEMORY_GROWTH -o app.js

# Set both
emcc app.c -sINITIAL_MEMORY=33554432 -sMAXIMUM_MEMORY=2147483648 -o app.js
```

Memory is allocated in pages of 64KB. Values must be multiples of 65536.

## CMake Integration

Use `emcmake cmake` to configure the CMake toolchain:

```bash
# Configure
emcmake cmake -B build -DCMAKE_BUILD_TYPE=Release

# Build
emmake cmake --build build

# Or directly
emmake make -C build
```

For CMake cache variables, set Emscripten flags via `CMAKE_C_FLAGS` and `CMAKE_CXX_FLAGS`:

```cmake
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -lembind -O3")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -sEXPORTED_RUNTIME_METHODS=ccall,cwrap")
```

Or use a `CMakeLists.txt` approach:

```cmake
target_link_options(myapp PRIVATE
  "SHELL:-sEXPORTED_FUNCTIONS=[\"_main\",\"_my_func\"]"
  "SHELL:-lembind"
  "SHELL:-sMODULARIZE=1"
)
```

## Important Settings Reference

### Filesystem Settings

| Setting | Description |
|---------|-------------|
| `FILESYSTEM` | `1` (default, auto-detect) or `0` (disable entirely) |
| `FORCE_FILESYSTEM` | Force inclusion of full JS FS API even if C/C++ doesn't use files |
| `WASMFS` | Use WasmFS (Wasm-based filesystem, replaces JS FS) |
| `NODEFS` | Include NODEFS library (Node.js host filesystem access) |
| `IDBFS` | Include IDBFS library (IndexedDB persistence) |
| `WORKERFS` | Include WORKERFS library (read-only worker filesystem) |
| `PROXYFS` | Include PROXYFS library (share another module's filesystem) |

### Threading Settings

| Setting | Description |
|---------|-------------|
| `PTHREAD_POOL_SIZE` | Pre-create pool of workers (e.g., `4` or `navigator.hardwareConcurrency`) |
| `PROXY_TO_PTHREAD` | Run `main()` on a worker thread instead of main browser thread |
| `MAXIMUM_PTHREADS` | Maximum number of pthreads (default 10) |
| `PTHREAD_POOL_STATIC` | Use static pool (no dynamic worker creation) |

### Async Settings

| Setting | Description |
|---------|-------------|
| `ASYNCIFY` | Enable Asyncify for pseudo-synchronous async calls |
| `ASYNCIFY_IMPORTS` | List of JS imports that may suspend (e.g., `["fetch_data"]`) |
| `ASYNCIFY_STACK_SIZE` | Stack size for Asyncify (default 5MB) |
| `ASYNCIFY_IGNORE_INDIRECT` | Ignore indirect calls in Asyncify analysis (smaller output) |
| `JSPI` | Enable JavaScript Promise Integration (experimental alternative to Asyncify) |

### Runtime Settings

| Setting | Description |
|---------|-------------|
| `MODULARIZE` | Wrap output as factory function |
| `ENVIRONMENT` | Target: `web`, `node`, `worker`, `web,worker` |
| `EXIT_RUNTIME` | Allow runtime shutdown (default 0) |
| `INVOKE_RUN` | Auto-call main() (default 1) |
| `WASM` | `1` (Wasm, default), `2` (Wasm + asm.js fallback), `0` (asm.js only) |
| `SUPPORT_LONGJMP` | Support setjmp/longjmp (`wasm` or `c`) |

### Library Inclusion

Some features require explicit library inclusion:

```bash
# IDBFS (IndexedDB persistence)
emcc app.c -lidbfs.js -o app.js

# NODEFS (Node.js filesystem)
emcc app.c -lnodefs.js -o app.js

# WORKERFS
emcc app.c -lworkerfs.js -o app.js

# PROXYFS
emcc app.c -lproxyfs.js -o app.js

# Embind
emcc app.cpp -lembind -o app.js
```
