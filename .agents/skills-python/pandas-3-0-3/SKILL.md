---
name: pandas-3-0-3
description: >
  Pandas 3.0.3 data manipulation and analysis library for Python. Use when working
  with DataFrames, Series, data wrangling, CSV/Excel/Parquet I/O, groupby aggregations,
  merging/joining, time series, resampling, rolling windows, string operations, or any
  tabular data processing in Python. Covers pandas 3.0 semantics including dedicated
  string dtype by default, Copy-on-Write behavior, pd.col() expressions, Arrow PyCapsule
  interface, and anti-joins. Trigger on: DataFrame, Series, read_csv, merge, groupby,
  pivot_table, resample, rolling, time series analysis, ETL pipelines, data cleaning,
  or any mention of pandas dataframes.
metadata:
  tags:
    - python
    - data-analysis
    - etl
    - tabular-data
---

# pandas 3.0.3

## Overview

Pandas is the foundational Python library for tabular data manipulation and analysis. Version 3.0.3 introduces major semantic shifts from earlier versions: dedicated string dtype by default, consistent Copy-on-Write behavior (no more `SettingWithCopyWarning`), `pd.col()` expression syntax, Arrow PyCapsule Interface support, and anti-joins in merge operations.

### Core Objects

- **DataFrame** — 2D labeled table with heterogeneous columns
- **Series** — 1D labeled array (single column of a DataFrame)
- **Index** — immutable label axis (includes DatetimeIndex, MultiIndex, CategoricalIndex, etc.)

### Key v3.0 Changes

1. **String dtype by default** — `pd.Series(["a", "b"])` now yields `dtype: str` instead of `object`
2. **Copy-on-Write** — all indexing returns views that *behave as copies*; chained assignment no longer works; `SettingWithCopyWarning` removed
3. **`pd.col()` expressions** — column references without lambdas in `assign`, `loc`, etc.
4. **Arrow PyCapsule Interface** — zero-copy data exchange with Arrow-compatible libraries via `from_arrow()` and `__arrow_c_stream__`
5. **Anti-joins** — `merge(how="left_anti")` and `merge(how="right_anti")` now supported

### Dependencies

- **Required**: `numpy>=1.26.0`, `python-dateutil>=2.8.2`, `tzdata` (Windows/Pyodide)
- **Python versions**: 3.11, 3.12, 3.13, 3.14
- **Optional**: `pyarrow>=13.0.0` (Parquet, Feather, ORC, Arrow-backed dtypes), `bottleneck`, `numexpr`, `scipy`, `xarray`, `fsspec`, `s3fs`, `gcsfs`

## Usage

```python
import pandas as pd
import numpy as np

# Create a DataFrame
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [30, 25, 35],
    "score": [85.5, 92.0, 78.3]
})

# String dtype is now default (v3.0)
df["name"].dtype  # str (not object)

# Read data
df = pd.read_csv("data.csv")
df = pd.read_parquet("data.parquet")

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

# Merge / join
merged = pd.merge(df1, df2, on="key", how="left")
anti = pd.merge(df1, df2, on="key", how="left_anti")  # v3.0 new

# Reshaping
pivoted = df.pivot_table(index="date", columns="category", values="value", aggfunc="sum")
melted = pd.melt(df, id_vars=["id"], value_vars=["a", "b", "c"])

# Time series
ts = pd.read_csv("data.csv", parse_dates=["date"])
ts = ts.set_index("date").sort_index()
resampled = ts.resample("M").sum()

# Rolling windows
rolling_avg = df["value"].rolling(window=7).mean()

# Export
df.to_csv("output.csv", index=False)
df.to_parquet("output.parquet")
```

### `pd.col()` Expression Syntax (v3.0+)

Use `pd.col()` instead of lambdas for column references:

```python
# Instead of:
df.assign(total=lambda d: d["a"] + d["b"])

# Write:
from pandas import col
df.assign(total=col("a") + col("b"))

# In loc (filtering):
df.loc[col("age") > 25]

# Chained expressions:
df.assign(
    ratio=col("score") / col("max_score"),
    label=(col("ratio") > 0.8).map({True: "high", False: "low"})
)
```

### Copy-on-Write (v3.0+)

Every indexing operation *behaves as a copy*. Modify the original object directly:

```python
# v3.0 correct — modify original directly
df.loc[mask, "col"] = value

# Chained assignment does NOT work in v3.0 (no warning, just silently fails to update)
df[df["age"] > 25]["score"] = 100  # WRONG — this modifies a copy

# Use .copy() explicitly when you need an independent object
subset = df.loc[mask].copy()
```

## Gotchas

- **String dtype is default in v3.0** — code checking for `dtype == "object"` to find strings will break. Use `is_string_dtype()` or check for `"str"` dtype instead.
- **Chained assignment silently fails** — `df[df["a"] > 0]["b"] = 1` modifies a copy, not the original. Always use `.loc[row_mask, "col"] = value`.
- **No `SettingWithCopyWarning`** — it was removed in v3.0 since Copy-on-Write makes the behavior consistent.
- **`pd.NA` vs `np.nan`** — the universal missing value sentinel is `pd.NA` for nullable dtypes. String dtype uses `np.nan` as its NA sentinel by default.
- **`mode.copy_on_write` option deprecated** — Copy-on-Write is always on in v3.0. The option will be removed in v4.0.
- **`pytz` replaced by `zoneinfo`** — time zones now use the standard library's `zoneinfo` module. Use `pd.Timestamp("2024-01-01", tz="America/New_York")` instead of `pytz.timezone()`.
- **Arrow-backed string dtype** — if PyArrow is installed, string columns are Arrow-backed by default. This affects `.dtype` representation and some operations.
- **`read_csv` engine defaults** — the C engine is still default, but specifying `engine="pyarrow"` gives Arrow-native parsing with different behavior for some edge cases.
- **`merge` anti-joins** — `how="left_anti"` keeps rows from left that have no match in right. Useful for finding missing records.
- **`fillna(value=None)` now works** — passes the dtype-appropriate NA value instead of raising an error.

## References

- [01-core-structures](references/01-core-structures.md) — DataFrame, Series, Index constructors and core attributes
- [02-data-types](references/02-data-types.md) — dtypes, nullable types, ArrowDtype, string dtype, type conversion
- [03-io-operations](references/03-io-operations.md) — CSV, Excel, Parquet, SQL, JSON, HTML, XML, pickle, clipboard
- [04-indexing-selection](references/04-indexing-selection.md) — loc, iloc, at, iat, boolean indexing, slicing, IndexSlice
- [05-groupby-aggregation](references/05-groupby-aggregation.md) — GroupBy, agg, transform, filter, apply, NamedAgg
- [06-reshaping-merging](references/06-reshaping-merging.md) — merge, concat, pivot_table, melt, stack/unstack, get_dummies
- [07-timeseries](references/07-timeseries.md) — Timestamp, Timedelta, date_range, resample, offset, holiday calendars
- [08-window-rolling](references/08-window-rolling.md) — Rolling, Expanding, EWM windows; first/last/nunique (v3.0)
- [09-accessors](references/09-accessors.md) — .str accessor, .dt accessor, .cat accessor, .array property
- [10-copy-on-write](references/10-copy-on-write.md) — Copy-on-Write semantics, migration from v2.x, common pitfalls
- [11-v3-changes](references/11-v3-changes.md) — Full v3.0 breaking changes, deprecations, new features, migration guide
