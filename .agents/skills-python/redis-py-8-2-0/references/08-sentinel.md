# Sentinel

## Sentinel Manager

```python
from redis import Sentinel

# Connect to Sentinel nodes
sentinel = Sentinel(
    [("sentinel1.example.com", 26379),
     ("sentinel2.example.com", 26379),
     ("sentinel3.example.com", 26379)],
    socket_timeout=0.1,
    password="sentinel_password",  # If Sentinels are authenticated
)

# Discover master
master_address = sentinel.discover_master("mymaster")
# ('127.0.0.1', 6379)

# Discover replicas
replicas = sentinel.discover_slaves("mymaster")
# [('127.0.0.1', 6380), ('127.0.0.1', 6381)]
```

## SentinelConnectionPool

The recommended way to use Sentinel — the pool handles master discovery and failover automatically.

```python
from redis.sentinel import SentinelConnectionPool
from redis import Redis

# Master pool — connects to the current master
pool = SentinelConnectionPool(
    service_name="mymaster",
    sentinels=[
        ("sentinel1.example.com", 26379),
        ("sentinel2.example.com", 26379),
        ("sentinel3.example.com", 26379),
    ],
    password="redis_password",
    db=0,
    socket_timeout=5,
    sentinel_kwargs={
        "password": "sentinel_password",  # Auth for Sentinel nodes themselves
    },
)

r = Redis(connection_pool=pool)
r.set("key", "value")
```

### Replica Read Pool

```python
# Replica pool — round-robins across replicas, falls back to master
replica_pool = SentinelConnectionPool(
    service_name="mymaster",
    sentinels=[("sentinel1.example.com", 26379), ...],
    password="redis_password",
    role="slave",  # or "replica"
)

r_read = Redis(connection_pool=replica_pool)
value = r_read.get("key")  # Reads from a replica
```

## Failover Handling

When a failover occurs:
1. Sentinel nodes elect a new master
2. `SentinelConnectionPool` detects the new master address on next connection attempt
3. Idle connections to the old master are disconnected
4. New connections go to the new master

```python
# Failover is transparent — no code changes needed
r = Redis(connection_pool=pool)
r.set("key", "value")  # Works before and after failover
```

## Sentinel Commands

Execute commands directly against Sentinel nodes:

```python
sentinel = Sentinel([("localhost", 26379)])

# Sentinel-specific commands
sentinel.sentinel_master("mymaster")
sentinel.sentinel_masters()
sentinel.sentinel_replicas("mymaster")
sentinel.sentinel_sentinels("mymaster")
sentinel.sentinel_get_master_addr_by_name("mymaster")
sentinel.sentinel_reset("*")
sentinel.sentinel_failover("mymaster")
sentinel.sentinel_ckquorum("mymaster")
```

## SSL Sentinel

```python
from redis.sentinel import SentinelConnectionPool
from redis import SSLConnection

pool = SentinelConnectionPool(
    service_name="mymaster",
    sentinels=[("sentinel1.example.com", 26379)],
    connection_class=SSLConnection,
    ssl_cert_reqs="required",
    ssl_ca_certs="/path/to/ca.pem",
    sentinel_kwargs={
        "connection_class": SSLConnection,
        "ssl_cert_reqs": "required",
        "ssl_ca_certs": "/path/to/ca.pem",
    },
)
```

## Sentinel Gotchas

- **Minimum 3 Sentinels** — Run at least 3 Sentinel instances for reliable quorum-based master discovery. With fewer, a single failure may prevent discovery
- **`sentinel_kwargs` for Sentinel auth** — Authentication for Sentinel nodes themselves goes in `sentinel_kwargs`, not in the main pool kwargs
- **`role="slave"` vs `role="replica"`** — Both are accepted. `slave` is the legacy name, `replica` is the Redis 5.0+ terminology
- **Replica pool falls back to master** — If no replicas are available, the replica pool connects to the master
- **Connection invalidation on failover** — When the master address changes, idle connections are disconnected. In-use connections get `ConnectionError` on next command and reconnect
- **`discover_master` raises `MasterNotFoundError`** — If no Sentinel can find the master
- **`rotate_slaves` raises `SlaveNotFoundError`** — If no replicas are available and fallback to master also fails
- **Sentinel is not cluster** — Sentinel manages a single master-replica set. For sharding, combine Sentinel with application-level key routing or use Redis Cluster

## Async Sentinel

```python
import asyncio
from redis.asyncio import Sentinel

async def main():
    sentinel = Sentinel(
        [("sentinel1.example.com", 26379), ("sentinel2.example.com", 26379)],
        socket_timeout=0.1,
    )

    master = await sentinel.master_for(
        "mymaster",
        password="redis_password",
        db=0,
    )

    replica = await sentinel.replica_for(
        "mymaster",
        password="redis_password",
        db=0,
    )

    await master.set("key", "value")
    result = await replica.get("key")

    await master.close()
    await replica.close()

asyncio.run(main())
```
