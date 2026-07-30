# Scripting

Valkey supports Lua scripting and the Functions system for server-side logic execution.

## Lua Scripting

Lua scripts execute atomically on the server, enabling complex operations as single transactions.

### EVAL / EVALSHA

```bash
# Execute inline Lua script
EVAL "return redis.call('GET', KEYS[1])" 1 mykey

# Execute by SHA1 hash (faster for repeated scripts)
EVALSHA <sha1> 1 mykey

# Read-only variants (safe in cluster read replicas)
EVAL_RO "return redis.call('GET', KEYS[1])" 1 mykey
EVALSHA_RO <sha1> 1 mykey
```

### Script management

```bash
# Load script and get SHA1
SCRIPT LOAD "return redis.call('GET', KEYS[1])"

# Check if script exists
SCRIPT EXISTS <sha1>

# Flush scripting cache
SCRIPT FLUSH [ASYNC|SYNC]

# Show loaded scripts
SCRIPT SHOW

# Kill running script (only if no writes performed)
SCRIPT KILL

# Debug mode
SCRIPT DEBUG <ON|OFF|STEP>
```

### Lua API

Inside scripts, use `redis.call()`, `redis.pcall()`, `redis.eval()`, `redis.evalsha()`:

```lua
-- Atomic increment with conditional logic
local current = redis.call('GET', KEYS[1])
if current == false then
    redis.call('SET', KEYS[1], 1)
    return 1
end
current = tonumber(current) + 1
redis.call('SET', KEYS[1], current)
return current
```

### Time limit

```conf
# Max execution time in milliseconds (default 5000)
lua-time-limit 5000
# Alias: busy-reply-threshold 5000
```

When exceeded, the server returns BUSY errors. Only `SCRIPT KILL`, `FUNCTION KILL`, and `SHUTDOWN NOSAVE` are accepted.

### Insecure API

```conf
# Allow scripts to call dangerous commands
# lua-enable-insecure-api no
```

## Functions (since 8.0)

Functions provide a more structured way to define reusable server-side logic with libraries and manifests.

### Function commands

```bash
# Load a function
FUNCTION LOAD "#!lua name=mylib\nredis.call('SET', KEYS[1], ARGV[1])"

# List functions
FUNCTION LIST [LIBRARY <name>] [WITHCODE]

# Delete a library
FUNCTION DELETE <library-name>

# Flush all functions
FUNCTION FLUSH [ASYNC|SYNC]

# Dump function for migration
FUNCTION DUMP

# Restore from dump
FUNCTION RESTORE <dump-data> [FLUSH|APPEND|REPLACE]

# Get function stats
FUNCTION STATS

# Kill running function
FUNCTION KILL
```

### FCALL

```bash
# Execute function
FCALL myfunc 1 mykey arg1

# Read-only variant
FCALL_RO myfunc 1 mykey arg1
```

### Function format

```lua
#!lua name=mylibrary description="My library" enabled=true

redis.register_function {
    function = myfunc,
    description = "My function",
    flags = {"no-writes"}
}

function myfunc(context, args)
    return redis.call('GET', args[1])
end
```

### Lua as module

Since 9.1.0, the Lua scripting engine can be loaded as a module instead of statically linked:

```conf
# Build options
make BUILD_LUA=static    # default — statically linked
make BUILD_LUA=module    # dynamically loaded module
make BUILD_LUA=no        # no Lua support
```

When built as a module, use `loadmodule` to load it. INFO includes a `scripting` section showing engine status.

## Scripting best practices

- **Keep scripts short** — they block the main thread during execution
- **Use EVALSHA** for repeated scripts to reduce network overhead
- **Use read-only commands** in cluster replicas (`EVAL_RO`, `FCALL_RO`)
- **Handle errors** with `redis.pcall()` for non-critical operations
- **Use Functions** for complex, reusable logic with proper library management
- **Monitor with `FUNCTION STATS`** to track execution patterns
