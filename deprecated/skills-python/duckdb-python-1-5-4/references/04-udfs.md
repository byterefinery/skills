# Python UDFs

## Native UDFs (Row-by-Row)

Native UDFs receive and return Python scalar values. DuckDB calls the function per row.

```python
import duckdb

def double_it(x):
    return x * 2

# Register with explicit types
duckdb.create_function(
    "double_it",
    double_it,
    parameters=["integer"],
    return_type="integer"
)

duckdb.sql("SELECT double_it(i) FROM range(5)").show()
```

### Type Annotations (Auto-Inference)

Python type annotations are used to infer parameter and return types:

```python
def add_values(a: int, b: int) -> str:
    return f"{a} + {b} = {a + b}"

duckdb.create_function("add_values", add_values)
# Parameters and return type inferred from annotations
duckdb.sql("SELECT add_values(1, 2)").show()
```

Supported annotation types: `int`, `float`, `str`, `bool`, `bytes`, `datetime.date`, `datetime.time`, `datetime.datetime`, `uuid.UUID`, etc.

### Per-Connection Registration

```python
conn = duckdb.connect()

def my_func(x):
    return x + 1

conn.create_function("my_func", my_func, ["bigint"], "bigint")
conn.sql("SELECT my_func(42)").show()
# Function is scoped to this connection
```

## Arrow UDFs (Vectorized)

Arrow UDFs receive PyArrow arrays and return arrays. Much faster for large datasets.

```python
import duckdb
import pyarrow as pa

def double_arrow(arr: pa.ChunkedArray) -> pa.ChunkedArray:
    return arr * 2

duckdb.create_function(
    "double_arrow",
    double_arrow,
    type=duckdb.func.PythonUDFType.ARROW
)

duckdb.sql("SELECT double_arrow(i) FROM range(10000)").show()
```

### Using the Vectorized Decorator

```python
import duckdb

@duckdb.udf.vectorized
def process_batch(x):
    # x is a pyarrow ChunkedArray
    import pyarrow.compute as pc
    return pc.multiply(x, 2)

duckdb.create_function("process_batch", process_batch, type=duckdb.func.PythonUDFType.ARROW)
```

## UDF Configuration Options

```python
import duckdb
from duckdb.func import FunctionNullHandling

def safe_divide(a, b):
    if b == 0:
        return None
    return a / b

duckdb.create_function(
    "safe_divide",
    safe_divide,
    parameters=["double", "double"],
    return_type="double",
    type=duckdb.func.PythonUDFType.NATIVE,
    null_handling=FunctionNullHandling.DEFAULT,  # skip NULL inputs
    exception_handling=duckdb.PythonExceptionHandling.THROW,
    side_effects=False,
)
```

### Options Reference

| Option | Values | Default | Description |
|---|---|---|---|
| `type` | `NATIVE`, `ARROW` | `NATIVE` | UDF execution mode |
| `null_handling` | `DEFAULT`, `SPECIAL`, `ARROW` | `DEFAULT` | How NULLs are handled |
| `exception_handling` | `THROW`, `RETURN_NULL`, `HANDLED` | `THROW` | On Python exception |
| `side_effects` | bool | `False` | Mark as having side effects |

- **`null_handling=DEFAULT`**: DuckDB skips rows where any input is NULL
- **`null_handling=SPECIAL`**: Function receives None for NULL values
- **`exception_handling=THROW`**: Python exceptions propagate to SQL (default)
- **`exception_handling=RETURN_NULL`**: Python exceptions return NULL
- **`exception_handling=HANDLED`**: Function must handle all errors itself

## Removing Functions

```python
# Remove a registered function
conn.remove_function("my_func")
duckdb.remove_function("my_func")
```

## UDF Transactionality

UDFs registered on a connection are transactional — they are rolled back with the transaction:

```python
conn.begin()
conn.create_function("temp_fn", fn_impl, ["integer"], "integer")
conn.rollback()  # temp_fn is removed
```

Functions registered at module level (`duckdb.create_function`) use the default connection and follow its transaction state.

## Multi-Parameter UDFs

```python
def concatenate(a: str, b: str, sep: str = "-") -> str:
    return f"{a}{sep}{b}"

duckdb.create_function("concatenate", concatenate)
duckdb.sql("SELECT concatenate('hello', 'world', '_')").show()
```

## Return Type Casting

If the return type annotation doesn't match the actual return value, DuckDB attempts to cast:

```python
def as_string(x: int) -> str:
    return str(x)

duckdb.create_function("as_string", as_string)
# Returns VARCHAR; if called with non-integer input, DuckDB casts
```
