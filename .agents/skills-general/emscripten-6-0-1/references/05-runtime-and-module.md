# Runtime and Module — Emscripten 6.0.1

## Table of Contents

- [Module Object](#module-object)
- [Lifecycle Hooks](#lifecycle-hooks)
- [Module Properties](#module-properties)
- [Runtime Initialization](#runtime-initialization)
- [Dynamic Linking](#dynamic-linking)
- [Module Splitting](#module-splitting)
- [Standalone WASM](#standalone-wasm)
- [Running with emrun](#running-with-emrun)
- [Local Development Server](#local-development-server)

## Module Object

`Module` is a global JavaScript object that controls Emscripten runtime behavior. Properties must be set **before** the runtime starts — changes after initialization are ignored.

### Creating Module

```javascript
// For JS-only output (no HTML)
var Module = {
    'print': function(text) { console.log('stdout:', text); },
    'printErr': function(text) { console.error('stderr:', text); },
    'onRuntimeInitialized': function() {
        console.log('Runtime ready, can call functions now');
    }
};
```

For HTML output, extend the existing Module:

```javascript
// In --pre-js file
Module['print'] = function(text) { alert('stdout: ' + text); };
```

With Closure Compiler, always use quoted property names: `Module['print']` not `Module.print`.

## Lifecycle Hooks

### preInit

Called before global initializers run, after basic JS runtime initialization. Use for filesystem setup that must happen before C++ static constructors.

```javascript
Module.preInit = function() {
    // Set up filesystem before anything else
    FS.mkdir('/data');
};

// Or array of functions
Module.preInit = [
    function() { FS.mkdir('/data'); },
    function() { /* more setup */ }
];
```

### preRun

Called right before `main()`, after global initializers and environment setup. Most common place for filesystem operations.

```javascript
Module.preRun = function() {
    FS.mkdir('/working');
    FS.writeFile('/working/input.txt', 'hello');
};
```

### onRuntimeInitialized

Called when the runtime is fully ready — Wasm compiled, files preloaded, etc. Safe to call exported functions.

```javascript
Module.onRuntimeInitialized = function() {
    // Safe to call compiled functions
    Module._my_function();
    Module.ccall('another_func', 'number', [], []);
};
```

### postRun

Called after `main()` returns.

```javascript
Module.postRun = function() {
    console.log('main() completed');
};
```

### onAbort

Called on abnormal termination (abort(), fatal startup errors, etc.). Cannot prevent termination.

```javascript
Module.onAbort = function(reason) {
    console.error('Aborting:', reason);
};
```

## Module Properties

### Execution Control

| Property | Description |
|----------|-------------|
| `arguments` | Array of command-line arguments for `argc`/`argv` |
| `noExitRuntime` | `true` = keep runtime alive after `main()` (default) |
| `noInitialRun` | `true` = don't auto-call `main()` |
| `INVOKE_RUN` | Set to `0` at compile time to skip auto-run |

### I/O

| Property | Description |
|----------|-------------|
| `print(text)` | Called for stdout output |
| `printErr(text)` | Called for stderr output |
| `printWithColors` | `true`/`false`/unset — control colored output (sanitizers) |

### File Handling

| Property | Description |
|----------|-------------|
| `locateFile(path, prefix)` | Return URL for loading `.wasm`, `.data`, `.mem` files |
| `logReadFiles` | If set, log file reads to stderr |
| `getPreloadedPackage(name, size)` | Manual control of `.data` file downloads |

### Memory

| Property | Description |
|----------|-------------|
| `buffer` | Custom `ArrayBuffer`/`SharedArrayBuffer` (WASM=0 only) |
| `wasmMemory` | Custom `WebAssembly.Memory` instance |
| `fetchSettings` | Settings for fetching Wasm module (default `{ credentials: 'same-origin' }`) |

### WASM Instantiation

| Property | Description |
|----------|-------------|
| `instantiateWasm(imports, successCallback)` | Custom Wasm instantiation |
| `mainScriptUrlOrBlob` | URL or blob for pthread/WASM worker to load main module |

### locateFile Example

```javascript
Module['locateFile'] = function(path, prefix) {
    if (path.endsWith('.wasm')) return 'https://cdn.example.com/' + path;
    if (path.endsWith('.data')) return 'https://cdn.example.com/' + path;
    return prefix + path;
};
```

### Custom Wasm Instantiation

```javascript
Module.instantiateWasm = function(imports, successCallback) {
    WebAssembly.instantiate(wasmBinary, imports).then(function(result) {
        successCallback(result.instance, result.module);
    });
    return {};
};
```

## Runtime Initialization

### Startup Sequence

1. `Module` object is read
2. `preInit` hooks run
3. Wasm module is compiled and instantiated
4. Memory is initialized
5. Global initializers run (C++ static constructors)
6. `preRun` hooks run
7. File preloading completes
8. `main()` is called (unless `noInitialRun`)
9. `onRuntimeInitialized` fires
10. `postRun` hooks run (after `main()` returns)

### When to Call Functions

- **Before `onRuntimeInitialized`**: Functions may not be available
- **After `onRuntimeInitialized`**: All functions are safe to call
- **Alternative**: Wait for `main()` to be called, or use `Module.callMain(args)` to call it manually

### Manual main() Invocation

```javascript
// Don't auto-run main
var Module = { noInitialRun: true };

// Later, when ready
Module.callMain(['arg1', 'arg2']);
// Or
Module.callMain();
```

## Dynamic Linking

### Side Modules (Dynamic Libraries)

```bash
# Compile as side module
emcc library.cpp -O3 -o libmylib.wasm -sSIDE_MODULE -sEXPORTED_FUNCTIONS='["_my_func"]'

# Compile main module that loads it
emcc main.cpp -O3 -sMAIN_MODULE=1 -o app.js
```

### dlopen at Runtime

```c
#include <dlfcn.h>

void* handle = dlopen("libmylib.wasm");
if (handle) {
    void (*my_func)() = dlsym(handle, "my_func");
    my_func();
    dlclose(handle);
}
```

### Async dlopen

```c
#include <emscripten.h>

void on_success(void* handle, void* user_data) {
    void (*my_func)() = dlsym((void*)handle, "my_func");
    my_func();
    dlclose((void*)handle);
}

void on_error(void* user_data) {
    const char* err = dlerror();
    printf("Load failed: %s\n", err);
}

emscripten_dlopen("libmylib.wasm", RTLD_NOW, NULL, on_success, on_error);
```

### Precompiling for Synchronous dlopen

With `--use-preload-plugins`, `.so` files are precompiled and can be loaded synchronously with `dlopen`.

## Module Splitting

Split large Wasm modules into smaller pieces loaded on demand:

```bash
# Split into multiple modules
emcc app.cpp -O3 -sMODULARIZE \
    -sLINKABLE \
    --llvm-lto=1 \
    -o app.js
```

## Standalone WASM

Compile to standalone WebAssembly that runs without JavaScript glue:

```bash
# Standalone WASM (WASI-compatible)
emcc app.c -O3 -sSTANDALONE_WASM -o app.wasm
```

Standalone WASM:
- No JavaScript runtime
- No filesystem (unless using WASI)
- No browser APIs
- Can run in any Wasm runtime (WASI, wasmer, wasmtime, etc.)

## Running with emrun

`emrun` is Emscripten's test runner that can run compiled output in browsers or Node.js:

```bash
# Run in default browser
emrun app.html

# Run in specific browser
emrun --browser=chrome app.html

# Run in Node.js
emrun --node app.js

# Run with local web server (needed for XHR/preload)
emrun --no_browser --serve_dir . app.html
```

## Local Development Server

For development with preloaded files, fetch, or SharedArrayBuffer, serve files from a local server:

```bash
# Simple Python server
python3 -m http.server 8000

# With required headers for SharedArrayBuffer (pthreads)
# Use a server that can set COOP/COEP headers

# Node.js with express
# app.js:
# app.use((req, res, next) => {
#   res.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
#   res.setHeader('Cross-Origin-Embedder-Policy', 'require-corp');
#   next();
# });
```

### Nginx Configuration for Pthreads

```nginx
add_header Cross-Origin-Opener-Policy same-origin;
add_header Cross-Origin-Embedder-Policy require-corp;
```

### Common Development Issues

- **Missing headers for pthreads**: SharedArrayBuffer requires COOP/COEP. Without them, `SharedArrayBuffer is undefined`.
- **File not found for preload**: Preloaded `.data` files must be served from the same origin. Use `locateFile` to redirect.
- **CORS errors**: Fetch/XHR to cross-origin URLs requires proper CORS headers on the server.
- **Memory growth + pthreads**: Tricky combination. JS memory accesses slow down. Keep JS-side memory access minimal.
