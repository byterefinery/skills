# Pub/Sub and Streams

## Pub/Sub

Redis Pub/Sub is a real-time message broadcasting system. Messages are fire-and-forget — not persisted.

### Channel Pub/Sub

```bash
# Subscribe
redis-cli SUBSCRIBE channel1 channel2

# Publish
redis-cli PUBLISH channel1 "hello"

# Pattern subscribe
redis-cli PSUBSCRIBE news:*
```

**Commands:** `SUBSCRIBE`, `UNSUBSCRIBE`, `PSUBSCRIBE`, `PUNSUBSCRIBE`, `PUBLISH`, `PUBSUB` (CHANNELS/NUMSUB/NUMPAT)

### Shard Channels (since 7.0)

Sharded pub/sub distributes subscribers across cluster nodes. A message is delivered to exactly one subscriber node based on hash slot of the channel name.

```bash
SSUBSCRIBE {news}.sports
SPUBLISH {news}.sports "goal!"
```

**Commands:** `SSUBSCRIBE`, `SUNSUBSCRIBE`, `SPUBLISH`, `SPUBSUB`

### Pub/Sub Characteristics

- **No persistence** — messages not delivered to active subscribers are lost
- **No acks** — fire-and-forget delivery
- **No ordering guarantees** across multiple publishers
- **Fan-out** — one message delivered to all subscribers
- **Cluster-aware** — `PUBLISH` broadcasts to all nodes; `SPUBLISH` routes to single shard

## Streams

Streams are append-only, persistent ordered logs with consumer group support. Ideal for message queues, event sourcing, and change data capture.

### Stream Structure

- **Entries** — ordered by ID (`timestamp-sequence`, e.g., `1609459200000-0`)
- **Macro nodes** — radix tree of listpacks, configurable via `stream-node-max-bytes`/`stream-node-max-entries`
- **Consumer groups** — multiple consumers reading from the same stream with per-consumer pending tracking

### Creating and Adding

```bash
# Add entries (auto ID with *)
XADD mystream * field1 value1 field2 value2

# With trimming
XADD mystream MAXLEN ~ 1000 * field1 value1

# Exact trimming
XADD mystream MAXLEN == 1000 * field1 value1

# Minimal ID trimming
XADD mystream MINID 1609459200000-0 * field1 value2

# With specific ID
XADD mystream 1609459200000-0 field1 value1
```

### Reading

```bash
# Range query
XRANGE mystream - +
XRANGE mystream 1609459200000-0 1609459300000-0
XREVRANGE mystream + - COUNT 10

# Read (blocking)
XREAD COUNT 10 BLOCK 1000 STREAMS mystream 0

# Read from last entry
XREAD COUNT 10 BLOCK 1000 STREAMS mystream $
```

**8.10 additions:** `XREAD`/`XREADGROUP` now support `MAXCOUNT` and `MAXSIZE` to cap cumulative reply entries and size.

### Consumer Groups

```bash
# Create group
XGROUP CREATE mystream mygroup $

# Read from group
XREADGROUP GROUP mygroup consumer1 COUNT 10 BLOCK 1000 STREAMS mystream >

# Acknowledge
XACK mystream mygroup <id1> <id2> ...

# Pending entries
XPENDING mystream mygroup
XPENDING mystream mygroup - + 10

# Claim stale entries
XCLAIM mystream mygroup consumer2 MINIDLE_TIME 30000 <id1> <id2>

# Auto-claim
XAUTOCLAIM mystream mygroup consumer2 MINIDLE_TIME 30000 0 COUNT 10
```

### Stream Trimming

```bash
# Explicit trim
XTRIM mystream MAXLEN ~ 1000
XTRIM mystream MINID 1609459200000-0

# Approximate (~) vs exact (==)
# ~ = approximate, O(1), may exceed target slightly
# == = exact, O(N), precise but slower
```

### Stream Info

```bash
XINFO STREAM mystream [FULL [COUNT <n>]]
XINFO CONSUMERS mystream mygroup
XINFO GROUPS mystream
```

### Stream Commands Summary

| Command | Purpose |
|---|---|
| `XADD` | Add entry |
| `XDEL` | Delete entry |
| `XTRIM` | Trim stream |
| `XRANGE`/`XREVRANGE` | Range query |
| `XREAD` | Read (blocking) |
| `XREADGROUP` | Read from consumer group |
| `XACK` | Acknowledge entry |
| `XGROUP` | Manage groups |
| `XCLAIM` | Claim pending entries |
| `XAUTOCLAIM` | Auto-claim stale entries |
| `XPENDING` | List pending entries |
| `XINFO` | Stream metadata |
| `XLEN` | Entry count |
| `XSETID` | Set stream ID |
| `XPEEL` | Pop entries (since 7.0) |

## Streams as Message Queues

```bash
# Producer
XADD orders * customer alice item widget quantity 1

# Consumer
XREADGROUP GROUP workers worker1 COUNT 1 BLOCK 0 STREAMS orders >

# Process and ack
XACK orders workers <entry-id>
```

## Gotchas

- **Pub/Sub has no persistence** — messages not delivered to active subscribers are lost forever
- **`XADD MAXLEN ~` is approximate** — use `==` for exact trimming (slower)
- **`XREADGROUP` with `>`** reads only new entries. Use `0` to re-read pending entries.
- **Pending entries accumulate** — unacked entries grow the PEL. Monitor with `XPENDING`.
- **`XCLAIM` with `JUSTID`** — returns only IDs, not full entries (faster for large PELs).
- **Stream IDs are lexicographically ordered** — comparison is string-based, not numeric.
- **`XREAD BLOCK 0`** blocks indefinitely. Use a timeout for responsive consumers.
- **Consumer groups don't auto-create** — use `XGROUP CREATE ... MKSTREAM` to create group and stream in one step.
- **`XREAD`/`XREADGROUP` MAXCOUNT/MAXSIZE (8.10)** — use these to prevent OOM on consumers with large pending entries.
- **Shard channels use hash tags** — `{channel}` ensures related channels route to the same shard.
