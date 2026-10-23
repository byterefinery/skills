# JavaScript interop

Timing note: JavaScript scripts execute as they load, Brython scripts execute only once the HTML has finished loading — so JS code cannot see Brython data until the page is fully loaded.

## Using JavaScript from Brython

Names in the global JavaScript namespace are attributes of `window` (module `browser`):

```python
from browser import document, window
document["result"].value = window.circle.surface(10)
```

Conversion table (JS → Python):

| JavaScript | Python |
|---|---|
| DOM element | `DOMNode` instance |
| DOM event | `DOMEvent` instance |
| collection of DOM elements | list of `DOMNode` |
| `true` / `false` | `True` / `False` |
| `null` / `undefined` | unchanged — test with `is` against `javascript.NULL` / `javascript.UNDEFINED` |
| number (Number) | `int` or `float` |
| BigInt | `int` |
| string | `str` |
| array | unchanged (items converted with this table) |
| function | unchanged (Python args are converted on the way in) |
| other objects | `javascript.JSObject` instance |

Other JS objects become `javascript.JSObject`; convert to a dict with `window.js_obj.to_dict()`.

Rules and traps:

- **No keyword arguments for JS functions** — `window.foo(y=0, x=1)` raises `TypeError`; pass positionally (Brython doesn't know the JS signature). Python dicts passed as arguments are converted to JS objects with string keys.
- **Constructors via `new`** — a JS function usable with `new` is called as `window.Rectangle.new(10, 10, 30, 30)`.
- **Errors** — an error in called JS code raises `JavascriptError`, catchable from Brython; the JS trace goes to `sys.stderr`.

### The `javascript` module

- `import_js(url, alias=None)` — import a JS file; the file must define `$module`, whose attributes become the module namespace. Default alias is derived from the url.
- `import_modules([urls], callback)` — import ES modules; `callback` is called with one argument per module.
- `JSObject` — class of JS objects used from Python (`isinstance(window.jsobj, javascript.JSObject)`).
- `py2js(src)` — return the JavaScript code Brython generates from Python source `src`.
- `this()` — return the Brython object matching the JS `this` value (useful inside JS-framework callbacks).
- JS globals exposed as names: `Date` (constructor, e.g. `Date.new(2012, 6, 10)`), `JSON` (`stringify`, `parse`), `Math`, `NULL`, `Number`, `RegExp` (`RegExp.new(r"^test(\d+)$")`, `exec` works on Python strings), `String` (needed for methods that take JS regexes, e.g. `String.new("test33").search(re)`), `UNDEFINED`.

### jQuery example

```python
from browser import window
jq = window.jQuery

def onSuccess(data, status, req):
    print(data)

jq.ajax('/cgi-bin/post_test.py', {'data': {'foo': 56}, 'success': onSuccess})
jq('#sel').append('<option>three')
assert jq('#c').attr('id') == 'c'

def callback(ev):
    print(jq(ev.target).text())
jq('#btn').on('click', callback)

def show(i, obj):
    print(i, obj)
jq.each(jq('span'), show)
```

### Wrapping a library in a Python module

`browser.load(script_url)` loads a JS library by blocking Ajax (use it when you can't add a `<script src>` tag); names the library adds to the JS namespace then become attributes of `window`. Define a Python module that does this once, e.g. `jquery.py`:

```python
from browser import window, load
load("/path/to/jquery.min.js")
jq = window.jQuery
```

then any Brython page can just `import jquery` without loading the library in the HTML.

## Using Brython from JavaScript

By default only two names exist in the JS namespace: `brython()` and the internal `__BRYTHON__` object. A JS `onclick="echo()"` cannot call a Brython function. Options:

- give the element an `id` and bind the event from Python (recommended);
- or expose the function with `window.echo = echo` — works, but risks name clashes with JS code in the page (not recommended).

`__BRYTHON__` methods for JS code:

- `whenReady` — a Promise resolved when Brython is loaded and usable
- `getPythonModule(module_name)` — the JS object of an imported Python module (for page scripts, `module_name` is the script's `id`); wait for the script's `load` event before using it
- `pythonToJS(src[, script_id])` — JS translation of Python source (runnable via `eval()`)
- `pythonToAST(src[, filename, mode])` — AST of Python source as a JS object (structure per the Python `ast` docs)
- `runPythonSource(src[, attributes])` — execute Python source as a script; `attributes` is the script `id` or a JS object of execution options (`pythonpath`, `debug`, ...); returns the module object
- `importPythonModule(module_name[, attributes])` — import a module, returns its JS object
- `pyobj2jsobj(pyobj)` — convert a Python object to JS per the conversion table
