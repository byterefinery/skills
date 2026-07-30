# Protocol and Responses

## Wire Protocol vs Response Shape

redis-py 8.0+ separates wire protocol from Python response shapes. Two independent settings:

- **`protocol`** — controls the wire protocol (RESP2 or RESP3)
- **`legacy_responses`** — controls the Python response shape returned to application code

### Response Modes Matrix

| Client Options | Wire Protocol | Python Response Shape |
|---|---|---|
| `Redis()` | RESP3 (default) | Legacy RESP2-compatible |
| `Redis(protocol=2)` | RESP2 | Legacy RESP2-compatible |
| `Redis(protocol=3)` | RESP3 | Native RESP3 shapes |
| `Redis(legacy_responses=False)` | RESP3 (default) | Unified (protocol-independent) |
| `Redis(protocol=2, legacy_responses=False)` | RESP2 | Unified |
| `Redis(protocol=3, legacy_responses=False)` | RESP3 | Unified |

### Recommendations

- **New projects**: Use `legacy_responses=False` for stable, protocol-independent responses
- **Existing projects**: Keep default (`legacy_responses=True`) and migrate gradually
- **Explicit protocol**: Set `protocol=3` when you need RESP3-specific features (push notifications, client tracking)
- **Force RESP2**: Set `protocol=2` for compatibility with older Redis servers

## RESP3 Features

RESP3 (Redis Serialization Protocol v3) adds:

- **Push notifications** — Server sends out-of-band messages (maintenance events, invalidation notices)
- **Richer types** — Native support for sets, maps, doubles, big integers, verbatim strings
- **Client tracking** — Server-assisted client-side caching with invalidation push
- **Maintenance notifications** — Server alerts about upcoming maintenance events

```python
# Enable RESP3 with native response shapes
r = redis.Redis(host="localhost", protocol=3)

# RESP3 on wire with legacy-compatible Python shapes (default in 8.0+)
r = redis.Redis(host="localhost")

# RESP3 with unified responses (recommended)
r = redis.Redis(host="localhost", legacy_responses=False)
```

### Push Notifications Handler

```python
def push_handler(message):
    # message is a dict with keys: 'type', 'data', etc.
    print(f"Push notification: {message}")
    if "maintenance" in str(message).lower():
        handle_maintenance(message)

r = redis.Redis(host="localhost", protocol=3)
pubsub = r.pubsub(push_handler_func=push_handler)
```

## Unified Responses

Unified responses (`legacy_responses=False`) provide protocol-independent Python types. The same command returns the same Python type regardless of whether RESP2 or RESP3 is used on the wire.

```python
r = redis.Redis(legacy_responses=False)

# Same response shape whether wire is RESP2 or RESP3
result = r.info()  # Always dict
members = r.smembers("myset")  # Always set
```

### Key Changes from Legacy Mode

- **`INFO`** — Returns `dict` instead of `dict` with nested strings
- **`HGETALL`** — Returns `dict` consistently
- **`SMEMBERS`** — Returns `set` instead of `list`
- **`ZRANGE`** with `WITHSCORES` — Returns `list` of `(member, score)` tuples
- **`XINFO`** commands — Return structured dicts
- **`CLIENT LIST`** — Returns `list` of `dict`
- **Module commands** — JSON, Search, TimeSeries return richer objects

### Migration Checklist

1. Add `legacy_responses=False` to client construction
2. Check response types for commands your application uses
3. Update type hints and assertions
4. Test module commands (JSON, Search, TimeSeries) separately
5. Roll out gradually per service

## `decode_responses`

Independent from protocol and response mode. Controls whether bulk string data is decoded to `str` or returned as `bytes`.

```python
# Returns bytes
r = redis.Redis(decode_responses=False)
r.set("key", "value")
r.get("key")  # b"value"

# Returns strings
r = redis.Redis(decode_responses=True)
r.set("key", "value")
r.get("key")  # "value"
```

### Gotchas

- `decode_responses=True` decodes **all** bulk strings, including keys returned by `KEYS`, `HKEYS`, `SMEMBERS`
- Do not use with binary data (`DUMP`, `RESTORE`, or binary keys)
- `decode_responses` is a connection pool setting — all connections in a pool share the same encoding behavior
- Structural keys in dicts (e.g., `INFO` response keys) follow the connection's encoding regardless of `decode_responses`

## Protocol Selection in URLs

```python
# RESP3 explicit
r = redis.Redis.from_url("redis://localhost:6379?protocol=3")

# RESP2 explicit
r = redis.Redis.from_url("redis://localhost:6379?protocol=2")

# Unified responses
r = redis.Redis.from_url("redis://localhost:6379?legacy_responses=false")

# Combined
r = redis.Redis.from_url("redis://localhost:6379?protocol=3&legacy_responses=false&decode_responses=yes")
```

## Checking Protocol Version

```python
from redis.utils import check_protocol_version

protocol = r.connection_pool.connection_kwargs.get("protocol")
if check_protocol_version(protocol, 3):
    # RESP3 features available
    pass
```

## RESP2 Compatibility

For servers that don't support RESP3:

```python
# Force RESP2 on the wire
r = redis.Redis(host="localhost", protocol=2)

# RESP2 wire with unified Python responses
r = redis.Redis(host="localhost", protocol=2, legacy_responses=False)
```

redis-py auto-negotiates the protocol with the server. If the server doesn't support RESP3, it falls back to RESP2 even if `protocol=3` is requested.
