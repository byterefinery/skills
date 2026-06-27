---
name: sqlalchemy-2-0-51
description: >
  SQLAlchemy 2.0 ORM and Core toolkit for Python database access. Use this skill whenever the user
  mentions SQLAlchemy, ORM models, database queries, engine creation, session management, declarative
  mappings, relationships (one-to-many, many-to-many), connection pooling, async database access,
  SQL expression construction, or any Python database abstraction task. Covers both Core (expression
  language) and ORM layers. Supports PostgreSQL, MySQL/MariaDB, SQLite, Oracle, Microsoft SQL Server,
  and third-party dialects (CockroachDB, IBM DB2, Firebird, SAP HANA, etc.).
metadata:
  tags:
    - orm
    - database
    - python
---

# sqlalchemy 2.0.51

SQLAlchemy is the Python SQL toolkit and Object-Relational Mapping (ORM) library. Version 2.0 introduced a major API redesign with `select()`, `insert()`, `update()`, `delete()` as core entry points, first-class async support, and improved type hints using `Mapped[]`.

## Overview

SQLAlchemy provides two layers:

- **Core** — SQL expression language, connection management, schema definition. Works directly with SQL constructs (`select`, `insert`, `join`, CTEs, etc.) without ORM.
- **ORM** — Object-relational mapping built on top of Core. Declarative class definitions, relationships, sessions, lazy loading strategies.

Both layers share the same engine, connection pool, and type system. You can mix Core and ORM in the same project.

### Supported Databases

SQLAlchemy ships with built-in dialects for these database backends:

| Database | Dialect Name | Drivers |
|---|---|---|
| PostgreSQL | `postgresql` | `psycopg`, `psycopg2`, `pg8000`, `asyncpg` (async) |
| MySQL | `mysql` | `pymysql`, `mysqldb`, `mysqlconnector`, `mariadb`, `asyncmy` (async), `aiomysql` (async) |
| MariaDB | `mariadb` | `mariadb`, `mariadbconnector`, `pymysql` |
| SQLite | `sqlite` | `pysqlite` (built-in `sqlite3`), `aiosqlite` (async), `pysqlcipher` (encrypted) |
| Oracle | `oracle` | `oracledb`, `cx_oracle` |
| MS SQL Server | `mssql` | `pyodbc`, `pymssql`, `aioodbc` (async) |

Third-party dialects extend support to: CockroachDB, IBM DB2, Firebird, SAP HANA, ClickHouse, Snowflake, BigQuery, SQLite via ODBC, and more. Install them as separate packages (e.g., `cockroachdb`, `ibm_db_sa`).

Connection URL format: `{dialect}+{driver}://{user}:{password}@host:{port}/{database}`

### Key Design Principles

- **Eagerly execute Core constructs** — `engine.execute(select(...))` returns results immediately.
- **Sessions manage object state** — The ORM `Session` tracks identity, changes, and relationships.
- **Declarative is the standard** — Use `DeclarativeBase` with `Mapped[]` type hints for modern mappings.
- **Async is first-class** — `AsyncEngine` and `AsyncSession` use `asyncpg`, `asyncmy`, or `aiosqlite`.

## Usage

### Quick Start: Core (No ORM)

```python
from sqlalchemy import create_engine, select, insert, text
from sqlalchemy.engine import Engine

engine = create_engine("sqlite:///example.db")

# Raw SQL
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 1})
    row = result.fetchone()

# Expression language
stmt = select(User).where(User.id == 1)
with engine.connect() as conn:
    result = conn.execute(stmt)
    user = result.scalar_one_or_none()
```

### Quick Start: ORM (Declarative)

```python
from sqlalchemy import create_engine, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    addresses: Mapped[list["Address"]] = relationship(back_populates="user")

class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")

engine = create_engine("sqlite:///example.db")
Base.metadata.create_all(engine)

with Session(engine) as session:
    user = User(name="alice", addresses=[Address(email="a@b.com")])
    session.add(user)
    session.commit()

    stmt = select(User).where(User.name == "alice")
    user = session.execute(stmt).scalar_one()
```

### Quick Start: Async ORM

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/dbname")
async_session = sessionmaker(engine, class_=AsyncSession)

async with async_session() as session:
    stmt = select(User).where(User.id == 1)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
```

## Gotchas

- **`session.add()` does not emit INSERT** — It schedules the insert. `session.flush()` sends SQL to the database; `session.commit()` flushes and commits the transaction. Call `flush()` explicitly if you need the INSERT before commit (e.g., to get a generated primary key).
- **`Session.execute(select(...))` vs `engine.execute(select(...))`** — Session-scoped execution auto-applies expiration rules and participates in the unit of work. Engine-level execution is raw Core with no ORM tracking. Use session for ORM objects, engine for pure Core queries.
- **Relationships default to lazy loading** — Accessing a relationship attribute triggers a separate SQL query (N+1 problem). Use `selectinload()` or `joinedload()` in the options of `select()` to eagerly load relationships. In 2.0+, `raiseload()` is the default for expired attributes, so unexpected lazy loads raise `LazyLoadError`.
- **`Mapped[list[Child]]` vs `Mapped[set[Child]]`** — The collection type in the annotation determines the Python collection used at runtime. Use `list` for ordered, `set` for unique, or `mapped_collection()` for dict-like mappings keyed by attribute.
- **Foreign keys need explicit `ForeignKey`** — SQLAlchemy does not infer relationships from matching column names alone. Always declare `ForeignKey("table.column")` on the child side and `relationship()` on both sides with `back_populates`.
- **Connection pooling is enabled by default** — `QueuePool` is used for most backends. For SQLite, use `StaticPool` with `check_same_thread=False` for in-memory databases shared across threads, or `NullPool` to disable pooling. For production PostgreSQL, tune `pool_size` and `max_overflow`.
- **`create_all()` vs `alembic`** — `Base.metadata.create_all(engine)` creates tables that don't exist but does not alter existing ones. Use Alembic for schema migrations in production.
- **Async sessions are not thread-safe** — Each async task should use its own `AsyncSession`. Do not share an `AsyncSession` across tasks or threads. Use `sessionmaker()` to create fresh sessions per request.
- **Type decorators need `process_bind_param` and `process_result_value`** — When writing custom `TypeDecorator`, implement both methods. `process_bind_param` transforms Python → database, `process_result_value` transforms database → Python.

## References

- [01-engine-connections](references/01-engine-connections.md) — Engine creation, URL format, connection pooling
- [02-core-expressions](references/02-core-expressions.md) — Core SQL expression language (SELECT, INSERT, UPDATE, DELETE, JOINs)
- [03-schema-definition](references/03-schema-definition.md) — Table, Column, MetaData, constraints, indexes, reflection
- [04-declarative-orm](references/04-declarative-orm.md) — DeclarativeBase, Mapped[], mapped_column, registry
- [05-session-management](references/05-session-management.md) — Session lifecycle, transactions, flush/commit, scoped_session
- [06-relationships](references/06-relationships.md) — One-to-many, many-to-one, many-to-many, back_populates, cascade
- [07-query-loading](references/07-query-loading.md) — joinedload, selectinload, subqueryload, defer, load_only, raiseload
- [08-type-system](references/08-type-system.md) — Built-in types, TypeDecorator, custom types, dialect-specific types
- [09-async-support](references/09-async-support.md) — AsyncEngine, AsyncSession, async drivers, streaming results
- [10-events-listeners](references/10-events-listeners.md) — Event listeners on engines, sessions, mappers, attributes
- [11-extensions](references/11-extensions.md) — hybrid properties, automap, baked queries, mutable, ordering_list
- [12-performance-patterns](references/12-performance-patterns.md) — Bulk operations, connection tuning, query optimization
