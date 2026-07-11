# Advanced Features

## Serializers

### Built-in Serializers

| Serializer | Alias | Notes |
|---|---|---|
| Pickle | `'pickle'` | Default, fastest, binary |
| JSON | `'json'` | Human-readable, slightly slower |
| YAML | `'yaml'` | Human-readable, requires `pyyaml` |
| BSON | `'bson'` | Used by MongoDB, requires `pymongo` |

```python
session = CachedSession('my_cache', serializer='json')
```

JSON supports alternative libraries:
```python
from requests_cache import CachedSession, json_serializer, ujson_serializer, orjson_serializer

session = CachedSession(serializer=ujson_serializer)  # requires ujson
session = CachedSession(serializer=orjson_serializer)  # requires orjson
```

### Content Decoding

By default, JSON/text responses are decoded for human readability. Binary content is saved as-is. To save all content as binary:

```python
from requests_cache import FileCache, CachedSession

backend = FileCache(decode_content=False)
session = CachedSession('http_cache', backend=backend)
```

### Serializer Pipelines

Compose multiple serialization/compression steps:

```python
import gzip
from requests_cache import CachedSession, SerializerPipeline, Stage, pickle_serializer

compressed_serializer = SerializerPipeline([
    pickle_serializer,
    Stage(dumps=gzip.compress, loads=gzip.decompress),
], is_binary=True)

session = CachedSession(serializer=compressed_serializer)
```

### Compressed JSON Pipeline

```python
import json, gzip
from requests_cache import CachedSession, SerializerPipeline, Stage, json_serializer, utf8_encoder

comp_json = SerializerPipeline([
    json_serializer,
    utf8_encoder,
    Stage(dumps=gzip.compress, loads=gzip.decompress),
])
session = CachedSession(serializer=comp_json)
```

### Custom Serializers

Any module/object with `dumps` and `loads` functions:

```python
import custom_pickle
from requests_cache import CachedSession

session = CachedSession(serializer=custom_pickle)
```

## Security

### Safe Pickling

Use `itsdangerous` to sign serialized data with a secret key. Tampered data raises `BadSignature`:

```bash
pip install itsdangerous
```

```python
import os
from requests_cache import CachedSession, safe_pickle_serializer

secret_key = os.environ['SECRET_KEY']
serializer = safe_pickle_serializer(secret_key=secret_key)
session = CachedSession(serializer=serializer)
```

### Sensitive Data

Use `ignored_parameters` to prevent credentials from being cached. Auth headers and common auth params are ignored by default. See [04-filtering-and-matching](04-filtering-and-matching.md) for details.

### Auth-Gated Content

For multi-user scenarios, either:
- Use a separate cache per user
- Exclude authenticated requests via filtering
- Include auth headers in cache keys: `match_headers=['Authorization']`, `ignored_parameters=[]`

## Compatibility

### requests-html

```python
from requests_cache import CacheMixin
from requests_html import HTMLSession

class CachedHTMLSession(CacheMixin, HTMLSession):
    pass

session = CachedHTMLSession()
response = session.get('https://github.com/')
print(response.html.links)
```

### requests-futures

```python
from requests_cache import CachedSession
from requests_futures.sessions import FuturesSession

session = FuturesSession(session=CachedSession())
```

`FuturesSession` must wrap `CachedSession`, not the other way around.

### requests-oauthlib

```python
from requests_cache import CacheMixin
from requests_oauthlib import OAuth2Session

class CachedOAuth2Session(CacheMixin, OAuth2Session):
    pass

session = CachedOAuth2Session('my_client_id')
```

### requests-ratelimiter

Inheritance order matters — caching before rate-limiting means cache hits don't count against the limit:

```python
from requests import Session
from requests_cache import CacheMixin
from requests_ratelimiter import LimiterMixin

class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass

session = CachedLimiterSession(
    cache_name='http_cache',
    per_second=5,
)
```

### requests-mock

Disable requests-cache in tests:

```python
import unittest
import pytest
import requests

@pytest.fixture(scope='function', autouse=True)
def disable_requests_cache():
    with unittest.mock.patch('requests_cache.CachedSession', requests.Session):
        yield
```

Or attach the mock adapter to `CachedSession`:

```python
import requests_mock
from requests_cache import CachedSession

session = CachedSession()
adapter = requests_mock.Adapter()
session.mount('http://', adapter)
session.mount('https://', adapter)
```

### VCR Export

Convert cache to VCR-compatible format for unit tests:

```python
from requests_cache import CachedSession

session = CachedSession('my_cache')
session.cache.responses  # access cached responses for export
```

See the `examples/vcr.py` file in the repository for a complete conversion script.

## Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level='DEBUG')
# Or only requests-cache:
logging.getLogger('requests_cache').setLevel('DEBUG')
```

With rich formatting:
```python
import logging
from rich.logging import RichHandler

logging.basicConfig(
    level='DEBUG', format="%(message)s", datefmt="[%X]",
    handlers=[RichHandler()]
)
```

## Common Errors

- **`Unable to deserialize response with key {key}`** — cache format incompatible with current version. Delete invalid responses or clear the cache.
- **`database is locked`** — concurrency issue with SQLite. File a bug report.
- **`ResourceWarning: unclosed <ssl.SSLSocket>`** — safe to ignore; normal `requests.Session` connection pooling behavior.
- **`ModuleNotFoundError: No module named 'requests_cache.core'`** — module removed in v0.8. Import from `requests_cache` instead.
