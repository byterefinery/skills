# Pub/Sub

## Basic Publish/Subscribe

```python
import redis

r = redis.Redis(host="localhost", port=6379)

# Publisher
r.publish("news", "Breaking news!")  # Returns number of receivers

# Subscriber
pubsub = r.pubsub()
pubsub.subscribe("news", "sports")

# Listen for messages
while True:
    message = pubsub.get_message(timeout=1.0)
    if message:
        print(message)
        # {'type': 'message', 'channel': b'news', 'data': b'Breaking news!'}
```

### Message Types

| Type | Description |
|---|---|
| `subscribe` | Confirmation of subscription |
| `unsubscribe` | Confirmation of unsubscription |
| `message` | Received message on a channel |
| `pmessage` | Received message matching a pattern |

### Callback Handlers

```python
def on_message(pubsub, message):
    print(f"Got message: {message['data']}")

def on_subscribe(pubsub, message):
    print(f"Subscribed to: {message['channel']}")

pubsub = r.pubsub()
pubsub.subscribe(**{"news": on_message, "sports": on_message})
pubsub.listen()  # Blocks, dispatching to callbacks
```

### Pattern Subscription

```python
pubsub = r.pubsub()
pubsub.psubscribe("news:*", "sports:*")

message = pubsub.get_message()
# {'type': 'pmessage', 'pattern': b'news:*', 'channel': b'news:tech', 'data': b'...'}
```

### Unsubscribe

```python
pubsub.unsubscribe("news")
pubsub.punsubscribe("sports:*")
pubsub.unsubscribe()  # Unsubscribe from all
```

### Ignoring Subscribe Messages

```python
# Skip subscribe/unsubscribe confirmations
pubsub = r.pubsub(ignore_subscribe_messages=True)
pubsub.subscribe("news")

# First get_message returns the actual message, not the subscribe confirmation
message = pubsub.get_message()
```

### Timeout on get_message

```python
# Block up to 1 second waiting for a message
message = pubsub.get_message(timeout=1.0)
if message is None:
    print("Timeout — no message received")
```

## Shard Channels (Redis 7.0+)

Shard channels scale Pub/Sub horizontally across multiple nodes.

```python
pubsub = r.pubsub()
pubsub.ssubscribe("shard:news:0", "shard:news:1")

# Publish to shard channel
r.spublish("shard:news:0", "message")

message = pubsub.get_message()
# {'type': 'smessage', 'channel': b'shard:news:0', 'data': b'message'}
```

## PubSub Worker Thread

For non-blocking message processing:

```python
def message_handler(message):
    print(f"Channel: {message['channel']}, Data: {message['data']}")

pubsub = r.pubsub()
pubsub.subscribe("news")
pubsub.get_message()  # Consume subscribe confirmation

worker = redis.client.PubSubWorkerThread(pubsub, {
    "news": message_handler,
})
worker.run()

# Stop the worker
worker.stop()
```

## Keyspace Notifications

Subscribe to events about key changes. Requires server configuration: `notify-keyspace-events "KEA"`.

```python
from redis.keyspace_notifications import KeyspaceNotifications

notifications = r.keyspace_notifications(
    key_prefix="user:",              # Filter and strip prefix
    ignore_subscribe_messages=True,
)

# Subscribe to all events for keys matching prefix
notifications.listen()

# Or use specific event types
from redis.keyspace_notifications import EventType, KeyNotification

for event in notifications.listen():
    print(f"Event: {event.event_type}, Key: {event.key}")
```

### Event Types

| Type | Constant | Description |
|---|---|---|
| `generic` | `EventType.GENERIC` | DEL, EXPIRE, RENAME |
| `string` | `EventType.STRING` | SET, APPEND |
| `list` | `EventType.LIST` | LPUSH, RPOP |
| `set` | `EventType.SET` | SADD, SREM |
| `hash` | `EventType.HASH` | HSET, HDEL |
| `zset` | `EventType.ZSET` | ZADD, ZREM |
| `stream` | `EventType.STREAM` | XADD, XDEL |
| `keyevent` | Per-event | Individual command events |

### Keyspace Notification Channels

```python
# Keyspace events (key name in payload)
# __keyspace@0__:mykey -> event

# Keyevent events (event type in payload)
# __keyevent@0__:set -> mykey
```

## PubSub Gotchas

- **Pub/Sub blocks the connection** — Once subscribed, the connection cannot execute regular commands. Use a separate `Redis` instance for publishing and subscribing
- **`get_message()` returns None on timeout** — Always check for None when using `timeout` parameter
- **Subscribe confirmations** — By default, `get_message()` returns subscribe confirmations first. Use `ignore_subscribe_messages=True` to skip them
- **`listen()` blocks forever** — Use `get_message(timeout=N)` for non-blocking reads, or run in a separate thread
- **Pattern subscriptions match literally** — `psubscribe("news:*")` matches `news:tech` but not `news:tech:us`. Use multiple patterns for deeper hierarchies
- **Messages are not persisted** — Pub/Sub is fire-and-forget. Messages sent when no one is subscribed are lost. Use Streams for persistent messaging
- **Channel names are case-sensitive** — `News` and `news` are different channels
- **`close()` on PubSub** — Always close PubSub when done to release the connection: `pubsub.close()`

## Async Pub/Sub

```python
import asyncio
import redis.asyncio as aioredis

async def main():
    r = await aioredis.Redis(host="localhost")

    # Publisher
    await r.publish("news", "hello")

    # Subscriber
    pubsub = r.pubsub()
    await pubsub.subscribe("news")

    message = await pubsub.get_message(timeout=1.0)
    print(message)

    await pubsub.unsubscribe("news")
    await pubsub.close()
    await r.close()

asyncio.run(main())
```
