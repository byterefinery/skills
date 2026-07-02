# Relational Plots

Plots showing relationships between continuous variables.

## scatterplot

Draw a scatter plot with optional semantic groupings.

```python
sns.scatterplot(data=df, x="total_bill", y="tip", hue="day", size="size", style="time")
```

**Parameters:**
- `x`, `y` — column names or array-like
- `hue` — semantic grouping for color
- `size` — semantic grouping for marker size
- `style` — semantic grouping for marker/dash style
- `palette` — color palette
- `sizes` — `(min, max)` tuple for size range, e.g., `(20, 200)`
- `markers` — `True` (default, different markers per style level), `False`, or dict mapping style levels to marker chars
- `legend` — `"auto"`, `True`, `False`
- `ax` — target Axes

## lineplot

Draw a line plot with optional error bands.

```python
sns.lineplot(data=df, x="day", y="total_bill", hue="time", style="smoker", errorbar=("ci", 95))
```

**Parameters:**
- `x`, `y` — column names or array-like
- `hue`, `style` — semantic groupings
- `units` — column name for repeated measures (draws separate lines per unit, no error bars)
- `errorbar` — `("ci", 95)`, `("sd",)`, `("pi", 95)`, `None`, or `(func, n)` tuple
- `estimator` — aggregation function (`"mean"`, `"median"`, `np.std`, callable, or `None`)
- `dashes` — `True` (default, different dash patterns per style level), `False`, or list of dash tuples
- `markers` — `True`, `False`, or dict mapping style levels to marker chars
- `sort` — `True` (default, sort by x), `False` (use data order)
- `err_kws` — dict passed to error band drawing (e.g., `{"alpha": 0.2}`)
- `ax` — target Axes

**Key behaviors:**
- When `estimator` is set (default `"mean"`), values at each x are aggregated. Multiple y values at the same x produce a single point with error bars.
- Set `estimator=None` to draw every data point (useful for time series with unique x values).
- `units` draws a separate line for each unit and disables error bars.

## relplot

Figure-level interface for relational plots with faceting.

```python
g = sns.relplot(
    data=df,
    x="total_bill", y="tip",
    hue="time", col="day", row="smoker",
    kind="scatter",  # or "line"
    height=4, aspect=1.2,
    facet_kws={"sharex": False}
)
```

**Parameters:**
- `kind` — `"scatter"` (default) or `"line"`
- `row`, `col` — column names for faceting
- `col_wrap` — max columns before wrapping
- `height`, `aspect` — subplot dimensions (height in inches, aspect ratio)
- `sharex`, `sharey` — share axes across facets (`True`, `False`, `"all"`)
- `facet_kws` — dict passed to FacetGrid constructor
- All other parameters passed through to `scatterplot` or `lineplot`

**Return value:** `FacetGrid` object. Use `g.figure.savefig()` to save.

## Objects API: Relational

```python
import seaborn.objects as so

# Scatter with regression line
(so.Plot(df, x="total_bill", y="tip", color="day")
    .add(so.Dot)
    .add(so.Line, so.Regress())
    .configure(xlabel="Total Bill", ylabel="Tip"))

# Line plot with error bands
(so.Plot(df, x="date", y="value", color="group")
    .add(so.Line, so.Est(errorbar=("ci", 95)))
    .scale(x="temporal")
    .configure(xlabel="Date", ylabel="Value"))
```
