# Core SQL Expressions

SQLAlchemy Core provides a full-featured SQL expression language that constructs SQL statements programmatically. All constructs compile to standard SQL and are dialect-aware.

## SELECT Statements

```python
from sqlalchemy import select, column, table, literal, func
from sqlalchemy.sql import and_, or_, not_

# Basic select
stmt = select(column("id"), column("name")).select_from(table("users"))

# With WHERE
stmt = select(User).where(User.age > 18)
stmt = select(User).where(and_(User.age > 18, User.active == True))
stmt = select(User).where(or_(User.name == "alice", User.name == "bob"))
stmt = select(User).where(not_(User.banned == True))

# Chained WHERE (implicit AND)
stmt = select(User).where(User.age > 18).where(User.active == True)

# ORDER BY
stmt = select(User).order_by(User.name.asc())
stmt = select(User).order_by(User.created_at.desc(), User.id.asc())

# LIMIT / OFFSET
stmt = select(User).limit(10).offset(20)

# DISTINCT
stmt = select(User.name).distinct()

# GROUP BY with HAVING
stmt = (
    select(User.department, func.count(User.id))
    .group_by(User.department)
    .having(func.count(User.id) > 5)
)

# Aggregate functions
stmt = select(
    func.count(User.id).label("total"),
    func.avg(User.age).label("avg_age"),
    func.min(User.created_at).label("earliest"),
    func.max(User.created_at).label("latest"),
)

# CASE expression
from sqlalchemy import case
stmt = select(
    User.name,
    case(
        (User.age < 18, "minor"),
        (User.age < 65, "adult"),
        else_="senior",
    ).label("age_group"),
)

# Subqueries
subq = select(User.department, func.avg(User.salary).label("avg_sal")).group_by(User.department).subquery()
stmt = select(User.name, subq.c.avg_sal).select_from(
    User.join(subq, User.department == subq.c.department)
)

# CTEs (Common Table Expressions)
dept_stats = (
    select(User.department, func.count(User.id).label("cnt"))
    .group_by(User.department)
    .cte("dept_stats")
)
stmt = select(User.name, dept_stats.c.cnt).join(
    dept_stats, User.department == dept_stats.c.department
)

# Recursive CTEs
with_ = cte.selectable.cte(name="recursive_cte", recursive=True)
```

## INSERT Statements

```python
from sqlalchemy import insert

# Single row
stmt = insert(User).values(name="alice", email="alice@example.com")

# Multiple rows (executemany)
stmt = insert(User)
rows = [{"name": "bob", "email": "b@e.com"}, {"name": "charlie", "email": "c@e.com"}]
conn.executemany(stmt, rows)

# Insert with return (PostgreSQL RETURNING, SQLite RETURNING)
stmt = insert(User).values(name="alice").returning(User.id, User.name)
result = conn.execute(stmt)
new_id = result.inserted_primary_key

# Insert from select
stmt = insert(Archive).from_select(
    [Archive.name, Archive.email],
    select(User.name, User.email).where(User.banned == True),
)

# Bulk insert many values (2.0 feature — batches large inserts efficiently)
engine = create_engine("postgresql://...", insertmanyvalues_page_size=1000)
```

## UPDATE Statements

```python
from sqlalchemy import update

# Simple update
stmt = update(User).where(User.id == 1).values(name="alice_updated")

# Multiple columns
stmt = update(User).values(
    name="alice",
    updated_at=func.now(),
    login_count=User.login_count + 1,  # Column reference in value
)

# Update with return
stmt = update(User).where(User.id == 1).values(name="alice").returning(User.name)

# Conditional update
stmt = (
    update(User)
    .where(User.last_login < func.now() - interval(30, "day"))
    .values(active=False)
)
```

## DELETE Statements

```python
from sqlalchemy import delete

# Simple delete
stmt = delete(User).where(User.id == 1)

# Delete with return
stmt = delete(User).where(User.banned == True).returning(User.id, User.name)

# Delete via join (PostgreSQL USING clause)
stmt = (
    delete(User)
    .where(User.id == BannedUser.user_id)
)
```

## JOINs

```python
from sqlalchemy import join, outerjoin

# Using ORM model methods (recommended)
stmt = select(User, Address).join(Address, User.id == Address.user_id)
stmt = select(User).outerjoin(Address).where(Address.email.is_(None))

# Explicit join types
stmt = select(User).join(Address, isouter=True)  # LEFT OUTER JOIN
stmt = select(User).join(Address, User.addresses)  # Auto-detect via relationship

# Multiple joins
stmt = (
    select(User, Order, Item)
    .join(Order, User.id == Order.user_id)
    .join(Item, Order.id == Item.order_id)
)

# Using join() function directly
j = join(users_table, addresses_table, users_table.c.id == addresses_table.c.user_id)
stmt = select(j)

# Self joins
left_alias = aliased(User, name="manager")
stmt = select(User.name, left_alias.name.label("manager_name")).join(
    left_alias, User.manager_id == left_alias.id
)
```

## Set Operations

```python
from sqlalchemy import union, union_all, intersect, except_

# UNION
s1 = select(User.name).where(User.age > 18)
s2 = select(Admin.username).where(Admin.active == True)
stmt = union(s1, s2)

# UNION ALL (duplicates kept)
stmt = union_all(s1, s2)

# INTERSECT
stmt = intersect(s1, s2)

# EXCEPT
stmt = except_(s1, s2)
```

## Text SQL

```python
from sqlalchemy import text

# Raw SQL with bound parameters
result = conn.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 1})

# Multiple parameters
result = conn.execute(
    text("SELECT * FROM users WHERE name = :name AND age > :age"),
    {"name": "alice", "age": 18},
)

# Text as subquery
text_subq = text("SELECT id, name FROM active_users").columns(id=Integer, name=String)
stmt = select(text_subq).where(text_subq.c.id > 100)
```

## Aliases and Column Labeling

```python
from sqlalchemy import alias, literal_column

# Alias a table
users_alias = users_table.alias("u")
stmt = select(users_alias.c.name).where(users_alias.c.active == True)

# Alias ORM models
UserAlias = aliased(User)
stmt = select(User, UserAlias).join(
    UserAlias, User.manager_id == UserAlias.id
)

# Label columns
stmt = select(func.count(User.id).label("total_users"))
```

## Exists and Correlated Subqueries

```python
from sqlalchemy import exists

# EXISTS clause
subq = select(Address.id).where(Address.user_id == User.id).correlate(User).exists()
stmt = select(User.name).where(subq)

# NOT EXISTS
stmt = select(User.name).where(~subq)

# Scalar subquery
avg_salary = (
    select(func.avg(User.salary))
    .correlate(User)
    .scalar_subquery()
)
stmt = select(User.name).where(User.salary > avg_salary)
```

## Compiling Statements

```python
from sqlalchemy import compile

# See the generated SQL
print(stmt.compile(engine, compile_kwargs={"literal_binds": True}))

# Compile for a specific dialect
from sqlalchemy.dialects import postgresql
print(stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))
```
