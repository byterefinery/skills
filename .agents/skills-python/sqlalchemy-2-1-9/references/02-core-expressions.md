# Core SQL Expressions

SQLAlchemy 2.1.9. Source: `tutorial/data_insert.rst`, `tutorial/data_select.rst`, `tutorial/data_update.rst` at tag `rel_2_1_9`.

## SELECT

```python
from sqlalchemy import select, func

stmt = select(UserTable)                                   # whole table
stmt = select(UserTable).where(UserTable.c.name == "x")    # WHERE
stmt = select(UserTable).where(UserTable.c.name.in_(["a", "b"]))
stmt = select(UserTable).where(UserTable.c.name == "a").where(UserTable.c.id == 1)  # AND
stmt = select(UserTable).order_by(UserTable.c.id).limit(10).offset(20)
stmt = select(UserTable.c.id, UserTable.c.name)            # column projection
stmt = select(UserTable).group_by(UserTable.c.name).having(func.count(UserTable.c.id) > 1)
stmt = select(UserTable).distinct()

# Subquery / CTE
subq = select(UserTable.c.id).where(UserTable.c.name == "x").scalar_subquery()
stmt = select(UserTable).where(UserTable.c.id == subq)

# EXISTS
from sqlalchemy import exists
stmt = select(UserTable).where(exists(select(AddressTable).where(AddressTable.c.user_id == UserTable.c.id)))

# Set operations
from sqlalchemy import union, union_all, intersect, except_
stmt = union(select(UserTable), select(OtherUserTable))
```

- `select()` takes entities/columns **positionally**: `select(UserTable, AddressTable.c.id)`. No keyword constructor args, no list form.
- Column expressions support `+` (concatenation, e.g. `UserTable.c.name + "@aol.com"`), comparisons, `func.*` aggregates.

## INSERT

```python
from sqlalchemy import insert

stmt = insert(UserTable).values(name="spongebob", fullname="Spongebob Squarepants")
stmt = insert(UserTable).values([{"name": "a"}, {"name": "b"}])   # executemany form
stmt = insert(UserTable).returning(UserTable.c.id)                # generated values (SQLite/PG/MySQL 8)
stmt = insert(AddressTable).from_select(
    [AddressTable.c.email_address], select(UserTable.c.name + "@aol.com")
)  # INSERT ... SELECT
```

- Values go to `.values()`, never to the constructor.
- `result.inserted_primary_key` after execute.

## UPDATE / DELETE

```python
from sqlalchemy import update, delete

stmt = update(UserTable).where(UserTable.c.name == "a").values(fullname="A")
stmt = update(UserTable).values(name=UserTable.c.name + "!")  # expression in SET
stmt = delete(UserTable).where(UserTable.c.name == "a")
stmt = delete(UserTable).where(UserTable.c.id == 1).returning(UserTable.c.name)
```

## JOINs

```python
stmt = select(UserTable, AddressTable).join(AddressTable)            # ON auto-detected
stmt = select(UserTable).join(AddressTable, UserTable.c.id == AddressTable.c.user_id)
stmt = select(UserTable).outerjoin(AddressTable)                     # LEFT OUTER JOIN
stmt = select(UserTable).join(AddressTable).join(TagTable, AddressTable.c.id == TagTable.c.address_id)
```

- Multiple foreign-key paths: pass the ON clause explicitly or `from_` aliases.
- Aliases: `from sqlalchemy import alias; u2 = alias(UserTable)`.

## Text SQL

```python
from sqlalchemy import text

result = conn.execute(text("SELECT * FROM users WHERE name = :name"), {"name": "x"})
result = conn.execute(text("SELECT * FROM users"), [{"name": "a"}, {"name": "b"}])  # executemany
```

## Inspecting Compilation

```python
stmt = insert(UserTable).values(name="x")
compiled = stmt.compile()          # or compile(engine) for dialect-specific SQL
print(stmt)                        # SQL string
print(compiled.params)             # bound parameters
```

## New in 2.1

- `CREATE VIEW` and `CREATE TABLE AS SELECT` support (`CreateView`, `CreateTable` with select).
- Explicit `USING` support for DELETE on MySQL/PostgreSQL.
- Non-integer RANGE window frame clauses (e.g. `RANGE BETWEEN INTERVAL '1 day' ...`).
- Syntax extension hooks for custom SELECT clauses (see `examples/syntax_extensions`).
