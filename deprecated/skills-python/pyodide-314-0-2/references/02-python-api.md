# Python API Reference

## JavaScript Modules

Two JavaScript modules are available by default via `import`:

| Module | Description |
|---|---|
| `js` | The global JavaScript scope (`globalThis`) |
| `pyodide_js` | The JavaScript Pyodide module (equivalent to `pyodide` returned by `loadPyodide`) |

```python
import js
js.document.title = "New Title"

from js import document, console, fetch, setTimeout

import pyodide_js
await pyodide_js.loadPackage("numpy")
```

Custom modules can be registered from JavaScript with `pyodide.registerJsModule()`.

## pyodide.code

Utilities for evaluating Python and JavaScript code.

### eval_code

```python
from pyodide.code import eval_code
result = eval_code(source, globals=None, locals=None, *, filename="<exec>")
```

Evaluate Python code. If the last statement is an expression (no trailing semicolon), returns its value. Otherwise returns `None`.

### eval_code_async

```python
from pyodide.code import eval_code_async
result = await eval_code_async(source, globals=None, locals=None, *, filename="<exec>")
```

Like `eval_code` but supports top-level `await`.

### find_imports

```python
from pyodide.code import find_imports
imports = find_imports(source)
# Returns list of module names imported in the source
```

### CodeRunner

```python
from pyodide.code import CodeRunner

runner = CodeRunner(
    source,
    mode="exec",           # "exec", "eval", "single"
    filename="<exec>",
    return_mode="last_expr",  # "last_expr", "last_expr_or_assign", "none", "raise"
    flags=0,
    dont_inherit=False,
    optimize=-1,
)
runner.compile()
result = runner.run(globals=None, locals=None)
result = await runner.run_async(globals=None, locals=None)
```

### run_js

```python
from pyodide.code import run_js
result = run_js(code)
```

Execute JavaScript code string and return result. Wrapper around `eval()`.

### should_quiet

```python
from pyodide.code import should_quiet
should_quiet(source)  # True if source ends with semicolon
```

### relaxed_wrap / relaxed_call

```python
from pyodide.code import relaxed_wrap, relaxed_call

@relaxed_wrap
def fn(a, b): return a + b
fn(1, 2, 3, extra=True)  # ignores extra args

relaxed_call(fn, 1, 2, 3, extra=True)
```

Decorators/callers that ignore extra positional and keyword arguments.

## pyodide.ffi

Foreign function interface — types and utilities for JS/Python interop.

### JsProxy Hierarchy

```
JsProxy (base)
├── JsWeakRef[T]         — WeakRef wrapper, .deref()
├── JsDoubleProxy[T]     — Proxy from create_proxy(), .destroy(), .unwrap()
├── JsPromise[T]         — awaitable, .then(), .catch(), .finally_()
├── JsBuffer              — ArrayBuffer/TypedArray, .to_bytes(), .to_memoryview(), .assign()
│   └── JsTypedArray      — TypedArray + JsArray, .subarray()
├── JsIterator[T]        — .__next__()
├── JsAsyncIterator[T]   — .__anext__()
├── JsIterable[T]        — .__iter__()
│   └── JsArray[T]        — Array/NodeList/TypedArray, .push(), .pop(), .to_py()
│   └── JsGenerator       — .send(), .throw(), .close()
├── JsAsyncIterable[T]   — .__aiter__()
│   └── JsAsyncGenerator  — .asend(), .athrow(), .aclose()
├── JsCallable            — callable JS object
├── JsMap[K, V]          — .get(), .keys(), .items(), .values()
│   └── JsMutableMap[K, V] — .pop(), .setdefault(), .update(), .clear()
├── JsOnceCallable        — single-use callable, .destroy()
├── JsCallableDoubleProxy — callable + double proxy
└── JsException           — JS Error, .name, .message, .stack
```

### JsProxy Methods

```python
proxy.to_py(depth=-1, default_converter=None)   # Convert to Python
proxy.new(*args, **kwargs)                       # Constructor call (new X(...))
proxy.to_weakref()                               # Wrap in WeakRef
proxy.object_entries()                           # Object.entries()
proxy.object_keys()                              # Object.keys()
proxy.object_values()                            # Object.values()
proxy.as_py_json()                               # Treat as JSON-like dict/list
proxy.bind_class(Signature)                      # Bind type signature
proxy.bind_sig(Signature)                        # Bind instance signature
proxy.typeof                                    # "object", "function", etc.
proxy.js_id                                     # Unique JS identity number
```

### JsProxy Supported Operations

| Python | JavaScript |
|---|---|
| `str(proxy)` | `x.toString()` |
| `proxy.foo` | `x.foo` |
| `proxy(...)` | `x(...)` |
| `proxy.new(...)` | `new X(...)` |
| `len(proxy)` | `x.length` or `x.size` |
| `foo in proxy` | `x.has(foo)` or `x.includes(foo)` |
| `proxy[foo]` | `x.get(foo)` (maps) or `x[foo]` (arrays) |
| `proxy1 == proxy2` | `x === y` |
| `iter(proxy)` | `x[Symbol.iterator]()` |
| `aiter(proxy)` | `x[Symbol.asyncIterator]()` |
| `await proxy` | `await x` |
| `proxy.__exit__()` | `x[Symbol.dispose]()` |

### Creating Proxies

```python
from pyodide.ffi import create_proxy, create_once_callable, to_js

# Persistent proxy (call many times, must destroy manually)
proxy = create_proxy(my_func, capture_this=False, roundtrip=True)
document.body.addEventListener("click", proxy)
# later:
document.body.removeEventListener("click", proxy)
proxy.destroy()

# One-shot proxy (auto-destroy after first call)
from js import setTimeout
setTimeout(create_once_callable(my_callback), 1000)

# Convert Python to JS
js_obj = to_js({"key": "value"})
js_list = to_js([1, 2, 3])
js_map = to_js({"a": 1}, dict_converter=js.Map.new)
```

### to_js Options

```python
from pyodide.ffi import to_js

result = to_js(
    obj,
    depth=-1,                        # -1 = unlimited, 1 = shallow
    pyproxies=None,                  # JS Array to collect created proxies
    create_pyproxies=True,           # False = raise on unconvertible types
    dict_converter=None,             # e.g., js.Object.fromEntries, js.Map.new
    default_converter=None,          # Fallback converter (value, convert, cache)
    eager_converter=None,            # Called before built-in conversions
)
```

### Other FFI Functions

```python
from pyodide.ffi import (
    destroy_proxies,   # Destroy all proxies in a JS array
    run_sync,          # Run async function synchronously (via stack switching)
    can_run_sync,      # Check if run_sync is available
    register_js_module,  # Register JS module from Python
    unregister_js_module, # Unregister JS module
)

# Special values
from pyodide.ffi import jsnull, JsBigInt, ConversionError, IN_PYODIDE
```

## pyodide.http

HTTP clients for browser/WASM environments.

### pyfetch (Async, Fetch API)

```python
from pyodide.http import pyfetch

resp = await pyfetch("https://example.com/api", method="POST", headers={"Content-Type": "application/json"})

# Response properties
resp.ok           # bool
resp.status       # int (e.g., 200)
resp.status_text  # str
resp.url          # str
resp.type         # str
resp.redirected   # bool
resp.body_used    # bool
resp.headers      # dict[str, str]

# Response body methods
text = await resp.text()
data = await resp.json()
bytes_data = await resp.bytes()
buffer = await resp.buffer()        # JsBuffer (ArrayBuffer)
view = await resp.memoryview()      # memoryview

# Archive extraction
await resp.unpack_archive(extract_dir="/data", format="zip")

# Error handling
resp.raise_for_status()             # Raises HttpStatusError for 4xx/5xx
resp.clone()                        # Clone for multiple reads
resp.abort(reason)                  # Abort the request
```

### pyxhr (Sync, XMLHttpRequest)

```python
from pyodide.http import pyxhr

# Methods: get, post, put, delete, head, patch, options
resp = pyxhr.get("https://example.com/api", headers={"Authorization": "Bearer token"})
resp = pyxhr.post("https://example.com/api", json={"key": "value"})
resp = pyxhr.post("https://example.com/api", data=b"raw data")
resp = pyxhr.get("https://example.com/api", params={"q": "search"})
resp = pyxhr.get("https://example.com/api", auth=("user", "pass"))

# Response properties
resp.status_code   # int
resp.text          # str
resp.content       # bytes
resp.headers       # dict[str, str]
resp.ok            # bool (200-399)
resp.url           # str

# Methods
data = resp.json()
resp.raise_for_status()
```

### Exceptions

```python
from pyodide.http import (
    HttpStatusError,    # 4xx/5xx status codes
    BodyUsedError,      # Body already consumed
    AbortError,         # Request was aborted
    XHRError,           # XMLHttpRequest error
    XHRNetworkError,    # Network error in XHR
)
```

### open_url (Deprecated)

```python
from pyodide.http import open_url
content = open_url("https://example.com/file.txt")  # Returns StringIO
```

## pyodide.console

Interactive console with async support and stream redirection.

### Console

```python
from pyodide.console import Console

console = Console(
    globals=None,                        # Custom namespace dict
    stdin_callback=None,                 # (size: int) -> str
    stdout_callback=None,                # (text: str) -> int | None
    stderr_callback=None,                # (text: str) -> int | None
    persistent_stream_redirection=False, # Keep redirection between calls
    filename="<console>",
    dont_inherit=False,
    optimize=-1,
)

# Push a line
future = console.push("x = 1 + 2")
# future.syntax_check: "complete" | "incomplete" | "syntax-error"
# future.formatted_error: str | None
result = await future

# Complete
completions, start = console.complete("str.isa")
# (['str.isalnum(', 'str.isalpha(', ...], 0)

# Stream management
console.persistent_redirect_streams()
console.persistent_restore_streams()
with console.redirect_streams():
    # streams redirected here
    pass
```

### PyodideConsole

```python
from pyodide.console import PyodideConsole

console = PyodideConsole()
# Auto-loads packages via loadPackagesFromImports before execution
future = console.push("import numpy as np; np.array([1, 2, 3])")
```

### ConsoleFuture

```python
# Returned by console.push() / console.runsource()
future.syntax_check      # "complete" | "incomplete" | "syntax-error"
future.formatted_error   # Formatted traceback string (if error)
```

### Utility Functions

```python
from pyodide.console import shorten, repr_shorten

shorten("very long text...", limit=20, split=8, separator="...")
repr_shorten(obj, limit=1000)
```

## pyodide.webloop

Custom asyncio event loop integrated with the browser.

### WebLoop

```python
from pyodide.webloop import WebLoop, WebLoopPolicy, PyodideFuture, PyodideTask

loop = WebLoop()
# Always running, always open
loop.is_running()   # True
loop.is_closed()    # False
loop.close()        # No-op
loop.run_forever()  # No-op
loop.stop()         # No-op
```

Key methods:

- `loop.create_task(coro)` — Schedule coroutine (returns `PyodideTask`)
- `loop.run_until_complete(future)` — Run via stack switching (if `enableRunUntilComplete`)
- `loop.call_soon(cb, *args)` — Schedule via `setTimeout(cb, 0)`
- `loop.call_later(delay, cb, *args)` — Schedule via `setTimeout`
- `loop.time()` — Monotonic time in seconds
- `loop.create_future()` — Returns `PyodideFuture`
- `loop.shutdown_asyncgens()` — Close all async generators

Unsupported (raises `NotImplementedError`):

- `add_reader` / `add_writer` / `remove_reader` / `remove_writer`
- `create_server`, `create_unix_connection`, `create_unix_server`
- `create_datagram_endpoint`, `start_tls`
- `subprocess_shell`, `subprocess_exec`
- `add_signal_handler`, `remove_signal_handler`

### PyodideFuture

```python
# Extended Future with Promise-like API
future = loop.create_future()

# Promise-style chaining
future.then(on_fulfilled, on_rejected)
future.catch(on_rejected)
future.finally_(on_finally)
```
