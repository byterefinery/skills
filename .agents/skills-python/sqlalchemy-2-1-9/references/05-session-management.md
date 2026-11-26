# Session Management

SQLAlchemy 2.1.9. Source: `orm/quickstart.rst`, `orm/queryguide/dml.rst`, `changelog/migration_21.rst` at tag `rel_2_1_9`.

## Creating Sessions

```python
from sqlalchemy.orm import Session, sessionmaker, scoped_session

# Context manager style (recommended)
with Session(engine) as session:
    session.add(user)
    session.commit()

# Factory with defaults
SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)
session = SessionFactory()

# Thread-local sessions
SessionLocal = scoped_session(sessionmaker(bind=engine))
session = SessionLocal()
SessionLocal.remove()   # clear the thread-local
```

Since 2.1, constructors also accept `execution_options={...}` applied to **all** operations in that session — queries, flushes, and eager-loader queries:

```python
session = Session(
    engine,
    execution_options={"schema_translate_map": {None: "my_schema"}},
)
```

## Unit of Work and State

- `session.add(obj)` / `session.add_all([...])` — mark for INSERT on next flush (INSERT is not emitted yet).
- Mutating loaded objects marks them dirty automatically (attribute events fire).
- `session.flush()` — emit pending INSERT/UPDATE/DELETE SQL **without** committing (gets generated IDs, validates).
- `session.commit()` — flush, then commit the transaction; expires all instances by default.
- `session.rollback()` — flush nothing; roll back the transaction and expire objects.
- `session.expunge(obj)` — detach without deleting; `session.close()` — release the transaction, detach all.
- Object states: transient (unsaved) → pending (added) → persistent (flushed) → detached (expired/closed).

## Expiration

- `expire_on_commit=True` (default): after commit, all attribute values expire; next access re-SELECTs. Set `expire_on_commit=False` when you keep using objects after commit (common for async and web requests).
- `session.expire(obj)` / `session.expire_all()` — force expiration to free memory.

## Loading

```python
user = session.get(User, 1)                          # by primary key
user = session.get(User, (1, "aux"))                 # composite PK
users = session.scalars(select(User).where(User.name.in_(["a", "b"]))).all()

# session.execute returns rows (tuples); .scalars() yields single-entity results
row = session.execute(select(User)).one()            # row: (User,)
obj = session.execute(select(User)).scalar_one()     # the User itself
```

## Bulk ORM DML

`session.execute` with Core DML bypasses per-object unit of work (no cascades, no attribute events on other objects) but is fast:

```python
from sqlalchemy import delete, insert, update

session.execute(insert(User), [{"name": "u1"}, {"name": "u2"}, {"name": "u3"}])
session.execute(insert(User).returning(User.id))          # server-generated values
session.execute(update(User).where(User.name == "u1").values(fullname="U1"))
session.execute(delete(User).where(User.name == "u1"))
```

For joined-inheritance / multi-table mappings, prefer unit-of-work deletes/updates unless performance demands raw DML (a per-table DELETE must be emitted manually for each table).

## 2.1 Autoflush Behavior

As of 2.1, the session **unconditionally autoflushes before every execute** — including raw `text()` statements. In 2.0 only ORM statements triggered the autoflush. Don't rely on a `text()` read skipping the flush.

## Transactions with Sessions

- The session participates in the current transaction; `session.begin()` / `async with session.begin()` delimits explicit units (nested begin = savepoint).
- `session.in_transaction()` — check state.
- Savepoints: `with session.begin_nested():` (2.0+ name; `session.connection().begin_nested()` for Core).
