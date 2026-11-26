# Sentinel

Source: docs/connections.rst (Sentinel Client), `valkey/sentinel.py` exports in `valkey/__init__.py`.

Valkey Sentinel provides high availability; sentinel-mode nodes accept only sentinel-specific commands, which requires the Sentinel client.

## Discovery

```python
from valkey import Sentinel

sentinel = Sentinel([('localhost', 26379)], socket_timeout=0.1)
sentinel.discover_master('mymaster')
# ('127.0.0.1', 6379)
sentinel.discover_slaves('mymaster')
# [('127.0.0.1', 6380)]
```

`Sentinel` takes a list of `(host, port)` tuples for the sentinel nodes plus connection kwargs (e.g. `socket_timeout`).

## Managed Connections

Exported from `valkey.sentinel` (re-exported at package level in `valkey/__init__.py`):

- `SentinelConnectionPool` — pool that resolves the current master (or a slave) through sentinel and handles failover transparently.
- `SentinelManagedConnection` — connection managed by a sentinel pool.
- `SentinelManagedSSLConnection` — TLS variant.

## Async

`valkey.asyncio.sentinel` provides the async equivalents (re-exported from `valkey.asyncio`).
