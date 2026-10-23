---
name: brython-3-15
description: >
  Brython is an implementation of Python 3 that runs entirely in the web browser,
  translating Python to JavaScript on the fly. Use when writing or debugging
  client-side Python web applications with Brython 3.15 — loading brython.js and
  brython_stdlib.js, manipulating the DOM through the browser package, binding
  events, Ajax requests, async code via browser.aio, timers, web workers,
  templates, dialogs and menus, JavaScript interop, and packaging/deployment
  with brython-cli.
license: MIT
metadata:
  tags:
    - python
    - browser
    - javascript
    - dom
    - client-side
---

# brython 3.15

## Overview

Brython (Browser Python) replaces JavaScript with Python as the scripting language for web browsers. Python code is translated to JavaScript in the browser at page load — there is no server-side Python and no build step. Since 3.8.0, Brython implements the Python version with the same major/minor number, so 3.15 tracks Python 3.15.

A Brython page is an HTML page that loads:

- `brython.js` — the engine (also bundles the `browser`, `browser.html`, and `javascript` modules)
- `brython_stdlib.js` — the pure-Python part of the CPython standard library (only needed if the app imports stdlib modules)

and contains Python in `<script type="text/python">` tags, either inline or via `src="app.py"` (loaded by Ajax, so same-domain only). The browser package gives Pythonic access to the DOM, events, timers, Ajax, web workers, and local storage; the `javascript` module interoperates with JS objects and libraries.

Official 3.15 docs: https://brython.info/static_doc/3.15/en/intro.html — the source tree is the `www` directory of the brython repository (layout in [09-www-repo-layout](references/09-www-repo-layout.md)).

## Usage

Minimal page, no install (CDN):

```xml
<html>
<head>
<script src="https://cdn.jsdelivr.net/npm/brython@3.15/brython.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/brython@3.15/brython_stdlib.js"></script>
</head>
<body>
<script type="text/python">
from browser import document, html

document <= html.H1("Hello from Brython")
</script>
</body>
</html>
```

Common patterns — elements are addressed by their `id` attribute:

```python
from browser import document, bind

# add children — `<=` is a left arrow (attach); `+` adds siblings; `del` removes
document["zone"] <= html.P("line 1") + html.P("line 2")

# event binding (callback gets a DOMEvent)
@bind(document["mybutton"], "click")
def echo(ev):
    print(document["zone"].value)      # goes to the browser console

# CSS selectors
for row in document.select("table#data tr"):
    ...
single = document.select_one(".foo")   # first match or None
```

Serve the page over HTTP for development (imports, `open()`, and external `.py` scripts all rely on Ajax, which is blocked under `file://`):

```bash
python -m http.server 8000
# then open http://localhost:8000/index.html
```

Installation, `brython-cli` subcommands, execution options (`<brython-options>`), and deployment are in [01-install-and-cli](references/01-install-and-cli.md).

## Gotchas

- **No blocking calls** — `time.sleep()` and CPython `asyncio` do not exist in the browser; a JS function cannot pause execution. Use `browser.timer.set_timeout()` / `set_interval()` for callbacks, or `async`/`await` with `browser.aio` (start with `aio.run(main())`).
- **`input()` is simulated** — it wraps the JavaScript `prompt()` dialog. For real input UX use `browser.widgets.dialog.EntryDialog`.
- **`open()` takes a URL, not a path** — the file is fetched by Ajax and must be on the same domain as the page. Writing to disk is impossible in the browser.
- **Pure Python only** — C extensions never run, so `numpy`, `pandas`, `matplotlib`, etc. are out. The `xml` package is absent (CPython's `pyexpat` is C). `requests` and `urllib.request` cannot send arbitrary requests; browsers only allow same-origin (or CORS-enabled) Ajax.
- **`file://` protocol breaks most features** — no external `<script src="app.py">`, no importing local modules, no `open()`. Always develop over `http://`.
- **404 errors in the console are normal** — `import` probes several URLs by Ajax until one matches; the same mechanism produces the "Synchronous XMLHttpRequest deprecated" warning. Both come from blocking Ajax calls, not from your code.
- **Output defaults to the browser console** — `print()` and error messages go there. `sys.stdout.write()` / `sys.stderr.write()` do not print to the console immediately: messages are buffered until `sys.stdout.flush()` / `sys.stderr.flush()` is called. `sys.stdout` and `sys.stderr` can be assigned any object with a `write()` method to redirect output (e.g. to an element).
- **`__del__` is never called** — object lifetime is managed by the JavaScript garbage collector, so do not rely on destructors.
- **Stdlib imports need `brython_stdlib.js`** — without it, `import re` and friends fail with `ImportError`. `brython.js` alone only provides `browser`, `browser.html`, and `javascript`.
- **A `browser.html` instance is a single DOM node** — using the same element variable in two places renders it only at the last one; call `elt.clone()` to duplicate.
- **Attributes and properties are different** — attributes live in the `elt.attrs` dict (values are strings), properties use dot syntax (any type); the property for attribute `class` is `className`. In `browser.html` keyword args, `class` must be written `Class=`, hyphens become underscores (`http_equiv`), and `style=` takes a dict with JavaScript camelCase keys (`backgroundColor`).
- **JavaScript functions cannot be called with keyword arguments** — `window.foo(y=0, x=1)` raises `TypeError`; pass positionally. Call constructors through their `new` method: `window.Rectangle.new(10, 10, 30, 30)`. JS errors surface as catchable `JavascriptError`.
- **`__name__` is the script's `id`** — `if __name__ == "__main__":` only works for the first unnamed script (or one explicitly given `id="__main__"`); other unnamed scripts get a random `__main__…` name, and duplicate `id`s raise an exception.
- **Web worker scripts need `class="webworker"` and a mandatory `id`** — inside a worker there is no `window` or `document`; `browser.self` replaces them for messaging.
- **Template markup uses Brython attributes** — code blocks use `b-code="for ...:"`, shared fragments use `b-include="file.html"`, and event handlers use `b-on="click:fn"`; handlers take `(event, element)` and changes to `element.data` re-render the template.

## References

- [01-install-and-cli](references/01-install-and-cli.md) — CDN and local install, `brython-cli` subcommands, execution options, web servers, deployment, `file://` limitations
- [02-dom-elements](references/02-dom-elements.md) — element access and selectors, attributes vs properties, `browser.html` element construction, operators, `maketag`, `document.query`
- [03-events](references/03-events.md) — `bind`/`unbind`/`events`, `@bind` decorator, `DOMEvent` attributes, mouse/keyboard/drag events
- [04-javascript-interop](references/04-javascript-interop.md) — `javascript` module, JS↔Python conversion, constructors, exposing Python to JS, jQuery example
- [05-ajax-network-storage](references/05-ajax-network-storage.md) — `browser.ajax`, `form_data`, `file_upload`, websockets, local/session/object storage, markdown
- [06-async-timers-workers](references/06-async-timers-workers.md) — `browser.aio`, `browser.timer`, `browser.worker`
- [07-templates-widgets-webcomponents](references/07-templates-widgets-webcomponents.md) — `browser.template`, dialogs, menus, web components, SVG
- [08-stdlib-import-syntax](references/08-stdlib-import-syntax.md) — import mechanism and search paths, module bundling, syntax limitations, `__name__`, how translation works
- [09-www-repo-layout](references/09-www-repo-layout.md) — the `www` directory of the brython repo, docs tree, gallery examples, tutorial, dev server
