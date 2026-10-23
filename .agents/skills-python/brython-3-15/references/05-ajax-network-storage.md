# Ajax, websockets, storage, markdown

## browser.ajax

Concise per-method functions instead of raw XHR.

**Methods without a body** — `get(url, blocking=False, headers={}, mode="text", encoding="utf-8", timeout=None, cache=False, data="", **callbacks)`, and the same interface for `connect`, `delete`, `head`, `options`, `trace`.

**Methods with a body** — `post(url, blocking=False, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=None, data="", **callbacks)`, and the same for `patch`, `put`. If `data` is a dict it is form-encoded and `Content-Length` is computed automatically.

Key parameters: `blocking` (default `False`, i.e. asynchronous), `mode` — `"text"`, `"binary"`, `"json"`, `"document"`, `encoding` (for text), `data` — string, dict, or `form_data()` object, `cache` (default `False`; when false a random parameter is appended to defeat caching), `timeout` in seconds, and `**callbacks` — keys of the form `on` + event name, e.g. `oncomplete=read`.

Callback events: `uninitialized`, `loading`, `loaded`, `interactive`, `complete` (and `timeout`, whose callback takes no argument). In practice only `oncomplete` is usually defined. The callback receives the request object, which exposes:

- `status` — HTTP code (200, 404, ...)
- `text` — response text (`str`, or `bytes` in binary mode; `AttributeError` in json mode)
- `json` — parsed object (json mode)
- `xml` — XML tree (document mode)
- `read()` — read in the mode's format

```python
from browser import ajax

def read(req):
    print(req.text)
ajax.get("test.txt", oncomplete=read)

def read_json(req):
    print(req.json)
ajax.get("test.json", mode="json", oncomplete=read_json)
```

### Standard Web API interface

`ajax.Ajax()` creates a request object with `open(method, url, async)`, `bind(evt, function)`, `send([data])`, plus `encoding`, `responseType`, `withCredentials`, `set_header(name, value)`, `set_timeout(duration, function)`, and all `XMLHttpRequest` properties.

### Form data and file upload

`ajax.form_data([form])` builds a key-value structure (from an HTML `<form>` if given); `form_data.append(name, value[, filename])` follows the Web API `FormData` interface.

`ajax.file_upload(url, file, method="POST", field_name="filetosave", headers=None, timeout=None, data=None, **callbacks)` uploads a file object, e.g. from `document["choosefiles"].files`:

```python
from browser import ajax, document

def upload_ok(req):
    print("all right")

for f in document["choosefiles"].files:
    ajax.file_upload("/cgi-bin/savefile.py", f, oncomplete=upload_ok)
```

## browser.websocket

- `websocket.supported` — boolean
- `websocket.WebSocket(host)` — returns a socket object; `NotImplementedError` if unsupported
- methods: `bind(evt, function)` for events `open` (no args), `error` (no args), `message` (one arg, a `DOMEvent` with `data` = the server message string), `close` (no args); `send(data)`; `close()`

## Storage

`browser.local_storage` and `browser.session_storage` each expose a dict-like `storage` object:

- values are **strings only**; scoped to the origin (`scheme://host:port`), shared across tabs of the same origin, but an `http` page cannot see data written over `https`
- `local_storage` is persistent (survives browser restarts); `session_storage` is cleared when the browser window closes (use it for per-session data like login tokens)
- dict interface: `get`, `pop`, `keys`, `values`, `items`, `clear`, `len`, `in`, iteration; `keys`/`values`/`items` return list copies, not views

```python
from browser.local_storage import storage
storage["foo"] = "bar"
del storage["foo"]        # KeyError afterwards
```

`browser.object_storage.ObjectStorage(storage)` extends either storage with JSON-serializable Python objects (dicts, lists). Keys can be lists (nested paths). Objects are immutable once stored — to update, read out, mutate, write back:

```python
from browser.session_storage import storage
from browser.object_storage import ObjectStorage

os_ = ObjectStorage(storage)
os_[["do", "re", "me"]] = {"tune": "in tune"}
tmp = os_[["do", "re", "me"]]
tmp.update({"duration": "one hour"})
os_[["do", "re", "me"]] = tmp
```

## browser.markdown

`markdown.mark(src)` returns a 2-tuple `(html, scripts)` — HTML rendered from the markdown source, and a list of the source code of scripts found in the page. Differences from plain markdown: `_text_` → `<I>` vs `*text*` → `<EM>`, `__text__` → `<B>` vs `**text**` → `<STRONG>`, underscores inside words untouched, and a line starting with ` ``` ` + language becomes `<PRE class="language">`.

Typical use (fetch a markdown page, render it, run its scripts):

```python
from browser import document, markdown
mk, scripts = markdown.mark(open(url).read())
document["zone"].html = mk
for script in scripts:
    exec(script, globals())
```
