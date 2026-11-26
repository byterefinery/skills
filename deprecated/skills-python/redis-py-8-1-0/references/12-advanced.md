# Advanced Features

## Distributed Locks

```python
from redis.lock import Lock

# Basic lock
lock = Lock(r, "resource-lock", timeout=10, sleep=0.1, blocking=True, blocking_timeout=5)

if lock.acquire():
    try:
        # Critical section
        pass
    finally:
        lock.release()

# Context manager
with Lock(r, "resource-lock", timeout=10) as lock:
    # Critical section
    pass

# Non-blocking
lock = Lock(r, "resource-lock", timeout=10, blocking=False)
acquired = lock.acquire()
if acquired:
    try:
        pass
    finally:
        lock.release()

# Extend lock TTL
lock.extend(additional_time=5)           # Add 5 seconds to existing TTL
lock.extend(additional_time=10, replace_ttl=True)  # Replace TTL entirely

# Reacquire (renew)
lock.reacquire()  # Re-set the original TTL
```

### Lock Parameters

| Parameter | Default | Description |
|---|---|---|
| `timeout` | `None` | Max lock lifetime in seconds |
| `sleep` | `0.1` | Seconds to sleep between acquisition attempts |
| `blocking` | `True` | Block until acquired or fail immediately |
| `blocking_timeout` | `None` | Max time to spend trying to acquire |
| `thread_local` | `True` | Store lock token in thread-local storage |
| `raise_on_release_error` | `True` | Raise on release failure or log warning |

## Retry and Backoff

### Retry Policy

```python
from redis.retry import Retry
from redis.backoff import ExponentialWithJitterBackoff, EqualJitterBackoff, FullJitterBackoff

# Default retry (already included in Redis() constructor)
r = redis.Redis(host="localhost")

# Custom retry
r = redis.Redis(
    host="localhost",
    retry=Retry(
        backoff=ExponentialWithJitterBackoff(base=0.008, cap=0.512),
        retries=3,
        supported_errors=(redis.ConnectionError, redis.TimeoutError),
    ),
)

# Retry on additional error types
r = redis.Redis(
    host="localhost",
    retry_on_error=[redis.ResponseError],
)
```

### Backoff Strategies

| Strategy | Description |
|---|---|
| `NoBackoff` | No delay between retries |
| `ConstantBackoff(n)` | Fixed delay of `n` seconds |
| `ExponentialBackoff` | `base * 2^failures`, capped at `cap` |
| `ExponentialWithJitterBackoff` | Exponential with random jitter |
| `FullJitterBackoff` | Random delay up to exponential cap |
| `EqualJitterBackoff` | Half exponential + random half |
| `DecorrelatedJitterBackoff` | AWS-style decorrelated jitter |

```python
from redis.backoff import default_backoff

# Default backoff (EqualJitterBackoff)
backoff = default_backoff()
```

## Client-Side Caching

Requires RESP3 protocol. The server pushes invalidation notifications when cached keys change.

```python
from redis.cache import CacheConfig

# Default caching config
r = redis.Redis(
    host="localhost",
    protocol=3,
    cache_config=CacheConfig(),
)

# Custom cache implementation
from redis.cache import CacheInterface, CacheConfig

class MyCache(CacheInterface):
    # Implement cache interface
    pass

r = redis.Redis(
    host="localhost",
    protocol=3,
    cache=MyCache(),
    cache_config=CacheConfig(
        max_size=10000,
        eviction_policy="frequency_based",  # or "time_based"
    ),
)
```

### Cache Configuration

```python
from redis.cache import CacheConfig

config = CacheConfig(
    max_size=10000,                  # Max entries
    eviction_policy="frequency_based",  # "time_based" or "frequency_based"
    # Commands allowed to be cached
    allowed_commands=None,  # None = default set
)
```

## Maintenance Notifications

Server-initiated push notifications about upcoming maintenance events. Requires RESP3.

```python
from redis.maint_notifications import MaintNotificationsConfig

config = MaintNotificationsConfig(
    enabled=True,
    # Notification handlers
)

r = redis.Redis(
    host="localhost",
    protocol=3,
    maint_notifications_config=config,
)
```

### OSS Cluster Maintenance Notifications

```python
from redis.maint_notifications import OSSMaintNotificationsHandler

handler = OSSMaintNotificationsHandler()

r = redis.Redis(
    host="localhost",
    protocol=3,
    oss_cluster_maint_notifications_handler=handler,
)
```

## Driver Info

Identify your application in `CLIENT LIST` / `CLIENT INFO` output.

```python
from redis.driver_info import DriverInfo

# Basic
info = DriverInfo(name="my-app", lib_version="1.0.0")

# With upstream driver
info = DriverInfo().add_upstream_driver("django-redis", "5.4.0")
# formatted_name: "redis-py(django-redis_v5.4.0)"

r = redis.Redis(host="localhost", driver_info=info)

# Disable CLIENT SETINFO
r = redis.Redis(host="localhost", driver_info=None)
```

## Credential Providers

Dynamic credentials from external sources.

```python
from redis.credentials import CredentialProvider, UsernamePasswordCredentialProvider

# Static
cred = UsernamePasswordCredentialProvider(username="default", password="secret")
r = redis.Redis(host="localhost", credential_provider=cred)

# Dynamic
class VaultCredentialProvider(CredentialProvider):
    def get_credentials(self):
        return fetch_from_vault()

    async def get_credentials_async(self):
        return await fetch_from_vault_async()

r = redis.Redis(host="localhost", credential_provider=VaultCredentialProvider())
```

## OCSP Validation

Online Certificate Status Protocol for SSL connections.

```python
# Requires: pip install "redis[ocsp]"
r = redis.Redis(
    host="redis.example.com",
    port=6379,
    ssl=True,
    ssl_validate_ocsp=True,           # Online OCSP check
    ssl_validate_ocsp_stapled=True,   # Stapled OCSP (faster)
)
```

## Event Dispatcher

Hook into client lifecycle events.

```python
from redis.event import EventDispatcher, AfterConnectionReleasedEvent

class MyDispatcher(EventDispatcher):
    def on_after_connection_released(self, event: AfterConnectionReleasedEvent):
        print(f"Connection released: {event}")

r = redis.Redis(host="localhost", event_dispatcher=MyDispatcher())
```

## Single Connection Client

```python
# Not thread-safe, but slightly faster (no pool overhead)
r = redis.Redis(host="localhost", single_connection_client=True)

# Or get a single-connection view of a pooled client
pooled = redis.Redis(host="localhost")
single = pooled.client()
```

Useful for `MONITOR`, deterministic connection behavior, or avoiding pool contention.

## Monitor

```python
monitor = r.monitor()
for entry in monitor:
    print(entry)
    # {'db': 0, 'timestamp': 1234567890, 'command': "SET 'key' 'value'", 'client': ...}

monitor.close()
```

## Advanced Gotchas

- **Lock token is thread-local by default** — A lock acquired in one thread cannot be released in another unless `thread_local=False`
- **Lock without timeout is dangerous** — If the client crashes, a lock without `timeout` is never released. Always set a timeout
- **`health_check_interval` adds latency** — Each health check is a PING. Set appropriately for your latency requirements
- **Client-side caching requires RESP3** — Cache tracking and invalidation only work with RESP3
- **Maintenance notifications require RESP3** — Server push notifications only work with RESP3
- **`single_connection_client` is not thread-safe** — Never share a single-connection client across threads
- **`retry` with `retry_on_error`** — `retry_on_error` errors are added to the Retry's default supported errors. To replace defaults entirely, create a custom `Retry` with explicit `supported_errors`
- **Default retry already includes TimeoutError** — `retry_on_timeout=True` is deprecated and redundant
- **`close()` behavior differs** — `from_pool()` and `from_url()` clients own their pool and close it. `Redis(connection_pool=pool)` does not close the pool
- **`SELECT` is deliberately omitted** — redis-py does not expose `SELECT` because it breaks connection pooling. Use separate clients per database
