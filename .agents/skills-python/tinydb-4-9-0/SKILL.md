---
name: tinydb-4-9-0
description: >
  TinyDB 4.9.0 — lightweight, zero-dependency document-oriented database for Python. Use this
  skill whenever the user mentions TinyDB, JSON-based local databases, document stores without
  external servers, lightweight Python databases, or small-app data persistence. Covers querying
  with Query objects and where(), advanced queries (matches, test, fragment, any/all, map),
  update operations (delete, add, increment, set), document IDs, multi-table support, custom
  storages, middlewares (CachingMiddleware), and the 4.9.0 changes (Python 3.10+ requirement,
  doc_ids error-handling fixes). Pure Python, MIT licensed, in maintenance mode.
metadata:
  tags:
    - database
    - nosql
    - python
    - json
---

# tinydb 4.9.0

TinyDB is a tiny, document-oriented database written in pure Python with no external dependencies. It stores data as JSON (by default) and provides a MongoDB-like query API. Targeted at small apps where SQL or an external database server would be overkill. In maintenance mode — bugfix releases only, no new features planned.

## Overview

### 4.9.0 Changes (from the changelog)

- **Requires Python 3.10+** — official support for 3.8 and 3.9 dropped (both EOL)
- `Table.update(doc_ids=...)` / `Table.remove(doc_ids=...)` no longer raise `KeyError` for missing IDs — skipped silently; the returned list contains only IDs actually affected (issue 591)
- `Query.test()` accepts unhashable extra arguments (lists, dicts) without `TypeError` (issue 517)
- Fixes: `FileNotFoundError` when creating a DB file in the current directory (PR 619); falsy values (`0`, `None`) in the query `LRUCache`; improved type hints for `Table.get`/`Table.update`/`operations`

### Core Concepts

- **Documents** — Python `dict` (any `Mapping`) instances stored in tables. Each gets an auto-incrementing integer `_id`, accessible via `Document.doc_id`.
- **Tables** — Named collections. The default table is `'_default'`; all operations on the `TinyDB` instance act on it. Access via `db.table('name')`.
- **Queries** — Built with the `Query()` class or `where()` shorthand. Combined with `&` (AND), `|` (OR), `~` (NOT). Comparisons only accept literal values on the right-hand side.
- **Storages** — Pluggable persistence layer. `JSONStorage` (file-based) is the default; `MemoryStorage` is in-memory. Custom storages implement `read()`/`write()`/`close()`.
- **Middlewares** — Wrap storages to add behavior. `CachingMiddleware` batches writes (flushes after 1000 writes) and caches reads.

### Installation

```bash
pip install tinydb==4.9.0
```

No dependencies. Requires Python 3.10+.

## Usage

### Basic CRUD

```python
from tinydb import TinyDB, Query, where

# Open (or create) a JSON database file
db = TinyDB('data.json')

# Insert — returns the document ID
doc_id = db.insert({'name': 'Alice', 'age': 30})

# Insert multiple — accepts a list or any iterable (e.g. generator)
ids = db.insert_multiple([
    {'name': 'Bob', 'age': 25},
    {'name': 'Charlie', 'age': 35},
])
db.insert_multiple({'int': 1, 'value': i} for i in range(2))

# Get all documents / iterate
docs = db.all()
for item in db:
    print(item)

# Search — returns list of matching documents
results = db.search(where('name') == 'Alice')
results = db.search(Query().name == 'Alice')

# Get one matching document — returns None if no match
doc = db.get(where('age') > 28)
doc = db.get(doc_id=1)
docs = db.get(doc_ids=[1, 2])  # multiple by ID

# Update matching documents — returns list of updated IDs
updated_ids = db.update({'age': 31}, where('name') == 'Alice')

# Remove matching documents — returns list of removed IDs
removed_ids = db.remove(where('name') == 'Bob')
removed_ids = db.remove(doc_ids=[1, 2])

# Truncate (remove all documents in the table)
db.truncate()

# Count / existence / length
count = db.count(where('age') >= 30)
exists = db.contains(where('name') == 'Alice')
exists = db.contains(doc_id=1)
n = len(db)  # document count in the default table

# Close the database (flushes the storage)
db.close()
```

### Context Manager

```python
with TinyDB('data.json') as db:
    db.insert({'key': 'value'})
# db.close() called automatically
```

### Query Language

```python
from tinydb import TinyDB, Query, where

User = Query()  # ORM-style query object

# Comparisons — ==, !=, <, <=, >, >= with literal values only
db.search(User.age == 30)
db.search(User.age >= 18)

# Nested fields via property or bracket access
db.search(User.birthday.year == 1990)
db.search(where('birthday')['year'] == 1900)

# Field names that are not valid identifiers — use bracket notation
db.search(User['country-code'] == 'foo')

# Field existence
db.search(User.name.exists())

# Regex — matches() requires the whole field to match; flags supported
db.search(User.name.matches(r'[aZ]*'))
db.search(User.name.matches('John', flags=re.IGNORECASE))

# Regex — search() matches any part of the field
db.search(User.name.search('b+'))

# Custom test function, optionally with extra arguments
db.search(User.age.test(test_func, 0, 21))

# Transform a field (or the whole document) before comparison
db.search(User.name.map(unidecode) == 'Jose')  # matches 'José' etc.

# Fragment — document (or a field) must contain this dict of fields
db.search(Query().fragment({'foo': True, 'bar': False}))

# Field containing a list — any() / all() with value lists or nested queries
db.search(User.groups.any(['admin', 'sudo']))       # at least one value
db.search(User.groups.all(['admin', 'user']))       # all values present
db.search(Group.permissions.any(Permission.type == 'read'))  # nested query

# Value contained in a list
db.search(User.name.one_of(['jane', 'john']))

# Combine queries — always parenthesize operands
db.search(~(User.name == 'John'))                       # NOT
db.search((User.name == 'John') & (User.age <= 30))    # AND
db.search((User.name == 'John') | (User.name == 'Bob')) # OR

# Compose queries dynamically with the no-op query
db.search(Query().noop() & (User.name == 'John'))
```

Field-to-field comparisons (`Query().a == Query().b`) are **not** supported — pass a callable predicate instead:

```python
db.search(lambda doc: doc.get('a') == doc.get('b'))
```

### Update Operations

```python
from tinydb import TinyDB, where
from tinydb.operations import delete, add, subtract, set, increment, decrement

# Each returns a function; pass it as the first argument to update()
db.update(delete('key1'), where('name') == 'Alice')   # delete a field
db.update(add('score', 10), where('name') == 'Alice') # also works for strings
db.update(subtract('score', 5), where('name') == 'Alice')
db.update(set('status', 'active'), where('name') == 'Alice')
db.update(increment('views'), where('doc_id') == 1)
db.update(decrement('stock'), where('doc_id') == 1)

# Custom transform function — mutates the document in place
db.update(lambda doc: doc.update({'processed': True}), where('done') == False)

# Multiple updates at once — list of (fields-or-operation, query) pairs
db.update_multiple([
    ({'int': 2}, where('char') == 'a'),
    ({delete('int')}, where('char') == 'b'),
])
```

### Upsert

Update all documents matching the condition, insert otherwise:

```python
from tinydb import TinyDB, where
from tinydb.table import Document

# Upsert by query
db.upsert({'name': 'Alice', 'score': 100}, where('name') == 'Alice')

# Upsert by explicit document ID
db.upsert(Document({'name': 'Bob', 'score': 50}, doc_id=42))
```

### Document IDs

```python
doc_id = db.insert({'name': 'John'})  # insert returns the ID
doc = db.get(doc_id=1)
doc.doc_id  # every fetched document carries its ID

# update / remove / contains / get all accept doc_id / doc_ids
db.update({'value': 2}, doc_ids=[1, 2])
db.contains(doc_id=1)
db.remove(doc_ids=[1, 2])
db.get(doc_ids=[1, 2])
```

### Tables

```python
users = db.table('users')   # same API as TinyDB itself
users.insert({'name': 'Alice'})
users.search(where('name') == 'Alice')

db.tables()                  # set of all table names
db.drop_table('posts')       # drop one table (irreversible)
db.drop_tables()             # drop all tables

# Default table name — set per instance or for all instances
db.default_table_name = 'my-default'
TinyDB.default_table_name = 'my-default'
```

### In-Memory Database

```python
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

db = TinyDB(storage=MemoryStorage)
```

### Caching Middleware

Batch writes and cache reads to reduce disk I/O:

```python
from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

db = TinyDB('data.json', storage=CachingMiddleware(JSONStorage))

# Writes hit disk after 1000 operations (CachingMiddleware.WRITE_CACHE_SIZE);
# flush manually or on close
db.storage.flush()
db.close()
```

### Query Cache Tuning

Tables keep an LRU query cache (default capacity 10):

```python
table = db.table('big', cache_size=100)   # larger cache
table = db.table('uncached', cache_size=0)  # disable
table = db.table('all', cache_size=None)    # unlimited

table.clear_cache()  # force re-read from storage (e.g. after external changes)
```

### JSON File Options

All constructor arguments except `storage` are forwarded to the storage; for `JSONStorage` they reach `json.dumps`:

```python
db = TinyDB('db.json', sort_keys=True, indent=4, separators=(',', ': '))
```

### MyPy

TinyDB ships a MyPy plugin — enable it in `mypy.ini` / `setup.cfg` via `plugins = tinydb.mypy_plugin`.

## Gotchas

- **`remove()` with no arguments raises `RuntimeError`** — use `db.truncate()` to remove all documents. Same for `get()` without `cond`/`doc_id`/`doc_ids` and `contains()` without `cond`/`doc_id`.
- **`update(fields)` with no condition updates ALL documents** — explicit in 4.9.0; the else-branch updates every document in the table. Always pass `cond` or `doc_ids` unless that is intentional.
- **`update(doc_ids=...)` / `remove(doc_ids=...)` skip missing IDs silently** — 4.9.0 behavior (issue 591). The returned list contains only IDs actually updated/removed; it may be shorter than the input. Previously these raised `KeyError`.
- **Inserting non-Mapping data raises `ValueError`** — `db.insert([1, 2])` fails with "Document is not a Mapping". Any `collections.abc.Mapping` works.
- **Inserting a `Document` with an existing ID raises `ValueError`** — explicit document IDs must be unique.
- **`upsert()` without a query requires a `Document` with `doc_id`** — passing a plain dict without `cond` raises `ValueError`.
- **Comparisons support only literal right-hand values** — `Query().a == Query().b` is not supported; use a callable predicate like `db.search(lambda doc: doc.get('a') == doc.get('b'))`.
- **Parenthesize `&`, `|`, `~` operands** — Python operator precedence parses `~User.name == 'John'` as `(~User.name) == 'John'`.
- **Non-identifier field names need bracket notation** — `User['country-code']`, not `User.country-code`.
- **Property access can collide with query methods** — if a document field is named like a query method (`map`, `test`, `exists`, ...), property syntax breaks; use dict access `Query()['field']` (noted in the changelog for new query methods).
- **`matches()` requires the whole field to match the regex** — use `search()` for substring matching; both accept `flags`.
- **`get(query)` with multiple matches returns an arbitrary document** — use `search()[0]` or a more specific query when order matters.
- **Document IDs are never reused** — auto-incrementing integers that persist across sessions; after removals, new IDs continue from the maximum.
- **Tables are cached** — `db.table('name')` returns the same `Table` instance on repeated calls; a second call with different `cache_size`/`persist_empty` settings has no effect.
- **Empty tables are dropped when empty by default** — pass `db.table('name', persist_empty=True)` to keep an empty table in the storage.
- **Query cache is not invalidated by external changes** — another process modifying the JSON file does not clear the cache; call `clear_cache()` to re-read from storage. Opening multiple `TinyDB` instances on the same file may give unexpected results.
- **Unlimited cache + `test()` queries hold function references** — long-running apps using `lambda` test functions may leak memory with `cache_size=None`.
- **Callables in query APIs execute in-process** — predicates, `test()` functions, and `map()` callables must never be derived from untrusted or user-controlled input.
- **`JSONStorage` forwards `**kwargs` to `json.dumps`** — never pass user-controlled callables (e.g. `default=`, `cls=`); they execute on every write.
- **`JSONStorage` keeps its file handle open until `close()`** — use a context manager or call `db.close()`; with `CachingMiddleware`, flush before close.
- **Concurrent multi-process/thread access is not supported** — TinyDB has no locking; for that use SQLite or an extension like `tinyrecord`.
- **`pip install tinydb==4.9.0` requires Python 3.10+** — 3.8/3.9 support dropped in 4.9.0.

## References

- [01-api-reference](references/01-api-reference.md) — Full API for TinyDB, Table, Document, Query, operations, storages, middlewares
- [02-query-examples](references/02-query-examples.md) — Comprehensive query patterns with worked examples from the docs
- [03-storage-and-middlewares](references/03-storage-and-middlewares.md) — Storage types, custom storage, middleware, extension points
- [04-extensions-and-upgrade](references/04-extensions-and-upgrade.md) — Official extensions ecosystem, when not to use TinyDB, upgrade notes
