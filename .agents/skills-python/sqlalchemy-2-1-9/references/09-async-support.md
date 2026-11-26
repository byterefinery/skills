# Async Support

SQLAlchemy 2.1.9. Source: `examples/asyncio/async_orm.py`, `changelog/migration_21.rst` at tag `rel_2_1_9`.

## Install — 2.1 change

`greenlet` (required by the asyncio extension) is **not** installed with plain `pip install sqlalchemy` since 2.1. Install the extra:

```bash
pip install "sqlalchemy[asyncio]"
```

## Complete Pattern (from upstream `examples/asyncio/async_orm.py`)

```python
import asyncio
from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

class Base(AsyncAttrs, DeclarativeBase):
    pass

class A(Base):
    __tablename__ = "a"
    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[Optional[str]]
    bs: Mapped[List["B"]] = relationship()

class B(Base):
    __tablename__ = "b"
    id: Mapped[int] = mapped_column(primary_key=True)
    a_id: Mapped[int] = mapped_column(ForeignKey("a.id"))

async def main():
    # driver must be async — asyncpg (PG), aiosqlite (SQLite), asyncmy/aiomysql (MySQL)
    engine = create_async_engine("postgresql+asyncpg://scott:tiger@localhost/test", echo=True)

    # DDL runs through run_sync
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # expire_on_commit=False keeps attributes loaded after commit
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with SessionLocal() as session:
        async with session.begin():
            session.add_all([A(bs=[B(), B()], data="a1")])

        # eager loading is mandatory — no implicit lazy load in AsyncSession
        result = await session.scalars(select(A).options(selectinload(A.bs)))
        for a in result:
            print(a)
            for b in a.bs:
                print(b)

        a1 = (await session.scalars(select(A).order_by(A.id))).first()
        a1.data = "new data"
        await session.commit()

        # deferred attribute access goes through awaitable_attrs
        for b in await a1.awaitable_attrs.bs:
            print(b)

asyncio.run(main())
```

## Rules

- `create_async_engine(url)` — same URL scheme as sync; the driver must be an async DBAPI.
- `AsyncAttrs` mixin on the base class enables `awaitable_attrs` for deferred (awaited) access to unloaded attributes/relationships.
- Everything that returns a Result is awaited: `await session.execute(...)`, `await session.scalars(...)`, `await session.stream(...)`.
- `await session.commit()` / `await session.rollback()`; `async with session.begin():` for explicit units.
- **No implicit lazy loading** — accessing an unloaded relationship outside a greenlet context fails; use `selectinload`/`joinedload` in the query, or `await obj.awaitable_attrs.rel`.
- `await session.stream(stmt)` returns a streaming `AsyncResult` for `async for` iteration (large result sets); `await session.scalars(...)` buffers in memory.
- Synchronous-only calls (like `Base.metadata.create_all`) run via `await conn.run_sync(func)`.
- Each async task should use its own `AsyncSession`; don't share one session across tasks/threads.
- `AsyncSession.bind` / `AsyncSession.binds` are always present since 2.1 (previously `AttributeError` when unset).

## Async Drivers

| Backend | Sync driver (2.1 default in parens) | Async driver |
|---|---|---|
| PostgreSQL | psycopg 3 | `asyncpg` |
| MySQL | (varies) | `asyncmy`, `aiomysql` |
| SQLite | pysqlite (stdlib) | `aiosqlite` |
| MSSQL | (pyodbc) | `aioodbc` |
