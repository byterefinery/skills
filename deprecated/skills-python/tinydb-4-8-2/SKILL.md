---
name: tinydb-4-8-2
description: >
  TinyDB 4.8.2 — lightweight, zero-dependency document-oriented database for Python. Use this skill
  whenever the user mentions TinyDB, JSON-based local databases, document stores without external
  servers, lightweight Python databases, or small-app data persistence. Covers querying with
  ComparisonQuery, multi-table support, custom storages, middlewares (CachingMiddleware), and
  update operations (increment, decrement, add, delete field). Pure Python, no dependencies.
metadata:
  tags:
    - database
    - nosql
    - python
    - json
---

# tinydb 4.8.2

TinyDB is a tiny, document-oriented database written in pure Python with no external dependencies. It stores data as JSON (by default) and provides a MongoDB-like query API. Targeted at small apps where SQL or an external database server would be overkill.

## Overview

### Core Concepts

- **Documents** — Python `dict` instances stored in tables. Each document gets an auto-incrementing integer `_id` (accessible via `Document.doc_id`).
- **Tables** — Named collections of documents. The default table is `'_default'`. Access via `db.table('name')` or directly on `db` for the default table.
- **Queries** — Built with the `Query` class or `where()` shorthand. Combined with `&` (AND), `|` (OR), `~` (NOT).
- **Storages** — Pluggable persistence layer. `JSONStorage` (file-based JSON) is default. `MemoryStorage` for in-memory use. Custom storages implement `read()`/`write()`/`close()`.
- **Middlewares** — Wrap storages to add behavior. `CachingMiddleware` batches writes and caches reads.

### Data Storage Model

All tables and documents are stored in a single nested dict:

```python
{
    '_default': {1: {'name': 'Alice'}, 2: {'name': 'Bob'}},
    'users': {1: {'email': 'a@b.com'}},
}
```

Document IDs are integers in memory but serialized as strings in JSON storage.

### Installation

```bash
pip install tinydb==4.8.2
```

No dependencies — pure Python, works on Python 3.8+ and PyPy3.

## Usage

### Basic CRUD

```python
from tinydb import TinyDB, where

# Open (or create) a JSON database file
db = TinyDB('data.json')

# Insert — returns document ID
doc_id = db.insert({'name': 'Alice', 'age': 30})
# doc_id == 1

# Insert multiple — returns list of IDs
ids = db.insert_multiple([
    {'name': 'Bob', 'age': 25},
    {'name': 'Charlie', 'age': 35},
])

# Search — returns list of matching documents
results = db.search(where('name') == 'Alice')

# Get one document by query or by ID
doc = db.get(where('age') > 28)
doc = db.get(doc_id=1)

# Update matching documents — returns list of updated IDs
updated_ids = db.update({'age': 31}, where('name') == 'Alice')

# Remove matching documents — returns list of removed IDs
removed_ids = db.remove(where('name') == 'Bob')

# Truncate (remove all documents in a table)
db.truncate()

# Count matching documents
count = db.count(where('age') >= 30)

# Check existence
exists = db.contains(where('name') == 'Alice')
exists = db.contains(doc_id=1)

# Close the database (flushes file handles)
db.close()
```

### Context Manager

Use `with` to ensure `close()` is called:

```python
with TinyDB('data.json') as db:
    db.insert({'key': 'value'})
# db.close() called automatically
```

### Tables

```python
# Access named tables
users = db.table('users')
posts = db.table('posts')

users.insert({'name': 'Alice'})
posts.insert({'title': 'Hello', 'author_id': 1})

# List all table names
all_tables = db.tables()  # {'_default', 'users', 'posts'}

# Drop a specific table
db.drop_table('posts')

# Drop all tables
db.drop_tables()

# Table methods mirror db methods (search, insert, update, etc.)
users.search(where('name') == 'Alice')
```

### Query Language

```python
from tinydb import TinyDB, Query, where

db = TinyDB('data.json')
User = Query()  # ORM-style query object

# Comparison operators
db.search(User.age == 30)
db.search(User.age != 30)
db.search(User.age > 25)
db.search(User.age >= 25)
db.search(User.age < 35)
db.search(User.age <= 35)

# Field existence
db.search(User.email.exists())

# Nested field access (dot notation)
db.search(User.address.city == 'London')

# Bracket notation for keys with special characters
db.search(User['log-in'] == True)

# Regex matching — whole string must match
db.search(User.name.matches(r'^A.*'))

# Regex search — substring match
db.search(User.name.search(r'li'))

# Custom test function
db.search(User.age.test(lambda x: x % 2 == 0))

# Custom test with extra arguments
def in_range(value, low, high):
    return low <= value <= high

db.search(User.score.test(in_range, 50, 100))

# Value in a list
db.search(User.status.one_of(['active', 'pending']))

# Any element in a list matches a sub-query
db.search(User.tags.any(Query() == 'python'))

# All elements in a list match a sub-query
db.search(User.tags.all(Query().test(lambda x: len(x) > 2)))

# Map — transform field before comparison
db.search(User.age.map(lambda x: x * 2) == 60)

# Map — transform entire document, then access new keys
rekey = lambda x: {'y': x['a'], 'z': x['b']}
db.search(Query().map(rekey).z == 10)

# Fragment on nested fields
db.search(Query().doc.fragment({'a': 4, 'b': True}))

# Fragment — match multiple fields at once (no path needed)
db.search(Query().fragment({'name': 'Alice', 'age': 30}))

# No-op — always True, useful for building queries dynamically
base = Query().noop()
if name:
    base = base & (User.name == name)
if age:
    base = base & (User.age == age)
db.search(base)
```

### Combining Queries

```python
# AND
db.search((User.name == 'Alice') & (User.age > 25))

# OR
db.search((User.name == 'Alice') | (User.name == 'Bob'))

# NOT
db.search(~(User.status == 'inactive'))

# Complex combinations
db.search(
    (User.age >= 18) &
    ((User.status == 'active') | (User.status == 'pending')) &
    ~(User.banned.exists())
)
```

### Update Operations

TinyDB provides functional update helpers from `tinydb.operations`:

```python
from tinydb import TinyDB, where
from tinydb.operations import delete, add, subtract, set, increment, decrement

db = TinyDB('data.json')

# Delete a field
db.update(delete('temp_field'), where('id') == 1)

# Add/subtract from a numeric field
db.update(add('score', 10), where('name') == 'Alice')
db.update(subtract('score', 5), where('name') == 'Alice')

# Set a field value (same as passing a dict)
db.update(set('status', 'active'), where('name') == 'Alice')

# Increment/decrement by 1
db.update(increment('views'), where('id') == 1)
db.update(decrement('stock'), where('id') == 1)

# Custom update function
db.update(lambda doc: doc.update({'processed': True}), where('done') == False)
```

### Upsert

Update if exists, insert otherwise:

```python
from tinydb import TinyDB, where

db = TinyDB('data.json')

# Upsert by query condition
db.upsert({'name': 'Alice', 'score': 100}, where('name') == 'Alice')

# Upsert by specifying a Document with explicit doc_id
from tinydb.table import Document
db.upsert(Document({'name': 'Bob', 'score': 50}, doc_id=42))
```

### In-Memory Database

```python
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

db = TinyDB(storage=MemoryStorage)
db.insert({'key': 'value'})
# All data lives in memory, lost when db is discarded
```

### Caching Middleware

Batch writes and cache reads for better performance:

```python
from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

db = TinyDB('data.json', storage=CachingMiddleware(JSONStorage))

# Writes are cached in memory and flushed every 1000 operations
for i in range(500):
    db.insert({'index': i})

# Force flush
db.storage.flush()

# Or close — auto-flushes on close
db.close()
```

### Lambda Queries

Any callable accepting a document dict and returning bool works as a query. Mark non-cacheable to skip the cache:

```python
def my_query(doc):
    return doc.get('foo') == 'bar'

my_query.is_cacheable = lambda: False
db.search(my_query)  # never cached
```

### Custom Storage

Implement `read()`, `write()`, and optionally `close()`:

```python
from tinydb import TinyDB, Storage
from typing import Dict, Any, Optional

class EncryptedStorage(Storage):
    def __init__(self, path: str, key: bytes):
        self.path = path
        self.key = key

    def read(self) -> Optional[Dict[str, Dict[str, Any]]]:
        import json
        try:
            with open(self.path, 'rb') as f:
                data = decrypt(f.read(), self.key)
                return json.loads(data)
        except FileNotFoundError:
            return None

    def write(self, data: Dict[str, Dict[str, Any]]) -> None:
        import json
        encrypted = encrypt(json.dumps(data).encode(), self.key)
        with open(self.path, 'wb') as f:
            f.write(encrypted)

db = TinyDB(storage=EncryptedStorage, path='secret.json', key=b'my-secret-key')
```

### Query Caching

Tables maintain an LRU query cache (default capacity: 10). Cached queries return instantly on repeated searches. The cache is cleared automatically on any write operation.

```python
# Disable caching entirely (no cache)
table = db.table('uncached', cache_size=0)

# Unlimited cache
table = db.table('uncached', cache_size=None)

# Larger cache
table = db.table('cached', cache_size=100)

# Manual cache clearing
table.clear_cache()
```

### Persist Empty Tables

By default, empty tables don't appear in `db.tables()`. Use `persist_empty=True` to force persistence:

```python
db.table('persisted', persist_empty=True)
assert 'persisted' in db.tables()

# Default behavior — empty table not listed
db.table('nonpersisted')
assert 'nonpersisted' not in db.tables()
```

## Gotchas

- **JSONStorage keeps the file handle open** — always call `db.close()` or use a context manager. Without closing, the file handle stays open and data may not be flushed.
- **Document IDs are auto-assigned integers starting at 1** — they persist across sessions. After removing documents, IDs are never reused.
- **`db.update()` with no condition updates ALL documents** — `db.update({'status': 'done'})` modifies every document in the table. Always specify a `cond` or `doc_ids` unless intentional.
- **`db.remove()` with no arguments raises `RuntimeError`** — use `db.truncate()` to remove all documents.
- **`insert_multiple()` rejects a single dict** — passing a plain dict raises `ValueError` (dicts iterate over keys). Always pass a list or generator of dicts.
- **Non-Mapping types raise `ValueError`** — `db.insert([1, 2])` or `db.insert('hello')` fails. Any `collections.abc.Mapping` works (dict, OrderedDict, custom Mapping subclasses).
- **Query cache is per-table, not per-database** — each table has its own LRU cache. Writes to any table only clear that table's cache.
- **`matches()` requires the whole string to match** — use `search()` for substring matching. Both use `re.match`/`re.search` internally, so anchor `^`/`$` as needed.
- **`test()` functions must be deterministic** — non-deterministic test functions break the query cache, returning stale results.
- **`map()` queries are never cached** — callables in the query path can be mutable, so these always re-evaluate.
- **Nested field queries fail silently** — `User.address.city == 'London'` returns `False` (not an error) if `address` is missing or not a dict.
- **`upsert()` with no condition requires a `Document` with `doc_id`** — passing a plain dict without a `cond` raises `ValueError`.
- **Storage writes are atomic per-operation** — JSONStorage writes the entire database on each operation. For high-write workloads, use `CachingMiddleware`.
- **Concurrent writes are not safe** — TinyDB has no locking mechanism. For multi-process access, use file-level locking or a different database.
- **Tables are cached** — `db.table('name')` returns the same `Table` instance on repeated calls.
- **`ensure_ascii=False` for Unicode JSON** — pass to JSONStorage: `TinyDB('db.json', ensure_ascii=False)` to store non-ASCII characters directly.
- **`access_mode='r'` on JSONStorage is read-only** — attempts to write raise `IOError`. Default is `'r+'` which reads and writes.
- **`insert()` rejects duplicate doc_ids** — if you pass a `Document` with an ID that already exists, it raises `ValueError`.

## References

- [01-api-reference](references/01-api-reference.md) — Full API reference for TinyDB, Table, Query, Storage, Middleware
- [02-query-examples](references/02-query-examples.md) — Comprehensive query patterns and edge cases
- [03-storage-and-middlewares](references/03-storage-and-middlewares.md) — Storage implementations, custom storage, middleware patterns
- [04-migration-tips](references/04-migration-tips.md) — Migrating from TinyDB 3.x, common upgrade issues
