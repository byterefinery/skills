# Pipelines and Transactions

## Pipeline Basics

Pipelines batch multiple commands into a single round-trip, dramatically reducing latency for groups of operations.

```python
# Create a pipeline
pipe = r.pipeline()

# Queue commands (all return the pipeline for chaining)
pipe.set("key1", "value1")
pipe.set("key2", "value2")
pipe.get("key1")
pipe.get("key2")

# Execute all at once
results = pipe.execute()
# [True, True, "value1", "value2"]

# Chaining
pipe.set("a", 1).set("b", 2).get("a").get("b").execute()
```

### Transactional vs Non-Transactional

```python
# Transactional (default) — wraps in MULTI/EXEC
pipe = r.pipeline(transaction=True)
pipe.set("k1", "v1")
pipe.set("k2", "v2")
pipe.execute()  # Atomic: all succeed or all fail

# Non-transactional — no MULTI/EXEC, just batching
pipe = r.pipeline(transaction=False)
pipe.set("k1", "v1")
pipe.set("k2", "v2")
pipe.execute()  # Each command executes independently
```

### Context Manager

```python
# Auto-reset on exit (releases connection back to pool)
with r.pipeline() as pipe:
    pipe.set("key1", "value1")
    pipe.set("key2", "value2")
    results = pipe.execute()

# Explicit reset
pipe = r.pipeline()
pipe.set("key", "value")
pipe.execute()
pipe.reset()  # Returns connection to pool
```

**Always use pipelines as context managers** or call `reset()` explicitly. Without reset, the connection stays bound to the pipeline and is not returned to the pool.

## WATCH and Optimistic Locking

WATCH provides CAS (compare-and-swap) semantics for transactions.

```python
with r.pipeline() as pipe:
    while True:
        try:
            # WATCH the key — transaction aborts if it changes
            pipe.watch("balance")

            # Read current value (executed immediately, not buffered)
            balance = int(pipe.get("balance"))

            if balance >= 100:
                # Start buffering (MULTI)
                pipe.multi()
                pipe.set("balance", balance - 100)
                pipe.lpush("transactions", f"debit:100")

                # Execute (EXEC)
                pipe.execute()
                break  # Success
            else:
                pipe.unwatch()
                break  # Insufficient balance

        except redis.WatchError:
            # Another client modified 'balance' — retry
            continue
```

### `transaction()` Helper

```python
def callback(pipe):
    pipe.set("balance", pipe.get("balance") - 100)

# Auto-retry on WatchError
result = r.transaction(callback, "balance")
```

With `value_from_callable=True`, returns the value from the callback instead of pipeline results.

## Pipeline Response Callbacks

Pipelines inherit response callbacks from the client. Custom callbacks apply to pipeline results.

```python
# Set callback for a command
pipe.set_response_callback("GET", lambda r: r.decode() if r else None)

# Pipeline callbacks are resolved at execute() time
results = pipe.execute()
```

## Cluster Pipelines

In cluster mode, pipelines have additional constraints.

```python
from redis.cluster import RedisCluster

rc = RedisCluster(host="localhost", port=6379)

# All keys must hash to the same slot
pipe = rc.pipeline()
pipe.set("{user}1:name", "Alice")
pipe.set("{user}1:email", "alice@example.com")
pipe.execute()  # Works: same slot via {user} hash tag

# Cross-slot pipelines fail with CrossSlotTransactionError
pipe = rc.pipeline()
pipe.set("user:1", "Alice")
pipe.set("user:2", "Bob")
pipe.execute()  # Error: keys hash to different slots
```

### Hash Tags

Force keys to the same slot using `{tag}` syntax. Only the text inside `{}` is hashed.

```python
# These keys always route to the same node
r.set("{user}:1:name", "Alice")
r.set("{user}:1:email", "alice@example.com")
r.set("{user}:1:age", "30")

# The tag can be any string
r.set("{account123}:balance", "1000")
r.set("{account123}:currency", "USD")
```

## Pipeline Gotchas

- **`execute()` returns a list** — All results are in a list, one per queued command, in order
- **Errors in transactional pipelines** — If any command errors, the entire transaction is aborted (`ExecAbortError`). Non-transactional pipelines continue executing remaining commands
- **WATCH keys must be in the same pipeline** — You cannot WATCH a key in one pipeline and execute the transaction in another
- **`WATCH` switches to immediate mode** — Commands between `watch()` and `multi()` execute immediately. Use this to read values before the transaction
- **Pipeline is not thread-safe** — Do not share Pipeline objects across threads
- **Empty pipelines** — Executing an empty transactional pipeline returns `[]`. Empty non-transactional pipelines also return `[]`
- **`pipeline()` creates a new instance** — Each call to `r.pipeline()` creates a fresh pipeline with its own connection

## WATCH Delay

For testing or controlled retry scenarios:

```python
result = r.transaction(
    callback,
    "balance",
    watch_delay=0.1  # Sleep 100ms between retries
)
```

## ExecAbortError Handling

```python
try:
    with r.pipeline() as pipe:
        pipe.watch("key")
        pipe.multi()
        pipe.set("key", "value")
        pipe.execute()
except redis.ExecAbortError:
    # Transaction was aborted (Lua script error, etc.)
    # WATCH errors raise WatchError, not ExecAbortError
    handle_abort()
```

`ExecAbortError` indicates a transaction-level failure (e.g., a Lua script error). `WatchError` indicates a watched key was modified.
