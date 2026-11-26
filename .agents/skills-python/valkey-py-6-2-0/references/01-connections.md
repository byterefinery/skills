# Connections

Full connection surface for valkey-py 6.2.0. All parameters below are taken from `valkey/client.py` (`Valkey.__init__`) and `valkey/connection.py` (`AbstractConnection.__init__`).

## Valkey() Parameters (sync client)

| Parameter | Default | Notes |
|---|---|---|
| `host` | `"localhost"` | TCP host |
| `port` | `6379` | TCP port |
| `db` | `0` | Database number |
| `password` | `None` | AUTH password |
| `username` | `None` | ACL username |
| `socket_timeout` | `None` | Per-connection timeout (connection-level default is 5s) |
| `socket_connect_timeout` | `None` | TCP connect timeout |
| `socket_keepalive` / `socket_keepalive_options` | `None` | TCP keepalive |
| `connection_pool` | `None` | Pass a shared `ConnectionPool`; if absent, a new pool is created |
| `unix_socket_path` | `None` | Unix Domain Socket path (selects `UnixDomainSocketConnection`) |
| `encoding` / `encoding_errors` | `"utf-8"` / `"strict"` | Response decoding (old names `charset`/`errors` are deprecated) |
| `decode_responses` | `False` | Return `str` instead of `bytes` |
| `retry_on_timeout` | `False` | Retry on `TimeoutError` |
| `retry_on_error` | `None` | List of exception types to retry on |
| `retry` | `None` | `Retry` instance (see 09-retry-backoff) |
| `ssl` | `False` | Enable TLS (selects `SSLConnection`) |
| `ssl_keyfile`, `ssl_certfile` | `None` | Client certificate/key |
| `ssl_cert_reqs` | `"required"` | Cert verification policy |
| `ssl_ca_certs`, `ssl_ca_path`, `ssl_ca_data` | `None` | CA configuration |
| `ssl_check_hostname` | `False` | Hostname verification |
| `ssl_password` | `None` | Key passphrase |
| `ssl_validate_ocsp`, `ssl_validate_ocsp_stapled` | `False` | OCSP validation (see `valkey/ocsp.py`) |
| `ssl_ocsp_context`, `ssl_ocsp_expected_cert` | `None` | OCSP context/expected cert |
| `ssl_min_version`, `ssl_ciphers` | `None` | TLS lower bound / cipher list |
| `max_connections` | `None` | Pool size limit |
| `single_connection_client` | `False` | If `True`, no pool is used and the instance is not thread-safe |
| `health_check_interval` | `0` | Seconds between health checks on idle connections |
| `client_name` | `None` | `CLIENT SETNAME` value |
| `lib_name` / `lib_version` | `"valkey-py"` / package version | `CLIENT SETINFO` values |
| `valkey_connect_func` | `None` | Hook invoked on each new connection |
| `credential_provider` | `None` | `CredentialProvider` (e.g. `UsernamePasswordCredentialProvider`) |
| `protocol` | `2` | RESP protocol version (2 or 3) |
| `cache_enabled` | `False` | Client-side caching (see 10-advanced) |
| `client_cache` | `None` | Custom `AbstractCache` implementation |
| `cache_max_size` | `10000` | Cache entries cap (async client default is 100) |
| `cache_ttl` | `0` | Per-entry TTL seconds (0 = no expiry) |
| `cache_policy` | LRU | One of `lru`, `lfu`, `random` (`valkey._cache.EvictionPolicy`) |
| `cache_deny_list` | module defaults | Commands never cached (e.g. `DUMP`, `EXPIRETIME`, `FT.*`, `JSON.DEBUG`) |
| `cache_allow_list` | module defaults | Commands allowed in cache |

## URL Schemes (`Valkey.from_url`)

- `valkey://[[username]:[password]]@host:6379/0` — plain TCP.
- `valkeys://...` — TLS-wrapped TCP.
- `unix://[username@]/path/to/socket.sock?db=0[&password=password]` — Unix socket.

Database number resolution (first found wins): 1) `db` querystring option, 2) URL path for `valkey://`/`valkeys://`, 3) `db` keyword argument; default `db=0`. All querystring values are percent-decoded (`urllib.parse.unquote`) and cast to Python types (booleans accept `True`/`False`/`Yes`/`No`); uncastable values raise `ValueError`. Querystring arguments win over keyword arguments. `from_url` sets `auto_close_connection_pool=True` — the returned client owns the pool it created.

## Pools

- `ConnectionPool` — default pool; created per client when you do not pass one.
- `BlockingConnectionPool` — blocking variant, exported from `valkey.connection`.
- `Connection` / `SSLConnection` / `UnixDomainSocketConnection` — individual connection classes; useful when building custom pools. Connection-level parameters include `socket_read_size=65536`, `parser_class`, `command_packer`, plus the same db/password/timeout/retry/protocol/cache options as the client.

## Credential Providers

Pass `credential_provider=` (a `valkey.credentials.CredentialProvider`, e.g. `UsernamePasswordCredentialProvider`) instead of static `username`/`password` for rotating or external credentials.

## RESP3

`protocol=3` enables RESP3 on any connection type (standalone, async, cluster, URL via `?protocol=3`). See 10-advanced for push notifications.
