# TinyDB 4.8.2 — Storage and Middlewares

## Storage Interface

All storages implement the `Storage` abstract base class with two required methods and one optional:

```python
from tinydb.storages import Storage
from typing import Dict, Any, Optional

class MyStorage(Storage):
    def read(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Read the database state.
        Return None if the storage is empty/uninitialized.
        Return a dict of {table_name: {doc_id: document}}.
        """
        ...

    def write(self, data: Dict[str, Dict[str, Any]]) -> None:
        """
        Write the complete database state.
        data is {table_name: {doc_id: document}}.
        """
        ...

    def close(self) -> None:
        """
        Optional cleanup — close file handles, connections, etc.
        Default does nothing.
        """
        pass
```

## Built-in Storages

### JSONStorage

File-based JSON storage. The default.

```python
from tinydb.storages import JSONStorage

# Basic usage
db = TinyDB('path/to/db.json')

# With create_dirs (creates parent directories)
db = TinyDB('path/to/db.json', storage=JSONStorage, create_dirs=True)

# With custom encoding
db = TinyDB('db.json', storage=JSONStorage, encoding='utf-8')

# Read-only mode
db = TinyDB('db.json', storage=JSONStorage, access_mode='r')

# With json.dumps kwargs (indent, sort_keys, etc.)
db = TinyDB('db.json', storage=JSONStorage, indent=2, sort_keys=True)
```

**How it works:** JSONStorage opens the file with `open(path, mode='r+')` and keeps the handle open for the lifetime of the database. `write()` seeks to position 0, writes JSON, flushes, fsyncs, and truncates. This means the file is always a valid JSON document (or empty).

**Access modes:**

| Mode | Behavior |
|---|---|
| `'r+'` (default) | Read and write. Creates file if missing. |
| `'r'` | Read-only. File must exist. Writes raise `IOError`. |
| `'rb'` | Read-only, binary. |
| `'rb+'` | Read and write, binary. |

**Warning:** Using modes like `'w'`, `'w+'`, or `'a'` will truncate or corrupt the file. A warning is emitted but not prevented.

### MemoryStorage

In-memory storage. No persistence.

```python
from tinydb.storages import MemoryStorage

db = TinyDB(storage=MemoryStorage)
db.insert({'key': 'value'})

# Access underlying data
data = db.storage.memory
# {'_default': {'1': {'key': 'value'}}}
```

Useful for testing, temporary data, or embedding TinyDB in processes where persistence is unnecessary.

## Custom Storage Examples

### SQLite Storage

```python
import json
import sqlite3
from tinydb.storages import Storage

class SQLiteStorage(Storage):
    def __init__(self, path):
        self.path = path
        self._conn = sqlite3.connect(path)
        self._conn.execute('CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value TEXT)')
        self._conn.commit()

    def read(self):
        cursor = self._conn.execute('SELECT value FROM data WHERE key = ?', ('_data',))
        row = cursor.fetchone()
        if row is None:
            return None
        return json.loads(row[0])

    def write(self, data):
        self._conn.execute(
            'INSERT OR REPLACE INTO data (key, value) VALUES (?, ?)',
            ('_data', json.dumps(data))
        )
        self._conn.commit()

    def close(self):
        self._conn.close()
```

### YAML Storage

```python
import yaml
from tinydb.storages import Storage

class YAMLStorage(Storage):
    def __init__(self, path):
        self.path = path

    def read(self):
        try:
            with open(self.path, 'r') as f:
                data = yaml.safe_load(f)
                return data if data else None
        except FileNotFoundError:
            return None

    def write(self, data):
        with open(self.path, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False)
```

### MessagePack Storage

```python
import msgpack
from tinydb.storages import Storage

class MessagePackStorage(Storage):
    def __init__(self, path):
        self.path = path

    def read(self):
        try:
            with open(self.path, 'rb') as f:
                data = msgpack.unpackb(f.read(), raw=False)
                return data if data else None
        except FileNotFoundError:
            return None

    def write(self, data):
        with open(self.path, 'wb') as f:
            f.write(msgpack.packb(data, use_bin_type=True))
```

### Encrypted Storage

```python
from cryptography.fernet import Fernet
from tinydb.storages import JSONStorage

class EncryptedStorage(Storage):
    def __init__(self, path, key):
        self._storage = JSONStorage(path)
        self._fernet = Fernet(key)

    def read(self):
        data = self._storage.read()
        if data is None:
            return None
        # Decrypt each table's data
        decrypted = {}
        for table, docs in data.items():
            decrypted[table] = {
                k: self._decrypt_doc(v) for k, v in docs.items()
            }
        return decrypted

    def write(self, data):
        # Encrypt each document
        encrypted = {}
        for table, docs in data.items():
            encrypted[table] = {
                k: self._encrypt_doc(v) for k, v in docs.items()
            }
        self._storage.write(encrypted)

    def _encrypt_doc(self, doc):
        import json
        return self._fernet.encrypt(json.dumps(doc).encode()).decode()

    def _decrypt_doc(self, encrypted):
        import json
        return json.loads(self._fernet.decrypt(encrypted.encode()))

    def close(self):
        self._storage.close()
```

## Middleware System

Middlewares wrap storage classes and intercept `read()`/`write()` calls. They are instantiated (not classes) when passed to TinyDB:

```python
TinyDB('db.json', storage=MiddlewareClass(RealStorageClass))
```

### Middleware Base Class

```python
from tinydb.middlewares import Middleware

class LoggingMiddleware(Middleware):
    def __init__(self, storage_cls):
        super().__init__(storage_cls)

    def read(self):
        print('[READ] Reading from storage')
        return self.storage.read()

    def write(self, data):
        print(f'[WRITE] Writing {len(data)} tables to storage')
        self.storage.write(data)
```

### Chaining Middlewares

Middlewares can be nested:

```python
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage

# Caching + Logging around JSONStorage
db = TinyDB(
    'db.json',
    storage=LoggingMiddleware(CachingMiddleware(JSONStorage))
)
```

Call order: `LoggingMiddleware.read()` → `CachingMiddleware.read()` → `JSONStorage.read()`.

### CachingMiddleware Details

```python
from tinydb.middlewares import CachingMiddleware

# Default: flush every 1000 writes
db = TinyDB('db.json', storage=CachingMiddleware(JSONStorage))

# Custom flush interval
CachingMiddleware.WRITE_CACHE_SIZE = 100

# Manual flush
db.storage.flush()

# Check pending writes
print(db.storage._cache_modified_count)  # number of unflushed writes
```

**How it works:**
- First `read()` loads data from underlying storage into `self.cache`
- Subsequent `read()` calls return the cached data
- `write()` updates the cache and increments `_cache_modified_count`
- When count reaches `WRITE_CACHE_SIZE`, `flush()` writes to disk
- `close()` always flushes before closing

**Gotchas:**
- If the process crashes, up to `WRITE_CACHE_SIZE` writes are lost
- The cache holds the entire database in memory
- `flush()` must be called before reading from another process

### Transaction Middleware (Example)

```python
from tinydb.middlewares import Middleware

class TransactionMiddleware(Middleware):
    def __init__(self, storage_cls):
        super().__init__(storage_cls)
        self._transaction_cache = None
        self._in_transaction = False

    def begin(self):
        self._transaction_cache = self.storage.read()
        self._in_transaction = True

    def commit(self):
        if self._in_transaction:
            self._in_transaction = False
            # Data already in cache, flush it
            if hasattr(self.storage, 'flush'):
                self.storage.flush()
            else:
                self.storage.write(self._transaction_cache)

    def rollback(self):
        if self._in_transaction and self._transaction_cache is not None:
            # Restore original data
            self.storage.write(self._transaction_cache)
            self._transaction_cache = None
            self._in_transaction = False

    def read(self):
        return self.storage.read()

    def write(self, data):
        if self._in_transaction:
            # Buffer writes during transaction
            self._transaction_cache = data
        else:
            self.storage.write(data)
```

## Storage Performance Considerations

### JSONStorage

- **Pros:** Human-readable, no dependencies, built-in
- **Cons:** Full rewrite on every operation, no concurrent write safety
- **Best for:** Small databases (<10MB), single-process use
- **Optimization:** Use `CachingMiddleware` for batch writes

### MemoryStorage

- **Pros:** Fastest possible, no I/O
- **Cons:** No persistence
- **Best for:** Testing, temporary data, benchmarks

### General Tips

1. **Use `CachingMiddleware`** for write-heavy workloads — reduces disk I/O
2. **Close the database** when done — `JSONStorage` holds an open file handle
3. **Avoid frequent small writes** — batch inserts with `insert_multiple()`
4. **Consider alternative storages** for large datasets — SQLite, MessagePack, etc.
5. **Never share a TinyDB instance across processes** — each process needs its own connection
6. **Query cache helps reads** — increase `cache_size` for tables with repeated queries
