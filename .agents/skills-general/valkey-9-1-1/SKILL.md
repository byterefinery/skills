---
name: valkey-9-1-1
description: >
  Build, configure, and operate Valkey 9.1.1 — the open-source in-memory data store forked from Redis.
  Covers building (Makefile/CMake), running the server, configuration, data types, persistence (RDB/AOF),
  replication, Cluster mode, Sentinel, ACL security, module API, TLS, Lua scripting, Streams, Pub/Sub,
  and testing. Use when working with Valkey server source, deploying instances, writing modules,
  tuning performance, or debugging cluster/sentinel setups.
license: BSD-3-Clause
compatibility: Requires GCC 9+ or Clang 12+, CMake 3.10+ (optional), Tcl 8.6+ (for tests)
metadata:
  tags:
    - database
    - nosql
    - in-memory
    - cache
    - key-value
---

# valkey 9.1.1

Valkey is a high-performance in-memory data structure server, forked from Redis before its license change.
Version 9.1.1 is a security patch release (July 2026) with critical CVE fixes.

## Overview

Valkey serves as a key-value store, cache, message broker, and streaming platform. It supports rich native data structures (strings, hashes, lists, sets, sorted sets, streams, geo) and an extensible module system for custom types and commands.

**Core binaries produced by build:**

| Binary | Purpose |
|---|---|
| `valkey-server` | Main server daemon |
| `valkey-cli` | Command-line client |
| `valkey-benchmark` | Performance benchmarking tool |
| `valkey-check-rdb` | RDB file integrity checker |
| `valkey-check-aof` | AOF file integrity checker / repair tool |

Redis-compatible symlinks (`redis-server`, `redis-cli`, etc.) are created by default via `make install`.

## Building

### Makefile build (default)

```bash
# Standard build
make

# With TLS support (built-in)
make BUILD_TLS=yes

# With TLS as loadable module
make BUILD_TLS=module

# With systemd integration
make USE_SYSTEMD=yes

# With enhanced stack traces (libbacktrace)
make USE_LIBBACKTRACE=yes

# Without Lua scripting engine
make BUILD_LUA=no

# With custom program suffix
make PROG_SUFFIX="-alt"

# 32-bit build
make 32bit

# Custom allocator
make MALLOC=jemalloc   # default on Linux
make MALLOC=libc       # force libc malloc

# Install binaries
make install
# or: make PREFIX=/opt/valkey install
```

### CMake build (experimental)

```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/valkey
# Optional flags:
#   -DBUILD_TLS=yes|no
#   -DBUILD_RDMA=no|module
#   -DBUILD_MALLOC=libc|jemalloc|tcmalloc|tcmalloc_minimal
#   -DBUILD_SANITIZER=address|thread|undefined
#   -DBUILD_UNIT_GTESTS=yes|no
#   -DBUILD_TEST_MODULES=yes|no
#   -DBUILD_EXAMPLE_MODULES=yes|no
make -j$(nproc)
sudo make install
```

### Clean rebuild

When build settings or bundled deps change, always do a full clean:

```bash
make distclean && make
```

This cleans jemalloc, lua, libvalkey, linenoise, and other deps.

## Running

```bash
# Default config (port 6379, bind 127.0.0.1)
./src/valkey-server

# With config file
./src/valkey-server /path/to/valkey.conf

# Override config at runtime
./src/valkey-server --port 9999 --loglevel debug

# Cluster mode
./src/valkey-server --cluster-enabled yes --port 7000

# Sentinel mode
./src/valkey-server /path/to/sentinel.conf --sentinel
```

### Client

```bash
./src/valkey-cli
valkey> ping
PONG
valkey> set foo bar
OK
valkey> get foo
"bar"

# Connect to specific host/port
./src/valkey-cli -h 10.0.0.1 -p 6379

# With TLS
./src/valkey-cli --tls --cert client.crt --key client.key --cacert ca.crt

# Run a single command
./src/valkey-cli -e INFO server
```

### Benchmark

```bash
./src/valkey-benchmark -n 100000 -c 50 -q
# With warmup and duration
./src/valkey-benchmark -n 100000 --warmup 5 --duration 30 -q
# With RPS histogram
./src/valkey-benchmark --hist-buckets 10,50,100,200,500,1000 -q
```

## Configuration

The main config file is `valkey.conf`. All config directives can also be set via CLI flags or runtime `CONFIG SET`.

**Key configuration areas:**

- **Network**: `bind`, `port`, `tls-port`, `tcp-backlog`, `tcp-keepalive`, `timeout`, `protected-mode`
- **General**: `daemonize`, `pidfile`, `loglevel`, `logfile`, `log-format` (legacy/logfmt/json), `databases`, `supervised`
- **Memory**: `maxmemory`, `maxmemory-policy`, `maxmemory-samples`, `maxmemory-clients`
- **Persistence**: `save`, `appendonly`, `appendfsync`, `rdbcompression`, `aof-use-rpreamble`
- **Replication**: `replicaof`, `repl-diskless-sync`, `repl-backlog-size`, `replica-read-only`
- **Cluster**: `cluster-enabled`, `cluster-config-file`, `cluster-node-timeout`
- **Security**: ACL users, `requirepass`, `rename-command`
- **I/O threads**: `io-threads` (reads + writes offloaded to worker threads)
- **Lazy freeing**: `lazyfree-lazy-user-del`, `lazyfree-lazy-eviction` (enabled by default since 8.0)
- **Command log**: `commandlog-execution-slower-than`, `commandlog-request-larger-than`, `commandlog-reply-larger-than`
- **Latency**: `latency-monitor-threshold`, `latency-tracking`

Use `CONFIG GET *` to list all runtime settings. `CONFIG REWRITE` persists runtime changes back to the config file.

## Gotchas

- **`make distclean` is mandatory** when switching build flags (e.g., 32bit to 64bit, enabling/disabling TLS). Build options are cached until distclean.
- **Lua is statically linked by default** since 9.1. Use `BUILD_LUA=no` to omit it or `BUILD_LUA=module` for dynamic loading.
- **Protected mode is on by default** — the server only accepts local connections unless a password is set or `protected-mode no` is configured.
- **`save ""` disables RDB snapshotting entirely** — useful for AOF-only setups but risks data loss on crash.
- **Cluster mode ignores `databases`** — use `cluster-databases` instead (default 1 DB in cluster mode).
- **`repl-diskless-sync yes` is the default** — RDB is streamed directly to replicas without touching disk on the primary.
- **`repl-diskless-load disabled` is the default on replicas** — replicas store received RDB to disk first. Use `on-empty-db` or `swapdb` for faster replication (higher memory cost).
- **ACL `requirepass` is a compatibility layer** — it sets the password for the `default` user. Prefer explicit ACL user definitions.
- **`maxmemory` on replicas is ignored by default** (`replica-ignore-maxmemory yes`) — eviction is driven by the primary sending DEL commands.
- **Symlinks to Redis names** are created by `make install` for compatibility. Disable with `USE_REDIS_SYMLINKS=no`. They are removed by `make uninstall`.
- **`install_server.sh` is Linux-only** — it will not work on macOS.
- **Cluster link send buffers can grow unbounded** on slow peers (e.g., large PubSub messages). Set `cluster-link-sendbuf-limit` to prevent OOM.
- **CMake is experimental** — the Makefile build is the primary and most tested path.
- **`hash-seed` is immutable at startup** — it enables deterministic SCAN ordering across restarts/failovers but cannot be changed at runtime.
- **`sanitize-dump-payload` defaults to `no`** temporarily due to cluster resharding via MIGRATE impact. Plan to switch to `clients` or `yes` for security.
- **9.1.1 includes critical security fixes** — CVE-2026-56684 (TLS use-after-free RCE) and CVE-2026-63639 (corrupt stream RDB RCE). Upgrade from 9.1.0 is recommended.

## References

- [01-data-types](references/01-data-types.md) — Strings, Hashes, Lists, Sets, Sorted Sets, Streams, Geo, HyperLogLog, Bitmaps
- [02-persistence](references/02-persistence.md) — RDB snapshots, AOF (multi-part), durability tradeoffs
- [03-replication](references/03-replication.md) — Primary-replica setup, diskless sync, dual-channel replication, failover
- [04-cluster](references/04-cluster.md) — Cluster mode, slot management, atomic slot migration, CLUSTER commands
- [05-sentinel](references/05-sentinel.md) — High availability with Sentinel, monitoring, automatic failover
- [06-security](references/06-security.md) — ACL system, authentication, hardened configs, TLS
- [07-modules](references/07-modules.md) — Module API, writing custom commands and data types, example modules
- [08-scripting](references/08-scripting.md) — Lua scripting, Functions, EVAL/FCALL, scripting engine as module
- [09-pubsub-streams](references/09-pubsub-streams.md) — Pub/Sub (channels + shard channels), Streams (consumer groups, pending)
- [10-advanced-config](references/10-advanced-config.md) — I/O threads, lazy freeing, memory tuning, latency monitoring, command log
- [11-testing](references/11-testing.md) — Unit tests (gtest), integration tests (Tcl), running against external servers
