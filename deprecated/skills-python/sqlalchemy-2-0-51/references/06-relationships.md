# Relationships

Relationships define how ORM models relate to each other. They are declared with `relationship()` and paired with `ForeignKey` on the child side.

## One-to-Many / Many-to-One

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    # One side: collection of addresses
    addresses: Mapped[list["Address"]] = relationship(back_populates="user")

class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # Many side: single user reference
    user: Mapped["User"] = relationship(back_populates="addresses")
```

### Key Points

- `ForeignKey` goes on the **child** side (the "many" side in one-to-many).
- `relationship()` goes on **both** sides with matching `back_populates`.
- The collection type (`list`, `set`, `dict`) is determined by the `Mapped[]` annotation.
- Foreign key is auto-detected when it references the parent table's primary key.

## Many-to-Many

```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    roles: Mapped[list["Role"]] = relationship(
        secondary="user_roles",
        back_populates="users",
    )

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    users: Mapped[list["User"]] = relationship(
        secondary="user_roles",
        back_populates="roles",
    )

# Association table (no ORM mapping, just Table)
from sqlalchemy import Table, Column
user_roles = Table(
    "user_roles", Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)
```

### Many-to-Many with Extra Columns

When the association table has additional columns, map it as a full ORM class:

```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

class Membership(Base):
    __tablename__ = "memberships"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    joined_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user: Mapped["User"] = relationship(back_populates="memberships")
    role: Mapped["Role"] = relationship()
```

## back_populates vs backref

```python
# back_populates — explicit, recommended (both sides declared)
class Parent(Base):
    children: Mapped[list["Child"]] = relationship(back_populates="parent")

class Child(Base):
    parent: Mapped["Parent"] = relationship(back_populates="children")

# backref — legacy, auto-creates the reverse side
# Avoid in new code; use back_populates instead
class Parent(Base):
    children: Mapped[list["Child"]] = relationship(backref="parent")
```

## Cascade Options

```python
# Default cascade: "save-update, merge"
# — save-update: adding to session cascades
# — merge: session.merge() cascades

# Common cascade configurations
relationship("children", cascade="all, delete-orphan")
# — all: save-update, merge, refresh-expire, expunge, delete
# — delete-orphan: deletes child when removed from parent collection

relationship("profile", cascade="all, delete-orphan", uselist=False)
# One-to-one with orphan deletion

# Cascade on many-to-many (usually default is fine)
relationship("roles", secondary="user_roles")
```

### Cascade Table

| Cascade | Description |
|---|---|
| `save-update` | Persist child when parent is added/modified in session |
| `delete` | Delete child when parent is deleted |
| `delete-orphan` | Delete child when removed from parent (orphaned) |
| `merge` | Cascade `session.merge()` |
| `refresh-expire` | Cascade attribute refresh/expire |
| `expunge` | Cascade `session.expunge()` |
| `all` | All of the above except delete-orphan |

## Self-Referential Relationships

```python
class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"))

    # The manager (one side)
    manager: Mapped["Employee | None"] = relationship(
        remote_side="Employee.id",
        back_populates="subordinates",
    )
    # Subordinates (many side)
    subordinates: Mapped[list["Employee"]] = relationship(back_populates="manager")
```

## Overriding Foreign Key Detection

```python
# When multiple foreign keys exist, specify explicitly
relationship("addresses", foreign_keys=[Address.user_id])

# Using foreign() and remote() for complex joins
relationship(
    "events",
    primaryjoin="and_(Event.start_user_id == User.id, "
                "foreign(Event.start_user_id) == remote(User.id))"
)
```

## Overlapping Joins

```python
from sqlalchemy.orm import overlaps

# When two relationships share the same join path
class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    editor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    owner: Mapped["User"] = relationship(overlaps="editor")
    editor: Mapped["User"] = relationship(overlaps="owner")
```

## Deferred Relationships

```python
# Postpone relationship configuration until mappers are ready
class Parent(Base):
    __tablename__ = "parents"
    id: Mapped[int] = mapped_column(primary_key=True)
    children: Mapped[list["Child"]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Configure after all classes are defined
        if cls.__name__ == "Parent":
            cls.children = relationship("Child", back_populates="parent")
```

## Relationship Configuration Options

| Option | Description |
|---|---|
| `back_populates` | Name of the reverse relationship attribute |
| `cascade` | Cascade behavior string |
| `lazy` | Loading strategy (`"select"`, `"joined"`, `"subquery"`, `"raise"`, `"noload"`) |
| `primaryjoin` | Custom join condition (string or SQL expression) |
| `secondary` | Association table for many-to-many |
| `order_by` | Default ordering for the collection |
| `viewonly` | If True, relationship is read-only |
| `uselist` | If False, scalar instead of collection (one-to-one) |
| `foreign_keys` | Explicit foreign key columns |
| `overlaps` | Name of overlapping relationships |
| `info` | Arbitrary metadata dict |
