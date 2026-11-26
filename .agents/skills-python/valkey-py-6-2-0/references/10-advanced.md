# Advanced Features

Source: docs/resp3_features.rst, docs/opentelemetry.rst, docs/advanced_features.rst (threading), `valkey/_cache.py`, `valkey/client.py`, `valkey/connection.py`, `valkey/utils.py`.

## Client-Side Caching (6.x)

The client can cache command responses locally. Constructor options (sync `Valkey`; see 01-connections for the full list):

- `cache_enabled=True` — turn on client-side caching
- `client_cache` — custom `AbstractCache` implementation
- `cache_max_size` — max entries (sync default `10000`, async default `100`)
- `cache_ttl` — per-entry TTL seconds (`0` = no expiry)
- `cache_policy` — `lru` (default), `lfu`, or `random` (`valkey._cache.EvictionPolicy`)
- `cache_deny_list` / `cache_allow_list` — command-level opt-out/opt-in. The default deny list excludes inherently non-cacheable commands (e.g. `DUMP`, `EXPIRETIME`, `PEXPIRETIME`, `PFCOUNT`, `HRANDFIELD`, `JSON.DEBUG`, `BF.*` info/debug, `FT.*` search/index commands, `CF.*`, `CMS.*`).

## RESP3 (`protocol=3`)

- Enable on any client: `valkey.Valkey(host=..., port=..., protocol=3)`, `ValkeyCluster(startup_nodes=[...], protocol=3)`, async, or URL `valkey://localhost:6379?protocol=3`.
- Benefits (docs): fewer client-side type translations and new response types (doubles, true simple strings, maps, booleans).
- **Push notifications** are out-of-band RESP3 data. By default the client logs simple push messages; to customize, pass a handler when creating the pubsub object:

```python
def our_func(message):
    if "This special thing happened" in message:
        raise IOError("This was the message: \n" + message)

r = valkey.Valkey(protocol=3)
p = r.pubsub(push_handler_func=our_func)
```

## OpenTelemetry

Install the instrumentation package and call `instrument()` once; valkey-py then works as usual (docs/opentelemetry.rst):

```bash
pip install opentelemetry-instrumentation-redis
```

```python
from opentelemetry.instrumentation.redis import RedisInstrumentor

RedisInstrumentor().instrument()

client = valkey.Valkey()          # sync
# or valkey.asyncio.Valkey() with await — async client works too
```

The runnable example in `docs/examples/opentelemetry/` (with Docker Compose for Valkey + Uptrace) pins `opentelemetry-instrumentation-valkey==0.35b0` in its `requirements.txt` and shows wrapping client calls in explicit spans with `opentelemetry.trace`.

## Credentials

- Static: `username` + `password` constructor parameters.
- Dynamic: `credential_provider=` accepts a `valkey.credentials.CredentialProvider` (e.g. `UsernamePasswordCredentialProvider`) — useful for rotating or secret-manager-backed credentials.

## Threading (docs/advanced_features.rst)

- Valkey client instances are safe to share across threads (connections are checked out of the pool per command).
- **Exception**: `PubSub` and `Pipeline` objects must not cross threads.
- **`SELECT` is deliberately not implemented** on client instances: a pooled connection could be returned with a different db selected. Use one client/pool per database.

## libvalkey Parser

`pip install "valkey[libvalkey]"` provides a compiled response parser. `valkey/utils.py` sets `LIBVALKEY_AVAILABLE` only when an importable libvalkey has major version >= 4 ("Only support libvalkey 4.0.0 and above"). `LIBVALKEY_AVAILABLE` is exported from `valkey.utils` for feature detection.

## Client Identification / Health

- `client_name` → `CLIENT SETNAME`.
- `lib_name` (default `"valkey-py"`) and `lib_version` (package version) → `CLIENT SETINFO`.
- `health_check_interval` (seconds) → periodic health checks on idle connections.
- `valkey_connect_func` → callback invoked after each connection is established.

## Exceptions (`valkey.exceptions`)

Exported at package level: `ValkeyError` (base), `ConnectionError`, `TimeoutError`, `ResponseError`, `WatchError`, `ExecAbortError`, `PubSubError`, `ReadOnlyError`, `OutOfMemoryError`, `BusyLoadingError`, `AuthenticationError`, `AuthenticationWrongNumberOfArgsError`, `ChildDeadlockedError`, `DataError`, `InvalidResponse`, plus the lock family `LockError`/`LockNotOwnedError` (used by `valkey.lock`). Cluster raises `ValkeyClusterException` (mentioned in docs/clustering.rst) when no startup node is reachable or slot constraints are violated.
