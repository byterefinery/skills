# WebSockets

Source: `docs/client_quickstart.rst` (WebSockets), `docs/web_quickstart.rst` (WebSockets), `docs/web_advanced.rst`, `aiohttp/client.py` (`ws_connect`), `aiohttp/web_ws.py` (`WebSocketResponse`).

## TOC

- Client (ws_connect)
- Server (WebSocketResponse)
- Message types
- Heartbeat
- Reading in the handler task only
- Graceful shutdown

## Client — `session.ws_connect(url, ...)`

Returns a context manager for a `ClientWebSocketResponse`.

Key parameters (verified from source): `method` (GET), `protocols`, `timeout` (`ClientWSTimeout`), `receive_timeout`, `autoclose=True`, `autoping=True`, `heartbeat=None`, `origin`, `params`, `headers`, `proxy`, `proxy_headers`, `ssl=True`, `compress=0` (**client compression off by default**), `max_msg_size=4*1024*1024` (4 MiB), `decode_text=True`.

```python
async with session.ws_connect("ws://example.org/ws") as ws:
    await ws.send_str("hello")
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == "close cmd":
                await ws.close()
                break
            await ws.send_str(msg.data + "/answer")
        elif msg.type == aiohttp.WSMsgType.ERROR:
            break
```

- `decode_text=False` (3.14) keeps TEXT frames as `bytes` (pair with `orjson`); default decodes to `str`.
- Send helpers: `send_str`, `send_bytes`, `send_json` (uses session `json_serialize`), `send_frame`.
- `await ws.receive()` pulls one message; iterating `async for msg in ws` is sugar.
- `await ws.ping()` / `await ws.pong()` / `await ws.close(code=..., message=...)`.

**Must use a single task for both reading and writing** on a client WS. Multiple writer tasks are allowed (send-only); a second reader is not.

## Server — `web.WebSocketResponse`

Create in the handler, `prepare(request)`, then consume.

Key parameters (verified from source): `timeout=10.0` (seconds to finish the handshake), `receive_timeout=None`, `autoclose=True`, `autoping=True`, `heartbeat=None`, `protocols=()`, `compress=True` (**server compresses by default**), `max_msg_size=4*1024*1024`, `writer_limit=DEFAULT_CHUNK_SIZE`, `decode_text=True`.

```python
async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == "close":
                await ws.close()
            else:
                await ws.send_str(msg.data + "/answer")
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print("ws connection closed with exception", ws.exception())
    return ws

app.add_routes([web.get("/ws", ws_handler)])
```

- `ws.can_prepare(request)` returns whether the request is a valid WS upgrade (the `examples/web_ws.py` demo serves HTML otherwise).
- Broadcast pattern: keep live sockets in `app[web.AppKey("sockets", list)]`; add on prepare, remove in `finally` (see `examples/web_ws.py`).

## Message types — `aiohttp.WSMsgType`

`TEXT`, `BINARY`, `PING`, `PONG`, `CLOSE`, `CLOSED`, `CONNECT`, `ERROR`. Each message is a `WSMessage` with `.type`, `.data`, and (for `ERROR`) `ws.exception()`.

```python
msg = await ws.receive()
if msg.type == aiohttp.WSMsgType.TEXT:
    print(msg.data.strip())
elif msg.type == aiohttp.WSMsgType.BINARY:
    print(msg.data)
elif msg.type == aiohttp.WSMsgType.PING:
    await ws.pong()
elif msg.type == aiohttp.WSMsgType.CLOSE:
    await ws.close()
    break
```

## Heartbeat / keep-alive

`heartbeat=<seconds>` (both client and server) sends periodic pings; combined with `autoping`/`autoclose`. The `heartbeat` timer is reset on inbound data (3.14 fix: avoids false ping/pong timeouts while receiving large frames). `receive_timeout` bounds how long `receive()` may wait between messages.

## Reading in the handler task only

`await ws.receive()` / `async for msg in ws` **must** run in the request-handler task only. `ws.send_*`, `ws.close()`, and cancelling the handler may be delegated to other tasks. Parallel reads from two tasks are forbidden.

## Graceful shutdown

Track open sockets and close them from `on_shutdown` with an appropriate `WSCloseCode` (e.g. `WSCloseCode.GOING_AWAY` = 1001):

```python
from aiohttp import WSCloseCode

sockets = web.AppKey("sockets", list)
app[sockets] = []

async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    app[sockets].append(ws)
    try:
        async for msg in ws: ...
    finally:
        app[sockets].remove(ws)
    return ws

async def on_shutdown(app):
    for ws in list(app[sockets]):
        await ws.close(code=WSCloseCode.GOING_AWAY, message="Server shutdown")

app.on_shutdown.append(on_shutdown)
```

Full shutdown sequence in [10-deployment-advanced](10-deployment-advanced.md).
