# Schema Definition (Core)

SQLAlchemy 2.1.9. Source: `tutorial/metadata.rst` at tag `rel_2_1_9`.

## Table Construction

```python
from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table

metadata_obj = MetaData()

user_table = Table(
    "user_account",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(30), nullable=False),
    Column("fullname", String),          # nullable by default
)
```

- Column access: `user_table.c.name`, `user_table.c.keys()`, `user_table.primary_key`.
- Column arguments: `primary_key`, `nullable`, `unique`, `index`, `default` (Python-side), `server_default` (SQL-side), `autoincrement`, `onupdate`, `comment`.

### New in 2.1 — TypedColumns

Type-checker-friendly table definitions using a typed base:

```python
from sqlalchemy import Named, TypedColumns, Table

class user_cols(TypedColumns):
    id: Named[int] = Named(primary_key=True)
    name: Named[str] = Named(length=30)

typed_user_table = Table("user_account", other_meta, user_cols)
```

## MetaData

```python
metadata_obj = MetaData()
metadata_obj.create_all(engine)    # emit CREATE TABLE for all tables
metadata_obj.drop_all(engine)
# create_all only creates tables that don't exist; it does not ALTER existing ones —
# use Alembic for production migrations
```

- Naming conventions for constraints: `MetaData(naming_convention={...})`.
- `MetaData(schema="myschema")` prefixes all tables with the schema.
- The ORM `DeclarativeBase` exposes its `MetaData` as `Base.metadata` — `Base.metadata.create_all(engine)` creates every mapped table.

## Constraints and Indexes

```python
from sqlalchemy import CheckConstraint, Index, UniqueConstraint

# Table-level
Table("t", meta,
    Column("a", Integer), Column("b", Integer),
    CheckConstraint("a > 0"),
    UniqueConstraint("a", "b"),
    Index("ix_t_a_b", "a", "b"),
)
```

- Partial indexes (PostgreSQL): `Index("ix", col, postgresql_where=condition)`.
- DDL events on tables run custom DDL around `create_all`/`drop_all`.

## Reflection

```python
metadata_obj = MetaData()
metadata_obj.reflect(bind=engine)              # reflect all tables
metadata_obj.reflect(bind=engine, only=["user_account"])
# or per-table:
user_table = Table("user_account", metadata_obj, autoload_with=engine)
```

The ORM has `DeferredReflection` (`registry.map_imperatively` after reflect) and automap (see [11-extensions](11-extensions.md)).

## Sequences / Identity (PostgreSQL)

```python
from sqlalchemy import Sequence

Column("id", Sequence("user_id_seq", start=1), primary_key=True)
# or SQL-standard IDENTITY on PG 10+ via dialect kwargs
```

SQLite/MySQL autoincrement happens automatically on integer PKs.
