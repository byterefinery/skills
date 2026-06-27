# GroupBy and Aggregation Reference

Split-apply-combine operations: `groupby`, aggregation, transformation, filtering.

## Basic GroupBy

```python
# Single column grouping
gb = df.groupby("category")

# Multiple columns
gb = df.groupby(["region", "category"])

# With sort=False for performance (default True)
gb = df.groupby("category", sort=False)

# Group by index level
gb = df.groupby(level=0)
gb = df.groupby(level="date", axis=1)  # Column grouping

# Group by Grouper (e.g., date bins)
gb = df.groupby(pd.Grouper(key="date", freq="M"))
```

## Aggregation (`.agg()`)

Reduce each group to a single value per group.

### Single Aggregation

```python
df.groupby("category")["score"].mean()
df.groupby("category").size()       # Group sizes (including NA groups)
df.groupby("category").count()      # Non-NA counts per column
```

### Multiple Aggregations with NamedAgg

```python
# Dict of aggregations
df.groupby("category").agg(
    {"score": ["mean", "std", "count"],
     "age": "median"}
)

# NamedAgg for custom output column names (v3.0 supports *args/**kwargs)
from pandas import NamedAgg
result = df.groupby("category").agg(
    avg_score=NamedAgg("score", "mean"),
    total=NamedAgg("score", "sum"),
    count=NamedAgg("score", "count"),
    median_age=NamedAgg("age", "median"),
    # v3.0: pass args/kwargs to aggfunc
    custom_stat=NamedAgg("score", "quantile", q=0.75),
)
```

### Common Aggregation Functions

| Function | Description |
|----------|-------------|
| `"sum"` / `.sum()` | Sum of values |
| `"mean"` / `.mean()` | Arithmetic mean |
| `"median"` / `.median()` | Median |
| `"count"` / `.count()` | Non-NA count |
| `"size"` / `.size()` | Total count (including NA) |
| `"std"` / `.std()` | Standard deviation |
| `"var"` / `.var()` | Variance |
| `"min"` / `.min()` | Minimum |
| `"max"` / `.max()` | Maximum |
| `"first"` / `.first()` | First value |
| `"last"` / `.last()` | Last value |
| `"nunique"` / `.nunique()` | Count of unique values |
| `"sem"` / `.sem()` | Standard error of mean |
| `"kurt"` / `.kurt()` | Kurtosis (v3.0+) |
| `"quantile"` | Quantile (pass `q=` kwarg) |

### Aggregation with `skipna` (v3.0+)

```python
df.groupby("cat").sum(skipna=False)    # NA propagates if any value is NA
df.groupby("cat").mean(skipna=True)    # Default: skip NAs
```

## Transformation (`.transform()`)

Return an object the same size as the input, with values transformed per group.

```python
# Normalize within groups
df["zscore"] = df.groupby("category")["score"].transform(
    lambda x: (x - x.mean()) / x.std()
)

# Common transforms
df.groupby("cat")["val"].transform("mean")     # Group mean broadcast
df.groupby("cat")["val"].transform("rank")      # Rank within group
df.groupby("cat")["val"].transform("cumsum")    # Cumulative sum within group
df.groupby("cat")["val"].transform("fillna", method="bfill")

# v3.0+: positional args as kwargs
df.groupby("cat")["val"].transform("quantile", q=0.5)
```

## Filtering (`.filter()`)

Keep/drop groups based on a condition.

```python
# Keep groups with more than 10 members
df.groupby("category").filter(lambda g: len(g) > 10)

# Keep groups where mean score > 80
df.groupby("category").filter(lambda g: g["score"].mean() > 80)
```

## Apply (`.apply()`)

Apply an arbitrary function to each group. Most flexible but slowest.

```python
# Custom function
def top_n(group, n=3):
    return group.nlargest(n, "score")

df.groupby("category").apply(top_n, n=3)

# Group-wise regression
import numpy as np
def linear_fit(group):
    slope, intercept = np.polyfit(group["x"], group["y"], 1)
    return pd.Series({"slope": slope, "intercept": intercept})

df.groupby("category").apply(linear_fit)

# v3.0+: positional args as kwargs
df.groupby("cat").apply(my_func, arg1, kwarg1=value)
```

## Iterating Over Groups

```python
for name, group in df.groupby("category"):
    print(f"Group {name}: {len(group)} rows")
    process(group)

# Access groups as dict
groups = dict(list(df.groupby("category")))
```

## GroupBy on Multiple Columns

```python
# Multi-level grouping
result = df.groupby(["region", "category"]).agg(
    total_sales=("sales", "sum"),
    avg_price=("price", "mean")
)
# Result has MultiIndex on (region, category)

# Reset to flat columns
result.reset_index()
```

## Cross-Tabulation (`pd.crosstab`)

Quick frequency table.

```python
ct = pd.crosstab(df["category"], df["region"])
ct = pd.crosstab(
    df["category"], df["region"],
    values=df["sales"],
    aggfunc="sum",
    margins=True,               # Add totals row/column
    normalize=True,             # Normalize to proportions
)
```

## Pivot Table (`pd.pivot_table`)

Spreadsheet-style pivot.

```python
pt = pd.pivot_table(
    df,
    values="sales",
    index="date",
    columns="category",
    aggfunc="sum",
    margins=True,               # Grand totals
    fill_value=0,               # Replace NA with 0
    dropna=False,               # Keep empty categories
)

# v3.0+: pass kwargs to aggfunc
pt = pd.pivot_table(
    df, values="score", index="cat",
    aggfunc="quantile", q=0.75
)
```

## Resampling (Time Series GroupBy)

Group by time frequency. See [07-timeseries](07-timeseries.md) for details.

```python
df.resample("M").sum()
df.resample("D").mean()
df.resample("W-SUN").agg({"sales": "sum", "price": "mean"})
```

## ngroup / ngroup Transform

```python
# Assign group numbers (0-indexed)
df["group_num"] = df.groupby("category").ngroup()

# Within-group row number
df["row_in_group"] = df.groupby("category").cumcount()
```

## Gotchas

- **`size()` vs `count()`** — `size()` counts all rows including those with NA; `count()` counts non-NA values per column.
- **`agg` with string names is faster** than lambdas. Use `"mean"` instead of `lambda x: x.mean()`.
- **`apply` drops the group key from result index** by default in some cases. Use `include_groups=False` (default) to exclude, or `True` to include.
- **Chained assignment after groupby fails** — use `.transform()` to broadcast results back to original shape, then assign via `.loc`.
- **GroupBy preserves NA groups by default** — use `dropna=True` in `groupby()` to exclude groups where the key is NA.
- **`sort=True` (default) sorts group keys** which can be expensive on large data. Use `sort=False` when order doesn't matter.
