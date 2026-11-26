# Data Types Reference

Pandas dtypes, nullable types, ArrowDtype, string dtype (v3.0 default), and type conversion.

## Type System Overview

Pandas supports three tiers of data types:

1. **NumPy dtypes** — `int64`, `float64`, `bool`, `object`, `datetime64[ns]`, `timedelta64[ns]`
2. **Pandas extension dtypes** — nullable integers (`Int64`), strings (`str`), booleans (`boolean`), categories, intervals, periods
3. **ArrowDtype** — PyArrow-backed types for memory efficiency and additional data types

### String Dtype Default (v3.0+)

In pandas 3.0+, string columns default to `str` dtype (Arrow-backed if PyArrow installed, otherwise NumPy object-backed). Previously they were `object`. The `future.infer_string` option is deprecated in 3.1 — str inference is permanent and cannot be disabled from 4.0.

```python
# v3.0+ behavior
s = pd.Series(["a", "b", None])
s.dtype  # str (not object)

# Check for string dtype
pd.api.types.is_string_dtype(s)  # True
```

### v3.1 Resolution Change: Numeric Datetime/Timedelta Input

Numeric input to `to_datetime`, `to_timedelta`, `Timestamp`, and `Timedelta` constructors now defaults to **microsecond** resolution (or nanoseconds if the input precision requires it), regardless of the `unit` argument used to convert:

```python
pd.to_datetime([1, 2], unit="s").dtype   # datetime64[us] (v3.1; was [s] in 3.0.x)
pd.to_timedelta([1, 2], unit="s").dtype   # timedelta64[us]
pd.Timestamp(1, unit="s").unit            # 'us'
pd.Timedelta(1, unit="s").unit            # 'us'
```

If you need the input's own resolution, convert afterwards: `ser.dt.as_unit("s")` / `ts.as_unit("ns")`, or cast integer data directly to `datetime64[...]`/`timedelta64[...]` with the desired unit.

## NumPy dtypes

| dtype | Description | NA sentinel |
|-------|-------------|-------------|
| `int8/16/32/64` | Signed integers | Cannot hold NA (use `Int8/16/32/64`) |
| `uint8/16/32/64` | Unsigned integers | Cannot hold NA |
| `float32/64` | Floating point | `np.nan` |
| `bool` | Boolean | Cannot hold NA (use `boolean`) |
| `object` | Python objects | `None`, `np.nan` |
| `datetime64[ns/us/...]` | Timestamps (any resolution) | `NaT` |
| `timedelta64[ns/us/...]` | Time differences (any resolution) | `NaT` |
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

# v3.1 — concat with union_categories=True unions categories
# instead of requiring identical category sets
pd.concat([s1, s2], axis=0, union_categories=True)

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

# v3.1 — Period supports f-string formatting
p = pd.Period("2024-01", freq="M")
f"{p:%Y-%m}"  # '2024-01'
```

### DatetimeTZDtype

Timezone-aware timestamps.

```python
dtype = pd.DatetimeTZDtype(tz="UTC")
s = pd.Series(pd.date_range("2024-01-01", periods=3), dtype=dtype)

# v3.1 — .values on tz-aware data is deprecated (lossy); use .array or .to_numpy()
s.array  # DatetimeArray with timezone
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
pd.ArrowDtype(pa.timestamp("us", tz="UTC"))
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

# v3.1 — %N directive matches exactly 9 digits (nanoseconds) in strptime formats
s = pd.to_datetime(s, format="%Y-%m-%d %H:%M:%S.%N")

# From components
s = pd.to_datetime({"year": [2024], "month": [1], "day": [15]})

# Options
pd.to_datetime(s, errors="coerce")       # Invalid → NaT
pd.to_datetime(s, utc=True)              # Parse as UTC
pd.to_datetime(s, dayfirst=True)         # DD/MM/YYYY
```

### `pd.to_timedelta()`

```python
s = pd.to_timedelta(["1 day", "2 hours", "30 minutes"])
s = pd.to_timedelta([1, 2, 3], unit="D")    # Days
s = pd.to_timedelta([1, 2, 3], unit="h")    # Hours

# v3.1 — strings with trailing characters (e.g. "3:25:00 PM") raise
# instead of silently dropping the AM/PM marker
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
| String (v3.0+) | `np.nan` | Follows float semantics |
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
df.fillna(value=None)         # Uses dtype-appropriate NA

# v3.1 — fillna with an incompatible value requiring dtype casting is
# deprecated; cast to a common dtype explicitly before filling

# Drop missing values
df.dropna()                   # Drop rows with any NA
df.dropna(how="all")          # Drop rows where all are NA
df.dropna(subset=["col1"])    # Only check specific columns
df.dropna(thresh=3)           # Keep rows with at least 3 non-NA
```

## v3.1 select_dtypes Rules

`DataFrame.select_dtypes` got stricter in 3.1:

- A Python class that does not name a dtype (`decimal.Decimal`, `datetime.date`, `Timestamp`) raises `TypeError`; pass `object` to select object-dtype columns as before
- A dtype **instance** selects only columns with exactly that dtype (`np.dtype("int64")` no longer selects `Int64` or Arrow `int64`)
- `"datetime64[ns]"` / `"timedelta64[ns]"` select only ns-resolution columns; unitless `"datetime64"` selects all resolutions
- Resolution-specific specs now work: `include=["datetime64[us]"]`, `np.dtype("timedelta64[ms]")`
- Partial `IntervalDtype`/`CategoricalDtype` specs (some but not all attributes) raise `ValueError`
- Passing `None` inside `include`/`exclude` is deprecated (it silently selected float64); pass `"float64"` explicitly
