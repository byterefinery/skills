# Relationships

SQLAlchemy 2.1.9. Source: `orm/basic_relationships.html` (published 2.1.9 docs), `orm/quickstart.rst`, `changelog/migration_21.rst` at tag `rel_2_1_9`.

## One-to-Many / Many-to-One

```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")

class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")
```

- `ForeignKey` goes on the **many** side (child table); `relationship()` with matching `back_populates` on **both** sides.
- The collection container comes from the annotation: `Mapped[List[...]]`, `Mapped[Set[...]]` (both shown in the 2.1.9 relationship docs).
- FK auto-detection works when the child has a single FK to the parent table; with multiple FKs, pass `foreign_keys=[...]`.
- Since 2.1, `back_populates` accepts a lambda for forward references: `relationship(back_populates=lambda: B.a)` (improves IDE/type-checker friendliness).
- PEP 604 unions are documented in 2.1.9 mappings: `Mapped[Child | None]` for nullable one-to-one.

## One-to-One

```python
class Parent(Base):
    child: Mapped["Child"] = relationship(back_populates="parent", uselist=False, single_parent=True)
```

- `uselist=False` makes the "many" side scalar.
- `single_parent=True` enforces at the mapper level that each child has only one parent (recommended for true 1:1).

## Many-to-Many

```python
class User(Base):
    roles: Mapped[List["Role"]] = relationship(secondary="user_roles", back_populates="users")

class Role(Base):
    users: Mapped[List["User"]] = relationship(secondary="user_roles", back_populates="roles")

user_roles = Table(
    "user_roles", Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)
```

- `secondary` can be a table name (string) or a `Table` object; late-evaluated forms are supported.
- Removing an object from a many-to-many collection deletes the association row on flush.
- **Association object pattern** (extra columns on the join): map the association table as its own class with `cascade="all, delete-orphan"` from the parent — see `examples/association/` upstream.

## Cascade Options

| Cascade | Effect |
|---|---|
| `save-update` | Adding parent to session cascades to children |
| `merge` | `session.merge()` cascades |
| `delete` | `session.delete(parent)` deletes children |
| `delete-orphan` | Child removed from collection is deleted (orphaned) |
| `refresh-expire` | Attribute refresh/expire cascades |
| `expunge` | `session.expunge()` cascades |
| `all` | Everything above except `delete-orphan` |

- Default cascade is `save-update, merge`.
- Common: `relationship(..., cascade="all, delete-orphan")` for parent-owned children.
- `viewonly=True` makes a relationship read-only (no SQL emitted on mutation).

## Self-Referential

```python
class Employee(Base):
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"))
    manager: Mapped[Optional["Employee"]] = relationship(
        remote_side=[Employee.id], back_populates="subordinates")
    subordinates: Mapped[List["Employee"]] = relationship(back_populates="manager")
```

## Join Configuration

- `primaryjoin` / `secondaryjoin` — override the join condition (string or SQL expression).
- `foreign_keys=[...]` — disambiguate when multiple FKs exist.
- `foreign()` / `remote()` annotations mark which side of the join is the "remote" one in ambiguous expressions.
- `overlaps="other_rel"` — tell SQLAlchemy two relationships share a join path (affects `joinedload` row expansion).
- `order_by` — default ordering of collections (column name, expression, or callable).
- `lazy` — per-relationship loading strategy (`"select"` default; `"joined"`, `"subquery"`, `"raise"`, `"noload"`, `"write_only"`).

## Large Collections

For huge collections, `lazy="write_only"` skips loading entirely (writes/counts only), and `session.query`-style paging via `select` with `limit`/`offset` on the relationship target avoids pulling the whole collection into memory. See `orm/large_collections.rst` upstream.
