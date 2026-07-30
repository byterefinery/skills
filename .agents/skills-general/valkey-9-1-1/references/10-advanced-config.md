# Advanced Configuration

## I/O Threads

Offload socket read/write operations from the main thread to worker threads. Provides 2x throughput improvement without pipelining or sharding.

```conf
# Number of I/O threads (1 = disabled, main thread only)
io-threads 4

# Recommended: use 2-3 threads on 4-core, 6 threads on 8-core
# Leave at least one core for the main thread
```

**Note:** Benchmark with matching `--threads` option to see the improvement:
```bash
./src/valkey-benchmark -t set,get -n 100000 --threads 4 -q
```

I/O threads handle `read()`/`write()` syscalls and protocol parsing. The main thread still processes commands.

## Lazy Freeing

Async deletion of keys in background threads. Enabled by default since 8.0.

```conf
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes
lazyfree-lazy-user-del yes
lazyfree-lazy-user-flush yes
replica-lazy-flush yes
```

`UNLINK` always frees lazily regardless of config. `DEL` follows `lazyfree-lazy-user-del`. `FLUSHDB`/`FLUSHALL` support explicit `[SYNC|ASYNC]` flags.

## Memory Management

### Maxmemory

```conf
maxmemory 2gb
# or as percentage of system memory
# maxmemory 80%
```

### Eviction policies

| Policy | Behavior |
|---|---|
| `noeviction` | Return errors on writes (default) |
| `allkeys-lru` | Evict any key, least recently used |
| `allkeys-lfu` | Evict any key, least frequently used |
| `allkeys-random` | Evict random key |
| `volatile-lru` | Evict keys with TTL, least recently used |
| `volatile-lfu` | Evict keys with TTL, least frequently used |
| `volatile-random` | Evict random key with TTL |
| `volatile-ttl` | Evict key with nearest TTL |

```conf
maxmemory-policy allkeys-lru
maxmemory-samples 5          # LRU sample size (1-64)
maxmemory-eviction-tenacity 10  # 0=min latency, 10=default, 100=max throughput
```

### LFU tuning

```conf
lfu-log-factor 10    # Logarithmic counter factor (0-100)
lfu-decay-time 1     # Counter decay in minutes (0 = never decay)
```

### Client memory

```conf
# Evict clients when their accumulated memory exceeds threshold
maxmemory-clients 0       # disabled (default)
# maxmemory-clients 1g
# maxmemory-clients 5%
```

### Output buffer limits

```conf
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
```

Format: `<hard-limit> <soft-limit> <soft-seconds>`

## Latency Monitoring

```conf
# Enable latency monitoring (0 = disabled)
latency-monitor-threshold 0

# Extended per-command latency tracking
latency-tracking yes

# Percentiles exported via INFO latencystats
latency-tracking-info-percentiles 50 99 99.9
```

### Latency commands

```bash
LATENCY LATEST
LATENCY HISTORY <event>
LATENCY GRAPH <event>
LATENCY DOCTOR
LATENCY RESET [<event>]
LATENCY HISTOGRAM [RESET]
```

## Command Log

Replaces the legacy slowlog system with three log types:

```conf
# SLOW — commands exceeding execution time (microseconds)
commandlog-execution-slower-than 10000
commandlog-slow-execution-max-len 128

# LARGE-REQUEST — commands with large request payloads (bytes)
commandlog-request-larger-than 1048576
commandlog-large-request-max-len 128

# LARGE-REPLY — commands producing large replies (bytes)
commandlog-reply-larger-than 1048576
commandlog-large-reply-max-len 128
```

### Commands

```bash
COMMANDLOG GET SLOW 10
COMMANDLOG GET LARGE-REQUEST 10
COMMANDLOG GET LARGE-REPLY 10
COMMANDLOG LEN SLOW
COMMANDLOG RESET SLOW
COMMANDLOG RESET LARGE-REQUEST
COMMANDLOG RESET LARGE-REPLY
COMMANDLOG LEN LARGE-REPLY
```

Legacy `slowlog-*` parameters still work but are deprecated.

## Active Rehashing

```conf
# Use 1% of CPU time for incremental hash table rehashing
activerehashing yes

# Server hz — background task frequency (1-500)
hz 10
```

Higher `hz` means more responsive expiry handling and timeouts but more CPU usage. Default 10 is suitable for most workloads. Use 100 for low-latency requirements.

## Kernel Controls

### OOM Score Adj

```conf
oom-score-adj yes              # or: no, absolute, relative
oom-score-adj-values 0 200 800  # primary, replica, background
```

Hints the Linux OOM killer to kill background children first, then replicas, then primary.

### Transparent Huge Pages

```conf
disable-thp yes
```

Disables THP for the Valkey process to avoid fork/CoW latency issues.

## Connection Limits

```conf
maxclients 10000
max-new-connections-per-cycle 10
max-new-tls-connections-per-cycle 1
client-query-buffer-limit 1gb
proto-max-bulk-len 512mb
```

## Internal Data Structure Tuning

```conf
# Hashes
hash-max-listpack-entries 512
hash-max-listpack-value 64

# Lists
list-max-listpack-size -2
list-compress-depth 0

# Sets
set-max-intset-entries 512
set-max-listpack-entries 128
set-max-listpack-value 64

# Sorted sets
zset-max-listpack-entries 128
zset-max-listpack-value 64

# HyperLogLog
hll-sparse-max-bytes 3000

# Streams
stream-node-max-bytes 4096
stream-node-max-entries 100
```

## Memory Prefetching

When multiple commands are parsed, Valkey prefetches hash table entries for upcoming commands. This reduces memory access latency for pipelined workloads.

## Process Title

```conf
set-proc-title yes
proc-title-template "{title} {listen-addr} {server-mode}"
```

Template variables: `{title}`, `{listen-addr}`, `{server-mode}`, `{port}`, `{tls-port}`, `{unixsocket}`, `{config-file}`.
