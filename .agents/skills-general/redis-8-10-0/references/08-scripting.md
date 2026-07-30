# Scripting

Redis supports Lua scripting and the Functions system for server-side logic.

## Lua Scripting

Lua scripts execute atomically on the server, enabling multi-step operations without round trips.

### EVAL

```
EVAL <script> <numkeys> [key [key ...]] [arg [arg ...]]
```

```lua
-- Increment and check threshold
local current = redis.call('INCR', KEYS[1])
if tonumber(current) == tonumber(ARGV[1]) then
    redis.call('EXPIRE', KEYS[1], ARGV[2])
end
return current
```

```bash
redis-cli EVAL "local v = redis.call('GET', KEYS[1]); return v" 1 mykey
```

### EVALSHA

```
EVALSHA <sha1> <numkeys> [key [key ...]] [arg [arg ...]]
```

Scripts are cached by SHA1 hash. Use `SCRIPT EXISTS` to check cache, `SCRIPT LOAD` to preload.

### Script Commands

- `EVAL` / `EVALSHA` — execute script
- `SCRIPT EXISTS <sha1> [sha1 ...]` — check cached scripts
- `SCRIPT LOAD <script>` — load script into cache
- `SCRIPT KILL` — kill running script (non-readonly)
- `SCRIPT FLUSH [ASYNC|SYNC]` — flush script cache
- `SCRIPT DEBUG` — enable/disable debug mode

### Scripting Rules

- Scripts run atomically — no interleaving with other commands
- `redis.call()` — synchronous, propagates errors
- `redis.pcall()` — synchronous, returns error as value
- `redis.evalsha()` / `redis.call()` — call other scripts/commands
- Scripts cannot block indefinitely (timeout via `lua-time-limit`)
- `KEYS[1..n]` for keys, `ARGV[1..m]` for arguments
- Keys are auto-propagated to replicas and AOF

## Functions (since 7.0)

Functions provide a managed, persistent scripting environment. Code is stored in libraries and invoked by name.

### Function Commands

- `FUNCTION LOAD <code> [REPLACE] [LANGUAGE <lang>]` — create/update library
- `FUNCTION DELETE <library-name>` — delete library
- `FUNCTION DUMP` — dump all functions
- `FUNCTION RESTORE <data> [FLUSH|APPEND|REPLACE]` — restore functions
- `FUNCTION LIST [WITHCODE] [LIBRARYNAME <pattern>]` — list libraries
- `FUNCTION INFO [<library-name>]` — library details
- `FUNCTION KILL` — kill running function
- `FUNCTION FLUSH [ASYNC|SYNC]` — flush all functions
- `FCALL <function-name> <numkeys> [key [key ...]] [arg [arg ...]]` — call function
- `FCALL_RO` — read-only call (can run on replicas)

### Example

```bash
# Load a library
FUNCTION LOAD "#!lua name=mylib\nredis.register_function('hello', function(keys, args) return 'Hello ' .. args[1] end)"

# Call it
FCALL hello 0 world
# Returns: "Hello world"
```

### Function Properties

- **Persistent** — stored in RDB/AOF, survives restarts
- **Replaceable** — `FUNCTION LOAD REPLACE` updates existing libraries
- **Replicated** — function calls propagate to replicas
- **Versioned** — each load creates a new version
- **Multi-language** — Lua is the default; other languages may be added via modules

## Scripting Best Practices

- **Keep scripts short** — long scripts block the server
- **Use `redis.pcall()` for non-critical calls** — prevents script abort on errors
- **Prefer `FCALL_RO` for read-only functions** — can run on replicas
- **Cache scripts with `SCRIPT LOAD`** — avoid sending full script body each time
- **Use `EVALSHA` after initial `EVAL`** — reduces network traffic
- **Avoid `KEYS` command in scripts** — it can block on large keyspaces; use `SCAN` instead
- **Set `lua-time-limit`** — default 5000ms. Scripts exceeding this can be killed with `SCRIPT KILL` (if non-readonly)

## Gotchas

- **Lua is statically linked by default** — use `BUILD_LUA=no` to omit or `BUILD_LUA=module` for dynamic loading.
- **Scripts are atomic** — a long-running script blocks all other commands. Keep scripts under a few milliseconds.
- **`SCRIPT KILL` only works on non-readonly scripts** — scripts that only read data cannot be killed.
- **`FCALL` propagates to AOF and replicas** — use `FCALL_RO` for read-only operations that don't need replication.
- **Functions are stored in RDB/AOF** — large function libraries increase persistence file size.
- **`FUNCTION RESTORE` requires `FLUSH` on first use** — subsequent uses can use `APPEND` or `REPLACE`.
- **`HIMPORT` fieldsets are scoped to script invocation** — they are freed after the script completes.
