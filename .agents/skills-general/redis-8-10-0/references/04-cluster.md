# Cluster Mode

Redis Cluster provides horizontal scaling through data sharding across multiple nodes using 16,384 hash slots.

## Architecture

- **16,384 hash slots** — each key maps to a slot via `CRC16(key) & 0x3FFF`
- **Hash tags** — `{user1000}.profile` and `{user1000}.settings` hash to the same slot, enabling multi-key operations
- **Primary-replica pairs** — each slot is owned by one primary, with configurable replicas for failover
- **Gossip protocol** — nodes exchange state via cluster bus (separate from client port)

## Configuration

```
cluster-enabled yes
cluster-config-file nodes-6379.conf
cluster-node-timeout 15000          # ms before node is marked PFAIL
cluster-require-full-coverage yes   # reject writes if any slot range is uncovered
cluster-migration-barrier 1         # min replicas before primary migration allowed
cluster-allow-reads-when-down no    # allow reads when cluster is DOWN
cluster-allow-reads-when-cluster-down no
cluster-announce-ip <ip>            # override advertised IP (NAT)
cluster-announce-port <port>        # override advertised client port
cluster-announce-bus-port <port>    # override advertised bus port
cluster-announce-hostname <name>    # advertise hostname instead of IP
cluster-migration-disallow-1-primary-shard no
cluster-allow-auth-pw-diff no       # allow different auth passwords across nodes
cluster-auth-trust-users no         # trust ACL users from other nodes
```

## Creating a Cluster

```bash
# Using redis-cli --cluster
redis-cli --cluster create \
  127.0.0.1:7000 127.0.0.1:7001 \
  127.0.0.1:7002 127.0.0.1:7003 \
  127.0.0.1:7004 127.0.0.1:7005 \
  --cluster-replicas 1

# Check cluster info
redis-cli --cluster check 127.0.0.1:7000

# Reshard data
redis-cli --cluster reshard 127.0.0.1:7000
```

## Cluster Commands

- `CLUSTER INFO` — cluster state, slots assigned, known nodes
- `CLUSTER NODES` — list all nodes and their roles
- `CLUSTER MEET <ip> <port>` — add a node to the cluster
- `CLUSTER FORGET <node-id>` — remove a node
- `CLUSTER ADDSLOTS <slot> [slot ...]` — assign slots to current node
- `CLUSTER DELSLOTS <slot> [slot ...]` — remove slots from current node
- `CLUSTER REPLICATE <node-id>` — set current node as replica of another
- `CLUSTER SAVECONFIG` — force config save
- `CLUSTER SET-SLOT <slot> NODE <node-id>` — assign slot to node
- `CLUSTER SET-SLOT <slot> MIGRATING <node-id>` — start migration
- `CLUSTER SET-SLOT <slot> IMPORTING <node-id>` — start import
- `CLUSTER SET-SLOT <slot> STABLE` — cancel migration/import
- `CLUSTER KEYSLOT <key>` — compute slot for a key
- `CLUSTER COUNTKEYSINSLOT <slot>` — count keys in slot
- `CLUSTER GETKEYSINSLOT <slot> <count>` — get keys in slot
- `CLUSTER FAILOVER [FORCE|TAKEOVER]` — trigger failover on replica
- `CLUSTER MYID` — get current node's ID
- `CLUSTER REPLICAS <node-id>` — list replicas of a node
- `CLUSTER SLOTES` — list slot ranges
- `CLUSTER LINKS` — show cluster bus link state
- `CLUSTER MYSHARDID` — get current shard ID
- `CLUSTER SHARDID <node-id>` — get shard ID for a node
- `CLUSTER SYSTEM-ENABLE-XXHASH64` — enable xxHash-64 for slot hashing

## Slot Migration

Atomic slot migration allows resharding without downtime:

1. `CLUSTER SET-SLOT <slot> MIGRATING <source-node>` on source
2. `CLUSTER SET-SLOT <slot> IMPORTING <dest-node>` on destination
3. Keys are migrated via `MIGRATE` or automatic migration
4. `CLUSTER SET-SLOT <slot> NODE <dest-node>` on all nodes
5. `CLUSTER SET-SLOT <slot> STABLE` on source and destination

## Cross-Slot Operations

Multi-key commands require all keys to be in the same slot:
- Use hash tags: `{user1000}.name` and `{user1000}.email`
- For `MGET`/`MSET` across slots, use `redis-cli --cluster` which auto-routes
- `CLUSTER KEYSCAN` for cross-slot key scanning

## Redirection Errors

- `-MOVED <slot> <node>` — slot moved to another node (update mapping)
- `-ASK <slot> <node>` — slot is being migrated, ask the target
- `-CLUSTERDOWN` — cluster is not fully covered or in error state
- `-CROSSSLOT` — keys in different slots in a multi-key command

## Cluster Pub/Sub

- `PUBLISH` — broadcast to all nodes (every node delivers locally)
- `PSUBSCRIBE`/`PUBSUBSCRIBE` — shard channels for distributed pub/sub
- Cluster pub/sub does not guarantee delivery ordering across nodes

## Gotchas

- **`cluster-require-full-coverage yes` is the default** — the entire cluster goes down if any slot range is uncovered. Set to `no` to allow partial operation.
- **`cluster-node-timeout` controls failover speed** — too low causes flapping, too high means slow failover. 15000ms (15s) is the default.
- **Hash tags must be properly formed** — `{tag}` with both braces present. `{` without `}` or empty `{}` falls back to full-key hashing.
- **`CLUSTER MEET` is asynchronous** — the node may not appear in `CLUSTER NODES` immediately. Wait for gossip convergence.
- **Cluster ignores `databases`** — use `cluster-databases` instead (default 1 DB in cluster mode).
- **`MIGRATE` with `AUTH`** — if nodes have different passwords, include `AUTH <password>` in MIGRATE commands.
- **Link send buffers can grow unbounded** on slow peers. Monitor with `CLUSTER LINKS`.
- **`cluster-allow-auth-pw-diff no` by default** — all nodes must share the same auth password. Enable to allow different passwords per node.
- **Atomic slot migration requires careful ordering** — use `redis-cli --cluster reshard` for automated migration.
