---
name: redis-py-8-2-0
description: >
  redis-py 8.2.0 — the official Python client for Redis (key-value store).
  Use this skill whenever the user works with redis-py, Redis clients, Redis connections,
  connection pooling, pipelines, transactions, Pub/Sub, cluster mode, Sentinel, distributed
  locks, Lua scripting, async Redis access, Redis modules (JSON, Search, Bloom filters,
  TimeSeries, VectorSet), RESP3 protocol, unified responses, HIMPORT bulk ingestion,
  client-side caching with tracking modes, OpenTelemetry observability, MultiDB geographic
  failover, or maintenance notifications. Covers both sync (`redis.Redis`) and async
  (`redis.asyncio.Redis`) APIs. Also applies when connecting to Redis Cloud, Redis Enterprise,
  or any Redis-compatible server. Requires Python 3.11+.
metadata:
  tags:
    - cache
    - database
    - key-value
    - python
    - nosql
    - redis
---

# redis-py 8.2.0

redis-py 8.2.0 is the official Python client for [Redis](https://redis.io/), the in-memory data store. It supports RESP2 and RESP3 wire protocols (RESP3 default on the wire), connection pooling, clustering, Sentinel failover, async/await, pipelines, Pub/Sub, distributed locks, Lua scripting, client-side caching, OpenTelemetry observability, HIMPORT bulk hash ingestion, Redis modules (JSON, Search, Bloom, TimeSeries, VectorSet), MultiDB geographic failover, and maintenance notifications.

## Overview

### What's New in 8.2.0

- **Client-side caching tracking modes** — `CacheConfig` takes `tracking_mode` (`redis.cache.TrackingMode.PLAIN` default, `OPTIN`, or `OPTOUT`) and an optional `cache_predicate(command, keys)` callable. With `OPTIN`/`OPTOUT` the server tracks only the keys the client caches.
- **Metadata-driven cache eligibility** — Cache eligibility and cluster replica routing come from command metadata in `redis.commands.metadata`. Pass a `MetadataResolver` via `metadata_resolver=` to `Redis`, `ConnectionPool`, `RedisCluster`, or `redis.asyncio.RedisCluster`. `CacheConfig.DEFAULT_ALLOW_LIST` and `READ_COMMANDS` are deprecated and no longer read.
- **Multi-shard cluster routing** — Cluster clients route `MULTI_SHARD` and `ALL_SHARDS` commands and movable-key commands by the request/response tips the server publishes. A multi-shard command is split per slot into one pipeline per node; a retry resends only the parts that got no reply.
- **Paced topology refresh** — Error paths only request a cluster topology refresh; requests are merged and run at most once per `topology_refresh_min_interval` (default 1 s). A refresh keeps the connections of nodes that stay in the cluster.
- **Set member expiration** — `saddex`, `sexpire`, `spexpire`, `sexpireat`, `spexpireat`, `sttl`, `spttl`, `sexpiretime`, `spexpiretime`, `spersist` (Redis 8.12+ servers).
- **Sorted set moves** — `zmove`, `bzmove` (blocking), `zmovemember`.
- **New commands** — `BACKUP` family (`backup_start`, `backup_status`, `backup_list`, `backup_seal`, `backup_abort`, `backup_cleanup`; Redis 8.10+), `bitrangeintarray`, `BLESS` family, `CLIENT LIST` iterator, `hybrid_search(explain_score=True)`, `CELL_SIZE` for `CMS.INITBYDIM`/`CMS.INITBYPROB`.
- **Connection resilience** — When `protocol` is not set explicitly and a server or proxy rejects `HELLO`, the client falls back to RESP2 instead of raising. `Retry` takes an optional `is_retryable` checker; `redis.retry.is_retryable_connect_error` fails fast on a missing Unix socket path (ENOENT).
- **Security hardening** — Stricter OCSP validation, credentials redacted from pipeline and cluster routing error messages, lock tokens generated with `uuid4`.
- **Python support** — Drops Python 3.10 (EOL), adds Python 3.15. Requires Python 3.11+.

### Core Client Classes

| Class | Module | Purpose |
|---|---|---|
| `Redis` | `redis` | Synchronous single-node client |
| `StrictRedis` | `redis` | Alias for `Redis` (backwards compat) |
| `RedisCluster` | `redis.cluster` | Synchronous cluster client |
| `redis.asyncio.Redis` | `redis.asyncio` | Asynchronous single-node client |
| `redis.asyncio.cluster.RedisCluster` | `redis.asyncio.cluster` | Asynchronous cluster client |
| `Sentinel` | `redis.sentinel` | Sentinel manager for master discovery |
| `MultiDBClient` | `redis.multidb.client` | Active-Active multi-database client (experimental) |
| `ConnectionPool` | `redis.connection` | Connection pool (shared across clients) |
| `Pipeline` | `redis.client` | Batched command execution with optional transactions |
| `PubSub` | `redis.client` | Publish/Subscribe interface |
| `Lock` | `redis.lock` | Distributed lock (Lua-based) |

### Connection Modes

- **Single-node** — `Redis(host, port)` connects to one server. Default mode.
- **Cluster** — `RedisCluster(startup_nodes=[...])` auto-discovers topology and routes key-based commands by hash slot.
- **Sentinel** — `SentinelConnectionPool` discovers the current master via Sentinel nodes, handles failover transparently.
- **Unix socket** — `Redis(unix_socket_path="/path/to/redis.sock")` for local IPC.
- **MultiDB** — `MultiDBClient(config)` for Active-Active geographic failover across multiple Redis deployments.

### Protocol and Response Modes

redis-py 8.0+ uses RESP3 on the wire by default. Three orthogonal settings control behavior:

- **`protocol`** — wire protocol version: `2` (RESP2), `3` (RESP3), or `None` (default, uses RESP3 on wire)
- **`legacy_responses`** — Python response shape: `True` (default, RESP2-compatible shapes), `False` (unified protocol-independent shapes)
- **`decode_responses`** — string decoding: `True` decodes bulk strings to `str`, `False` returns `bytes`

For new projects, set `legacy_responses=False` for stable, protocol-independent Python response types. Existing applications can keep the default while migrating response handling gradually.

### Namespace Accessors (Redis Modules)

Module commands are accessed via namespace methods on the client:

- `r.json()` → `JSON` / `AsyncJSON` — RedisJSON module
- `r.ft(index_name)` → `Search` / `AsyncSearch` — RediSearch module
- `r.ts()` → `TimeSeries` / `AsyncTimeSeries` — RedisTimeSeries module
- `r.bf()` → `BFBloom` — Bloom filters
- `r.cf()` → `CFBloom` — Cuckoo filters
- `r.cms()` → `CMSBloom` — Count-Min Sketch
- `r.topk()` → `TOPKBloom` — Top-K
- `r.tdigest()` → `TDigestBloom` — T-Digest
- `r.vset()` → `VectorSet` / `AsyncVectorSet` — Vector Set (new in 8.x)

## Usage

### Basic Connection

```python
import redis

# Direct connection (creates its own pool)
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
r.set("greeting", "hello")
print(r.get("greeting"))  # "hello"

# From URL
r = redis.Redis.from_url("redis://localhost:6379/0")
r = redis.Redis.from_url("rediss://user:pass@localhost:6379/0")  # SSL
r = redis.Redis.from_url("unix:///path/to/redis.sock?db=0")

# From pool (client takes ownership, closes pool on close())
pool = redis.ConnectionPool.from_url("redis://localhost:6379/0")
r = redis.Redis.from_pool(pool)

# Shared pool (client does NOT own the pool)
with redis.ConnectionPool.from_url("redis://localhost:6379/0") as pool:
    r1 = redis.Redis(connection_pool=pool)
    r2 = redis.Redis(connection_pool=pool)
```

### Unified Responses (Recommended for New Projects)

```python
import redis

# Unified Python responses, RESP3 wire (default)
r = redis.Redis(legacy_responses=False)

# Unified responses with explicit RESP2 wire
r = redis.Redis(protocol=2, legacy_responses=False)

# Unified responses with explicit RESP3 wire
r = redis.Redis(protocol=3, legacy_responses=False)
```

### Pipelines

```python
pipe = r.pipeline()
pipe.set("key1", "value1")
pipe.set("key2", "value2")
pipe.get("key1")
results = pipe.execute()  # [True, True, "value1"]

# Non-transactional pipeline (no MULTI/EXEC)
pipe = r.pipeline(transaction=False)

# Transactional pipeline with WATCH
with r.pipeline() as pipe:
    while True:
        try:
            pipe.watch("balance")
            balance = int(pipe.get("balance"))
            if balance >= 100:
                pipe.multi()
                pipe.set("balance", balance - 100)
                pipe.execute()
                break
        except redis.WatchError:
            continue
```

### Async Client

```python
import asyncio
import redis.asyncio as aioredis

async def main():
    r = aioredis.Redis(host="localhost", port=6379)
    await r.set("key", "value")
    result = await r.get("key")
    await r.close()

asyncio.run(main())
```

### HIMPORT Bulk Hash Ingestion

```python
# Register fieldset once per client
r.himport_prepare("users", ["name", "email", "age"])

# Create hashes by sending only values
r.himport_set("user:1", "users", ["alice", "alice@example.com", "25"])
r.himport_set("user:2", "users", ["bob", "bob@example.com", "30"])

# In a pipeline for highest throughput
with r.pipeline(transaction=False) as pipe:
    pipe.himport_prepare("users", ["name", "email", "age"])
    for uid, row in rows:
        pipe.himport_set(f"user:{uid}", "users", row)
    pipe.execute()

# Clean up
r.himport_discard("users")
```

## Gotchas

- **Python 3.10 is gone in 8.2.0** — The package requires Python 3.11+ (3.15 supported). Environments pinned to 3.10 need redis-py 8.1.x or earlier.
- **`Redis()` creates its own pool** — Each `Redis()` instance gets a separate `ConnectionPool` by default. Share a pool explicitly via `connection_pool=pool` when multiple clients should reuse connections. Use `from_pool(pool)` when the client should own the pool lifecycle.
- **RESP3 is default on the wire** — redis-py 8.0+ uses RESP3 by default. Legacy RESP2-compatible Python response shapes are preserved by default (`legacy_responses=True`). Set `legacy_responses=False` for unified, protocol-independent responses. If a server or proxy rejects `HELLO` and `protocol` was not set explicitly, 8.2.0 falls back to RESP2 instead of raising.
- **`legacy_responses` vs `protocol`** — These are orthogonal. `protocol` controls the wire format; `legacy_responses` controls the Python response shape. A RESP3 wire connection can return RESP2-compatible Python shapes, and vice versa.
- **`decode_responses=True` decodes everything** — Including keys returned by `KEYS`, `HKEYS`, `SMEMBERS`, etc. Do not use with binary keys or `DUMP`/`RESTORE` commands.
- **Pipelines are not thread-safe** — A `Pipeline` object should not be shared between threads. Create one per thread or use `single_connection_client=True`.
- **`WATCH` must precede `MULTI`** — In transactional pipelines, call `watch()` before any other commands, then `multi()` to start the transaction block. Commands between `watch()` and `multi()` are executed immediately.
- **Cluster mode does not support `db` selection** — `RedisCluster` ignores `db` parameter (only db=0 is valid). All keys route via hash slots, not database number.
- **Cluster pipelines require same-slot keys** — In cluster mode, pipeline commands must operate on keys hashing to the same slot, or use hash tags `{tag}` to force co-location.
- **`Pipeline.execute()` returns all results as a list** — Even commands that normally return `True`/`False` or `None`. Index into the list or iterate to get individual results.
- **Pub/Sub blocks the connection** — Once subscribed, the underlying connection cannot execute regular commands. Use a separate `Redis` instance for publishing.
- **`Lock` uses Lua scripts internally** — The release, extend, and reacquire operations are atomic Lua scripts. Scripts are registered lazily on first `Lock` creation.
- **`close()` on `Redis` disconnects the pool** — When using `from_pool()` or `from_url()`, the client owns the pool and `close()` disconnects all connections. With explicit `connection_pool=pool`, the client does not close the pool.
- **Sentinel requires at least 3 nodes** — For reliable quorum-based master discovery, run at least 3 Sentinel instances.
- **Async client is in `redis.asyncio`** — Import as `import redis.asyncio as aioredis` or `from redis.asyncio import Redis`.
- **`SELECT` is not available on `Redis` instances** — redis-py deliberately omits `SELECT` because it breaks connection pooling in multi-threaded contexts. Create separate clients per database instead.
- **HIMPORT fieldsets are connection state** — A prepared fieldset lives in the server-side session of the physical connection. redis-py handles lazy re-prepare on reconnects automatically, but fieldsets are invisible to other connections. Use pipelines to ensure PREPARE and SETs execute on the same connection.
- **HIMPORT is not supported on MultiDB client** — The Active-Active `MultiDBClient` does not support HIMPORT commands.
- **Client-side caching requires RESP3** — Cache tracking and invalidation only work with `protocol=3` (or default).
- **`tracking_mode` is a connection-setup property** — The server refuses to switch a live connection between `OPTIN` and `OPTOUT`, so a `CacheConfig` change applies to new connections only.
- **`cache_predicate` needs `OPTIN` or `OPTOUT`** — Passing `cache_predicate` with the default `TrackingMode.PLAIN` warns and is ignored; `OPTIN` without `cache_predicate` warns and stores nothing (every read is sent alone, untracked).
- **`CacheConfig.DEFAULT_ALLOW_LIST` is deprecated** — Editing it changes nothing; eligibility is decided from command metadata. Change what gets cached via a custom `metadata_resolver` passed to the client or pool.
- **Set member expiration needs Redis 8.12+ servers** — `saddex` and the `sexpire` family (`sttl`, `spttl`, `sexpiretime`, `spexpiretime`, `spersist`) require Redis 8.12+; the `BACKUP` commands require Redis 8.10+.
- **`bzmove` needs exactly one of `min`/`max`** — Passing both or neither raises `DataError`; `timeout=0` blocks indefinitely, and inside a transaction it never blocks.
- **`zmove` takes `byscore` as a tuple** — Unlike `zrange`, `zmove(..., byscore=(lo, hi))` takes the bounds as a 2-tuple (inclusive; prefix a bound with `(` for exclusive). Exactly one of `min`, `max`, `byscore` must be given.
- **Maintenance notifications require RESP3** — Server-initiated maintenance push notifications are only available with RESP3.
- **`retry_on_timeout` is deprecated** — Use the `retry` parameter with a `Retry` object and `retry_on_error` list for fine-grained control. The default `Retry` already retries on `ConnectionError`, `TimeoutError`, and `socket.timeout`.

## References

- [01-connections](references/01-connections.md) — Connection parameters, pools, SSL, Unix sockets, URL schemes, `from_pool` vs `connection_pool`, RESP2 fallback on rejected `HELLO`
- [02-protocol-responses](references/02-protocol-responses.md) — RESP2/RESP3, `legacy_responses`, unified responses, `decode_responses`, response modes matrix
- [03-basic-commands](references/03-basic-commands.md) — GET, SET, DEL, EXISTS, EXPIRE, TTL, key management, scanning
- [04-data-structures](references/04-data-structures.md) — Strings, Lists, Sets (member expiration), Hashes, Sorted Sets (`zmove` family), Streams, HyperLogLog, Bitmaps, Geo
- [05-pipelines-transactions](references/05-pipelines-transactions.md) — Pipeline batching, MULTI/EXEC, WATCH, CAS patterns, cluster pipelines
- [06-pubsub](references/06-pubsub.md) — Pub/Sub channels, pattern matching, shard channels, message handling, keyspace notifications
- [07-cluster](references/07-cluster.md) — Cluster client, topology discovery and paced refresh, multi-shard routing, slot routing, hash tags, target nodes, cluster pipelines
- [08-sentinel](references/08-sentinel.md) — Sentinel discovery, master/replica routing, failover handling, SentinelConnectionPool
- [09-async](references/09-async.md) — Async client, async connections, async pipelines, async locks, async Pub/Sub
- [10-scripting](references/10-scripting.md) — Lua scripting, EVAL/EVALSHA, registered scripts, KEYS/ARGV
- [11-himport](references/11-himport.md) — HIMPORT bulk hash ingestion, fieldset lifecycle, pipeline patterns, cluster/Sentinel behavior
- [12-advanced](references/12-advanced.md) — Distributed locks, retry/backoff with `is_retryable` checkers, client-side caching with tracking modes, credentials, OCSP, driver info, maintenance notifications
- [13-modules](references/13-modules.md) — JSON, Search (RediSearch, hybrid search), Bloom filters, Cuckoo, CMS, TopK, T-Digest, TimeSeries, VectorSet
- [14-multidb](references/14-multidb.md) — MultiDBClient, geographic failover, health checks, circuit breakers, failover strategies
- [15-observability](references/15-observability.md) — OpenTelemetry integration, metrics, attributes, event dispatching
