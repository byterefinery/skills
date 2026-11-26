# Extensions

SQLAlchemy provides several extensions that add functionality beyond the core ORM.

## Hybrid Properties

`hybrid_property`, `hybrid_method`, and `hybrid_expression` define attributes that work at both the class level (SQL expressions) and instance level (Python values).

```python
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

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

# Instance-level use
i = Interval(start=5, end=10)
print(i.length)       # 5
print(i.contains(7))  # True

# Class-level SQL use
stmt = select(Interval).where(Interval.length > 10)
stmt = select(Interval).where(Interval.contains(7))
```

### hybrid_expression

Define a custom SQL expression for the class-level behavior:

```python
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func

class User(Base):
    __tablename__ = "users"
    first_name: Mapped[str]
    last_name: Mapped[str]

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @full_name.inplace.expression
    def full_name_expression(cls):
        return func.concat(cls.first_name, " ", cls.last_name)
```

## Automap

Automatically generate ORM mappings from an existing database schema.

```python
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

Base = automap_base()
engine = create_engine("sqlite:///existing.db")

# Reflect and generate mappings
Base.prepare(engine, reflect=True)

# Access generated classes
User = Base.classes.user
Address = Base.classes.address

# Relationships are auto-generated
session = Session(engine)
user = session.get(User, 1)
print(user.address_collection)  # Auto-named collection
```

### Customizing Automap

```python
Base = automap_base()

# Override relationship naming
Base.configure(
    relationships={
        "user": {
            "addresses": {"backpopulates": "user"},
        },
    }
)

# Add custom attributes to generated classes
from sqlalchemy.orm import column_property

def user_mapper(mapper, class_):
    class_.full_name = column_property(class_.first_name, " ", class_.last_name)

Base.listen("configure", user_mapper)
```

## Baked Queries

Cache query construction for repeated execution with different parameters.

```python
from sqlalchemy.ext.baked import bake, BakedQuery

baked = BakedQuery()

def user_query(user_id):
    return (
        baked(query=select(User).where(User.id == user_id))
    )

# First call: constructs and caches the query template
result1 = session.execute(user_query(1))

# Subsequent calls: reuse cached template with new parameters
result2 = session.execute(user_query(2))
```

### Use Cases

- Repeated query patterns in loops
- API endpoints with the same query structure
- Reduces overhead of query construction

## Mutable Types

Track changes to mutable types (dict, list) that SQLAlchemy wouldn't normally detect.

```python
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy import JSON

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    settings: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSON))
    tags: Mapped[list] = mapped_column(MutableList.as_mutable(JSON))

# Changes to nested values are tracked
user.settings["theme"] = "dark"   # Detected!
user.tags.append("premium")        # Detected!
session.commit()  # UPDATE fires
```

### Custom Mutable Types

```python
from sqlalchemy.ext.mutable import Mutable

class MyDict(Mutable, dict):
    @classmethod
    def coerce_class(cls, value):
        if isinstance(value, dict) and not isinstance(value, Mutable):
            return MyDict.coerce(value)
        return None

    def __setitem__(self, key, value):
        self.changed()
        super().__setitem__(key, value)

    def __delitem__(self, key):
        self.changed()
        super().__delitem__(key)

Column("data", MutableDict.as_mutable(JSON))
```

## Ordering List

Maintain ordered collections with automatic position management.

```python
from sqlalchemy.ext.orderinglist import ordering_list

class Parent(Base):
    __tablename__ = "parents"
    id: Mapped[int] = mapped_column(primary_key=True)
    children: Mapped[list["Child"]] = relationship(
        order_by="Child.position",
        collection_class=ordering_list("position"),
    )

class Child(Base):
    __tablename__ = "children"
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("parents.id"))
    position: Mapped[int]

# List operations auto-update positions
parent.children.append(Child())     # position = len(children)
parent.children.insert(0, Child())  # Shifts other positions
parent.children.pop()               # Updates remaining positions
```

## Association Proxy

Access nested collection items through a proxy attribute.

```python
from sqlalchemy.ext.associationproxy import association_proxy

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    addresses: Mapped[list["Address"]] = relationship(back_populates="user")
    # Proxy to access address emails directly
    email_addresses = association_proxy("addresses", "email")

class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    email: Mapped[str]
    user: Mapped["User"] = relationship(back_populates="addresses")

# Use the proxy
user.email_addresses.append("new@example.com")
print(user.email_addresses)  # ['a@b.com', 'new@example.com']
```

## Indexable

Key-value pair storage with SQL-level key access.

```python
from sqlalchemy.ext.indexable import indexable

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    data = indexable({})  # Empty dict, becomes K/V table

# Query by key
stmt = select(User).where(User.data["role"] == "admin")
```

## Serializer

Serialize/deserialize column values for transport.

```python
from sqlalchemy.ext.serializer import serializable

@serializable
class MyType:
    def __init__(self, value):
        self.value = value

    def __getstate__(self):
        return {"value": self.value}

    def __setstate__(self, state):
        self.value = state["value"]
```
