---
name: plotly-py-6-8-0
description: >
  Plotly.py (v6.8.0) — interactive, browser-based charting library for Python. Use this skill
  whenever the user needs interactive plots, charts, or data visualizations in Python using
  plotly, plotly.express (px), plotly.graph_objects (go), Dash charts, subplots, figure
  factories, templates, image export (Kaleido), or any Plotly Express convenience function
  (scatter, bar, line, area, box, violin, histogram, pie, sunburst, treemap, choropleth,
  density, parallel coordinates, heatmap, imshow, 3D plots, maps, Gantt, candlestick, etc.).
  Covers both the high-level px API and the low-level go API.
metadata:
  tags:
    - python
    - visualization
    - plotting
    - interactive
---

# plotly-py 6.8.0

## Overview

Plotly.py is a high-level, declarative, interactive charting library for Python built on top of [plotly.js](https://github.com/plotly/plotly.js) (v3.6.0 in this release). It provides two primary APIs:

- **`plotly.express` (`px`)** — terse, high-level functions for rapid data exploration. Accepts DataFrames (pandas, polars, or any Narwhals-compatible frame) and column names. Returns `go.Figure`.
- **`plotly.graph_objects` (`go`)** — low-level, fully typed object hierarchy for precise control over every figure element. Auto-generated from the plotly.js schema.

Figures render as interactive HTML in Jupyter notebooks, standalone `.html` files, or Dash applications. Static image export (PNG, SVG, PDF) uses the [Kaleido](https://github.com/plotly/Kaleido) package.

### Key modules

| Import | Alias | Purpose |
|--------|-------|---------|
| `import plotly.express as px` | `px` | High-level chart functions |
| `import plotly.graph_objects as go` | `go` | Low-level figure/trace objects |
| `import plotly.io as pio` | `pio` | I/O, templates, renderers, image export |
| `from plotly.subplots import make_subplots` | — | Subplot grid factory |
| `import plotly.figure_factory as ff` | `ff` | Pre-built chart factories (annotated heatmap, Gantt, dendrogram, etc.) |

### Installation

```bash
pip install plotly                     # core (no numpy needed for go.Figure)
pip install "plotly[express]"          # adds numpy for px
pip install "plotly[kaleido]"          # adds kaleido>=1.3.0 for write_image
pip install anywidget                  # for go.FigureWidget in notebooks
```

## Usage

### Quick start with Plotly Express

```python
import plotly.express as px

df = px.data.tips()

# Scatter with color/size encoding
fig = px.scatter(df, x="total_bill", y="tip", color="smoker", size="size")
fig.show()

# Bar chart
fig = px.bar(df, x="day", y="total_bill", color="smoker", barmode="group")

# Histogram
fig = px.histogram(df, x="tip", marginal="box")

# Save as HTML or image
fig.write_html("chart.html")
fig.write_image("chart.png", scale=2)  # requires kaleido
```

### Low-level with Graph Objects

```python
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 3, 2], mode="lines+markers", name="Series A"))
fig.add_trace(go.Bar(x=[1, 2, 3], y=[2, 5, 3], name="Series B"))
fig.update_layout(
    title="Interactive Chart",
    xaxis_title="X",
    yaxis_title="Y",
    legend=dict(itemsizing="constant"),
)
fig.show()
```

### Subplots

```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("Scatter", "Bar", "Line", "Pie"),
    specs=[[{"type": "xy"}, {"type": "xy"}],
           [{"type": "xy"}, {"type": "pie"}]],
)

fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]), row=1, col=1)
fig.add_trace(go.Bar(x=[1, 2], y=[3, 4]), row=1, col=2)
fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4], mode="lines"), row=2, col=1)
fig.add_trace(go.Pie(labels=["A", "B"], values=[3, 4]), row=2, col=2)

fig.update_layout(height=600, showlegend=False)
```

### Templates and styling

```python
import plotly.io as pio

# Built-in templates: plotly, plotly_white, plotly_dark, ggplot, seaborn, xgridon
pio.templates.default = "plotly_white"

# Per-figure template
fig.update_layout(template="ggplot")

# Custom template
custom = pio.templates["plotly_white"].clone()
custom.layout.font.family = "Inter"
pio.templates["custom"] = custom
```

### Figure modification helpers

```python
# Add shapes, annotations, lines
fig.add_vline(x=5, line_dash="dash", annotation_text="Threshold")
fig.add_hrect(y0=0, y1=3, fillcolor="gray", opacity=0.2)
fig.add_annotation(x=1, y=5, text="Peak", arrowhead=2, ax=30, ay=-40)

# Update traces in bulk
fig.for_each_trace(lambda t: t.update(marker=dict(size=8)))

# Update layout attributes
fig.update_xaxes(title="Time", tickformat="%Y-%m-%d")
fig.update_yaxes(title="Value", rangemode="tozero")
```

## Gotchas

- **`px` requires numpy** — `plotly.express` won't import without numpy. Install with `pip install "plotly[express]"`. The core `go.Figure` works without numpy.
- **`fig.show()` renderer is environment-dependent** — in Jupyter it renders inline; in scripts it opens a browser; in headless servers it fails. Set explicitly: `pio.renderers.default = "browser"` or `"iframe"` or `"svg"` (for terminal). Use `fig.write_html()` or `fig.write_image()` for deterministic output.
- **`write_image()` requires Kaleido** — `pip install "plotly[kaleido]"` (v1.3.0+). The legacy `orca` CLI is deprecated. Kaleido v1 uses a bundled Chromium; if tiles are blocked, default headers are set automatically.
- **`go.FigureWidget` needs `anywidget`** — install separately. It replaces the old ipywidgets-based widget and works in JupyterLab 4+ and Jupyter Notebook 7+.
- **`make_subplots` secondary axes** — use `secondary_y=True` for twin-y axes. Use `rows`/`cols` in `add_trace` to target the correct subplot; omitting them defaults to `row=1, col=1`.
- **Datetime axes on subplots** — `add_vline`/`add_hline`/`add_vrect`/`add_hrect` annotations on datetime axes had placement bugs in earlier v6 releases; v6.8.0 fixes these. Pass datetime values directly (no string formatting needed).
- **`color_continuous_scale` ignored with `autocolorscale=True`** — if a template sets `autocolorscale=True`, user-specified continuous color scales were silently ignored. v6.8.0 fixes this, but be aware when debugging color issues with templates.
- **Mapbox traces are deprecated** — `scatter_mapbox`, `choropleth_mapbox`, `density_mapbox`, and `create_hexbin_mapbox` are deprecated. Use `scatter_map`, `choropleth_map`, `density_map` (MapLibre-based) instead. Mapbox still works but will be removed.
- **`pointcloud` and `heatmapgl` removed in v6** — these trace types were dropped. Use `scattergl` and `heatmap` instead.
- **`add_trace` vs `append_trace`** — `append_trace` is legacy. Use `add_trace` (single) or `add_traces` (batch) with `row`/`col` for subplots.
- **`px` is DataFrame-agnostic via Narwhals** — works with pandas, polars, and other Narwhals-compatible frames. Column name quoting and type coercion follow Narwhals rules.
- **`fig.update_layout()` merges, doesn't replace** — each call merges into the existing layout. To fully reset, create a new figure or use `fig.layout = go.Layout(...)`.
- **Hover templates** — use `{variable}` syntax in `hovertemplate`. For custom formats: `hovertemplate="%{x:.2f}<br>%{y:,.0f}"`. Use `hovertemplatefallback=True` (default) to append non-templated data.
- **`to_html` responsive sizing** — `default_height`/`default_width` on `pio.defaults` now propagate to the wrapper div so percentage-based dimensions work correctly.
- **`subtitle` on layout title** — use `fig.update_layout(title=dict(text="Main", subtitle="Details"))` for titles with subtitles (available in all px traces since v6.0).
- **`category_orders` on `px.pie`** — earlier v6 had a `ColumnNotFoundError` bug; fixed in v6.0.1.
- **`orjson` serialization** — if `orjson` is installed, plotly uses it for JSON serialization. It handles `pandas.NA` correctly in v6.0.1+.

## References

Detailed topic guides loaded on demand:

- [01-core-apis](references/01-core-apis.md) — px vs go, Figure hierarchy, data model, Narwhals DataFrame support
- [02-plotly-express](references/02-plotly-express.md) — All px functions, common parameters, trendline, facet, animation
- [03-graph-objects](references/03-graph-objects.md) — go.Figure, go.Layout, trace types, markers, lines, fills
- [04-subplots](references/04-subplots.md) — make_subplots, specs, secondary axes, shared axes, mixed subplot types
- [05-templates-and-styling](references/05-templates-and-styling.md) — pio.templates, built-in themes, custom templates, color sequences
- [06-io-and-export](references/06-io-and-export.md) — write_html, write_image (Kaleido), to_json, renderers, defaults
- [07-annotations-and-shapes](references/07-annotations-and-shapes.md) — add_vline/hline/vrect/hrect, annotations, shapes, rangeslider
- [08-figures-factories](references/08-figure-factories.md) — ff.create_annotated_heatmap, create_gantt, create_dendrogram, create_quiver
- [09-interactive-features](references/09-interactive-features.md) — hover, click, relayout events, FigureWidget, callbacks, config
- [10-maps](references/10-maps.md) — scatter_map/choropleth_map (MapLibre), scatter_geo, deprecation of Mapbox traces
- [11-3d-and-specialized](references/11-3d-and-specialized.md) — 3D scatter/surface/mesh, cone/streamtube, isosurface, volume
- [12-v6-migration](references/12-v6-migration.md) — Breaking changes from v5 to v6, removed features, new defaults
