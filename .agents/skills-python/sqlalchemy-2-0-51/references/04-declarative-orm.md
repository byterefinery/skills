# Declarative ORM

The declarative system is the standard way to define ORM mappings in SQLAlchemy 2.0. Classes inherit from `DeclarativeBase` and use `Mapped[]` type hints for column and relationship annotations.

## DeclarativeBase

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

class Base(DeclarativeBase):
    pass

# Or with metadata configuration
from sqlalchemy import MetaData

class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "pk": "pk_%(table_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "ix": "ix_%(table_name)s_%(column_0_name)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
        }
    )

# Table definition
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
```

### Base Class Options

```python
class Base(DeclarativeBase):
    # Custom table prefix
    # __abstract__ is implicit — Base itself has no __tablename__

    # Register a registry for shared metadata
    registry = None  # Auto-created by DeclarativeBase

# Alternative: declarative_base() (legacy, still works)
from sqlalchemy.orm import declarative_base
Base = declarative_base()
```

## Mapped[] Type Hints

`Mapped[T]` is the standard annotation for ORM-mapped attributes. The type parameter `T` determines the Python type of the attribute value.

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, DateTime, Text, Float
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    # Basic types
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    age: Mapped[int | None] = mapped_column(Integer)  # Optional
    active: Mapped[bool] = mapped_column(default=True)
    bio: Mapped[str | None] = mapped_column(Text)
    balance: Mapped[float | None] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Optional columns (nullable by default when type is T | None)
    middle_name: Mapped[str | None] = mapped_column(String(50))
```

### mapped_column Arguments

| Argument | Description |
|---|---|
| `primary_key` | Part of primary key |
| `nullable` | Allow NULL values |
| `default` | Python-side default value (callable or literal) |
| `server_default` | Database-side default (`FetchedValue`, `func.now()`) |
| `unique` | Unique constraint |
| `index` | Create index |
| `ForeignKey` | Foreign key reference |
| `computed` | Server-generated computed column |
| `identity` | Identity/auto-increment configuration |
| `info` | Arbitrary metadata dict |

```python
# Default as callable
class User(Base):
    __tablename__ = "users"
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

# Server default
class User(Base):
    __tablename__ = "users"
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

# FetchedValue — database generates value, SQLAlchemy reads it back
from sqlalchemy import FetchedValue
class User(Base):
    __tablename__ = "users"
    version: Mapped[int] = mapped_column(default=0, server_default=text("0"))
```

## Multiple Registries

```python
from sqlalchemy.orm import registry

# Create separate registries for different schemas or metadata
registry1 = registry()
registry2 = registry()

Base1 = registry1.generate_base()
Base2 = registry2.generate_base()

class User(Base1):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

class Product(Base2):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)

# Each registry has its own MetaData
Base1.metadata.create_all(engine)
Base2.metadata.create_all(engine)
```

## Deferred Reflection

Define the class structure first, then reflect columns from the database:

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    # Columns will be reflected from the database
    id: Mapped[int]
    name: Mapped[str]

# Reflect after engine is available
Base.metadata.reflect(engine, only=["users"])

# Now User.id and User.name are real columns
```

## Declarative Mixins

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, Integer
from datetime import datetime

class TimestampMixin:
    """Add created_at and updated_at to any model."""
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

class SoftDeleteMixin:
    """Add deleted_at for soft deletes."""
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)

class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
```

## declared_attr

Use `@declared_attr` for dynamic class attributes:

```python
from sqlalchemy.orm import declared_attr

class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

class User(Base):
    # __tablename__ is automatically "users"
    id: Mapped[int] = mapped_column(primary_key=True)

# Dynamic table arguments
class VersionedMixin:
    @declared_attr
    def __table_args__(cls):
        return {"sqlite_autoincrement": True}
```

## Table Arguments (`__table_args__`)

```python
class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", "tenant_id", name="uq_user_email_tenant"),
        {"sqlite_autoincrement": True},
    )

# Schema specification
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

# PostgreSQL partitioning
class Event(Base):
    __tablename__ = "events"
    __table_args__ = {
        "postgresql_partition_by": "RANGE (event_date)"
    }
```

## Inheritance Strategies

### Single Table Inheritance

```python
class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    type: Mapped[str] = mapped_column(String(50))

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "employee",
    }

class Engineer(Employee):
    department: Mapped[str]

    __mapper_args__ = {"polymorphic_identity": "engineer"}

class Manager(Employee):
    team_size: Mapped[int]

    __mapper_args__ = {"polymorphic_identity": "manager"}
```

### Joined Table Inheritance

```python
class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    type: Mapped[str]

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "employee",
    }

class Engineer(Employee):
    __tablename__ = "engineers"
    id: Mapped[int] = mapped_column(ForeignKey("employees.id"), primary_key=True)
    department: Mapped[str]

    __mapper_args__ = {"polymorphic_identity": "engineer"}
```

### Concrete Table Inheritance

```python
class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    __mapper_args__ = {"concrete": True}

class Engineer(Base):
    __tablename__ = "engineers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    department: Mapped[str]

    __mapper_args__ = {"concrete": True}
```

## Column Property and Hybrid Expressions

```python
from sqlalchemy.orm import column_property
from sqlalchemy import func

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]

    # Computed column property (SQL-level)
    full_name = column_property(first_name, " ", last_name)

    # Aggregate column
    order_count = column_property(
        select(func.count(Order.id)).where(Order.user_id == id).correlate_except(Order).scalar_subquery()
    )
```

## mapped_as_dataclass

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, mapped_as_dataclass

class Base(DeclarativeBase):
    pass

@mapped_as_dataclass
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

# User is now a dataclass — supports dataclasses.astuple(), etc.
u = User(id=1, name="alice")
print(dataclasses.asdict(u))
```
