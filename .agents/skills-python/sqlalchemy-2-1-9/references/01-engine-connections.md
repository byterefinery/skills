# Engine and Connections

SQLAlchemy 2.1.9. Source: `tutorial/engine.rst`, `core/connections.rst`, 2.0/2.1 migration guides.

## Creating an Engine

```python
from sqlalchemy import create_engine

# URL format: dialect[+driver]://user:password@host:port/database
engine = create_engine("postgresql+psycopg://scott:tiger@pg14/dbname")
engine = create_engine("sqlite:///example.db")        # file database
engine = create_engine("sqlite://", echo=True)        # in-memory; echo logs SQL
engine = create_engine("sqlite+pysqlite:///:memory:") # explicit driver segment
```

The URL encodes: (1) the dialect (database), (2) the optional DBAPI driver (`+driver`; each dialect has a default — since 2.1 PostgreSQL defaults to psycopg 3, Oracle to python-oracledb), (3) the location. The engine connects lazily — `create_engine` never opens a connection.

### Common `create_engine` Parameters

| Parameter | Purpose |
|---|---|
| `echo=True` | Log emitted SQL (shorthand; use `logging` for real apps) |
| `pool_size` / `max_overflow` / `pool_timeout` | QueuePool tuning |
| `pool_recycle` | Seconds before a pooled connection is recycled (avoid stale connections) |
| `pool_pre_ping=True` | Validate connection before use (detects dropped connections) |
| `future` | No longer needed — 2.0-style behavior is the only behavior |

## Connection Pooling

Default pool is `QueuePool` (server backends). Options:

```python
from sqlalchemy.pool import QueuePool, StaticPool, NullPool, SingletonThreadPool

# In-memory SQLite shared across threads (tests)
engine = create_engine(
    "sqlite://",
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

# No pooling — close after each use
engine = create_engine("sqlite:///app.db", poolclass=NullPool)
```

**SQLite in-memory gotcha**: an in-memory DB lives only as long as its connection. Each `engine.connect()` against a fresh connection would see an empty database, so use `StaticPool` (one shared connection) for in-memory SQLite in tests.

## Using Connections — Transaction Rules (2.0+)

Library-level "autocommit" was removed in 2.0. Two supported styles:

```python
# Preferred for writes: one connection, one transaction,
# commits on clean exit, rolls back on exception
with engine.begin() as conn:
    conn.execute(insert(UserTable).values(name="x"))
    conn.execute(update(UserTable).where(UserTable.c.id == 1).values(name="y"))

# "Commit as you go": first execute autobegins a transaction,
# but NOTHING commits automatically — call commit() yourself
with engine.connect() as conn:
    conn.execute(insert(UserTable).values(name="x"))
    conn.commit()
```

- `conn.execute(stmt)` — execute Core expression or `text()`; returns `Result`.
- `conn.executemany(stmt, [dict, ...])` — bulk DML.
- `result.inserted_primary_key` — generated keys after INSERT.
- `conn.commit()` / `conn.rollback()` / `conn.begin()` — explicit transaction control; `conn.begin()` supports nesting via savepoints.

## Result Objects (2.0+)

Rows behave like named tuples: `row.id`, `row["id"]`, `row[0]`. Methods: `.all()`, `.first()`, `.one()`, `.one_or_none()`, `.scalar()`, `.scalar_one()`, `.scalar_one_or_none()`, `.fetchone()`, `.fetchmany(n)`, `.mappings()` (RowMapping access). Results stream — iterate once.

## Inspection (schema discovery)

```python
from sqlalchemy import inspect

insp = inspect(engine)
insp.get_table_names()
insp.get_columns("user_account")
insp.get_foreign_keys("address")
insp.get_indexes("user_account")
has = insp.has_table("user_account")
```

## Disposal

```python
engine.dispose()   # close all pooled connections (e.g. before deleting a SQLite file)
```

## New in 2.1

- `mssql+mssqlpython` dialect — Microsoft's `mssql-python` driver (URL: `mssql+mssqlpython://user:password@hostname/database`).
- `TypedColumns`/`Named` — type-checker-friendly table definition bases (see [03-schema-definition](03-schema-definition.md)).
