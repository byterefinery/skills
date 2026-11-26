# Lua Scripting and Distributed Locks

Source: docs/lua_scripting.rst, `valkey/lock.py`, `valkey/asyncio/lock.py`.

## `register_script`

`client.register_script(lua_code)` returns a callable `Script` instance:

```python
lua = """
local value = redis.call('GET', KEYS[1])
value = tonumber(value)
return value * ARGV[1]"""
multiply = r.register_script(lua)

r.set('foo', 2)
multiply(keys=['foo'], args=[5])    # 10
```

Call arguments:

- `keys` — list of key names → Lua `KEYS`
- `args` — list of argument values → Lua `ARGV`
- `client` — the client (or pipeline) that executes the script; defaults to the client that created the Script. Scripts can therefore be executed against a *different* server:

```python
r2 = valkey.Valkey('valkey2.example.com')
r2.set('foo', 3)
multiply(keys=['foo'], args=[5], client=r2)   # 15
```

The Script object ensures the Lua source is loaded into Valkey's script cache and, on a `NOSCRIPT` error, loads the script and retries the execution.

## Scripts in Pipelines

Pass the pipeline as `client=`; the script is registered just prior to pipeline execution:

```python
pipe = r.pipeline()
pipe.set('foo', 5)
multiply(keys=['foo'], args=[5], client=pipe)
pipe.execute()
# [True, 25]
```

## Cluster Mode Limitations

Cluster support is limited (docs/lua_scripting.rst):

- `EVAL` / `EVALSHA` — sent to the node that owns the keys; all keys **must be on the same node**. With 0 keys the command goes to a **random primary**.
- `SCRIPT EXISTS` — sent to all primaries; each result boolean is the AND across nodes.
- `SCRIPT FLUSH` — sent to all primaries; result is AND of node responses.
- `SCRIPT LOAD` — sent to all primaries; returns the SHA1 digest.
- **Not supported**: `EVAL_RO`, `EVALSHA_RO`, and scripting inside cluster pipelines.

## `Lock`

`valkey.lock.Lock(valkey, name, timeout=None, sleep=0.1, blocking=True, blocking_timeout=None, thread_local=True)` — a shared distributed lock backed by three Lua scripts (`LUA_RELEASE_SCRIPT`, `LUA_EXTEND_SCRIPT`, `LUA_REACQUIRE_SCRIPT`) registered lazily via `register_scripts()`.

Parameters (from `valkey/lock.py`):

- `name` — lock key
- `timeout` — maximum life in seconds (float or int). **Default `None`: the lock stays locked until `release()`** — set a timeout to survive crashed holders.
- `sleep` — seconds to sleep per loop iteration while blocking (default `0.1`)
- `blocking` — whether `acquire` blocks until acquired (default `True`)
- `blocking_timeout` — max time to wait when blocking
- `thread_local` — lock state kept per-thread (default `True`)

API (all verified in `valkey/lock.py`): `acquire(blocking=..., token=...)` (custom token supported), `locked()`, `owned()`, `release()`, `extend(additional_time, replace_ttl=False)`, `reacquire()`, context-manager `__enter__`/`__exit__`.

- Release/extend/reacquire are atomic Lua scripts that verify the token first; releasing a lock you do not own raises `LockNotOwnedError` (see `valkey.exceptions.LockError` family).
- `blocking_timeout` prevents deadlocks when the lock cannot be acquired.
- Deadlock avoidance between your own clients is the user's responsibility (docstring: "It's left to the user to resolve deadlock issues").
- Async equivalent: `valkey.asyncio.lock.Lock` with `await lock.acquire(...)`; cluster clients expose `rc.lock(...)`.
