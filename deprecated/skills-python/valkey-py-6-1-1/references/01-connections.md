# Connections

Connection management is the foundation of valkey-py. Every client uses a `ConnectionPool` to manage TCP or Unix socket connections to Valkey servers.

## Creating Connections

### Direct Constructor

```python
import valkey

# Minimal — defaults: localhost:6379, db=0
r = valkey.Valkey()

# Explicit parameters
r = valkey.Valkey(
    host="localhost",
    port=6379,
    db=0,
    password="secret",
    username="default",
    decode_responses=False,
    encoding="utf-8",
    encoding_errors="strict",
    socket_timeout=5,
    socket_connect_timeout=5,
    socket_keepalive=True,
    socket_keepalive_options=None,
    retry_on_timeout=False,
    retry=None,
    ssl=False,
    ssl_keyfile=None,
    ssl_certfile=None,
    ssl_cert_reqs="required",
    ssl_ca_certs=None,
    ssl_ca_data=None,
    ssl_check_hostname=False,
    ssl_password=None,
    ssl_validate_ocsp=False,
    protocol=2,          # 2 or 3 (RESP version)
    client_name="my-app",
    max_connections=None, # passed to ConnectionPool
    health_check_interval=0,
    client_cache=False,   # client-side caching
)
```

### From URL

```python
# TCP
r = valkey.Valkey.from_url("valkey://localhost:6379/0")
r = valkey.Valkey.from_url("valkey://user:pass@localhost:6379/0")

# SSL/TLS
r = valkey.Valkey.from_url("valkeys://user:pass@localhost:6379/0")

# Unix socket
r = valkey.Valkey.from_url("unix:///path/to/valkey.sock?db=0")
r = valkey.Valkey.from_url("unix://user@/path/to/valkey.sock?db=0&password=secret")

# URL query parameters map to constructor kwargs
r = valkey.Valkey.from_url(
    "valkey://localhost:6379/0?socket_timeout=10&retry_on_timeout=True&decode_responses=True"
)
```

URL schemes:
- `valkey://` — plain TCP
- `valkeys://` — SSL-wrapped TCP
- `unix://` — Unix Domain Socket

Database number is taken from path (`/0`) or `db` query parameter, in that priority order.

### From Connection Pool

```python
pool = valkey.ConnectionPool(
    host="localhost",
    port=6379,
    db=0,
    max_connections=50,
    password="secret",
    decode_responses=True,
)
r = valkey.Valkey(connection_pool=pool)
```

### From URL (ConnectionPool)

```python
pool = valkey.ConnectionPool.from_url("valkey://localhost:6379/0")
r = valkey.Valkey(connection_pool=pool)
```

## Connection Pools

`ConnectionPool` manages a pool of persistent connections. Each `Valkey()` instance gets its own pool by default.

```python
pool = valkey.ConnectionPool(
    host="localhost",
    port=6379,
    db=0,
    max_connections=50,        # max simultaneous connections (None = unlimited)
    connection_class=valkey.Connection,
    connection_kwargs={},      # extra kwargs passed to each Connection
    wrapper=None,
)
```

### BlockingConnectionPool

A pool that blocks (rather than raising) when no connections are available:

```python
from valkey.connection import BlockingConnectionPool

pool = BlockingConnectionPool(
    host="localhost",
    port=6379,
    max_connections=50,
    timeout=5,  # seconds to wait for an available connection
)
```

### Pool Lifecycle

```python
# Get a connection from the pool
conn = pool.get_connection("COMMAND_NAME")

# Return it to the pool (after use)
pool.release(conn)

# Disconnect all idle connections
pool.disconnect(inuse_connections=False)

# Disconnect all connections (including in-use)
pool.disconnect(inuse_connections=True)
```

### Sharing Pools

```python
# Multiple clients sharing one pool
pool = valkey.ConnectionPool(host="localhost", port=6379, db=0)
r1 = valkey.Valkey(connection_pool=pool)
r2 = valkey.Valkey(connection_pool=pool)

# Both r1 and r2 draw from the same connection pool
```

## SSL/TLS Connections

```python
# Via constructor
r = valkey.Valkey(
    host="localhost",
    port=6379,
    ssl=True,
    ssl_cert_reqs="required",
    ssl_ca_certs="/path/to/ca.pem",
    ssl_certfile="/path/to/client-cert.pem",
    ssl_keyfile="/path/to/client-key.pem",
    ssl_check_hostname=True,
)

# Via URL (valkeys://)
r = valkey.Valkey.from_url("valkeys://localhost:6379/0")

# SSL connection class
pool = valkey.ConnectionPool(
    host="localhost",
    port=6379,
    connection_class=valkey.SSLConnection,
    connection_kwargs={
        "ssl_cert_reqs": "required",
        "ssl_ca_certs": "/path/to/ca.pem",
    },
)
```

### OCSP Validation

For certificate revocation checking (requires `cryptography` package):

```python
r = valkey.Valkey(
    host="localhost",
    port=6379,
    ssl=True,
    ssl_validate_ocsp=True,
)
```

## Unix Domain Sockets

```python
r = valkey.Valkey(unix_socket_path="/var/run/valkey/valkey.sock")

# Or via URL
r = valkey.Valkey.from_url("unix:///var/run/valkey/valkey.sock?db=0")
```

Unix socket connections use `UnixDomainSocketConnection` internally.

## Connection Parameters Reference

| Parameter | Default | Description |
|---|---|---|
| `host` | `"localhost"` | Server hostname or IP |
| `port` | `6379` | Server port |
| `db` | `0` | Database number (0-15) |
| `password` | `None` | AUTH password |
| `username` | `None` | AUTH username (ACL) |
| `socket_timeout` | `None` | Socket operation timeout in seconds |
| `socket_connect_timeout` | `socket_timeout` | Connection establishment timeout |
| `socket_keepalive` | `False` | Enable TCP keepalive |
| `socket_keepalive_options` | `None` | Dict of keepalive socket options |
| `socket_read_size` | `65536` | Bytes to read per socket operation |
| `encoding` | `"utf-8"` | Character encoding for strings |
| `encoding_errors` | `"strict"` | Error handler for encoding/decoding |
| `decode_responses` | `False` | Auto-decode byte responses to str |
| `retry_on_timeout` | `False` | Retry on TimeoutError |
| `retry` | `None` | `Retry` object for advanced retry |
| `ssl` | `False` | Enable SSL/TLS |
| `ssl_cert_reqs` | `"required"` | SSL certificate verification mode |
| `ssl_ca_certs` | `None` | Path to CA certificate file |
| `ssl_ca_data` | `None` | PEM-encoded CA certificate data |
| `ssl_certfile` | `None` | Path to client certificate file |
| `ssl_keyfile` | `None` | Path to client private key file |
| `ssl_check_hostname` | `False` | Verify server hostname matches cert |
| `ssl_password` | `None` | Password for encrypted client key |
| `ssl_validate_ocsp` | `False` | Enable OCSP certificate validation |
| `protocol` | `2` | RESP protocol version (2 or 3) |
| `client_name` | `None` | Client name (visible in CLIENT LIST) |
| `max_connections` | `None` | Max connections in pool (None = unlimited) |
| `health_check_interval` | `0` | Seconds between PING health checks |
| `credential_provider` | `None` | `CredentialProvider` for dynamic credentials |
| `cache_enabled` | `False` | Enable client-side caching |
| `cache_max_size` | `10000` | Max entries in client-side cache |
| `cache_ttl` | `0` | TTL for cache entries (0 = no TTL) |
| `cache_policy` | `LRU` | Eviction policy: LRU, LFU, RANDOM |
| `cache_deny_list` | `DEFAULT_DENY_LIST` | Commands excluded from caching |
| `cache_allow_list` | `DEFAULT_ALLOW_LIST` | Commands allowed for caching |

## Connection Health Checks

Enable periodic PING-based health checks:

```python
r = valkey.Valkey(
    host="localhost",
    port=6379,
    health_check_interval=30,  # check every 30 seconds
)
```

The connection sends `PING` and expects `PONG`. On failure, the connection is disconnected and re-established on the next command.

## Closing Connections

```python
# Single connection client — keeps one connection open
r = valkey.Valkey.from_url("valkey://localhost:6379/0", single_connection_client=True)

# Close releases the connection back to the pool and disconnects it
r.close()

# For pool-backed clients, close() disconnects the entire pool
r = valkey.Valkey(host="localhost", port=6379)
r.close()  # disconnects all connections in the pool
```

## libvalkey Parser

When `libvalkey` (C library) is installed via `pip install "valkey[libvalkey]"`, valkey-py uses it for faster response parsing. No code changes needed — it is detected automatically.

```python
import valkey
from valkey.utils import LIBVALKEY_AVAILABLE

print(LIBVALKEY_AVAILABLE)  # True if libvalkey is installed
```
