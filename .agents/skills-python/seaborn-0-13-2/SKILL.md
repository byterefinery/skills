---
name: seaborn-0-13-2
description: >
  Seaborn 0.13.2 — statistical data visualization library built on matplotlib.
  Use when the user needs attractive statistical plots in Python: relational plots
  (scatter, line), distribution plots (histogram, KDE, ECDF, rug), categorical plots
  (strip, swarm, box, violin, bar, point, count, boxen), regression plots (regplot,
  lmplot, residplot), matrix plots (heatmap, clustermap), multi-plot grids
  (FacetGrid, PairGrid, PairPlot, JointGrid, JointPlot), or the new declarative
  seaborn.objects API (so.Plot). Covers themes, palettes, color mapping, and
  the full figure-level / axes-level API. Trigger on: seaborn, sns., statistical
  plots, data visualization, heatmap, boxplot, violinplot, pairplot, jointplot,
  relplot, catplot, displot, lmplot, or any mention of seaborn.
metadata:
  tags:
    - python
    - data-visualization
    - statistics
    - plotting
---

# seaborn 0.13.2

## Overview

Seaborn is a high-level Python visualization library built on matplotlib. It provides a unified API for statistical graphics with sensible defaults, integrated color palettes, and automatic handling of categorical and continuous variables.

### Two API Styles

- **Classic API** (top-level functions) — `sns.histplot()`, `sns.scatterplot()`, `sns.boxplot()`, etc. Divided into *axes-level* (draw on a single `Axes`) and *figure-level* (create a `Figure` with multiple subplots, e.g., `relplot`, `catplot`, `displot`, `lmplot`).
- **Objects API** (`seaborn.objects` or `import seaborn.objects as so`) — Declarative, layer-based interface. `so.Plot(df, x="a", y="b").add(so.Dot())`. Inspired by ggplot2. Available since v0.12, stable in v0.13.

### Core Design

- All plotting functions accept `data` (DataFrame) and column names (`x`, `y`, `hue`, `size`, `style`) as keyword arguments — no positional args for variables.
- `hue`, `size`, and `style` map data dimensions to visual encodings (color, marker size, marker style/dashes).
- Figure-level functions return a Grid object (`FacetGrid`, `PairGrid`, `JointGrid`); axes-level functions return a matplotlib `Axes`.
- Seaborn manages matplotlib rcParams via `set_theme()` / `set_style()` / `set_context()`.

### Dependencies

- **Required**: `matplotlib>=3.3.0`, `numpy>=1.15.0`, `pandas>=0.25.0`
- **Optional**: `scipy>=1.0.0` (KDE, clustering), `statsmodels` (some regression features)
- **Python**: 3.8+

## Usage

### Quick Start

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Load a built-in dataset
df = sns.load_dataset("tips")

# Axes-level — returns matplotlib Axes
ax = sns.histplot(data=df, x="total_bill", hue="day", kde=True)

# Figure-level — creates a FacetGrid
g = sns.relplot(data=df, x="total_bill", y="tip", hue="time", col="day", kind="scatter")
g.figure.savefig("plot.png", dpi=150, bbox_inches="tight")
```

### Objects API (Declarative)

```python
import seaborn.objects as so
import pandas as pd

df = sns.load_dataset("penguins")

# Declarative layer-based plot
(so.Plot(df, x="bill_length_mm", y="bill_depth_mm", color="species")
    .add(so.Dot, so.Regress())
    .add(so.Line, so.PolyFit(degree=2), color="gray")
    .scale(color="husl")
    .on(plt.figure(figsize=(6, 4)))
    .configure(xlabel="Bill Length (mm)", ylabel="Bill Depth (mm)")
    .save("penguins.png"))
```

### Figure-Level vs Axes-Level

| Figure-Level (creates Figure) | Axes-Level (draws on Axes) |
|---|---|
| `relplot(kind="scatter"\|"line")` | `scatterplot()`, `lineplot()` |
| `displot(kind="hist"\|"kde"\|"ecdf"\|"rug")` | `histplot()`, `kdeplot()`, `ecdfplot()`, `rugplot()` |
| `catplot(kind="strip"\|"swarm"\|"box"\|"violin"\|"bar"\|"point"\|"count"\|"boxen")` | `stripplot()`, `swarmplot()`, `boxplot()`, `violinplot()`, `barplot()`, `pointplot()`, `countplot()`, `boxenplot()` |
| `lmplot()` | `regplot()`, `residplot()` |
| `jointplot()` | — |
| `pairplot()` | — |

Figure-level functions accept `row` and `col` for faceting. Axes-level functions accept `ax` to draw on a specific subplot.

### Common Parameters

- **`data`** — pandas DataFrame (or dict, numpy array for some functions)
- **`x`, `y`** — column names or array-like data
- **`hue`** — column name for color grouping
- **`size`** — column name for marker/line size mapping
- **`style`** — column name for marker/dash style mapping
- **`palette`** — color palette name or list (`"deep"`, `"muted"`, `"pastel"`, `"bright"`, `"dark"`, `"colorblind"`, `"husl"`, `"hls"`, list of colors)
- **`color`** — single color override (ignores palette)
- **`ax`** — matplotlib Axes to draw on (axes-level only)
- **`legend`** — `"auto"`, `True`, `False`
- **`errorbar`** — `("ci", 95)`, `("sd",)`, `("pi", 95)`, `None`, or callable
- **`estimator`** — aggregation function (`"mean"`, `"median"`, `np.std`, or callable)
- **`ci`** — confidence interval (legacy, use `errorbar` in v0.13)

### Theming and Styling

```python
# Set global theme (recommended)
sns.set_theme(style="whitegrid", context="talk", palette="deep")

# Style only (no context change)
sns.set_style("darkgrid")  # "whitegrid", "dark", "white", "ticks"

# Context (font/line scaling)
sns.set_context("paper")  # "paper", "notebook", "talk", "poster"

# Use as context manager
with sns.axes_style("whitegrid"):
    sns.histplot(data=df, x="value")
```

### Palettes

```python
# Named palettes
sns.color_palette("deep")        # default 6-color
sns.color_palette("muted", 8)    # 8 muted colors
sns.color_palette("colorblind")  # accessible
sns.color_palette("husl", 10)    # evenly spaced hues
sns.color_palette("viridis")     # matplotlib colormap

# Sequential (one color, many shades)
sns.color_palette("Blues", 7)
sns.dark_palette("red", 5)
sns.light_palette("blue", 5)

# Diverging (two hues meeting at neutral)
sns.diverging_palette(250, 15, s=75, l=50, n=7)

# Custom
sns.color_palette(["#e69f00", "#56b4e9", "#009e73", "#f0e442"])

# Blend
sns.blend_palette(["red", "blue"], 5)

# As continuous colormap
cmap = sns.color_palette("mako", as_cmap=True)
```

### Working with Grids (Figure-Level Return Values)

```python
g = sns.relplot(data=df, x="x", y="y", col="category")

# Access underlying matplotlib objects
g.figure.savefig("plot.png")
g.axes  # dict of (row, col) -> Axes
g.axes_flat  # flat list of Axes
g.despine()  # remove top/right spines from all subplots
g.set_titles("{col_name}")  # customize facet titles
g.set_axis_labels("X Label", "Y Label")  # set labels on all facets
g.add_legend()  # show/hide legend
g.figure.tight_layout()  # adjust layout
```

## Gotchas

- **`ci` is legacy** — use `errorbar=("ci", 95)` instead of `ci=95`. The `ci` parameter is deprecated and will be removed.
- **Figure-level functions return Grid objects, not Axes** — `sns.relplot()` returns a `FacetGrid`, not an `Axes`. To get the Axes, use `g.axes` or `g.ax` (single facet). To save, use `g.figure.savefig()`.
- **`distplot` is deprecated** — replaced by `histplot()`, `kdeplot()`, and `ecdfplot()`. Use `displot()` for figure-level.
- **`data` parameter is keyword-only** — all variable arguments (`x`, `y`, `hue`, etc.) are keyword-only. Positional args are not supported.
- **`palette` vs `color`** — `color` overrides `palette`. If both are set, `color` wins and palette is ignored.
- **`hue` order matters** — use `hue_order` to control the order of categories in the legend and plot. Without it, seaborn uses the order of appearance in the data.
- **`errorbar` defaults** — the default is `("ci", 95)` which computes 95% confidence intervals via bootstrapping. For large datasets, this can be slow; use `errorbar="sd"` or `errorbar=None` to skip.
- **`set_theme()` vs `set_style()`** — `set_theme()` sets both style and context; `set_style()` only sets style. Prefer `set_theme()` for full control.
- **`native_scale` in categorical plots** — by default, categorical plots use a categorical (integer) scale on the axis. Set `native_scale=True` to preserve the original data type (e.g., datetime) on the categorical axis.
- **`fill=True` in box/violin/bar plots** — v0.13 defaults to `fill=True` (filled shapes). Use `fill=False` for outline-only style.
- **Objects API is separate namespace** — import as `import seaborn.objects as so`, not `from seaborn import Plot`. The `so` namespace contains `Plot`, marks (`so.Dot`, `so.Line`, `so.Bar`), stats (`so.KDE`, `so.Hist`, `so.PolyFit`), and moves (`so.Dodge`, `so.Jitter`, `so.Stack`).
- **`gap` parameter in categorical plots** — v0.13 introduced `gap` (fraction of blank space between groups, 0–1) alongside `width`. Default `gap=0` preserves backward compatibility.
- **`common_norm` in distribution plots** — when `hue` splits data, `common_norm=True` (default) normalizes across all groups; `common_norm=False` normalizes per group.

## References

- [01-relational-plots](references/01-relational-plots.md) — scatterplot, lineplot, relplot
- [02-distribution-plots](references/02-distribution-plots.md) — histplot, kdeplot, ecdfplot, rugplot, displot
- [03-categorical-plots](references/03-categorical-plots.md) — stripplot, swarmplot, boxplot, violinplot, barplot, pointplot, countplot, boxenplot, catplot
- [04-regression-plots](references/04-regression-plots.md) — regplot, lmplot, residplot
- [05-matrix-plots](references/05-matrix-plots.md) — heatmap, clustermap
- [06-multi-plot-grids](references/06-multi-plot-grids.md) — FacetGrid, PairGrid, pairplot, JointGrid, jointplot
- [07-objects-api](references/07-objects-api.md) — so.Plot, Marks, Stats, Moves, Scales
- [08-themes-and-styling](references/08-themes-and-styling.md) — set_theme, set_style, set_context, axes_style
- [09-palettes-and-colors](references/09-palettes-and-colors.md) — color_palette, named palettes, sequential, diverging, cubehelix, blend
- [10-datasets-and-utilities](references/10-datasets-and-utilities.md) — load_dataset, built-in datasets, move_legend, descriptive_stat
