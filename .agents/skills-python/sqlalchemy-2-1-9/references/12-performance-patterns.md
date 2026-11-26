# Performance Patterns

SQLAlchemy 2.1.9. Source: `faq/performance.html` (published 2.1.9 docs), `orm/queryguide/dml.rst`, `changelog/migration_21.rst` at tag `rel_2_1_9`.

## Bulk Operations

### Bulk Insert

```python
from sqlalchemy import insert

# 1. executemany — large batches of rows
conn.executemany(insert(UserTable), [{"name": f"u{i}"} for i in range(10000)])

# 2. insertmanyvalues (2.0+) — automatic batching of many rows into
#    multi-row INSERTs; engine kwarg insertmanyvalues_page_size tunes chunk size
conn.execute(insert(UserTable), [{"name": f"u{i}"} for i in range(10000)])

# 3. ORM unit of work — session.add_all([...]) + flush()
#    (fires events, cascades; slower than the Core paths above)
```

- 2.1: PostgreSQL supports server-side monotonic functions such as `uuidv7()` in batched INSERT operations.

### Bulk Update / Delete (ORM bypass)

```python
from sqlalchemy import delete, update

session.execute(update(User).where(User.active == False).values(active=True))
session.execute(delete(User).where(User.banned == True))
```

Bypasses per-object unit of work (no cascades, no attribute events) — fast. For multi-table (joined inheritance) mappings, unit-of-work operations are preferred unless performance demands raw DML.

### Upsert

- PostgreSQL/SQLite: `insert(User).on_conflict_do_update(index_elements=[...], set_={...})`.
- MySQL: `insert(User).on_duplicate_key_update(...)`.
- Dialect-specific — check the target backend's docs.

## Connection Pool Tuning

```python
engine = create_engine(
    "postgresql://user:pass@localhost/dbname",
    pool_size=20,          # persistent connections
    max_overflow=10,       # burst capacity
    pool_timeout=30,       # seconds to wait for a connection
    pool_recycle=3600,     # recycle to avoid stale connections
    pool_pre_ping=True,    # validate before use (detects dropped connections)
)
```

Guidelines: web apps scale `pool_size` with worker count; async drivers manage their own pools; batch jobs benefit from larger `max_overflow`.

## Query Optimization

### Avoid N+1

```python
# BAD — one query per user's addresses in the loop
for user in session.scalars(select(User)):
    print(user.addresses)

# GOOD — 2 queries total
for user in session.scalars(select(User).options(selectinload(User.addresses))):
    print(user.addresses)
```

### Select Only Needed Columns

```python
from sqlalchemy.orm import load_only
stmt = select(User).options(load_only(User.id, User.name))
```

### Keyset Pagination (better than OFFSET for large datasets)

```python
# OFFSET 10000 LIMIT 20 is slow; keyset:
stmt = select(User).where(User.id > last_seen_id).order_by(User.id).limit(20)
```

### Statement Caching (default since 2.0)

Compiled SQL is cached automatically. Custom types must set `cache_ok = True` or statements using them won't cache.

## Detecting Slow Queries

```python
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)  # or echo=True on create_engine
```

Count queries in tests via `before_cursor_execute`:

```python
from sqlalchemy import event

query_count = 0
@event.listens_for(Engine, "before_cursor_execute")
def count_queries(conn, cursor, statement, parameters, context, executemany):
    global query_count
    query_count += 1
```

## Memory Management

### Stream Large Results

```python
# Core — streaming cursor
with engine.connect() as conn:
    result = conn.execution_options(stream_results=True).execute(select(UserTable))
    for row in result:
        process(row)

# Async
async with async_engine.connect() as conn:
    result = await conn.stream(select(User))
    async for row in result:
        process(row)
```

### Expire to Free Attribute Buffers

```python
session.expire(user)      # single object
session.expire_all()      # everything in the session
```

## Common Anti-Patterns

1. **Loading whole tables into memory** — paginate or stream.
2. **N+1 in loops** — eager-load with `selectinload`.
3. **Commit per object** — batch changes, commit once.
4. **Missing index on FK columns** — `ForeignKey` columns should be indexed.
5. **`SELECT *` when you need two columns** — `load_only` or explicit column projection.
6. **Filtering in Python after loading** — push filters into `where()` before loading.
7. **Using `Query` API** — legacy; use `select()` + `Session.execute`/`scalars`.
