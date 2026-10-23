# Async, timers, web workers

- [browser.aio (asynchronous programming)](#browseraio-asynchronous-programming)
- [browser.timer](#browsertimer)
- [browser.worker (Web Workers)](#browserworker-web-workers)

## browser.aio (asynchronous programming)

Replaces `asyncio`, which cannot run in a browser (no blocking event loop; the browser has its own implicit loop). Uses ordinary `async`/`await`:

```python
from browser import aio

async def main():
    req = await aio.get("test.html")
    print(req.data)

aio.run(main())     # non-blocking start; run the coroutine
```

Functions:

- `ajax(method, url, format="text", headers=None, data=None, cache=False)` — `req = await aio.ajax("GET", url)`; `format` is `"text"`, `"binary"`, or `"dataURL"`; `data` is a string or dict (query string for GET, body for POST)
- `get(url, ...)` / `post(url, ...)` — shortcuts
- `event(element, name)` — `evt = await aio.event(input, "blur")` suspends until the event fires; returns a `DOMEvent`
- `sleep(seconds)` — `await aio.sleep(n)` yields control for n seconds
- `run(coroutine)` — start a coroutine without blocking
- `Future` — basic future with `set_result` / `set_exception`, for adapting callback-style APIs to `await`

`Request` instances (from `ajax`/`get`/`post`) expose `data` (body in the requested format), `response_headers` (dict), `status` (int), `statusText` (str).

Example — simulated `input()` with validation:

```python
from browser import alert, document, html, aio

async def main():
    input = html.INPUT()
    document <= input
    while True:
        ev = await aio.event(input, "blur")
        try:
            v = int(ev.target.value)
            input.remove()
            alert(f"Value: {v}")
            break
        except ValueError:
            input.value = ""

aio.run(main())
```

## browser.timer

- `set_timeout(function, ms, *args)` — run once after ms; returns an id for `clear_timeout`
- `clear_timeout(timer)` — cancel a pending timeout
- `set_interval(function, ms, *args)` — repeat every ms; returns an id for `clear_interval`
- `clear_interval(timer)` — stop the interval
- `request_animation_frame(function)` / `cancel_animation_frame(id)` — browser-driven animation loop; prefer over `set_interval` when possible

Wraps the corresponding `window` timer APIs.

## browser.worker (Web Workers)

A worker is a Python script running on a separate thread so long work doesn't freeze the browser. It has restricted browser access (no `document`, no `html`, no `window`).

Declare the worker in the HTML page with the `webworker` class — `id` is mandatory:

```xml
<script type="text/python" class="webworker" id="myworker">
# worker code
</script>
```

(or `src="myworker.py"`). The class marks the script as not to be executed as a normal script.

Main script:

```python
from browser import worker

def onready(myWorker):
    myWorker.send([1, 2])

def onmessage(e):
    print(e.data)            # e.target is the worker object

worker.create_worker("myworker", onready, onmessage, onerror=None)
```

`create_worker(worker_id, onready=None, onmessage=None, onerror=None)` is asynchronous; `onmessage` gets an event with `data` (the message) and `target` (the worker); `onerror` gets the error string. The worker object has `send(message)`.

Worker side — `browser.self` replaces `window` and manages the connection:

```python
from browser import bind, self

@bind(self, "message")
def message(evt):
    try:
        result = int(evt.data[0]) * int(evt.data[1])
        self.send(f"Result: {result}")
    except ValueError:
        self.send("Please write two numbers")
```

Messages must be "simple" objects: strings, numbers, lists of simple items, dicts with simple keys/values. The old `Worker(worker_id)` class still exists but is deprecated since 3.12 (synchronous, not the recommended path).
