# TinyDB 4.9.0 — API Reference

Signatures verified against the v4.9.0 source tree (`tinydb/`).

## `tinydb` top-level exports

```python
from tinydb import TinyDB, Storage, JSONStorage, Query, where
```

`where('field')` is a shorthand for `Query()['field']`.

## `TinyDB` (`tinydb.database.TinyDB`)

### Constructor

```python
TinyDB(*args, storage=JSONStorage, **kwargs)
```

All `*args`/`**kwargs` except `storage` are forwarded to the storage class constructor. For `JSONStorage` the positional argument is the file path.

### Class variables (customization hooks)

| Variable | Default | Description |
|---|---|---|
| `table_class` | `Table` | Class used to create table instances |
| `default_table_name` | `'_default'` | Name of the default table (set per instance or on the class) |
| `default_storage_class` | `JSONStorage` | Storage class used when none is passed |

### Properties and methods

| Member | Returns | Description |
|---|---|---|
| `storage` | `Storage` | The underlying storage (or outermost middleware) instance |
| `default_table_name` | `str` | Settable per instance; also a class variable |
| `table(name, **kwargs)` | `Table` | Get or create a named table; kwargs go to the table class (`cache_size`, `persist_empty`) |
| `tables()` | `set[str]` | Set of all table names |
| `drop_table(name)` | `None` | Drop a table (irreversible) |
| `drop_tables()` | `None` | Drop all tables (irreversible) |
| `close()` | `None` | Close the storage |
| `__enter__()` / `__exit__()` | `TinyDB` | Context manager |
| `__len__()` | `int` | Document count in the default table |
| `__iter__()` | `Iterator[Document]` | Iterate documents in the default table |
| `__getattr__(name)` | — | Delegates unknown attributes to the default table (`db.insert(...)`, `db.search(...)`, ... all work directly) |

## `Table` (`tinydb.table.Table`)

### Constructor

```python
Table(storage, name, cache_size=default_query_cache_capacity, persist_empty=False)
```

Tables are usually created through `db.table(name, cache_size=..., persist_empty=...)`, which passes `name` plus kwargs to the table class. Class variables: `default_query_cache_capacity = 10`, `document_class = Document`, `query_cache_class = LRUCache`.

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `insert` | `(document: Mapping)` | `int` | Insert a document; returns its ID. Raises `ValueError` if not a Mapping or ID taken |
| `insert_multiple` | `(documents: Iterable[Mapping])` | `list[int]` | Insert many (list, generator, ...); returns IDs |
| `all` | `()` | `list[Document]` | All documents |
| `search` | `(cond: QueryLike)` | `list[Document]` | Documents matching a query or predicate |
| `get` | overloads: `(cond)` / `(doc_id=)` / `(doc_ids=)` | `Document` or `list[Document]` or `None` | First match, document(s) by ID(s); raises `RuntimeError` with no arguments |
| `contains` | `(cond)` or `(doc_id=)` | `bool` | Existence check; raises `RuntimeError` with no arguments |
| `update` | `(fields: Mapping \| Callable, cond=None, doc_ids=None)` | `list[int]` | Update matching docs; no `cond`/`doc_ids` updates ALL docs; missing `doc_ids` skipped silently (4.9.0) |
| `update_multiple` | `(updates: Iterable[tuple[Mapping \| Callable, QueryLike]])` | `None` | Apply several (fields-or-operation, query) pairs |
| `upsert` | `(document: Mapping, cond=None)` | `list[int]` | Update all matching, insert if none match; needs `cond` or a `Document` with `doc_id` |
| `remove` | `(cond=None, doc_ids=None)` | `list[int]` | Remove matching docs; missing `doc_ids` skipped silently (4.9.0); raises `RuntimeError` with no arguments (use `truncate()`) |
| `truncate` | `()` | `None` | Remove all documents |
| `count` | `(cond: QueryLike)` | `int` | Count of matching documents |
| `clear_cache` | `()` | `None` | Clear this table's query cache |
| `__len__` | `()` | `int` | Document count |
| `__iter__` | `()` | `Iterator[Document]` | Iterate documents |
| `name` | property | `str` | Table name |
| `storage` | property | `Storage` | Underlying storage instance |

`QueryLike` = any `Query`/`QueryInstance` or a callable `doc -> bool`.

## `Document` (`tinydb.table.Document`)

A `dict` subclass.

```python
Document({'name': 'John', 'age': 22}, doc_id=12)
doc.doc_id  # the document's ID
```

Use it to insert/update/upsert with explicit IDs.

## `Query` / `QueryInstance` (`tinydb.queries`)

`Query()` provides field access; comparison operators and the methods below return `QueryInstance`.

| Operation | Meaning |
|---|---|
| `Query().field` / `Query()['field']` | Field path (property or bracket access) |
| `==`, `!=`, `<`, `<=`, `>`, `>=` | Compare field to a **literal** value |
| `&`, `|`, `~` | Logical AND / OR / NOT between instances |
| `.exists()` | Field exists |
| `.matches(regex, flags=0)` | Whole field matches regex |
| `.search(regex, flags=0)` | Any part of the field matches regex |
| `.test(func, *args)` | `func(value, *args)` returns `True`; unhashable `*args` OK since 4.9.0 |
| `.any(cond \| list)` | Field is a list where at least one element matches `cond` (query) or is in `list` |
| `.all(cond \| list)` | Field is a list where every element matches `cond` (query) or is in `list` |
| `.one_of(items: list)` | Field value is contained in `items` |
| `.fragment(document: Mapping)` | Document (or field) contains all given keys/values |
| `.map(fn)` | Apply `fn` to the document or field before further comparison; never cached |
| `.noop()` | Always-True query for dynamic composition |
| `.is_cacheable` | Property; set `is_cacheable = lambda: False` on a callable to skip caching |

`QueryInstance` is the result object; it is hashable, callable (`instance(doc) -> bool`), and supports `&`/`|`/`~`.

## `tinydb.operations`

Each returns a transform `MutableMapping -> None` for use as the first `update()` argument:

| Function | Signature | Effect |
|---|---|---|
| `delete` | `(field)` | Delete a key |
| `add` | `(field, n)` | Add `n` (works for strings) |
| `subtract` | `(field, n)` | Subtract `n` |
| `set` | `(field, val)` | Set key to value |
| `increment` | `(field)` | Add 1 |
| `decrement` | `(field)` | Subtract 1 |

Since 4.9.0 these are typed to accept `MutableMapping` documents, so in-place mutation transforms type-check.

## `tinydb.storages`

### `Storage` (ABC)

```python
class Storage(ABC):
    def read(self) -> Optional[dict[str, dict[str, Any]]]: ...   # None if uninitialized
    def write(self, data: dict[str, dict[str, Any]]) -> None: ...
    def close(self) -> None: ...                                  # optional cleanup
```

### `JSONStorage`

```python
JSONStorage(path: str, create_dirs=False, encoding=None, access_mode='r+', **kwargs)
```

`access_mode` is a normal file mode (`'r'` = read-only, writes raise `IOError`). `**kwargs` are forwarded to `json.dumps` on every write.

### `MemoryStorage`

No constructor arguments; data lives only in memory.

## `tinydb.middlewares`

### `Middleware` (base)

```python
class Middleware:
    def __init__(self, storage_cls): ...   # must be called by subclasses
    def __call__(self, *args, **kwargs): ...  # middleware stack — instantiates the next layer
    self.storage  # underlying storage/middleware instance (set after __call__)
```

Middleware receive and must return the full database dict `{table_name: {doc_id: document}}`. Attributes not defined on the middleware are proxied to the underlying storage (`__getattr__`).

### `CachingMiddleware`

```python
CachingMiddleware(storage_cls)   # WRITE_CACHE_SIZE = 1000
mw.flush()  # force pending writes to disk
```

Caches all reads; writes are batched to disk after `WRITE_CACHE_SIZE` operations. Flush on `close()` or via the context manager.

## MyPy plugin

Add to `mypy.ini` / `setup.cfg`:

```ini
[mypy]
plugins = tinydb.mypy_plugin
```

Helps MyPy type-check code patterns that use TinyDB's delegation and class-variable overrides.
