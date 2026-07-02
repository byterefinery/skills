# Categorical Plots

Plots where one variable is categorical.

## stripplot

Scatter plot with categorical axis, optional jitter.

```python
sns.stripplot(data=df, x="day", y="total_bill", hue="time", jitter=True)
```

**Parameters:**
- `x`, `y` — one categorical, one numeric
- `hue` — semantic grouping
- `order` — list of category names to control order
- `jitter` — `True` (default), `False`, or float for jitter magnitude
- `dodge` — `True` to separate hue groups within categories, `False` (default)
- `orient` — `"v"`, `"h"`, or `None` (auto-detect)
- `size` — marker size (default 5)
- `edgecolor`, `linewidth` — marker edge styling
- `native_scale` — `True` to preserve original data type on categorical axis
- `formatter` — callable for formatting tick labels
- `ax` — target Axes

## swarmplot

Categorical scatter with non-overlapping points (beeswarm algorithm).

```python
sns.swarmplot(data=df, x="day", y="total_bill", hue="time", dodge=True)
```

**Parameters:**
- Same as `stripplot` but `jitter` is not applicable (points are positioned algorithmically)
- `dodge` — `True` to separate hue groups
- `warn_thresh` — time threshold before warning about large datasets (default 0.05s)

**Note:** Computationally expensive for large datasets (>1000 points). Use `stripplot` with `jitter=True` for large data.

## boxplot

Box and whisker plot showing median, quartiles, and outliers.

```python
sns.boxplot(data=df, x="day", y="total_bill", hue="time", fill=True, gap=0.05)
```

**Parameters:**
- `x`, `y` — one categorical, one numeric
- `hue` — semantic grouping
- `order`, `hue_order` — control category ordering
- `orient` — `"v"`, `"h"`, or `None` (auto-detect)
- `color` — single color override
- `palette` — color palette for hue groups
- `saturation` — color saturation (0–1, default 0.75)
- `fill` — `True` (default, filled boxes), `False` (outline only)
- `dodge` — `"auto"` (default, dodge when hue is used), `True`, `False`
- `width` — width of boxes (0–1, default 0.8)
- `gap` — fraction of blank space between groups (0–1, default 0)
- `whis` — whisker extent (default 1.5, IQR multiplier)
- `linecolor`, `linewidth` — line styling
- `fliersize` — outlier marker size
- `native_scale` — `True` to preserve original data type
- `log_scale` — `True` or column names
- `formatter` — callable for tick label formatting
- `legend` — `"auto"`, `True`, `False`
- `ax` — target Axes

## violinplot

Violin plot showing kernel density estimate mirrored.

```python
sns.violinplot(data=df, x="day", y="total_bill", hue="time", inner="box", split=True)
```

**Parameters:**
- Same as `boxplot` for positioning parameters
- `inner` — `"box"` (default, mini box plot), `"quartile"`, `"point"`, `"stick"`, `None`
- `split` — `True` to show hue groups as split halves (for 2-level hue)
- `bw_method`, `bw_adjust` — KDE bandwidth control
- `cut` — how far to extend beyond data (default 2, in bandwidth units)
- `gridsize` — evaluation grid points (default 100)
- `linewidth` — outline width

## boxenplot

Letter-value plot (boxen plot) for heavy-tailed distributions.

```python
sns.boxenplot(data=df, x="day", y="total_bill", k_depth="tukey", outlier_prop=0.007)
```

**Parameters:**
- Same positioning parameters as `boxplot`
- `width_method` — `"exponential"` (default) or `"linear"` for box width scaling
- `k_depth` — `"tukey"` (default), `"proportion"`, `"truncate"`
- `outlier_prop` — fraction considered outlier (default 0.007)
- `trust_arbitrary` — `True` to trust non-integer depth values

**Note:** Shows more detail in the tails than a box plot. Useful for heavy-tailed or skewed distributions.

## barplot

Bar plot with error bars showing estimated central tendency.

```python
sns.barplot(data=df, x="day", y="total_bill", hue="time", errorbar=("ci", 95), fill=True)
```

**Parameters:**
- `x`, `y` — one categorical, one numeric
- `hue` — semantic grouping
- `estimator` — aggregation function (default `"mean"`)
- `errorbar` — `("ci", 95)` (default), `("sd",)`, `("pi", 95)`, `None`, or `(func, n)`
- `n_boot` — number of bootstrap iterations (default 1000)
- `seed` — random seed for reproducibility
- `units` — column name for repeated measures
- `weights` — column name for weighting
- `width` — bar width (0–1, default 0.8)
- `gap` — fraction of blank space between groups (0–1, default 0)
- `dodge` — `"auto"`, `True`, `False`
- `fill` — `True` (default), `False`
- `orient`, `order`, `hue_order`, `palette`, `color`, `saturation` — same as other categorical plots
- `log_scale`, `native_scale`, `formatter`, `legend` — same as other categorical plots
- `ax` — target Axes

## pointplot

Point estimate with error bars connected by lines.

```python
sns.pointplot(data=df, x="day", y="total_bill", hue="time", dodge=True)
```

**Parameters:**
- Same as `barplot` for statistical parameters
- `markers` — marker style (default `"o"`, or dict per style level)
- `linestyles` — line style (default `"-"`, or list per style level)
- `dodge` — `True` to separate hue groups, `False` (default)
- No `width`, `gap`, `fill` parameters (points and lines, not bars)

## countplot

Count of observations in each category.

```python
sns.countplot(data=df, x="day", hue="time", stat="count", fill=True)
```

**Parameters:**
- `x` or `y` — categorical column (only one needed)
- `hue` — semantic grouping
- `stat` — `"count"` (default), `"frequency"`, `"density"`, `"probability"`, `"proportion"`, `"percent"`
- `width`, `gap`, `dodge`, `fill` — same as `barplot`
- All other positioning/styling parameters same as other categorical plots

## catplot

Figure-level categorical plot with faceting.

```python
g = sns.catplot(
    data=df,
    x="day", y="total_bill", hue="time",
    kind="box",  # "strip", "swarm", "box", "violin", "bar", "point", "count", "boxen"
    col="smoker", row="sex",
    height=4, aspect=1.2,
    native_scale=True
)
```

**Parameters:**
- `kind` — determines underlying plot type
- `row`, `col` — faceting columns
- `col_wrap`, `height`, `aspect` — facet layout
- `sharex`, `sharey` — axis sharing
- All other parameters passed through to the underlying axes-level function

**Return value:** `FacetGrid` object.

## Objects API: Categorical

```python
import seaborn.objects as so

# Box plot
(so.Plot(df, x="day", y="total_bill", color="time")
    .add(so.Bars, so.Aggregate(func="median", width=0.5))
    .add(so.Dot, so.Aggregate(func="median"), so.Dodge())
    .configure(xlabel="Day", ylabel="Total Bill"))

# Bar chart with error bars
(so.Plot(df, x="day", y="total_bill", color="time")
    .add(so.Bar, so.Aggregate(errorbar=("ci", 95)), so.Dodge())
    .configure(xlabel="Day", ylabel="Total Bill"))
```
