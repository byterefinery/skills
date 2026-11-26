# Pipelines and Transactions

Source: docs/advanced_features.rst (Pipelines), docs/README examples, `valkey/client.py`.

## Default Pipelines

`r.pipeline()` returns a `Pipeline` instance (a subclass of the client) that buffers commands and sends them in one request. `execute()` sends all buffered commands and returns a list of responses, one per command, in order.

```python
>>> pipe = r.pipeline()
>>> pipe.set('foo', 'bar')
>>> pipe.get('bing')
>>> pipe.execute()
[True, b'baz']
```

Buffering calls return the pipeline itself, so chains work:

```python
pipe.set('foo', 'bar').sadd('faz', 'baz').incr('auto_number').execute()
# [True, True, 6]
```

Pipelines are **transactions by default** (wrapped in MULTI/EXEC). Pass `transaction=False` to keep the batching speedup without atomicity:

```python
pipe = r.pipeline(transaction=False)
```

## WATCH / MULTI Compare-and-Set

`watch()` monitors keys; if any watched key changes before `execute()`, the transaction is cancelled and `WatchError` is raised. After `watch()`, the pipeline is in **immediate execution mode** until `multi()` restores buffering.

```python
with r.pipeline() as pipe:
    while True:
        try:
            pipe.watch('OUR-SEQUENCE-KEY')
            current_value = pipe.get('OUR-SEQUENCE-KEY')   # executes immediately
            next_value = int(current_value) + 1
            pipe.multi()                                   # back to buffered mode
            pipe.set('OUR-SEQUENCE-KEY', next_value)
            pipe.execute()
            break
        except WatchError:
            continue
```

The pipeline must bind to a single connection for the duration of a WATCH, so the connection must be returned to the pool via `reset()`. Using the pipeline as a context manager (as above) calls `reset()` automatically; otherwise call `pipe.reset()` in a `finally` block.

## `r.transaction()` Helper

`r.transaction(func, *keys, ...)` handles the WATCH/MULTI/retry boilerplate. `func` receives the pipeline and must call `pipe.multi()` before any write commands:

```python
def client_side_incr(pipe):
    current_value = pipe.get('OUR-SEQUENCE-KEY')
    next_value = int(current_value) + 1
    pipe.multi()
    pipe.set('OUR-SEQUENCE-KEY', next_value)

r.transaction(client_side_incr, 'OUR-SEQUENCE-KEY')   # [True]
```

**Warning (from the docs):** transactions are retried an **infinite** number of times by default, which can cause infinite loops (e.g. if `r.set` is accidentally used instead of `pipe.set`). Use the `watch_delay` and `max_tries` arguments to mitigate.

## Cluster Pipelines

`ClusterPipeline` groups buffered commands by destination node and executes per-node batches in parallel; responses come back as a list in send order.

```python
with rc.pipeline() as pipe:
    pipe.set('foo', 'value1')
    pipe.set('bar', 'value2')
    pipe.get('foo')
    pipe.get('bar')
    print(pipe.execute())
# [True, True, b'value1', b'value2']
```

Cluster pipeline constraints (docs):
- Only **key-based commands** are supported.
- The pipeline inherits `read_from_replicas` from the cluster instance.
- The `transaction` option is **NOT supported** in cluster mode (commands are partitioned across nodes, so they cannot form one MULTI/EXEC block).
