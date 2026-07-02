# Distribution Plots

Plots showing the distribution of one or more variables.

## histplot

Histogram with optional density estimation.

```python
sns.histplot(data=df, x="total_bill", hue="day", kde=True, binwidth=5)
```

**Parameters:**
- `x`, `y` — column names (one for 1D, both for 2D histogram)
- `hue` — semantic grouping
- `weights` — column name for weighting observations
- `stat` — aggregation: `"count"` (default), `"frequency"`, `"density"`, `"probability"`, `"proportion"`, `"percent"`
- `bins` — number of bins (int), bin edges (array), or `"auto"`, `"fd"`, `"scott"`, `"sqrt"`, `"stellas"`, `"rice"`, `"murphy"`
- `binwidth` — fixed bin width
- `binrange` — `(min, max)` tuple for bin range
- `discrete` — `True` to shift bins to center on integer values
- `kde` — `True` to overlay kernel density estimate
- `cumulative` — `True` for cumulative histogram
- `multiple` — how to handle overlapping groups: `"layer"` (default), `"dodge"`, `"fill"`, `"stack"`
- `common_bins` — `True` (default, shared bins across hue groups), `False` (per-group bins)
- `common_norm` — `True` (default, stat computed across all groups), `False` (per-group)
- `shrink` — scale factor for bar width (0–1)
- `fill` — `True` (default, filled bars), `False` (outline only)
- `linecolor`, `linewidth` — edge color and width of bars
- `ax` — target Axes

**2D histograms:** Pass both `x` and `y` for a 2D histogram (color-encoded matrix of bin counts).

## kdeplot

Kernel density estimate plot.

```python
sns.kdeplot(data=df, x="total_bill", hue="day", fill=True, common_norm=False)
```

**Parameters:**
- `x`, `y` — column names (one for 1D, both for 2D contour)
- `hue` — semantic grouping
- `weights` — column name for weighting
- `palette` — color palette
- `fill` — `True` to fill under curve, `False` for line only
- `multiple` — `"layer"` (default), `"fill"`, `"stack"`
- `common_norm` — `True` (default), `False` (per-group normalization)
- `common_grid` — `True` (default, shared evaluation grid), `False` (per-group grid)
- `bw_method` — bandwidth method: `"scott"` (default), `"silverman"`, or scalar
- `bw_adjust` — bandwidth multiplier (1 = default, >1 = smoother, <1 = more detailed)
- `cumulative` — `True` for cumulative KDE
- `thresh` — contour threshold (for 2D, fraction of max density)
- `levels` — number of contour levels (for 2D)
- `gridsize` — number of points for evaluation grid (default 200)
- `cut` — how far to extend the plot beyond data range (in bandwidth units)
- `clip` — `(min, max)` to clip the plot range
- `log_scale` — `True` or column names for log scale
- `ax` — target Axes

**2D KDE:** Pass both `x` and `y` for a contour plot. Use `fill=True` for filled contours.

## ecdfplot

Empirical cumulative distribution function.

```python
sns.ecdfplot(data=df, x="total_bill", hue="day", stat="proportion")
```

**Parameters:**
- `x`, `y` — column names
- `hue` — semantic grouping
- `weights` — column name for weighting
- `stat` — `"proportion"` (default), `"count"`, `"percentage"`
- `complementary` — `True` for survival-style curve (1 - ECDF)
- `log_scale` — `True` or column names
- `legend` — `"auto"`, `True`, `False`
- `ax` — target Axes

## rugplot

Small tick marks showing individual observations.

```python
sns.rugplot(data=df, x="total_bill", hue="day", height=0.05)
```

**Parameters:**
- `x`, `y` — column names
- `hue` — semantic grouping
- `height` — height of rug marks (fraction of axis, default 0.025)
- `expand_margins` — `True` (default, expand axis to fit rugs), `False`
- `ax` — target Axes

## displot

Figure-level distribution plot with faceting.

```python
g = sns.displot(
    data=df,
    x="total_bill", hue="day",
    kind="hist",  # "hist", "kde", "ecdf", "step"
    col="smoker", row="time",
    binwidth=5, rug=True,
    height=4, aspect=1.2
)
```

**Parameters:**
- `kind` — `"hist"` (default, uses `histplot`), `"kde"` (uses `kdeplot`), `"ecdf"` (uses `ecdfplot`), `"step"` (step histogram)
- `rug` — `True` to add rug plot
- `rug_kws` — dict passed to `rugplot`
- `row`, `col` — faceting columns
- `height`, `aspect` — subplot dimensions
- `log_scale` — `True` or `(True, False)` for (x, y) log scale
- All other parameters passed through to the underlying axes-level function

**Return value:** `FacetGrid` object.

## Objects API: Distributions

```python
import seaborn.objects as so

# Histogram
(so.Plot(df, x="total_bill", color="day")
    .add(so.Bar, so.Hist(bins=30, stat="density"))
    .add(so.Line, so.KDE(), linewidth=2)
    .configure(xlabel="Total Bill"))

# ECDF
(so.Plot(df, x="total_bill", color="day")
    .add(so.Line, so.Est(aggregator="cumcount"))
    .configure(xlabel="Total Bill", ylabel="Cumulative Count"))
```
