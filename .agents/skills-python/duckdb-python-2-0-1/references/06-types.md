# Types

## SQL Type Construction

```python
import duckdb

# Parse type from SQL string
duckdb.dtype("INTEGER")
duckdb.dtype("VARCHAR")
duckdb.dtype("DOUBLE")
duckdb.dtype("TIMESTAMP")
duckdb.sqltype("INTEGER")       # alias for dtype()
con.sqltype("INTEGER")
con.type("INTEGER")
con.dtype("INTEGER")

# String type with optional collation
duckdb.string_type()
duckdb.string_type(collation="en")
```

## Struct Type

```python
# Dict notation: {field_name: type_string}
duckdb.struct_type({"name": "varchar", "age": "integer", "active": "boolean"})

# List of tuples: [(field_name, type), ...]
duckdb.struct_type([("name", "varchar"), ("age", "integer")])

# Row type (alias)
duckdb.row_type({"x": "integer", "y": "double"})
```

## List Type

```python
duckdb.list_type("integer")
duckdb.list_type("varchar")
duckdb.list_type(duckdb.struct_type({"x": "integer"}))
```

## Array Type (Fixed-Size)

```python
duckdb.array_type("integer", 3)   # integer[3]
duckdb.array_type("double", 10)   # double[10]
```

## Map Type

```python
duckdb.map_type("varchar", "integer")
duckdb.map_type("integer", duckdb.list_type("double"))
```

## Enum Type

```python
duckdb.enum_type("status", "varchar", ["open", "closed", "pending"])
duckdb.enum_type("priority", "integer", [0, 1, 2, 3, 4])
```

## Decimal Type

```python
duckdb.decimal_type(10, 2)   # DECIMAL(10, 2) — 10 digits total, 2 after decimal
duckdb.decimal_type(18, 4)   # DECIMAL(18, 4)
```

## Union Type

```python
duckdb.union_type({"text": "varchar", "number": "integer", "flag": "boolean"})
```

## Type Inspection

```python
# From a relation
rel = duckdb.sql("SELECT * FROM t")
rel.dtypes        # list of DuckDBPyType
rel.types         # alias for dtypes
rel.description   # DB-API style: [(name, type, ...), ...]

# Select columns by type
rel.select_dtypes([duckdb.dtype("INTEGER"), duckdb.dtype("DOUBLE")])
rel.select_types([duckdb.dtype("VARCHAR")])
```

## DB-API Type Objects

```python
from duckdb import DBAPITypeObject, NUMBER, STRING, BINARY, DATETIME, ROWID

# Check if a type matches a category
isinstance(some_type, DBAPITypeObject)
```

## Value Types

DuckDB exposes typed value wrappers for constructing SQL literals:

```python
from duckdb.value.constant import (
    IntegerValue, LongValue, DoubleValue, FloatValue,
    StringValue, BooleanValue, NullValue,
    DateValue, TimeValue, TimestampValue,
    ListValue, StructValue, MapValue,
    DecimalValue, UUIDValue, BitValue, BlobValue,
    IntervalValue,
    # Unsigned variants
    UnsignedIntegerValue, UnsignedLongValue,
    UnsignedShortValue, UnsignedHugeIntegerValue,
    UnsignedBinaryValue,
    # Timestamp variants
    TimestampSecondValue, TimestampMillisecondValue,
    TimestampNanosecondValue, TimestampTimeZoneValue,
    # Time variants
    TimeValue, TimeTimeZoneValue,
    # Short/HugeInteger
    ShortValue, HugeIntegerValue,
    BinaryValue,
)

# Example usage in SQL expressions
IntegerValue(42)
StringValue("hello")
ListValue([1, 2, 3])
StructValue({"name": "Alice", "age": 30})
```

## Type Constants

```python
# Standard vector size (batch size used internally)
duckdb.__standard_vector_size__   # typically 8192
```
