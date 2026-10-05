---
name: aiosqlite-0-22-1
description: AsyncIO interface to the standard library sqlite3 module. Use when writing asynchronous Python code against SQLite with aiosqlite 0.22.1; covers connect, Connection and Cursor proxies, async context managers, async iteration, and sqlite3 re-exports such as Row and register_adapter.
license: MIT
compatibility: Requires Python 3.9+ and the standard library sqlite3; no third-party dependencies
metadata:
  tags:
    - asyncio
    - sqlite
    - database
    - python
---
# aiosqlite 0.22.1

## Overview

aiosqlite is an async bridge to the standard `sqlite3` module. It replicates the `sqlite3` API, but the query and fetch methods are coroutines, so the event loop is not blocked while queries run. Each connection owns a single background thread that executes all operations through a shared queue, serializing them. `Connection` and `Cursor` are proxies over the real `sqlite3` objects and add async context managers that close resources automatically.

The module re-exports `Row`, the `sqlite3` error hierarchy (`Warning`, `Error`, `DatabaseError`, `IntegrityError`, `ProgrammingError`, `OperationalError`, `NotSupportedError`), `paramstyle`, `register_adapter`, `register_converter`, `sqlite_version`, and `sqlite_version_info`, so most `import sqlite3` code ports by swapping the import and adding `await`/`async for`.

Install with `pip install aiosqlite`. No runtime dependencies.

## Usage

### Connecting

```python
import aiosqlite

# Preferred — the context manager closes the connection on exit
async with aiosqlite.connect("app.db") as db:
    await db.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)")
    await db.commit()

# Or explicit, without a context manager
db = await aiosqlite.connect("app.db")
# ...
await db.close()
```

`connect(database, *, iter_chunk_size=64, **kwargs)` accepts a `str`, `Path`, `bytes`, or anything with `__str__` as the database location. Extra keyword arguments are passed through to `sqlite3.connect` (e.g. `timeout`, `uri`, `check_same_thread`). The returned object is awaitable, so `async with aiosqlite.connect(...)` works directly.

### Executing queries

`execute`-family helpers return an object that is both awaitable and an async context manager, so both forms are valid:

```python
cursor = await db.execute("INSERT INTO items (name) VALUES (?)", ["apple"])
async with db.execute("SELECT * FROM items") as cursor:
    async for row in cursor:
        print(row)
```

- `db.execute(sql, parameters=None)` — run one query, returns a `Cursor`
- `db.executemany(sql, parameters)` — one statement, many parameter sets
- `db.executescript(sql_script)` — run a full SQL script
- `db.execute_insert(sql, parameters=None)` — insert and return the `last_insert_rowid()` as a `Row`
- `db.execute_fetchall(sql, parameters=None)` — query and return all rows
- `db.cursor()` — async context manager yielding a fresh `Cursor`
- `db.commit()`, `db.rollback()`

### Fetching rows

```python
async with db.execute("SELECT * FROM items") as cursor:
    row = await cursor.fetchone()      # Optional[Row]
    rows = await cursor.fetchmany(10)   # pass size=None to use cursor.arraysize
    rows = await cursor.fetchall()

# Async iteration fetches in chunks of iter_chunk_size (default 64)
async for row in cursor:
    ...
```

Cursor methods return the cursor itself for chaining; `cursor.close()` closes it. Cursor properties `rowcount`, `lastrowid`, `arraysize`, `description`, and `row_factory` are plain attributes.

### Row access

```python
db.row_factory = aiosqlite.Row          # connection-wide, sync property
# or per-cursor
cursor.row_factory = aiosqlite.Row

async with db.execute("SELECT id, name FROM items") as cursor:
    row = await cursor.fetchone()
    print(row["name"], row[0])          # column name or index access
```

`db.row_factory` and `db.text_factory` are sync get/set properties; `text_factory` receives the raw bytes.

### Advanced features

- `await db.create_function(name, num_params, func, deterministic=False)` — user-defined SQL functions; `deterministic` requires SQLite >= 3.8.3 (raises `NotSupportedError` on older)
- `async for line in db.iterdump()` — dump the database as SQL text lines
- `await db.backup(target, pages=0, progress=None, name="main", sleep=0.250)` — target is an aiosqlite `Connection` or a stdlib `sqlite3.Connection`
- `await db.set_authorizer(callback)` — query access control; the callback takes `(action_code, arg1, arg2, db_name, trigger_name)` and returns `sqlite3.SQLITE_OK`, `SQLITE_DENY`, or `SQLITE_IGNORE`; pass `None` to remove it
- `await db.set_trace_callback(handler)`, `await db.set_progress_handler(handler, n)`
- `await db.enable_load_extension(True)`, `await db.load_extension(path)`
- `await db.interrupt()` — interrupt pending queries

### Connection state (no await)

These are plain properties read from the connection, not coroutines: `db.in_transaction`, `db.isolation_level` (settable to `None` or `"DEFERRED"` / `"IMMEDIATE"` / `"EXCLUSIVE"`), `db.row_factory`, `db.text_factory`, `db.total_changes`.

A single connection can be used from multiple event loops, including loops on different threads.

## Gotchas

- **Close or stop every connection you do not use as a context manager.** Since 0.22.0, `Connection` no longer inherits from `threading.Thread`, so nothing auto-cleans it on garbage collection — a `ResourceWarning` is emitted for any open connection that is collected. Call `await db.close()` (idempotent; it drains the pending operation queue first) or `db.stop()`, a synchronous method (added in 0.22.1) that terminates the background thread even after the event loop has closed.
- **Do not pass `loop=` to `connect()` or `Connection`.** It has been ignored since 0.15.0 and now only emits a `DeprecationWarning`.
- **`execute_insert()` returns a `Row`, not an int.** It executes `SELECT last_insert_rowid()` and returns the single fetched row.
- **`Cursor.connection` is the raw `sqlite3.Connection`, not the aiosqlite proxy.** Do not call async-style methods on it from the event loop.
- **Queries on a closed connection raise `ValueError`** ("Connection closed" for pending cursor operations, "no active connection" for property access).
- **`interrupt()` bypasses the worker thread.** Unlike every other method, it calls the underlying `sqlite3` connection directly on the calling thread instead of queuing the call, which can hit sqlite3 thread-affinity checks depending on how the connection was created.
- **`db.isolation_level = ...` is a plain assignment**, not a coroutine; do not `await` it.

## References

- [aiosqlite documentation](https://aiosqlite.omnilib.dev/en/latest/) — API reference and changelog
- [omnilib/aiosqlite on GitHub](https://github.com/omnilib/aiosqlite) — source repository
