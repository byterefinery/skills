# Connections

## Connection Parameters

### `Redis()` Constructor

```python
import redis

r = redis.Redis(
    host="localhost",           # Redis server hostname
    port=6379,                  # Redis server port
    db=0,                       # Database number (0-15, standalone only)
    password="secret",          # AUTH password
    username="default",         # AUTH username (Redis 6.0+ ACL)
    encoding="utf-8",           # Encoding for keys/values
    encoding_errors="strict",   # Error handler for encoding
    decode_responses=False,     # If True, decode responses to str
    socket_timeout=5,           # Socket read timeout in seconds
    socket_connect_timeout=5,   # Socket connect timeout in seconds
    socket_keepalive=True,      # Enable TCP keepalive
    socket_keepalive_options=None,  # Custom keepalive options dict
    socket_read_size=65536,     # Socket read buffer size
    max_connections=None,       # Max connections in pool (None = unlimited)
    health_check_interval=0,    # Seconds between health checks (0 = disabled)
    client_name=None,           # CLIENT SETNAME identifier
    retry_on_timeout=False,     # Deprecated — TimeoutError included by default
    retry=redis.retry.Retry(...),  # Retry policy
    retry_on_error=None,        # Additional error types to retry on
    ssl=False,                  # Use SSL/TLS
    ssl_cert_reqs="required",   # SSL certificate verification mode
    ssl_ca_certs=None,          # Path to CA certificate file
    ssl_check_hostname=True,    # Verify server hostname matches cert
    ssl_min_version=None,       # Minimum TLS version
    ssl_ciphers=None,           # Allowed cipher suites
    single_connection_client=False,  # Use single connection (not thread-safe)
    credential_provider=None,   # CredentialProvider for dynamic credentials
    protocol=None,              # RESP protocol version (2, 3, or None=default RESP3)
    legacy_responses=True,      # True=RESP2-compatible shapes, False=unified
    cache=None,                 # Custom CacheInterface implementation
    cache_config=None,          # CacheConfig for client-side caching
    event_dispatcher=None,      # EventDispatcher for observability hooks
    maint_notifications_config=None,  # Maintenance notifications config
    driver_info=None,           # DriverInfo for CLIENT SETINFO
)
```

### `from_url()` Class Method

```python
# TCP
r = redis.Redis.from_url("redis://localhost:6379/0")
r = redis.Redis.from_url("redis://user:pass@localhost:6379/0")
r = redis.Redis.from_url("redis://default:mypassword@localhost:6379/0?db=1&socket_timeout=5")

# SSL/TLS
r = redis.Redis.from_url("rediss://localhost:6379/0")
r = redis.Redis.from_url("rediss://user:pass@localhost:6379/0?ssl_cert_reqs=required")

# Unix socket
r = redis.Redis.from_url("unix:///path/to/redis.sock?db=0")
r = redis.Redis.from_url("unix://user:pass@/path/to/redis.sock?db=0")

# With protocol and response options
r = redis.Redis.from_url("redis://localhost:6379/0?protocol=3&legacy_responses=false")
r = redis.Redis.from_url("redis://localhost:6379/0?decode_responses=yes")
```

URL query parameters map to constructor kwargs. Boolean values accept `True`/`False`, `Yes`/`No`, `1`/`0`.

### `from_pool()` Class Method

```python
# Client takes ownership of the pool — close() disconnects all connections
pool = redis.ConnectionPool.from_url("redis://localhost:6379/0")
r = redis.Redis.from_pool(pool)

# When r.close() is called, the pool is closed and all connections disconnected
```

**Key difference from `connection_pool=`:** `from_pool()` sets `auto_close_connection_pool=True`, meaning the client owns the pool lifecycle. Passing `connection_pool=pool` to the constructor does NOT take ownership — the pool must be managed separately.

```python
# Shared pool — use context manager for lifecycle
with redis.ConnectionPool.from_url("redis://localhost:6379/0") as pool:
    r1 = redis.Redis(connection_pool=pool)
    r2 = redis.Redis(connection_pool=pool)
    # Both clients share the pool; neither closes it
```

## Connection Pools

### `ConnectionPool`

```python
pool = redis.ConnectionPool(
    host="localhost",
    port=6379,
    db=0,
    password="secret",
    max_connections=50,
    connection_class=redis.Connection,
    health_check_interval=30,
    retry_on_error=[redis.ConnectionError],
    retry=redis.retry.Retry(...),
)

# Get a connection (returned to pool after use)
conn = pool.get_connection("_")
try:
    # use conn
finally:
    pool.release(conn)

# Close pool (disconnects all connections)
pool.close()

# ConnectionPool supports context manager protocol
with redis.ConnectionPool(host="localhost", port=6379) as pool:
    r = redis.Redis(connection_pool=pool)
```

### `BlockingConnectionPool`

```python
pool = redis.BlockingConnectionPool(
    host="localhost",
    port=6379,
    max_connections=10,
    timeout=5,  # Max seconds to wait for an available connection
)
```

When all connections are in use, `BlockingConnectionPool` blocks up to `timeout` seconds waiting for one to be returned. `ConnectionPool` raises `MaxConnectionsError` immediately when exhausted.

### Connection Classes

| Class | Module | Purpose |
|---|---|---|
| `Connection` | `redis.connection` | Standard TCP connection |
| `SSLConnection` | `redis.connection` | TCP with SSL/TLS |
| `UnixDomainSocketConnection` | `redis.connection` | Unix domain socket |

```python
# Use custom connection class in pool
pool = redis.ConnectionPool(
    connection_class=redis.SSLConnection,
    ssl_cert_reqs="required",
    ssl_ca_certs="/path/to/ca.pem",
)
```

## SSL/TLS Connections

```python
# Via constructor
r = redis.Redis(
    host="redis.example.com",
    port=6379,
    ssl=True,
    ssl_certfile="/path/to/client-cert.pem",
    ssl_keyfile="/path/to/client-key.pem",
    ssl_ca_certs="/path/to/ca.pem",
    ssl_cert_reqs="required",
    ssl_check_hostname=True,
    ssl_min_version=ssl.TLSVersion.TLSv1_2,
)

# Via URL
r = redis.Redis.from_url("rediss://user:pass@redis.example.com:6379/0")

# OCSP validation (requires `ocsp` extra: pip install "redis[ocsp]")
r = redis.Redis(
    host="redis.example.com",
    port=6379,
    ssl=True,
    ssl_validate_ocsp=True,          # Online OCSP
    ssl_validate_ocsp_stapled=True,  # Stapled OCSP
)
```

## Credential Providers

For dynamic credentials (e.g., from AWS Secrets Manager, Azure Key Vault):

```python
from redis.credentials import CredentialProvider, UsernamePasswordCredentialProvider

# Static credentials
cred = UsernamePasswordCredentialProvider(username="default", password="secret")
r = redis.Redis(host="localhost", port=6379, credential_provider=cred)

# Dynamic credentials
class MyCredentialProvider(CredentialProvider):
    def get_credentials(self):
        # Fetch from secrets store
        return get_credentials_from_vault()

    async def get_credentials_async(self):
        return await get_credentials_from_vault_async()

r = redis.Redis(host="localhost", credential_provider=MyCredentialProvider())
```

`StreamingCredentialProvider` supports real-time credential rotation via callbacks.

## Health Checks

```python
# Check connection health every 30 seconds before use
r = redis.Redis(host="localhost", port=6379, health_check_interval=30)
```

When `health_check_interval > 0`, redis-py sends a `PING` before executing a command if the connection has been idle longer than the interval. Connection and timeout errors during health checks are retried once automatically.

## Driver Info

```python
from redis.driver_info import DriverInfo

# Identify your application in CLIENT LIST/INFO
info = DriverInfo(name="my-app", lib_version="1.0.0")
info = info.add_upstream_driver("django-redis", "5.4.0")

r = redis.Redis(host="localhost", driver_info=info)
# CLIENT SETINFO LIB-NAME my-app(django-redis_v5.4.0) LIB-VER 1.0.0

# Disable CLIENT SETINFO entirely
r = redis.Redis(host="localhost", driver_info=None)
```

## Single Connection Client

```python
# Single connection — not thread-safe, but slightly faster
r = redis.Redis(host="localhost", single_connection_client=True)

# Or via client() method — returns a single-connection view
r = redis.Redis(host="localhost")
single = r.client()
```

Useful for monitoring (`MONITOR`), dump/restore operations, or when you need deterministic connection behavior.

## Connection URL Parsing

```python
from redis.connection import parse_url

# Parse URL into connection kwargs
kwargs = parse_url("redis://user:pass@localhost:6379/0?db=1&socket_timeout=5")
```

Supported URL schemes: `redis://`, `rediss://` (SSL), `unix://` (Unix socket), `sentinel://`, `sents://` (Sentinel SSL).
