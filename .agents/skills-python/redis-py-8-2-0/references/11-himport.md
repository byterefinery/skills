# HIMPORT

HIMPORT is a bulk hash ingestion protocol introduced in Redis 8.10. It lets you register field names once per connection, then create many hashes by sending only values — significantly reducing bandwidth and parsing overhead.

## Basic Usage

```python
# Register fieldset once per client
r.himport_prepare("users", ["name", "email", "age"])

# Create hashes by sending only values (paired positionally with fields)
r.himport_set("user:1", "users", ["alice", "alice@example.com", "25"])
r.himport_set("user:2", "users", ["bob", "bob@example.com", "30"])

# Create multiple fieldsets
r.himport_prepare("products", ["sku", "price", "category"])
r.himport_set("prod:1", "products", ["ABC123", "29.99", "electronics"])

# Clean up fieldsets
r.himport_discard("users")
r.himport_discard_all()  # Discard all fieldsets
```

## Fieldset Lifecycle

```python
# 1. Prepare — register field names
r.himport_prepare("schema_name", ["field1", "field2", "field3"])

# 2. Use — create hashes with just values
r.himport_set("key1", "schema_name", ["val1", "val2", "val3"])
r.himport_set("key2", "schema_name", ["val4", "val5", "val6"])

# 3. Discard — remove fieldset when done
r.himport_discard("schema_name")
```

### Important: Fieldsets Are Connection State

A prepared fieldset lives in the **server-side session** of the physical connection that prepared it. It is:

- **Invisible to other connections** — Connection B cannot use a fieldset prepared on Connection A
- **Destroyed by disconnect** — Closing the connection drops all fieldsets
- **Destroyed by `RESET`** — The `RESET` command clears session state
- **Destroyed by `maxmemory-clients` eviction** — Server memory pressure can evict session state

redis-py handles this automatically:
- `himport_prepare()` records the fieldset in a **client-level registry**
- The server-side `PREPARE` is applied **lazily** on whatever pooled connection serves each `himport_set`
- After reconnect, `RESET`, or failover, the `PREPARE` is **re-applied automatically**

You declare each fieldset **once per client** with `himport_prepare`; there is no constructor argument for it.

## Pipeline Pattern (Highest Throughput)

For maximum throughput, send PREPARE and SETs in one pipeline — a single batch always executes on one connection:

```python
with r.pipeline(transaction=False) as pipe:
    pipe.himport_prepare("users", ["name", "email", "age"])
    for uid, row in rows:
        pipe.himport_set(f"user:{uid}", "users", row)
    pipe.execute()
```

**Important:** The automatic re-prepare applies to direct calls only, not to commands inside `pipeline`/`transaction` blocks. A batched `himport_set` relies on the single pre-flight `PREPARE` in that batch.

## HIMPORT in Cluster Mode

```python
from redis.cluster import RedisCluster

rc = RedisCluster(host="localhost", port=6379)

# himport_prepare/himport_discard update the shared cluster-wide registry
# They return immediately — no server I/O
rc.himport_prepare("users", ["name", "email", "age"])

# himport_set routes by the key's hash slot
# The PREPARE is applied lazily on each node's connection
rc.himport_set("user:1", "users", ["alice", "alice@example.com", "25"])
rc.himport_set("user:2", "users", ["bob", "bob@example.com", "30"])

# Discard
rc.himport_discard("users")
```

In cluster mode:
- `himport_prepare`/`himport_discard`/`himport_discard_all` update the client's shared registry and return immediately
- Server-side `PREPARE` is applied lazily on each node's connection when it serves an `himport_set`
- After reconnect or failover, `PREPARE` is re-applied per node
- `himport_set` routes by the key's hash slot

## HIMPORT with Sentinel

```python
# Use the master client
master = sentinel.master_for("mymaster", db=0)
master.himport_prepare("users", ["name", "email", "age"])
master.himport_set("user:1", "users", ["alice", "alice@example.com", "25"])
```

The fieldset survives failover automatically — redis-py re-prepares on the new master connection.

## Async HIMPORT

```python
import redis.asyncio as aioredis

async def main():
    r = aioredis.Redis(host="localhost")

    await r.himport_prepare("users", ["name", "email", "age"])
    await r.himport_set("user:1", "users", ["alice", "alice@example.com", "25"])
    await r.himport_set("user:2", "users", ["bob", "bob@example.com", "30"])
    await r.himport_discard("users")

    await r.close()
```

## Reading HIMPORT-created Hashes

Keys written via HIMPORT are regular Redis hashes — every hash command works on them:

```python
r.himport_prepare("users", ["name", "email", "age"])
r.himport_set("user:1", "users", ["alice", "alice@example.com", "25"])

# Read with standard hash commands
r.hget("user:1", "name")        # "alice"
r.hgetall("user:1")             # {"name": "alice", "email": "alice@example.com", "age": "25"}
r.hkeys("user:1")               # ["name", "email", "age"]

# Note: field enumeration order (HGETALL, HKEYS) is not guaranteed to match prepare order
```

## HIMPORT Gotchas

- **Not supported on MultiDB client** — `MultiDBClient` does not support HIMPORT commands
- **Not supported on Active-Active setups** — HIMPORT relies on per-connection session state which doesn't map to geographic failover
- **Field order matters** — Values pair positionally with the prepared fields. Mismatched counts cause errors
- **Field enumeration order not guaranteed** — `HGETALL`/`HKEYS` may return fields in a different order than the prepare order
- **Pipeline requires explicit PREPARE** — Inside a pipeline, include `himport_prepare` in the batch. The automatic re-prepare does not apply to pipeline commands
- **`himport_prepare` is idempotent** — Calling it multiple times with the same fieldset name and fields is safe
- **Registry is client-level** — Access via `r.himport_registry` to inspect registered fieldsets
- **`NoSuchFieldsetError` triggers auto-retry** — If the server drops session state (RESET, eviction), redis-py catches `NoSuchFieldsetError`, re-prepares, and retries the SET once
