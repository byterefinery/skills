# Cluster

## Connecting to Cluster

```python
from redis.cluster import RedisCluster, ClusterNode

# From host/port (discovers topology from one node)
rc = RedisCluster(host="localhost", port=6379)

# From URL
rc = RedisCluster.from_url("redis://localhost:6379")

# From startup nodes
nodes = [
    ClusterNode("localhost", 6379),
    ClusterNode("localhost", 6380),
    ClusterNode("localhost", 6381),
]
rc = RedisCluster(startup_nodes=nodes)

# With options
rc = RedisCluster(
    host="localhost",
    port=6379,
    password="secret",
    decode_responses=True,
    protocol=3,
    legacy_responses=False,
    skip_full_coverage_check=False,  # Ensure all 16384 slots are covered
    require_full_coverage=True,       # Error if not all slots covered
)
```

## Key Routing

Redis Cluster distributes data across 16384 hash slots. Each key is assigned to a slot via `CRC16(key) % 16384`. The cluster client automatically routes commands to the correct node.

```python
# Single-key commands — auto-routed
rc.set("user:1:name", "Alice")
rc.get("user:1:name")

# Multi-key commands — all keys must be in the same slot
rc.mset({"user:1:a": "1", "user:1:b": "2"})  # May fail if keys hash to different slots

# Use hash tags to force co-location
rc.mset({"{user1}:a": "1", "{user1}:b": "2"})  # Same slot guaranteed
```

## Target Nodes

Non-key commands accept `target_nodes` to specify which node(s) to execute on.

```python
# Node flags
rc.ping(target_nodes=RedisCluster.PRIMARIES)    # All primary nodes
rc.ping(target_nodes=RedisCluster.REPLICAS)     # All replica nodes
rc.ping(target_nodes=RedisCluster.ALL_NODES)    # All nodes
rc.ping(target_nodes=RedisCluster.RANDOM)       # One random node

# Info on all primaries
info = rc.info(target_nodes=RedisCluster.PRIMARIES)

# Keys on all nodes
all_keys = rc.keys("*", target_nodes=RedisCluster.ALL_NODES)

# Specific node
node = rc.get_node("localhost", 6379)
rc.info(target_nodes=node)
```

## Cluster Topology

```python
# Get all nodes
nodes = rc.get_nodes()

# Get primaries
primaries = rc.get_primaries()

# Get replicas
replicas = rc.get_replicas()

# Get specific node
node = rc.get_node("localhost", 6379)
node = rc.get_node_by_name("127.0.0.1:6379")

# Get default node (random primary)
default = rc.get_default_node()
rc.set_default_node(node)

# Get slots cache
slots = rc.get_connection_kwargs().get("slots_cache")

# Get nodes for a key's slot
nodes = rc.get_nodes_from_key("mykey")
```

## Hash Slots

```python
from redis.crc import key_slot

slot = key_slot("mykey")  # Which slot this key maps to

# Keys with same hash tag share a slot
key_slot("{user}1:name")  # Same slot
key_slot("{user}1:email")  # Same slot
```

## Cluster Pipelines

```python
# Pipeline with same-slot keys
pipe = rc.pipeline()
pipe.set("{user}1:name", "Alice")
pipe.set("{user}1:email", "alice@example.com")
results = pipe.execute()

# Non-transactional pipeline (cross-slot allowed in some cases)
pipe = rc.pipeline(transaction=False)
pipe.set("key1", "v1")
pipe.set("key2", "v2")
results = pipe.execute()
```

### Cluster Pipeline Constraints

- Transactional pipelines (`transaction=True`) require all keys in the same slot
- Non-transactional pipelines may route commands to different nodes
- `WATCH` is not supported in cluster mode

## Cluster Scan

```python
# Scan across all nodes
cursor = 0
while True:
    cursor, keys = rc.scan(cursor=cursor, match="user:*", count=100)
    for key in keys:
        process(key)
    if cursor == {}:  # Empty dict means done in cluster mode
        break

# Use scan_iter for convenience
for key in rc.scan_iter(match="user:*", count=100):
    process(key)
```

Cluster scan returns a `dict` of cursors (one per node) instead of a single integer cursor.

## Cluster Pub/Sub

```python
# Pub/Sub on cluster (shard channels recommended)
pubsub = rc.pubsub()
pubsub.ssubscribe("shard:news:0")

# Publish
rc.spublish("shard:news:0", "message")
```

Traditional Pub/Sub has limitations in cluster mode. Shard channels (SSUBSCRIBE/SPUBLISH) provide better scaling.

## Cluster Failover and Reconnection

```python
rc = RedisCluster(
    host="localhost",
    port=6379,
    retry=redis.retry.Retry(
        backoff=redis.backoff.ExponentialWithJitterBackoff(),
        retries=3,
    ),
)
```

The cluster client automatically:
- Detects MOVED/ASK redirects and updates the slots cache
- Reconnects to nodes on failure
- Refreshes topology on cluster changes
- Retries commands on transient errors

## Cluster Gotchas

- **No `SELECT` / `db` parameter** — Cluster mode only supports db=0. The `db` parameter is ignored
- **`KEYS` is restricted** — Use `SCAN` instead. `KEYS` may only work on a single node
- **Multi-key commands need same slot** — `MSET`, `MGET`, `DEL` with multiple keys require all keys in the same slot (use hash tags)
- **`WATCH` is not supported** — Optimistic locking via WATCH doesn't work in cluster mode
- **`SCAN` cursor is a dict** — Cluster scan returns `{node_name: cursor}` per node. Check for `{}` (empty dict) to detect completion
- **Topology changes cause retries** — MOVED/ASK redirects trigger automatic retries. Commands may execute multiple times — ensure idempotency
- **`require_full_coverage`** — Set to `True` (default) to ensure all 16384 slots are covered. Set to `False` for partial cluster coverage
- **Replica read** — By default, read commands go to primaries. Use `read_from_replicas=True` to allow reads from replicas:

```python
rc = RedisCluster(host="localhost", port=6379, read_from_replicas=True)
```

## Async Cluster

```python
import asyncio
from redis.asyncio.cluster import RedisCluster

async def main():
    rc = RedisCluster(host="localhost", port=6379)
    await rc.set("key", "value")
    result = await rc.get("key")
    await rc.close()

asyncio.run(main())
```
