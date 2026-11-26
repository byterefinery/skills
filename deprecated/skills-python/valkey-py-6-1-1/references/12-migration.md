# Migration from redis-py

valkey-py is forked from redis-py and provides backward-compatible aliases. Migration ranges from zero code changes to full API updates depending on your usage.

## Zero-Code Migration

valkey-py provides `Redis` and `StrictRedis` aliases that map directly to `Valkey` and `StrictValkey`:

```python
# This works unchanged — Redis is an alias for Valkey
import valkey as redis

r = redis.Redis(host="localhost", port=6379, db=0)
r.set("foo", "bar")
print(r.get("foo"))  # b"bar"
```

### Available Aliases

| redis-py Name | valkey-py Name | Alias |
|---|---|---|
| `redis.Redis` | `valkey.Valkey` | `valkey.Redis` |
| `redis.StrictRedis` | `valkey.StrictValkey` | `valkey.StrictRedis` |
| `redis.RedisCluster` | `valkey.ValkeyCluster` | `valkey.RedisCluster` |
| `redis.RedisError` | `valkey.ValkeyError` | `valkey.RedisError` |

### Package Name

```bash
# Install valkey-py (replaces redis-py)
pip install valkey

# redis-py package is no longer maintained for new features
```

## Minimal Migration

Replace `redis` imports with `valkey`:

```python
# Before (redis-py)
import redis
r = redis.Redis(host="localhost", port=6379)

# After (valkey-py)
import valkey
r = valkey.Valkey(host="localhost", port=6379)
```

### Connection URL Scheme Change

```python
# redis-py used redis:// URLs
r = redis.Redis.from_url("redis://localhost:6379/0")

# valkey-py uses valkey:// URLs
r = valkey.Valkey.from_url("valkey://localhost:6379/0")

# redis:// still works for backward compatibility
r = valkey.Valkey.from_url("redis://localhost:6379/0")
```

URL schemes:
- `valkey://` — plain TCP (preferred)
- `valkeys://` — SSL/TLS
- `redis://` — still works (backward compat)
- `rediss://` — still works (backward compat)
- `unix://` — Unix Domain Socket

## RESP3 Migration

RESP3 is the new protocol with richer response types. Enable it by setting `protocol=3`:

```python
r = valkey.Valkey(host="localhost", port=6379, protocol=3)
```

### RESP3 Response Type Changes

| Command | RESP2 Response | RESP3 Response |
|---|---|---|
| `INFO` | `str` | `dict` (sectioned) |
| `HGETALL` | `list` of pairs | `dict` |
| `SMEMBERS` | `list` | `set` |
| `ZRANGE` | `list` | `set` or `list` |
| `CONFIG GET` | `list` of pairs | `dict` |
| `CLIENT INFO` | `str` | `dict` |

### Handling RESP3 Dict Responses

```python
r = valkey.Valkey(host="localhost", port=6379, protocol=3)

# INFO returns a dict in RESP3
info = r.info()
print(info["server"]["redis_version"])

# HGETALL returns a dict
user = r.hgetall("user:1")
print(user["name"])

# SMEMBERS returns a set
tags = r.smembers("tags")
```

If your code expects list responses, either:
1. Stay on RESP2 (`protocol=2` or omit the parameter)
2. Update code to handle dict/set responses

## API Differences

### New Classes

```python
# valkey-py preferred names
from valkey import Valkey, ValkeyCluster, ValkeyError
from valkey.connection import ConnectionPool, SSLConnection
from valkey.sentinel import Sentinel, SentinelConnectionPool

# redis-py names (aliases, still work)
from valkey import Redis, RedisCluster, RedisError
```

### ConnectionPool Changes

```python
# redis-py
pool = redis.ConnectionPool(host="localhost", port=6379)

# valkey-py (same API)
pool = valkey.ConnectionPool(host="localhost", port=6379)
```

### Exception Hierarchy

```python
# valkey-py exceptions (redis-py names are aliases)
from valkey.exceptions import (
    ValkeyError,           # RedisError
    ConnectionError,
    TimeoutError,
    ResponseError,
    DataError,
    AuthenticationError,
    WatchError,
    ExecAbortError,
    NoScriptError,
    PubSubError,
    OutOfMemoryError,
    ReadOnlyError,
)

# Cluster-specific
from valkey.exceptions import (
    ValkeyClusterException,
    ClusterError,
    ClusterDownError,
    AskError,
    MovedError,
    TryAgainError,
    ClusterCrossSlotError,
    SlotNotCoveredError,
)
```

## Feature Additions in valkey-py

### Credential Providers

```python
from valkey.credentials import CredentialProvider

class MyProvider(CredentialProvider):
    def get_credentials(self):
        return ("username", "password")

r = valkey.Valkey(
    host="localhost",
    port=6379,
    credential_provider=MyProvider(),
)
```

### Client-Side Caching

```python
r = valkey.Valkey(
    host="localhost",
    port=6379,
    protocol=3,
    cache_enabled=True,
    cache_max_size=10000,
)
```

### Enhanced Backoff Strategies

```python
from valkey.backoff import (
    EqualJitterBackoff,
    FullJitterBackoff,
    DecorrelatedJitterBackoff,
)

retry = valkey.retry.Retry(
    backoff=EqualJitterBackoff(cap=0.5, base=0.01),
    retries=3,
)
```

### `from_pool()` Method

```python
# valkey-py: explicit pool ownership
pool = valkey.ConnectionPool(host="localhost", port=6379)
r = valkey.Valkey.from_pool(pool)
# r.close() will also close the pool
```

## Migration Checklist

1. **Replace `pip install redis` with `pip install valkey`**
2. **Replace `import redis` with `import valkey`** (or use `import valkey as redis`)
3. **Replace `redis.Redis` with `valkey.Valkey`** (or keep `Redis` alias)
4. **Update URL schemes** from `redis://` to `valkey://` (optional — `redis://` still works)
5. **Check RESP2/RESP3 response types** if enabling `protocol=3`
6. **Update exception imports** from `redis.exceptions` to `valkey.exceptions`
7. **Update cluster imports** from `redis.cluster` to `valkey.cluster`
8. **Update async imports** from `redis.asyncio` to `valkey.asyncio`
9. **Update sentinel imports** from `redis.sentinel` to `valkey.sentinel`
10. **Test all commands** — API is compatible but verify response handling

## Common Migration Patterns

### Pattern 1: Drop-in Replace

```python
# Change only the import
import valkey as redis  # was: import redis

# All existing code works unchanged
r = redis.Redis(host="localhost", port=6379)
```

### Pattern 2: Full Rename

```python
# Find and replace
# redis.Redis → valkey.Valkey
# redis.RedisCluster → valkey.ValkeyCluster
# redis.RedisError → valkey.ValkeyError
# redis.ConnectionPool → valkey.ConnectionPool
# redis.exceptions → valkey.exceptions
# redis.asyncio → valkey.asyncio
# redis.cluster → valkey.cluster
# redis.sentinel → valkey.sentinel
```

### Pattern 3: Gradual Migration

```python
# Step 1: Use alias
import valkey as redis

# Step 2: Rename classes in new code
import valkey
r = valkey.Valkey(host="localhost", port=6379)

# Step 3: Remove redis-py dependency entirely
```

## Gotchas

- **`redis://` URLs still work** — valkey-py accepts both `redis://` and `valkey://` URL schemes.
- **RESP3 changes response types** — `INFO`, `HGETALL`, `SMEMBERS`, etc. return dicts/sets instead of lists. Test thoroughly.
- **Package name is `valkey`** — `pip install valkey`, not `pip install redis`. The `redis` PyPI package is the old redis-py.
- **Module imports changed** — `from redis.sentinel import Sentinel` becomes `from valkey.sentinel import Sentinel`.
- **`redis.lock` → `valkey.lock`** — Lock class moved to `valkey.lock`.
- **`redis.client.PubSub` → `valkey.client.PubSub`** — Pub/Sub class location unchanged relative to package.
- **Cluster `RedisCluster` → `ValkeyCluster`** — The cluster client class name changed. Alias available.
