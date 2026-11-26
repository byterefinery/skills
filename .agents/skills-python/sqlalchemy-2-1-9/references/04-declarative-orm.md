# Declarative ORM

SQLAlchemy 2.1.9. Source: `orm/quickstart.rst`, `changelog/migration_21.rst` at tag `rel_2_1_9`.

## DeclarativeBase

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]          # no mapped_column needed for plain columns
    addresses: Mapped[List["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")
```

- One `Base` per registry; `Base.metadata` / `Base.registry` give access to the shared MetaData and registry.
- PEP 604 unions work in annotations: `Mapped[Child | None]` (shown in the 2.1.9 relationship docs).

## Mapped[] Type Rules

| Annotation | Column type | Nullability |
|---|---|---|
| `Mapped[int]` | `INTEGER` | NOT NULL |
| `Mapped[str]` | `VARCHAR` | NOT NULL |
| `Mapped[Optional[str]]` / `Mapped[str | None]` | `VARCHAR` | NULL |
| `Mapped[float]` | `FLOAT` | NOT NULL |
| `Mapped[bool]` | `BOOLEAN` | NOT NULL |
| `Mapped[datetime]` | `DATETIME` | NOT NULL |

- The Python type in the annotation determines the SQL type; `Optional`/`| None` controls nullability.
- `mapped_column(...)` is required for: primary keys, foreign keys, explicit SQL types (`String(30)`), server defaults, constraints, autoincrement — it accepts a superset of Core `Column` arguments.
- `mapped_column(default=...)` — Python-side default (dataclass-level default in dataclass mapping); `server_default=...` — SQL-side default; `insert_default=...` — Core-level INSERT default. In Declarative Dataclass mapping, `default` and `insert_default` are **mutually exclusive** (2.1).
- Custom type resolution: `DeclarativeBase` accepts a type-annotation map; 2.1 adds the `resolve_type_annotation` registry event (see [10-events-listeners](10-events-listeners.md)).

## Dataclass Mapping

`class Base(MappedAsDataclass, DeclarativeBase)` generates `__init__`/`__repr__`/`__eq__` via dataclasses (`init=False`, field ordering, etc.). 2.1 behavior:

- Dataclass `default`/`default_factory` values are delivered via descriptor, **not** stored in `__dict__`.
- Setting only the FK on a many-to-one (e.g. `Parent(related_id=5)`) no longer clobbers the related relationship with `None` (2.0 did; 2.1 inserts the FK correctly).
- `relationship.default` accepts only `None` (many-to-one); `relationship.default_factory` must match the annotated collection type exactly (enforced at configure time).
- `init=False` fields can still expose defaults on instances.

## Unmapped Table Columns (2.1.5+)

Declare a column that exists in the table but is **not** mapped (excluded from the mapper, dataclass, and SQL statements):

```python
from sqlalchemy.orm import Unmapped, unmapped_column

class SomeObject(Base):
    __tablename__ = "some_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[str]
    legacy_status: Unmapped[str] = unmapped_column(default="default_status")
```

Using `exclude_properties`/`include_properties` to hide *declared* attributes is deprecated (2.1.5); those parameters are for table-only columns (reflection, `__table__`).

## Multiple Registries and Mixins

- Separate `DeclarativeBase` subclasses (or `registry()` instances) give independent MetaData/registries — useful for different schemas or pluggable model packages.
- Mixins: plain classes with mapped attributes mixed into mapped classes; `declared_attr` for class-level computed attributes (dynamic table args, per-class columns).
- `__table_args__`: extra `Table` kwargs (`schema=`, `__table__` for explicit Table objects, dialect options like `postgresql_partition_by`).

## Inheritance Strategies

- **Single table** — one table, `polymorphic_on` discriminator; all subclasses in one table.
- **Joined** — each subclass gets its own table joined to the parent table (default for multi-table inheritance).
- **Concrete** — each subclass table is standalone; queries load from all tables (UNION).

Configure via `__mapper_args__ = {"polymorphic_on": ..., "polymorphic_identity": ...}`. See `examples/inheritance/` (`joined.py`, `single.py`, `concrete.py`) in the upstream repo.
