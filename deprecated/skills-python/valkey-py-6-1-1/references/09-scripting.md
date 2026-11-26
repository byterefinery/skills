# Scripting

Valkey supports Lua scripting for atomic multi-step operations. Scripts execute server-side in a single thread, guaranteeing atomicity without explicit transactions.

## EVAL — Inline Scripting

```python
# EVAL script numkeys key [key ...] arg [arg ...]
result = r.eval(
    "return redis.call('get', KEYS[1])",
    1,       # number of keys
    "mykey", # key[1]
)

# Script with arguments
result = r.eval(
    """
    local key = KEYS[1]
    local increment = tonumber(ARGV[1])
    local current = tonumber(redis.call('get', key) or '0')
    local new_value = current + increment
    redis.call('set', key, new_value)
    return new_value
    """,
    1,
    "counter",
    5,
)
```

### EVAL_RO — Read-Only Evaluation

```python
result = r.eval_ro(
    "return redis.call('get', KEYS[1])",
    1,
    "mykey",
)
```

## EVALSHA — Script by Hash

Register a script once, then reference it by its SHA1 hash:

```python
import hashlib

script = "return redis.call('get', KEYS[1])"
sha1 = hashlib.sha1(script.encode()).hexdigest()

# Evaluate by hash (faster — no script transfer)
result = r.evalsha(sha1, 1, "mykey")

# If script is not loaded, you get NoScriptError
# Load it first:
r.script_load(script)  # returns sha1
result = r.evalsha(sha1, 1, "mykey")
```

### EVALSHA_RO

```python
result = r.evalsha_ro(sha1, 1, "mykey")
```

## Registered Scripts

The `Script` object caches the SHA1 and handles automatic loading:

```python
# Register a script
incr_script = r.register_script("""
    local key = KEYS[1]
    local increment = tonumber(ARGV[1])
    local current = tonumber(redis.call('get', key) or '0')
    local new_value = current + increment
    redis.call('set', key, new_value)
    return new_value
""")

# Call like a function — auto-loads if needed
result = incr_script(keys=["counter"], args=[5])
result = incr_script(keys=["counter"], args=[10])

# Script can be called multiple times
# First call: sends SCRIPT LOAD + EVALSHA
# Subsequent calls: EVALSHA directly
```

### Script in Pipelines

```python
pipe = r.pipeline()
incr_script = r.register_script("return redis.call('incr', KEYS[1])")

pipe.set("counter", 0)
incr_script(keys=["counter"], args=[], pipe=pipe)
incr_script(keys=["counter"], args=[], pipe=pipe)

results = pipe.execute()
# [True, 1, 2]
```

## Script Management Commands

```python
# Load script (returns SHA1)
sha1 = r.script_load("return 'hello'")

# Check if script exists
exists = r.script_exists(sha1)  # [True] or [False]

# Flush loaded scripts
r.script_flush()
r.script_flush("ASYNC")

# Kill running script
r.script_kill()
```

## Common Script Patterns

### Atomic Increment with Bounds

```python
bounded_incr = r.register_script("""
    local key = KEYS[1]
    local increment = tonumber(ARGV[1])
    local min_val = tonumber(ARGV[2])
    local max_val = tonumber(ARGV[3])

    local current = tonumber(redis.call('get', key) or '0')
    local new_value = current + increment

    if new_value < min_val or new_value > max_val then
        return -1  -- out of bounds
    end

    redis.call('set', key, new_value)
    return new_value
""")

result = bounded_incr(keys=["score"], args=[5, 0, 100])
```

### Set with Expiration (Atomic)

```python
set_with_ttl = r.register_script("""
    local key = KEYS[1]
    local value = ARGV[1]
    local ttl = tonumber(ARGV[2])

    redis.call('set', key, value)
    redis.call('expire', key, ttl)
    return redis.call('ttl', key)
""")

result = set_with_ttl(keys=["session:abc"], args=["data", 3600])
```

### Queue with Bounded Size

```python
bounded_lpush = r.register_script("""
    local key = KEYS[1]
    local value = ARGV[1]
    local max_size = tonumber(ARGV[2])

    redis.call('lpush', key, value)
    redis.call('ltrim', key, 0, max_size - 1)
    return redis.call('llen', key)
""")

result = bounded_lpush(keys=["recent:items"], args=["new_item", 100])
```

### Leader Election

```python
elect_leader = r.register_script("""
    local key = KEYS[1]
    local candidate = ARGV[1]
    local ttl = tonumber(ARGV[2])

    local current = redis.call('get', key)
    if current == false or current == candidate then
        redis.call('set', key, candidate, 'EX', ttl)
        return 1  -- elected
    end
    return 0  -- not elected
""")

result = elect_leader(keys=["leader"], args=["worker-1", 30])
```

### Rate Limiter

```python
rate_limit = r.register_script("""
    local key = KEYS[1]
    local window = tonumber(ARGV[1])
    local max_requests = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])

    -- Remove old entries
    redis.call('zremrangebyscore', key, 0, now - window)

    -- Count current requests
    local count = redis.call('zcard', key)

    if count < max_requests then
        redis.call('zadd', key, now, now .. ':' .. math.random())
        redis.call('expire', key, window)
        return 1  -- allowed
    end
    return 0  -- rate limited
""")

import time
allowed = rate_limit(
    keys=["rate:user:123"],
    args=[60, 10, time.time()],  # 10 requests per 60 seconds
)
```

## Lua API in Scripts

Inside Lua scripts, use `redis.call()` and `redis.pcall()`:

```lua
-- redis.call() — raises error on failure
local value = redis.call('GET', KEYS[1])

-- redis.pcall() — returns error table instead of raising
local status, value = pcall(redis.call, 'GET', KEYS[1])

-- redis.call('COMMAND', ...) — any Valkey command
redis.call('SET', KEYS[1], ARGV[1])
redis.call('EXPIRE', KEYS[1], tonumber(ARGV[2]))

-- Access reply types
local ok = redis.call('SET', 'key', 'value')  -- "OK"
local num = redis.call('INCR', 'counter')      -- integer
local bulk = redis.call('GET', 'key')          -- bulk string or false
local array = redis.call('SMEMBERS', 'set')    -- array or empty array
```

### redis.error_reply and redis.status_reply

```lua
-- Return custom error
return redis.error_reply("Custom error message")

-- Return status string
return redis.status_reply("OK")
```

## Async Scripting

```python
from valkey.asyncio import Valkey

async def main():
    r = Valkey(host="localhost", port=6379)

    script = r.register_script("return redis.call('get', KEYS[1])")
    result = await script(keys=["mykey"], args=[])

    await r.close()

asyncio.run(main())
```

## Gotchas

- **Scripts are atomic** — Lua scripts run to completion without interruption. Long scripts block the server.
- **`redis.call()` vs `redis.pcall()`** — `call()` propagates errors (aborts the script). `pcall()` returns the error for handling.
- **KEYS and ARGV are 1-indexed** — `KEYS[1]` is the first key, not `KEYS[0]`.
- **`numkeys` parameter in EVAL** — Must match the actual number of key arguments. Mismatch causes an error.
- **Scripts are loaded per-server** — Each Valkey node in a cluster loads scripts independently. Use `register_script()` which handles this.
- **`SCRIPT FLUSH` clears all scripts** — After flushing, `EVALSHA` raises `NoScriptError` until the script is reloaded.
- **No network calls in scripts** — Lua scripts cannot make external network requests. They only call Valkey commands.
- **Deterministic execution** — Avoid `math.random()` without seeding, as scripts should be deterministic for replication/AOF.
