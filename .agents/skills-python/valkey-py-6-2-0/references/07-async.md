# Async Client

Source: docs/connections.rst (Async Client, Async Cluster Client), docs/resp3_features.rst, `valkey/asyncio/` (client.py, cluster.py, connection.py, lock.py, retry.py, sentinel.py).

## Basic Usage

The async client lives in `valkey.asyncio`, **not** at the top level:

```python
import asyncio
import valkey.asyncio as valkey

async def main():
    r = valkey.Valkey(host='localhost', port=6379)
    await r.set('key', 'value')
    result = await r.get('key')
    await r.close()        # aclose() is the alias-style name; both exist

asyncio.run(main())
```

URL form: `valkey.asyncio` also exposes `from_url` (same schemes: `valkey://`, `valkeys://`, `unix://`).

## Client Parameters (async `Valkey.__init__`)

Async constructor is **keyword-only** (`*,` in the signature). Key differences from the sync client:

- `socket_timeout` defaults to `5` (sync client default is `None`).
- `cache_max_size` defaults to `100` (sync default is `10000`).
- `auto_close_connection_pool` is accepted but **deprecated** (passing it emits a `DeprecationWarning`); it only had an effect when `connection_pool` was `None` — the client now assumes you manage the pool if you pass one.
- Same `protocol=2` default, `decode_responses=False`, `credential_provider`, `retry`, `cache_*` options as sync.

Other async client surface (from `valkey/asyncio/client.py`):

- `await r.initialize()` — usable as `r = await valkey.Valkey(...)`-style initialization (method returns the client).
- `await r.close()` / `await r.aclose()` — close the client (optional `close_connection_pool` argument).
- `r.pipeline()` — async pipelines with the same semantics (transaction flag, WATCH/MULTI).
- `r.pubsub()` — async PubSub (same message dict shape as sync).
- `r.register_script(...)` — async Script objects.
- `r.lock(...)` — async lock factory (see below).

## Async Lock

`valkey.asyncio.lock.Lock` mirrors the sync lock: `async def acquire(...)` (blocking/blocking_timeout semantics, token support), `def release()`, plus `locked()`/`owned()`/`extend()`/`reacquire()` equivalents. The sync class is in `valkey.lock`.

## Async Cluster

`valkey.asyncio.cluster.ValkeyCluster` mirrors the sync cluster client: `startup_nodes`/`host`+`port`/`from_url`, `target_nodes` flags, `pipeline(transaction=None, shard_hint=None)`, `pubsub(node=None, host=None, port=None, **kwargs)`, `mget_nonatomic`/`mset_nonatomic`, `read_from_replicas`, retry/`cluster_error_retry_attempts` parameters. See 05-cluster for the shared semantics.

## Async Sentinel

`valkey.asyncio.sentinel` re-exports the async Sentinel classes (see 06-sentinel).
