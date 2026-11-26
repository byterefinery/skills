# Indexing and Selection Reference

`loc`, `iloc`, `at`, `iat`, `select`, `filter`, boolean indexing, slicing, and the `IndexSlice` helper.

## Label-Based: `.loc`

Select by row/column labels. Includes the stop bound in slices.

```python
# Single label
df.loc[0]                    # Row with index label 0 → Series
df.loc[:, "col"]             # Column "col" → Series
df.loc[0, "col"]             # Single value

# Multiple labels
df.loc[[0, 2, 4]]            # Rows with labels 0, 2, 4
df.loc[:, ["a", "b"]]        # Columns a and b
df.loc[[0, 1], ["a", "b"]]   # Specific rows and columns

# Label slicing (inclusive on both ends)
df.loc["2024-01-01":"2024-03-31"]   # Date range
df.loc["A":"C"]                   # Alphabetical range

# Boolean mask
df.loc[df["age"] > 25]
df.loc[df["age"] > 25, "name"]     # Names where age > 25
df.loc[df["age"] > 25, ["name", "score"]]

# Setting values
df.loc[0, "col"] = new_value
df.loc[mask, "col"] = new_value

# With pd.col() (v3.0+)
from pandas import col
df.loc[col("age") > 25]
```

## Position-Based: `.iloc`

Select by integer position. Standard Python slicing (exclusive stop).

```python
# Single position
df.iloc[0]                    # First row → Series
df.iloc[0, 0]                 # Top-left value
df.iloc[:, 0]                 # First column → Series

# Multiple positions
df.iloc[[0, 2, 4]]            # Rows at positions 0, 2, 4
df.iloc[:, [0, 2]]            # Columns at positions 0, 2
df.iloc[0:3, 1:4]             # Slice: rows 0-2, cols 1-3

# Boolean mask
df.iloc[mask]                  # Boolean array for row selection

# Negative indexing
df.iloc[-1]                   # Last row
df.iloc[:-1]                  # All but last row
```

## Scalar Access: `.at` / `.iat`

Fast scalar access (single value by label or position).

```python
df.at[0, "col"]               # Fast single value by label
df.iat[0, 0]                  # Fast single value by position
df.at[0, "col"] = new_value   # Fast scalar assignment
```

v3.1 notes:
- Setting values with a non-scalar indexer (boolean mask, list, array) raises a clearer `InvalidIndexError` directing you to `.loc`
- Setting a value at a key that does not exist (expanding the object) is deprecated — use `.loc`

## Column Selection (Bracket Notation)

```python
df["col"]                     # Single column → Series
df[["a", "b"]]                # Multiple columns → DataFrame
df[df["age"] > 25]            # Boolean mask → filtered DataFrame
```

**Avoid**: `df.col` attribute-style access. It works but conflicts with DataFrame methods (e.g., `df.min` shadows `.min()`).

## `DataFrame.select` (v3.1+)

Select a subset of columns by label, `pd.col()` expression, or callable keyword arguments. Later arguments can refer to columns computed earlier in the same call (like `assign`).

```python
from pandas import col

# By label
df.select("first_name", "last_name")

# With computed columns via pd.col() expressions
df.select("first_name", col("age"), age_months=col("age") * 12)

# Chained computed columns — age_days refers to age_months from the same call
df.select(
    "first_name",
    age_months=col("age") * 12,
    age_days=col("age_months") * 30,
)
```

## Boolean-Mask Filtering: `filter(cond=)` (v3.1+)

`DataFrame.filter` and `Series.filter` accept a boolean mask through the `cond` keyword, keeping rows where the mask is True (columns with `axis=1`). `cond` may be a mask, a callable returning a mask, or a `pd.col()` expression — the latter two also work positionally.

```python
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

# Mask as cond
df.filter(cond=df["a"] > 1)

# pd.col expression (positional in chains)
df.filter(col("a") > 1)

# Callable
df.filter(lambda d: d["b"] < 6)

# Missing values in the mask default to False; na=True keeps them, na="raise" raises
mask = pd.array([True, None, False], dtype="boolean")
df.filter(cond=mask, na=True)
```

Note: any other value passed positionally to `filter` still selects labels (as before). A list-like of booleans passed positionally now issues a `UserWarning` — pass `items=` to select labels or `cond=` to filter.

## Boolean Indexing

```python
# Single condition
mask = df["age"] > 25
df[mask]

# Multiple conditions (use & | ~, not and/or/not)
mask = (df["age"] > 25) & (df["score"] > 80)
df[mask]

# Negation
df[~df["name"].isin(exclude_list)]

# Using .query()
df.query("age > 25 and score > 80")
df.query("name in @exclude_list")    # @ references Python variables

# Using .eval()
df = df.eval("ratio = score / max_score")   # reassign; inplace= deprecated in 3.1
```

## Slicing Patterns

### Partial String Indexing (DatetimeIndex)

```python
df.loc["2024"]                    # All of 2024
df.loc["2024-01"]                 # January 2024
df.loc["2024-01-15"]              # Specific day
df.loc["2024-01":"2024-03"]       # Jan to Mar 2024
```

### MultiIndex Slicing

```python
# Cross-section
df.xs("A", level="group")         # All rows where group == "A"
df.xs("A", level="group", axis=1) # Columns at level "group" == "A"

# IndexSlice for clean multi-level slicing
idx = pd.IndexSlice
df.loc[idx["A", :], :]            # Group A, all subgroups
df.loc[idx[:, "x"], :]            # All groups, subgroup x
df.loc[idx["A":"B", "x":"y"], :] # Range across both levels
```

## Reindexing

Conform to a new index (introduces NA for missing labels).

```python
# Series
s.reindex([0, 1, 2, 3, 4])
s.reindex(new_index, fill_value=0)
s.reindex(new_index, method="ffill")   # Forward fill gaps
```

Note (v3.1): automatic dtype promotion when reindexing with a `fill_value` that cannot be held by the original dtype is deprecated — cast to a common dtype explicitly.

## Aligning Two Objects

```python
s1, s2 = s1.align(s2)              # Align on common index
df1, df2 = df1.align(df2, join="outer")  # Outer join alignment
df1, df2 = df1.align(df2, join="inner")  # Inner join (common labels only)
```

## Selecting by Type / Pattern

```python
# Select columns by dtype (see 02-data-types for v3.1 strictness rules)
df.select_dtypes(include=["number"])
df.select_dtypes(include=["int64", "float64"])
df.select_dtypes(exclude=["object"])
df.select_dtypes(include="datetime64")

# Select columns by name pattern (label selection via filter)
df.filter(like="revenue")           # Columns containing "revenue"
df.filter(regex="^col_")            # Columns starting with "col_"
df.filter(items=["a", "b", "c"])    # Specific column names
```

## Sampling

```python
# Random rows
df.sample(n=10)                     # 10 random rows
df.sample(frac=0.1)                 # 10% of rows
df.sample(n=10, random_state=42)    # Reproducible
df.sample(weights=df["weight_col"]) # Weighted sampling
```

## First / Last N

```python
df.head(5)                          # First 5 rows
df.tail(5)                          # Last 5 rows
df.first("5D")                      # First 5 days (DatetimeIndex)
df.last("1M")                       # Last month (DatetimeIndex)
```

## Cross-Section (`xs`)

Select data at a particular level of a MultiIndex.

```python
# Row cross-section
df.xs("2024", level="year")
df.xs(("A", "x"), level=["group", "subgroup"])

# Column cross-section
df.xs("revenue", axis=1, level="metric")
```

## Gotchas

- **`.loc` slices are inclusive on both ends** — `df.loc[0:5]` includes row 5. `.iloc` follows standard Python slicing (exclusive stop).
- **Setting with `.loc` is the safe pattern** — always use `df.loc[mask, "col"] = value`, never `df[mask]["col"] = value` (chained assignment does not update the original).
- **`.at` and `.iat` are faster for scalar access** but only work with single labels/positions; non-scalar indexers now raise `InvalidIndexError`.
- **Boolean indexing returns a copy** due to Copy-on-Write. Modify via `.loc` on the original.
- **`select` is for columns only** — row filtering still goes through masks, `query`, or `filter(cond=)`.
- **`filter(items/like/regex)` is label selection, not row filtering** — the new `cond=` keyword does row masking; mixing the two up is a common mistake.
- **Partial string indexing only works on sorted DatetimeIndex** — sort first with `df.sort_index()`.
