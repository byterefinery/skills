# Backends

## Available Backends

| Backend | Class | Alias | Dependencies |
|---|---|---|---|
| SQLite | `SQLiteCache` | `'sqlite'` | None (default) |
| Filesystem | `FileCache` | `'filesystem'` | None |
| Memory | `BaseCache` | `'memory'` | None |
| Redis | `RedisCache` | `'redis'` | `redis` |
| MongoDB | `MongoCache` | `'mongodb'` | `pymongo` |
| GridFS | `GridFSCache` | `'gridfs'` | `pymongo` |
| DynamoDB | `DynamoDbCache` | `'dynamodb'` | `boto3`, `botocore` |

Install with extras: `pip install requests-cache[redis]`, `requests-cache[mongodb]`, `requests-cache[dynamodb]`, or `requests-cache[all]`.

## Choosing a Backend

Start with SQLite. Switch when you have a specific reason:
- **Distributed across machines** without shared filesystem → Redis, MongoDB, DynamoDB
- **High concurrent writes** (many nodes/threads caching different URLs) → Redis, MongoDB
- **Slow file storage** (magnetic drives, high-latency NFS) → Redis, MongoDB
- **Little or no local storage** (some cloud services) → Redis, MongoDB, DynamoDB
- **Reuse cached data outside requests-cache** → filesystem (JSON), MongoDB, Redis
- **Already using a backend** → use it directly

All backends perform well up to ~700-1000 requests/second.

## Specifying a Backend

By name:
```python
session = CachedSession('my_cache', backend='redis')
```

By instance (for additional options):
```python
from requests_cache import CachedSession, RedisCache

backend = RedisCache(host='192.168.1.63', port=6379)
session = CachedSession('my_cache', backend=backend)
```

## Backend-Specific Use of cache_name

| Backend | cache_name used as |
|---|---|
| SQLite | Database path |
| Redis | Hash namespace |
| MongoDB, GridFS | Database name |
| DynamoDB | Table name |
| Filesystem | Cache directory |

Each backend class accepts optional parameters for the underlying connection (e.g., `SQLiteCache` accepts `sqlite3.connect` parameters).

## File-Based Backend Paths

### Relative and Absolute Paths
```python
session = CachedSession('http_cache', backend='sqlite')
print(session.cache.db_path)  # '<cwd>/http_cache.sqlite'

session = CachedSession('~/.myapp/http_cache', backend='sqlite')
print(session.cache.db_path)  # '/home/user/.myapp/http_cache.sqlite'
```

### System Directories
```python
# Use system temp directory
session = CachedSession('http_cache', backend='sqlite', use_temp=True)

# Use system cache directory
session = CachedSession('http_cache', backend='filesystem', use_cache_dir=True)
```

These resolve to platform-specific locations (`/tmp/` on Linux, `~/Library/Caches/` on macOS, `AppData\Local\` on Windows).

## Migrating Between Backends

```python
src_session = CachedSession('my_cache', backend='redis')
dest_session = CachedSession('~/cache_dump', backend='filesystem', serializer='json')
dest_session.cache.update(src_session.cache)
```

Or using backend classes directly:
```python
from requests_cache import RedisCache, FileCache

src_cache = RedisCache()
dest_cache = FileCache('~/cache_dump', serializer='json')
dest_cache.update(src_cache)
```

## Custom Backends

Subclass `BaseCache` and `BaseStorage`:

```python
from requests_cache import CachedSession
from requests_cache.backends import BaseCache, BaseStorage

class CustomStorage(BaseStorage):
    def __getitem__(self, key): pass
    def __setitem__(self, key, value): pass
    def __delitem__(self, key): pass
    def __iter__(self): pass
    def __len__(self): pass
    def clear(self): pass

class CustomCache(BaseCache):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.redirects = CustomStorage(**kwargs)
        self.responses = CustomStorage(**kwargs)

session = CachedSession(backend=CustomCache())
```
