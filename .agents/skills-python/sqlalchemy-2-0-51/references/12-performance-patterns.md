# Performance Patterns

Optimization techniques for SQLAlchemy applications, covering bulk operations, connection tuning, query optimization, and common pitfalls.

## Bulk Operations

### Bulk Insert

```python
from sqlalchemy import insert

# Method 1: executemany (recommended for large batches)
stmt = insert(User)
rows = [{"name": f"user_{i}", "email": f"user_{i}@example.com"} for i in range(10000)]
conn.executemany(stmt, rows)

# Method 2: insertmanyvalues (2.0 feature — batches automatically)
engine = create_engine("postgresql://...", insertmanyvalues_page_size=1000)
stmt = insert(User)
conn.execute(stmt, rows)  # Auto-batches into chunks of 1000

# Method 3: Session.add_all + flush
session.add_all([User(name=f"user_{i}") for i in range(1000)])
session.flush()  # Sends all INSERTs at once
```

### Bulk Update

```python
from sqlalchemy import update

# ORM-aware (fires events, tracks changes)
for user in session.execute(select(User).where(User.active == False)).scalars():
    user.active = True
session.commit()

# Raw SQL bulk update (faster, bypasses ORM)
session.execute(
    update(User).where(User.active == False).values(active=True)
)
session.commit()

# Bulk update with executemany
stmt = update(User).returning(User.id)
session.execute(stmt, [{"name": f"new_{i}", "id": i} for i in range(100)])
```

### Bulk Delete

```python
from sqlalchemy import delete

# Raw SQL bulk delete (fast)
session.execute(delete(User).where(User.banned == True))
session.commit()

# With cascade (ORM-aware, slower)
for user in session.execute(select(User).where(User.banned == True)).scalars():
    session.delete(user)
session.commit()
```

### Bulk Save (Insert or Update)

```python
from sqlalchemy import insert

# PostgreSQL: ON CONFLICT DO UPDATE (upsert)
stmt = insert(User).values(name="alice", email="a@b.com")
stmt = stmt.on_conflict_do_update(
    index_elements=["email"],
    set_={"name": stmt.excluded.name},
)
conn.execute(stmt)

# MySQL: ON DUPLICATE KEY UPDATE
stmt = insert(User).values(name="alice", email="a@b.com")
stmt = stmt.on_duplicate_key_update(name=stmt.inserted.name)

# SQLite: ON CONFLICT DO UPDATE
stmt = insert(User).values(name="alice", email="a@b.com")
stmt = stmt.on_conflict_do_update(
    index_elements=["email"],
    set_={"name": stmt.excluded.name},
)
```

## Connection Pool Tuning

```python
engine = create_engine(
    "postgresql://user:pass@localhost/dbname",
    pool_size=20,          # Persistent connections
    max_overflow=10,       # Extra connections under load
    pool_timeout=30,       # Wait timeout for connection
    pool_recycle=3600,     # Recycle after 1 hour (prevents stale connections)
    pool_pre_ping=True,    # Test before use (adds latency but catches broken connections)
)
```

### Pool Size Guidelines

- **Web applications**: `pool_size` = number of worker processes × 2–5
- **Async applications**: Pool is managed differently; rely on driver defaults
- **High-throughput batch jobs**: Increase `max_overflow` for burst capacity
- **Read-heavy workloads**: Consider separate read replicas with their own engines

## Query Optimization

### Avoid N+1 Queries

```python
from sqlalchemy.orm import selectinload, joinedload

# BAD: N+1 — one query per user's addresses
users = session.execute(select(User)).scalars().all()
for user in users:
    print(user.addresses)  # Fires query per iteration

# GOOD: 2 queries total
stmt = select(User).options(selectinload(User.addresses))
users = session.execute(stmt).scalars().all()
```

### Select Only Needed Columns

```python
from sqlalchemy.orm import load_only

# Load only id and name (other columns deferred)
stmt = select(User).options(load_only(User.id, User.name))
users = session.execute(stmt).scalars().all()
```

### Use Scalar Results When Appropriate

```python
# Instead of:
result = session.execute(select(User.id).where(User.name == "alice"))
user_id = result.scalar()

# Same thing, cleaner:
user_id = session.scalar(select(User.id).where(User.name == "alice"))
```

### Pagination with Offset/Limit

```python
stmt = select(User).order_by(User.id).limit(20).offset(40)
users = session.execute(stmt).scalars().all()
```

### Keyset Pagination (Better for Large Datasets)

```python
# Instead of OFFSET 10000 LIMIT 20 (slow), use:
stmt = select(User).where(User.id > last_seen_id).order_by(User.id).limit(20)
users = session.execute(stmt).scalars().all()
```

## Indexing Strategies

```python
from sqlalchemy import Index

# Single column
Column("email", String(255), index=True)

# Composite index (order matters!)
idx = Index("ix_users_active_created", User.active, User.created_at)

# Partial index (PostgreSQL)
idx = Index(
    "ix_active_users_email",
    User.email,
    postgresql_where=User.active == True,
)

# Functional index
idx = Index("ix_users_lower_name", func.lower(User.name))

# Unique index
Column("slug", String(100), unique=True)
```

## Statement Caching

SQLAlchemy 2.0 caches compiled SQL statements by default. Ensure types have `cache_ok = True`:

```python
class MyType(TypeDecorator):
    impl = String
    cache_ok = True  # Enable caching
```

Check cache statistics:

```python
from sqlalchemy import event

@event.listens_for(Engine, "handle_error")
def log_cache(context):
    print(f"Cache hits: {engine._compiled_cache.stats()}")
```

## Eager vs Lazy Loading Trade-offs

| Strategy | Queries | Best For |
|---|---|---|
| `selectinload` | 1 + 1 per relationship | Collections, large result sets |
| `joinedload` | 1 (with JOIN) | Small result sets, one-to-one |
| `subqueryload` | 1 + 1 per relationship | Older databases, complex filters |
| Lazy (`select`) | 1 + N | Single object access, not in loops |

## Detecting Slow Queries

```python
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Or via engine
engine = create_engine("postgresql://...", echo=True)
```

### Query Counting in Tests

```python
from sqlalchemy import event

query_count = 0

@event.listens_for(Engine, "before_cursor_execute")
def count_queries(conn, cursor, statement, parameters, context, executemany):
    global query_count
    query_count += 1

# In tests
def test_no_n_plus_one():
    global query_count
    query_count = 0
    users = get_users_with_addresses()
    assert query_count == 2  # One for users, one for addresses
```

## Memory Management

### Stream Large Results

```python
# Core: streaming cursor
with engine.connect() as conn:
    result = conn.execution_options(stream_results=True).execute(select(User))
    for row in result:
        process(row)

# Async: stream method
async with engine.connect() as conn:
    result = await conn.stream(select(User))
    async for row in result:
        process(row)
```

### Expire Objects to Free Memory

```python
# After processing, expire to free attribute buffers
session.expire(user)

# Or expire all
session.expire_all()
```

## Common Performance Anti-Patterns

1. **Loading everything into memory** — Use pagination or streaming for large datasets.
2. **N+1 queries in loops** — Always use `selectinload` or `joinedload` for collections accessed in loops.
3. **Unnecessary session commits** — Batch changes and commit once, not per object.
4. **Missing indexes on foreign keys** — ForeignKey columns should always be indexed.
5. **SELECT \* patterns** — Use `load_only()` to fetch only needed columns.
6. **Loading deleted objects** — Filter with `where()` before loading; don't load and filter in Python.
