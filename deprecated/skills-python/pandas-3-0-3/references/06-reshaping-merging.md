# Reshaping and Merging Reference

`merge`, `concat`, `pivot_table`, `melt`, `stack`/`unstack`, `get_dummies`, and reshape operations.

## Merge (SQL-Style Joins)

### `pd.merge()` / `df.merge()`

```python
# Basic inner join
merged = pd.merge(df1, df2, on="key")

# Left join (keep all rows from left)
merged = pd.merge(df1, df2, on="key", how="left")

# Right join
merged = pd.merge(df1, df2, on="key", how="right")

# Outer join (all rows from both)
merged = pd.merge(df1, df2, on="key", how="outer")

# Anti-join (v3.0+) — rows in left with no match in right
anti = pd.merge(df1, df2, on="key", how="left_anti")
anti = pd.merge(df1, df2, on="key", how="right_anti")

# Different key columns
merged = pd.merge(df1, df2, left_on="user_id", right_on="id")

# Multi-column join
merged = pd.merge(df1, df2, on=["key1", "key2"])

# Suffixes for overlapping columns
merged = pd.merge(df1, df2, on="key", suffixes=("_left", "_right"))

# Indicator column showing source
merged = pd.merge(df1, df2, on="key", indicator=True)
# Adds '_merge' column: "left_only", "right_only", "both"
```

### `df.join()`

Index-based join (convenient for joining on the index).

```python
df1.join(df2, lsuffix="_left", rsuffix="_right")   # Left join on index
df1.join(df2.set_index("key"), on="key")            # Join df2 on df1's "key" column
```

## Concatenation (`pd.concat()`)

Stack DataFrames/Series together.

```python
# Vertical stack (row-wise)
combined = pd.concat([df1, df2, df3], ignore_index=True)

# Horizontal stack (column-wise)
side_by_side = pd.concat([df1, df2], axis=1)

# With keys (creates MultiIndex)
with_keys = pd.concat([df1, df2], keys=["source_a", "source_b"])

# Options
pd.concat([df1, df2], ignore_index=True)    # Reset row index
pd.concat([df1, df2], axis=1, join="inner") # Inner join on columns
pd.concat([df1, df2], sort=False)           # Don't sort columns

# v3.0: ValueError if ignore_index=True and keys is not None
```

## Pivot Table

Spreadsheet-style aggregation.

```python
pt = pd.pivot_table(
    df,
    values="sales",            # Column(s) to aggregate
    index="date",              # Rows
    columns="category",        # Columns
    aggfunc="sum",             # Aggregation function
    margins=True,              # Grand totals
    fill_value=0,              # Replace NA
    dropna=False,              # Keep empty categories
)

# Multiple values with different aggregations
pt = pd.pivot_table(
    df,
    index="date",
    values=["sales", "quantity"],
    aggfunc={"sales": "sum", "quantity": "mean"}
)

# v3.0+: pass kwargs to aggfunc
pt = pd.pivot_table(
    df, values="score", index="cat",
    aggfunc="quantile", q=0.75
)
```

## `df.pivot()`

Unstack without aggregation (errors on duplicate index/column combos).

```python
pivoted = df.pivot(index="date", columns="category", values="value")
# Equivalent to pivot_table with aggfunc=None
```

## Melt (Wide → Long)

Convert wide format to long/tidy format.

```python
# Basic melt
long_df = pd.melt(
    df,
    id_vars=["id", "date"],       # Columns to keep as-is
    value_vars=["a", "b", "c"],   # Columns to unpivot
    var_name="variable",          # Name for the variable column
    value_name="value"            # Name for the value column
)

# Melt all non-id columns
long_df = pd.melt(df, id_vars=["id"], var_name="metric", value_name="reading")
```

## Stack / Unstack

Rotate data between levels of a MultiIndex.

```python
# Stack: columns → index level
long = df.stack()           # Innermost column level → rows
long = df.stack(level=0)    # Specific level

# Unstack: index level → columns
wide = long.unstack()       # Innermost index level → columns
wide = long.unstack(level=-1)  # Specific level

# MultiIndex example
df_with_mi = df.set_index(["date", "category"])
stacked = df_with_mi.stack()      # category level → rows
unstacked = df_with_mi.unstack()  # category level → columns
```

## `get_dummies` / `from_dummies`

One-hot encoding.

```python
# Create dummy variables
dummies = pd.get_dummies(df["category"], prefix="cat")
#   cat_A  cat_B  cat_C
# 0    1      0      0
# 1    0      1      0

# Multiple columns
dummies = pd.get_dummies(df, columns=["category", "region"], drop_first=True)

# Combine with original
df_encoded = pd.concat([df, pd.get_dummies(df["category"])], axis=1)

# Reverse (v3.0+)
original = pd.from_dummies(dummies, default_category="unknown")
```

## `wide_to_long()`

Reshape wide panel data to long format with stub names.

```python
long = pd.wide_to_long(
    df,
    stubnames=["gdp", "pop"],   # Column name prefixes
    i="country",                # ID variable
    j="year",                   # Time variable
    sep="_",                    # Separator between stub and suffix
    suffix=r"\d+"               # Pattern for suffixes (e.g., years)
)
```

## `cut()` / `qcut()`

Bin continuous data into categories.

```python
# Equal-width bins
bins = pd.cut(df["age"], bins=[0, 18, 35, 60, 100],
              labels=["child", "young", "middle", "senior"])

# Equal-frequency (quantile) bins
qbins = pd.qcut(df["income"], q=4)  # Quartiles
# Labels: Q1, Q2, Q3, Q4

# With duplicates in quantiles
qbins = pd.qcut(df["income"], q=4, duplicates="drop")
```

## `lreshape()` (Legacy)

Reshape long format data. Prefer `melt()` for new code.

```python
# Legacy — use melt() instead
reshaped = pd.lreshape(df, {
    "old_name1": ["new_col1_a", "new_col1_b"],
    "old_name2": ["new_col2_a", "new_col2_b"]
})
```

## Merge Patterns

### Self-Join

```python
# Compare rows within the same DataFrame
merged = pd.merge(df, df, on="group_key", suffixes=("_a", "_b"))
```

### Cross Join

```python
# Cartesian product of two DataFrames
merged = pd.merge(df1.assign(key=1), df2.assign(key=1), on="key").drop("key", axis=1)
```

### Conditional Join (Merge Condition Not on Equal Keys)

```python
# Merge where df1.start <= df2.date < df1.end
# Use pd.merge_asof for time-based nearest-key joins
merged = pd.merge_asof(
    df1.sort_values("date"),
    df2.sort_values("date"),
    on="date",
    direction="backward"    # Match to nearest key <= target
)
```

### Ordered Merge

```python
# Merge sorted data, filling forward within groups
merged = pd.merge_ordered(
    df1, df2,
    on="date",
    fill_method="ffill",    # Forward fill missing values
    suffixes=("_lhs", "_rhs")
)
```

## Gotchas

- **Anti-joins are new in v3.0** — `how="left_anti"` and `how="right_anti"`. Not available in earlier versions.
- **`merge` vs `join`** — `merge` joins on columns; `join` joins on index. Use `set_index()` before `join` if needed.
- **`concat` with `ignore_index=True` and `keys` raises ValueError in v3.0** — these are mutually exclusive.
- **`pivot_table` creates NA for missing combinations** — use `fill_value=0` to replace.
- **`melt` without `value_vars` melts all non-id columns** — convenient but watch for unintended columns.
- **`stack`/`unstack` drop NA entries by default** — use `dropna=False` to keep them.
- **`get_dummies` with `drop_first=True` avoids multicollinearity** in regression models.
- **`merge` validates `how` parameter in v3.0** — invalid values raise an error instead of silently defaulting.
