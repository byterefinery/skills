# TinyDB 4.9.0 — Storage and Middlewares

From `docs/usage.rst`, `docs/extend.rst`, and the v4.9.0 source (`tinydb/storages.py`, `tinydb/middlewares.py`).

## Data layout

All tables and documents live in one nested dict:

```python
{
    '_default': {1: {'key': 'value'}, 2: {'key': 'value'}},
    # other tables
}
```

Document IDs are integers in memory but serialized as strings in JSON storage.

## Storage types

### JSONStorage (default)

```python
JSONStorage(path: str, create_dirs=False, encoding=None, access_mode='r+', **kwargs)
```

- `access_mode` is a normal file mode — `'r'` makes it read-only (writes raise `IOError`)
- `**kwargs` are forwarded to `json.dumps` on every write:

```python
# Prettified JSON output
db = TinyDB('db.json', sort_keys=True, indent=4, separators=(',', ': '))
```

- The file handle stays open until `close()` — use a context manager or call `db.close()`
- 4.9.0 fix: creating a database file in the current directory without an explicit path prefix no longer raises `FileNotFoundError`

JSON cannot serialize custom classes. If you need that, write a custom storage using `pickle` or `PyYAML` (or install the `tinydb-serialization` extension).

### MemoryStorage

```python
from tinydb.storages import MemoryStorage
db = TinyDB(storage=MemoryStorage)
```

No constructor arguments; data is lost when the instance is discarded.

## Storage forwarding and defaults

- All `TinyDB(...)` arguments except `storage` are forwarded to the storage class — for `JSONStorage` the positional argument is the file path.
- Change the default storage for all instances: `TinyDB.default_storage_class = MemoryStorage`.
- Access the live storage instance (e.g. to call `flush()` on middleware): `db.storage`.

## Query caching

Tables cache query results in an LRU cache (default capacity 10):

```python
table = db.table('name', cache_size=30)    # tune capacity
table = db.table('name', cache_size=0)     # disable
table = db.table('name', cache_size=None)  # unlimited
table.clear_cache()                        # force re-read from storage
```

Notes from the docs:

- The same table cannot be opened twice with different settings — after the first `db.table(name)`, later calls return the cached instance.
- The cache is not invalidated when the underlying storage is modified by an external process — call `clear_cache()` to re-read.
- Opening multiple `TinyDB` instances on the same data may give unexpected behavior due to query caching.
- With an unlimited cache, `test()` queries store a reference to the test function — long-running apps using `lambda` test functions may leak memory.

## Middlewares

A middleware wraps a storage to modify its behavior. It needs `read()`/`write()` and can reach the underlying storage via `self.storage`. The constructor **must** call the `Middleware` base constructor with `storage_cls`:

```python
from tinydb.middlewares import Middleware

class RemoveEmptyItemsMiddleware(Middleware):
    def __init__(self, storage_cls):
        # Any middleware has to call the super constructor with storage_cls
        super().__init__(storage_cls)

    def read(self):
        data = self.storage.read()
        for table_name in data:
            table_data = data[table_name]
            for doc_id in table_data:
                if table_data[doc_id] == {}:
                    del table_data[doc_id]
        return data

    def write(self, data):
        for table_name in data:
            table_data = data[table_name]
            for doc_id in table_data:
                if table_data[doc_id] == {}:
                    del table_data[doc_id]
        self.storage.write(data)

    def close(self):
        self.storage.close()

db = TinyDB(storage=RemoveEmptyItemsMiddleware(JSONStorage))
```

Middleware can be nested:

```python
db = TinyDB('/path/to/db.json', storage=FirstMiddleware(SecondMiddleware(JSONStorage)))
```

### CachingMiddleware

Reduces disk I/O: caches all reads and writes to disk after a configured number of write operations (`WRITE_CACHE_SIZE = 1000`).

```python
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

db = TinyDB('/path/to/db.json', storage=CachingMiddleware(JSONStorage))

# Make sure data reaches disk:
#   - context manager (with TinyDB(...) as db: ...)
#   - db.close()
#   - db.storage.flush()  # force it sooner
```

## Custom storage

Implement the `Storage` ABC. The docs' YAML example (using PyYAML):

```python
import yaml
from tinydb import Storage

class YAMLStorage(Storage):
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        with open(self.filename) as handle:
            try:
                data = yaml.safe_load(handle.read())
                return data
            except yaml.YAMLError:
                return None  # return None if uninitialized

    def write(self, data):
        with open(self.filename, 'w+') as handle:
            yaml.dump(data, handle)

    def close(self):
        pass

db = TinyDB('db.yml', storage=YAMLStorage)
```

Rules:

1. The storage constructor receives every argument passed to `TinyDB(...)` except `storage` — `TinyDB('something', storage=YAMLStorage)` passes `'something'` to `YAMLStorage`. If your constructor accepts callables, do not derive them from untrusted input.
2. Use `yaml.safe_load` when processing data from a potentially untrusted source.
3. `read()` must return `None` when the storage is uninitialized (TinyDB does its internal initialization).
4. Put cleanup (closing file handles) in `close()` — run via `db.close()` or the context manager.

## Other extension points

- **Hooks and overrides** — class variables change behavior without subclassing:

```python
TinyDB.default_table_name = 'my_table_name'
TinyDB.table_class.default_query_cache_capacity = 100
```

- **Subclassing** — override `TinyDB` and/or `Table` and register them:

```python
class MyTable(Table):
    ...

TinyDB.table_class = MyTable
```
