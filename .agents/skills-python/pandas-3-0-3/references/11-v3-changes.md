# v3.0 Changes and Migration Reference

Breaking changes, new features, deprecations, and migration guidance for pandas 3.0.x.

## Major Breaking Changes

### 1. String Dtype by Default

String columns now default to `str` dtype instead of `object`.

```python
# v2.x
s = pd.Series(["a", "b"])
s.dtype  # object

# v3.0
s = pd.Series(["a", "b"])
s.dtype  # str
```

**Impact**: Code checking `dtype == "object"` to find strings will break. Use `is_string_dtype()` or check for `"str"`.

**Migration**:
- Replace `df.select_dtypes(include="object")` with `include=["object", "string"]` or use `is_string_dtype()`
- String columns now reject non-string values on setitem
- Missing value sentinel is `np.nan` (not `pd.NA`) for string dtype

### 2. Copy-on-Write Always On

See [10-copy-on-write](10-copy-on-write.md) for full details.

- All indexing behaves as a copy
- Chained assignment silently fails
- `SettingWithCopyWarning` removed
- `mode.copy_on_write` option deprecated (removed in v4.0)

### 3. `pytz` Replaced by `zoneinfo`

Time zones now use the standard library's `zoneinfo` module.

```python
# v2.x
import pytz
ts = pd.Timestamp("2024-01-01", tz=pytz.timezone("America/New_York"))

# v3.0
ts = pd.Timestamp("2024-01-01", tz="America/New_York")
# Or:
from zoneinfo import ZoneInfo
ts = pd.Timestamp("2024-01-01", tz=ZoneInfo("America/New_York"))
```

**v3.0.3 fix**: PyArrow-backed IO (`read_parquet`, `read_feather`, `read_orc`) now consistently returns `zoneinfo` time zones.

### 4. Removed Deprecated Functionality

Many features deprecated in v1.x–v2.x are removed:

- `pd.Panel` (removed long ago)
- Various deprecated parameter names and aliases
- `VerifiableStringFaker` test utilities
- Many `frame.append()` / `series.append()` (use `pd.concat()`)
- `pd.concat` with `verify_integrity` parameter
- Various deprecated offset aliases

## New Features in v3.0

### `pd.col()` Expression Syntax

Column references without lambdas:

```python
from pandas import col

df.assign(total=col("a") + col("b"))
df.loc[col("age") > 25]
df.assign(ratio=col("score") / col("max_score"))
```

### Arrow PyCapsule Interface

Zero-copy data exchange:

```python
# Import from Arrow-compatible objects
df = pd.DataFrame.from_arrow(arrow_table)
s = pd.Series.from_arrow(arrow_chunk)

# Export (implements __arrow_c_stream__)
```

### Anti-Joins in Merge

```python
# Rows in df1 with no match in df2
anti = pd.merge(df1, df2, on="key", how="left_anti")
anti = pd.merge(df1, df2, on="key", how="right_anti")
```

### Rolling/Expanding: `first()`, `last()`, `nunique()`, `pipe()`

```python
df["value"].rolling(7).first()     # First value in window
df["value"].rolling(7).last()      # Last value in window
df["value"].rolling(7).nunique()   # Unique count in window
df["value"].rolling(7).pipe(my_func)  # Pipe to external function
```

### `fillna(value=None)` Support

```python
# v3.0: passes dtype-appropriate NA value
df.fillna(value=None)
```

### Half-Year DateOffsets

```python
from pandas.tseries.offsets import HalfYearBegin, HalfYearEnd
from pandas.tseries.offsets import BHalfYearBegin, BHalfYearEnd

ts + HalfYearBegin()
```

### `Holiday.exclude_dates`

```python
holiday = Holiday(
    "MyHoliday", month=7, day=4,
    exclude_dates=["2025-07-04"]  # Exclude specific dates
)
```

### `Easter.method`

```python
easter = Easter(method="orthodox")  # Orthodox Easter calculation
```

### Iceberg Support

```python
df = pd.read_iceberg("s3://bucket/db/table")
df.to_iceberg("s3://bucket/db/table")
```

### Other Enhancements

| Feature | Details |
|---------|---------|
| `to_csv` f-string format | `float_format="{:.6f}"` (also `%` format) |
| `to_excel` `autofilter` | Add auto-filters to all columns |
| `to_excel` `merge_cells="columns"` | Only merge MultiIndex column headers |
| `read_parquet` `to_pandas_kwargs` | Forward kwargs to `pyarrow.Table.to_pandas` |
| `merge` validates `how` parameter | Invalid values raise error |
| `NamedAgg` with `*args`/`**kwargs` | Pass arguments to aggfunc |
| GroupBy `skipna` parameter | On `sum`, `mean`, `median`, etc. |
| `Series.str.isascii()` | Check if all chars are ASCII |
| `Series.str.get_dummies(dtype=)` | Specify output dtype |
| `Series.str.replace(dict)` | Dict of pattern→replacement mappings |
| `merge` propagates `attrs` | If all inputs have identical attrs |
| `to_json` encodes `Decimal` as strings | Instead of floats |
| `cummin/cummax/cumprod/cumsum` `numeric_only` | Parameter on DataFrame methods |
| `corrwith` accepts `min_periods` | Consistent with `corr` |
| `Series.map` accepts kwargs | Pass to the mapping function |
| `Series.nlargest` uses stable sort | Preserves original ordering for ties |
| `read_stata` improved datetime resolution | Better matching of native Stata formats |
| `read_stata` supports older formats | 102, 103, 104, 106, 108 formats |
| `Styler.to_typst()` | Export to Typst format |
| `Styler.format_index_names()` | Format index/column names |
| `DataFrame/iloc` boolean masks | More consistent indexing behavior |

## Deprecation Policy (v3.0+)

Three-stage deprecation policy:

1. **`DeprecationWarning`** — Initial deprecation (invisible by default)
2. **`FutureWarning`** — Last minor version before next major (visible)
3. **Removal** — In the next major release

Warning classes:

| Class | Category | When Visible |
|-------|----------|-------------|
| `PandasDeprecationWarning` | `DeprecationWarning` | With `-Wd` flag |
| `PandasFutureWarning` | `FutureWarning` | Always visible |
| `Pandas4Warning` | Will be enforced in v4.0 | Initially hidden, visible in last 3.x |
| `Pandas5Warning` | Will be enforced in v5.0 | Currently hidden |
| `PandasPendingDeprecationWarning` | `PendingDeprecationWarning` | With `-Wd` flag |

All inherit from `PandasChangeWarning`.

## v3.0.x Patch Releases

### v3.0.1
- Bug fixes and regression patches

### v3.0.2
- Additional bug fixes

### v3.0.3 (May 11, 2026)
- **PyArrow IO now returns `zoneinfo` time zones** (consistent with default)
- Fixed `bdate_range` regression with `end` on weekend + `periods`
- Fixed `to_timedelta` ignoring `unit` for round floats in mixed lists
- Fixed `Series.rank` regression with custom extension dtypes
- Fixed `Timedelta.round/floor/ceil` `ZeroDivisionError` for sub-second freq
- Fixed reading Parquet with tz-aware timestamps + older pytz
- Fixed `read_csv` C engine `thousands=","` parsing non-numeric values
- Fixed performance regression with zoneinfo timezone-aware data
- Fixed ArrowDtype string arithmetic (string + large_string)
- Fixed NA addition to PyArrow-backed string arrays
- Fixed `Series.str.replace` hang with empty pattern on PyArrow strings

## Migration Checklist

1. **Replace `object` dtype checks for strings** → use `is_string_dtype()` or check `"str"`
2. **Fix chained assignment** → use `.loc[mask, "col"] = value`
3. **Remove `SettingWithCopyWarning` handling** → no longer emitted
4. **Remove `pytz` imports** → use string tz names or `zoneinfo.ZoneInfo()`
5. **Remove `mode.copy_on_write` settings** → always on, option deprecated
6. **Update offset aliases** → use new class names (e.g., `MonthEnd` not `ME`)
7. **Test with `mode.chained_assignment = "raise"`** → catches remaining issues
8. **Upgrade to v2.3 first** → get deprecation warnings, fix before v3.0
9. **Check `read_csv`/IO behavior** → string columns are now `str` dtype
10. **Verify merge/join results** → anti-joins available if needed

## Gotchas

- **Upgrading directly from v1.x to v3.0 is risky** — go through v2.3 first to catch deprecation warnings.
- **String dtype affects `.dtype` checks everywhere** — `df.dtypes == "object"` no longer matches string columns.
- **Some third-party libraries may not support v3.0 yet** — check compatibility before upgrading in production.
- **`pytz` time zones in existing data** can still be read but new operations use `zoneinfo`.
- **Arrow-backed strings behave slightly differently** from object strings in edge cases (e.g., mixed types).
- **The `inplace` parameter is not deprecated in v3.0** but is discouraged due to CoW semantics. Prefer reassignment.
