# Cluster

Source: docs/clustering.rst, docs/retry.rst, `valkey/cluster.py`, `valkey/commands/cluster.py`.

## Creating a Cluster Client

At least one startup node is required for discovery. Three forms:

```python
from valkey.cluster import ValkeyCluster, ClusterNode

# 1. host/port
rc = ValkeyCluster(host='localhost', port=6379)

# 2. URL
rc = ValkeyCluster.from_url("valkey://localhost:6379/0")

# 3. explicit nodes
nodes = [ClusterNode('localhost', 6379), ClusterNode('localhost', 6378)]
rc = ValkeyCluster(startup_nodes=nodes)
```

If no startup node is reachable, a `ValkeyClusterException` is thrown. On init the client builds three caches: a slots cache (16384 slots → nodes), a nodes cache (`ClusterNode` objects), and a commands cache (server `COMMAND` output).

## Routing and `target_nodes`

Key-based commands route to the node owning the key's slot. Non-key-based commands accept a `target_nodes` kwarg; best practice is to use the class flags:

```python
rc.cluster_meet('127.0.0.1', 6379, target_nodes=ValkeyCluster.ALL_NODES)
rc.ping(target_nodes=ValkeyCluster.REPLICAS)
rc.ping(target_nodes=ValkeyCluster.RANDOM)
rc.keys(target_nodes=ValkeyCluster.ALL_NODES)   # [b'foo1', b'foo2']
rc.bgsave(ValkeyCluster.PRIMARIES)
```

Flags (class attributes in `valkey/cluster.py`): `PRIMARIES`, `REPLICAS`, `ALL_NODES`, `RANDOM` (plus an internal `DEFAULT_NODE`). Without `target_nodes`, non-key commands run on the cluster's default node (a random primary, updated on reinitialization). Inspect/override with `rc.get_default_node()` / `rc.set_default_node(node)`.

You may also pass `ClusterNode` objects directly, but note: if the topology changed, **no retry** is made for explicitly passed nodes (flags are re-resolved, raw nodes are not). Use `rc.get_node(host=..., port=...)` to fetch one, or reach into a node's raw connection via `cluster_node.valkey_connection` (that client does not handle cluster failures/retries).

Other helpers: `rc.get_nodes()`, `rc.get_primaries()`, `rc.get_replicas()`, `rc.get_random_node()`, `rc.get_node_from_key(key, replica=False)`.

## Multi-Key Commands

- **Atomic** multi-key operations (`mset`, `mget`, set unions/intersections, ...) require all keys to hash to the same slot, else a cluster exception is raised. Force co-location with **hash tags**: `rc.mset({'{foo}1': 'bar1', '{foo}2': 'bar2'})`.
- **Non-atomic** variants split keys by slot and batch per slot owner: `rc.mset_nonatomic({'foo': 'value1', 'bar': 'value2'})`, `rc.mget_nonatomic('foo', 'bar')` (defined in `valkey/commands/cluster.py`).

## Pub/Sub on Cluster

- A `ClusterPubSub` created without a node picks one transparently on first use: hash the channel name → keyslot → node handling that slot (a replica may be selected when `read_from_replicas=True`).
- Pin a node explicitly: `rc.pubsub(node)` / `rc.pubsub(host=..., port=...)`.
- **Pattern subscribe/publish do not work properly** (a pattern like `fo*` has no determinable keyslot) — the commands exist but are not recommended.

## Read-Only / Replica Reads

By default Valkey Cluster returns MOVE redirects to replicas. Enable `read_from_replicas=True` in the constructor to spread read commands between a primary and its replicas round-robin. It can also be toggled at runtime: `readonly(target_nodes=...)` and `readwrite()` (e.g. `rc.readwrite(target_nodes='replicas')`).

## Retry Semantics (Cluster)

Two tiers (docs/retry.rst):

- `retry`: `Retry` instance for reconnect attempts to a failing node. **Default `Retry(NoBackoff(), 0)`** (no retries).
- `cluster_error_retry_attempts`: how many times to retry (with a cluster re-initialization that removes the failed node from startup nodes) when `TimeoutError`, `ConnectionError`, or `ClusterDownError` is encountered. **Default 3**.

Flow: connect → on failure retry to that node up to `retry` → still failing → cluster update/re-init (one of `cluster_error_retry_attempts`) → new retry cycle → finally raise.

Also available at runtime: `rc.get_retry()` / `rc.set_retry(retry)`.
