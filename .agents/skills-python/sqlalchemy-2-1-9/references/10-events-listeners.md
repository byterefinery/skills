# Events and Listeners

SQLAlchemy 2.1.9. Source: `core/events.html` (published 2.1.9 docs), `changelog/migration_21.rst` at tag `rel_2_1_9`.

## Event API

```python
from sqlalchemy import event

@event.listens_for(<target>, "<event_name>")
def listener(*args):
    ...
```

`<target>` can be an Engine/Connection/Session/Mapper/class instance or the class itself (global). `append=False` (default) prepends; `append=True` appends; `retval=True` makes the listener return a value used to replace the operation result.

## Engine / Pool Events (2.1.9 doc names)

```python
# Pool-level
@event.listens_for(engine, "connect")            # new DBAPI connection created
def on_connect(dbapi_connection, connection_record):
    cur = dbapi_connection.cursor()
    cur.execute("SET search_path TO my_schema")
    cur.close()

@event.listens_for(engine, "first_connect")     # first connection for this pool
@event.listens_for(engine, "checkout")          # connection taken from pool
@event.listens_for(engine, "checkin")           # connection returned
@event.listens_for(engine, "close")             # connection closed
@event.listens_for(engine, "invalidate")        # pooled connection invalidated
@event.listens_for(engine, "reset")             # session reset on return to pool

# Connection-level
@event.listens_for(engine, "begin")
@event.listens_for(engine, "commit")
@event.listens_for(engine, "rollback")
@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    pass  # context.execution_options available here (2.1: set via Session.execution_options)

@event.listens_for(engine, "after_cursor_execute")
@event.listens_for(engine, "handle_error")      # exception_context: .is_disconnect, .statement, .original_exception
```

## Session Events

```python
@event.listens_for(Session, "before_flush")
def before_flush(session, flush_context, instances):
    for obj in session.new:
        obj.created_at = now()
    for obj in session.dirty:
        obj.updated_at = now()

@event.listens_for(Session, "after_flush")
@event.listens_for(Session, "after_commit")
@event.listens_for(Session, "after_rollback")
@event.listens_for(Session, "before_commit")
```

## Mapper Events (per mapped class)

```python
@event.listens_for(User, "before_insert")
def before_insert(mapper, connection, target): ...

@event.listens_for(User, "after_insert")       # generated values available
@event.listens_for(User, "before_update")
@event.listens_for(User, "after_update")
@event.listens_for(User, "after_delete")
@event.listens_for(User, "after_load")         # after loading from DB
@event.listens_for(User, "init")               # after __init__
```

`@reconstructor` — a method marked with the decorator runs after object load (alternative to `after_load`).

## Attribute Events

```python
@event.listens_for(User.email, "set")
def email_set(target, value, oldvalue, initiator):
    target.email = value.lower().strip() if value else value

@event.listens_for(User.email, "init")
@event.listens_for(User.addresses, "append")
@event.listens_for(User.addresses, "remove")
```

Watch for recursion: setting an attribute inside its own `set` listener re-fires; use the `initiator` object to distinguish internal vs external sets.

## DDL Events

```python
from sqlalchemy import DDL

@event.listens_for(User.__table__, "after_create")
def after_create(target, connection, **kw):
    connection.execute(DDL("CREATE INDEX idx_user_email ON users (email)"))
```

Fires around `create_all`/`drop_all`; also `before_create`, `after_drop`, `before_drop`, and `MetaData`-wide variants.

## Registry Events (new in 2.1)

```python
@event.listens_for(Base, "before_configured")
@event.listens_for(Base, "after_configured")
@event.listens_for(Base, "resolve_type_annotation")
def resolve_custom_type(resolve_type):
    if resolve_type.resolved_type is MyCustomType:
        return MyCustomSQLType()
    return None
```

`before_configured`/`after_configured` complement the same-named Mapper events at registry scope; `resolve_type_annotation` hooks into `Mapped[...]` → SQL type resolution (custom type hierarchies, PEP 695 aliases). Declarative `__declare_first__`/`__declare_last__` now run via registry events (2.1) — they no longer hold permanent references to classes.

## Removal and Introspection

```python
event.remove(target, "event_name", listener_fn)   # remove one
event.contains(target, "event_name", listener_fn) # check
```

## Gotchas

- Listeners registered on a **class** fire for all instances; on an **instance** only for that instance.
- `before_cursor_execute` fires on every statement — keep it cheap (it's the usual query-counting hook for tests).
- Async: sync event listeners work with the async API, but you cannot `await` inside a sync listener; do async work outside the event.
