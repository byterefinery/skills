---
name: sqlalchemy-2-1-9
description: Python SQL toolkit and ORM (SQLAlchemy 2.1.9). Use when working with database code in Python - Core (Engine, Table, select/insert/update/delete, transactions), ORM (DeclarativeBase, Mapped, mapped_column, relationship, Session), async (create_async_engine, AsyncSession, selectinload), or dialects (PostgreSQL, MySQL, SQLite, SQL Server, Oracle).
license: MIT
compatibility: Python 3.11+. pip install sqlalchemy; the asyncio extension needs pip install sqlalchemy[asyncio] (bundles greenlet, not installed by default since 2.1)
---

# sqlalchemy 2.1.9

## Overview

SQLAlchemy 2.1.9 is the Python SQL toolkit and Object-Relational Mapper. It has two integrated APIs over one Engine:

- **Core** — the SQL expression language. `create_engine`, `Table`/`MetaData`, `select`/`insert`/`update`/`delete`, explicit transactions, raw `text()` SQL.
- **ORM** — mapped classes on `DeclarativeBase` with `Mapped` type annotations, `relationship()`, and a `Session` that tracks pending, dirty, and deleted objects (unit of work) and flushes them as SQL.

Both use the same `select()` construct; executing it through a `Session` returns ORM objects, through a `Connection` returns rows. Python 3.11+ is required (`requires-python >=3.11`).

## Usage

Install — plain, or with the asyncio extra (since 2.1 the `greenlet` dependency ships only in this extra):

```bash
pip install sqlalchemy
pip install "sqlalchemy[asyncio]"   # for create_async_engine / AsyncSession
```

Minimal Core path (in-memory SQLite, from the unified tutorial):

```python
from sqlalchemy import Column, Integer, MetaData, Table, create_engine, insert, select

engine = create_engine("sqlite://", echo=True)  # sqlite+pysqlite:///:memory: also works

with engine.begin() as conn:  # one transaction; commits on success
    result = conn.execute(insert(UserTable).values(name="spongebob"))
    print(result.inserted_primary_key)
```

Minimal ORM path (2.x declarative style — this is the only style to write new code in):

```python
from typing import List, Optional
from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    addresses: Mapped[List["Address"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")

engine = create_engine("sqlite://")
Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add(User(name="spongebob", fullname="Spongebob Squarepants"))
    session.commit()

    for user in session.scalars(select(User).where(User.name == "spongebob")):
        print(user)
    patrick = session.get(User, 1)          # load by primary key
```

Minimal async path (from `examples/asyncio/async_orm.py` in the source repo):

```python
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

class Base(AsyncAttrs, DeclarativeBase):
    pass

engine = create_async_engine("postgresql+asyncpg://scott:tiger@localhost/test", echo=True)
session_factory = async_sessionmaker(engine, expire_on_commit=False)

async with session_factory() as session:
    async with session.begin():
        session.add_all([...])
    result = await session.scalars(select(A).options(selectinload(A.bs)))
```

Deeper material lives in the reference files below — mapping details, querying/loaders, Core, asyncio, and the upstream repo's example demos.

## Gotchas

- **Do not use `session.query()`** — the 1.x `Query` API is legacy. Write `session.execute(select(...))` / `session.scalars(...)`, and `session.get(Entity, pk)` instead of `Query.get()`. `select()` also absorbs most `Query` methods (`filter`, `filter_by`, `order_by`, `limit`, `options`, `join`), so migrating a 1.x query is mostly mechanical.
- **`session.execute` returns rows (tuples), not objects** — call `.scalars()` first for a single-entity query (`session.scalars(select(User))`), and `.unique()` before iterating when using `joinedload` on collections, since Result objects no longer deduplicate ORM rows (identity-map uniquification is Query-era behavior).
- **`first()` does not add `LIMIT 1`** — it returns the first row of whatever was fetched. Add `.limit(1)` explicitly if you want the database to stop at one row.
- **Positional constructor args only** — `select(User, Address.id)` not `select(User, Address.id, entity=True)` style kwargs, and DML takes no keyword constructor args: `insert(User).values(name="x")`, never `insert(User, name="x")`.
- **ORM bulk DML via `session.execute`** — `session.execute(insert(User), [{"name": "u1"}, {"name": "u2"}])`, `session.execute(update(User).where(...).values(...))`, `session.execute(delete(User).where(...))`. These bypass the unit of work (no cascades, no attribute events on other objects) but are fast.
- **`expire_on_commit=True` is the default** — after `session.commit()`, all instance attributes expire and reload lazily on next access (extra SELECTs). Pass `expire_on_commit=False` to `Session`/`sessionmaker` if you keep using objects after commit.
- **Lazy loading emits SQL on attribute access** — `user.addresses` on a freshly loaded object fires a SELECT (this is the documented default `lazyload`). In `AsyncSession` that implicit lazy load is not allowed; use eager loaders (`selectinload` is the usual choice) or `AsyncAttrs` + `awaitable_attrs` for deferred access.
- **Use the Session as a context manager** — `with Session(engine) as session:` closes it when done; it holds active DB resources.
- **2.1 changed autoflush to be unconditional** — any `session.execute(...)` (including raw `text()` statements) now autoflushes pending ORM changes first. Don't rely on a `text()` read skipping the flush.
- **2.1 install gotcha** — `create_async_engine` needs the `[asyncio]` extra (`greenlet`); a plain `pip install sqlalchemy` no longer pulls it in.
- **2.1 default drivers** — the default PostgreSQL driver is psycopg 3 (`postgresql://` resolves to `postgresql+psycopg://`), Oracle defaults to python-oracledb, and a new `mssql+mssqlpython` dialect supports Microsoft's `mssql-python` driver.
- **2.1 composites return non-None objects by default** — a `composite()` attribute on a pending object returns `Point(x=None, y=None)` rather than `None`; opt back into None with `return_none_on=lambda *a: all(v is None for v in a)` (automatic if the annotation is `Mapped[Point | None]`).
- **`exclude_properties` is the wrong tool for declared attributes (2.1.5+)** — use the `Unmapped` annotation + `unmapped_column()` to declare a table column that the mapper ignores.
- **Sessions take `execution_options` now (2.1)** — e.g. `Session(engine, execution_options={"schema_translate_map": {None: "my_schema"}})` applies the options to all operations in that session, including flushes.

## References

- [01-engine-connections](references/01-engine-connections.md) — Engine creation, URL format, pooling, 2.0+ transaction rules, inspection
- [02-core-expressions](references/02-core-expressions.md) — Core SQL expression language (SELECT, INSERT, UPDATE, DELETE, JOINs, CTEs, text)
- [03-schema-definition](references/03-schema-definition.md) — Table, Column, MetaData, constraints, indexes, reflection, 2.1 `TypedColumns`
- [04-declarative-orm](references/04-declarative-orm.md) — DeclarativeBase, Mapped[], mapped_column, dataclass mapping (2.1 changes), unmapped_column, inheritance
- [05-session-management](references/05-session-management.md) — Session lifecycle, flush/commit, expiration, bulk DML, 2.1 unconditional autoflush and execution_options
- [06-relationships](references/06-relationships.md) — one-to-many, one-to-one, many-to-many, back_populates (2.1 lambda), cascade, join config
- [07-query-loading](references/07-query-loading.md) — lazy vs selectinload/joinedload/subqueryload, raiseload/noload, defer/load_only, Result rules
- [08-type-system](references/08-type-system.md) — built-in types, Mapped[] coercion, TypeDecorator, dialect-specific types
- [09-async-support](references/09-async-support.md) — create_async_engine, AsyncSession/async_sessionmaker, AsyncAttrs, selectinload, stream(), 2.1 install change
- [10-events-listeners](references/10-events-listeners.md) — engine/pool, session, mapper, attribute, DDL events, 2.1 RegistryEvents
- [11-extensions](references/11-extensions.md) — hybrid properties (2.1 bulk_dml/update_expression), mutable, ordering_list, associationproxy, automap
- [12-performance-patterns](references/12-performance-patterns.md) — bulk operations, pool tuning, N+1, keyset pagination, statement caching
- [13-upstream-examples](references/13-upstream-examples.md) — the SQLAlchemy repo's `examples/` demos (association, inheritance, versioned_history, asyncio, …) with source paths
