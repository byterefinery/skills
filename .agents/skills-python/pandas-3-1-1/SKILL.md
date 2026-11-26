---
name: pandas-3-1-1
description: >
  Pandas 3.1.1 data manipulation and analysis library for Python. Use when working
  with DataFrames, Series, data wrangling, CSV/Excel/Parquet I/O, groupby aggregations,
  merging/joining, time series, resampling, rolling windows, string operations, or any
  tabular data processing in Python. Covers pandas 3.1 semantics including DataFrame.select,
  boolean-mask filtering via filter cond, parallel read_csv, NumPy 2 requirement, string
  dtype by default, Copy-on-Write behavior, pd.col() expressions, and anti-joins. Triggers
  on DataFrame, Series, read_csv, merge, groupby, pivot_table, resample, rolling, time
  series analysis, ETL pipelines, data cleaning, or any mention of pandas dataframes.
metadata:
  tags:
    - python
    - data-analysis
    - etl
    - tabular-data
---

# pandas 3.1.1

## Overview

Pandas 3.1.1 is the Python library for tabular data manipulation and analysis. It builds on the pandas 3.0 semantic foundation — dedicated string dtype by default, Copy-on-Write behavior (no `SettingWithCopyWarning`), `pd.col()` expressions, Arrow PyCapsule interface, anti-joins — and adds the 3.1 features listed below.

### Core Objects

- **DataFrame** — 2D labeled table with heterogeneous columns
- **Series** — 1D labeled array (single column of a DataFrame)
- **Index** — immutable label axis (includes DatetimeIndex, MultiIndex, CategoricalIndex, etc.)

### Key v3.1 Changes

1. **`DataFrame.select`** — select columns by label, `pd.col()` expression, or callable kwargs; later kwargs may refer to columns computed earlier in the same call (v3.1.0)
2. **Boolean-mask filtering** — `DataFrame.filter` and `Series.filter` accept `cond=` (mask, callable, or `pd.col` expression) plus `na=` handling (v3.1.0)
3. **Faster `read_csv`** — C engine is 2–3× faster than 3.0 and reads large local uncompressed files (≥ 5 MB) in parallel across cores; `mode.max_threads` controls it (v3.1.0)
4. **NumPy ≥ 2 required** — pandas 3.1 drops NumPy 1.x (≥ 2.0.2, or ≥ 2.3.3 on Python 3.14) (v3.1.0)
5. **`inplace` keyword deprecated** (PDEP-8) for methods that never worked inplace — reassign the result instead (v3.1.0)
6. **Lossy `.values` deprecated** — tz-aware datetime, period, and interval `.values` emit `Pandas4Warning`; `.values` will return the ExtensionArray in 4.0 (v3.1.0)
7. **Microsecond default resolution** — numeric input to `Timestamp`/`Timedelta`/`to_datetime`/`to_timedelta` now defaults to `us` resolution (v3.1.0)

### Dependencies

- **Required**: `numpy>=2.0.2` (`numpy>=2.3.3` on Python 3.14), `python-dateutil>=2.9.0`, `tzdata` (Windows/Pyodide)
- **Python versions**: 3.11+
- **Optional**: `pyarrow>=16.0.0` (Parquet, Feather, ORC, Arrow-backed dtypes), `bottleneck`, `numexpr` (≥ 2.14.2 — 2.14.1 returns incorrect results and is bypassed), `scipy`, `fsspec`, `calamine` (Excel), `pyiceberg`

## Usage

```python
import pandas as pd

# Create a DataFrame
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [30, 25, 35],
    "score": [85.5, 92.0, 78.3]
})

# String dtype is default in v3.0+
df["name"].dtype  # str (not object)

# Read data (large local CSVs read in parallel automatically in v3.1)
df = pd.read_csv("data.csv")
df = pd.read_parquet("data.parquet")

# v3.1 — select columns, including computed ones via pd.col()
from pandas import col
df.select("name", avg_score=col("score") / col("score").mean())

# v3.1 — filter rows with a boolean mask
df.filter(cond=df["age"] > 25)
df.filter(col("age") > 25)
df.filter(lambda d: d["score"] < 80)

# Indexing — loc (label-based), iloc (position-based)
row = df.loc[0]
first_two = df.iloc[:2]

# Boolean filtering
filtered = df[df["age"] > 25]

# Groupby aggregation
result = df.groupby("category").agg(
    avg_score=("score", "mean"),
    total=("score", "sum")
)

# Merge / join (anti-joins from v3.0)
merged = pd.merge(df1, df2, on="key", how="left")
anti = pd.merge(df1, df2, on="key", how="left_anti")

# Reshaping
pivoted = df.pivot_table(index="date", columns="category", values="value", aggfunc="sum")
melted = pd.melt(df, id_vars=["id"], value_vars=["a", "b", "c"])

# Time series
ts = pd.read_csv("data.csv", parse_dates=["date"])
ts = ts.set_index("date").sort_index()
resampled = ts.resample("ME").sum()

# Rolling windows
rolling_avg = df["value"].rolling(window=7).mean()

# Export
df.to_csv("output.csv", index=False)
df.to_parquet("output.parquet")
```

### Copy-on-Write (v3.0+)

Every indexing operation *behaves as a copy*. Modify the original object directly:

```python
# Correct — modify original directly
df.loc[mask, "col"] = value

# Chained assignment does NOT work (warns ChainedAssignmentError, df unchanged)
df[df["age"] > 25]["score"] = 100  # WRONG — modifies a copy
```

## Gotchas

- **NumPy 2 is required** — pandas 3.1 does not work with NumPy 1.x; upgrade before upgrading pandas.
- **`inplace=True` is deprecated** for `drop`, `rename`, `rename_axis`, `reset_index`, `set_index`, `dropna`, `drop_duplicates`, `sort_values`, `sort_index`, `eval`, `query`. Reassign instead: `df = df.reset_index()`.
- **`.values` on tz-aware/period/interval data is deprecated** — use `.array` (ExtensionArray) or `.to_numpy()`; for tz-aware UTC-converted NumPy output use `ser.dt.tz_convert(None).to_numpy()` or `ser.to_numpy(dtype="datetime64[us]")`.
- **Numeric datetime/timedelta input defaults to `us` resolution** — `pd.Timestamp(1, unit="s")`, `pd.to_datetime([1], unit="s")`, `pd.to_timedelta([1], unit="s")` all yield microsecond dtype; use `.as_unit("ns")` or cast integers explicitly when another resolution is needed.
- **Large CSV reads are parallel by default** — local uncompressed files ≥ 5 MB are read on multiple threads (identical result to serial). Set `pd.option_context("mode.max_threads", 1)` to read serially (e.g., inside apps that already parallelize).
- **Chained assignment now warns** — pandas 3.0 removed `SettingWithCopyWarning`; since 3.1 chained assignment emits `ChainedAssignmentError` (a `Warning` subclass). The `mode.chained_assignment` option is deprecated; silence or promote the warning with `warnings.filterwarnings(...)`.
- **`Timestamp` no longer ignores date components** — `pd.Timestamp(datetime(2020, 12, 31), hour=5)` raises `ValueError`. Pass all components by keyword (`pd.Timestamp(year=2020, month=12, day=31, hour=5)`) or in the value.
- **`Timedelta`/`to_timedelta` raise on trailing characters** — `"3:25:00 PM"` previously parsed as 3 hours silently; it now raises. AM/PM is not supported for timedeltas.
- **`select_dtypes` is stricter** — passing a Python class that does not name a dtype (e.g., `datetime.date`, `decimal.Decimal`) raises `TypeError`; a dtype *instance* matches only exactly that dtype; `"datetime64[ns]"` selects only ns-resolution columns (use unitless `"datetime64"` for all).
- **`read_csv` with `dtype="category"` infers numeric/boolean categories** — zero-padded IDs like zip codes get integer categories, dropping leading zeros. Read as `str` and convert with `.astype("category")` to keep them.
- **`fastparquet` engine is deprecated** — the library is retired; use `engine="pyarrow"` for Parquet.
- **`df.join(lsuffix=, rsuffix=)` is deprecated** — use `suffixes=("_left", "_right")` consistent with `merge`.
- **String dtype is default (v3.0)** — code checking `dtype == "object"` for strings breaks; use `is_string_dtype()` or check `"str"`.
- **`pytz` replaced by `zoneinfo`** — use `pd.Timestamp("2024-01-01", tz="America/New_York")` or `zoneinfo.ZoneInfo`, not `pytz.timezone()`.
- **`infer_freq` will return offsets, not strings** — `pd.infer_freq` currently returns `"D"` but will return a `BaseOffset` in a future version (option `future.infer_freq_returns_offset` opts in).

## References

- [01-core-structures](references/01-core-structures.md) — DataFrame, Series, Index constructors and core attributes
- [02-data-types](references/02-data-types.md) — dtypes, nullable types, ArrowDtype, string dtype, type conversion
- [03-io-operations](references/03-io-operations.md) — CSV (parallel reads), Excel, Parquet, SQL, JSON, HTML, XML, pickle
- [04-indexing-selection](references/04-indexing-selection.md) — loc, iloc, select, filter cond, boolean indexing, IndexSlice
- [05-groupby-aggregation](references/05-groupby-aggregation.md) — GroupBy, agg, NamedAgg/NamedFunc, transform, filter, apply
- [06-reshaping-merging](references/06-reshaping-merging.md) — merge, anti-joins, concat, pivot_table, melt, stack/unstack
- [07-timeseries](references/07-timeseries.md) — Timestamp, Timedelta, date_range, resample, offsets, zoneinfo
- [08-window-rolling](references/08-window-rolling.md) — Rolling, Expanding, EWM windows
- [09-accessors](references/09-accessors.md) — .str accessor, .dt accessor, .cat accessor, .array property
- [10-copy-on-write](references/10-copy-on-write.md) — Copy-on-Write semantics, ChainedAssignmentError, migration from v2.x
- [11-v3.1-changes](references/11-v3.1-changes.md) — v3.1.0/v3.1.1 breaking changes, deprecations, new features, migration guide
