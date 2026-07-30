# Persistence

Valkey supports two persistence mechanisms: RDB snapshots and AOF (Append Only File). Both can be enabled simultaneously — on startup, AOF is loaded preferentially (better durability).

## RDB Snapshots

Point-in-time binary snapshots of the dataset. Created by forking a child process that iterates the dataset and writes to disk.

### Configuration

```conf
# Save triggers: save <seconds> <changes> [<seconds> <changes> ...]
save 3600 1 300 100 60 10000

# Disable all snapshotting
# save ""

# RDB file name and location
dbfilename dump.rdb
dir ./

# Compression (LZF, enabled by default)
rdbcompression yes

# CRC64 checksum at end of file
rdbchecksum yes

# Stop accepting writes if bgsave fails
stop-writes-on-bgsave-error yes

# Incremental fsync during RDB save (reduces latency spikes)
rdb-save-incremental-fsync yes

# Future-version RDB loading: strict (default) or relaxed
rdb-version-check strict
```

### Commands

- `BGSAVE` — trigger background save (forks child)
- `SAVE` — blocking save (blocks main thread, use only for debugging)
- `LASTSAVE` — timestamp of last successful save
- `DEBUG RELOAD` — save + restart (development only)

### Checking RDB integrity

```bash
./src/valkey-check-rdb dump.rdb
```

## AOF (Append Only File)

Logs every write command. On restart, Valkey replays the AOF to reconstruct the dataset.

### Multi-part AOF (since 7.0)

AOF uses a set of files managed by a manifest:

```
appendonlydir/
├── appendonly.aof.manifest       # tracks file order
├── appendonly.aof.1.base.rdb     # base file (RDB or AOF format)
├── appendonly.aof.1.incr.aof     # incremental commands
├── appendonly.aof.2.incr.aof     # more incremental commands
```

### Configuration

```conf
appendonly yes
appendfilename "appendonly.aof"
appenddirname "appendonlydir"

# fsync policy
# appendfsync always      # safest, slowest
appendfsync everysec      # default — ~1 second of data loss max
# appendfsync no          # fastest, OS-controlled flushing

# Don't fsync during BGSAVE/BGREWRITEAOF (latency tradeoff)
no-appendfsync-on-rewrite no

# Auto-rewrite triggers
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Load truncated AOF on startup (recover partial data)
aof-load-truncated yes

# Use RDB preamble for base files (faster loading)
aof-use-rdb-preamble yes

# Timestamp annotations in AOF (point-in-time restore)
aof-timestamp-enabled no
```

### Commands

- `BGREWRITEAOF` — trigger background AOF rewrite (compacts the log)
- `LASTSAVE` — also reflects last AOF rewrite time

### Checking AOF integrity

```bash
./src/valkey-check-aof appendonlydir/appendonly.aof.1.incr.aof
# Repair mode:
./src/valkey-check-aof --fix appendonlydir/appendonly.aof.1.incr.aof
```

## Durability Tradeoffs

| Mode | Data Loss Risk | Performance Impact |
|---|---|---|
| RDB only (save 60 10000) | Up to minutes | Low — fork + child process |
| AOF `always` | At most 1 write | High — fsync on every write |
| AOF `everysec` (default) | Up to ~1 second | Low-moderate |
| AOF `no` | Up to OS flush interval | Lowest |
| RDB + AOF `everysec` | Up to ~1 second | Low-moderate |

## Choosing a strategy

- **Cache / acceptable data loss**: RDB only or AOF `no`
- **Balanced durability/performance**: AOF `everysec` (default recommendation)
- **Maximum durability**: AOF `always` (significant latency cost)
- **Replicated setups**: RDB is often sufficient since replicas provide redundancy

## Conversion

To switch persistence modes on a running server:

```bash
# Enable AOF on a running server that uses only RDB
valkey-cli CONFIG SET appendonly yes

# Disable AOF (ensure at least one RDB save point is configured)
valkey-cli CONFIG SET appendonly no
```

After changing via CONFIG, update `valkey.conf` and run `CONFIG REWRITE` to persist.

## Payload sanitization

```conf
# Sanitize RDB/RESTORE payloads to prevent corruption attacks
# Options: no, yes, clients
# Default: no (temporarily, due to cluster resharding impact)
sanitize-dump-payload no
```

Set to `clients` to sanitize only user-facing RESTORE commands, or `yes` for full sanitization including replication.
