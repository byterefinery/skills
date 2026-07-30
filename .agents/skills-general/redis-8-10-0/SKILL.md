---
name: redis-8-10-0
description: >
  Build, configure, and operate Redis 8.10.0 — the in-memory data store, cache, and query engine.
  Covers building from source (Makefile, modules system), running the server, configuration,
  data types (strings, hashes, lists, sets, sorted sets, streams, arrays, vector sets),
  persistence (RDB, AOF, MP-AOF, BACKUP), replication with stream compression,
  Cluster mode, Sentinel, ACL security, module API, TLS, Lua scripting, Pub/Sub,
  and testing. Use when working with Redis server source, deploying instances,
  writing modules, tuning performance, or debugging cluster/sentinel setups.
  Redis 8.10 adds compact hashes, HIMPORT, BACKUP, replication stream compression,
  LMOVEM/BLMOVEM, SUNIONCARD, SDIFFCARD, and more.
license: RSALv2 / SSPLv1 / AGPLv3
compatibility: Requires GCC 9+ or Clang 12+, libzstd (for BUILD_COMPRESSION), Tcl 8.6+ (for tests)
metadata:
  tags:
    - database
    - nosql
    - in-memory
    - cache
    - key-value
    - vector-search
---

# redis 8.10.0

Redis 8.10.0 is the GA release (July 2026) of Redis Open Source. It introduces compact hashes for reduced memory usage, the `HIMPORT` command for high-throughput bulk hash insertion, the `BACKUP` command for node-side multi-part AOF backups, replication stream compression, and new list/set commands.

## Overview

Redis serves as a key-value store, cache, data structure server, message broker, streaming platform, and vector query engine. It supports rich native data structures (strings, hashes, lists, sets, sorted sets, streams, arrays, vector sets) and an extensible module system for custom types and commands (JSON, Search, TimeSeries, Bloom).

**Core binaries produced by build:**

| Binary | Purpose |
|---|---|
| `redis-server` | Main server daemon |
| `redis-cli` | Command-line client |
| `redis-benchmark` | Performance benchmarking tool |
| `redis-check-rdb` | RDB file integrity checker |
| `redis-check-aof` | AOF file integrity checker / repair tool |

## Building

### Standard build

```bash
# Clone and build
git clone --branch 8.10.0 https://github.com/redis/redis.git
cd redis
make

# With TLS support (built-in)
make BUILD_TLS=yes

# With TLS as loadable module
make BUILD_TLS=module

# With replication stream compression (requires libzstd)
make BUILD_COMPRESSION=yes

# With systemd integration
make USE_SYSTEMD=yes

# With enhanced stack traces (libbacktrace)
make USE_LIBBACKTRACE=yes

# Without Lua scripting engine
make BUILD_LUA=no

# Custom allocator
make MALLOC=jemalloc   # default on Linux
make MALLOC=libc       # force libc malloc

# Custom optimization
make OPTIMIZATION=-O2

# Install binaries
make install
# or: make PREFIX=/opt/redis install
```

### Modules build

Redis 8.10 uses a manifest-driven module system (`modules/modules.yaml`). Bundled modules include RedisBloom, RediSearch, RedisJSON, and RedisTimeSeries.

```bash
# Build Redis core + all cloned modules
make build

# Build specific modules
make build redistimeseries redisjson

# Update/clone module sources
make modules-update
make modules-update redisjson

# Bootstrap module build dependencies
make bootstrap

# Generate redis-full.conf (redis.conf + module loadmodule lines)
make sync-redis-conf
```

Module sources are pinned in `modules/modules.yaml` and cloned into `modules/<name>/src/`. The in-tree `vector-sets` module is compiled directly into the Redis binary — no separate `.so` needed.

### Clean rebuild

```bash
# Full clean (mandatory when switching build flags)
make distclean && make

# Clean specific modules
make clean redisjson
make clean all
```

## Running

```bash
# Default config (port 6379, bind 127.0.0.1)
./src/redis-server

# With config file
./src/redis-server /path/to/redis.conf

# Override config at runtime
./src/redis-server --port 9999 --loglevel debug

# Cluster mode
./src/redis-server --cluster-enabled yes --port 7000

# Sentinel mode
./src/redis-server /path/to/sentinel.conf --sentinel

# Load modules
./src/redis-server --loadmodule ./modules/redisjson/rejson.so
```

### Client

```bash
./src/redis-cli
redis> ping
PONG
redis> set foo bar
OK
redis> get foo
"bar"

# Connect to specific host/port
./src/redis-cli -h 10.0.0.1 -p 6379

# With TLS
./src/redis-cli --tls --cert client.crt --key client.key --cacert ca.crt

# Run a single command
./src/redis-cli -e INFO server

# RESP3 mode (default in 8.x)
./src/redis-cli --no-auth-warning
```

### Benchmark

```bash
./src/redis-benchmark -n 100000 -c 50 -q
# With warmup and duration
./src/redis-benchmark -n 100000 --warmup 5 --duration 30 -q
```

## Configuration

The main config file is `redis.conf`. All directives can also be set via CLI flags or runtime `CONFIG SET`.

**Key configuration areas:**

- **Network**: `bind`, `port`, `tcp-backlog`, `tcp-keepalive`, `timeout`, `protected-mode`
- **General**: `daemonize`, `pidfile`, `loglevel`, `logfile`, `databases`, `supervised`
- **Memory**: `maxmemory`, `maxmemory-policy`, `maxmemory-samples`
- **Persistence**: `save`, `appendonly`, `appendfsync`, `rdbcompression`, `aof-use-rdb-preamble`
- **Replication**: `replicaof`, `repl-diskless-sync`, `repl-backlog-size`, `replica-read-only`
- **Cluster**: `cluster-enabled`, `cluster-config-file`, `cluster-node-timeout`
- **Security**: ACL users, `requirepass`, `rename-command`, TLS options
- **I/O threads**: `io-threads` (reads + writes offloaded to worker threads)
- **Lazy freeing**: `lazyfree-lazy-user-del`, `lazyfree-lazy-eviction`
- **Latency**: `latency-monitor-threshold`, `latency-tracking`
- **8.10 new**: `hash-max-template-entries` (compact hashes), `backupdirname`/`backup-sealed-ttl` (BACKUP), `BUILD_COMPRESSION` (replication stream compression)

Use `CONFIG GET *` to list all runtime settings. `CONFIG REWRITE` persists runtime changes back to the config file.

## Gotchas

- **`make distclean` is mandatory** when switching build flags (e.g., enabling/disabling TLS, compression, 32bit). Build options are cached until distclean.
- **Lua is statically linked by default** — use `BUILD_LUA=no` to omit it or `BUILD_LUA=module` for dynamic loading.
- **Protected mode is on by default** — the server only accepts local connections unless a password is set or `protected-mode no` is configured.
- **`save ""` disables RDB snapshotting entirely** — useful for AOF-only setups but risks data loss on crash.
- **Cluster mode ignores `databases`** — use `cluster-databases` instead (default 1 DB in cluster mode).
- **`repl-diskless-sync yes` is the default** — RDB is streamed directly to replicas without touching disk on the primary.
- **`repl-diskless-load disabled` is the default on replicas** — replicas store received RDB to disk first. Use `on-empty-db` or `swapdb` for faster replication (higher memory cost).
- **ACL `requirepass` is a compatibility layer** — it sets the password for the `default` user. Prefer explicit ACL user definitions.
- **`maxmemory` on replicas is ignored by default** (`replica-ignore-maxmemory yes`) — eviction is driven by the primary sending DEL commands.
- **`BUILD_COMPRESSION=yes` requires libzstd** — build will fail without it. Replication stream compression is opt-in and disabled by default.
- **Compact hashes require `hash-max-template-entries > 0`** — the default is 0 (disabled). Set to a value like 1024 to enable. Templates are shared across hashes with matching field schemas.
- **`HIMPORT PREPARE` is session-scoped** — fieldsets are tied to the client connection and freed on disconnect. Use `HIMPORT DISCARD`/`DISCARDALL` to clean up.
- **`BACKUP` requires MP-AOF** — the BACKUP command produces multi-part AOF backups. Ensure AOF is enabled.
- **`BACKUP` blocks BGREWRITEAOF** — a manual BGREWRITEAOF is postponed while a backup is in progress.
- **`LMOVEM`/`BLMOVEM` delete the source list** if it becomes empty after the move. Use `COUNT` (not `EXACTLY`) to avoid null replies when insufficient elements exist.
- **`SUNIONCARD`/`SDIFFCARD` support `APPROX`** — use probabilistic counting for large sets to save memory.
- **Vector Sets (VSET) are built into the binary** — no separate module needed for `VADD`, `VSIM`, etc.
- **`hash-max-template-entries` controls compact hash template cache** — set too low and templates are evicted; set too high and memory is wasted. Monitor with `INFO memory`.
- **`backup-sealed-ttl 0` disables auto-cleanup** — sealed backups persist indefinitely. Set a TTL (seconds) to auto-remove old backups.
- **`backupdirname` defaults to `"backupdir"`** — relative to the working directory. Use an absolute path for clarity.
- **`repl-compression-level` is only available with `BUILD_COMPRESSION=yes`** — levels 1-22, default 3. Higher levels reduce bandwidth but increase CPU.
- **`XREAD`/`XREADGROUP` now support `MAXCOUNT` and `MAXSIZE`** — use these to cap cumulative reply size in consumer groups.

## References

- [01-data-types](references/01-data-types.md) — Strings, Hashes (compact), Lists, Sets, Sorted Sets, Streams, Arrays, Vector Sets, Geo, HLL, Bitmaps
- [02-persistence](references/02-persistence.md) — RDB snapshots, AOF, MP-AOF, BACKUP command, durability tradeoffs
- [03-replication](references/03-replication.md) — Primary-replica setup, diskless sync, stream compression, failover
- [04-cluster](references/04-cluster.md) — Cluster mode, slot management, CLUSTER commands, cross-slot operations
- [05-sentinel](references/05-sentinel.md) — High availability with Sentinel, monitoring, automatic failover
- [06-security](references/06-security.md) — ACL system, authentication, TLS, hardened configs
- [07-modules](references/07-modules.md) — Module API, RedisJSON, RediSearch, RedisTimeSeries, RedisBloom, Vector Sets
- [08-scripting](references/08-scripting.md) — Lua scripting, Functions, EVAL/FCALL
- [09-pubsub-streams](references/09-pubsub-streams.md) — Pub/Sub (channels + shard channels), Streams (consumer groups, pending)
- [10-advanced-config](references/10-advanced-config.md) — I/O threads, lazy freeing, memory tuning, latency monitoring, compact hashes
- [11-testing](references/11-testing.md) — Unit tests, integration tests (Tcl), module tests, benchmarking
