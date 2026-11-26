# Copy-on-Write Reference

Copy-on-Write (CoW) semantics in pandas 3.0, migration from v2.x, and common pitfalls.

## What Changed in v3.0

Pandas 3.0 makes Copy-on-Write the default and only behavior. The `mode.copy_on_write` option is deprecated and has no effect.

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

### The v3.0 Rule

```python
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

# Always behaves as a copy
subset = df[df["a"] > 1]
subset["b"] = 100
# df is NEVER modified. No warning. Consistent behavior.

# To modify the original, use .loc directly:
df.loc[df["a"] > 1, "b"] = 100  # This works
```

## Key Behavioral Changes

### 1. Chained Assignment No Longer Works

```python
# v2.x: sometimes worked, sometimes warned
df[df["a"] > 1]["b"] = 100

# v3.0: silently modifies a copy — df is unchanged
df[df["a"] > 1]["b"] = 100  # WRONG — no effect on df

# v3.0 correct pattern:
df.loc[df["a"] > 1, "b"] = 100  # Always works
```

### 2. `SettingWithCopyWarning` Removed

The warning is gone because the behavior is now consistent. If you were using `.copy()` to silence it, those calls are no longer necessary (but harmless).

### 3. Column Access Behaves as Copy

```python
# v3.0: accessing a column behaves as a copy
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

## Migration from v2.x

### Pattern Replacements

| v2.x Pattern | v3.0 Replacement |
|---|---|
| `df[mask]["col"] = val` | `df.loc[mask, "col"] = val` |
| `df[["a"]]["b"] = val` | Not applicable — select and assign separately |
| `df.iloc[mask]["col"] = val` | `df.iloc[mask, df.columns.get_loc("col")] = val` |
| `subset = df[...]; subset[...] = ...` (expecting original modified) | Use `.loc` on original |
| `pd.options.mode.copy_on_write = True` | Remove — always on in v3.0 |

### Common Fix: Chained Assignment

```python
# WRONG (v3.0): modifies a copy
df[df["category"] == "A"]["value"] = 0

# CORRECT (v3.0): use .loc
df.loc[df["category"] == "A", "value"] = 0

# Also correct: assign new column
df["value"] = df["value"].where(df["category"] != "A", 0)
```

### Common Fix: Column Modification

```python
# WRONG (v3.0): modifies a copy
col = df["price"]
col = col * 1.1  # This is fine — reassignment
# But df["price"] is unchanged!

# CORRECT: assign back to DataFrame
df["price"] = df["price"] * 1.1

# Or use .loc
df.loc[:, "price"] = df["price"] * 1.1
```

## How CoW Works Internally

Pandas uses lazy copying under the hood:

1. **Indexing returns a view** (memory-efficient, no data copied)
2. **On write, pandas checks if the data is shared**
3. **If shared, it copies before writing** (the "copy-on-write" step)
4. **This guarantees the original is never modified unexpectedly**

This means CoW gives you *consistent semantics* while maintaining *memory efficiency*.

## `ChainedAssignmentError`

In v3.0, pandas can detect some chained assignment patterns and raise a clear error:

```python
pd.options.mode.chained_assignment = "raise"  # "warn" (default) or "raise" or None

# This raises ChainedAssignmentError
df[df["a"] > 0]["b"] = 1
```

Set to `"raise"` during development to catch problematic patterns early.

## Performance Considerations

CoW is designed to be performant:

- **No unnecessary copies** — data is only copied when a write would affect shared data
- **Read operations are free** — views are used internally
- **Single-owner writes avoid copy overhead** — if no other object references the data, writes proceed directly

### When CoW Copies

```python
df = pd.DataFrame({"a": [1, 2, 3]})
view = df["a"]                     # No copy (shared reference)
view.iloc[0] = 99                  # Copy triggered! view gets its own data
# df["a"] is unchanged
```

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
- **`inplace=True` is discouraged** — many methods still support it, but it can interact unpredictably with CoW. Prefer reassignment: `df = df.method()`.
- **`pd.options.mode.copy_on_write` is deprecated** — will be removed in v4.0. Don't set it.
- **Defensive `.copy()` calls are harmless but unnecessary** — every indexing result already behaves as a copy.
- **`ChainedAssignmentError` only catches some patterns** — not all chained assignment is detected. Use `mode.chained_assignment = "raise"` to catch more during development.
- **Views in NumPy arrays accessed via `.values` bypass CoW** — use `.to_numpy()` for explicit copies, or be aware that modifying `.values` directly can affect the original.
