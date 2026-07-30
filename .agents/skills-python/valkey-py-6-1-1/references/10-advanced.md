# Advanced Features

Distributed locks, retry/backoff strategies, client-side caching, credential providers, and OCSP validation.

## Distributed Locks

The `Lock` class implements a Redisson-like distributed lock using Lua scripts for atomicity.

### Basic Usage

```python
from valkey.lock import Lock

lock = Lock(r, "my-resource", timeout=10, sleep=0.1)

# Acquire
acquired = lock.acquire()
if acquired:
    try:
        # critical section
        pass
    finally:
        lock.release()
```

### Context Manager

```python
with Lock(r, "my-resource", timeout=10) as lock:
    # lock is automatically acquired and released
    pass
```

### Constructor Parameters

| Parameter | Default | Description |
|---|---|---|
| `valkey` | required | Valkey client instance |
| `name` | required | Lock key name |
| `timeout` | `None` | Max lock lifetime in seconds (no auto-expire if None) |
| `sleep` | `0.1` | Sleep between acquisition attempts (seconds) |
| `blocking` | `True` | Block until acquired (False = return False immediately) |
| `blocking_timeout` | `None` | Max time to wait for acquisition (None = forever) |
| `thread_local` | `True` | Store lock token in thread-local storage |

### Lock Methods

```python
lock = Lock(r, "my-resource", timeout=10)

# Acquire
acquired = lock.acquire()
acquired = lock.acquire(blocking=True, blocking_timeout=5)

# Extend timeout
lock.extend(additional_time=5)           # add 5 seconds
lock.extend(additional_time=5, replace=False)  # add to existing TTL
lock.extend(additional_time=5, replace=True)   # set absolute TTL

# Reacquire (renew)
lock.reacquire()  # reset TTL to original timeout

# Release
lock.release()

# Check ownership
lock.owned()  # True if current thread owns the lock

# Get lock details
lock.name     # lock key name
lock.token    # unique token for this lock acquisition
```

### Lock with Timeout

```python
# Lock expires after 10 seconds even if not released
lock = Lock(r, "my-resource", timeout=10)

# Try to acquire, wait up to 5 seconds
lock = Lock(r, "my-resource", timeout=10, blocking_timeout=5)
acquired = lock.acquire()  # False if not acquired within 5 seconds
```

### Non-blocking Lock

```python
lock = Lock(r, "my-resource", timeout=10, blocking=False)
if lock.acquire():
    try:
        pass
    finally:
        lock.release()
else:
    # Could not acquire — handle gracefully
    pass
```

### Thread Safety

```python
# thread_local=True (default) — token is per-thread
lock = Lock(r, "my-resource", timeout=10, thread_local=True)

# thread_local=False — token is shared across threads
# Use when passing lock between threads
lock = Lock(r, "my-resource", timeout=10, thread_local=False)
```

## Retry and Backoff

### Retry Object

```python
from valkey.retry import Retry
from valkey.backoff import ExponentialBackoff

retry = Retry(
    backoff=ExponentialBackoff(cap=0.5, base=0.01),
    retries=3,
    supported_errors=(valkey.ConnectionError, valkey.TimeoutError),
)

r = valkey.Valkey(
    host="localhost",
    port=6379,
    retry=retry,
    retry_on_error=[valkey.ResponseError],  # additional errors to retry on
)
```

### Backoff Strategies

```python
from valkey.backoff import (
    NoBackoff,
    ConstantBackoff,
    ExponentialBackoff,
    FullJitterBackoff,
    EqualJitterBackoff,
    DecorrelatedJitterBackoff,
    default_backoff,
)

# No delay between retries
backoff = NoBackoff()

# Fixed delay
backoff = ConstantBackoff(backoff=0.5)

# Exponential: base * 2^failures, capped at cap
backoff = ExponentialBackoff(cap=0.512, base=0.008)

# Full jitter: random(0, min(cap, base * 2^failures))
backoff = FullJitterBackoff(cap=0.512, base=0.008)

# Equal jitter: half + random(0, half)
backoff = EqualJitterBackoff(cap=0.512, base=0.008)

# Decorrelated jitter: AWS-style
backoff = DecorrelatedJitterBackoff(cap=0.512, base=0.008)

# Default (EqualJitterBackoff)
backoff = default_backoff()
```

### Simple Retry on Timeout

```python
# Shorthand — retries on TimeoutError with default backoff
r = valkey.Valkey(host="localhost", port=6379, retry_on_timeout=True)
```

## Client-Side Caching

Server-assisted client-side caching using RESP3 client tracking:

```python
r = valkey.Valkey(
    host="localhost",
    port=6379,
    protocol=3,
    cache_enabled=True,
    cache_max_size=10000,
    cache_ttl=0,           # 0 = no TTL (rely on server invalidation)
    cache_policy="lru",    # "lru", "lfu", "random"
)

# First call — hits server
value = r.get("key")

# Subsequent calls — served from cache
value = r.get("key")  # cache hit

# Cache invalidated when server value changes
r.set("key", "new_value")  # invalidates cache entry
```

### Custom Cache Backend

```python
from valkey._cache import AbstractCache, EvictionPolicy

class MyCache(AbstractCache):
    def __init__(self, max_size, ttl, policy):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def delete(self, key):
        self._store.pop(key, None)

    def flush(self):
        self._store.clear()

r = valkey.Valkey(
    host="localhost",
    port=6379,
    protocol=3,
    cache_enabled=True,
    client_cache=MyCache(10000, 0, EvictionPolicy.LRU),
)
```

### Cache Policy Lists

```python
# Commands excluded from caching (default deny list includes PTTL, TTL, DUMP, etc.)
r = valkey.Valkey(
    host="localhost",
    port=6379,
    protocol=3,
    cache_enabled=True,
    cache_deny_list=["PTTL", "TTL", "DUMP", "EXPIRETIME"],
    cache_allow_list=["GET", "EXISTS", "STRLEN"],
)
```

## Credential Providers

Dynamic credential resolution without hardcoding passwords:

```python
from valkey.credentials import CredentialProvider, UsernamePasswordCredentialProvider

# Static credentials
provider = UsernamePasswordCredentialProvider(username="default", password="secret")

r = valkey.Valkey(
    host="localhost",
    port=6379,
    credential_provider=provider,
)

# Custom provider (e.g., from environment, vault, IAM)
class VaultCredentialProvider(CredentialProvider):
    def get_credentials(self):
        # Fetch from HashiCorp Vault, AWS Secrets Manager, etc.
        username, password = fetch_from_vault()
        if username:
            return username, password
        return (password,)

r = valkey.Valkey(
    host="localhost",
    port=6379,
    credential_provider=VaultCredentialProvider(),
)
```

### Cannot Mix Credentials

```python
# ERROR — cannot use both password and credential_provider
r = valkey.Valkey(
    host="localhost",
    port=6379,
    password="secret",
    credential_provider=UsernamePasswordCredentialProvider(password="other"),
)
# Raises DataError
```

## OCSP Validation

Certificate revocation checking (requires `cryptography` package):

```python
r = valkey.Valkey(
    host="valkey.example.com",
    port=6379,
    ssl=True,
    ssl_validate_ocsp=True,
    ssl_ca_certs="/path/to/ca.pem",
)
```

## ACL Commands

```python
# List users
r.acl_list()

# Get user details
r.acl_getuser("default")

# Set user
r.acl_setuser("myuser", passwords=["+secret"], commands="+@all", keys="*")

# Delete user
r.acl_deluser("myuser")

# Generate password
r.acl_genpass()
r.acl_genpass(256)

# Load/Save ACL
r.acl_save()
r.acl_load()

# Check permissions
r.acl_dryrun("myuser", "GET", "key")

# Current user
r.acl_whoami()

# Categories
r.acl_cat()
r.acl_cat("string")
```

## Client Tracking (RESP3)

```python
# Enable client tracking for server-assisted caching
r.client_tracking_on()
r.client_tracking_off()

# Check tracking info
r.client_trackinginfo()

# Set client name
r.client_setname("my-app")
r.client_getname()

# Client ID
r.client_id()

# Pause clients
r.client_pause(1000)  # pause all clients for 1 second
r.client_pause(1000, all=False)  # pause only write clients

# Unpause
r.client_unpause()

# No-evict mode
r.client_no_evict("ON")
r.client_no_evict("OFF")

# No-touch mode (commands don't affect LRU/LFU)
r.client_no_touch("ON")
r.client_no_touch("OFF")
```

## Connection Info

```python
# Client list
r.client_list()
r.client_list(type="normal")

# Client info (self)
r.client_info()

# Get redirected client ID
r.client_getredir()

# Reply mode
r.client_reply("ON")
r.client_reply("OFF")
r.client_reply("SKIP")

# Set client info
r.client_setinfo("LIB-NAME", "my-lib")
r.client_setinfo("LIB-VER", "1.0.0")
```

## Gotchas

- **Lock timeout is max lifetime** — If the holder crashes, the lock expires after `timeout` seconds. Set it longer than the maximum expected critical section duration.
- **`Lock` is not reentrant** — The same thread cannot acquire the same lock twice. Use a different pattern for reentrant locking.
- **`thread_local=False` risks cross-thread release** — If thread A acquires and thread B releases, B might release A's lock. Only use when you control the thread handoff.
- **Client-side caching requires RESP3** — `protocol=3` is mandatory. Caching does not work with RESP2.
- **Cache invalidation is best-effort** — Server push notifications may be lost on connection drops. Combine with `cache_ttl` for safety.
- **`credential_provider` is called on each connect** — Implement caching in your provider if fetching credentials is expensive.
- **OCSP requires network access** — The client must reach the OCSP responder. Add timeouts to avoid blocking.
