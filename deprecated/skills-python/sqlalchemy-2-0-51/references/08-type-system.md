# Type System

SQLAlchemy's type system maps Python types to database types. Types control how values are serialized, deserialized, and compared in SQL expressions.

## Built-in Types

### Numeric Types

```python
from sqlalchemy import Integer, BigInteger, SmallInteger, Float, Numeric, DECIMAL

Column("id", Integer)                    # INTEGER
Column("big_id", BigInteger)             # BIGINT
Column("small_val", SmallInteger)        # SMALLINT
Column("price", Numeric(10, 2))          # NUMERIC(10, 2) / DECIMAL(10, 2)
Column("ratio", Float)                   # FLOAT / DOUBLE PRECISION
```

### String Types

```python
from sqlalchemy import String, Text, CHAR, VARCHAR

Column("name", String(100))              # VARCHAR(100)
Column("code", CHAR(3))                  # CHAR(3)
Column("bio", Text)                      # TEXT (unlimited length)
Column("slug", VARCHAR(200))             # VARCHAR(200)
```

### Boolean

```python
from sqlalchemy import Boolean

Column("active", Boolean)                # BOOLEAN (or SMALLINT on some dialects)
```

### Date and Time

```python
from sqlalchemy import Date, DateTime, Time, Interval

Column("born", Date)                     # DATE
Column("created", DateTime)              # TIMESTAMP
Column("started_at", Time)               # TIME
Column("duration", Interval)             # INTERVAL (PostgreSQL)
```

### Binary and Large Objects

```python
from sqlalchemy import LargeBinary, BLOB

Column("data", LargeBinary)              # BLOB / BYTEA
Column("file", LargeBinary(65536))       # BLOB with size hint
```

### JSON

```python
from sqlalchemy import JSON

Column("metadata", JSON)                 # JSON (or JSONB on PostgreSQL)

# Works with Python dicts and lists
user.metadata_ = {"role": "admin", "permissions": ["read", "write"]}
```

### UUID

```python
from sqlalchemy import Uuid, UUID
import uuid

Column("id", Uuid, primary_key=True)     # UUID
Column("token", Uuid, default=uuid.uuid4)
```

### Enum

```python
from sqlalchemy import Enum
import enum

class Status(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

Column("status", Enum(Status))           # Uses Python enum values
Column("role", Enum("admin", "user", name="role_enum"))  # String enum
```

## TypeDecorator — Custom Types

`TypeDecorator` wraps an existing type and adds custom processing for bind (Python → DB) and result (DB → Python) values.

```python
from sqlalchemy import TypeDecorator, String
import json

class EncryptedString(TypeDecorator):
    """Encrypts/decrypts string values transparently."""
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return encrypt(value)  # Your encryption function
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return decrypt(value)  # Your decryption function
        return value

# Usage
Column("ssn", EncryptedString(255))
```

### TypeDecorator Methods

| Method | Direction | Description |
|---|---|---|
| `process_bind_param(value, dialect)` | Python → DB | Transform before INSERT/UPDATE |
| `process_result_value(value, dialect)` | DB → Python | Transform after SELECT |
| `process_literal_param(value, dialect)` | Literal | For literal rendering in SQL |
| `coluate(other)` | Comparison | Handle comparison operators |

### cache_ok

Set `cache_ok = True` when the type has no state that affects SQL compilation. This enables statement caching. Omit only if the type holds mutable state.

## UserDefinedType — Database-Specific Types

For types not covered by built-in types, implement `UserDefinedType`:

```python
from sqlalchemy import TypeDecorator
from sqlalchemy.types import UserDefinedType

class PostGISPoint(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw):
        return "GEOMETRY(POINT, 4326)"

    def bind_processor(self, dialect):
        def process(value):
            if value:
                return f"ST_MakePoint({value.x}, {value.y})"
            return None
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value:
                return Point.from_wkb(value)
            return None
        return process
```

## Dialect-Specific Types

### PostgreSQL

```python
from sqlalchemy.dialects.postgresql import (
    JSONB, ARRAY, INET, MACADDR, CIDR, BIT,
    UUID as PG_UUID, INTERVAL, TSVECTOR, HSTORE,
    INT4RANGE, INT8RANGE, NUMRANGE, DATERANGE, TSRANGE, TSTZRANGE,
)

Column("data", JSONB)                     # JSONB with indexing
Column("tags", ARRAY(String))             # TEXT[]
Column("ip", INET)                        # IP address
Column("addr", MACADDR)                   # MAC address
Column("network", CIDR)                   # Network range
Column("ts", TSVECTOR)                    # Full-text search
Column("hstore_data", HSTORE)             # Key-value store
Column("int_range", INT4RANGE)            # Integer range
```

### MySQL

```python
from sqlalchemy.dialects.mysql import (
    JSON as MySQLJSON, ENUM, SET, YEAR,
    TINYINT, MEDIUMINT, BIGINT,
    LONGBLOB, MEDIUMBLOB, TINYBLOB,
    GEOMETRY, POINT, LINESTRING, POLYGON,
)

Column("data", MySQLJSON)
Column("status", ENUM("active", "inactive"))
Column("location", POINT(srid=4326))
```

### SQLite

```python
from sqlalchemy.dialects.sqlite import (
    UNION,  # For UNION queries
)
# SQLite has limited type system; most types map to INTEGER, REAL, TEXT, BLOB
```

## Adapting Types

```python
from sqlalchemy import adapt_type

# Adapt a type to a different implementation
from sqlalchemy import String, Text
adapted = adapt_type(Text, String)
print(adapted)  # String()
```

## Type Coercion in Mapped[]

SQLAlchemy infers the column type from the `Mapped[T]` annotation:

| Python Type | Inferred Column Type |
|---|---|
| `int` | `Integer` |
| `str` | `String(50)` |
| `bool` | `Boolean` |
| `float` | `Float` |
| `bytes` | `LargeBinary` |
| `datetime.date` | `Date` |
| `datetime.datetime` | `DateTime` |
| `datetime.time` | `Time` |
| `dict`, `list` | `JSON` (when not a relationship) |
| `uuid.UUID` | `Uuid` |
| `Decimal` | `Numeric` |

Override with explicit type:

```python
name: Mapped[str] = mapped_column(String(200))  # Override default String(50)
data: Mapped[dict] = mapped_column(JSON)        # Explicit JSON
```

## Type Comparison Operators

Types define how Python operators translate to SQL:

```python
# String concatenation
User.name + " " + User.last_name    # || in PostgreSQL, CONCAT in others

# Pattern matching
User.name.like("alice%")            # LIKE 'alice%'
User.name.ilike("alice%")          # ILIKE (case-insensitive, PostgreSQL)
User.name.contains("alice")         # LIKE '%alice%'
User.name.startswith("alice")       # LIKE 'alice%'
User.name.endswith("com")           # LIKE '%com'

# Collection membership
User.id.in_([1, 2, 3])             # id IN (1, 2, 3)
User.id.notin_([1, 2, 3])          # id NOT IN (1, 2, 3)

# Null checks
User.email.is_(None)               # email IS NULL
User.email.isnot(None)             # email IS NOT NULL

# Between
User.age.between(18, 65)           # age BETWEEN 18 AND 65
```
