# Python API

## Contents

- JavaScript modules (`js`, `pyodide_js`)
- `pyodide.code`
- `pyodide.ffi`
- `pyodide.http`
- `pyodide.console`
- `pyodide.webloop`
- The Pyodide Python CLI

Backward compatibility of the Python API is not guaranteed.

## JavaScript modules

Two JavaScript modules are importable like normal Python modules; more can be
added with `pyodide.registerJsModule` (JS) or `pyodide.ffi.register_js_module`.

| Module | Scope |
|---|---|
| `js` | The global JavaScript scope (`globalThis` by default, or the `jsglobals` config option). |
| `pyodide_js` | The JavaScript Pyodide module (the JS `pyodide` object). |

```python
import js
js.document.title = "New window title"
from js.document.location import reload as reload_page
reload_page()

# Assigning to JS globals works too
js.x = 2
```

Note: imported functions from `pyodide_js` do not all work until after
`pyodide` has first been imported; `pyodide_js` functions should not be used at
import time. Functions from `js` are fine at import time.

If a name is a Python reserved keyword, use `getattr(js, "lambda")` etc.

## `pyodide.code`

Utilities for evaluating Python and JavaScript code:

- `eval_code(code, ...)` — the sync evaluator behind `pyodide.runPython`
- `eval_code_async(code, ...)` — the async evaluator behind `pyodide.runPythonAsync` (supports top-level await)
- `find_imports(source)` — return the list of packages a code chunk imports (used by `loadPackagesFromImports`)
- `run_js(code)` — evaluate a JavaScript expression from Python
- `relaxed_wrap(func)`, `relaxed_call(func, *args, **kwargs)` — wrappers that translate Python/JS call signatures
- `CodeRunner`, `should_quiet` — helpers for console-like execution

`runPython`/`runPythonAsync` are thin wrappers:

```js
function runPython(code) {
  return pyodide.pyodide_py.code.eval_code(code, pyodide.globals);
}
```

To customize behavior, write your own entrypoint calling `eval_code`
(e.g. to also return extra globals state), rather than monkey-patching.

## `pyodide.ffi`

The `JsProxy` class and utilities to interact with JavaScript:

- `JsProxy` — proxy of a JavaScript object into Python (with `to_py`, `as_py_json`, `typeof`, ...). Subtypes: `JsArray`, `JsAsyncGenerator`, `JsAsyncIterable`, `JsAsyncIterator`, `JsBuffer`, `JsCallable`, `JsCallableDoubleProxy`, `JsDoubleProxy`, `JsException`, `JsFetchResponse`, `JsGenerator`, `JsIterable`, `JsIterator`, `JsMap`, `JsMutableMap`, `JsDomElement`, `JsTypedArray`, `JsWeakRef`, `JsOnceCallable`, `JsPromise`.
- `to_js(obj, ...)` — explicit Python→JS conversion (use on return values from callbacks to avoid leaks). Options include `depth`, `create_pyproxies`, `dict_converter` (e.g. `Object.fromEntries`).
- `create_proxy(fn)` — wrap a Python callable for repeated use from JS (event handlers); destroy when done.
- `create_once_callable(fn)` — wrap for a single call (e.g. `setTimeout` callbacks).
- `destroy_proxies` — destroy a list of proxies.
- `run_sync` — run a coroutine to completion from a sync context.
- `register_js_module`, `unregister_js_module` — Python-side module registration.
- `jsnull` (`JsNull`) — the value that converts to JS `null`.
- `JsBigInt` — an `int` subtype that converts to JS `BigInt`; standard arithmetic supported.
- `ConversionError`, `JsException` — error types (see [03-type-conversions](03-type-conversions.md)).
- `IN_PYODIDE` — `True` when running under Pyodide.

## `pyodide.http`

- `pyfetch(request, *, signal=None, fetcher=None, **kwargs)` — async; convenient `fetch` wrapper. `request` is a URL string or JS `Request`; `**kwargs` are passed as fetch options. Returns a `FetchResponse` whose methods return already-Python-converted types (`.json()`, `.bytes()`, `.text()`, `.unpack_archive()`, ...).
- `pyxhr` — synchronous HTTP via XMLHttpRequest: `get`, `post`, `put`, `delete`, `head`, `patch`, `options`, each taking `**kwargs` (`XHRRequestParams`).

```python
from pyodide.http import pyfetch
resp = await pyfetch("https://some_url/myfiles.zip")
await resp.unpack_archive()  # unpacks to the current directory by default
```

## `pyodide.console`

Similar to the builtin `code` module but handles top-level await; used for
implementing the Pyodide console.

- `Console` / `PyodideConsole` — interactive console classes
- `ConsoleFuture` — future type used by the console
- `redirect_stdin` — `contextlib.redirect_stdin`-style context manager
- `shorten`, `repr_shorten` — output shortening helpers

## `pyodide.webloop`

The Pyodide event loop implementation, automatically configured for most use
cases; unlikely you will need it outside niche cases.

- `WebLoop` — the event loop class (e.g. `WebLoop.create_task`, `call_later`, `call_at`; as of 314.0.8, `create_task` passes arguments through to a configured task factory, and `call_later`/`call_at` with a past delay run the callback as soon as possible rather than raising)
- `_initialize_event_loop` — internal initialization (run when `pyodide` is imported)

## The Pyodide Python CLI

Pyodide ships a `python` CLI that is a drop-in replacement for the native
python CLI (`python -c ...`, `python file.py`, `python -m some.module`).
Primarily useful for testing and experimentation, and for installing Pyodide
Python packages with uv/pip for bundling. Execution is **not sandboxed** — this
Pyodide Python has direct access to the native file system.

- Platform support: Linux, macOS, Windows; requires Node.js >= 20.
- Installation options:
  1. Extract `pyodide-core-v<version>.tar.bz2` from GitHub releases (contains the `python` command).
  2. `pyodide-build`: `pyodide venv .venv-pyodide` (if installed via uv, run `uv pip install pip` first — it will not work without pip).
  3. uv: `uv python install cpython-3.14.2-emscripten-wasm32-musl`, then `uv venv .venv-pyodide -p cpython-3.14.2-emscripten-wasm32-musl`.
- Installing packages into a Pyodide venv:
  `uv pip install --no-build --extra-index-url https://index.pyodide.org/314.0.0/ --index-strategy unsafe-best-match <package>`
  (or set `no-build`, `index-strategy = "unsafe-best-match"`, and the index URL in `uv.toml`/`pyproject.toml` — but not in a native Python venv config you also use for regular Python).
