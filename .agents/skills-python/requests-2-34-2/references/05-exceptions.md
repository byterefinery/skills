# requests 2.34.2 — Exception Hierarchy

```
BaseException
 └── Exception
      └── IOError
           └── RequestException              # Base for all requests exceptions
                ├── InvalidJSONError          # JSON-related error (base)
                │    └── JSONDecodeError      # Body not valid JSON
                ├── HTTPError                 # 4xx/5xx status (from raise_for_status)
                ├── ConnectionError           # Network-level failure
                │    ├── ProxyError           # Proxy connection failure
                │    └── SSLError             # TLS/SSL handshake or cert error
                ├── Timeout                   # Request timed out
                │    └── ConnectTimeout       # Timed out connecting (safe to retry)
                │         └── ReadTimeout     # Server didn't send data in time
                ├── URLRequired               # Missing URL
                ├── TooManyRedirects          # Exceeded max_redirects (default 30)
                ├── MissingSchema             # No http:// or https:// in URL
                ├── InvalidSchema             # Unsupported scheme (no adapter)
                ├── InvalidURL                # Malformed URL
                ├── InvalidHeader             # NUL bytes or invalid chars in header
                ├── InvalidProxyURL           # Malformed proxy URL (subclass of InvalidURL)
                ├── ChunkedEncodingError      # Server broke chunked transfer encoding
                ├── ContentDecodingError      # Failed to decode compressed response
                ├── StreamConsumedError       # Tried to read stream after consumption
                ├── RetryError                # Custom retry logic exhausted
                └── UnrewindableBodyError     # Could not rewind request body for retry
```

## Warnings

```
Warning
 └── RequestsWarning              # Base warning
      ├── FileModeWarning         # File opened in text mode (DeprecationWarning)
      └── RequestsDependencyWarning  # Dependency version mismatch
```

## When Each Exception Is Raised

### `RequestException`
Base class. Catch this to handle any requests error generically. Always has `.request` and `.response` attributes (may be `None`).

### `HTTPError`
Raised by `Response.raise_for_status()` on 4xx/5xx status codes. The `.response` attribute holds the full Response object for inspection.

```python
try:
    r.raise_for_status()
except requests.exceptions.HTTPError as e:
    print(e.response.status_code)  # e.g., 404
    print(e.response.text)         # error body
```

### `ConnectionError`
Catches DNS failures, refused connections, and broken pipes. This is the most common network error.

**Retryable:** Yes — transient network issues often resolve on retry.

### `ProxyError`
Specific proxy connection failure. Subclass of `ConnectionError`.

### `SSLError`
TLS handshake failures, certificate verification errors, or protocol mismatches. Subclass of `ConnectionError`.

Common causes:
- Expired or self-signed server certificate
- `verify=True` with no matching CA in certifi bundle
- Server requires TLS version not supported by urllib3/OpenSSL
- Client certificate rejected by server

### `Timeout`
Base timeout exception. Catch this to handle both connect and read timeouts.

**Retryable:** Yes — timeouts are typically transient.

### `ConnectTimeout`
Connection to the server timed out. Subclass of both `ConnectionError` and `Timeout`.

**Retryable:** Yes — explicitly safe to retry per requests documentation.

### `ReadTimeout`
Server connected but did not send data within the read timeout period. Subclass of `Timeout` only (not `ConnectionError`).

**Retryable:** Depends on idempotency. GET/HEAD are safe; POST may have side effects.

### `TooManyRedirects`
Exceeded `Session.max_redirects` (default 30). Often indicates a redirect loop.

Check `r.history` (accessible via exception `.response`) to inspect the redirect chain.

### `MissingSchema`
URL lacks `http://` or `https://` prefix.

```python
requests.get("example.com")  # MissingSchema
requests.get("https://example.com")  # OK
```

### `InvalidSchema`
URL scheme has no registered adapter. Occurs when using schemes like `ftp://`, `file://`, or custom protocols without mounting a custom `BaseAdapter`.

```python
requests.get("ftp://example.com/file")  # InvalidSchema
# Fix: mount a custom adapter for the scheme
```

### `InvalidURL`
Malformed URL — missing host, invalid IDNA encoding, or wildcard in hostname.

### `InvalidHeader`
Header value contains NUL bytes, non-printable characters, or other invalid content. Header names and values must be valid Latin-1 strings.

### `ChunkedEncodingError`
Server declared `Transfer-Encoding: chunked` but sent malformed chunks.

### `ContentDecodingError`
Failed to decompress response body (gzip, deflate, brotli corruption).

### `StreamConsumedError`
Tried to iterate a streaming response after its content was already consumed (e.g., accessed `.content` then called `.iter_content()`).

### `UnrewindableBodyError`
Request body is a non-seekable stream (pipe, socket) and requests needed to rewind it for a retry or redirect.

**Fix:** Use `io.BytesIO` wrapper or ensure the body is seekable.

### `RetryError`
Raised when custom `urllib3.Retry` logic exhausts all attempts.

## Retryability Guide

| Exception | Safe to Retry? | Notes |
|---|---|---|
| `ConnectTimeout` | ✅ Yes | Explicitly safe per docs |
| `ConnectionError` | ✅ Usually | DNS failures, refused connections are transient |
| `ReadTimeout` | ⚠️ Idempotent only | Safe for GET/HEAD; risky for POST with side effects |
| `ProxyError` | ✅ Usually | Proxy may be temporarily unavailable |
| `SSLError` | ⚠️ Sometimes | Retry if transient (clock skew, cert rotation); not if misconfigured |
| `ChunkedEncodingError` | ✅ Yes | Server-side glitch |
| `ContentDecodingError` | ❌ No | Response data is corrupted |
| `TooManyRedirects` | ❌ No | Indicates a logic error (redirect loop) |
| `HTTPError (5xx)` | ✅ With policy | Use `Retry.status_forcelist` for specific codes |
| `HTTPError (4xx)` | ❌ Usually | Client errors (401, 403, 404) won't resolve on retry |
| `UnrewindableBodyError` | ❌ No | Fix the body source to be seekable |

## Best Practices

```python
import requests
from requests.exceptions import (
    ConnectionError, Timeout, HTTPError, RequestException
)

def fetch(url, timeout=10):
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.JSONDecodeError:
        # Response was OK but body isn't JSON
        return None
    except HTTPError as e:
        # 4xx or 5xx
        if e.response.status_code == 429:
            # Rate limited — back off
            pass
        raise
    except (ConnectionError, Timeout):
        # Transient network error — safe to retry
        raise
    except RequestException as e:
        # Any other requests error
        raise
```
