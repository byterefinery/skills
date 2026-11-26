# Python UDFs

## Creating UDFs

```python
import duckdb

# Native UDF — row-by-row execution
def double_it(x):
    return x * 2

duckdb.create_function(
    "double_it",
    double_it,
    parameters=[duckdb.Integer],
    return_type=duckdb.Integer,
)

# Use in SQL
duckdb.sql("SELECT double_it(x) FROM t").show()

# Multiple parameters
def add(a, b):
    return a + b

duckdb.create_function(
    "my_add",
    add,
    parameters=[duckdb.Integer, duckdb.Integer],
    return_type=duckdb.Integer,
)

# String type parameters
def upper(s):
    return s.upper()

duckdb.create_function(
    "my_upper",
    upper,
    parameters=[duckdb.Varchar],
    return_type=duckdb.Varchar,
)
```

## Arrow (Vectorized) UDFs

Arrow UDFs operate on entire arrays at once, avoiding Python per-row overhead:

```python
import duckdb
import pyarrow as pa

# Arrow UDF — receives ChunkedArray, returns ChunkedArray
def arrow_double(arr):
    return arr * 2

duckdb.create_function(
    "arrow_double",
    arrow_double,
    parameters=["integer"],
    return_type="integer",
    type=duckdb.func.ARROW,
)

# Multiple columns
def arrow_add(a, b):
    return a + b

duckdb.create_function(
    "arrow_add",
    arrow_add,
    parameters=["integer", "integer"],
    return_type="integer",
    type=duckdb.func.ARROW,
)
```

## Vectorized Decorator

The `@vectorized` decorator auto-annotates function parameters with `pyarrow.ChunkedArray`:

```python
from duckdb.udf import vectorized

@vectorized
def my_func(col1, col2):
    return col1 + col2

duckdb.create_function("my_func", my_func, type=duckdb.func.ARROW)
```

## UDF Types

| Type | Constant | Description |
|------|----------|-------------|
| `NATIVE` | `duckdb.func.NATIVE` | Row-by-row Python execution (default) |
| `ARROW` | `duckdb.func.ARROW` | Vectorized, operates on PyArrow arrays |
| `DEFAULT` | `duckdb.func.DEFAULT` | Auto-select based on annotations |
| `SPECIAL` | `duckdb.func.SPECIAL` | Special handling (table functions, etc.) |

## Null Handling

```python
duckdb.create_function(
    "my_func",
    my_func_impl,
    parameters=[duckdb.Integer],
    return_type=duckdb.Integer,
    null_handling=duckdb.func.FunctionNullHandling.DEFAULT,  # passes NULL to function
    # null_handling=duckdb.func.FunctionNullHandling.SKIP,   # skips NULL inputs, returns NULL
)
```

## Exception Handling

```python
duckdb.create_function(
    "my_func",
    my_func_impl,
    parameters=[duckdb.Integer],
    return_type=duckdb.Integer,
    exception_handling=duckdb.PythonExceptionHandling.RETURN_NULL,  # error → NULL
    # exception_handling=duckdb.PythonExceptionHandling.THROW,       # error → SQL exception
)
```

## Side Effects

Mark functions with side effects to prevent optimization away:

```python
duckdb.create_function(
    "log_value",
    log_impl,
    parameters=[duckdb.Varchar],
    return_type=duckdb.Varchar,
    side_effects=True,
)
```

## Connection-Specific UDFs

```python
con = duckdb.connect()

con.create_function("my_func", func, parameters=[duckdb.Integer], return_type=duckdb.Integer)
con.remove_function("my_func")
```

## Type Construction for UDF Parameters

```python
# Simple types
duckdb.Integer, duckdb.Varchar, duckdb.Boolean, duckdb.Double
duckdb.dtype("INTEGER"), duckdb.dtype("VARCHAR")

# Struct parameters
duckdb.struct_type({"name": "varchar", "age": "integer"})

# List parameters
duckdb.list_type("integer")

# Decimal
duckdb.decimal_type(10, 2)
```

## Table Functions

DuckDB also supports Python table functions (returning multiple rows):

```python
# Use table_function() on a connection
rel = con.table_function("generate_series", parameters=(1, 10))
```

## Performance Notes

- **NATIVE UDFs** have significant per-row Python overhead — suitable for complex logic, not for large datasets
- **ARROW UDFs** process entire arrays in C++ with minimal Python calls — preferred for numeric operations
- Use Arrow UDFs whenever the operation can be expressed on arrays (arithmetic, string ops via pyarrow compute)
- For very heavy computation, consider implementing in C++ as a DuckDB extension rather than Python UDF
