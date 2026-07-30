# Pub/Sub

Valkey's publish/subscribe messaging paradigm enables real-time message distribution. A separate `PubSub` object manages subscriptions, as the underlying connection enters a dedicated state that cannot execute regular commands.

## Basic Publish/Subscribe

```python
import valkey

# Publisher — uses a regular Valkey client
pub = valkey.Valkey(host="localhost", port=6379, decode_responses=True)

# Subscriber
sub = pub.pubsub()
sub.subscribe("channel-1", "channel-2")

# Listen for messages
while True:
    message = sub.get_message(timeout=1.0)
    if message is not None:
        print(message)
        # {'type': 'message', 'channel': 'channel-1', 'data': 'hello'}

# Publish
pub.publish("channel-1", "hello world")
```

### Message Format

```python
# get_message() returns dict or None
message = sub.get_message(timeout=1.0)

# Message types:
# {'type': 'subscribe',    'channel': 'ch', 'pattern': None, 'data': 1}
# {'type': 'unsubscribe',  'channel': 'ch', 'pattern': None, 'data': 0}
# {'type': 'message',      'channel': 'ch', 'pattern': None, 'data': 'payload'}
# {'type': 'pmessage',     'channel': 'ch', 'pattern': 'pat', 'data': 'payload'}
# {'type': 'pong',         'channel': None, 'pattern': None, 'data': 'data'}
```

## Pattern Subscriptions

Subscribe to channels matching a glob pattern:

```python
sub = r.pubsub()
sub.psubscribe("news:*", "sports:*")

while True:
    message = sub.get_message(timeout=1.0)
    if message and message["type"] == "pmessage":
        print(f"Pattern: {message['pattern']}")
        print(f"Channel: {message['channel']}")
        print(f"Data: {message['data']}")
```

Patterns use glob-style matching: `*` matches any sequence, `?` matches single character.

## Shard Channels (Valkey 7+)

Shard channels distribute publishing across cluster nodes using CRC16, avoiding the bottleneck of single-node Pub/Sub:

```python
sub = r.pubsub()
sub.ssubscribe("shard-channel-1")

# Publish to shard channel
r.spublish("shard-channel-1", "message")

message = sub.get_message(timeout=1.0)
# {'type': 'smessage', 'channel': 'shard-channel-1', 'data': 'message'}
```

## Unsubscribe

```python
# Unsubscribe from specific channels
sub.unsubscribe("channel-1")
sub.unsubscribe()  # unsubscribe from all

# Unsubscribe from patterns
sub.punsubscribe("news:*")
sub.punsubscribe()  # unsubscribe from all patterns

# Unsubscribe from shard channels
sub.sunsubscribe("shard-channel-1")
sub.sunsubscribe()  # unsubscribe from all shard channels
```

## Callback Handlers

Register callbacks for specific channels:

```python
def handle_news(message):
    print(f"News: {message['data']}")

def handle_sports(message):
    print(f"Sports: {message['data']}")

sub = r.pubsub()
sub.subscribe(**{"news": handle_news, "sports": handle_sports})

# Messages matching callbacks are handled automatically
# get_message() still returns them, but callback fires first
while True:
    message = sub.get_message(timeout=1.0)
    if message:
        print(f"Got: {message}")
```

### Callback with Pattern Subscriptions

```python
def handle_pattern(message):
    print(f"[{message['channel']}] {message['data']}")

sub = r.pubsub()
sub.psubscribe(**{"news:*": handle_pattern})
```

## get_message vs get_response

```python
# get_message() — returns parsed dict, handles health checks
message = sub.get_message(timeout=1.0)

# get_response() — lower-level, returns raw response
response = sub.get_response(timeout=1.0)

# parse_response() — block until message or timeout
response = sub.parse_response(block=True, timeout=1.0)
```

- `get_message()` returns a dict with `type`, `channel`, `pattern`, `data` keys, or `None` on timeout.
- `parse_response()` blocks and returns the raw Valkey response.

## Context Manager

```python
with r.pubsub() as sub:
    sub.subscribe("channel-1")
    while True:
        message = sub.get_message(timeout=1.0)
        if message:
            process(message)
    # reset() called automatically on exit
```

## PubSubWorkerThread

For non-blocking consumption with a background thread:

```python
from valkey.client import PubSubWorkerThread

def handler(message):
    print(f"Received: {message}")

sub = r.pubsub()
sub.subscribe("channel-1")

thread = PubSubWorkerThread(sub)
thread.get_message_callback = handler
thread.run()

# Thread runs in background, calling handler for each message
# Stop the thread:
thread.stop()
```

## Health Checks

PubSub connections send periodic PING health checks. If no subscriptions are active, the server responds with a bulk `PONG`. With active subscriptions, it responds with a push `pong`.

```python
sub = r.pubsub()
sub.subscribe("channel-1")

# Ping the connection
sub.ping()
# Health check PONG is automatically filtered out by get_message()
```

## Reconnection

When a PubSub connection is lost, valkey-py automatically re-subscribes to all previously subscribed channels and patterns upon reconnection. The `on_connect` callback handles this transparently.

```python
sub = r.pubsub()
sub.subscribe("channel-1", "channel-2")
sub.psubscribe("news:*")

# If connection drops and reconnects, all subscriptions are restored automatically
```

## Common Patterns

### Event Bus

```python
# Producer
def emit(event_type, data):
    r.publish(f"events:{event_type}", json.dumps(data))

emit("user.created", {"id": 1, "name": "Alice"})

# Consumer
sub = r.pubsub()
sub.subscribe("events:user.created", "events:order.placed")

while True:
    msg = sub.get_message(timeout=1.0)
    if msg and msg["type"] == "message":
        event_type = msg["channel"].split(":", 1)[1]
        data = json.loads(msg["data"])
        handle_event(event_type, data)
```

### Fan-out with Patterns

```python
# Subscribe to all events for a tenant
sub.psubscribe("tenant:42:*")

# Publish tenant-specific events
r.publish("tenant:42:user.login", "...")
r.publish("tenant:42:order.created", "...")
```

## Gotchas

- **Pub/Sub connections cannot run regular commands** — Once subscribed, the connection is dedicated to Pub/Sub. Use a separate `Valkey` instance for publishing.
- **Messages are fire-and-forget** — Unsubscribed messages are lost. For reliability, use Streams with consumer groups instead.
- **`get_message(timeout=0)` is non-blocking** — Returns `None` immediately if no message is available. Use `timeout > 0` to block.
- **Callbacks fire before `get_message()` returns** — If a callback is registered, it runs first. The message is still returned by `get_message()`.
- **Shard channels require Valkey 7+** — `ssubscribe`/`spublish` are not available on older servers.
