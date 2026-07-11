---
name: requests-cache-1-3-3
description: Persistent HTTP cache for Python requests. Use when caching HTTP responses with the requests library, reducing API call latency, implementing offline modes, or managing cached responses with expiration policies, backends (SQLite, Redis, MongoDB, DynamoDB, filesystem), and fine-grained filtering.
---

# requests-cache 1.3.3

## Overview

requests-cache is a persistent HTTP cache for the Python `requests` library. It provides two usage patterns: `CachedSession` (drop-in replacement for `requests.Session`) and `install_cache()` (global monkey-patching). Cached responses are stored with configurable expiration, support conditional revalidation via ETags/Last-Modified, and work with multiple backends (SQLite default, Redis, MongoDB, DynamoDB, filesystem, memory).

Install with `pip install requests-cache`. For all backends: `pip install requests-cache[all]`. Requires Python 3.8+.

## Usage

**CachedSession** (recommended):
```python
from requests_cache import CachedSession

session = CachedSession('my_cache', expire_after=3600)
session.get('https://api.example.com/data')  # cached on subsequent calls
```

**Global patching**:
```python
import requests_cache
requests_cache.install_cache('my_cache', expire_after=3600)
import requests
requests.get('https://api.example.com/data')  # transparently cached
```

**Key parameters for `CachedSession`**:
- `cache_name` — cache path/name (default: `http_cache`)
- `backend` — `'sqlite'` (default), `'redis'`, `'mongodb'`, `'dynamodb'`, `'filesystem'`, `'memory'`
- `expire_after` — seconds, `timedelta`, `datetime`, or `NEVER_EXPIRE` / `DO_NOT_CACHE`
- `urls_expire_after` — dict of URL glob/regex patterns to expiration values
- `cache_control` — use server `Cache-Control` headers for expiration (opt-in)
- `allowable_methods` — HTTP methods to cache (default: `('GET', 'HEAD')`)
- `allowable_codes` — status codes to cache (default: `(200,)`)
- `stale_if_error` — return stale cache on request errors (bool or max staleness)
- `stale_while_revalidate` — return stale response while async refresh runs
- `ignored_parameters` — params/headers to exclude from cache keys and redact (auth headers/params ignored by default)
- `match_headers` — headers to include in cache key matching
- `serializer` — `'pickle'` (default), `'json'`, `'yaml'`, `'bson'`
- `read_only` — read existing cache without writing new entries
- `filter_fn` — custom `Callable[[Response], bool]` to decide what to cache
- `key_fn` — custom cache key function for advanced matching

**Per-request options** (on `session.get()`, `session.request()`, etc.):
- `expire_after` — override session expiration for this request
- `only_if_cached` — offline mode; returns 504 if not cached
- `refresh` — revalidate with server (soft refresh, like F5)
- `force_refresh` — always make a new request (hard refresh, like Ctrl+F5)

**Response attributes** (added to all responses):
- `from_cache` — whether response came from cache
- `is_expired` — whether cached response has expired
- `cache_key` — unique identifier used for matching
- `created_at` / `expires` — timestamps

**Cache management**:
```python
session.cache.clear()           # delete all
session.cache.delete(expired=True)  # delete expired
session.cache.delete(urls=['https://example.com/api'])  # delete by URL
session.cache.urls()            # list cached URLs
session.cache.contains(url='...')  # check if cached
session.cache.reset_expiration(timedelta(days=7))  # reset all expirations
```

## Gotchas

- **Expiration is not retroactive** — changing `expire_after` only affects new responses. Use `session.cache.reset_expiration()` to apply to existing entries.
- **Patching limitations** — `install_cache()` is unsafe in multi-threaded/multiprocess apps, in libraries imported by others, or when other libraries also patch `requests.Session`. Use `CachedSession` instead.
- **Pickle security** — the default `pickle` serializer can execute arbitrary code on deserialization. Use `safe_pickle_serializer(secret_key=...)` for untrusted data, or switch to `json`/`yaml`/`bson` serializers.
- **Auth-gated content** — if caching authenticated requests for multiple users, ensure the auth header/param is part of the cache key (via `match_headers` or by removing from `ignored_parameters`), or use separate caches per user. Otherwise one user may receive another user's cached response.
- **`ignored_parameters` replaces defaults** — setting `ignored_parameters=['foo']` drops the default auth header/param exclusions. Use `list(DEFAULT_IGNORED_PARAMS) + ['foo']` to append.
- **`Vary` header respected by default** — requests-cache automatically matches on `Vary`-specified headers. Use `match_headers` only when the server omits `Vary` but response content still varies by header.
- **Custom `key_fn` invalidates existing cache** — switching cache key functions makes previously cached responses unreachable. Clear the cache or run `session.cache.recreate_keys()`.
- **SQLite is thread/process-safe** — the default SQLite backend handles concurrent access. Use Redis/MongoDB for distributed multi-node caching.
- **`CachedSession` cannot be pickled** — it holds live backend connections. Use `session.close()` and recreate, or share a backend instance with `autoclose=False`.
- **Compression libraries affect cache keys** — presence/absence of `zstandard`, `brotli`, etc. changes the `Accept-Encoding` header, which changes cache keys. A cache built with one environment may have different hit rates in another.
- **`stale_if_error` also catches Python exceptions** — not just HTTP error codes. A `requests.RequestException` (timeout, connection error) will also fall back to stale cache data.

## References

- [01-sessions-and-patching](references/01-sessions-and-patching.md) — CachedSession, install_cache, patching controls
- [02-backends](references/02-backends.md) — Backend types, selection criteria, migration
- [03-expiration](references/03-expiration.md) — Expiration strategies, URL patterns, error handling
- [04-filtering-and-matching](references/04-filtering-and-matching.md) — Method/code/URL filtering, request matching, cache keys
- [05-advanced](references/05-advanced.md) — Serializers, security, compatibility with other libraries
