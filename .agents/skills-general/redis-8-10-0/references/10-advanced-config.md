# Advanced Configuration

## I/O Threads

Offload network I/O (reads and writes) to worker threads, reducing main thread contention.

```
io-threads 4                    # number of I/O threads (0 = disabled, 1 = main thread only)
io-threads-do-reads yes         # offload command parsing to threads
io-threads-multiplier 12        # min items per thread batch
```

**Gotchas:**
- I/O threads do not execute commands — only parse input and send output
- Best benefit on multi-core systems with high connection counts
- `io-threads-do-reads` adds command parsing to threads (more CPU, less main thread load)
- Not compatible with single-threaded debugging

## Memory Management

### Maxmemory

```
maxmemory 2gb                   # hard memory limit
maxmemory-policy noeviction     # eviction policy
maxmemory-samples 5             # samples for LRU approximation
maxmemory-clients 0             # memory reserved for client output buffers
```

**Eviction policies:**
| Policy | Behavior |
|---|---|
| `noeviction` | Return errors on write when memory limit reached |
| `allkeys-lru` | Evict least recently used keys |
| `allkeys-lfu` | Evict least frequently used keys |
| `allkeys-random` | Evict random keys |
| `volatile-lru` | Evict LRU keys with TTL |
| `volatile-lfu` | Evict LFU keys with TTL |
| `volatile-random` | Evict random keys with TTL |
| `volatile-ttl` | Evict keys with shortest TTL |
| `volatile-expired` | Evict expired keys (fast path) |

### Active Defragmentation

Reclaim fragmented memory by moving objects in memory. Requires Jemalloc.

```
activedefrag no
active-defrag-enabled yes
active-defrag-ignore-bytes 100mb
active-defrag-threshold-lower 10
active-defrag-threshold-upper 100
active-defrag-cycle-min 1
active-defrag-cycle-max 25
active-defrag-max-scan-fields 1000
```

## Lazy Freeing

Free memory asynchronously by delegating deletion to a background thread.

```
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
lazyfree-lazy-user-del no
lazyfree-lazy-user-flush no
```

When enabled, `DEL`/`UNLINK`/eviction/expiration free objects in the background. Use `UNLINK` explicitly for async deletion regardless of config.

## Latency Monitoring

Track and report high-latency events.

```
latency-monitor-threshold 100   # ms threshold (0 = disabled)
latency-tracking yes            # enable latency tracking
```

**Commands:**
- `LATENCY LATEST` — latest latency events
- `LATENCY HISTORY <event>` — history for specific event
- `LATENCY RESET [event]` — reset latency data
- `LATENCY DOCTOR` — diagnostic report

## Hz and Dynamic Hz

```
hz 10                           # server internal timer frequency
dynamic-hz yes                  # adapt Hz based on client count
```

Higher Hz means more frequent background tasks (expire checking, cleanup) but more CPU. `dynamic-hz` adapts between 1-500 based on load.

## Compact Hashes (new in 8.10)

Compact hashes share field name storage across hashes with matching schemas, reducing memory for keys that share a structure.

```
hash-max-template-entries 0     # max cached templates (0 = disabled)
```

**How it works:**
1. When a hash is created/updated, Redis checks if a matching template exists
2. If found, the hash uses the shared template (`OBJ_ENCODING_TMPL_LP` or `OBJ_ENCODING_TMPL_ARRAY`)
3. Templates are cached up to `hash-max-template-entries`
4. Templates are evicted when the cache is full

**Use `HIMPORT PREPARE`** to hint at the schema for bulk operations — the prepared fieldset guides template creation.

**Memory savings:** Significant when many hashes share the same field names (e.g., user profiles, product catalogs). Field names are stored once in the template instead of per-key.

## Client Output Buffers

Limit memory used by client output buffers to prevent OOM from slow consumers.

```
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
```

Format: `<class> <hard-limit> <soft-limit> <soft-seconds>`
- `hard-limit` — disconnect immediately if exceeded
- `soft-limit` + `soft-seconds` — disconnect if exceeded for N seconds

## Slow Log

```
slowlog-log-slower-than 10000   # microseconds (10ms default)
slowlog-max-len 128             # max entries
```

**Commands:**
- `SLOWLOG GET [n]` — get slow log entries
- `SLOWLOG LEN` — entry count
- `SLOWLOG RESET` — clear log
- `SLOWLOG HELP` — help

**8.10 addition:** `SLOWLOG GET` now includes total argument count in the reply.

## Keyspace Notifications

```
notify-keyspace-events ""       # empty = disabled
# Flags: K (keyspace), E (keyevent), g (generic), $ (string), l (list),
#        s (set), h (hash), z (sorted set), x (expire), e (evicted),
#        A (all, alias to g$slzhxe), t (stream), d (module), c (ACL)
```

## Command Renaming

```
rename-command FLUSHDB ""       # disable command
rename-command CONFIG "config_cmd_1234"  # rename command
```

Note: `rename-command` is deprecated — prefer ACLs for command restriction.

## Process Title

```
proc-title-template "{title} {listen-addr} {server-mode}"
```

Available variables: `{title}`, `{listen-addr}`, `{server-mode}`, `{config-file}`, `{threads}`, `{io-threads}`, `{db-num}`, `{used-mem-human}`.

## Gotchas

- **`hash-max-template-entries 0` disables compact hashes** — set to a positive value (e.g., 1024) to enable. Monitor template usage with `INFO memory`.
- **I/O threads don't execute commands** — they only parse input and send output. Command execution remains single-threaded.
- **`maxmemory` on replicas is ignored by default** — eviction is driven by the primary sending DEL commands.
- **Active defrag requires Jemalloc** — not available with libc malloc.
- **`hz` affects expire accuracy** — lower Hz means expires may be delayed by up to 1/hz seconds.
- **Client output buffer limits apply per-client** — a single slow consumer can still use significant memory before being disconnected.
- **`dynamic-hz` can cause oscillation** — on systems with rapidly changing client counts, Hz may fluctuate. Pin `hz` if stability is needed.
- **Keyspace notifications add overhead** — each notified event generates a pub/sub message. Use selectively.
