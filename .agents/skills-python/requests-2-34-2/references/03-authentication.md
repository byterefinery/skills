# requests 2.34.2 — Authentication

## Built-In Auth Handlers

### HTTP Basic Auth

```python
from requests.auth import HTTPBasicAuth

# Tuple shorthand
requests.get(url, auth=("username", "password"))

# Explicit object (reusable)
auth = HTTPBasicAuth("username", "password")
requests.get(url, auth=auth)
session.auth = auth  # applies to all session requests
```

Sends `Authorization: Basic <base64(username:password)>` header. Credentials are Latin-1 encoded per RFC 7617.

**Security note:** Basic auth transmits credentials in base64 (trivially decodable). Always use HTTPS.

### HTTP Digest Auth

```python
from requests.auth import HTTPDigestAuth

auth = HTTPDigestAuth("username", "password")
requests.get(url, auth=auth)
```

Implements RFC 2617 digest authentication. Handles `WWW-Authenticate` challenge-response flow automatically, including `qop` (quality of protection) negotiation.

### Proxy Auth

```python
from requests.auth import HTTPProxyAuth

# In proxies dict (credentials in URL)
proxies = {"https": "http://user:pass@proxy:3128/"}

# Or as separate auth object
proxy_auth = HTTPProxyAuth("user", "pass")
# Note: urllib3 handles proxy auth from the URL; HTTPProxyAuth is for direct use
```

## Custom Auth

Subclass `AuthBase` and implement `__call__(request)` → `PreparedRequest`:

```python
from requests.auth import AuthBase

class BearerAuth(AuthBase):
    """Attaches Bearer Token Authentication to the given Request."""

    def __init__(self, token: str):
        self.token = token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r

# Usage
auth = BearerAuth("my-token-123")
requests.get(url, auth=auth)
```

The `__call__` method receives a `PreparedRequest` and must return it (modified or unchanged). This is called during `PreparedRequest.prepare_auth()`.

### OAuth Example Pattern

```python
class OAuth1Auth(AuthBase):
    def __init__(self, consumer_key, consumer_secret, token=None, token_secret=None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token = token
        self.token_secret = token_secret

    def __call__(self, r):
        # Compute OAuth signature and add to header or query params
        sig = compute_signature(r, self.consumer_key, ...)
        r.headers["Authorization"] = f"OAuth oauth_consumer_key=\"...\", ..."
        return r
```

## Auth and Redirects

When a request is redirected:

1. **Same host, same scheme:** Auth headers are preserved
2. **Same host, http→https (standard ports 80→443):** Auth preserved (backwards compatibility)
3. **Different host:** `Authorization` header is stripped to prevent credential leakage
4. **Different port or scheme (non-standard):** Auth stripped

The `Session.rebuild_auth()` method handles this logic. New `.netrc` credentials are applied if the target host has entries and `trust_env=True`.

## .netrc Integration

When `Session.trust_env=True`, requests checks the user's `.netrc` file (`~/.netrc` or `~/_netrc`) for credentials matching the request host:

```
# ~/.netrc
machine api.example.com
login myuser
password mypass
```

If a match is found and no explicit `auth` parameter is provided, basic auth is automatically applied.

## Session-Level Auth

Setting `session.auth` applies authentication to every request in that session:

```python
s = requests.Session()
s.auth = HTTPBasicAuth("user", "pass")

# All requests include Basic Auth
s.get("https://api.example.com/users")
s.post("https://api.example.com/users", json={"name": "Alice"})

# Override per-request
s.get("https://api.example.com/public", auth=None)  # no auth
```

Per-request `auth` overrides session-level `auth`. Pass `auth=None` explicitly to clear it for a specific request.
