# Type Conversions

Pyodide translates objects between Python and JavaScript using two strategies:
**implicit conversion** for immutables and **proxying** for mutables.

## Implicit Conversions

### Python → JavaScript

| Python | JavaScript |
|---|---|
| `int` | `Number` (≤ MAX_SAFE_INTEGER) or `BigInt` |
| `float` | `Number` |
| `str` | `String` |
| `bool` | `Boolean` |
| `None` | `undefined` |
| `pyodide.ffi.jsnull` | `null` |
| `pyodide.ffi.JsBigInt` | `BigInt` |

### JavaScript → Python

| JavaScript | Python |
|---|---|
| `Number` | `int` (integer value) or `float` |
| `BigInt` | `pyodide.ffi.JsBigInt` |
| `String` | `str` |
| `Boolean` | `bool` |
| `undefined` | `None` |
| `null` | `pyodide.ffi.jsnull` |

Mutable types (lists, dicts, sets, custom objects) are **never** implicitly converted — they are always proxied.

## Proxying

### JsProxy (JavaScript → Python)

When a JavaScript object enters Python, it becomes a `JsProxy`. The proxy forwards operations to the underlying JS object.

```python
import js

# DOM manipulation
div = js.document.createElement("div")
div.innerHTML = "<h1>Hello</h1>"
js.document.body.prepend(div)

# Array access (special case for arrays)
arr = js.Array.new(1, 2, 3)
arr[0]        # 1
arr[0] = 10   # mutation
len(arr)      # 3
0 in arr      # True

# Map-like objects
obj = js.Object.new()
obj["key"] = "value"
obj.get("key")
"key" in obj
del obj["key"]

# Calling functions
result = js.Math.sqrt(16)

# Constructor
date = js.Date.new()

# Iteration
for item in js.Array.new(1, 2, 3):
    print(item)

# Async iteration
async for item in js_async_iterable:
    print(item)

# Awaiting promises
result = await js_promise

# Context manager (Symbol.dispose)
with js_context_object as x:
    use(x)
```

### Array-like Special Cases

JavaScript arrays and array-like objects (HTMLCollection, NodeList) use bracket notation:

| Python | JavaScript |
|---|---|
| `proxy[idx]` | `array[idx]` |
| `proxy[idx] = val` | `array[idx] = val` |
| `idx in proxy` | `idx in array` |
| `del proxy[idx]` | `array.splice(idx)` |

An object is array-like if it is iterable and has a `length` property.

### Python Keywords on JS Objects

Python reserved words are accessed with trailing underscore:

```python
from js import Array
Array.from_([1, 2, 3])     # Array.from
Array.from__               # Array.from_ (actual underscore property)

obj = js.some_obj
obj.global_                # obj.global
obj.return_                # obj.return
```

Use `getattr` / `setattr` / `delattr` as alternatives:

```python
from_func = getattr(Array, "from")
setattr(obj, "global", "value")
```

### as_py_json

Access JS objects as Python dicts/lists:

```python
from pyodide.code import run_js

obj = run_js("({a: 7, b: {c: 11}})")
mapped = obj.as_py_json()
mapped["a"]           # 7
mapped["b"]["c"]      # 11
```

### PyProxy (Python → JavaScript)

When a Python object enters JavaScript, it becomes a `PyProxy`.

```js
const proxy = pyodide.runPython("[1, 2, 3]"); // auto-converted (immutable result)
const dict = pyodide.globals.get("my_dict");  // PyProxy

// Supported operations
proxy.toString();           // str(x)
"key" in proxy;             // hasattr(x, 'key')
proxy.foo;                  // x.foo
proxy(...);                 // x(...)
proxy.length;               // len(x)
proxy.has("key");           // "key" in x
proxy.get("key");           // x["key"]
proxy.set("key", val);      // x["key"] = val
proxy.delete("key");        // del x["key"]
proxy.type;                 // type(x)
proxy[Symbol.iterator]();   // iter(x)
await proxy;                // await x
```

For dictionaries, `proxy[key]` falls back to dict item access if no attribute exists.

## Explicit Conversion

### PyProxy.toJs() (JavaScript)

```js
// Deep conversion (default)
const jsObj = proxy.toJs();

// Shallow conversion
const jsObj = proxy.toJs({ depth: 1 });

// Collect created proxies for cleanup
let pyproxies = [];
const jsObj = proxy.toJs({ pyproxies });
// use jsObj...
for (let px of pyproxies) px.destroy();
proxy.destroy();

// Fail instead of creating proxies
const jsObj = proxy.toJs({ create_pyproxies: false });

// Custom dict converter
const jsObj = proxy.toJs({ dict_converter: Object.fromEntries });
const jsObj = proxy.toJs({ dict_converter: Map.new });
```

Explicit conversions:

| Python | JavaScript |
|---|---|
| `list`, `tuple` | `Array` |
| `dict` | `Object` (or custom via `dict_converter`) |
| `set` | `Set` |
| buffer | `TypedArray` |

### JsProxy.to_py() (Python)

```python
# Deep conversion (default)
py_obj = js_proxy.to_py()

# Shallow conversion
py_obj = js_proxy.to_py(depth=1)

# Custom converter
def convert_date(value, convert, cache):
    if value.constructor.name == "Date":
        from datetime import datetime
        return datetime.fromtimestamp(value.valueOf() / 1000)
    return value

py_obj = js_proxy.to_py(default_converter=convert_date)
```

Explicit conversions:

| JavaScript | Python |
|---|---|
| `Array` | `list` |
| `Object` (plain) | `dict` |
| `Map` | `dict` |
| `Set` | `set` |

Note: Only plain `Object` instances (constructor is `Object`) are converted to `dict`. Custom class instances remain as proxies.

## Buffers

### JavaScript TypedArrays from Python

```python
from js import Float32Array

jsarray = Float32Array.new([1, 2, 3, 4, 5, 6])

# Convert to memoryview
memory = jsarray.to_memoryview()

# Convert to numpy
import numpy as np
arr = np.asarray(jsarray.to_py()).reshape((2, 3))

# Write back
jsarray.assign(arr)  # copies data back to JS

# Zero-copy write to file
with open("data.bin", "wb") as f:
    jsarray.to_file(f)       # one copy
    jsarray._into_file(f)    # zero copy (buffer consumed)

# Read from file
buf = Float32Array.new(10)
with open("data.bin", "rb") as f:
    buf.from_file(f)          # one copy
```

### Python Buffers from JavaScript

```js
// Simple: copy to JS
const proxy = pyodide.globals.get("numpy_array");
const typedArray = proxy.toJs(); // copies data
proxy.destroy();

// Advanced: zero-copy access via getBuffer
const proxy = pyodide.globals.get("numpy_array");
const buffer = proxy.getBuffer();
proxy.destroy();
try {
  const data = buffer.data;       // TypedArray pointing to WASM memory
  const shape = buffer.shape;     // e.g., [1920, 1080, 4]
  const strides = buffer.strides;
  const offset = buffer.offset;
  const readonly = buffer.readonly;
  // manipulate data...
} finally {
  buffer.release();
}

// Or with explicit resource management:
{
  using proxy = pyodide.globals.get("numpy_array");
  using buffer = proxy.getBuffer();
  // use buffer.data, buffer.shape, etc.
} // auto-cleanup
```

`getBuffer` returns: `{ data: TypedArray, shape: number[], strides: number[], offset: number, readonly: boolean }`.

## Memory Management

### PyProxy Lifecycle

Every Python object returned to JavaScript creates a `PyProxy` that holds a reference to the Python object. **Destroy proxies when done to avoid memory leaks.**

```js
// Manual cleanup
let proxy = pyodide.globals.get("x");
use(proxy);
proxy.destroy();

// Explicit resource management (using keyword)
{
    using proxy = pyodide.globals.get("x");
    use(proxy);
} // auto-destroyed

// toJs with proxy collection
let pyproxies = [];
let result = proxy.toJs({ pyproxies });
use(result);
for (let px of pyproxies) px.destroy();
proxy.destroy();
```

### Python-Side Proxy Creation

```python
# create_proxy: persistent, manual destroy
from pyodide.ffi import create_proxy
proxy = create_proxy(my_func)
document.body.addEventListener("click", proxy)
# later:
document.body.removeEventListener("click", proxy)
proxy.destroy()

# create_once_callable: auto-destroy after first call
from pyodide.ffi import create_once_callable
from js import setTimeout
setTimeout(create_once_callable(my_callback), 1000)

# to_js: convert and auto-manage
from pyodide.ffi import to_js
result = to_js([1, 2, 3])  # JS Array, no cleanup needed
```

Use `to_js` on return values of functions called from JavaScript to prevent leaks without requiring the caller to call `.destroy()`.

## Round-Trip Guarantees

- Python → JS → Python: result `is` the original object (same memory address)
- JS → Python → JS: result `===` the original object (same identity)
- Proxies unwrap on round-trip: converting a proxy back gives the original
