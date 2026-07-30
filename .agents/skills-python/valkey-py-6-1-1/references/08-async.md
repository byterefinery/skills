# Async

valkey-py provides full async/await support via the `valkey.asyncio` module. The async API mirrors the sync API with `await` on all commands.

## Async Client

```python
import asyncio
from valkey.asyncio import Valkey

async def main():
    r = Valkey(host="localhost", port=6379, decode_responses=True)

    await r.set("key", "value")
    result = await r.get("key")
    print(result)  # "value"

    await r.close()

asyncio.run(main())
```

### Constructor Parameters

Same as sync `Valkey`, plus async-specific behaviors:

```python
r = Valkey(
    host="localhost",
    port=6379,
    db=0,
    password="secret",
    decode_responses=True,
    socket_timeout=5,
    retry_on_timeout=False,
    ssl=False,
    protocol=2,
)
```

### From URL

```python
r = Valkey.from_url("valkey://localhost:6379/0")
r = Valkey.from_url("valkeys://localhost:6379/0")  # SSL
r = Valkey.from_url("unix:///path/to/valkey.sock?db=0")
```

### From Connection Pool

```python
from valkey.asyncio.connection import ConnectionPool

pool = ConnectionPool(host="localhost", port=6379, db=0)
r = Valkey(connection_pool=pool)
```

## Async Commands

All commands are async and must be awaited:

```python
# Strings
await r.set("key", "value")
value = await r.get("key")
await r.delete("key")

# Multiple keys
await r.mset({"k1": "v1", "k2": "v2"})
values = await r.mget("k1", "k2")

# Lists
await r.lpush("mylist", "a", "b", "c")
items = await r.lrange("mylist", 0, -1)

# Hashes
await r.hset("user:1", mapping={"name": "Alice", "age": "30"})
name = await r.hget("user:1", "name")
user = await r.hgetall("user:1")

# Sets
await r.sadd("tags", "python", "async")
members = await r.smembers("tags")

# Sorted Sets
await r.zadd("scores", {"alice": 100, "bob": 95})
top = await r.zrevrange("scores", 0, 2, withscores=True)

# Streams
await r.xadd("mystream", {"msg": "hello"})
entries = await r.xrange("mystream")

# Scan
async for key in r.scan_iter(match="user:*"):
    print(key)
```

## Async Pipelines

```python
# Non-transactional pipeline
pipe = r.pipeline(transaction=False)
pipe.set("key1", "value1")
pipe.set("key2", "value2")
pipe.get("key1")
results = await pipe.execute()

# Transactional pipeline
pipe = r.pipeline(transaction=True)
pipe.set("key1", "value1")
pipe.set("key2", "value2")
results = await pipe.execute()

# Context manager
async with r.pipeline() as pipe:
    pipe.set("key1", "value1")
    pipe.get("key1")
    results = await pipe.execute()
```

### WATCH in Async Pipelines

```python
pipe = r.pipeline(True)
await pipe.watch("balance")

balance = int(await r.get("balance") or 0)

if balance >= 100:
    await pipe.multi()
    await pipe.set("balance", balance - 100)
    try:
        result = await pipe.execute()
    except valkey.WatchError:
        pass  # retry
```

## Async Pub/Sub

```python
from valkey.asyncio import Valkey

async def main():
    r = Valkey(host="localhost", port=6379, decode_responses=True)
    pubsub = r.pubsub()

    await pubsub.subscribe("channel-1")

    # Listen for messages
    while True:
        message = await pubsub.get_message(timeout=1.0)
        if message is not None:
            print(message)

    await pubsub.close()

asyncio.run(main())
```

### Pattern Subscriptions

```python
pubsub = r.pubsub()
await pubsub.psubscribe("news:*", "sports:*")

while True:
    message = await pubsub.get_message(timeout=1.0)
    if message and message["type"] == "pmessage":
        print(f"{message['channel']}: {message['data']}")
```

## Async Lock

```python
from valkey.asyncio.lock import Lock

async def main():
    r = Valkey(host="localhost", port=6379)

    lock = Lock(r, "my-resource", timeout=10, sleep=0.1)
    acquired = await lock.acquire()

    if acquired:
        try:
            # critical section
            pass
        finally:
            await lock.release()

    # Context manager
    async with Lock(r, "my-resource", timeout=10) as lock:
        pass

    await r.close()

asyncio.run(main())
```

## Async Cluster

```python
from valkey.asyncio.cluster import ValkeyCluster

async def main():
    rc = ValkeyCluster(
        host="10.0.0.1",
        port=6379,
        decode_responses=True,
    )

    await rc.set("key", "value")
    result = await rc.get("key")

    await rc.close()

asyncio.run(main())
```

## Async Sentinel

```python
from valkey.asyncio import Valkey
from valkey.asyncio.sentinel import Sentinel

async def main():
    sentinel = Sentinel(
        [("sentinel1.example.com", 26379),
         ("sentinel2.example.com", 26379)],
        socket_timeout=0.1,
    )

    master_address = await sentinel.discover_master("mymaster")
    replicas = await sentinel.discover_slaves("mymaster")

    await sentinel.close()

asyncio.run(main())
```

## Async Connection Pool

```python
from valkey.asyncio.connection import ConnectionPool, SSLConnection

# Basic pool
pool = ConnectionPool(host="localhost", port=6379, db=0, max_connections=50)
r = Valkey(connection_pool=pool)

# SSL pool
pool = ConnectionPool(
    host="localhost",
    port=6379,
    connection_class=SSLConnection,
    connection_kwargs={"ssl_cert_reqs": "required"},
)
```

### BlockingConnectionPool (Async)

```python
from valkey.asyncio.connection import ConnectionPool

# Async pools don't block — they use asyncio queues internally
pool = ConnectionPool(host="localhost", port=6379, max_connections=50)
```

## Async Retry and Backoff

```python
from valkey.asyncio.retry import Retry
from valkey.backoff import ExponentialBackoff

retry = Retry(ExponentialBackoff(cap=0.5, base=0.01), retries=3)

r = Valkey(
    host="localhost",
    port=6379,
    retry=retry,
    retry_on_error=[valkey.ConnectionError, valkey.TimeoutError],
)
```

## Resource Management

```python
# Explicit close
r = Valkey(host="localhost", port=6379)
await r.set("key", "value")
await r.close()

# Context manager (if available)
async with Valkey(host="localhost", port=6379) as r:
    await r.set("key", "value")
```

## Gotchas

- **Import from `valkey.asyncio`** — The async `Valkey` is in `valkey.asyncio`, not top-level `valkey`.
- **All commands must be awaited** — Forgetting `await` returns a coroutine, not the result.
- **Async connections are not thread-safe** — Each async task should use its own client or share via async-safe patterns.
- **`close()` is async** — Call `await r.close()`, not `r.close()`.
- **Async Pub/Sub uses `await`** — `await pubsub.subscribe()` and `await pubsub.get_message()`.
- **Async lock uses `await`** — `await lock.acquire()` and `await lock.release()`.
- **Event loop conflicts** — Do not mix sync and async valkey-py clients in the same event loop context. Use separate processes or stick to one paradigm.
