# Engine and Connections

The `Engine` is the starting point for any SQLAlchemy application. It coordinates a `ConnectionPool` and a `Dialect`, which together manage database connectivity and SQL generation.

## Creating an Engine

```python
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# From a connection string (most common)
engine = create_engine("sqlite:///myfile.db")
engine = create_engine("postgresql://user:pass@localhost/dbname")
engine = create_engine("mysql+pymysql://user:pass@host:3306/dbname")
engine = create_engine("oracle+oracledb://user:pass@host:1521/service_name")
engine = create_engine("mssql+pyodbc://user:pass@host/dbname?driver=ODBC+Driver+17+for+SQL+Server")

# From a URL object (programmatically constructed)
url = URL.create(
    drivername="postgresql",
    username="user",
    password="pass",
    host="localhost",
    port=5432,
    database="dbname",
    query={"options": "-c search_path=my_schema"},
)
engine = create_engine(url)

# From a config dictionary (useful with frameworks)
engine = create_engine(
    "postgresql://user:pass@localhost/dbname",
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False,
)
```

### Common `create_engine` Parameters

| Parameter | Default | Description |
|---|---|---|
| `echo` | `False` | Log all SQL statements to stdout via logging |
| `echo_pool` | `False` | Log pool behavior (checkin/checkout) |
| `pool_size` | 5 | Maximum persistent connections in the pool |
| `max_overflow` | 10 | Extra connections allowed beyond pool_size |
| `pool_timeout` | 30 | Seconds to wait for a connection from the pool |
| `pool_recycle` | -1 | Seconds after which a connection is recycled (-1 = never) |
| `pool_pre_ping` | `False` | Test connections with ping before use (detects stale connections) |
| `pool_reset_on_return` | `"commit"` | How to reset connections: `"commit"`, `"rollback"`, or `"none"` |
| `isolation_level` | None | Override default isolation level per connection |
| `connect_args` | `{}` | Extra keyword arguments passed to the DBAPI driver |
| `json_serializer` | `json.dumps` | Custom JSON serializer for JSON/JSONB columns |
| `json_deserializer` | `json.loads` | Custom JSON deserializer for JSON/JSONB columns |
| `execution_options` | `{}` | Default execution options applied to all statements |

## Connection Pooling

SQLAlchemy manages connections through pool implementations. The default is `QueuePool`, which maintains a fixed number of persistent connections and allows overflow.

### Pool Implementations

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool, StaticPool, NullPool, SingletonThreadPool

# QueuePool (default for most backends)
engine = create_engine("postgresql://...", poolclass=QueuePool, pool_size=10)

# StaticPool — connections are never returned to the pool
# Use for in-memory SQLite shared across threads
from sqlalchemy.pool import StaticPool
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# NullPool — no pooling; connections are closed after each use
engine = create_engine("postgresql://...", poolclass=NullPool)

# SingletonThreadPool — one connection per thread
engine = create_engine("sqlite:///file.db", poolclass=SingletonThreadPool)
```

### SQLite Pooling Gotchas

- File-based SQLite: `QueuePool` is the default and works well.
- In-memory SQLite (`:memory:`): Each connection gets its own database. Use `StaticPool` to share a single in-memory database across the application.
- URI filename (`sqlite:///file:path/to/db.db`): Required for absolute paths on Windows.

## Using Connections

```python
from sqlalchemy import text, select

# Context manager — auto-commits or rollbacks
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users"))
    rows = result.fetchall()
    # Explicit commit needed for DML
    conn.execute(text("INSERT INTO users (name) VALUES (:name)"), {"name": "alice"})
    conn.commit()

# Transaction context manager — auto-commits on success
with engine.begin() as conn:
    conn.execute(text("INSERT INTO users (name) VALUES (:name)"), {"name": "bob"})
    # Auto-commits if no exception; rolls back on exception

# Using connection directly from the pool
conn = engine.connect()
try:
    result = conn.execute(select(User))
finally:
    conn.close()  # Returns to pool, does not close DB connection
```

### Connection Execution Methods

```python
from sqlalchemy import text, select, insert

# Execute Core SQL expressions (SELECT, INSERT, UPDATE, DELETE)
result = conn.execute(select(User).where(User.id == 1))

# Execute raw SQL with text()
result = conn.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 1})

# Execute DML
conn.execute(insert(users_table).values(name="alice", email="a@b.com"))

# Bulk execution
conn.executemany(
    insert(users_table),
    [{"name": "alice"}, {"name": "bob"}, {"name": "charlie"}],
)
```

## URL Construction

The `URL` class is an immutable named tuple representing a database connection specification.

```python
from sqlalchemy.engine import URL, make_url

# Parse from string
url = make_url("postgresql+psycopg2://user:pass@host/dbname")
print(url.drivername)  # "postgresql+psycopg2"
print(url.username)    # "user"
print(url.host)        # "host"
print(url.database)    # "dbname"

# Build programmatically
url = URL.create(
    drivername="postgresql",
    username="user",
    password="pass",
    host="localhost",
    port=5432,
    database="mydb",
)

# Modify (returns new URL, original is immutable)
url = url.set(username="newuser")
url = url.update_query_dict({"sslmode": "require"})
```

## Engine Inspection

```python
from sqlalchemy import inspect

inspector = inspect(engine)

# List all tables
tables = inspector.get_table_names(schema="public")

# Get column info for a table
columns = inspector.get_columns("users", schema="public")
for col in columns:
    print(col["name"], col["type"], col["nullable"], col["default"])

# Get foreign keys
fks = inspector.get_foreign_keys("addresses", schema="public")

# Get indexes
indexes = inspector.get_indexes("users", schema="public")

# Get unique constraints
constraints = inspector.get_unique_constraints("users", schema="public")

# Check if table exists
print(inspector.has_table("users"))
```

## Disposal and Shutdown

```python
# Gracefully close all pooled connections
engine.dispose()

# In async
await async_engine.dispose()
```

Call `dispose()` during application shutdown to release database connections. The pool will recreate connections on next use if the engine is still referenced.
