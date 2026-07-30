# Pub/Sub and Streams

## Pub/Sub

Traditional publish-subscribe messaging. Messages are fire-and-forget — not persisted.

### Channel-based Pub/Sub

```bash
# Subscribe
SUBSCRIBE channel1 channel2

# Publish
PUBLISH channel1 "hello"

# Pattern-based subscription
PSUBSCRIBE news:*

# Unsubscribe
UNSUBSCRIBE channel1
PUNSUBSCRIBE news:*
```

### Shard Pub/Sub (since 7.0)

Hash-based channel distribution for horizontal scaling. Channels are hashed to slots (like Cluster keys).

```bash
# Shard subscribe
SSUBSCRIBE shard-channel1

# Shard publish
SPUBLISH shard-channel1 "hello"

# Shard unsubscribe
SUNSUBSCRIBE shard-channel1
```

### Info commands

```bash
# List active channels
PUBSUB CHANNELS [pattern] [TYPE channel|shardchannel]

# Count subscribers
PUBSUB NUMSUB channel1 channel2
PUBSUB SHARDNUMSUB shard-channel1

# Count pattern subscriptions
PUBSUB NUMPAT
```

### Cluster Pub/Sub

In cluster mode, `PUBLISH` delivers to the node owning the channel's hash slot. `SPUBLISH` uses shard channel hashing. Set `cluster-allow-pubsubshard-when-down yes` to allow shard Pub/Sub during cluster-down state.

## Streams

Ordered, append-only data structures with consumer group support. Similar to Kafka topics but in-memory.

### Basic operations

```bash
# Add entry (auto-generated ID)
XADD mystream * field1 value1 field2 value2

# Add with specific ID
XADD mystream 1564436473611-0 field1 value1

# Trim stream (keep last 1000 entries)
XADD mystream MAXLEN ~1000 * field1 value1

# Read range
XRANGE mystream - + COUNT 10
XREVRANGE mystream + - COUNT 10

# Get length
XLEN mystream

# Delete entries
XDEL mystream <id1> <id2>

# Trim without adding
XTRIM mystream MAXLEN ~1000
```

### XTRIM options

```
MAXLEN [~|=} <count>     — keep last N entries
MINID [~|=} <id>         — keep entries with ID >= minid
LIMIT <count>            — limit entries examined during trim
```

`~` = approximate trimming (more efficient), `=` = exact trimming.

### Reading streams

```bash
# Block-read from stream (multiple streams supported)
XREAD COUNT 10 BLOCK 5000 STREAMS mystream myotherstream $ $

# Read from last delivered ID
XREAD COUNT 10 STREAMS mystream <last-id>
```

### Consumer Groups

```bash
# Create consumer group
XGROUP CREATE mystream mygroup $

# Create consumer within group
XGROUP CREATECONSUMER mystream mygroup consumer1

# Read from group (each message delivered once)
XREADGROUP GROUP mygroup consumer1 COUNT 10 BLOCK 5000 STREAMS mystream >

# Acknowledge processed messages
XACK mystream mygroup <id1> <id2>

# Delete consumer
XGROUP DELCONSUMER mystream mygroup consumer1

# Destroy group
XGROUP DESTROY mystream mygroup

# Set group last-delivered ID
XGROUP SETID mystream mygroup $
```

### Claiming messages

```bash
# Claim pending messages from another consumer
XCLAIM mystream mygroup newconsumer 3600000 <id1> <id2>
  [MINIDLETIME 3600000] [JSON]

# Auto-claim (claim + return claimed IDs)
XAUTOCLAIM mystream mygroup newconsumer 3600000 <start-id>
  [COUNT count] [JUSTID]
```

### Pending entries

```bash
# Summary of pending entries
XPENDING mystream mygroup

# Detailed pending list
XPENDING mystream mygroup IDLE 3600000 - + 10

# With consumer filter
XPENDING mystream mygroup consumer1 - + 10
```

### Stream info

```bash
# Stream metadata
XINFO STREAM mystream [FULL [COUNT n]]

# Consumer groups
XINFO GROUPS mystream

# Consumers in a group
XINFO CONSUMERS mystream mygroup
```

### Stream internals

Streams use a radix tree of macro nodes. Each node holds up to:
- `stream-node-max-bytes` (default 4096) bytes
- `stream-node-max-entries` (default 100) entries

Set to 0 to disable the respective limit.

### Use cases

- **Event sourcing** — append-only log of domain events
- **Task queues** — consumer groups distribute work
- **Activity feeds** — XRANGE for chronological reads
- **Change data capture** — stream database changes
- **Real-time analytics** — continuous processing with consumer groups
