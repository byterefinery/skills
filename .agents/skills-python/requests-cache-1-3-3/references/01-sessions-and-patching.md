# Sessions and Patching

## CachedSession

`CachedSession` is a drop-in replacement for `requests.Session`. It supports all standard session methods (`get`, `post`, `put`, `patch`, `delete`, `head`, `options`, `request`, `send`).

```python
from requests_cache import CachedSession

session = CachedSession('my_cache')
session.get('https://httpbin.org/get')
session.post('https://httpbin.org/post', json={'key': 'value'})
```

### Disabling Cache Temporarily

```python
with session.cache_disabled():
    session.get('https://httpbin.org/get')  # not cached
```

### Modifying Settings at Runtime

Session settings can be changed after initialization:

```python
session.settings.expire_after = 360
session.settings.stale_if_error = True
session.settings.read_only = True
```

Backend and serializer settings cannot be changed after initialization.

### Sharing a Backend Across Sessions

```python
from requests_cache import CachedSession, RedisCache

backend = RedisCache()
session1 = CachedSession(backend=backend, autoclose=False)
session2 = CachedSession(backend=backend, autoclose=False)
```

Set `autoclose=False` so closing one session does not disconnect the shared backend.

### Wrapping an Existing Session

```python
session = CachedSession.wrap(original_session, expire_after=3600)
```

This retains all original session settings (adapters, auth, cookies, headers, hooks, proxies, etc.).

## Patching

`install_cache()` globally patches `requests` so all `requests.get()`, `requests.post()`, etc. calls are transparently cached.

```python
import requests_cache
import requests

requests_cache.install_cache('my_cache', expire_after=3600)
requests.get('https://httpbin.org/get')  # cached
```

### Patching Controls

```python
# Temporarily enable caching
with requests_cache.enabled():
    requests.get('https://httpbin.org/get')  # cached

# Temporarily disable caching
with requests_cache.disabled():
    requests.get('https://httpbin.org/get')  # not cached

# Remove patching entirely
requests_cache.uninstall_cache()

# Check if patching is active
requests_cache.is_installed()

# Clear cache when using patching
requests_cache.clear()

# Delete expired when using patching
requests_cache.delete(expired=True)
```

### Context Managers

```python
# Scoped caching
requests_cache.install_cache('my_cache')
with requests_cache.disabled():
    requests.get('https://httpbin.org/get')  # not cached
# Caching resumes after the block
```

### Patching Limitations

Avoid `install_cache()` in these scenarios:
- Other libraries that patch `requests.Session`
- Multi-threaded or multiprocess applications
- Libraries that will be imported by other applications
- Large applications with requests in many modules (unclear what is cached)

Use `CachedSession` instead in these cases.

## CacheMixin

For combining requests-cache with other Session-modifying libraries:

```python
from requests import Session
from requests_cache import CacheMixin
from some_other_lib import SomeOtherMixin

class CustomSession(CacheMixin, SomeOtherMixin, Session):
    pass
```

Use keyword arguments instead of positional arguments with mixins — argument order changes based on inheritance.
