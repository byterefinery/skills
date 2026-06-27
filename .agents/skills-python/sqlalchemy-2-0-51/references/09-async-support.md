# Async Support

SQLAlchemy 2.0 provides first-class async support via `AsyncEngine`, `AsyncSession`, and async-compatible dialects.

## Async Engine

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

# PostgreSQL with asyncpg
engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/dbname")

# MySQL with asyncmy
engine = create_async_engine("mysql+asyncmy://user:pass@localhost/dbname")

# MySQL with aiomysql
engine = create_async_engine("mysql+aiomysql://user:pass@localhost/dbname")

# SQLite with aiosqlite
engine = create_async_engine("sqlite+aiosqlite:///myfile.db")
```

### Async Engine Parameters

Same as sync `create_engine()`, plus:

| Parameter | Description |
|---|---|
| `async_creator` | Async callable returning a driver connection (alternative to URL) |
| `future` | Not needed in 2.0; async is the default for async engines |

## AsyncSession

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# Create session factory
async_session_factory = sessionmaker(engine, class_=AsyncSession)

# Use as async context manager
async with async_session_factory() as session:
    result = await session.execute(select(User))
    user = result.scalar_one()
    await session.commit()
```

### AsyncAttrs Mixin

By default, `AsyncSession` does not allow lazy attribute access. Add `AsyncAttrs` to your base class for async-compatible attribute loading:

```python
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

class Base(AsyncAttrs, DeclarativeBase):
    pass

# Now attributes load lazily via await
async with session() as sess:
    user = await sess.get(User, 1)
    addresses = await user.addresses  # Lazy-loaded via await
```

Without `AsyncAttrs`, use eager loading (`selectinload`, `joinedload`) to avoid lazy loads.

## Async Connection

```python
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text, select

async with engine.connect() as conn:
    result = await conn.execute(text("SELECT * FROM users"))
    rows = await result.fetchall()

# Transaction context
async with engine.begin() as conn:
    await conn.execute(insert(User).values(name="alice"))
    # Auto-commits on success
```

## Async Streaming Results

For large result sets, use streaming to avoid loading everything into memory:

```python
async with engine.connect() as conn:
    result = await conn.stream(select(User))
    async for row in result:
        process(row.user)
```

## Async Engine from Config

```python
from sqlalchemy.ext.asyncio import async_engine_from_config

config = {
    "sqlalchemy.url": "postgresql+asyncpg://user:pass@localhost/dbname",
    "sqlalchemy.pool_size": "10",
}
engine = async_engine_from_config(config, prefix="sqlalchemy.")
```

## Async Inspection

```python
from sqlalchemy.ext.asyncio import AsyncEngine

async with engine.connect() as conn:
    # Use sync inspector on async connection
    from sqlalchemy import inspect
    insp = inspect(await conn.run_sync(lambda c: c))
```

Or use the async-aware approach:

```python
async def get_tables(engine: AsyncEngine):
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        )
        return [row[0] for row in result]
```

## Async Session Patterns

### Request-Scoped Session (Web Frameworks)

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_session():
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# Usage in FastAPI
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one()
```

### Dependency Injection (FastAPI)

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session

@app.get("/users/{user_id}")
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404)
    return user
```

## Async Bulk Operations

```python
from sqlalchemy import insert

# Bulk insert
async with engine.connect() as conn:
    await conn.executemany(
        insert(User),
        [{"name": "alice"}, {"name": "bob"}],
    )
    await conn.commit()
```

## Async dispose

```python
await engine.dispose()
```

Call during application shutdown to release all async connections.

## Async Gotchas

- **No thread safety** — Each async task must use its own `AsyncSession`. Never share an `AsyncSession` across tasks.
- **Lazy loading requires `AsyncAttrs`** — Without it, accessing unloaded attributes raises `PendingRollbackError` or returns unloaded sentinel.
- **`await` everywhere** — Every `execute()`, `commit()`, `rollback()`, and attribute access (with `AsyncAttrs`) must be awaited.
- **Connection pooling differs** — Async engines use `AsyncAdaptedQueuePool` internally, which wraps sync connections for async use. True async drivers (`asyncpg`, `asyncmy`, `aiosqlite`) have native async pools.
- **No `server_side_cursors` on engine** — Use `conn.stream()` instead of setting `server_side_cursors` globally.

## Async Drivers Summary

| Database | Driver | URL Prefix | Package |
|---|---|---|---|
| PostgreSQL | asyncpg | `postgresql+asyncpg` | `asyncpg` |
| MySQL | asyncmy | `mysql+asyncmy` | `asyncmy` |
| MySQL | aiomysql | `mysql+aiomysql` | `aiomysql` |
| SQLite | aiosqlite | `sqlite+aiosqlite` | `aiosqlite` |
| MSSQL | aioodbc | `mssql+aioodbc` | `aioodbc` |
