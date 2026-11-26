# Copy-on-Write Reference

Copy-on-Write (CoW) semantics in pandas 3.x, the `ChainedAssignmentError` warning, and common pitfalls.

## What CoW Means

Pandas 3.0 made Copy-on-Write the only behavior (the `mode.copy_on_write` option is deprecated and will be removed in 4.0).

### Core Principle

> Every indexing operation *behaves as if* it returns a copy. Modifications to the result never affect the original.

This eliminates the ambiguity of "is this a view or a copy?" that plagued earlier versions.

## Before v3.0 vs After

### The Old Problem (v2.x)

```python
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

# Was this a view or a copy? It depended on the operation.
subset = df[df["a"] > 1]
subset["b"] = 100
# Sometimes modified df, sometimes didn't → SettingWithCopyWarning
```

### The v3.0+ Rule

```python
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

# Always behaves as a copy
subset = df[df["a"] > 1]
subset["b"] = 100
# df is NEVER modified. Consistent behavior.

# To modify the original, use .loc directly:
df.loc[df["a"] > 1, "b"] = 100  # This works
```

## Key Behavioral Changes

### 1. Chained Assignment Does Not Update the Original

```python
# v2.x: sometimes worked, sometimes warned
df[df["a"] > 1]["b"] = 100

# v3.x: modifies a copy — df is unchanged
df[df["a"] > 1]["b"] = 100  # WRONG — no effect on df

# Correct pattern:
df.loc[df["a"] > 1, "b"] = 100  # Always works
```

### 2. `SettingWithCopyWarning` Removed (v3.0)

The warning is gone because the behavior is now consistent. Since v3.1, chained assignment emits `ChainedAssignmentError` instead (see below). If you used `.copy()` to silence the old warning, those calls are no longer necessary (but harmless).

### 3. Column Access Behaves as Copy

```python
# v3.x: accessing a column behaves as a copy
col = df["b"]
col[0] = 999  # Does NOT modify df

# Modify through the original
df.loc[0, "b"] = 999  # This works
```

### 4. `.copy()` Still Available

Use `.copy()` when you explicitly need an independent object:

```python
independent = df.copy()       # Deep copy
independent = df.copy(deep=False)  # Shallow copy
```

### 5. Lossy `.values` Deprecated (v3.1)

`.values` on three dtypes returns a NumPy array that loses information and now emits `Pandas4Warning`:

- `DatetimeTZDtype` — tz dropped, converted to UTC
- `PeriodDtype` — object array of `Period`
- `IntervalDtype` (Series) — object array of `Interval`

In pandas 4.0, `.values` will return the ExtensionArray for these dtypes too.

```python
ser = pd.Series(pd.date_range("2016-01-01", periods=2, tz="US/Pacific"))

# Preferred: ExtensionArray
ser.array

# NumPy array of Timestamp objects (tz-aware data)
ser.to_numpy()

# Keep the old tz-dropped UTC result explicitly
ser.dt.tz_convert(None).to_numpy()
ser.to_numpy(dtype="datetime64[us]")
```

`DataFrame.values` and `np.asarray(ser)` are unaffected (they already returned object-dtype arrays in these cases).

## `ChainedAssignmentError` (v3.1)

Chained assignment emits `ChainedAssignmentError`, a subclass of `Warning` (verified in `pandas/errors`). The old `mode.chained_assignment` option is deprecated — use the standard warnings machinery:

```python
import warnings
from pandas.errors import ChainedAssignmentError

# Default: emit the warning
df[df["a"] > 0]["b"] = 1  # ChainedAssignmentError emitted

# Silence it
warnings.filterwarnings("ignore", category=ChainedAssignmentError)

# Turn it into an error (useful during development)
warnings.filterwarnings("error", category=ChainedAssignmentError)
```

Not all chained assignment patterns are detected; the warning is best-effort.

## Migration from v2.x

### Pattern Replacements

| v2.x Pattern | v3.x Replacement |
|---|---|
| `df[mask]["col"] = val` | `df.loc[mask, "col"] = val` |
| `subset = df[...]; subset[...] = ...` (expecting original modified) | Use `.loc` on original |
| `pd.options.mode.copy_on_write = True` | Remove — always on |
| `mode.chained_assignment = "raise"` (v3.0) | `warnings.filterwarnings("error", category=ChainedAssignmentError)` |

### Common Fix: Chained Assignment

```python
# WRONG (v3.x): modifies a copy
df[df["category"] == "A"]["value"] = 0

# CORRECT: use .loc
df.loc[df["category"] == "A", "value"] = 0

# Also correct: assign new column
df["value"] = df["value"].where(df["category"] != "A", 0)
```

### Common Fix: Column Modification

```python
# WRONG: reassigning a local does not touch the DataFrame
col = df["price"]
col = col * 1.1  # df["price"] is unchanged

# CORRECT: assign back to the DataFrame
df["price"] = df["price"] * 1.1
```

## How CoW Works Internally

Pandas uses lazy copying under the hood:

1. **Indexing returns a view** (memory-efficient, no data copied)
2. **On write, pandas checks if the data is shared**
3. **If shared, it copies before writing** (the "copy-on-write" step)
4. **This guarantees the original is never modified unexpectedly**

CoW gives *consistent semantics* while maintaining *memory efficiency*.

## Performance Considerations

- **No unnecessary copies** — data is only copied when a write would affect shared data
- **Read operations are free** — views are used internally
- **Single-owner writes avoid copy overhead** — if no other object references the data, writes proceed directly

### Avoiding Unnecessary Copies

```python
# If you need to modify a subset independently, use .copy() explicitly
subset = df.loc[mask].copy()
subset["new_col"] = values  # No CoW overhead — independent object

# For large transformations, work on the original directly
df.loc[:, "transformed"] = some_function(df["raw"])
```

## Gotchas

- **`df["col"] = df["col"].method()` works fine** — the right side creates a new Series, assignment replaces the column.
- **Method chaining after indexing returns a copy** — `df.loc[mask].sort_values("a")` returns an independent DataFrame.
- **`inplace=True` is deprecated in 3.1** for methods that don't work inplace (`drop`, `rename`, `rename_axis`, `reset_index`, `set_index`, `dropna`, `drop_duplicates`, `sort_values`, `sort_index`, `eval`, `query`) — reassign the result: `df = df.reset_index()`.
- **`pd.options.mode.copy_on_write` is deprecated** — removed in v4.0. Don't set it.
- **Defensive `.copy()` calls are harmless but unnecessary** — every indexing result already behaves as a copy.
- **`ChainedAssignmentError` only catches some patterns** — not all chained assignment is detected.
- **`Index.values` / `Index.array` return read-only arrays (v3.1)** — you can no longer corrupt an Index by mutating the returned array.
