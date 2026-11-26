# Query Loading Strategies

SQLAlchemy 2.1.9. Source: `orm/quickstart.rst`, `examples/asyncio/async_orm.py`, 2.0/2.1 migration guides at tag `rel_2_1_9`.

The default relationship loading strategy is **lazy** (`lazy="select"`): first access to the attribute emits a SELECT (the quickstart calls this out explicitly — `patrick.addresses` fired a SELECT). The N+1 problem is one query for the parents plus one per parent; use eager loaders to collapse it.

## Eager Loaders (options on `select`)

```python
from sqlalchemy.orm import joinedload, selectinload, subqueryload

# SELECT IN — two queries total; the usual choice for collections
stmt = select(User).options(selectinload(User.addresses))

# LEFT OUTER JOIN — one query; pair with Result.unique()
stmt = select(User).options(joinedload(User.addresses))
users = session.execute(stmt).unique().scalars().all()

# Subquery — two queries, no cartesian product
stmt = select(User).options(subqueryload(User.addresses))
```

### Trade-offs

- `selectinload` — works with large result sets and pagination; no row duplication; recommended default for collections and for async (mandatory — no implicit lazy load in `AsyncSession`).
- `joinedload` — single round-trip; row multiplication (cartesian product) when a parent has many children; `LIMIT`/`OFFSET` apply to joined rows, so use `selectinload` when paging collections.
- `subqueryload` — middle ground; second query filtered by parent PKs.

Nested eager loading chains the loader: `selectinload(User.addresses).selectinload(Address.tags)` → 3 queries.

## Preventing / Controlling Lazy Loads

```python
from sqlalchemy.orm import noload, raiseload, lazyload, defaultload

stmt = select(User).options(raiseload(User.addresses))   # access raises — find N+1 in tests
stmt = select(User).options(noload(User.addresses))     # never loaded; attribute stays unloaded
stmt = select(User).options(lazyload(User.addresses))   # force lazy even if global default differs
stmt = select(User).options(defaultload(User.addresses))  # revert to the mapper default
```

`raiseload("*")` applies to all relationships under a path. Note the 2.1 rule change: when the same object is loadable via multiple query paths, loader options apply from the **shallowest** path (deterministic since 2.1; 2.0 varied by loader strategy).

## Column-Level Loading

```python
from sqlalchemy.orm import defer, undefer, load_only

stmt = select(User).options(defer(User.bio))            # load bio lazily on access
stmt = select(User).options(undefer(User.bio))         # load a by-default-deferred column
stmt = select(User).options(load_only(User.id, User.name))  # everything else deferred
```

Use for large text/blob columns on list views.

## Global Loader Filters

```python
from sqlalchemy.orm import with_loader_criteria

stmt = select(User).options(
    with_loader_criteria(Address, raiseload(), include_aliases=True)
)
```

Applies a loader option to every occurrence of the entity in the query (including joined/subquery occurrences).

## Decision Guide

| Scenario | Strategy |
|---|---|
| List view with related collections | `selectinload` |
| One-to-one / small fixed related set | `joinedload` (+ `.unique()`) |
| Paging parents with collections | `selectinload` (avoid joined + LIMIT) |
| Catching N+1 in tests | `raiseload` |
| Large text/blob columns | `defer` / `load_only` |
| Async code | eager loaders only (`selectinload` typical) |

## Result Object Rules (applies to all queries)

- `session.execute(select(Entity))` → rows (tuples); `.scalars()` for single-entity.
- Rows are **not uniquified** — after `joinedload` on collections call `.unique()`.
- `first()` does not add `LIMIT 1` — add `.limit(1)` yourself.
- Accessors: `.one()`, `.one_or_none()`, `.scalar_one()`, `.scalar_one_or_none()`, `.all()`, `.first()`, `.tuples()`.
