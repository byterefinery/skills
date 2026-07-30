# Cluster Mode

Valkey Cluster provides horizontal scaling through data partitioning across multiple nodes using a sharded architecture with automatic failover.

## Architecture

- **16384 hash slots** distributed across shard (primary) nodes
- Each key is mapped to a slot via `CRC16(key) mod 16384`
- Each primary can have zero or more replicas
- Nodes communicate via a **cluster bus** (separate from client connections)
- Minimum recommended: 3 shards (primary + replica each = 6 nodes)

## Configuration

```conf
cluster-enabled yes
cluster-config-file nodes-6379.conf
cluster-node-timeout 15000

# Allow reads when cluster is partially down
cluster-require-full-coverage yes

# Replica migration to orphaned primaries
cluster-migration-barrier 1
cluster-allow-replica-migration yes

# Replica failover restrictions
cluster-replica-validity-factor 10
cluster-replica-no-failover no

# Manual failover timeout
cluster-manual-failover-timeout 5000

# Allow reads during cluster-down state
cluster-allow-reads-when-down no

# Pub/Sub during cluster-down
cluster-allow-pubsubshard-when-down yes

# Cluster config save behavior
# sync (default) — exit on save failure
# best-effort — log warning and continue
cluster-config-save-behavior sync

# Per-slot statistics tracking
cluster-slot-stats-enabled no

# Announce hostname (for SNI / DNS routing)
cluster-announce-hostname ""
cluster-preferred-endpoint-type ip

# Docker/NAT support
# cluster-announce-ip 10.1.1.5
# cluster-announce-port 6379
# cluster-announce-bus-port 16379
```

## Creating a Cluster

```bash
# Using valkey-cli (create 3 shards with 1 replica each)
./src/valkey-cli --cluster create \
  127.0.0.1:7000 127.0.0.1:7001 \
  127.0.0.1:7002 127.0.0.1:7003 \
  127.0.0.1:7004 127.0.0.1:7005 \
  --cluster-replicas 1

# Using create-cluster utility
./utils/create-cluster start
./utils/create-cluster create
```

## Cluster Commands

**Topology:** `CLUSTER NODES`, `CLUSTER SHARDS`, `CLUSTER SLOTS`, `CLUSTER MYID`, `CLUSTER MYSHARDID`, `CLUSTER LINKS`, `CLUSTER SAVECONFIG`, `CLUSTER FORGET <node-id>`, `CLUSTER MEET <ip> <port>`

**Slot management:** `CLUSTER KEYSLOT <key>`, `CLUSTER COUNTKEYSINSLOT <slot>`, `CLUSTER GETKEYSINSLOT <slot> <count>`, `CLUSTER COUNT-FAILURE-REPORTS <node-id>`

**Failover:** `CLUSTER FAILOVER` (manual), `CLUSTER FAILOVER FORCE`, `CLUSTER FAILOVER TAKEOVER`

**Info:** `CLUSTER INFO`, `CLUSTER REPLICAS <node-id>`, `CLUSTER REPLICATE <node-id>`

**Slot operations:** `CLUSTER SETSLOT <slot> NODE <node-id>`, `CLUSTER SETSLOT <slot> MIGRATING/IMPORTING <node-id>`, `CLUSTER FLUSHSLOT <slot>`, `CLUSTER FLUSHSLOTS` (careful — removes all keys)

**Reseting:** `CLUSTER RESET HARD`/`SOFT`

**New 9.1 commands:** `CLUSTERSCAN` (cluster-wide key scanning), `CLUSTER GETSLOTMIGRATIONS`, `CLUSTER CANCELSLOTMIGRATIONS`, `CLUSTER BUMPEPOCH`, `CLUSTER SLOT-STATS`

## Atomic Slot Migration (ASM)

Replaces the legacy `SET SLOT MIGRATING/IMPORTING` + `MIGRATE` approach. Uses replication primitives for seamless, atomic slot transfers.

```bash
# Migrate slots 0-5000 from source to target
./src/valkey-cli --cluster migrate-source <source-id> <target-host> <target-port> \
  --from <source-host> --from-port <source-port> \
  --slots 0-5000

# Or via CLUSTER MIGRATESLOTS command
valkey-cli CLUSTER MIGRATESLOTS <target-node-id> 0 1 2 ... 5000
```

**ASM phases:**
1. **ESTABLISH** — source and target coordinate
2. **Snapshot transfer** — source serializes slot keys in AOF format
3. **Incremental updates** — changes during snapshot are replayed
4. **PAUSE** — source pauses writes to migrating slots
5. **FAILOVER** — atomic ownership transfer (like manual failover)
6. **Cleanup** — source removes migrated keys

**Monitoring:** `CLUSTER GETSLOTMIGRATIONS`, `CLUSTER CANCELSLOTMIGRATIONS`

**Config:** `slot-migration-max-failover-repl-bytes` controls pause threshold.

## Cluster Links

The cluster bus carries gossip, failover votes, slot ownership, and Pub/Sub shard messages.

```conf
# Limit send buffer per link (prevent unbounded growth)
cluster-link-sendbuf-limit 0
```

Monitor with `CLUSTER LINKS` and `INFO cluster` (includes `cluster_bus_messages_sent`/`received` and traffic usage metrics since 9.1).

## Cluster-aware clients

Clients must handle `MOVED` and `ASK` redirect responses. In `cluster-require-full-coverage no` mode, the cluster serves partial key space when some slots are uncovered.

## Hash tags

Force keys into the same slot using `{tag}` syntax:

```
SET {user1000}:profile "data"
SET {user1000}:settings "data"
# Both keys hash to the same slot
```

## Cross-slot operations

Multi-key commands (e.g., `MGET`, `SUNION`) require all keys to be in the same slot. Use hash tags or `CLUSTER KEYSLOT` to verify.

## Availability zone

```conf
availability-zone "zone-name"
```

Exposed in `INFO` and `HELLO` commands. `CLUSTER SHARDS`/`CLUSTER SLOTS` include `availability-zone` field since 9.1.
