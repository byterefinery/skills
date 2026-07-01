# Asyncify and Pthreads — Emscripten 6.0.1

## Table of Contents

- [Asyncify Overview](#asyncify-overview)
- [Asyncify Usage](#asyncify-usage)
- [Asyncify API Patterns](#asyncify-api-patterns)
- [JSPI (JavaScript Promise Integration)](#jpi-javascript-promise-integration)
- [Asyncify with Dynamic Linking](#asyncify-with-dynamic-linking)
- [Asyncify with Embind](#asyncify-with-embind)
- [Asyncify Optimization](#asyncify-optimization)
- [Asyncify Pitfalls](#asyncify-pitfalls)
- [Pthreads Overview](#pthreads-overview)
- [Pthreads Compilation](#pthreads-compilation)
- [Pthreads Gotchas](#pthreads-gotchas)
- [Proxying](#proxying)
- [Blocking on Main Thread](#blocking-on-main-thread)
- [Allocator Performance](#allocator-performance)

## Asyncify Overview

Asyncify lets synchronous C/C++ code interact with asynchronous JavaScript. It automatically transforms compiled Wasm so it can be paused and resumed, enabling:

- Synchronous-looking calls that yield to the event loop
- Synchronous C code that waits for async JS operations (fetch, timers, etc.)

Two mechanisms:
- **Asyncify** (`-sASYNCIFY`) — Works in most environments, increases Wasm size
- **JSPI** (`-sJSPI`) — Uses VM's JavaScript Promise Integration, same code size, experimental

## Asyncify Usage

```bash
# Enable Asyncify (always use with -O3)
emcc app.c -O3 -sASYNCIFY -o app.js

# With specific imports that may suspend
emcc app.c -O3 -sASYNCIFY -sASYNCIFY_IMPORTS='["fetch_data","my_async_func"]' -o app.js
```

### Basic Sleep Example

```c
#include <emscripten.h>
#include <stdio.h>

int main() {
    printf("before sleep\n");
    emscripten_sleep(100);  // Yields to event loop for 100ms
    printf("after sleep\n");
    return 0;
}
```

### Waiting for Async JS

```c
#include <emscripten.h>

// Timer check via EM_JS
EM_JS(void, start_timer, (), {
    Module.timer = false;
    setTimeout(function() { Module.timer = true; }, 500);
});

EM_JS(bool, check_timer, (), {
    return Module.timer;
});

int main() {
    start_timer();
    while (1) {
        if (check_timer()) {
            printf("timer happened!\n");
            break;
        }
        emscripten_sleep(100);  // Yield to event loop
    }
    return 0;
}
```

## Asyncify API Patterns

### EM_ASYNC_JS (Recommended)

```c
#include <emscripten.h>

EM_ASYNC_JS(int, do_fetch, (const char* url), {
    out("fetching " + UTF8ToString(url));
    const response = await fetch(UTF8ToString(url));
    const text = await response.text();
    out("got response");
    return 42;
});

int main() {
    int result = do_fetch("http://example.com");
    printf("result: %d\n", result);  // Runs after fetch completes
    return 0;
}
```

### JS Library with __async Decorator

```javascript
addToLibrary({
    fetch_data__async: 'auto',
    fetch_data: async (url) => {
        const response = await fetch(UTF8ToString(url));
        const json = await response.json();
        return stringToNewUTF8(JSON.stringify(json));
    },
});
```

`__async: 'auto'` — Automatically suspends Wasm and handles the async wrapper.
`__async: 1` — Just marks as async import (manual Asyncify API needed).

### Asyncify.handleAsync (Promise-based)

```c
EM_JS(int, do_fetch, (), {
    return Asyncify.handleAsync(function() {
        return fetch("http://example.com")
            .then(function(response) {
                return response.text();
            })
            .then(function(text) {
                return 42;
            });
    });
});
```

Must add to `ASYNCIFY_IMPORTS`: `-sASYNCIFY_IMPORTS=do_fetch`

### Asyncify.handleSleep (Callback-based)

```c
EM_JS(int, do_fetch, (), {
    return Asyncify.handleSleep((wakeUp) => {
        fetch("http://example.com")
            .then(function(response) {
                wakeUp(42);  // Resume with return value
            });
    });
});
```

Return value passed to `wakeUp()`, not from the function itself.

### val::await (Embind)

```cpp
#include <emscripten/val.h>

val result = myObject.call<val>("asyncMethod").await();
// No ASYNCIFY_IMPORTS needed — handled automatically
```

### ccall with async

```javascript
// Call async Wasm export from JS
Module.ccall("func", "number", [], [], { async: true })
    .then(result => {
        console.log("result:", result);
    });
```

## JSPI (JavaScript Promise Integration)

JSPI is an experimental alternative to Asyncify using the VM's native promise integration:

```bash
# Use JSPI instead of Asyncify
emcc app.c -O3 -sJSPI -o app.js

# Run with Node.js (requires flag)
node --experimental-wasm-stack-switching a.out.js
```

### Key Differences

| Feature | Asyncify | JSPI |
|---------|----------|------|
| Code size increase | ~50% | None |
| Explicit imports | `ASYNCIFY_IMPORTS` | `JSPI_IMPORTS` |
| Explicit exports | Auto-detected | `JSPI_EXPORTS` |
| Embind return | Promise only if suspends | Always Promise (use `emscripten::async()`) |
| Browser support | Wide | Experimental |

### JSPI with Embind

```cpp
EMSCRIPTEN_BINDINGS(example) {
    // JSPI: always returns Promise
    emscripten::function("delayAndReturn", &delayAndReturn, emscripten::async());
}
```

## Asyncify with Dynamic Linking

When using Asyncify with side modules, imports from linked modules must be listed:

```bash
# Compile side module
emcc sleep.cpp -O3 -o libsleep.wasm -sASYNCIFY -sSIDE_MODULE

# Compile main module (list cross-module async imports)
emcc main.cpp libsleep.wasm -O3 -sASYNCIFY \
    -sASYNCIFY_IMPORTS=sleep_for_seconds -sMAIN_MODULE -o app.js
```

## Asyncify with Embind

### Asyncify (auto-detect)

```cpp
static int delayAndReturn(bool sleep) {
    if (sleep) emscripten_sleep(0);
    return 42;
}

EMSCRIPTEN_BINDINGS(example) {
    emscripten::function("delayAndReturn", &delayAndReturn);
}
```

JS: Returns `Promise` only if the function actually suspends. Otherwise returns value directly.

```javascript
let result = Module.delayAndReturn(false);  // 42 (sync)
let asyncResult = Module.delayAndReturn(true);  // Promise { 42 }
```

### JSPI (always async)

```cpp
EMSCRIPTEN_BINDINGS(example) {
    emscripten::function("delayAndReturn", &delayAndReturn, emscripten::async());
}
```

JS: Always returns `Promise`.

## Asyncify Optimization

Unoptimized Asyncify builds are extremely large. Always use `-O3`:

```bash
emcc app.c -O3 -sASYNCIFY -o app.js
```

### Reducing Overhead

```bash
# Ignore indirect calls (safe if you know indirect calls never suspend)
emcc app.c -O3 -sASYNCIFY -sASYNCIFY_IGNORE_INDIRECT -o app.js

# Remove functions that never suspend
emcc app.c -O3 -sASYNCIFY -sASYNCIFY_REMOVE='["render","update_physics"]' -o app.js

# Add functions that do suspend (beyond detected ones)
emcc app.c -O3 -sASYNCIFY -sASYNCIFY_ADD='["my_suspending_func"]' -o app.js

# Only instrument specific functions
emcc app.c -O3 -sASYNCIFY -sASYNCIFY_ONLY='["fetch_data","save_data"]' -o app.js

# Advise mode: see what's being instrumented and why
emcc app.c -O0 -sASYNCIFY -sASYNCIFY_ADVISE -o app.js
```

### Stack Size

```bash
# Increase Asyncify stack if you get stack overflow errors
emcc app.c -O3 -sASYNCIFY -sASYNCIFY_STACK_SIZE=16777216 -o app.js
```

## Asyncify Pitfalls

### Reentrancy

While waiting on async operations, browser events can fire. If event handlers call into compiled code, execution interleaves like coroutines:

- **Not safe** to start a second async operation while one is already running
- Global state can be modified by event handlers during sleep
- Use `setTimeout(wakeUp, 0)` to defer `wakeUp` and avoid stack interference

### Stack Overflow

If you see exceptions from `asyncify_*` APIs, increase stack size:

```bash
emcc app.c -O3 -sASYNCIFY -sASYNCIFY_STACK_SIZE=16777216 -o app.js
```

### Rewind with Compiled Code on Stack

If `wakeUp()` is called while compiled code is on the stack, later unwinds will break. Workaround: defer with `setTimeout(wakeUp, 0)`.

## Pthreads Overview

Emscripten implements POSIX threads (pthreads) using Web Workers with SharedArrayBuffer. This provides true multithreading with shared memory and atomic operations.

## Pthreads Compilation

```bash
# Enable pthreads (must use -pthread at compile AND link)
emcc app.c -pthread -o app.js

# With worker pool (pre-create workers before main)
emcc app.c -pthread -sPTHREAD_POOL_SIZE=4 -o app.js

# With dynamic pool size
emcc app.c -pthread -sPTHREAD_POOL_SIZE=navigator.hardwareConcurrency -o app.js

# Run main() on a worker (recommended)
emcc app.c -pthread -sPROXY_TO_PTHREAD -o app.js
```

### C/C++ Code

```c
#include <pthread.h>
#include <stdio.h>

void* thread_func(void* arg) {
    printf("Thread running\n");
    return NULL;
}

int main() {
    pthread_t thread;
    pthread_create(&thread, NULL, thread_func, NULL);
    pthread_join(thread, NULL);
    return 0;
}
```

Detect pthreads support: `#ifdef __EMSCRIPTEN_PTHREADS__`

## Pthreads Gotchas

### COOP/COEP Headers Required

SharedArrayBuffer requires these HTTP headers:

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

Without these, SharedArrayBuffer is unavailable and pthreads won't work.

### pthread_create Returns to Event Loop

When `pthread_create()` needs to create a new Web Worker, it returns to the event loop. The worker only starts running after you yield. Solutions:

1. Use `emscripten_set_main_loop()` or Asyncify
2. Use `-sPTHREAD_POOL_SIZE` to pre-create workers
3. Use `-sPROXY_TO_PTHREAD` to run main on a worker

### No POSIX Signals

Signals are not supported (cannot send signals to Web Workers). Exception: `pthread_kill()` works to terminate a thread.

### No fork()/multiprocessing

`fork()` and `vfork()` are not supported.

### Thread Limit (Firefox)

Firefox limits threads to 20 by default. Adjust via `about:config` → `dom.workers.maxPerDomain`.

### Unsupported Features

- Thread prioritization
- `pthread_rwlock_unlock()` in priority order
- `pthread_mutexattr_setprotocol()`, `pthread_mutexattr_setprioceiling()`, `pthread_attr_setscope()` — all no-ops

### Callback Signatures

pthread callbacks must have correct signatures. Omitting the `void*` argument in `pthread_create()` callback causes runtime abort.

## Proxying

Certain operations (DOM access, etc.) can only happen on the main browser thread. Pthreads code on workers must proxy these calls.

### Automatic Proxying

JS library functions marked with `__proxy: 'sync'` or `__proxy: 'async'` are automatically proxied:

- `sync` — Calling thread blocks until main thread completes
- `async` — Returns immediately, JS runs on main thread later

### Manual Proxying (proxying.h)

```c
#include <emscripten/proxying.h>

// Sync proxy (blocks caller)
EM_ASYNC_PROXY(sync, int, my_func, (int x), {
    return x * 2;
});

// Async proxy (fire-and-forget)
EM_ASYNC_PROXY(async, void, my_func, (int x), {
    console.log(x);
});
```

### Proxying + Asyncify

When a function is both `__proxy: 'sync'` and `__async: 'auto'`, it returns a Promise. The calling thread blocks until the Promise resolves. This allows async functions to be called from workers without Asyncify.

## Blocking on Main Thread

The Web API doesn't allow `Atomics.wait` on the main thread. Blocking operations use busy-wait, which can cause:

- Unresponsive browser tab
- Wasted power
- Deadlocks if main thread blocks while workers try to proxy to it

### Solutions

1. **Use `-sPROXY_TO_PTHREAD`** — Runs main() on a worker, leaving main thread free for proxying
2. **Replace blocking calls** — Use `pthread_tryjoin_np` instead of `pthread_join`
3. **Use Asyncify** — Convert blocking to async patterns

### Settings

```bash
# Disallow blocking on main thread (throws error)
emcc app.c -pthread -sALLOW_BLOCKING_ON_MAIN_THREAD=0 -o app.js
```

## Allocator Performance

Default allocator (`dlmalloc`) has a global lock causing contention under multithreading. Use `mimalloc` for better performance:

```bash
# Use mimalloc (better multithreaded performance, larger code size)
emcc app.c -pthread -sMALLOC=mimalloc -o app.js
```

mimalloc has per-thread allocation contexts, scaling better under malloc/free contention. Tradeoff: larger code size and more runtime memory (may need higher `INITIAL_MEMORY`).
