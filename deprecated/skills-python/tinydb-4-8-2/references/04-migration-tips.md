# TinyDB 4.8.2 — Migration Tips

## From TinyDB 3.x to 4.x

### Major Changes

#### 1. Python 3.8+ Only

TinyDB 4.x drops support for Python 2 and Python 3.5-3.7. Minimum is Python 3.8.

#### 2. `where()` Returns Query, Not QueryInstance

In 3.x, `where('field')` returned a special object. In 4.x, it returns a `Query` with a path set. The API is the same but internals changed.

```python
# 3.x and 4.x — same usage
from tinydb import where
db.search(where('name') == 'Alice')
```

#### 3. Table API Changes

```python
# 3.x — remove required a condition
db.remove(where('name') == 'Alice')

# 4.x — same, but you can also remove by doc_ids
db.remove(doc_ids=[1, 2, 3])
```

#### 4. `get()` Signature Changes

```python
# 3.x — get by query only
db.get(where('name') == 'Alice')

# 4.x — get by query, doc_id, or multiple doc_ids
db.get(where('name') == 'Alice'))
db.get(doc_id=1)
db.get(doc_ids=[1, 2, 3])  # returns list
```

#### 5. `update()` Changes

```python
# 3.x — update by query or all
db.update({'field': 'value'}, where('name') == 'Alice')
db.update({'field': 'value'})  # all documents

# 4.x — same, plus update by doc_ids
db.update({'field': 'value'}, where('name') == 'Alice'))
db.update({'field': 'value'}, doc_ids=[1, 2, 3])
db.update({'field': 'value'})  # all documents (same as 3.x)
```

#### 6. `upsert()` Added

New in 4.x — update if exists, insert otherwise:

```python
from tinydb import TinyDB, where
from tinydb.table import Document

db = TinyDB('db.json')

# Upsert by query
db.upsert({'name': 'Alice', 'score': 100}, where('name') == 'Alice')

# Upsert by doc_id
db.upsert(Document({'name': 'Bob', 'score': 50}, doc_id=42))
```

#### 7. `update_multiple()` Added

Apply multiple conditional updates in a single operation:

```python
from tinydb import TinyDB, where

db = TinyDB('db.json')

db.update_multiple([
    ({'status': 'processed'}, where('status') == 'pending')),
    ({'status': 'archived'}, where('status') == 'old')),
])
```

#### 8. Storage Interface

The storage interface is the same but with proper type hints:

```python
# 3.x and 4.x — same interface
from tinydb.storages import Storage

class MyStorage(Storage):
    def read(self):
        ...

    def write(self, data):
        ...

    def close(self):
        ...
```

#### 9. Middleware Interface

Same as 3.x but with `self.storage` access:

```python
from tinydb.middlewares import Middleware

class MyMiddleware(Middleware):
    def __init__(self, storage_cls):
        super().__init__(storage_cls)

    def read(self):
        return self.storage.read()

    def write(self, data):
        self.storage.write(data)
```

#### 10. Query Methods Added

New query methods in 4.x:

- `any()` — check if any list element matches
- `all()` — check if all list elements match
- `one_of()` — check if value is in a list
- `map()` — transform field before comparison
- `fragment()` — match multiple fields at once
- `noop()` — always-true query for dynamic composition

```python
from tinydb import Query

# New in 4.x
Query().tags.any(['sale', 'clearance'])
Query().status.one_of(['active', 'pending'])
Query().age.map(lambda x: x * 2) == 60
Query().fragment({'name': 'Alice', 'age': 30})
Query().noop()  # base for dynamic queries
```

## Common Upgrade Issues

### Issue: `from tinydb import Query` Missing

In 3.x, `Query` was accessible as `where`. In 4.x, both are exported:

```python
# Both work in 4.x
from tinydb import Query, where

User = Query()
db.search(User.name == 'Alice')

db.search(where('name') == 'Alice')
```

### Issue: Custom Storages Not Working

If your custom storage relied on internal TinyDB APIs, check that it implements the public `Storage` interface:

```python
# Correct — implements public interface
class MyStorage(Storage):
    def read(self):
        ...

    def write(self, data):
        ...

    def close(self):
        ...
```

### Issue: Query Cache Behavior

The query cache is now an LRU cache with configurable capacity:

```python
# Default cache size is 10
table = db.table('my_table')

# Disable caching
table = db.table('my_table', cache_size=None)

# Larger cache
table = db.table('my_table', cache_size=100)
```

### Issue: `contains()` Signature

```python
# 4.x — supports both query and doc_id
db.contains(where('name') == 'Alice')
db.contains(doc_id=1)
```

### Issue: Document Class Access

```python
# 4.x — Document is in tinydb.table
from tinydb.table import Document

doc = Document({'name': 'Alice'}, doc_id=1)
db.insert(doc)
```

## Data Format Compatibility

TinyDB 4.x uses the same JSON data format as 3.x. Existing database files are compatible without migration:

```json
{
    "_default": {
        "1": {"name": "Alice", "age": 30},
        "2": {"name": "Bob", "age": 25}
    },
    "users": {
        "1": {"email": "alice@example.com"}
    }
}
```

Document IDs are stored as strings in JSON (required by JSON spec) but accessed as integers in Python.

## Testing Migration Tips

### Using MemoryStorage for Tests

```python
import pytest
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage

@pytest.fixture
def db():
    return TinyDB(storage=MemoryStorage)

def test_insert_and_search(db):
    db.insert({'name': 'Alice', 'age': 30})
    db.insert({'name': 'Bob', 'age': 25})

    results = db.search(where('age') > 26)
    assert len(results) == 1
    assert results[0]['name'] == 'Alice'
```

### Testing Custom Storages

```python
import pytest
from tinydb import TinyDB, where
from tinydb.storages import JSONStorage
import tempfile
import os

@pytest.fixture
def tmp_db():
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        path = f.name
    try:
        db = TinyDB(path)
        yield db
    finally:
        db.close()
        os.unlink(path)

def test_persistence(tmp_db):
    tmp_db.insert({'key': 'value'})
    # Reopen to verify persistence
    tmp_db.close()
    with TinyDB(tmp_db.storage._handle.name) as reopened:
        results = reopened.search(where('key') == 'value')
        assert len(results) == 1
```
