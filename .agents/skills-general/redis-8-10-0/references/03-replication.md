# Replication

Redis supports asynchronous primary-replica replication with automatic full sync and partial resync.

## Basic Setup

```bash
# On replica
redis-cli REPLICAOF <primary-ip> <primary-port>
# or in redis.conf:
# replicaof <primary-ip> <primary-port>
```

**Config:**
- `replicaof` — set primary (also via `REPLICAOF` command)
- `replica-read-only yes` — replicas reject writes (default yes)
- `replica-serve-stale-data yes` — serve stale data during sync (default yes)
- `replica-priority 100` — priority for Sentinel failover (lower = preferred)
- `replica-ignore-maxmemory yes` — ignore maxmemory on replicas (default yes)

## Full Sync

When a replica connects or is too far behind:
1. Primary forks and produces an RDB snapshot
2. RDB is transferred to replica
3. Replica loads RDB and catches up with buffered commands

### Diskless Sync

```
repl-diskless-sync yes              # default: yes
repl-diskless-sync-delay 5          # wait 5s for more replicas to join
repl-diskless-sync-max-replicas 0   # 0 = unlimited
```

With diskless sync, the primary streams RDB directly to replicas without writing to disk. The delay allows multiple replicas to join a single sync session.

### Diskless Load (on replicas)

```
repl-diskless-load disabled         # default: store to disk first
# Options:
#   disabled  — write to disk, then load (safe, uses disk I/O)
#   on-empty-db — load directly into memory (only if DB is empty)
#   swapdb    — load into a swap DB, then swap (faster, uses 2x memory)
```

## Partial Resync

When a replica briefly disconnects, it can resume from the replication backlog instead of doing a full sync.

**Config:**
- `repl-backlog-size` — size of the replication backlog buffer (default 1MB)
- `repl-backlog-ttl` — how long to keep backlog after last replica disconnects (default 3600s)

Partial resync works when the replica's missing data is still in the backlog. Monitor with `INFO replication`.

## Replication Stream Compression (new in 8.10)

Compress the replication stream to reduce bandwidth between primary and replicas. Requires `BUILD_COMPRESSION=yes` at build time (links libzstd).

**Config:**
- `enable-repl-compression no` — enable compression (requires build flag)
- `repl-compression-level 3` — compression level 1-22 (default 3)

Higher levels reduce bandwidth but increase CPU on the primary. Useful for WAN replication or bandwidth-constrained environments.

**Build:**
```bash
make BUILD_COMPRESSION=yes
```

Requires libzstd development headers. Without it, compression is a no-op.

## Replication Commands

- `REPLICAOF` — change primary at runtime
- `READ ONLY` / `READ WRITE` — change replica read-only mode
- `PSYNC` — internal sync command (used by replicas)
- `INFO replication` — replication status
- `DEBUG RELOAD` — force full resync (testing only)

## Dual-Channel Replication

Redis 8.x supports dual-channel replication where the primary uses separate connections for data replication and PubSub/message propagation. This reduces head-of-line blocking.

## Replica Authentication

```
masterauth <password>    # password to use when this instance becomes primary
requirepass <password>   # password replicas must use to connect
```

## Monitoring Replication

```bash
redis-cli INFO replication
# Key fields:
#   role: master|slave
#   connected_slaves: N
#   slave0: ip:port@bus-port,state,state,...
#   master_repl_offset: N
#   slave_repl_offset: N
#   second_repl_offset: N  (dual-channel)
```

## Gotchas

- **`repl-diskless-sync yes` is the default** — RDB streams directly without touching disk on primary
- **`repl-diskless-load disabled` is the default** — replicas write to disk first for safety
- **Backlog size matters** — set `repl-backlog-size` large enough to cover expected network blips
- **Compression requires build flag** — `BUILD_COMPRESSION=yes` and libzstd at build time
- **Replicas inherit maxmemory** — but `replica-ignore-maxmemory yes` is default, so eviction is driven by primary's DEL commands
- **`replica-read-only yes` can be overridden** — use `READ WRITE` to allow writes on replicas (for read-heavy setups with occasional writes)
- **Full sync blocks writes on primary** — briefly, during fork. Large datasets mean longer forks. Use `repl-diskless-sync` to minimize impact.
