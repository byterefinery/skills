# Expiration

## Expiration Precedence

When multiple expiration values apply, this order is used (highest priority first):

1. `Cache-Control` response headers (if `cache_control=True`)
2. `Cache-Control` request headers
3. Per-request `expire_after` (e.g., `session.get(url, expire_after=60)`)
4. Per-URL pattern from `urls_expire_after`
5. Per-session `expire_after` (default)

## Expiration Values

`expire_after` accepts:
- Positive number (seconds)
- `datetime.timedelta`
- `datetime.datetime`
- `NEVER_EXPIRE` — store indefinitely (default)
- `DO_NOT_CACHE` — skip reading and writing cache
- `EXPIRE_IMMEDIATELY` — cache but consider already expired (enables conditional revalidation)

```python
from datetime import timedelta
from requests_cache import CachedSession, DO_NOT_CACHE, NEVER_EXPIRE, EXPIRE_IMMEDIATELY

session = CachedSession(expire_after=60)
session = CachedSession(expire_after=timedelta(days=30))
session = CachedSession(expire_after=NEVER_EXPIRE)
session = CachedSession(expire_after=DO_NOT_CACHE)  # effectively disables caching
```

## URL Patterns

```python
import re
from requests_cache import NEVER_EXPIRE, DO_NOT_CACHE, CachedSession

urls_expire_after = {
    '*.site_1.com': 30,
    'site_2.com/resource_1': 60 * 2,
    'site_2.com/resource_*': 60 * 60,
    'site_2.com/static': NEVER_EXPIRE,
    re.compile(r'site_2.com/resource_\d'): 60 * 60 * 24 * 7,
}
session = CachedSession(urls_expire_after=urls_expire_after)
```

- Glob patterns match base URLs without protocol (`site.com/resource/` matches `http*://site.com/resource/**`)
- Regex patterns match the full URL (can restrict protocol)
- First match wins (order matters)
- Unmatched URLs fall back to session-level `expire_after`

## URL Allowlisting

Use `DO_NOT_CACHE` for non-matching URLs to create an allowlist:

```python
from requests_cache import DO_NOT_CACHE, NEVER_EXPIRE, CachedSession

urls_expire_after = {
    '*.site_1.com': 30,
    'site_2.com/static': NEVER_EXPIRE,
    '*': DO_NOT_CACHE,  # everything else is not cached
}
session = CachedSession(urls_expire_after=urls_expire_after)
```

## Stale-if-Error

Return expired cache data when a new request fails:

```python
from datetime import timedelta
from requests_cache import CachedSession

session = CachedSession(stale_if_error=True)
# Or with max staleness:
session = CachedSession(stale_if_error=timedelta(minutes=5))
```

Applies to both HTTP error codes (4xx, 5xx) and Python exceptions (timeouts, connection errors).

## Stale-While-Revalidate

Return stale response immediately while an async background request refreshes it:

```python
from datetime import timedelta
from requests_cache import CachedSession

session = CachedSession(stale_while_revalidate=True)
# Or with max staleness:
session = CachedSession(stale_while_revalidate=timedelta(minutes=5))
```

## Conditional Requests (Revalidation)

Automatically sent for servers that support ETags or Last-Modified. After a cached response expires, it is only updated if the remote content has changed.

```python
session = CachedSession(expire_after=1)
session.get(url)
time.sleep(1)
response = session.get(url)
print(response.from_cache)  # True if content unchanged (304 Not Modified)
```

## Per-Request Options

```python
# Override expiration for a single request
session.get(url, expire_after=60)

# Soft refresh (revalidate with server)
session.get(url, refresh=True)

# Hard refresh (always make new request, overwrite cache)
session.get(url, force_refresh=True)

# Offline mode (504 if not cached)
session.get(url, only_if_cached=True)

# Always revalidate (only for responses with validators)
session = CachedSession(always_revalidate=True)
```

## Resetting Expiration

Changing session settings does not apply retroactively. Options:

```python
# Reset all responses to expire in 30 days
session.cache.reset_expiration(timedelta(days=30))

# Delete expired responses
session.cache.delete(expired=True)

# Delete responses older than 7 days
session.cache.delete(older_than=timedelta(days=7))

# Clear entire cache
session.cache.clear()
```

## Automatic Removal

Redis, MongoDB, and DynamoDB backends support native TTL for automatic expiration. SQLite and filesystem backends remove expired entries lazily (on next access).
