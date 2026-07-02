# Multi-Plot Grids

Grid-based plotting for exploring multi-dimensional relationships.

## FacetGrid

Multi-plot grid conditioned on categorical variables.

```python
g = sns.FacetGrid(
    data=df,
    row="smoker", col="day", hue="time",
    col_wrap=3, height=3, aspect=1,
    palette="deep",
    row_order=["No", "Yes"],
    col_order=["Thur", "Fri", "Sat", "Sun"],
    sharex=True, sharey=True,
    margin_titles=True,
    dropna=True
)
g.map(sns.scatterplot, "total_bill", "tip")
g.add_legend()
```

**Parameters:**
- `data` — DataFrame (required)
- `row`, `col`, `hue` — column names for faceting
- `col_wrap` — wrap columns after this many
- `height`, `aspect` — subplot dimensions
- `palette` — color palette for hue
- `row_order`, `col_order`, `hue_order` — explicit ordering
- `hue_kws` — dict of artist kwargs to vary by hue (e.g., `{"marker": ["o", "s"]}`)
- `sharex`, `sharey` — share axes (`True`, `False`, `"all"`)
- `despine` — `True` (default, remove top/right spines)
- `margin_titles` — `True` for row margin titles
- `dropna` — `True` (default, drop rows with NaN in facet variables)

**Methods:**
- `g.map(func, *args, **kwargs)` — apply function to each facet
- `g.map_dataframe(func, *args, **kwargs)` — apply function that takes `data` keyword
- `g.map_dataframe(sns.scatterplot, x="total_bill", y="tip", hue="time")`
- `g.set(xlabel="X", ylabel="Y")` — set axis labels on all facets
- `g.set_titles("{col_name}")` — customize facet titles (use `{row_name}`, `{col_name}`)
- `g.set_axis_labels("X Label", "Y Label")` — set outer axis labels
- `g.add_legend()` — show legend
- `g.despine()` — remove spines
- `g.fig` / `g.figure` — underlying matplotlib Figure
- `g.axes` — dict of `(row, col)` → Axes
- `g.axes.flat` — flat iterator over Axes
- `g.axes_dict` — dict keyed by column category names

## PairGrid

Grid of pairwise relationships.

```python
g = sns.PairGrid(
    data=df,
    vars=["total_bill", "tip", "size"],
    x_vars=["total_bill", "tip"],
    y_vars=["total_bill", "tip"],
    hue="day",
    hue_order=["Thur", "Fri", "Sat", "Sun"],
    palette="deep",
    diag_sharey=True
)
g.map_lower(sns.scatterplot)
g.map_upper(sns.kdeplot, levels=4)
g.map_diag(sns.histplot, kde=True)
g.add_legend()
```

**Parameters:**
- `data` — DataFrame (required)
- `vars` — subset of columns to include
- `x_vars`, `y_vars` — separate lists for asymmetric grids
- `hue` — column for color grouping
- `hue_order`, `palette` — hue control
- `diag_sharey` — share y-axis on diagonal with lower triangle

**Methods:**
- `g.map(func, **kwargs)` — apply to all cells
- `g.map_lower(func, **kwargs)` — apply to lower triangle
- `g.map_upper(func, **kwargs)` — apply to upper triangle
- `g.map_diag(func, **kwargs)` — apply to diagonal
- `g.map_offdiag(func, **kwargs)` — apply to off-diagonal cells
- `g.set(xlabel="X", ylabel="Y")` — set labels
- `g.set_axis_labels("X", "Y")` — set outer labels
- `g.add_legend()` — show legend

## pairplot

Convenience function for PairGrid with common defaults.

```python
sns.pairplot(
    data=df,
    hue="species",
    vars=["bill_length_mm", "bill_depth_mm", "flipper_length_mm"],
    x_vars=None, y_vars=None,
    kind="scatter",       # "scatter", "reg", "kde", "hist"
    diag_kind="auto",     # "auto", "hist", "kde", None
    markers="o",
    height=2.5, aspect=1,
    corner=False,          # only show lower triangle
    dropna=True,
    plot_kws=None,         # kwargs for off-diagonal plots
    diag_kws=None,         # kwargs for diagonal plots
    grid_kws=None          # kwargs for PairGrid
)
```

**Return value:** `PairGrid` object.

**Off-diagonal plot types by `kind`:**
- `"scatter"` → `scatterplot`
- `"reg"` → `regplot`
- `"kde"` → `kdeplot`
- `"hist"` → `histplot` (2D)

**Diagonal plot types by `diag_kind`:**
- `"auto"` → `"hist"` if `kind="scatter"`, `"kde"` if `kind="kde"`
- `"hist"` → `histplot`
- `"kde"` → `kdeplot`
- `None` → no diagonal plots

## JointGrid

Bivariate plot with marginal univariate plots.

```python
g = sns.JointGrid(data=df, x="total_bill", y="tip", height=6, ratio=5, space=0.2)
g.plot_joint(sns.scatterplot, color="steelblue")
g.plot_marginals(sns.histplot, color="steelblue", kde=True)
```

**Parameters:**
- `data` — DataFrame
- `x`, `y` — column names
- `hue` — column for color grouping
- `height` — total figure height (default 6)
- `ratio` — ratio of joint to marginal axis size (default 5)
- `space` — space between joint and marginal (default 0.2)
- `palette`, `hue_order`, `hue_norm` — hue control

**Methods:**
- `g.plot_joint(func, **kwargs)` — plot on joint axes
- `g.plot_marginals(func, **kwargs)` — plot on both marginal axes
- `g.plot_single(func, **kwargs)` — plot on one marginal axis
- `g.set_axis_labels("X", "Y")` — set labels
- `g.annotate(stat_func, **kwargs)` — add statistical annotation (e.g., correlation)

## jointplot

Convenience function for JointGrid.

```python
g = sns.jointplot(
    data=df,
    x="total_bill", y="tip", hue="day",
    kind="scatter",   # "scatter", "reg", "resid", "kde", "hist", "hex"
    height=6, ratio=5, space=0.2,
    marginal_ticks=False,
    joint_kws=None,    # kwargs for joint plot
    marginal_kws=None  # kwargs for marginal plots
)
```

**Return value:** `JointGrid` object.

**Plot types by `kind`:**
- `"scatter"` → `scatterplot` (joint), `histplot` (marginals)
- `"reg"` → `regplot` (joint), `histplot` (marginals)
- `"resid"` → `residplot` (joint), `histplot` (marginals)
- `"kde"` → `kdeplot` (joint), `kdeplot` (marginals)
- `"hist"` → `histplot` 2D (joint), `histplot` (marginals)
- `"hex"` → `hexbin` (joint), `histplot` (marginals)
