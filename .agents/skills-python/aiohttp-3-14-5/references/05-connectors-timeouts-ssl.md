# Connectors, Timeouts, SSL, Proxies

Source: `docs/client_advanced.rst`, `aiohttp/client.py`, `aiohttp/connector.py`.

## TOC

- Connector ownership
- TCPConnector
- DNS cache and custom resolvers
- socket_factory
- Unix and named-pipe connectors
- ClientTimeout
- SSL control
- Proxies
- Graceful client shutdown

## Connector ownership

Pass a custom `connector` to `ClientSession` to change the transport layer. By default the session **owns** the connector and closes its connections on `session.close()`. To share one connector across sessions, create it explicitly and pass `connector_owner=False` to each session.

## TCPConnector

```python
conn = aiohttp.TCPConnector()
session = aiohttp.ClientSession(connector=conn)
```

- `limit=100` — total simultaneous connections (default **100**; `0` = unlimited)
- `limit_per_host=0` — per-endpoint limit on `(host, port, is_ssl)` (default **0** = no per-host limit)
- `ttl_dns_cache=10` — DNS cache TTL seconds (default **10**; `0` disables caching)
- `use_dns_cache=False` — disable the DNS cache entirely
- `resolver=...` — e.g. `AsyncResolver(nameservers=["8.8.8.8", "8.8.4.4"])` (requires `aiodns`)
- `ssl=...` — default SSL setting for all connections (request-level `ssl` overrides)
- `socket_factory=fn(addr_info)` — custom socket creation (see below)
- `force_close` — close connection after each request (disables keep-alive)

## socket_factory

`TCPConnector(socket_factory=fn)` where `fn(addr_info) -> socket` — used for every socket for the lifetime of the connector. Common uses: keepalive tuning (SO_KEEPALIVE, TCP_KEEPIDLE/TCP_KEEPCNT), binding to a network interface (`SO_BINDTODEVICE`).

```python
import socket

def socket_factory(addr_info):
    family, type_, proto, _, _ = addr_info
    sock = socket.socket(family=family, type=type_, proto=proto)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 7200)
    return sock

conn = aiohttp.TCPConnector(socket_factory=socket_factory)
```

## Unix and named-pipe connectors

- `aiohttp.UnixConnector(path='/path/to/socket')` — UNIX domain socket. Keep using the `http://` scheme; the domain/port in the URL still form the `Host` header (e.g. `http://localhost/get`).
- `aiohttp.NamedPipeConnector(path=r'\\.\pipe\<name>')` — Windows named pipes; works only with the ProactorEventLoop.

## ClientTimeout

attrs dataclass: `total`, `connect`, `sock_connect`, `sock_read`, `ceil_threshold=5`.

- `total` — whole operation (default **300 s**)
- `connect` — new connection establishment, or wait for a free pooled connection when pool limits are exceeded
- `sock_connect` — TCP connect only, non-pooled (default **30 s**, covers DNS fallback)
- `sock_read` — max gap between data portions from the peer
- `ceil_threshold` — values >= 5 s are ceiled to the next integer second (event-loop wakeup batching)

`None`/`0` disables a check. Default: `ClientTimeout(total=300, sock_connect=30)`.

## SSL control

- `ssl=False` (per request or `TCPConnector(ssl=False)`) disables verification.
- Custom `ssl.SSLContext`:

```python
ssl_context = ssl.create_default_context()
# system CAs, or certifi:
# ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.load_cert_chain("/path/cert.pem", "/path/key.key")  # self-signed/client certs
session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))
```

- Fingerprint pinning: `ssl=aiohttp.Fingerprint(b"<sha256 of DER cert>")` — raises `aiohttp.FingerprintMismatch` (`expected`/`got` attributes) on mismatch. Convert PEM→DER: `openssl x509 -in crt.pem -inform PEM -outform DER > crt.der`.
- Failure exceptions: `ClientConnectorSSLError` (wraps `ssl.SSLError`), `ClientConnectorCertificateError` (wraps `ssl.CertificateError`); catch both with `ClientSSLError`.
- `verify_ssl`, `ssl_context`, `fingerprint` parameters are deprecated — use the `ssl=` parameter (`True`, `False`, context, or `Fingerprint`).

## Proxies

- Per request: `session.get(url, proxy="http://proxy.com")`
- Proxy auth (3.14 way): `proxy_headers={"Proxy-Authorization": encode_basic_auth("user", "pass")}` — the `proxy_auth` parameter is deprecated (removed in 4.0). Credentials in the proxy URL (`http://user:pass@some.proxy.com`) also work.
- Session default: `ClientSession(proxy="http://proxy.com")` (constructor takes `proxy`; `proxy_headers` is a per-request parameter in this version)
- Environment variables are **not** read by default: `ClientSession(trust_env=True)` honors `HTTP_PROXY`, `HTTPS_PROXY`, `WS_PROXY` (3.8+), `WSS_PROXY` (3.8+), and `no_proxy` (via `urllib.request.getproxies`).
- Plain HTTP proxies and HTTP CONNECT for HTTPS are supported; TLS-in-TLS (HTTPS through an HTTPS proxy tunnel) depends on the Python runtime declaring support.
- Custom `ssl` contexts are used for **both** the endpoint TLS and the tunnel to the HTTPS proxy — make the trust chain cover both.
- `~/.netrc` provides proxy credentials if present.

## Graceful client shutdown

When a `ClientSession` closes, the underlying transport may close slightly later; stopping the event loop first can emit `ResourceWarning: unclosed transport`. After closing the session, add a short wait before stopping the loop:

```python
async def read_website():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://example.org/") as resp:
            await resp.read()
    await asyncio.sleep(0)          # non-SSL
    # await asyncio.sleep(0.25)    # SSL: a little longer
```
