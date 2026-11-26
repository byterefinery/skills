# Cluster

Valkey Cluster distributes data across multiple nodes using hash slots (0-16383). `ValkeyCluster` auto-discovers topology, routes commands to the correct node, and handles MOVED/ASK redirections.

## Creating a Cluster Client

```python
from valkey.cluster import ValkeyCluster

# From startup node(s)
startup_nodes = [
    {"host": "10.0.0.1", "port": 6379},
    {"host": "10.0.0.2", "port": 6379},
]
rc = ValkeyCluster(startup_nodes=startup_nodes)

# From host/port (single startup node)
rc = ValkeyCluster(host="10.0.0.1", port=6379)

# From URL
rc = ValkeyCluster.from_url("valkey://10.0.0.1:6379")

# With options
rc = ValkeyCluster(
    host="10.0.0.1",
    port=6379,
    require_full_coverage=False,   # allow partial slot coverage
    read_from_replicas=False,       # read only from primaries
    reinitialize_steps=5,           # steps before full topology refresh on MOVED
    cluster_error_retry_attempts=3, # retries on cluster errors
    dynamic_startup_nodes=True,     # update startup nodes from discovered topology
    decode_responses=True,
    username="default",
    password="secret",
)
```

### Constructor Parameters

| Parameter | Default | Description |
|---|---|---|
| `host` | `None` | Host of a startup node |
| `port` | `6379` | Port of a startup node |
| `startup_nodes` | `[]` | List of `{"host": ..., "port": ...}` dicts or `ClusterNode` objects |
| `require_full_coverage` | `False` | If True, all 16384 slots must be covered at init |
| `read_from_replicas` | `False` | Route READ commands to replicas (round-robin) |
| `reinitialize_steps` | `5` | MOVED errors before full topology reinit |
| `cluster_error_retry_attempts` | `3` | Retries on TimeoutError/ConnectionError/ClusterDownError |
| `dynamic_startup_nodes` | `True` | Replace startup nodes with discovered topology |
| `address_remap` | `None` | Callable `(host, port) -> (host, port)` for address mapping |
| `url` | `None` | URL of a startup node |

## Hash Slots and Key Routing

Valkey Cluster uses 16384 hash slots. Each key is assigned to a slot via `CRC16(key) % 16384`.

```python
from valkey.crc import key_slot

slot = key_slot("mykey")  # e.g., 12182
```

### Hash Tags

Force keys to the same slot using `{tag}` syntax:

```python
# These keys always hash to the same slot
r.hset("user:{42}", "name", "Alice")
r.hset("user:{42}", "email", "alice@example.com")
r.delete("user:{42}")

# Works with any command that takes multiple keys
r.mget("session:{abc}:token", "session:{abc}:data")
r.rename("old:{tag}", "new:{tag}")
```

The hash tag is the portion between the first `{` and the next `}`. If no `{` is found, the entire key is used for hashing.

## Cluster Commands

Most single-node commands work transparently in cluster mode. The client routes each command to the correct node.

```python
# Key-based commands — routed to the correct slot
rc.set("key", "value")
rc.get("key")
rc.delete("key")

# Multi-key commands — all keys must be in the same slot
rc.mget("user:{1}:name", "user:{1}:email")
rc.mset({"user:{1}:name": "Alice", "user:{1}:email": "a@b.com"})

# Commands that span all nodes
rc.info()       # merged from all nodes
rc.dbsize()     # merged from all nodes
rc.flushall()   # executed on all nodes
rc.flushdb()    # executed on all nodes
```

### Commands That Require Same Slot

Multi-key commands in cluster mode require all keys to hash to the same slot:

- `MGET`, `MSET`, `DEL` (with multiple keys)
- `RENAME`, `RENAMENX`
- `SUNIONSTORE`, `SINTERSTORE`, `SDIFFSTORE`
- `ZUNIONSTORE`, `ZINTERSTORE`
- `EVAL` with multiple KEYS

Use hash tags `{tag}` to ensure co-location.

## Cluster Pipelines

```python
# Basic pipeline
pipe = rc.pipeline()
pipe.set("key1", "value1")
pipe.get("key1")
results = pipe.execute()

# Transactional pipeline (same slot required)
pipe = rc.pipeline(transaction=True)
pipe.watch("user:{42}:balance")
balance = int(rc.get("user:{42}:balance") or 0)
pipe.multi()
pipe.set("user:{42}:balance", balance - 100)
pipe.execute()
```

## Cluster Scanning

```python
# Scan across all nodes
for key in rc.scan_iter(match="user:*"):
    print(key)

# HSCAN, SSCAN, ZSCAN — routed to the correct node
for field, value in rc.hscan_iter("myhash"):
    print(field, value)
```

## Cluster Topology

```python
# Get cluster nodes info
nodes = rc.get_nodes()

# Get cluster info
info = rc.cluster_info()

# Get cluster slots mapping
slots = rc.cluster_slots()

# Get cluster shards (Valkey 7+)
shards = rc.cluster_shards()

# Meet a new node
rc.cluster_meet("10.0.0.5", 6379)

# Add/Remove slots
rc.cluster_addslots(1, 2, 3)
rc.cluster_delslots(1, 2, 3)

# Failover
rc.cluster_failover()
rc.cluster_failover("FORCE")
rc.cluster_failover("ABORT")

# Reset
rc.cluster_reset("SOFT")
rc.cluster_reset("HARD")

# Key slot
rc.cluster_keyslot("mykey")

# Count key slots
rc.cluster_countkeysinslot(100)

# Get keys from slot
rc.cluster_getkeysinslot(100, 10)
```

## Read from Replicas

Enable stale reads from replicas:

```python
rc = ValkeyCluster(
    host="10.0.0.1",
    port=6379,
    read_from_replicas=True,  # read commands go to replicas round-robin
)

# GET, MGET, STRLEN, EXISTS, etc. may hit replicas
# SET, DEL, INCR, etc. always hit primaries
```

Read commands are identified by the `READ_COMMANDS` set in `valkey.commands.cluster`. Write commands always route to primaries.

## Cluster Error Handling

```python
from valkey.exceptions import (
    ClusterDownError,
    AskError,
    MovedError,
    TryAgainError,
    ClusterCrossSlotError,
    SlotNotCoveredError,
)

try:
    rc.set("key", "value")
except ClusterDownError:
    # Cluster has uncovered slots and require-full-coverage is set
    pass
except ClusterCrossSlotError:
    # Multi-key command with keys in different slots
    # Fix: use hash tags
    pass
except SlotNotCoveredError:
    # No node covers the required slot
    # Topology may need refresh
    pass
```

### Automatic Redirection

- **MOVED** — Key moved to another node. Client updates its slot map and retries.
- **ASK** — Key is migrating. Client redirects to target node with `ASKING` command.
- **TRYAGAIN** — Operation retry during resharding. Client retries automatically.

## Cluster Lock

```python
from valkey.lock import Lock

lock = Lock(rc, "my-lock", timeout=10, sleep=0.1)
if lock.acquire():
    try:
        pass
    finally:
        lock.release()
```

Distributed locks work in cluster mode but require the lock key to be accessible (use hash tags if the lock is related to other keys).

## Closing

```python
rc.close()  # Disconnects all connections in the cluster
```

## Gotchas

- **`db` parameter is ignored** — Cluster mode only supports db=0. Passing `db` raises `ValkeyClusterException`.
- **Multi-key commands need same slot** — Use `{hash-tags}` to force co-location.
- **`KEYS` command is not supported** — Use `SCAN` / `scan_iter()` instead.
- **`SELECT` is not supported** — There is no database selection in cluster mode.
- **`read_from_replicas` enables stale reads** — Data may be slightly behind the primary. Only use for read-heavy, tolerance-to-staleness workloads.
- **`require_full_coverage=True` fails on partial clusters** — If not all 16384 slots are covered, the client refuses to initialize. Leave as `False` for development or partial deployments.
- **Cluster pipelines require same-slot keys** — Unlike single-node pipelines, cluster pipelines enforce slot consistency.
