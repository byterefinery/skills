# Extensions

SQLAlchemy 2.1.9. Source: `orm/extensions/*.rst` (published 2.1.9 docs), `changelog/migration_20.rst`, `changelog/migration_21.rst` at tag `rel_2_1_9`.

## Hybrid Properties (`sqlalchemy.ext.hybrid`)

Attributes usable both on instances (Python) and on the class (SQL expressions):

```python
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

class Interval(Base):
    __tablename__ = "intervals"
    id: Mapped[int] = mapped_column(primary_key=True)
    start: Mapped[int]
    end: Mapped[int]

    @hybrid_property
    def length(self) -> int:
        return self.end - self.start

    @hybrid_method
    def contains(self, point: int) -> bool:
        return (self.start <= point) & (point <= self.end)

# Instance: i.length, i.contains(7)
# Class/SQL: select(Interval).where(Interval.length > 10)
```

- `.expression` — explicit SQL expression for class-level use.
- `.inplace` — PEP 484-compliant variant (property descriptor on the class).
- `.getter` / `.setter` / `.comparator` — customize instance access and SQL comparison behavior.
- **2.1: `update_expression`** — hook so `update().values({Hybrid: value})` rewrites the SET clause (e.g. `total_price` → `price / (1 + tax_rate)`).
- **2.1: `bulk_dml`** — decorator intercepting the parameter dict for ORM-enabled bulk `insert`/`update`:

```python
@coordinates.inplace.bulk_dml
@classmethod
def _coordinates_bulk_dml(cls, mapping, value):
    mapping["x"] = value.x
    mapping["y"] = value.y
```

- **2.1: `from_dml_column()`** — in an `update_expression`, reference another column's new value from the same UPDATE's SET clause.

## Mutable Types (`sqlalchemy.ext.mutable`)

Track in-place mutations of JSON/dict/list columns:

```python
from sqlalchemy.ext.mutable import MutableDict, MutableList

class User(Base):
    settings: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSON))
    tags: Mapped[list] = mapped_column(MutableList.as_mutable(JSON))

user.settings["theme"] = "dark"   # detected → UPDATE on commit
user.tags.append("premium")       # detected
```

## Ordering List (`sqlalchemy.ext.orderinglist`)

Ordered collections with automatic position maintenance:

```python
from sqlalchemy.ext.orderinglist import ordering_list

class Parent(Base):
    children: Mapped[List["Child"]] = relationship(
        order_by="Child.position",
        collection_class=ordering_list("position"),
    )
```

`append`/`insert`/`pop` on the collection rewrite `position` values for children.

## Association Proxy (`sqlalchemy.ext.associationproxy`)

Proxy a sub-attribute through a relationship:

```python
from sqlalchemy.ext.associationproxy import association_proxy

class User(Base):
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")
    email_addresses = association_proxy("addresses", "email")

user.email_addresses.append("new@example.com")   # acts on the related objects
```

## Indexable (`sqlalchemy.ext.indexable`)

Column-level key/value access: `data = indexable(default_value)` on a class gives `User.data["role"]` attribute access plus `User.data["role"] == "admin"` SQL filtering.

## Serializer (`sqlalchemy.ext.serializer`)

`@serializable` on classes used in ORM mappings makes them pickle-safe across session boundaries.

## Automap (`sqlalchemy.ext.automap`)

Generate mappings from an existing schema:

```python
from sqlalchemy.ext.automap import automap_base

Base = automap_base()
Base.prepare(engine, reflect=True)     # reflect tables AND generate classes/relationships

User = Base.classes.user
session.get(User, 1)
```

- Relationships between reflected tables are auto-generated.
- `Base.classes` maps table name → generated class.

## Baked Queries (`sqlalchemy.ext.baked`)

Superseded: the 2.0 migration guide notes baked queries are superseded by the built-in SQL statement caching system — use statement caching (default since 2.0) instead of caching query construction.

## Association Proxy vs. Custom Logic

Prefer `associationproxy` for simple pass-throughs; for custom SQL on the fly, use `hybrid_property` or a `column_property`.
