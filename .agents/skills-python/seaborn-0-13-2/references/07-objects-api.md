# Objects API

The declarative, layer-based API (`seaborn.objects` or `so`). Available since v0.12, stable in v0.13.

## Core Concept

```python
import seaborn.objects as so

(so.Plot(data, x="col_x", y="col_y", color="col_hue")
    .add(so.Mark, so.Stat, so.Move)
    .scale(x="continuous", color="husl")
    .on(figsize=(8, 5))
    .configure(xlabel="X Label", ylabel="Y Label", legend={"title": "Group"})
    .save("plot.png"))
```

## Plot

The main entry point. Holds data and variable mappings.

```python
so.Plot(df, x="a", y="b", color="c", size="d", marker="e")
```

**Positional encodings:** `x`, `y` — column names or array-like.

**Non-positional encodings:** `color`, `size`, `marker`, `alpha`, `linewidth`, `varext` — column names for mapping.

**Methods:**
- `.add(mark, stat=None, move=None, **kwargs)` — add a layer
- `.scale(x=..., y=..., color=...)` — override scale mappings
- `.on(ax=None, figsize=(w, h))` — set target figure/axes
- `.configure(**kwargs)` — set plot-level configuration (labels, limits, legend, theme)
- `.show()` — display the plot
- `.save(path)` — save to file

## Marks

Visual elements drawn on the plot.

| Mark | Description |
|------|-------------|
| `so.Dot` | Scatter points |
| `so.Dots` | Multiple dots per group |
| `so.Line` | Line connecting points |
| `so.Lines` | Multiple lines per group |
| `so.Bar` | Bar chart |
| `so.Bars` | Grouped bars |
| `so.Area` | Filled area under curve |
| `so.Band` | Shaded band (e.g., confidence interval) |
| `so.Path` | Path connecting points |
| `so.Paths` | Multiple paths |
| `so.Dash` | Dashed line |
| `so.Range` | Range bar (error bar style) |
| `so.Text` | Text annotations |

**Mark kwargs:** `linewidth`, `edgewidth`, `edgecolor`, `format`, `short_ratio`, `orientation`, `interpolate`, `shift`, `threshold`, `stack`, `grouped`.

## Stats

Statistical transformations applied before plotting.

| Stat | Description |
|------|-------------|
| `so.Agg(func, errorbar)` | Aggregate with optional error bars |
| `so.Est(func, errorbar)` | Estimate (alias for Agg) |
| `so.Count()` | Count observations per bin |
| `so.Hist(bins, binwidth, stat)` | Histogram computation |
| `so.KDE(bw_adjust, bw_method, cumulative)` | Kernel density estimate |
| `so.Perc(aggregator)` | Percentile computation |
| `so.PolyFit(degree)` | Polynomial regression fit |
| `so.Regress()` | Linear regression |

**Stat kwargs:** `bins`, `binwidth`, `stat`, `orient`, `common`, `estimate`, `width`, `gap`, `method`, `adjust`, `cumulative`, `threshold`, `degree`, `robust`.

## Moves

Adjustments to reduce overplotting.

| Move | Description |
|------|-------------|
| `so.Dodge()` | Separate overlapping elements side by side |
| `so.Jitter(amount)` | Add random noise to positions |
| `so.Stack()` | Stack elements vertically/horizontally |
| `so.Shift(amount)` | Shift elements by fixed amount |
| `so.Norm()` | Normalize positions |

## Scales

Control mappings from data values to visual properties.

```python
# Override default scale behavior
(so.Plot(df, x="date", y="value", color="group")
    .add(so.Line, so.Est())
    .scale(x="temporal", color="husl", size="continuous"))
```

**Scale types:**
- `so.Continuous(palette=None, norm=None, scheme=None, limits=None, ticks=None, tick_interval=None)` — continuous scale
- `so.Nominal(colors=None, levels=None)` — categorical scale
- `so.Temporal(ticker=None, formatter=None, limits=None)` — datetime scale
- `so.Boolean()` — boolean scale

**Built-in palette names:** `"deep"`, `"muted"`, `"pastel"`, `"bright"`, `"dark"`, `"colorblind"`, `"husl"`, `"hls"`, `"viridis"`, `"mako"`, `"crest"`, `"flare"`, `"rocket"`, `"icefire"`, `"cividis"`, `"magma"`, `"plasma"`, `"inferno"`.

## Configure

Plot-level settings.

```python
.configure(
    xlabel="X Label",
    ylabel="Y Label",
    title="Plot Title",
    xlim=(0, 100),
    ylim=(0, 50),
    aspect=1.5,
    size=(800, 600),
    legend=True,  # or {"title": "Groups", "offset": (0, 0)}
    tickrotate=45,
    ticks=True,
    grid=True,    # or {"x": True, "y": False}
    facet={"wrap": 3},
    theme="darkgrid",  # or {"axes_style": "whitegrid"}
)
```

## Complete Examples

```python
# Scatter with regression
(so.Plot(df, x="total_bill", y="tip", color="day")
    .add(so.Dot)
    .add(so.Line, so.Regress())
    .configure(xlabel="Total Bill", ylabel="Tip"))

# Histogram with KDE overlay
(so.Plot(df, x="total_bill", color="day")
    .add(so.Bar, so.Hist(bins=30, stat="density"))
    .add(so.Line, so.KDE(), linewidth=2)
    .configure(xlabel="Total Bill", ylabel="Density"))

# Grouped bar chart
(so.Plot(df, x="day", y="total_bill", color="time")
    .add(so.Bar, so.Agg(func="mean", errorbar=("ci", 95)), so.Dodge())
    .configure(xlabel="Day", ylabel="Mean Total Bill"))

# Line plot with error bands
(so.Plot(df, x="date", y="value", color="group")
    .add(so.Line, so.Est(errorbar=("ci", 95)))
    .add(so.Band, so.Est(errorbar=("ci", 95)), alpha=0.2)
    .scale(x="temporal")
    .configure(xlabel="Date", ylabel="Value"))

# Faceted scatter
(so.Plot(df, x="total_bill", y="tip", color="time", facet="day")
    .add(so.Dot)
    .configure(facet={"wrap": 4}, size=(12, 4)))
```
