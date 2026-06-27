# Session Management

The `Session` is the ORM's central interface. It manages object identity, change tracking, transactions, and query execution.

## Creating Sessions

```python
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

engine = create_engine("sqlite:///example.db")

# Create a session factory
SessionFactory = sessionmaker(bind=engine)
session = SessionFactory()

# Or use the context manager pattern (recommended)
with Session(engine) as session:
    user = User(name="alice")
    session.add(user)
    session.commit()

# sessionmaker with defaults
SessionFactory = sessionmaker(
    bind=engine,
    expire_on_commit=True,    # Default: True
    autoflush=True,           # Default: True
    autocommit=False,         # Default: False
    info={"app": "myapp"},
)
```

## Session Lifecycle

```
Transient → Persistent → Detached
   (new)      (in session)  (after commit/close)
```

- **Transient**: Object created but not in any session. No database identity.
- **Persistent**: Object added to a session and flushed. Has database identity.
- **Detached**: Object was persistent but the session is closed/committed. Retains identity but no session tracking.
- **Deleted**: Object marked for deletion via `session.delete()`.

### State Transitions

```python
from sqlalchemy.orm import object_session, make_transient, make_detached

# Check if object is in a session
print(object_session(user))  # Session or None

# Make a persistent object transient (remove from session without deleting)
make_transient(user)

# Make a persistent object detached
make_detached(user)
```

## Adding Objects

```python
# Add single object
session.add(user)

# Add multiple objects
session.add_all([user1, user2, user3])

# Add via relationship (cascade handles it)
session.add(Address(email="a@b.com", user=user))
```

## Flush and Commit

```python
# flush() — sends pending changes to the database but does not commit
session.flush()  # INSERTs, UPDATEs, DELETEs are sent
# Transaction is still open; can still rollback

# commit() — flushes AND commits the transaction
session.commit()

# rollback() — discards all pending changes
session.rollback()

# Explicit flush without commit (e.g., to get generated IDs)
session.add(user)
session.flush()
print(user.id)  # Available after flush
```

### Flush vs Commit Behavior

- `add()` schedules an INSERT but does not execute it.
- `flush()` executes all pending SQL (INSERTs, UPDATEs, DELETEs) within the current transaction.
- `commit()` calls `flush()` then commits the database transaction.
- If `autoflush=True` (default), queries trigger an implicit `flush()` before execution.

## Querying with Sessions

```python
from sqlalchemy import select

# Execute a Core select
result = session.execute(select(User).where(User.name == "alice"))
user = result.scalar_one_or_none()  # Single scalar or None
user = result.scalar_one()          # Exactly one, raises if 0 or >1
users = result.scalars().all()      # List of objects
users = result.all()                # List of Row tuples

# With ORM options
result = session.execute(
    select(User).options(selectinload(User.addresses)).where(User.active == True)
)
active_users = result.scalars().all()

# get() — load by primary key
user = session.get(User, 1)  # Returns User or None

# get with multiple PKs
row = session.get(Address, (1, "primary"))
```

## Result Methods

```python
result = session.execute(select(User))

# Single object
result.scalar_one_or_none()   # First row's first column, or None
result.scalar_one()            # Exactly one result
result.scalars().all()         # List of ORM objects
result.scalars().first()       # First ORM object or None

# Row tuples
result.all()                   # List of Row
result.first()                 # First Row or None
result.one()                   # Exactly one Row

# Iterate
for row in result:
    print(row.user.name)

# Mapping access
result = session.execute(select(User).execution_options(populate_existing=True))
for row in result.mappings():
    print(row["name"])
```

## Updating and Deleting

```python
# Update an existing object
user = session.get(User, 1)
user.name = "alice_updated"
session.commit()  # Change detected automatically (dirty tracking)

# Delete an object
user = session.get(User, 1)
session.delete(user)
session.commit()

# Bulk update (bypasses ORM event hooks, faster)
from sqlalchemy import update
session.execute(
    update(User).where(User.active == False).values(active=True)
)
session.commit()

# Bulk delete
from sqlalchemy import delete
session.execute(delete(User).where(User.banned == True))
session.commit()
```

## Transactions

```python
# Automatic transaction management (default)
with Session(engine) as session:
    session.add(user)
    session.commit()  # Commits if no exception
    # Auto-rollback on exception

# Explicit transaction control
session = Session(engine)
try:
    session.add(user)
    session.flush()
    session.commit()
except Exception:
    session.rollback()
    raise
finally:
    session.close()

# Nested transactions (savepoints)
with Session(engine) as session:
    with session.begin_nested():
        # This is a savepoint
        session.add(user)
        # Rollback just this savepoint
        session.rollback()  # Rolls back to savepoint, outer tx continues
```

## Expunge and Close

```python
# Remove object from session (becomes detached)
session.expunge(user)

# Remove all objects from session
session.expunge_all()

# Close the session (all objects become detached)
session.close()

# Remove stale/expired objects
session.expire(user, ["addresses"])  # Expire specific attributes
session.expire_all()                  # Expire all attributes
```

## scoped_session (Thread-Local Sessions)

```python
from sqlalchemy.orm import scoped_session, sessionmaker

SessionFactory = sessionmaker(bind=engine)
ScopedSession = scoped_session(SessionFactory)

# Each thread gets its own Session
session = ScopedSession()
session.add(user)
session.commit()

# Remove the session from the scope
ScopedSession.remove()

# Registry configuration
ScopedSession = scoped_session(
    SessionFactory,
    scopefunc=some_scope_function  # Custom scoping function
)
```

## Session Events

```python
from sqlalchemy.orm import Session
from sqlalchemy import event

@event.listens_for(Session, "before_flush")
def before_flush(session, flush_context, instances):
    for obj in session.new:
        if hasattr(obj, "created_at"):
            obj.created_at = datetime.utcnow()

@event.listens_for(Session, "after_commit")
def after_commit(session):
    # Safe to access generated values
    for obj in session.new:
        print(f"Created {obj.__class__.__name__} with id={obj.id}")
```

## Session Configuration Options

| Option | Default | Description |
|---|---|---|
| `expire_on_commit` | `True` | Expire all attributes after commit (reload on next access) |
| `autoflush` | `True` | Auto-flush before queries |
| `autocommit` | `False` | If True, each statement is its own transaction (legacy) |
| `bind` | `None` | Engine or dict of bind keys to engines |
| `twophase` | `False` | Use two-phase commit for distributed transactions |
