---
name: valkey-py-6-1-1
description: >
  valkey-py 6.1.1 — the official Python client for Valkey (Redis-compatible key-value store).
  Use this skill whenever the user works with valkey-py, Valkey clients, Redis-compatible
  connections, connection pooling, pipelines, transactions, Pub/Sub, cluster mode, Sentinel,
  distributed locks, Lua scripting, async Valkey access, or Valkey modules (JSON, Search,
  Bloom filters, Graph, TimeSeries). Covers both sync (`valkey.Valkey`) and async
  (`valkey.asyncio.Valkey`) APIs. Also applies when migrating from redis-py to valkey-py.
metadata:
  tags:
    - cache
    - database
    - key-value
    - python
    - nosql
---

# valkey-py 6.1.1

valkey-py is the official Python client for [Valkey](https://valkey.io/), the open-source distributed key-value data store forked from Redis. Version 6.1.1 supports RESP2 and RESP3 protocols, connection pooling, clustering, Sentinel failover, async/await, pipelines, Pub/Sub, distributed locks, Lua scripting, client-side caching, and Valkey modules (JSON, Search, Bloom, Graph, TimeSeries).

## Overview

### Core Client Classes

| Class | Module | Purpose |
|---|---|---|
| `Valkey` | `valkey` | Synchronous single-node client |
| `ValkeyCluster` | `valkey.cluster` | Synchronous cluster client |
| `valkey.asyncio.Valkey` | `valkey.asyncio` | Asynchronous single-node client |
| `valkey.asyncio.cluster.ValkeyCluster` | `valkey.asyncio.cluster` | Asynchronous cluster client |
| `Sentinel` | `valkey.sentinel` | Sentinel manager for master discovery |
| `ConnectionPool` | `valkey.connection` | Connection pool (shared across clients) |
| `Pipeline` | `valkey.client` | Batched command execution with optional transactions |
| `PubSub` | `valkey.client` | Publish/Subscribe interface |
| `Lock` | `valkey.lock` | Distributed lock (Redisson-like) |

### Connection Modes

- **Single-node** — `Valkey(host, port)` connects to one server. Default mode.
- **Cluster** — `ValkeyCluster(startup_nodes=[...])` auto-discovers topology and routes key-based commands to the correct slot.
- **Sentinel** — `SentinelConnectionPool` discovers the current master via Sentinel nodes, handles failover transparently.
- **Unix socket** — `Valkey(unix_socket_path="/path/to/valkey.sock")` for local IPC.

### Protocol Versions

- **RESP2** (default) — Binary-safe, widely compatible. Set `protocol=2` explicitly.
- **RESP3** — Richer response types (push notifications, client tracking, sets, maps). Set `protocol=3`.

### Response Encoding

By default, all responses are returned as `bytes`. Set `decode_responses=True` to receive `str`. This applies to both keys and values. Binary data (e.g., from `DUMP`) should never use `decode_responses=True`.

### redis-py Compatibility

valkey-py provides `Redis` and `RedisCluster` aliases that map to `Valkey` and `ValkeyCluster`. You can `import valkey as redis` for a drop-in migration path. The package name on PyPI is `valkey`.

## Usage

### Basic Connection

```python
import valkey

# Direct connection (creates its own pool)
r = valkey.Valkey(host="localhost", port=6379, db=0, decode_responses=True)
r.set("greeting", "hello")
print(r.get("greeting"))  # "hello"

# From URL
r = valkey.Valkey.from_url("valkey://localhost:6379/0")
r = valkey.Valkey.from_url("valkeys://user:pass@localhost:6379/0")  # SSL
r = valkey.Valkey.from_url("unix:///path/to/valkey.sock?db=0")

# Shared connection pool
pool = valkey.ConnectionPool(host="localhost", port=6379, db=0, max_connections=50)
r1 = valkey.Valkey(connection_pool=pool)
r2 = valkey.Valkey(connection_pool=pool)
```

### RESP3 with Push Notifications

```python
r = valkey.Valkey(host="localhost", port=6379, protocol=3)
# RESP3 enables client tracking for server-assisted client-side caching
```

### Pipelines

```python
pipe = r.pipeline()
pipe.set("key1", "value1")
pipe.set("key2", "value2")
pipe.get("key1")
results = pipe.execute()  # [True, True, "value1"]

# Transactional pipeline (MULTI/EXEC)
pipe = r.pipeline(transaction=True)
pipe.watch("balance")
balance = int(pipe.get("balance"))
if balance >= 100:
    pipe.multi()
    pipe.set("balance", balance - 100)
    pipe.execute()
else:
    pipe.unwatch()
```

### Async Client

```python
import asyncio
from valkey.asyncio import Valkey

async def main():
    r = Valkey(host="localhost", port=6379)
    await r.set("key", "value")
    result = await r.get("key")
    await r.close()

asyncio.run(main())
```

### Distributed Lock

```python
from valkey.lock import Lock

lock = Lock(r, "resource-lock", timeout=10, sleep=0.1, blocking=True, blocking_timeout=5)
if lock.acquire():
    try:
        # critical section
        pass
    finally:
        lock.release()

# Context manager
with Lock(r, "resource-lock", timeout=10) as lock:
    pass
```

## Gotchas

- **`Valkey()` creates its own pool** — Each `Valkey()` instance gets a separate `ConnectionPool` by default. Share a pool explicitly via `connection_pool=pool` when multiple clients should reuse connections.
- **`decode_responses=True` decodes everything** — Including keys returned by `KEYS`, `HKEYS`, `SMEMBERS`, etc. Do not use with binary keys or `DUMP`/`RESTORE` commands.
- **Pipelines are not thread-safe** — A `Pipeline` object should not be shared between threads. Create one per thread or use `single_connection_client=True`.
- **`WATCH` must precede `MULTI`** — In transactional pipelines, call `watch()` before any other commands, then `multi()` to start the transaction block. Commands between `watch()` and `multi()` are executed immediately.
- **Cluster mode does not support `db` selection** — `ValkeyCluster` ignores `db` parameter (only db=0 is valid). All keys route via hash slots, not database number.
- **Cluster pipelines require same-slot keys** — In cluster mode, pipeline commands must operate on keys hashing to the same slot, or use hash tags `{tag}` to force co-location.
- **`Pipeline.execute()` returns all results as a list** — Even commands that normally return `True`/`False` or `None`. Index into the list or iterate to get individual results.
- **Pub/Sub blocks the connection** — Once subscribed, the underlying connection cannot execute regular commands. Use a separate `Valkey` instance for publishing.
- **`Lock` uses Lua scripts internally** — The release, extend, and reacquire operations are atomic Lua scripts. Scripts are registered lazily on first `Lock` creation.
- **`retry_on_timeout` vs `retry`** — `retry_on_timeout=True` is shorthand for retrying on `TimeoutError`. For fine-grained control, pass a `Retry` object with a `Backoff` strategy.
- **`close()` on `Valkey` disconnects the pool** — Calling `r.close()` releases and disconnects the connection pool. Use `from_pool()` or `from_url()` with care — the client owns the pool lifecycle.
- **Sentinel requires at least 3 nodes** — For reliable quorum-based master discovery, run at least 3 Sentinel instances. With fewer, a failure may prevent discovery.
- **Async client is in `valkey.asyncio`** — The async `Valkey` lives in `valkey.asyncio`, not the top-level `valkey`. Import as `from valkey.asyncio import Valkey`.
- **RESP3 changes response types** — With `protocol=3`, some commands return Python dicts/sets instead of lists. Callback handlers differ between RESP2 and RESP3.

## References

- [01-connections](references/01-connections.md) — Connection parameters, pools, SSL, Unix sockets, URL schemes
- [02-basic-commands](references/02-basic-commands.md) — GET, SET, DEL, EXISTS, EXPIRE, TTL, key management
- [03-data-structures](references/03-data-structures.md) — Strings, Lists, Sets, Hashes, Sorted Sets, Streams, HyperLogLog, Bitmaps
- [04-pipelines-transactions](references/04-pipelines-transactions.md) — Pipeline batching, MULTI/EXEC, WATCH, CAS patterns
- [05-pubsub](references/05-pubsub.md) — Pub/Sub channels, pattern matching, shard channels, message handling
- [06-cluster](references/06-cluster.md) — Cluster client, topology discovery, slot routing, hash tags, cluster pipelines
- [07-sentinel](references/07-sentinel.md) — Sentinel discovery, master/replica routing, failover handling
- [08-async](references/08-async.md) — Async client, async connections, async pipelines, async locks
- [09-scripting](references/09-scripting.md) — Lua scripting, EVAL/EVALSHA, registered scripts, KEYS/ARGV
- [10-advanced](references/10-advanced.md) — Distributed locks, retry/backoff, client-side caching, credentials, OCSP
- [11-modules](references/11-modules.md) — JSON, Search (RediSearch), Bloom filters, Graph, TimeSeries modules
- [12-migration](references/12-migration.md) — Migrating from redis-py, API differences, aliases, RESP3 migration
