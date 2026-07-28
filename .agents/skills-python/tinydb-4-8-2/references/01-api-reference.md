# TinyDB 4.8.2 — API Reference

## TinyDB

### Constructor

```python
TinyDB(*args, storage=JSONStorage, **kwargs)
```

All `*args` and `**kwargs` (except `storage`) are forwarded to the storage class. For `JSONStorage`, the positional arg is the file path.

**Class variables** (override in subclasses):

| Variable | Default | Description |
|---|---|---|
| `table_class` | `Table` | Class used to create table instances |
| `default_table_name` | `'_default'` | Name of the default table |
| `default_storage_class` | `JSONStorage` | Fallback storage class if none passed |

### Methods

| Method | Returns | Description |
|---|---|---|
| `table(name, **kwargs)` | `Table` | Get or create a named table. Passes kwargs to `table_class` |
| `tables()` | `Set[str]` | Set of all table names |
| `drop_table(name)` | `None` | Drop a specific table. Irreversible. |
| `drop_tables()` | `None` | Drop all tables. Irreversible. |
| `close()` | `None` | Close the storage (flushes handles). |
| `__enter__()` | `TinyDB` | Context manager entry. |
| `__exit__(*args)` | `None` | Context manager exit, calls `close()`. |
| `__len__()` | `int` | Document count in default table. |
| `__iter__()` | `Iterator[Document]` | Iterate default table documents. |

### Forwarded to Default Table

All unknown attribute access on `TinyDB` is forwarded to the default table. So `db.insert()`, `db.search()`, `db.update()`, `db.remove()`, `db.get()`, `db.all()`, `db.truncate()`, `db.count()`, `db.contains()`, `db.clear_cache()` all operate on the `'_default'` table.

### Properties

| Property | Type | Description |
|---|---|---|
| `storage` | `Storage` | The storage instance used by this database. |

## Table

### Constructor

```python
Table(storage, name, cache_size=10, persist_empty=False)
```

| Parameter | Type | Description |
|---|---|---|
| `storage` | `Storage` | The storage instance |
| `name` | `str` | Table name |
| `cache_size` | `int` | Query cache capacity. `None` for unlimited. |
| `persist_empty` | `bool` | If True, write the table to storage even when empty |

**Class variables**:

| Variable | Default | Description |
|---|---|---|
| `document_class` | `Document` | Class for representing documents |
| `document_id_class` | `int` | Class for representing document IDs |
| `query_cache_class` | `LRUCache` | Class for the query cache |
| `default_query_cache_capacity` | `10` | Default cache size |

### Methods

| Method | Returns | Description |
|---|---|---|
| `insert(document)` | `int` | Insert a document. Returns its ID. |
| `insert_multiple(documents)` | `List[int]` | Insert multiple documents. Returns list of IDs. |
| `get(cond=None, doc_id=None, doc_ids=None)` | `Optional[Document \| List[Document]]` | Get one doc by query/ID, or multiple by `doc_ids`. |
| `search(cond)` | `List[Document]` | Search for matching documents. |
| `update(fields, cond=None, doc_ids=None)` | `List[int]` | Update matching docs. Returns updated IDs. |
| `update_multiple(updates)` | `List[int]` | Apply multiple (fields, cond) pairs. Returns updated IDs. |
| `upsert(document, cond=None)` | `List[int]` | Update if exists, insert otherwise. |
| `remove(cond=None, doc_ids=None)` | `List[int]` | Remove matching docs. Returns removed IDs. |
| `truncate()` | `None` | Remove all documents. |
| `all()` | `List[Document]` | Get all documents. |
| `count(cond)` | `int` | Count matching documents. |
| `contains(cond=None, doc_id=None)` | `bool` | Check if a document exists. |
| `clear_cache()` | `None` | Clear the query cache. |
| `__len__()` | `int` | Total document count. |
| `__iter__()` | `Iterator[Document]` | Iterate all documents. |

### Properties

| Property | Type | Description |
|---|---|---|
| `name` | `str` | The table name. |
| `storage` | `Storage` | The storage instance. |

## Document

A subclass of `dict` with an additional `doc_id` attribute.

```python
Document(value: Mapping, doc_id: int)
```

```python
doc = table.get(doc_id=1)
print(doc['name'])   # dict access
print(doc.doc_id)    # document ID
```

## Query

### Construction

```python
from tinydb import Query, where

# ORM-style
User = Query()
User.name == 'Alice'
User.address.city == 'London'
User['log-in'] == True  # bracket notation

# Shorthand
where('name') == 'Alice'
```

### Comparison Operators

| Operator | Method | Example |
|---|---|---|
| `==` | `__eq__` | `User.age == 30` |
| `!=` | `__ne__` | `User.status != 'inactive'` |
| `<` | `__lt__` | `User.age < 18` |
| `<=` | `__le__` | `User.score <= 100` |
| `>` | `__gt__` | `User.age > 0` |
| `>=` | `__ge__` | `User.score >= 50` |

### Query Methods

| Method | Returns | Description |
|---|---|---|
| `exists()` | `QueryInstance` | True if field exists in document. |
| `matches(regex, flags=0)` | `QueryInstance` | Whole string matches regex (`re.match`). |
| `search(regex, flags=0)` | `QueryInstance` | Substring matches regex (`re.search`). |
| `test(func, *args)` | `QueryInstance` | Custom test function. Must be deterministic. |
| `any(cond)` | `QueryInstance` | Any list element matches sub-query or is in value list. |
| `all(cond)` | `QueryInstance` | All list elements match sub-query or value list is subset. |
| `one_of(items)` | `QueryInstance` | Field value is in the given list. |
| `map(fn)` | `Query` | Transform field value before comparison. |
| `fragment(document)` | `QueryInstance` | Match multiple fields at once. No path needed. |
| `noop()` | `QueryInstance` | Always True. Base for dynamic query composition. |

### QueryInstance (Result of Query Operations)

| Operation | Method | Description |
|---|---|---|
| `&` (AND) | `__and__` | Combine two queries with logical AND. |
| `\|` (OR) | `__or__` | Combine two queries with logical OR. |
| `~` (NOT) | `__invert__` | Negate a query. |
| `__call__(value)` | — | Evaluate query against a document dict. |
| `is_cacheable()` | `bool` | Whether this query can be cached. |
| `__hash__()` | `int` | Stable hash for cache key. |

## Storage

Abstract base class. Implement `read()` and `write()`.

### Storage (ABC)

| Method | Returns | Description |
|---|---|---|
| `read()` | `Optional[Dict[str, Dict[str, Any]]]` | Read current state. Return `None` if empty. |
| `write(data)` | `None` | Write database state. |
| `close()` | `None` | Optional cleanup (file handles, etc.). |

### JSONStorage

```python
JSONStorage(path, create_dirs=False, encoding=None, access_mode='r+', **kwargs)
```

| Parameter | Default | Description |
|---|---|---|
| `path` | — | Path to the JSON file. |
| `create_dirs` | `False` | Create parent directories if missing. |
| `encoding` | `None` | File encoding. |
| `access_mode` | `'r+'` | File access mode. Use `'r'` for read-only. |
| `**kwargs` | — | Extra kwargs passed to `json.dumps()`. |

### MemoryStorage

```python
MemoryStorage()
```

Stores data in memory. No constructor arguments. Data is lost when the instance is discarded.

## Middleware

### Middleware (Base Class)

```python
Middleware(storage_cls)
```

Wrap a storage class. Implement `read()`, `write()`, and optionally `close()`. Access the wrapped storage via `self.storage`.

### CachingMiddleware

```python
CachingMiddleware(storage_cls)
```

| Attribute | Default | Description |
|---|---|---|
| `WRITE_CACHE_SIZE` | `1000` | Flush after this many write operations. |

| Method | Returns | Description |
|---|---|---|
| `flush()` | `None` | Force-flush cached data to underlying storage. |
| `close()` | `None` | Flush and close underlying storage. |

## Operations (Update Helpers)

Import from `tinydb.operations`:

| Function | Description | Example |
|---|---|---|
| `delete(field)` | Remove a field from matching documents. | `db.update(delete('temp'), where('id') == 1)` |
| `add(field, n)` | Add `n` to a field. Works with numbers and strings (concatenation). | `db.update(add('score', 10), where('id') == 1)` | `db.update(add('name', ' Jr'), where('id') == 1)` |
| `subtract(field, n)` | Subtract `n` from a numeric field. | `db.update(subtract('score', 5), where('id') == 1)` |
| `set(field, val)` | Set a field to a value. | `db.update(set('status', 'done'), where('id') == 1)` |
| `increment(field)` | Increment a field by 1. | `db.update(increment('views'), where('id') == 1)` |
| `decrement(field)` | Decrement a field by 1. | `db.update(decrement('stock'), where('id') == 1)` |

## Utilities

### LRUCache

```python
LRUCache(capacity=None)
```

Fixed-size LRU cache. `capacity=None` means unlimited. Implements `MutableMapping`.

| Property/Method | Description |
|---|---|
| `capacity` | Max entries (or `None` for unlimited). |
| `lru` | List of keys in LRU order. |
| `length` | Current number of entries. |
| `clear()` | Remove all entries. |

### freeze(obj)

Make an object hashable by converting dicts to `FrozenDict`, lists to tuples, sets to `frozenset`. Used internally for query hashing.
