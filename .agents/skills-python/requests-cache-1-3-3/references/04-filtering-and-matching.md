# Filtering and Matching

## HTTP Method Filtering

Default: only `GET` and `HEAD` are cached.

```python
session = CachedSession(allowable_methods=('GET', 'POST'))
session.post('https://httpbin.org/post', json={'key': 'value'})  # cached
```

Method override headers are respected:
```python
session = CachedSession(allowable_methods=('GET',))
session.post('https://httpbin.org/post', headers={'X-HTTP-Method-Override': 'GET'})  # cached as GET
```

## Status Code Filtering

Default: only `200` responses are cached.

```python
session = CachedSession(allowable_codes=(200, 400, 404))
```

## URL Filtering

Use `urls_expire_after` with `DO_NOT_CACHE` as a catch-all to create an allowlist. See [03-expiration](03-expiration.md) for details.

## Custom Filter Function

```python
from sys import getsizeof
from requests_cache import CachedSession

def filter_by_size(response) -> bool:
    """Don't cache responses with a body over 1 MB"""
    return getsizeof(response.content) <= 1024 * 1024

session = CachedSession(filter_fn=filter_by_size)
```

`filter_fn` is applied on both read and write, in addition to other filtering options.

## Read-Only Mode

Read existing cache without writing new entries:

```python
session = CachedSession(read_only=True)
# Or: session.settings.read_only = True
```

## Parameter Ignoring

Exclude parameters from cache keys and redact from cached data:

```python
session = CachedSession(ignored_parameters=['auth-token'])

session.get('https://httpbin.org/get', params={'auth-token': 'ABC123'})
r = session.get('https://httpbin.org/get', params={'auth-token': 'XYZ789'})
assert r.from_cache is True  # same cache key, different token values ignored
```

Applies to query params, JSON body params, and headers (when `match_headers=True`).

**Default ignored params**: `Authorization`, `Proxy-Authorization`, `X-API-Key`, `X-Auth-Token`, `X-API-Token`, `X-Access-Token`, `access_token`, `api_key`, `apikey`.

To append to defaults:
```python
from requests_cache import CachedSession, DEFAULT_IGNORED_PARAMS

ignored = list(DEFAULT_IGNORED_PARAMS) + ['X-Custom-Credential']
session = CachedSession(ignored_parameters=ignored)
```

## Header Matching

By default, `Vary` response headers are respected automatically. Use `match_headers` when `Vary` is not available:

```python
# Match specific headers
session = CachedSession(match_headers=['Accept-Language'])

# Match all headers
session = CachedSession(match_headers=True)
```

## Custom Cache Keys

```python
from requests import PreparedRequest
from requests_cache import CachedSession, create_key

def custom_key(request: PreparedRequest, **kwargs) -> str:
    request = request.copy()
    # Normalize or remove headers/params as needed
    if 'gzip' in request.headers.get('Accept-Encoding', ''):
        request.headers['Accept-Encoding'] = 'gzip'
    return create_key(request, **kwargs)

session = CachedSession(key_fn=custom_key)
```

After changing `key_fn` on a non-empty cache, run `session.cache.recreate_keys()` to rebuild keys, or clear the cache first.

## Cache Inspection

```python
# Check if URL is cached
session.cache.contains(url='https://httpbin.org/get')

# Check with full request object
from requests import Request
request = Request('GET', 'https://httpbin.org/get', params={'k': 'v'})
session.cache.contains(request=request)

# Check by cache key
session.cache.contains('d1e666e9fdfb3f86')

# List all cached URLs
session.cache.urls()

# Filter responses
for response in session.cache.filter(expired=False):
    print(response)

# Access raw cache (dict-like)
for key, response in session.cache.responses.items():
    print(key, response.url, response.request.method)
```

## Deleting Responses

```python
session.cache.clear()  # all
session.cache.delete(expired=True)  # expired only
session.cache.delete(older_than=timedelta(days=7))  # older than
session.cache.delete(urls=['https://httpbin.org/json'])  # by URL
session.cache.delete(requests=[request_1, request_2])  # by Request objects
session.cache.delete('e25f7e6326966e82')  # by cache key
```
