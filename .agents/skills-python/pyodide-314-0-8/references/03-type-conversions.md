# Type conversions

## Contents

- Where translations occur
- Round-trip guarantees
- Implicit conversions
- Proxying (JsProxy, PyProxy)
- Explicit conversion (`toJs`, `to_py`)
- Functions and callbacks
- Buffers
- Errors

## Where translations occur

Python → JavaScript translations occur when: returning the final expression
from `runPython`; importing Python objects into JS (`pyimport`,
`globals.get`); passing arguments to a JS function called from Python;
returning results of a Python function called from JS; accessing an attribute
of a PyProxy.

JavaScript → Python translations occur when: importing from the `js` module;
passing arguments to a Python function called from JS; returning results of a
JS function called from Python; accessing an attribute of a JsProxy.

**Any Python→JS translation may create a `PyProxy` — store it and `destroy()`
it when done, or declare it with `using`, or return `to_js(value)` from Python
so the JS side needs no cleanup.**

## Round-trip guarantees

- Python → JS → Python gives an object equal to the original; if proxied, the
  round trip is `is` the original object (same memory address).
- JS → Python → JS gives `===` the original; if proxied, it unwraps to the
  same object.

## Implicit conversions

Immutable types convert implicitly; mutable types are proxied so both sides
can modify the same object. `tuple` and `bytes` have no JS equivalent, so they
are proxied to keep round-trips type-stable.

### Python → JavaScript

| Python | JavaScript |
|---|---|
| `int` | `Number`, or `BigInt` if abs value > `Number.MAX_SAFE_INTEGER` (lossy `Number` if the browser lacks BigInt) |
| `float` | `Number` |
| `str` | `String` |
| `bool` | `Boolean` |
| `None` | `undefined` |
| `pyodide.ffi.jsnull` | `null` |
| `pyodide.ffi.JsBigInt` | `BigInt` |

### JavaScript → Python

| JavaScript | Python |
|---|---|
| `Number` | `int` if integral and abs value <= `Number.MAX_SAFE_INTEGER`, else `float` |
| `BigInt` | `pyodide.ffi.JsBigInt` |
| `String` | `str` |
| `Boolean` | `bool` |
| `undefined` | `None` |
| `null` | `pyodide.ffi.jsnull` |

## Proxying

### JsProxy (JS object into Python)

Supported operations (each only if the proxied object supports it):

| Python | JavaScript |
|---|---|
| `str(proxy)` / `repr(proxy)` | `x.toString()` |
| `proxy.foo` / `proxy.foo = bar` / `del proxy.foo` | `x.foo` / `x.foo = bar` / `delete x.foo` |
| `hasattr(proxy, "foo")` | `"foo" in x` |
| `proxy(...)` / `proxy.foo(...)` | `x(...)` / `x.foo(...)` |
| `proxy.new(...)` | `new X(...)` |
| `len(proxy)` | `x.length` or `x.size` |
| `foo in proxy` | `x.has(foo)` or `x.includes(foo)` |
| `proxy[foo]` / `proxy[foo] = bar` / `del proxy[foo]` | `x.get(foo)` / `x.set(foo, bar)` / `x.delete(foo)` |
| `proxy1 == proxy2` | `x === y` |
| `proxy.typeof` | `typeof x` |
| `iter` / `aiter` / `next` / `anext(proxy)` | `x[Symbol.iterator]()` / `x[Symbol.asyncIterator]()` / `x.next()` |
| `await proxy` | `await x` |
| `proxy.__exit__()` / `proxy.__aexit__()` | `x[Symbol.dispose]()` / `x[Symbol.asyncDispose]()` |

- `dir(proxy)` returns all keys on the prototype chain.
- A JsProxy is a context manager if the object has `[Symbol.dispose]()` (and
  async context manager with `[Symbol.asyncDispose]()`).
- **Array-like special case**: JS `Array` and array-like objects (iterable with
  a `length` field, e.g. `HTMLCollection`, `NodeList`) translate `proxy[idx]`
  → `array[idx]`, `idx in proxy` → `idx in array`, `del proxy[idx]` →
  `array.splice(idx)`.
- Access JS fields via `obj.field_name` or `getattr(obj, "field name")`; for
  map-style access use `proxy.as_py_json()` (returns a dict).
- **Python keyword mangling**: `Array.from` → `Array.from_`; a JS attribute
  literally ending in underscore needs a second (`o.from__`). `dir` reflects
  the mangled names. Alternatively `getattr`/`setattr`/`delattr` with the real
  name works on both proxies and the `js` module.

### PyProxy (Python object into JavaScript)

| JavaScript | Python |
|---|---|
| `proxy.toString()` | `str(x)` |
| `foo in proxy` | `hasattr(x, 'foo')` |
| `proxy.foo` / `proxy.foo = bar` / `delete proxy.foo` | `x.foo` / `x.foo = bar` / `del x.foo` |
| `Object.getOwnPropertyNames(proxy)` | `dir(x)` |
| `proxy(...)` / `proxy.foo(...)` | `x(...)` / `x.foo(...)` |
| `proxy.length` | `len(x)` |
| `proxy.has(foo)` / `proxy.get(foo)` / `proxy.set(foo, bar)` / `proxy.delete(foo)` | `foo in x` / `x[foo]` / `x[foo] = bar` / `del x[foo]` |
| `proxy.type` | `type(x)` |
| `proxy[Symbol.iterator]()` / `proxy[Symbol.asyncIterator]()` | `iter(x)` / `aiter(x)` |
| `proxy.next()` | `next(x)` or `anext(x)` |
| `await proxy` | `await x` |

For a dict PyProxy, `proxy[key]` falls back to dict-item access when no
attribute named `key` exists; properties and attributes take precedence over
keys.

**Memory**: destroy PyProxies when done (`proxy.destroy()`; calling after
destroy raises `Error: Object has already been destroyed`). With modern JS
runtimes, `using proxy = ...` cleans up at end of scope.

## Explicit conversion

### `PyProxy.toJs()` / `pyodide.ffi.to_js()`

Deep by default; `toJs({depth: 1})` for shallow. Beyond normal conversions:

| Python | JavaScript |
|---|---|
| `list`, `tuple` | `Array` |
| `dict` | `Object` (or pass `dict_converter`, e.g. `Object.fromEntries`) |
| `set` | `Set` |
| a buffer (`bytes`, numpy arrays, ...) | `TypedArray` |

Options: `pyproxies: []` collects any proxies created for later destruction;
`create_pyproxies: false` raises `ConversionError` where a proxy would be made
(asserts full conversion). JS `Set`/`Map` key identity semantics differ from
Python's deep-equality keys — ambiguous keys raise `ConversionError`.

### `JsProxy.to_py()`

Deep by default; `to_py(depth=1)` for shallow.

| JavaScript | Python |
|---|---|
| `Array` | `list` |
| `Object`* | `dict` |
| `Map` | `dict` |
| `Set` | `set` |

\* Only when the constructor is exactly `Object` (plain objects); class
instances are left alone. JS `true`/`1` as distinct map keys raises
`ConversionError` since a Python dict cannot hold both.

## Functions and callbacks

### Python called from JS

- Arguments translate JS→Python; return value translates Python→JS. If the
  return is a PyProxy you must destroy it. To avoid the leak entirely, return
  `to_js(value)` from the Python function.
- Keyword arguments from JS: use `proxy.callKwargs(args, {key: value})` — the
  last argument is the kwargs object.

### JS called from Python

- **Keyword arguments are combined into one JS object passed as the final
  argument**: `f(a=2, b=3)` calls the JS function with a single object
  `{a: 2, b: 3}`. This is why `js.fetch(url, {options-dict})` with a plain
  dict does not behave like JS — the options must arrive as the final argument
  (e.g. build it with `to_js({...}, dict_converter=Object.fromEntries)` or
  pass kwargs through).
- If the return is not a `Promise`/`Generator`/`AsyncGenerator`, any PyProxies
  created during argument conversion are destroyed after the call. So to
  persist a PyProxy as a callback, wrap with `create_proxy` (many calls) or
  `create_once_callable` (single call).
- If the return is a `Promise`, the Python call returns an `asyncio.Future`;
  arg proxies are kept alive until the promise resolves. Generators/AsyncGenerators keep args alive until exhausted or `JsGenerator.close()`.

## Buffers

### JS TypedArrays from Python

JS `ArrayBuffer`/`TypedArray` objects outside the WASM heap are proxied; use
`proxy.to_py()` to get a Python `memoryview`, then e.g. `np.asarray`. Write
back with `JsBuffer.assign` / `assign_to` (requires matching dtype, matching
total length, contiguous Python buffer).

### Python buffers from JS

- `PyProxy.toJs()` — copies the buffer into JS (prefer for simple cases).
  0/1-d buffers become a single TypedArray (format `'s'` → string, `'?'` →
  boolean array); higher-dim become nested arrays.
- `PyBuffer.getBuffer()` — low-level reference into WASM memory with
  `data`, `shape`, `strides`, `offset`, `readonly` metadata; **call
  `buffer.release()` when done** (or use `using`). Use this for large
  bitmapped image data where `toJs()` would be very slow.

## Errors

- JS errors are wrapped in `pyodide.ffi.JsException`; Python exceptions become
  `pyodide.ffi.PythonError` in JS.
- `PythonError` carries a formatted traceback but **no reference to the
  original Python exception** (to avoid leaking the stack frame). The actual
  exception is in `sys.last_value`.
- To reformat tracebacks (e.g. filter frames), define a Python helper using
  `sys.last_type`/`last_value`/`last_traceback` + `traceback.format_exception`,
  call it from JS `catch`, and replace `e.message`.
- If you proxy `sys.last_value`, destroy that PyProxy promptly — it can leak
  the whole stack frame.
