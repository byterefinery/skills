# Standard library, imports, syntax behavior

## Import mechanism

`import` works like CPython: for `import X`, the search order is

1. module `X` in the standard library (bundled in `brython_stdlib.js`)
2. `X.py` in the directory of the current page
3. package directory `X/` (with `__init__.py`) next to the page
4. `X.py` in the standard library's `site-packages`
5. package directory `site-packages/X`

Since the browser has no file system, each probe is a (blocking) Ajax call — hence the 404 spam and the synchronous-XHR warnings in the console. Already-executed page scripts can be imported by their `id`.

```xml
<script type="text/python" id="module">
def hello():
    return "world"
</script>

<script type="text/python">
import module
</script>
```

Modules must be UTF-8; an encoding declaration at the top of a file is ignored.

External scripts load with `<script type="text/python" src="app.py">` (Ajax, same domain only). Use `.bry` instead of `.py` if the server would treat `.py` requests as CGI execution.

**Bundling options:**

- `brython_stdlib.js` — the full supported stdlib (>4 MB)
- `brython_modules.js` — `brython-cli make_modules`; only the modules the app actually uses
- `NAME.brython.js` — `brython-cli make_package`; a third-party package loadable with a plain `<script src>` tag

## Standard library coverage

Brython ships the part of CPython's stdlib written in pure Python. C modules were rewritten in JavaScript where needed (`json`, `math`, `random`, `re`, `unicodedata`, ...). Gaps that matter in practice:

- `xml` is **not provided** — CPython's package depends on the C module `pyexpat`
- C extensions of third-party packages never run (`numpy`, `pandas`, `matplotlib`, ...)
- networking is limited to Ajax: `urllib.request` and `requests` cannot reach arbitrary URLs (browser security); same origin or CORS-enabled endpoints only

## Syntax and runtime behavior

- All keywords/builtins of the matching Python 3 version work; `time.sleep()` does not (no blocking) — use `browser.timer`.
- `input()` is simulated with the JS `prompt()` dialog; return value is the entered string (or the `default` argument, else `""`).
- CPython `asyncio` is unavailable; use `browser.aio` instead.
- `open(url)` — URL argument, fetched by Ajax (same domain); supports `read`, `readlines`, `seek`, `tell`, `close`. No writing anywhere.
- `print()` and errors go to the browser console by default. `sys.stdout` / `sys.stderr` can be reassigned to any object with `write()` (e.g. an element) to redirect output; note their `write()` is buffered — call `flush()` for immediate console output.
- `window.print` opens the browser print dialog.
- `__del__` is never called — the JS garbage collector manages lifetimes.
- Generated JS is verbose (roughly 10x the source size); on-the-fly translation plus the IndexedDB compilation cache is faster than precompiling, so no build step is needed.

## `__name__`

Set to the `id` attribute of the `<script>` tag. Rules:

- two scripts with the same `id` → exception
- if no script has `id="__main__"`, the first unnamed script gets `__name__ == "__main__"` (so a single-script page supports the usual `if __name__ == "__main__":` guard)
- other unnamed scripts get a random string starting with `__main__`

## How translation works (sketch)

`brython()` reads each script (Ajax if external), `__BRYTHON__.py2js(source, module)` tokenizes it into a syntax tree, and `to_js()` emits JavaScript that is run via `eval()`. The generated code keeps Python semantics dynamic — attribute access becomes `getattr(obj, "name")`, operators call `__add__`/`__iadd__`/`__getitem__` methods, calls go through `__call__`, keyword args are wrapped in `$Kw(name, value)`, argument binding uses the internal `$MakeArgs`, and classes are built by `$class_constructor` (a factory plus a class-attributes object). Each function gets its own namespace stored in `__BRYTHON__.vars["module-name-random"]`, which is what `globals()`/`locals()` read. See `www/doc/en/implem.md` in the repo for the full Python→JS table.

## Testing and debugging

- The brython.info console/editor (and the site mirror's `console.html`) run snippets in a page namespace that is **not** refreshed between runs — reload the page to reset state.
- The repo's `www/tests/` directory groups the official test pages, reachable from the console's "Test pages" link.
- Syntax errors are always reported in the console/`sys.stderr` with module, line, and source line. Runtime exceptions appear with a CPython-style message at debug level ≥ 1; levels 2/10 additionally dump the generated JavaScript (level 10 includes imported modules).
