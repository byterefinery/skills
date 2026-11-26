---
name: valkey-py-6-2-0
description: valkey-py 6.2.0 — the official Python client for Valkey, the open-source Redis-compatible key-value store. Use this skill when working with the valkey PyPI package, sync or async Valkey clients, connection pools and URLs, RESP2/RESP3, pipelines and transactions, Pub/Sub, Monitor, Lua scripting, distributed locks, cluster mode, Sentinel, retry and backoff, client-side caching, or Valkey modules (JSON, Search, Bloom, TimeSeries, Graph). Also applies when migrating from redis-py.
license: MIT
compatibility: Requires Python 3.11+ and a running Valkey server
metadata:
  tags:
    - cache
    - database
    - key-value
    - python
    - nosql
---

# valkey-py 6.2.0

valkey-py 6.2.0 (`__version__ == "6.2.0"`) is the official Python client for [Valkey](https://valkey.io/), the open-source key-value store forked from Redis. It is itself a fork of redis-py and exposes every built-in Valkey command under its raw name (`set`, `get`, `hset`, `zadd`, ...), plus pipelines, Pub/Sub, Monitor, Lua scripting, distributed locks, cluster mode, Sentinel, client-side caching, and async clients. Requires Python 3.11+ (MIT licensed).

## Overview

### Installation

```bash
pip install valkey                 # base client
pip install "valkey[libvalkey]"    # optional compiled response parser
```

The libvalkey compiled parser is used automatically when libvalkey 4.0.0+ is importable (`valkey/utils.py` gates on major version >= 4); no code changes are needed.

### Core Classes

| Class | Import path | Purpose |
|---|---|---|
| `Valkey` | `valkey` | Synchronous single-node client |
| `StrictValkey` | `valkey` | Exported sync client variant |
| `ValkeyCluster` | `valkey.cluster` | Synchronous cluster client (topology discovery + slot routing) |
| `Valkey` | `valkey.asyncio` | Asynchronous single-node client |
| `ValkeyCluster` | `valkey.asyncio.cluster` | Asynchronous cluster client |
| `Sentinel` | `valkey.sentinel` | Sentinel master/replica discovery |
| `ConnectionPool`, `BlockingConnectionPool`, `Connection`, `SSLConnection`, `UnixDomainSocketConnection` | `valkey.connection` | Connection plumbing and pools |
| `Pipeline` | via `client.pipeline()` | Buffered command batches, optional MULTI/EXEC |
| `PubSub` | via `client.pubsub()` | Subscribe/listen interface |
| `Lock` | `valkey.lock` (sync), `valkey.asyncio.lock` (async) | Distributed lock (Lua-backed) |
| `Retry` + backoffs | `valkey.retry`, `valkey.backoff` | Retry policies |

### Connection Modes

- **Direct** — `Valkey(host="localhost", port=6379, db=0)` creates its own `ConnectionPool`.
- **URL** — `Valkey.from_url("valkey://user:pass@host:6379/0")`; schemes are `valkey://` (TCP), `valkeys://` (TLS), `unix://` (Unix socket).
- **Cluster** — `ValkeyCluster(startup_nodes=[ClusterNode(...)])`, `ValkeyCluster(host=..., port=...)`, or `ValkeyCluster.from_url(...)`.
- **Sentinel** — `Sentinel([("localhost", 26379)])` then `discover_master("mymaster")`.

### Protocol and Encoding

- `protocol=2` (RESP2) is the default; `protocol=3` enables RESP3 (richer response types, push notifications).
- `decode_responses=False` by default — responses (and returned keys) are `bytes`; set `True` to get `str`.

### redis-py Compatibility

Drop-in aliases: `Redis = Valkey`, `StrictRedis = StrictValkey`, `RedisCluster = ValkeyCluster`, `RedisError = ValkeyError`. `import valkey as redis` works; the PyPI package name is `valkey`.

## Usage

### Basic Client

```python
import valkey

r = valkey.Valkey(host="localhost", port=6379, db=0)
r.set("foo", "bar")          # True
r.get("foo")                 # b"bar"

# Decoded strings instead of bytes
r = valkey.Valkey(host="localhost", port=6379, decode_responses=True)

# From URL (db resolution order: querystring, then path, then keyword)
r = valkey.Valkey.from_url("valkey://localhost:6379/0")
r = valkey.Valkey.from_url("valkeys://user:pass@host:6380?protocol=3")
r = valkey.Valkey.from_url("unix:///tmp/valkey.sock?db=1")

# Shared connection pool
pool = valkey.ConnectionPool(host="localhost", port=6379, db=0)
r1 = valkey.Valkey(connection_pool=pool)
r2 = valkey.Valkey(connection_pool=pool)
```

### Pipelines and Transactions

```python
pipe = r.pipeline()                    # transaction=True by default (MULTI/EXEC)
pipe.set("foo", 5).set("bar", 18.5).get("foo")
pipe.execute()                         # [True, True, b"5"]

# Pure batching without a transaction
pipe = r.pipeline(transaction=False)

# Compare-and-set via WATCH/MULTI — context manager auto-calls reset()
with r.pipeline() as pipe:
    while True:
        try:
            pipe.watch("OUR-SEQUENCE-KEY")
            current = int(pipe.get("OUR-SEQUENCE-KEY"))  # executes immediately
            pipe.multi()                                # back to buffered mode
            pipe.set("OUR-SEQUENCE-KEY", current + 1)
            pipe.execute()
            break
        except valkey.WatchError:
            continue

# Or use the helper, which retries WatchError for you (see Gotchas)
def client_side_incr(pipe):
    current = pipe.get("OUR-SEQUENCE-KEY")
    pipe.multi()
    pipe.set("OUR-SEQUENCE-KEY", int(current) + 1)

r.transaction(client_side_incr, "OUR-SEQUENCE-KEY")
```

### Pub/Sub

```python
p = r.pubsub()
p.subscribe("channel-1", "channel-2")
p.psubscribe("my-*")
p.get_message()   # dict with keys type, channel, pattern, data
for message in p.listen():        # blocking generator
    ...
r.publish("channel-1", "some data")   # returns count of matching subscriptions
```

### Async Client

```python
import asyncio
import valkey.asyncio as valkey

async def main():
    r = valkey.Valkey(host="localhost", port=6379)
    await r.set("key", "value")
    value = await r.get("key")
    await r.close()               # or aclose()

asyncio.run(main())
```

### Cluster

```python
from valkey.cluster import ValkeyCluster, ClusterNode

rc = ValkeyCluster(startup_nodes=[ClusterNode("localhost", 6379),
                                  ClusterNode("localhost", 6380)])
# also: ValkeyCluster(host="localhost", port=6379)
# also: ValkeyCluster.from_url("valkey://localhost:6379/0")

rc.set("{foo}1", "bar1")                     # hash tag keeps keys in one slot
rc.mget("{foo}1", "{foo}2")                  # atomic multi-key: same slot
rc.mget_nonatomic("a", "b")                  # non-atomic: keys split by slot
rc.keys(target_nodes=ValkeyCluster.ALL_NODES)  # non-key commands take target_nodes
rc.ping(target_nodes=ValkeyCluster.REPLICAS)
```

### Sentinel

```python
from valkey import Sentinel

sentinel = Sentinel([("localhost", 26379)], socket_timeout=0.1)
sentinel.discover_master("mymaster")   # ('127.0.0.1', 6379)
sentinel.discover_slaves("mymaster")   # [('127.0.0.1', 6380)]
```

### Distributed Lock

```python
from valkey.lock import Lock

lock = Lock(r, "resource-lock", timeout=10, sleep=0.1, blocking=True, blocking_timeout=5)
lock.acquire(blocking=False)           # token=... to set your own token
# lock.extend(5) / lock.reacquire() / lock.locked() / lock.owned()
lock.release()

# Context manager form
with Lock(r, "resource-lock", timeout=10) as lock:
    ...
```

### Lua Scripting

```python
lua = """
local value = redis.call('GET', KEYS[1])
value = tonumber(value)
return value * ARGV[1]"""
multiply = r.register_script(lua)      # returns a callable Script instance
multiply(keys=["foo"], args=[5])       # 10
```

### Retry and Backoff

```python
from valkey.backoff import ExponentialBackoff
from valkey.retry import Retry

retry = Retry(ExponentialBackoff(), 3)
r = valkey.Valkey(host="localhost", port=6379,
                  retry=retry, retry_on_timeout=True)
```

## Gotchas

- **Each `Valkey()` creates its own pool** — share a `ConnectionPool` explicitly (`connection_pool=pool`) when many clients should reuse connections.
- **Responses are `bytes` by default** — `decode_responses=False` is the default; never enable decoding for binary payloads such as `DUMP` output.
- **`SELECT` is not implemented on client instances** — pooled connections could be returned to the pool with a different database selected, so create one client (and ideally one pool) per database instead of switching dbs at runtime.
- **Client instances are thread-safe, but `PubSub` and `Pipeline` objects are not** — never pass them between threads; `single_connection_client=True` also makes the client itself not thread-safe.
- **Pipelines are transactions by default** — `pipeline()` wraps execution in MULTI/EXEC; pass `transaction=False` to batch without atomicity. In cluster mode the `transaction` option is not supported at all.
- **After `watch()`, the pipeline executes immediately** — commands between `watch()` and `multi()` run at once instead of being buffered. Use `with r.pipeline() as pipe` so `reset()` returns the bound connection to the pool.
- **`r.transaction()` retries `WatchError` forever by default** — pass `max_tries`/`watch_delay` to bound it; a typo like `r.set` instead of `pipe.set` becomes an infinite loop.
- **Cluster multi-key commands need same-slot keys** — use hash tags (`{tag}key`) or the `_nonatomic` variants (`mget_nonatomic`, `mset_nonatomic`); otherwise a cluster exception is raised.
- **Cluster does not use `db` selection** — routing is by hash slot only; non-key commands take `target_nodes` (`ValkeyCluster.ALL_NODES`, `.PRIMARIES`, `.REPLICAS`, `.RANDOM`).
- **Cluster Pub/Sub pattern commands are unreliable** — `psubscribe`/pattern publish cannot be mapped to key slots and are not recommended; use sharded pub/sub (`ssubscribe`, `get_sharded_message`) for cluster pub/sub scaling.
- **Cluster scripting is limited** — EVAL/EVALSHA keys must all hash to the same node (0-key scripts go to a random primary), `EVAL_RO`/`EVALSHA_RO` are unsupported, and scripts cannot be run inside cluster pipelines.
- **Cluster retry is two-tiered** — `retry` covers reconnect attempts to a node (default `Retry(NoBackoff(), 0)`), while `cluster_error_retry_attempts` (default 3) counts full cluster re-initialization cycles after those are exhausted.
- **Standalone retry is minimal without an explicit `retry`** — `retry_on_timeout=True` or `retry_on_error=[...]` alone defaults to `Retry(NoBackoff(), 1)`, i.e. one immediate retry.
- **`from_url`/`from_pool` clients own their pool** — they set `auto_close_connection_pool=True`, so closing the client also closes the pool.
- **RESP3 changes response handling** — `protocol=3` alters response types and callbacks; push notifications are logged by default, or supply your own via `r.pubsub(push_handler_func=...)`.
- **Lock `timeout=None` means no expiry** — the lock lives until `release()`; set a `timeout` so a crashed holder does not wedge the resource. `thread_local=True` and `sleep=0.1` are the defaults.
- **`charset` and `errors` parameters are deprecated** — use `encoding` and `encoding_errors`.
- **The libvalkey compiled parser requires libvalkey 4.0.0+** — `valkey/utils.py` only enables it when an importable libvalkey has major version >= 4.
- **Module commands hang off the client** — `r.json()`, `r.ft(index)`, `r.ts()`, `r.bf()`, `r.cf()`, `r.cms()`, `r.topk()`, `r.tdigest()`, `r.graph()` return the module command objects.

## References

- [01-connections](references/01-connections.md) — full connection parameters, URL schemes, pools, SSL, Unix sockets, credentials
- [02-commands](references/02-commands.md) — command exposure model, server/admin command catalog
- [03-pipelines-transactions](references/03-pipelines-transactions.md) — batching, MULTI/EXEC, WATCH compare-and-set, transaction helper
- [04-pubsub-monitor](references/04-pubsub-monitor.md) — subscriptions, message dicts, callbacks, run_in_thread, sharded pub/sub, Monitor
- [05-cluster](references/05-cluster.md) — topology, target_nodes, multi-key commands, hash tags, read replicas, pubsub limits
- [06-sentinel](references/06-sentinel.md) — Sentinel discovery and managed connections
- [07-async](references/07-async.md) — asyncio clients, async pools, async locks
- [08-scripting-lock](references/08-scripting-lock.md) — register_script, Script arguments, NOSCRIPT retry, Lock parameters
- [09-retry-backoff](references/09-retry-backoff.md) — Retry, backoff strategies, standalone vs cluster retry semantics
- [10-advanced](references/10-advanced.md) — client-side caching, RESP3 push notifications, OpenTelemetry, credentials, exceptions
- [11-modules](references/11-modules.md) — JSON, Search, TimeSeries, Bloom, Cuckoo filter, CMS, Top-K, t-digest, Graph
- [12-migration](references/12-migration.md) — migrating from redis-py, aliases, package name
