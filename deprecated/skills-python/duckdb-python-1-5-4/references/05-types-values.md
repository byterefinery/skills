# Types and Values

## DuckDBPyType

`DuckDBPyType` represents a DuckDB SQL type. Access via `duckdb.sqltypes`:

```python
from duckdb import sqltypes

# Primitive types
sqltypes.TINYINT       # 8-bit signed integer
sqltypes.SMALLINT      # 16-bit signed integer
sqltypes.INTEGER       # 32-bit signed integer
sqltypes.BIGINT        # 64-bit signed integer
sqltypes.HUGEINT       # 128-bit signed integer

sqltypes.UTINYINT      # 8-bit unsigned
sqltypes.USMALLINT     # 16-bit unsigned
sqltypes.UINTEGER      # 32-bit unsigned
sqltypes.UBIGINT       # 64-bit unsigned
sqltypes.UHUGEINT      # 128-bit unsigned

sqltypes.FLOAT         # 32-bit float
sqltypes.DOUBLE        # 64-bit float
sqltypes.DECIMAL       # fixed-point decimal (via decimal_type)

sqltypes.VARCHAR       # variable-length string
sqltypes.BLOB          # binary data
sqltypes.BOOLEAN       # true/false
sqltypes.BIT           # bitstring

# Temporal types
sqltypes.DATE
sqltypes.TIME
sqltypes.TIME_TZ
sqltypes.TIME_NS
sqltypes.TIMESTAMP
sqltypes.TIMESTAMP_S
sqltypes.TIMESTAMP_MS
sqltypes.TIMESTAMP_NS
sqltypes.TIMESTAMP_TZ
sqltypes.INTERVAL

# Other
sqltypes.UUID
sqltypes.SQLNULL
sqltypes.VARIANT
```

## Creating Composite Types

```python
import duckdb

# List type
list_type = duckdb.list_type("INTEGER")
list_type = duckdb.list_type(duckdb.sqltypes.INTEGER)
nested = duckdb.list_type(duckdb.list_type("VARCHAR"))  # VARCHAR[][]

# Array (fixed-size list)
array_type = duckdb.array_type("INTEGER", 10)  # INTEGER[10]

# Struct type
struct_type = duckdb.struct_type({"name": "VARCHAR", "age": "INTEGER"})
struct_type = duckdb.struct_type([duckdb.sqltypes.VARCHAR, duckdb.sqltypes.INTEGER])

# Map type
map_type = duckdb.map_type("VARCHAR", "INTEGER")

# Decimal type
dec_type = duckdb.decimal_type(10, 2)  # DECIMAL(10, 2)

# Enum type
enum_type = conn.enum_type("status", sqltypes.VARCHAR, ["pending", "active", "done"])

# Row type (same as struct)
row_type = duckdb.row_type({"x": "INTEGER", "y": "INTEGER"})

# Union type
union_type = duckdb.union_type({"i": "INTEGER", "s": "VARCHAR"})
```

## Type Conversion

```python
# String to DuckDBPyType
t = duckdb.dtype("INTEGER")
t = duckdb.sqltype("VARCHAR")
t = conn.type("BIGINT")
t = conn.dtype("DOUBLE")
t = conn.sqltype("TIMESTAMP")

# List of types
lt = duckdb.list_type("VARCHAR")
```

## Value Classes

Value classes wrap Python objects with explicit DuckDB types. Useful for typed parameter passing:

```python
from duckdb.value.constant import (
    IntegerValue, LongValue, DoubleValue, StringValue,
    BooleanValue, DateValue, TimestampValue, NullValue,
    ListValue, StructValue, MapValue, DecimalValue,
)

# Simple values
v = IntegerValue(42)        # INTEGER
v = LongValue(42)           # BIGINT
v = DoubleValue(3.14)       # DOUBLE
v = StringValue("hello")    # VARCHAR
v = BooleanValue(True)      # BOOLEAN
v = NullValue()             # NULL

# Temporal
v = DateValue(datetime.date(2024, 1, 1))
v = TimestampValue(datetime.datetime(2024, 1, 1, 12, 0, 0))

# Composite
v = ListValue([1, 2, 3], child_type=duckdb.sqltypes.INTEGER)
v = StructValue({"a": 1, "b": "x"}, children={"a": "INTEGER", "b": "VARCHAR"})
v = MapValue({"key": "val"}, key_type="VARCHAR", value_type="VARCHAR")

# Decimal
v = DecimalValue(123.45, width=5, scale=2)
```

## DB-API 2.0 Type Objects

Check column types against standard categories:

```python
import duckdb
from duckdb import sqltypes

conn = duckdb.connect()
cursor = conn.cursor()
cursor.execute("SELECT 'hello' as txt, 42 as num, CURRENT_DATE as dt")

for name, col_type, *_ in cursor.description:
    if col_type == duckdb.STRING:
        print(f"{name} is a string type")
    elif col_type == duckdb.NUMBER:
        print(f"{name} is a numeric type")
    elif col_type == duckdb.DATETIME:
        print(f"{name} is a date/time type")
    elif col_type == duckdb.BINARY:
        print(f"{name} is a binary type")
```

Type objects available:
- `duckdb.STRING` — VARCHAR
- `duckdb.NUMBER` — all integer, float, decimal types
- `duckdb.DATETIME` — DATE, TIME, TIMESTAMP variants
- `duckdb.BINARY` — BLOB
- `duckdb.ROWID` — always `None` (DuckDB has no ROWID)

## Expression Builders

Build SQL expressions in Python:

```python
from duckdb import (
    ColumnExpression, ConstantExpression, FunctionExpression,
    SQLExpression, StarExpression, CaseExpression, LambdaExpression,
)

# Column reference
expr = ColumnExpression("amount")
expr = ColumnExpression("table", "amount")  # qualified

# Constant
expr = ConstantExpression(42)
expr = ConstantExpression("hello")

# Function call
expr = FunctionExpression("upper", ColumnExpression("name"))

# SQL fragment
expr = SQLExpression("amount * 1.1")

# Star with exclusions
expr = StarExpression(exclude=["internal_col"])

# Case expression
expr = CaseExpression(
    ColumnExpression("score") > 80,
    ConstantExpression("A")
).when(
    ColumnExpression("score") > 60,
    ConstantExpression("B")
).otherwise(ConstantExpression("C"))

# Lambda
expr = LambdaExpression("x", SQLExpression("x * 2"))
```

### Expression Operators

Expressions support arithmetic and comparison operators:

```python
from duckdb import ColumnExpression

col = ColumnExpression("amount")
col + 10
col * 2
col > 100
col == "active"
col.isnull()
col.isnotnull()
col.cast("VARCHAR")
col.alias("renamed")
col.asc()
col.desc()
col.between(10, 100)
col.isin(1, 2, 3)
```
