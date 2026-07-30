# Sentinel

Valkey Sentinel provides high availability through automatic master discovery and failover. The `Sentinel` class discovers the current master, and `SentinelConnectionPool` manages connections to it.

## Sentinel Manager

```python
from valkey.sentinel import Sentinel

# Create sentinel manager
sentinel = Sentinel(
    [("sentinel1.example.com", 26379),
     ("sentinel2.example.com", 26379),
     ("sentinel3.example.com", 26379)],
    socket_timeout=0.1,
    socket_connect_timeout=0.1,
)

# Discover master address
master_address = sentinel.discover_master("mymaster")
# ("10.0.0.5", 6379)

# Discover replicas
replicas = sentinel.discover_slaves("mymaster")
# [("10.0.0.6", 6379), ("10.0.0.7", 6379)]

# Check sentinel master address (single sentinel, no quorum)
address = sentinel.sentinel_master_address("mymaster")
```

### Sentinel Constructor Parameters

| Parameter | Default | Description |
|---|---|---|
| `sentinels` | required | List of `(host, port)` tuples for Sentinel nodes |
| `min_sentinels` | `None` | Minimum Sentinels to query for quorum |
| `socket_timeout` | `0.1` | Socket timeout in seconds |
| `socket_connect_timeout` | `0.1` | Connection timeout in seconds |
| `sentinel_kwargs` | `{}` | Extra kwargs for Sentinel connections |
| `dns_refresh_interval` | `30` | Seconds between DNS refresh attempts |

## SentinelConnectionPool

The recommended way to use Sentinel — the pool discovers the master and reconnects on failover:

```python
from valkey.sentinel import Sentinel, SentinelConnectionPool
import valkey

sentinel = Sentinel(
    [("sentinel1.example.com", 26379),
     ("sentinel2.example.com", 26379)],
    socket_timeout=0.1,
)

# Master pool
pool = SentinelConnectionPool(
    service_name="mymaster",
    sentinel_manager=sentinel,
    password="secret",
    db=0,
    decode_responses=True,
)

r = valkey.Valkey(connection_pool=pool)
r.set("key", "value")
```

### Reading from Replicas

```python
# Replica pool — reads from replicas with round-robin
replica_pool = SentinelConnectionPool(
    service_name="mymaster",
    sentinel_manager=sentinel,
    is_master=False,    # connect to replicas
    check_connection=True,  # PING after connecting
)

replica_r = valkey.Valkey(connection_pool=replica_pool)
value = replica_r.get("key")  # may return stale data
```

### SSL Sentinel Connections

```python
pool = SentinelConnectionPool(
    service_name="mymaster",
    sentinel_manager=sentinel,
    ssl=True,
    ssl_cert_reqs="required",
    ssl_ca_certs="/path/to/ca.pem",
)
```

## Sentinel with Authentication

```python
# Sentinel requires auth
sentinel = Sentinel(
    [("sentinel1.example.com", 26379)],
    sentinel_kwargs={"password": "sentinel_password"},
)

# Valkey master requires auth
pool = SentinelConnectionPool(
    service_name="mymaster",
    sentinel_manager=sentinel,
    password="valkey_password",
)
```

## Failover Handling

When a failover occurs:

1. Sentinels detect the master is unreachable
2. A new master is elected from replicas
3. `SentinelConnectionPool` discovers the new master on next connection attempt
4. Idle connections to the old master are disconnected
5. New connections go to the new master

```python
# Failover is handled transparently by SentinelConnectionPool
# After failover, existing commands may raise ConnectionError
# but subsequent commands automatically reconnect to the new master

try:
    r.get("key")
except valkey.ConnectionError:
    # Connection to old master was dropped
    # Next command will reconnect to new master
    pass

r.get("key")  # Works — connected to new master
```

## Sentinel Commands

```python
# Sentinel manager exposes sentinel commands
sentinel.sentinel("MASTER", "mymaster")
sentinel.sentinel("MASTERS")
sentinel.sentinel("REPLICAS", "mymaster")
sentinel.sentinel("SENTINELS", "mymaster")
sentinel.sentinel("GET-MASTER-ADDR-BY-NAME", "mymaster")
sentinel.sentinel("RESET", "mymaster")
sentinel.sentinel("FAILOVER", "mymaster")
sentinel.sentinel("CKQUORUM", "mymaster")
```

## Master/Replica Address Access

```python
pool = SentinelConnectionPool(
    service_name="mymaster",
    sentinel_manager=sentinel,
)

# Get current master address
master = pool.master_address
print(master)  # ("10.0.0.5", 6379)

# Access via proxy
print(pool.proxy.master_address)
```

## DNS Refresh

For dynamic DNS endpoints, enable periodic DNS resolution:

```python
sentinel = Sentinel(
    [("sentinel-dns.example.com", 26379)],
    dns_refresh_interval=30,  # refresh DNS every 30 seconds
)
```

## Complete Example

```python
import valkey
from valkey.sentinel import Sentinel

# Sentinel configuration
SENTINELS = [
    ("sentinel-1.prod.internal", 26379),
    ("sentinel-2.prod.internal", 26379),
    ("sentinel-3.prod.internal", 26379),
]
SERVICE_NAME = "myapp"

# Create sentinel manager
sentinel = Sentinel(
    SENTINELS,
    socket_timeout=0.5,
    socket_connect_timeout=0.5,
    min_sentinels=2,  # need at least 2 sentinels responding
)

# Master connection pool
master_pool = SentinelConnectionPool(
    service_name=SERVICE_NAME,
    sentinel_manager=sentinel,
    password="secret",
    db=0,
    decode_responses=True,
    max_connections=50,
)

# Replica connection pool (for read scaling)
replica_pool = SentinelConnectionPool(
    service_name=SERVICE_NAME,
    sentinel_manager=sentinel,
    password="secret",
    db=0,
    decode_responses=True,
    is_master=False,
    check_connection=True,
)

# Clients
master = valkey.Valkey(connection_pool=master_pool)
replica = valkey.Valkey(connection_pool=replica_pool)

# Write to master
master.set("user:1:name", "Alice")

# Read from replica (may be slightly stale)
name = replica.get("user:1:name")
```

## Gotchas

- **Minimum 3 Sentinels** — For reliable quorum-based decisions, run at least 3 Sentinel instances. With fewer, a single failure may block discovery.
- **`socket_timeout` should be low** — Sentinel queries are discovery calls, not data operations. Use 0.1-0.5 seconds so failures are detected quickly.
- **Failover is not instant** — There is a delay between master failure detection and new master election. Commands during this window may raise `ConnectionError`.
- **`check_connection=True` adds latency** — It sends PING after each new connection. Enable only if replicas may be in inconsistent states.
- **Replicas serve stale data** — `is_master=False` connects to replicas which may lag behind the master. Use for read scaling where eventual consistency is acceptable.
- **Pool owns the connection lifecycle** — `SentinelConnectionPool` manages reconnection to new masters. Do not manually create connections to specific addresses.
