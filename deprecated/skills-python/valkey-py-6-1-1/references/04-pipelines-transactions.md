# Pipelines and Transactions

Pipelines batch multiple commands into a single network round-trip. Transactions (MULTI/EXEC) guarantee atomic execution of a command group.

## Basic Pipeline

```python
# Create pipeline
pipe = r.pipeline()

# Queue commands
pipe.set("key1", "value1")
pipe.set("key2", "value2")
pipe.get("key1")
pipe.get("key2")
pipe.delete("key1")

# Execute all at once
results = pipe.execute()
# [True, True, "value1", "value2", 1]
```

### Context Manager

```python
with r.pipeline() as pipe:
    pipe.set("key1", "value1")
    pipe.set("key2", "value2")
    pipe.get("key1")
    results = pipe.execute()
```

### Chaining

```python
pipe = r.pipeline()
results = (
    pipe.set("key1", "value1")
       .set("key2", "value2")
       .get("key1")
       .execute()
)
```

### Transactional Pipeline

```python
pipe = r.pipeline(transaction=True)
pipe.set("key1", "value1")
pipe.set("key2", "value2")
results = pipe.execute()
# Commands wrapped in MULTI/EXEC — all succeed or all fail
```

### Non-transactional Pipeline

```python
pipe = r.pipeline(transaction=False)
pipe.set("key1", "value1")
pipe.set("key2", "value2")
results = pipe.execute()
# Commands sent in batch but NOT wrapped in MULTI/EXEC
# Individual command errors don't affect others
```

## WATCH (Optimistic Locking)

WATCH monitors keys for changes. If a watched key is modified by another client between WATCH and EXEC, the transaction is aborted.

```python
pipe = r.pipeline(True)

# Watch a key
pipe.watch("balance")

# Read current value
balance = int(r.get("balance") or 0)

if balance >= 100:
    # Start transaction
    pipe.multi()
    pipe.set("balance", balance - 100)
    try:
        result = pipe.execute()
        # Transaction succeeded
    except valkey.WatchError:
        # Another client modified 'balance' — retry
        pass
else:
    pipe.unwatch()
```

### WATCH with Multiple Keys

```python
pipe = r.pipeline(True)
pipe.watch("account:A", "account:B")

balance_a = int(r.get("account:A") or 0)
balance_b = int(r.get("account:B") or 0)

if balance_a >= 50:
    pipe.multi()
    pipe.set("account:A", balance_a - 50)
    pipe.set("account:B", balance_b + 50)
    pipe.execute()
```

### WATCH in Context Manager

```python
pipe = r.pipeline(True)
pipe.watch("counter")

try:
    current = int(r.get("counter") or 0)
    pipe.multi()
    pipe.set("counter", current + 1)
    pipe.execute()
except valkey.WatchError:
    # Key was modified — handle conflict
    pass
finally:
    pipe.reset()  # always clean up
```

## Pipeline Execution Details

### Return Values

`execute()` returns a list where each element corresponds to a queued command:

```python
pipe = r.pipeline()
pipe.set("a", 1)      # → True
pipe.get("a")          # → b"1"
pipe.incr("a")         # → 2
pipe.delete("nonexist") # → 0
pipe.exists("a")       # → 1

results = pipe.execute()
# [True, b"1", 2, 0, 1]
```

### Errors in Pipelines

Exceptions from individual commands are placed into the results list:

```python
pipe = r.pipeline()
pipe.set("key", "value")
pipe.lpush("key", "item")  # Error: wrong type
pipe.get("key")

results = pipe.execute()
# [True, ResponseError("WRONGTYPE"), b"value"]

for i, result in enumerate(results):
    if isinstance(result, Exception):
        print(f"Command {i} failed: {result}")
```

### Pipeline with Large Batches

```python
pipe = r.pipeline(transaction=False)
for i in range(10000):
    pipe.hset(f"user:{i}", mapping={"name": f"user{i}", "score": i})
pipe.execute()
```

## Transaction Guarantees

- **Atomicity** — All commands in a MULTI/EXEC block execute as a unit. If any command errors, the entire transaction is aborted.
- **Isolation** — Commands in a transaction are not interleaved with commands from other clients.
- **No rollbacks** — If a command within a transaction fails (e.g., wrong type), the error is recorded but other commands still execute. The transaction does not rollback partial changes.

## Pipeline vs Transaction Comparison

| Aspect | Pipeline (non-transactional) | Pipeline (transactional) |
|---|---|---|
| Network round-trips | 1 (batched) | 1 (batched) |
| Atomicity | No — commands execute individually | Yes — MULTI/EXEC wraps all |
| Isolation | No — interleaved with other clients | Yes — queued and executed atomically |
| WATCH support | No | Yes |
| Error handling | Errors in results list | EXEC returns None on WATCH failure |
| Use case | Bulk writes, batch reads | CAS patterns, atomic updates |

## CAS Pattern (Compare-And-Swap)

```python
def update_atomically(r, key, update_fn, max_retries=5):
    """Atomically update a key using WATCH/MULTI/EXEC."""
    for attempt in range(max_retries):
        pipe = r.pipeline(True)
        pipe.watch(key)

        current = r.get(key)
        pipe.multi()
        pipe.set(key, update_fn(current))

        try:
            result = pipe.execute()
            return result[0]  # True if SET succeeded
        except valkey.WatchError:
            continue  # retry on conflict

    raise valkey.WatchError("Max retries exceeded")

# Usage
update_atomically(r, "counter", lambda val: str(int(val or 0) + 1))
```

## DISCARD

Cancel a transaction without executing:

```python
pipe = r.pipeline(True)
pipe.multi()
pipe.set("key", "value")
pipe.execute_command("DISCARD")  # cancel the transaction
```

## UNWATCH

Clear all watched keys:

```python
pipe = r.pipeline(True)
pipe.watch("key1", "key2")
# ... decide not to proceed
pipe.unwatch()
```

## Pipeline Gotchas

- **Pipelines are not reusable** — After `execute()`, the pipeline is reset. Create a new one for subsequent batches.
- **`execute()` clears the command stack** — All queued commands are sent and the pipeline resets.
- **WATCH keys must be watched before MULTI** — The order is: `watch()` → read values → `multi()` → queue commands → `execute()`.
- **Pipeline commands don't return immediately** — Each command method returns the pipeline object (for chaining), not the command result. Results come from `execute()`.
- **In cluster mode, pipeline keys must share a slot** — Use hash tags `{tag}` to ensure co-location, or use cluster-aware pipelines.
