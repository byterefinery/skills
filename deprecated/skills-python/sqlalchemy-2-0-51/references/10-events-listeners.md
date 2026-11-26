# Events and Listeners

SQLAlchemy's event system allows hooks into engine, session, mapper, and attribute lifecycle events.

## Event API

```python
from sqlalchemy import event

@event.listens_for(<target>, "<event_name>")
def listener_fn(*args, **kwargs):
    ...
```

## Engine Events

```python
from sqlalchemy import event, create_engine

@event.listens_for(Engine, "connect")
def on_connect(dbapi_connection, connection_record):
    """Called when a new DBAPI connection is created."""
    # Set connection-level options
    cursor = dbapi_connection.cursor()
    cursor.execute("SET search_path TO my_schema")
    cursor.close()

@event.listens_for(Engine, "pool_connect")
def on_pool_connect(dbapi_connection, connection_record, connection_proxy):
    """Called when a connection is checked out from the pool."""

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Before SQL execution."""
    context.snippet = statement  # Store for logging

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """After SQL execution."""
    pass

@event.listens_for(Engine, "handle_error")
def handle_error(exception_context):
    """Handle DBAPI errors."""
    if exception_context.is_disconnect:
        print("Connection lost!")
```

### Per-Engine Events

```python
engine = create_engine("postgresql://...")

@event.listens_for(engine, "connect")
def on_connect(dbapi_connection, connection_record):
    # Only fires for this specific engine
    pass
```

## Session Events

```python
from sqlalchemy.orm import Session, SessionEvents

@event.listens_for(Session, "before_flush")
def before_flush(session, flush_context, instances):
    """Before flush — modify objects before SQL is generated."""
    for obj in session.new:
        if hasattr(obj, "created_at"):
            obj.created_at = datetime.utcnow()
    for obj in session.dirty:
        if hasattr(obj, "updated_at"):
            obj.updated_at = datetime.utcnow()

@event.listens_for(Session, "after_flush")
def after_flush(session, flush_context):
    """After flush — objects have IDs but transaction not committed."""
    for obj in session.new:
        print(f"Inserted {obj.__class__.__name__} id={obj.id}")

@event.listens_for(Session, "after_commit")
def after_commit(session):
    """After commit — safe to access generated values."""
    pass

@event.listens_for(Session, "after_rollback")
def after_rollback(session):
    """After rollback."""
    pass

@event.listens_for(Session, "on_exception")
def on_exception(session, exception, execution_state):
    """Session-level exception handler."""
    print(f"Session error: {exception}")
```

## Mapper Events

```python
from sqlalchemy.orm import.MapperEvents, reconstructor

@event.listens_for(User, "before_insert")
def before_insert(mapper, connection, target):
    """Before INSERT for a specific mapped class."""
    target.created_at = datetime.utcnow()

@event.listens_for(User, "before_update")
def before_update(mapper, connection, target):
    """Before UPDATE."""
    target.updated_at = datetime.utcnow()

@event.listens_for(User, "after_insert")
def after_insert(mapper, connection, target):
    """After INSERT — generated values available."""
    print(f"Inserted user {target.id}")

@event.listens_for(User, "after_load")
def after_load(target, loader_identity):
    """After object is loaded from a query."""
    pass

@event.listens_for(User, "init")
def on_init(args, kwargs):
    """Called when __init__ is called (if using @reconstructor)."""
    pass

# @reconstructor — called after loading from database
@reconstructor
def init_on_load(self):
    self._loaded = True
```

## Attribute Events

```python
from sqlalchemy.orm import AttributeEvents

@event.listens_for(User.email, "set")
def email_set(target, value, oldvalue, initiator):
    """Called when User.email is set."""
    if value:
        target.email = value.lower().strip()

@event.listens_for(User.email, "init")
def email_init(target, value, initiator):
    """Called during __init__."""
    pass

@event.listens_for(User.addresses, "append")
def address_append(value, initiator):
    """Called when an Address is appended to User.addresses."""
    print(f"Added address: {value.email}")

@event.listens_for(User.addresses, "remove")
def address_remove(value, initiator):
    """Called when an Address is removed from User.addresses."""
    pass
```

### AttributeEvents API

```python
# Programmatic registration (alternative to decorator)
from sqlalchemy.orm import attributes

def email_set(target, value, oldvalue, initiator):
    target.email = value.lower() if value else value

attributes.event.listen(User, "email", "set", email_set)

# Remove listener
attributes.event.remove(User, "email", "set", email_set)
```

## DDL Events

```python
from sqlalchemy import event, DDL

@event.listens_for(User.__table__, "after_create")
def after_create(target, connection, **kw):
    """Execute custom DDL after table creation."""
    connection.execute(DDL("CREATE INDEX idx_user_email ON users (email)"))

@event.listens_for(MetaData, "before_create")
def before_metadata_create(target, connection, **kw):
    """Before any tables are created."""
    connection.execute(DDL("SET search_path TO my_schema"))
```

## Event Removal

```python
# Remove a specific listener
event.remove(Session, "before_flush", before_flush_fn)

# Remove all listeners for an event
event.contains(Session, "before_flush", before_flush_fn)  # Check first
event.remove(Session, "before_flush")  # Removes all
```

## Event Ordering

Listeners are called in the order they were registered. Use `append=True` (default) or `insert=True` to control order:

```python
@event.listens_for(Session, "before_flush", append=False)
def first_listener(session, flush_context, instances):
    """Called before other listeners."""
    pass
```

## Event Gotchas

- **Avoid infinite loops** — Modifying an attribute in its own `set` listener triggers recursion. Use the `initiator` parameter to detect internal changes.
- **Connection in mapper events** — The `connection` argument in `before_insert`/`before_update` is the active DBAPI connection. You can execute additional SQL, but be careful with transaction state.
- **Performance** — Event listeners add overhead. Avoid heavy computation in frequently-fired events like `before_cursor_execute`.
- **Async compatibility** — Sync event listeners work with async sessions, but you cannot `await` inside a sync listener. Use async-compatible patterns or handle async work outside the event.
