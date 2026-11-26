# Async

## Async Client

```python
import asyncio
import redis.asyncio as aioredis

async def main():
    # Direct connection
    r = aioredis.Redis(host="localhost", port=6379, db=0)

    # From URL
    r = aioredis.Redis.from_url("redis://localhost:6379/0")

    # From pool
    pool = aioredis.ConnectionPool.from_url("redis://localhost:6379/0")
    r = aioredis.Redis(connection_pool=pool)

    # Operations
    await r.set("key", "value")
    result = await r.get("key")
    await r.delete("key")

    # Cleanup
    await r.close()

asyncio.run(main())
```

## Async Connection Parameters

The async client accepts the same parameters as the sync client:

```python
r = aioredis.Redis(
    host="localhost",
    port=6379,
    db=0,
    password="secret",
    username="default",
    decode_responses=True,
    encoding="utf-8",
    socket_timeout=5,
    socket_connect_timeout=5,
    ssl=True,
    ssl_cert_reqs="required",
    max_connections=50,
    health_check_interval=30,
    protocol=3,
    legacy_responses=False,
    retry=aioredis.retry.Retry(...),
    retry_on_error=[aioredis.ConnectionError],
    single_connection_client=False,
)
```

## Async Pipelines

```python
async def main():
    r = aioredis.Redis(host="localhost")

    # Non-transactional pipeline
    pipe = r.pipeline(transaction=False)
    pipe.set("key1", "value1")
    pipe.set("key2", "value2")
    pipe.get("key1")
    results = await pipe.execute()  # [True, True, "value1"]

    # Transactional pipeline
    pipe = r.pipeline(transaction=True)
    pipe.set("a", 1)
    pipe.set("b", 2)
    results = await pipe.execute()

    # Context manager
    async with r.pipeline() as pipe:
        pipe.set("key", "value")
        results = await pipe.execute()

    await r.close()
```

## Async Pub/Sub

```python
async def main():
    r = aioredis.Redis(host="localhost")

    pubsub = r.pubsub()
    await pubsub.subscribe("news", "sports")

    # Consume subscribe confirmations
    await pubsub.get_message()
    await pubsub.get_message()

    # Listen for messages
    while True:
        message = await pubsub.get_message(timeout=1.0)
        if message:
            print(message)
            if message.get("data") == "quit":
                break

    await pubsub.unsubscribe()
    await pubsub.close()
    await r.close()
```

### Async Pub/Sub with Callbacks

```python
async def on_message(pubsub, message):
    print(f"Message: {message}")

async def main():
    r = aioredis.Redis(host="localhost")
    pubsub = r.pubsub()
    await pubsub.subscribe(**{"news": on_message})

    # listen() is not async — use get_message loop instead
    while True:
        message = await pubsub.get_message(timeout=1.0)
        if message:
            # Handle message
            pass

    await r.close()
```

## Async Lock

```python
from redis.asyncio.lock import Lock

async def main():
    r = aioredis.Redis(host="localhost")

    lock = Lock(r, "resource-lock", timeout=10, sleep=0.1, blocking=True, blocking_timeout=5)

    # Acquire
    acquired = await lock.acquired()
    if acquired:
        try:
            # Critical section
            pass
        finally:
            await lock.release()

    # Context manager
    async with Lock(r, "resource-lock", timeout=10) as lock:
        # Critical section
        pass

    await r.close()
```

## Async Cluster

```python
from redis.asyncio.cluster import RedisCluster

async def main():
    rc = RedisCluster(host="localhost", port=6379)

    await rc.set("key", "value")
    result = await rc.get("key")

    # Scan
    async for key in rc.scan_iter(match="user:*", count=100):
        process(key)

    await rc.close()
```

## Async Sentinel

```python
import redis.asyncio as aioredis

async def main():
    sentinel = aioredis.Sentinel(
        [("sentinel1.example.com", 26379), ("sentinel2.example.com", 26379)],
        socket_timeout=0.1,
    )

    master = await sentinel.master_for("mymaster", password="secret", db=0)
    replica = await sentinel.replica_for("mymaster", password="secret", db=0)

    await master.set("key", "value")
    result = await replica.get("key")

    await master.close()
    await replica.close()
```

## Async Lua Scripting

```python
async def main():
    r = aioredis.Redis(host="localhost")

    script = r.register_script("return redis.call('get', KEYS[1])")
    result = await script(keys=["mykey"])

    # EVAL
    result = await r.eval("return redis.call('get', KEYS[1])", 1, "mykey")

    # EVALSHA
    result = await r.evalsha(sha, 1, "mykey")

    await r.close()
```

## Async HIMPORT

```python
async def main():
    r = aioredis.Redis(host="localhost")

    await r.himport_prepare("users", ["name", "email", "age"])
    await r.himport_set("user:1", "users", ["alice", "alice@example.com", "25"])
    await r.himport_discard("users")

    await r.close()
```

## Async Gotchas

- **`redis.asyncio` is a separate import** — Use `import redis.asyncio as aioredis`, not `import redis`
- **All operations are awaitable** — Every command must be `await`ed. Forgetting `await` returns a coroutine, not a result
- **`async with` for pipelines** — Use `async with r.pipeline() as pipe` for proper cleanup
- **Connection pooling is async** — `ConnectionPool` in `redis.asyncio` manages async connections
- **`close()` is async** — `await r.close()` to properly shut down
- **No thread safety** — Async clients are designed for single-threaded async use. Don't share across threads
- **Event loop must be running** — All async operations require an active event loop
- **`from_url` returns async client** — `aioredis.Redis.from_url()` returns an async Redis, not sync
