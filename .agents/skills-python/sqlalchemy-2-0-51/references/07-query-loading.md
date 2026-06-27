# Query Loading Strategies

SQLAlchemy provides several strategies for loading related objects. Choosing the right strategy is critical for performance, especially avoiding the N+1 query problem.

## Default: Lazy Loading (`select`)

By default, relationships use lazy loading — a separate SELECT fires when the attribute is first accessed.

```python
users = session.execute(select(User)).scalars().all()
for user in users:
    print(user.addresses)  # Fires a new query per user (N+1!)
```

This is the **N+1 problem**: one query to load users, then N queries to load each user's addresses. Use eager loading strategies to avoid this.

## selectinload — SELECT IN (Recommended Default)

Issues a second SELECT using `IN` clause to load related objects in a single query.

```python
from sqlalchemy.orm import selectinload

stmt = select(User).options(selectinload(User.addresses))
users = session.execute(stmt).scalars().all()
# 2 queries: one for users, one for all addresses (WHERE user_id IN (...))
for user in users:
    print(user.addresses)  # No additional query
```

### Nested selectinload

```python
stmt = select(User).options(
    selectinload(User.addresses).selectinload(Address.tags)
)
# Loads users, their addresses, and address tags in 3 queries
```

### Advantages
- Works well with large result sets
- Handles pagination naturally
- No cartesian product

## joinedload — JOIN

Uses a LEFT OUTER JOIN to load related objects in the same query.

```python
from sqlalchemy.orm import joinedload

stmt = select(User).options(joinedload(User.addresses))
users = session.execute(stmt).scalars().all()
# 1 query with LEFT OUTER JOIN
```

### Advantages
- Single query (no round-trip for related data)
- Good for small result sets

### Disadvantages
- Cartesian product: if a user has many addresses, rows are duplicated
- Can produce very large result sets with nested joins
- Pagination (`LIMIT`/`OFFSET`) applies to joined rows, not distinct parents

## subqueryload — Subquery

Issues a second SELECT as a subquery filtered by parent primary keys.

```python
from sqlalchemy.orm import subqueryload

stmt = select(User).options(subqueryload(User.addresses))
users = session.execute(stmt).scalars().all()
# 2 queries: one for users, one subquery for addresses
```

### Advantages
- No cartesian product
- Works with older databases that don't support `IN` well

## raiseload — Raise on Access (2.0 Default for Expired)

Prevents lazy loading entirely. Accessing an unloaded relationship raises `LazyLoadError`.

```python
from sqlalchemy.orm import raiseload

# Per-relationship
stmt = select(User).options(raiseload(User.addresses))

# Global default
stmt = select(User).execution_options(_sa_orm_option={"lazyload_strategy": "raise"})

# Via Session
session = Session(engine, lazyload_strategy="raise")
```

### Use Case
- Catch N+1 bugs in testing by making lazy loads fail loudly
- Production safety: prevent unexpected queries

## noload — Leave Unloaded

Attribute is never loaded. Accessing it returns `UNLOADABLE` sentinel.

```python
from sqlalchemy.orm import noload

stmt = select(User).options(noload(User.addresses))
# user.addresses will always raise — never loaded
```

## defaultload — Force Default Strategy

Override a globally configured loading strategy for a specific relationship.

```python
from sqlalchemy.orm import defaultload

# If global default is raiseload, force lazy on this one
stmt = select(User).options(defaultload(User.addresses))
```

## defer — Defer Column Loading

Do not load a specific column. It loads only when accessed.

```python
from sqlalchemy.orm import defer

stmt = select(User).options(defer(User.bio))
user = session.execute(stmt).scalar_one()
print(user.name)   # Already loaded
print(user.bio)    # Fires a separate query to load bio
```

### Use Case
- Skip loading large text/blob columns when not needed
- Improve query performance for list views

## undefer — Load a Deferred Column

```python
from sqlalchemy.orm import undefer

# If bio is deferred by default, load it explicitly
stmt = select(User).options(undefer(User.bio))
```

## load_only — Only Load Specific Columns

```python
from sqlalchemy.orm import load_only

stmt = select(User).options(load_only(User.id, User.name))
# Only loads id and name; other columns are deferred
users = session.execute(stmt).scalars().all()
```

## with_loader_criteria — Global Loader Filter

Apply a loading strategy to all relationships matching a criterion.

```python
from sqlalchemy.orm import with_loader_criteria, raiseload

# Raise on all lazy-loaded collections
stmt = select(User).options(
    with_loader_criteria(
        Relationship,
        raiseload(),
        include_relationships=True,
    )
)
```

## Combining Options

```python
from sqlalchemy.orm import selectinload, joinedload, defer, load_only

stmt = select(User).options(
    selectinload(User.addresses),           # Eager load addresses
    joinedload(User.profile),               # JOIN for profile (always 1:1)
    defer(User.bio),                        # Defer large text column
    load_only(User.id, User.name, User.email),  # Only load these columns
)
```

## Loading Strategy Decision Guide

| Scenario | Recommended Strategy |
|---|---|
| List view with related collections | `selectinload` |
| Single object with few related items | `joinedload` |
| One-to-one relationships | `joinedload` |
| Large result sets with pagination | `selectinload` |
| Catching N+1 bugs in tests | `raiseload` |
| Skipping large columns | `defer` / `load_only` |
| Deeply nested relationships | `selectinload` (avoids cartesian explosion) |

## The Load Object (2.0+)

The `Load` object provides a fluent API for configuring loading:

```python
from sqlalchemy.orm import Load

stmt = select(User).options(
    Load(User).options(
        selectinload(User.addresses),
        joinedload(User.profile),
    ).load_only(User.id, User.name)
)
```
