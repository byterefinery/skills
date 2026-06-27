# Window and Rolling Operations Reference

Rolling, expanding, and exponential moving window operations.

## Rolling Windows

Compute statistics over a sliding window of observations.

### Fixed-Size Windows

```python
# Basic rolling mean
df["ma_7"] = df["value"].rolling(window=7).mean()

# Multiple aggregations
result = df["value"].rolling(7).agg(["mean", "std", "min", "max"])

# Min periods (default equals window size)
df["value"].rolling(7, min_periods=1).mean()  # Start computing after 1 value

# Centered window
df["value"].rolling(7, center=True).mean()    # Window centered on current row

# With closed interval
df["value"].rolling(7, closed="both").sum()   # "both", "left", "right", "neither"
```

### Time-Based Windows (DatetimeIndex required)

```python
# Rolling by time span
df.rolling("7D").mean()       # 7 calendar days
df.rolling("24H").sum()       # 24 hours
df.rolling("30min").max()     # 30 minutes
df.rolling("5D", min_periods=1).mean()

# Business day window
df.rolling("5B").mean()       # 5 business days
```

### Rolling on Grouped Data

```python
df.groupby("category")["value"].rolling(7).mean()
df.groupby("category")["value"].rolling("30D").sum()
```

### Common Rolling Methods

| Method | Description |
|--------|-------------|
| `.mean()` | Moving average |
| `.sum()` | Moving sum |
| `.std()` | Moving standard deviation |
| `.var()` | Moving variance |
| `.min()` / `.max()` | Moving min/max |
| `.median()` | Moving median |
| `.count()` | Count of non-NA values in window |
| `.corr(other)` | Rolling correlation with another series |
| `.cov(other)` | Rolling covariance |
| `.apply(func)` | Custom function applied to each window |
| `.agg([func1, func2])` | Multiple aggregations |
| `.first()` | First value in window (v3.0+) |
| `.last()` | Last value in window (v3.0+) |
| `.nunique()` | Count of unique values in window (v3.0+) |
| `.pipe(func)` | Pipe to external function (v3.0+) |

### Custom Rolling Functions

```python
# Using .apply()
df["custom"] = df["value"].rolling(7).apply(
    lambda x: np.percentile(x, 90),
    raw=True                    # Pass numpy array instead of Series (faster)
)

# v3.0+: pass positional args as kwargs
df["value"].rolling(7).apply(my_func, arg1, kwarg=value)

# With Numba JIT (requires numba package)
from numba import jit

@jit(nopython=True)
def fast_quantile(values, q):
    sorted_vals = np.sort(values)
    idx = int(q * len(sorted_vals))
    return sorted_vals[idx]

df["q90"] = df["value"].rolling(7).apply(
    fast_quantile, engine="numba", args=(0.9,)
)
```

## Expanding Windows

Growing window from the first observation to the current one.

```python
# Expanding mean (cumulative average)
df["expanding_mean"] = df["value"].expanding().mean()

# Min periods
df["value"].expanding(min_periods=1).mean()

# Common methods (same as Rolling)
df["value"].expanding().sum()
df["value"].expanding().std()
df["value"].expanding().max()
df["value"].expanding().min()
df["value"].expanding().count()
df["value"].expanding().corr(other)
df["value"].expanding().cov(other)

# v3.0 additions
df["value"].expanding().first()     # First value ever seen
df["value"].expanding().last()      # Current value
df["value"].expanding().nunique()   # Running count of unique values
df["value"].expanding().pipe(func)  # Pipe to external function

# Custom functions
df["value"].expanding().apply(np.mean, raw=True)

# v3.0+: NamedAgg through **kwargs
df["value"].expanding().agg(
    avg=("value", "mean"),
    total=("value", "sum")
)
```

## Exponential Weighted Windows (EWM)

Weight recent observations more heavily.

```python
# Basic EWM
df["ewm_mean"] = df["value"].ewm(span=7).mean()

# Parameters: choose one of halflife, com, span, alpha
df["value"].ewm(halflife=7).mean()    # Half-life: 7 periods
df["value"].ewm(com=2).mean()         # Center of mass
df["value"].ewm(span=7).mean()        # Span ≈ window size
df["value"].ewm(alpha=0.5).mean()     # Smoothing factor

# Adjusted vs. biased
df["value"].ewm(span=7, adjust=True).mean()    # Default: adjusted weights
df["value"].ewm(span=7, adjust=False).mean()   # Simple exponential smoothing

# v3.0+: adjust=False now works with times parameter
df["value"].ewm(span="7D", times=df["timestamp"], adjust=False).mean()

# Min periods
df["value"].ewm(span=7, min_periods=7).mean()

# Multiple operations
result = df["value"].ewm(span=7).agg(["mean", "std", "var"])

# Time-based EWM
df["value"].ewm(span="7D").mean()     # 7-day half-life
df["value"].ewm(halflife="30min").mean()

# v3.0+: NamedAgg through **kwargs
df["value"].ewm(span=7).agg(
    avg=("value", "mean"),
    vol=("value", "std")
)
```

### EWM with Time (`times` parameter)

Weight by actual time elapsed, not row count.

```python
# Irregularly spaced timestamps
df["ewm"] = df["value"].ewm(
    span="7D",
    times=df["timestamp"],           # Actual timestamps
    halflife="7D"
)
```

## Window on Grouped Data

```python
# Rolling within groups
df.groupby("symbol")["price"].rolling(5).mean()

# Expanding within groups
df.groupby("symbol")["price"].expanding().max()

# v3.0+: positional args as kwargs
df.groupby("cat")["val"].rolling(7).apply(my_func, arg1, kwarg=value)
```

## Performance Tips

```python
# Use raw=True to pass numpy arrays (faster for simple functions)
df["value"].rolling(7).apply(np.mean, raw=True)

# Bottleneck library auto-accelerates common operations
pd.set_option("compute.use_bottleneck", True)  # Default: True

# Numba JIT for custom functions
@jit(nopython=True)
def my_func(values):
    return values.max() - values.min()

df["value"].rolling(7).apply(my_func, engine="numba")
```

## Gotchas

- **Rolling windows produce NA for first `window-1` rows** — use `min_periods=1` to start earlier.
- **Time-based rolling requires DatetimeIndex** — set index with `df.set_index("date")` first.
- **`ewm(span=7)` ≈ 7-period window** but weights decay exponentially, not uniformly like `rolling(7)`.
- **`adjust=True` (default) normalizes weights** so they sum to 1. Use `adjust=False` for simple exponential smoothing.
- **v3.0+: `ewm(times=..., adjust=False)` now works** — previously raised an error.
- **`rolling().apply()` with `raw=False` passes a Series** which is slower than `raw=True` (numpy array).
- **`corr()` and `cov()` between rolling windows** need another series as argument.
- **Grouped rolling preserves group order** but result index is MultiIndex (group key + original index).
- **`pipe()` in v3.0+** lets you chain external functions: `df.rolling(7).pipe(my_custom_window_func)`.
