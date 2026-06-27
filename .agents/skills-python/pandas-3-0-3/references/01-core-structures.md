# Core Structures Reference

DataFrame, Series, and Index — the three fundamental pandas objects.

## DataFrame

A 2D labeled table with potentially heterogeneous columns. Each column is a `Series`.

### Construction

```python
# From dict of lists/arrays
df = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "age": [30, 25],
    "score": [85.5, 92.0]
})

# From list of dicts (rows)
df = pd.DataFrame([
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
])

# From numpy array
df = pd.DataFrame(np.random.randn(10, 3), columns=["a", "b", "c"])

# With explicit index and columns
df = pd.DataFrame(data, index=dates, columns=["open", "high", "low", "close"])

# From records (tuples)
df = pd.DataFrame.from_records([("Alice", 30), ("Bob", 25)], columns=["name", "age"])
```

### Key Attributes

| Attribute | Description |
|-----------|-------------|
| `df.shape` | Tuple `(nrows, ncols)` |
| `df.columns` | Index of column labels |
| `df.index` | Index of row labels |
| `df.dtypes` | Series of column dtypes |
| `df.ndim` | Always 2 |
| `df.size` | Total elements (`nrows * ncols`) |
| `df.values` | NumPy array (use `.to_numpy()` preferred) |
| `df.attrs` | Dict for arbitrary metadata propagation |

### Key Methods

```python
# Inspection
df.head(n=5)           # First n rows
df.tail(n=5)           # Last n rows
df.info()              # Summary: dtypes, non-null counts, memory
df.describe()          # Statistical summary of numeric columns
df.shape               # (rows, cols)

# Column operations
df["new_col"] = values             # Add/replace column
df[["a", "b"]]                     # Select multiple columns → DataFrame
df["a"]                            # Select single column → Series
df.drop(columns=["a", "b"])        # Drop columns
df.rename(columns={"old": "new"})  # Rename columns
df.add_prefix("pre_")              # Prefix all column names
df.add_suffix("_post")             # Suffix all column names

# Row operations
df.drop(index=[0, 1])              # Drop rows by index
df.dropna()                        # Drop rows with any NA
df.drop_duplicates(subset=["col"]) # Drop duplicate rows
df.reset_index(drop=True)          # Reset to RangeIndex

# Sorting
df.sort_values("col", ascending=False)
df.sort_values(["a", "b"], ascending=[True, False])
df.sort_index()                    # Sort by index

# Selection
df.loc[row_label, col_label]       # Label-based
df.iloc[row_pos, col_pos]          # Position-based
df.query("age > 25")               # Expression-based filtering
df.eval("new = a + b", inplace=True)  # Expression evaluation
```

### DataFrame Arithmetic

```python
# Element-wise operations (broadcast across columns/rows)
df + 1
df * 2
df["a"] + df["b"]

# Operations between DataFrames (align on index/columns)
df1 + df2                          # NA where labels don't overlap
df1.add(df2, fill_value=0)         # Fill missing with 0 before adding

# Comparison → boolean DataFrame
df["age"] > 25
(df["age"] > 25) & (df["score"] > 80)
```

## Series

A 1D labeled array. Single column of a DataFrame.

### Construction

```python
# From list
s = pd.Series([1, 2, 3, 4])

# With explicit index
s = pd.Series([10, 20, 30], index=["a", "b", "c"])

# From dict (keys become index)
s = pd.Series({"a": 1, "b": 2, "c": 3})

# From scalar (broadcast to index length)
s = pd.Series(5, index=[0, 1, 2, 3])  # all values are 5

# From numpy array
s = pd.Series(np.arange(10))
```

### Key Attributes

| Attribute | Description |
|-----------|-------------|
| `s.values` / `s.to_numpy()` | Underlying NumPy array |
| `s.index` | Index labels |
| `s.dtype` | Data type |
| `s.name` | Name (column name when part of DataFrame) |

### Key Methods

```python
# Inspection
s.head(), s.tail()
s.describe()
s.value_counts()           # Count unique values
s.nunique()                # Number of unique values
s.isna().sum()             # Count missing values

# Transformation
s.astype(float)            # Convert dtype
s.map({"a": 1, "b": 2})    # Map values (like dict lookup)
s.replace("old", "new")    # Replace values
s.clip(lower=0, upper=100) # Clip to range
s.round(2)                 # Round decimals
s.abs()                    # Absolute value

# Aggregation
s.sum(), s.mean(), s.median()
s.min(), s.max()
s.std(), s.var()
s.count()                  # Non-NA count
s.nlargest(5)              # Top 5 values
s.nsmallest(5)             # Bottom 5 values
s.quantile(0.75)           # 75th percentile
s.cumsum(), s.cummax()     # Cumulative operations

# Set operations
s.unique()                 # Unique values
s.isin([1, 2, 3])          # Boolean mask: is value in list?
s.str.split(",").explode() # Split and explode strings
```

## Index Types

All indexes are immutable. Pandas supports several specialized index types.

### Base Index

```python
idx = pd.Index([1, 2, 3, 4])
idx = pd.Index(["a", "b", "c"], name="letters")

# Methods
idx.isin([1, 3])           # Boolean mask
idx.intersection(other)    # Set intersection
idx.union(other)           # Set union
idx.difference(other)      # Set difference
idx.get_loc(label)         # Position of label
```

### DatetimeIndex

```python
# Construction
idx = pd.date_range("2024-01-01", periods=365, freq="D")
idx = pd.DatetimeIndex(["2024-01-01", "2024-06-15", "2024-12-31"])

# Time-based slicing
df.loc["2024-01":"2024-03"]         # Partial string indexing
df.loc["2024-01-15"]                # Single day
df.loc["2024-Q1"]                   # Quarter (if supported)

# Time components via .dt accessor
idx.year, idx.month, idx.day
idx.hour, idx.minute, idx.second
idx.dayofweek, idx.dayofyear
idx.is_month_start, idx.is_year_end
```

### MultiIndex

Hierarchical index for multi-level row/column labels.

```python
# Construction
mi = pd.MultiIndex.from_tuples([
    ("A", "x"), ("A", "y"), ("B", "x"), ("B", "y")
], names=["group", "subgroup"])

# Or from product
mi = pd.MultiIndex.from_product([["A", "B"], ["x", "y", "z"]])

# From existing columns
df.set_index(["group", "subgroup"])
df.stack()                         # Columns → MultiIndex rows
df.unstack()                       # MultiIndex rows → columns

# Slicing with IndexSlice
idx = pd.IndexSlice
df.loc[idx["A", :], :]             # All of group A
df.loc[idx[:, "x"], :]             # All subgroup x across groups
df.loc[idx["A":"B", "x":"y"], :]  # Range slice

# Operations
mi.levels                            # Unique values per level
mi.get_level_values(0)               # Values at level 0
mi.swaplevel()                       # Swap two levels
mi.droplevel(0)                      # Drop a level
```

### CategoricalIndex

```python
idx = pd.CategoricalIndex(["low", "med", "high", "low"],
                           categories=["low", "med", "high"],
                           ordered=True)
idx.categories                       # Available categories
idx.ordered                          # Whether categories are ordered
```

### RangeIndex

Auto-generated integer index (default when no index specified).

```python
# Most DataFrames use this by default
df.index  # RangeIndex(start=0, stop=100, step=1)
```

## NDFrame Base (Shared by DataFrame and Series)

Both inherit from `NDFrame`, sharing these methods:

```python
# Missing data
obj.isna(), obj.notna()
obj.dropna(axis=0, how="any", thresh=None)
obj.fillna(value)
obj.bfill(), obj.ffill()            # Back/forward fill

# Duplicates
obj.duplicated(keep="first")        # Boolean mask of duplicates
obj.drop_duplicates()

# Sorting
obj.sort_values(by, ascending=True)
obj.sort_index(ascending=True)

# Apply operations
obj.apply(func)                      # Apply function along axis
obj.map(func)                        # Series: element-wise map

# Pipe (method chaining)
obj.pipe(np.sort)
df.pipe(my_custom_function)

# Reindexing
obj.reindex(new_index)              # Conform to new index
obj.rename(index={old: new})        # Rename index labels
obj.set_axis(new_labels)            # Replace axis labels entirely
```
