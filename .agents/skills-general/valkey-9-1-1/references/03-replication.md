# Replication

Valkey supports asynchronous primary-replica replication with automatic partial resynchronization.

## Basic Setup

```conf
# On the replica
replicaof <primary-ip> <primary-port>

# If primary requires auth
primaryauth <password>

# Or use a dedicated ACL user for replication
primaryuser <username>
```

Or at runtime:

```bash
# On the replica instance
valkey-cli REPLICAOF 10.0.0.1 6379
# Stop replicating (become primary)
valkey-cli REPLICAOF NO ONE
```

## Full Synchronization

When a new replica connects or partial sync is not possible:

1. Primary forks a child process
2. Child writes an RDB snapshot (to disk or directly to socket)
3. RDB is transferred to the replica
4. Replica loads the RDB and starts receiving incremental commands

### Diskless replication (default)

```conf
# Primary streams RDB directly to replica sockets (no disk I/O)
repl-diskless-sync yes

# Delay before starting transfer (let multiple replicas connect)
repl-diskless-sync-delay 5

# Max replicas to wait for (0 = unlimited)
repl-diskless-sync-max-replicas 0
```

### Replica diskless load

```conf
# disabled   — store RDB to disk first (default, safest)
# on-empty-db — diskless load only when replica dataset is empty
# swapdb      — keep old dataset in RAM while loading new one (higher memory)
# flush-before-load — [dangerous] flush before parsing
repl-diskless-load disabled
```

## Dual-Channel Replication

Optimizes full sync by separating RDB transfer from replication stream:

```conf
# Enable on both primary and replicas
dual-channel-replication-enabled no
```

**How it works:** The primary's bgsave process streams the RDB snapshot over a separate connection while the replication buffer carries incremental commands. This reduces memory and CPU load on the primary but shifts buffer burden to the replica.

**Requirements:** Primary must have `repl-diskless-sync yes`. Replica must have sufficient memory for the replication buffer.

## Partial Resynchronization

When the replication link is briefly lost, the replica can resume from where it left off using the replication backlog:

```conf
# Backlog size — larger = longer disconnect tolerance
repl-backlog-size 10mb

# Free backlog after this many seconds with no replicas
repl-backlog-ttl 3600
```

The backlog is only allocated when at least one replica is connected.

## Replica behavior

```conf
# Serve stale data when disconnected from primary
replica-serve-stale-data yes

# Read-only mode (default)
replica-read-only yes

# Priority for Sentinel promotion (lower = preferred, 0 = never promote)
replica-priority 100

# Replica ignores its own maxmemory (eviction driven by primary)
replica-ignore-maxmemory yes

# Lazy flush during full resync
replica-lazy-flush yes

# Exclude from Sentinel announcements (still eligible for promotion)
replica-announced yes
```

## Network tuning

```conf
# Ping interval (seconds)
repl-ping-replica-period 10

# Timeout for replication operations
repl-timeout 60

# Disable TCP_NODELAY (batch packets, reduce bandwidth, add latency)
repl-disable-tcp-nodelay no

# MPTCP for replication (Linux 5.6+)
repl-mptcp no

# Announce different IP/port (NAT scenarios)
replica-announce-ip 5.5.5.5
replica-announce-port 1234
```

## Minimum replicas

Require N replicas with lag ≤ M seconds before accepting writes:

```conf
min-replicas-to-write 3
min-replicas-max-lag 10
```

## Failover

Replicas can be promoted to primary via:

1. **Sentinel** — automatic failover (recommended for HA)
2. **Manual** — `CLUSTER FAILOVER` in cluster mode
3. **CLI** — `REPLICAOF NO ONE` (manual demotion)

### Propagation errors

```conf
# How to handle errors in replicated commands
# ignore (default) — skip the error
# panic — crash the server
# panic-on-replicas — crash only on replicas
propagation-error-behavior ignore
```

## INFO replication

Check replication status:

```bash
valkey-cli INFO replication
```

Key fields: `role`, `connected_replicas`, `repl_backlog_active`, `master_repl_offset`, `second_repl_offset`, `replica_last_io`, `replica_read_only`
