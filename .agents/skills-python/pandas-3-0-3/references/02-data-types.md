# Data Types Reference

Pandas dtypes, nullable types, ArrowDtype, string dtype (v3.0 default), and type conversion.

## Type System Overview

Pandas supports three tiers of data types:

1. **NumPy dtypes** — `int64`, `float64`, `bool`, `object`, `datetime64[ns]`, `timedelta64[ns]`
2. **Pandas extension dtypes** — nullable integers (`Int64`), strings (`str`), booleans (`boolean`), categories, intervals, periods
3. **ArrowDtype** — PyArrow-backed types for memory efficiency and additional data types

### v3.0 String Dtype Default

In pandas 3.0+, string columns default to `str` dtype (Arrow-backed if PyArrow installed, otherwise NumPy object-backed). Previously they were `object`.

```python
# v3.0 behavior
s = pd.Series(["a", "b", None])
s.dtype  # str (not object)

# Check for string dtype
pd.api.types.is_string_dtype(s)  # True

# Explicit control
pd.set_option("mode.string_storage", "python")   # Use Python strings
pd.set_option("mode.string_storage", "pyarrow")  # Use PyArrow strings
```

## NumPy dtypes

| dtype | Description | NA sentinel |
|-------|-------------|-------------|
| `int8/16/32/64` | Signed integers | Cannot hold NA (use `Int8/16/32/64`) |
| `uint8/16/32/64` | Unsigned integers | Cannot hold NA |
| `float32/64` | Floating point | `np.nan` |
| `bool` | Boolean | Cannot hold NA (use `boolean`) |
| `object` | Python objects | `None`, `np.nan` |
| `datetime64[ns]` | Timestamps | `NaT` |
| `timedelta64[ns]` | Time differences | `NaT` |
| `complex64/128` | Complex numbers | N/A |

## Pandas Extension dtypes

Extension dtypes support NA values and provide more specific type semantics.

### Nullable Integer Types

```python
# Construction
s = pd.Series([1, 2, None], dtype="Int64")
s.dtype  # Int64

# Available: Int8, Int16, Int32, Int64, UInt8, UInt16, UInt32, UInt64
s = pd.array([1, 2, pd.NA], dtype="UInt32")

# NA value is pd.NA (not np.nan)
s.isna()  # [False, False, True]

# Arithmetic preserves nullable type
s + 1     # Int64 with NA propagation
```

### Nullable Boolean

```python
s = pd.Series([True, False, None], dtype="boolean")
s.dtype  # boolean
s & True              # Logical AND with NA propagation
(~s).fillna(False)    # Negation with fill
```

### Nullable Float

```python
s = pd.Series([1.0, 2.0, None], dtype="Float64")
# Available: Float32, Float64
```

### String Dtype

```python
# Explicit construction
s = pd.Series(["hello", "world"], dtype="string")
s.dtype  # string

# With PyArrow backend
s = pd.Series(["hello", "world"], dtype=pd.StringDtype(storage="pyarrow"))

# Operations
s.str.upper()
s.str.contains("ell")
s + "!"                     # String concatenation
```

### Categorical Dtype

For columns with limited distinct values (memory efficient).

```python
# Construction
s = pd.Series(["low", "med", "high", "low"], dtype="category")
s = pd.Categorical(["low", "med", "high"],
                    categories=["low", "med", "high"],
                    ordered=True)

# Properties
s.cat.categories            # Index of category names
s.cat.ordered               # Whether ordered
s.cat.codes                 # Integer codes (-1 for NA)

# Operations
s.cat.add_categories(["critical"])
s.cat.remove_categories(["low"])
s.cat.rename_categories({"low": "Low", "med": "Medium"})
s.cat.as_ordered()          # Convert to ordered
s.cat.as_unordered()        # Convert to unordered

# Sorting respects category order (if ordered)
s.sort_values()
```

### Interval Dtype

```python
# Construction
idx = pd.IntervalIndex.from_breaks([0, 10, 20, 30])
s = pd.Series(idx, dtype="interval")

# Properties
s.left                       # Left endpoints
s.right                      # Right endpoints
s.mid                        # Midpoints
s.width                      # Interval widths
s.closed                     # "left", "right", "both", "neither"

# Membership test
pd.Interval(0, 10).contains(5)  # True
```

### Period Dtype

Fixed-frequency time periods.

```python
# Construction
s = pd.Series(pd.period_range("2024-01", periods=3, freq="M"))
s.dtype  # period[M]

# Components
s.dt.year, s.dt.month, s.dt.day
```

### DatetimeTZDtype

Timezone-aware timestamps.

```python
dtype = pd.DatetimeTZDtype(tz="UTC")
s = pd.Series(pd.date_range("2024-01-01", periods=3), dtype=dtype)
```

## ArrowDtype

PyArrow-backed extension type for memory efficiency and additional types.

```python
# Construction
import pyarrow as pa
dtype = pd.ArrowDtype(pa.int64())
s = pd.Series([1, 2, 3], dtype=dtype)

# Common Arrow types
pd.ArrowDtype(pa.string())
pd.ArrowDtype(pa.float64())
pd.ArrowDtype(pa.timestamp("ns", tz="UTC"))
pd.ArrowDtype(pa.list_(pa.int64()))       # List type
pd.ArrowDtype(pa.struct([("x", pa.int64()), ("y", pa.float64())]))  # Struct
pd.ArrowDtype(pa.map_(pa.string(), pa.int64()))  # Map/dict

# From PyArrow table
table = pa.table({"a": [1, 2, 3], "b": ["x", "y", "z"]})
df = pd.DataFrame(table)
```

## Type Conversion

### `pd.to_numeric()`

```python
# Convert to numeric, coerce errors to NA
s = pd.to_numeric(["1", "2", "bad"], errors="coerce")
# [1.0, 2.0, NaN]

# Options
pd.to_numeric(s, errors="raise")   # Raise on failure (default)
pd.to_numeric(s, errors="ignore")  # Return original on failure
pd.to_numeric(s, downcast="integer")  # Use smallest sufficient integer type
pd.to_numeric(s, downcast="float")    # Use smallest sufficient float type
```

### `pd.to_datetime()`

```python
# From strings
s = pd.to_datetime(["2024-01-01", "2024-02-15", "2024-03-31"])

# With format hint (faster parsing)
s = pd.to_datetime(s, format="%Y-%m-%d")

# From components
s = pd.to_datetime({"year": [2024], "month": [1], "day": [15]})

# Options
pd.to_datetime(s, errors="coerce")       # Invalid → NaT
pd.to_datetime(s, utc=True)              # Parse as UTC
pd.to_datetime(s, dayfirst=True)         # DD/MM/YYYY
pd.to_datetime(s, infer_datetime_format=True)  # Auto-detect format
```

### `pd.to_timedelta()`

```python
s = pd.to_timedelta(["1 day", "2 hours", "30 minutes"])
s = pd.to_timedelta([1, 2, 3], unit="D")    # Days
s = pd.to_timedelta([1, 2, 3], unit="h")    # Hours
```

### `astype()`

```python
# Series / DataFrame dtype conversion
s.astype(float)
df.astype({"col1": "Int64", "col2": "string"})

# With nullable types
s.astype("Int64")              # Nullable integer
s.astype("boolean")            # Nullable boolean
s.astype(pd.StringDtype())     # String dtype

# Error handling
s.astype(float, errors="coerce")   # Invalid → NaN
s.astype(float, errors="ignore")   # Keep original on failure

# Custom converter
df["col"].astype(lambda x: x.strip())
```

## Type Inspection

```python
# Check dtype categories
pd.api.types.is_integer_dtype(s)
pd.api.types.is_float_dtype(s)
pd.api.types.is_bool_dtype(s)
pd.api.types.is_string_dtype(s)
pd.api.types.is_numeric_dtype(s)
pd.api.types.is_datetime64_any_dtype(s)
pd.api.types.is_extension_array_dtype(s)

# Get pandas dtype from string
pd.api.types.pandas_dtype("Int64")
pd.api.types.pandas_dtype("float64")

# Infer dtype from values
pd.api.types.infer_dtype(["a", "b", "c"])  # 'string'
pd.api.types.infer_dtype([1, 2, 3])        # 'integer'
```

## Missing Value Semantics

| Type | NA Sentinel | Notes |
|------|-------------|-------|
| NumPy float | `np.nan` | IEEE 754 NaN |
| NumPy int/bool | N/A | Cannot represent missing |
| Nullable Int/Bool/Float | `pd.NA` | Three-valued logic |
| String (v3.0) | `np.nan` | Follows float semantics |
| ArrowDtype string | `None` / `pd.NA` | Depends on backend |
| Datetime/Timedelta | `NaT` | Not a Time |
| Object | `None`, `np.nan`, `pd.NA` | Multiple sentinels |

```python
# Unified missing value checks
pd.isna(df)        # Works for all types
pd.notna(df)       # Inverse
df.isnull()        # Alias for isna
df.notnull()       # Alias for notna

# Fill missing values
df.fillna(0)
df.fillna(method="ffill")     # Forward fill
df.fillna({"col1": 0, "col2": "unknown"})  # Per-column
df.fillna(value=None)         # v3.0: uses dtype-appropriate NA

# Drop missing values
df.dropna()                   # Drop rows with any NA
df.dropna(how="all")          # Drop rows where all are NA
df.dropna(subset=["col1"])    # Only check specific columns
df.dropna(thresh=3)           # Keep rows with at least 3 non-NA
```
