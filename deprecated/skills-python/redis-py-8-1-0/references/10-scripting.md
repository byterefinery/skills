# Scripting

## EVAL — Inline Script

```python
# EVAL script numkeys key [key ...] arg [arg ...]
result = r.eval(
    "return redis.call('get', KEYS[1])",
    1,          # number of keys
    "mykey",    # key[1]
    "arg1",     # argv[1] (optional args)
)

# Multiple keys
result = r.eval(
    "return redis.call('mget', KEYS[1], KEYS[2])",
    2,
    "key1", "key2",
)
```

## EVALSHA — Script by SHA1

```python
import hashlib

script = "return redis.call('get', KEYS[1])"
sha = hashlib.sha1(script.encode()).hexdigest()

# EVALSHA — executes cached script by SHA1
result = r.evalsha(sha, 1, "mykey")

# If script is not cached, NOSCRIPT error is raised
# Use evalsha() with fallback:
try:
    result = r.evalsha(sha, 1, "mykey")
except redis.NoScriptError:
    result = r.eval(script, 1, "mykey")
```

## Script Object — Registered Scripts

```python
from redis.commands.core import Script

# Register a script — automatically handles EVAL/EVALSHA
get_script = r.register_script("return redis.call('get', KEYS[1])")

# First call uses EVAL (loads script), subsequent calls use EVALSHA
result = get_script(keys=["mykey"], args=["arg1"])

# Script with multiple keys
mget_script = r.register_script("return redis.call('mget', KEYS[1], KEYS[2])")
result = mget_script(keys=["key1", "key2"])

# Script with no keys
script = r.register_script("return 'hello'")
result = script(keys=[], args=[])
```

### Script in Pipelines

```python
script = r.register_script("return redis.call('incr', KEYS[1])")

pipe = r.pipeline()
pipe.set("counter", 0)
script(keys=["counter"], pipe=pipe)  # Pass pipeline
results = pipe.execute()
```

## Lua Scripting Patterns

### Atomic Increment with Check

```python
script = """
local current = tonumber(redis.call('get', KEYS[1]) or '0')
if current < tonumber(ARGV[1]) then
    current = current + 1
    redis.call('set', KEYS[1], current)
    return current
end
return -1  -- Limit reached
"""

incr_script = r.register_script(script)
result = incr_script(keys=["counter"], args=[100])  # Max 100
```

### Atomic List Operations

```python
# LPUSH + LTRIM atomically
script = """
redis.call('lpush', KEYS[1], ARGV[1])
redis.call('ltrim', KEYS[1], 0, tonumber(ARGV[2]))
return redis.call('llen', KEYS[1])
"""

script = r.register_script(script)
result = script(keys=["recent_items"], args=["new_item", 99])  # Keep last 100
```

### Distributed Lock (Lua-based)

```python
# redis-py Lock uses Lua internally for atomic acquire/release
# You can write your own:

acquire_script = """
if redis.call('setnx', KEYS[1], ARGV[1]) == 1 then
    if redis.call('expire', KEYS[1], tonumber(ARGV[2])) then
        return 1
    end
    return 0
end
return 0
"""

release_script = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
end
return 0
"""
```

## SCRIPT Commands

```python
# Check if script exists
exists = r.script_exists(sha1)  # List of booleans

# Delete scripts
r.script_flush()           # Delete all scripts
r.script_flush("ASYNC")    # Async flush (Redis 7.0+)

# Kill running script
r.script_kill()
```

## KEYS and ARGV

In Lua scripts executed by redis-py:

- **`KEYS[1]`, `KEYS[2]`, ...** — Key names (passed as the keys list)
- **`ARGV[1]`, `ARGV[2]`, ...** — Additional arguments (passed as the args list)
- **`redis.call()`** — Execute Redis commands within the script
- **`redis.pcall()`** — Execute command, catch errors (returns error string instead of failing)

```python
script = """
local key = KEYS[1]
local value = ARGV[1]
local ttl = tonumber(ARGV[2])

local result = redis.call('set', key, value, 'EX', ttl)
return result
"""

script_obj = r.register_script(script)
result = script_obj(keys=["mykey"], args=["myvalue", 3600])
```

## Script Gotchas

- **`register_script` handles caching** — It tries EVALSHA first, falls back to EVAL on `NOSCRIPT`. No manual caching needed
- **Keys affect cluster slot routing** — In cluster mode, all KEYS must hash to the same slot. Use hash tags for multi-key scripts
- **`redis.call` vs `redis.pcall`** — `call` propagates errors; `pcall` returns error as a string. Use `pcall` for non-critical operations
- **Script execution is atomic** — Lua scripts run to completion without interruption. Long-running scripts block the server
- **`evalsha` raises `NoScriptError`** — If the script is not in the server's cache. Use `register_script` for automatic handling
- **Scripts in pipelines** — Pass `pipe=pipe` to the script callable, or use `pipe.eval()`/`pipe.evalsha()` directly
- **Memory limit** — Scripts are limited to 2MB. Large scripts should be broken into smaller ones
- **Cluster mode** — `SCRIPT FLUSH` and `SCRIPT KILL` are cluster-wide commands that require `target_nodes` parameter
