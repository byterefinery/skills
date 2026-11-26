# Schema Definition

SQLAlchemy's schema system defines tables, columns, constraints, indexes, and other database objects. The `Table` construct is the core building block.

## Table Construction

```python
from sqlalchemy import (
    Table, Column, Integer, String, Boolean, DateTime,
    MetaData, ForeignKey, Text, Float
)

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("email", String(255), unique=True),
    Column("active", Boolean, default=True),
    Column("created_at", DateTime, server_default=func.now()),
)

addresses = Table(
    "addresses", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("users.id"), nullable=False),
    Column("email", String(255)),
    Column("kind", String(50)),
)
```

### Column Arguments

| Argument | Description |
|---|---|
| `primary_key` | If `True`, this column is part of the primary key |
| `nullable` | Whether NULL values are allowed (default: `True`) |
| `default` | Python-side default value (applied before INSERT) |
| `server_default` | Database-side default (e.g., `func.now()`, `FetchedValue()`) |
| `unique` | If `True`, adds a unique constraint |
| `index` | If `True`, creates an index on this column |
| `ForeignKey` | Foreign key reference to another table/column |
| `info` | Arbitrary dict for application-level metadata |

## MetaData

```python
from sqlalchemy import MetaData

# Default (no naming convention)
metadata = MetaData()

# With naming conventions (recommended for constraints)
metadata = MetaData(
    naming_convention={
        "pk": "pk_%(table_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "ix": "ix_%(table_name)s_%(column_0_name)s",
    }
)

# With schema prefix
metadata = MetaData(schema="my_schema")

# Create all tables
metadata.create_all(engine)

# Create only missing tables
metadata.create_all(engine, checkfirst=True)

# Drop all tables
metadata.drop_all(engine)

# Reflect existing database
metadata.reflect(engine)
metadata.reflect(engine, only=["users", "addresses"])
```

## Constraints

```python
from sqlalchemy import CheckConstraint, UniqueConstraint, PrimaryKeyConstraint

# Inline on a column
Column("age", Integer, CheckConstraint("age >= 0"))

# Table-level check constraint
Table(
    "users", metadata,
    Column("age", Integer),
    Column("salary", Float),
    CheckConstraint("salary > 0", name="ck_users_salary_positive"),
)

# Composite unique constraint
Table(
    "events", metadata,
    Column("user_id", Integer),
    Column("event_date", Date),
    UniqueConstraint("user_id", "event_date", name="uq_events_user_date"),
)

# Primary key (usually inline, but can be table-level)
PrimaryKeyConstraint("col1", "col2", name="pk_mytable")
```

## Indexes

```python
from sqlalchemy import Index

# Inline on column
Column("email", String(255), index=True)

# Explicit index
idx = Index("ix_users_email", users_table.c.email, unique=True)
idx = Index("ix_users_name_lower", func.lower(users_table.c.name))  # Functional index

# Composite index
idx = Index("ix_users_active_created", users_table.c.active, users_table.c.created_at.desc())

# Conditional (partial) index — PostgreSQL
from sqlalchemy.dialects.postgresql import INDEX
idx = Index(
    "ix_active_users",
    users_table.c.email,
    postgresql_where=users_table.c.active == True,
)

# Add/remove indexes to a table
users_table.indexes  # Set of all indexes on the table
```

## Sequences and Identity Columns

```python
from sqlalchemy import Sequence, Identity

# PostgreSQL sequence
Column("id", Integer, server_default=Sequence("user_id_seq"))

# PostgreSQL IDENTITY (SQL standard, PG 10+)
Column("id", Integer, Identity(), primary_key=True)

# Auto-increment (SQLite, MySQL default behavior)
Column("id", Integer, primary_key=True, autoincrement=True)
```

## Computed Columns

```python
from sqlalchemy import Computed

# PostgreSQL stored generated column
Column(
    "full_name",
    String(200),
    Computed("first_name || ' ' || last_name"),
)

# Persisted computed (SQL Server)
Column(
    "total",
    Float,
    Computed("quantity * unit_price", persisted=True),
)
```

## Reflection (Schema Discovery)

```python
from sqlalchemy import inspect, MetaData

metadata = MetaData()
metadata.reflect(engine)

# Access reflected tables
for name, table in metadata.tables.items():
    print(name, [col.name for col in table.columns])

# Reflect specific tables
metadata.reflect(engine, only=["users", "orders"])

# Using Inspector
inspector = inspect(engine)
columns = inspector.get_columns("users")
fks = inspector.get_foreign_keys("addresses")
indexes = inspector.get_indexes("users")
pk_constraint = inspector.get_pk_constraint("users")
unique_constraints = inspector.get_unique_constraints("users")
check_constraints = inspector.get_check_constraints("users")
```

## DDL Events

```python
from sqlalchemy import event, DDL

# Execute custom DDL after table creation
event.listen(users_table, "after_create", DDL(
    "CREATE INDEX ix_users_name ON users (name)"
))

# Schema-level events
event.listen(metadata, "before_create", DDL("SET search_path TO my_schema"))
```

## Table Inheritance with Core

Core does not have built-in inheritance like the ORM. Use table-per-hierarchy manually:

```python
base_table = Table(
    "entities", metadata,
    Column("id", Integer, primary_key=True),
    Column("type", String(50)),
)

user_table = Table(
    "users", metadata,
    Column("id", ForeignKey("entities.id"), primary_key=True),
    Column("email", String(255)),
)
```

## Dialect-Specific Types in Core

```python
from sqlalchemy.dialects import postgresql, mysql

# PostgreSQL-specific
Column("data", postgresql.JSONB)
Column("tags", postgresql.ARRAY(String))
Column("addr", postgresql.INET)
Column("range_val", postgresql.INT4RANGE)

# MySQL-specific
Column("data", mysql.JSON)
Column("geom", mysql.GEOMETRY)
```
