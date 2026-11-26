---
name: plotly-py-7-2-0
description: >
  Plotly.py (v7.2.0) — interactive, browser-based charting library for Python. Use this skill
  whenever the user needs interactive plots, charts, or data visualizations in Python using
  plotly, plotly.express (px), plotly.graph_objects (go), Dash charts, subplots, figure
  factories, templates, image export (Kaleido), or any Plotly Express convenience function
  (scatter, bar, line, area, box, violin, histogram, pie, sunburst, treemap, choropleth_map,
  density_map, 3D plots, maps, quiver, etc.). Requires Python 3.10+, bundles plotly.js 4.1.1.
  Covers both the high-level px API and the low-level go API.
metadata:
  tags:
    - python
    - visualization
    - plotting
    - interactive
---

# plotly-py 7.2.0

## Overview

Plotly.py is a high-level, declarative, interactive charting library for Python built on top of [plotly.js](https://github.com/plotly/plotly.js) (v4.1.1 in this release; v7 upgrades the bundled plotly.js from v3 to v4). It provides two primary APIs:

- **`plotly.express` (`px`)** — terse, high-level functions for rapid data exploration. Accepts DataFrames (pandas, polars, or any Narwhals-compatible frame) and column names. Returns `go.Figure`.
- **`plotly.graph_objects` (`go`)** — low-level, fully typed object hierarchy for precise control over every figure element. Auto-generated from the plotly.js schema.

Figures render as interactive HTML in Jupyter notebooks, standalone `.html` files, or Dash applications. Static image export (PNG, SVG, PDF) uses the [Kaleido](https://github.com/plotly/Kaleido) package (v1.0+ only in v7; Orca is gone).

### Key modules

| Import | Alias | Purpose |
|--------|-------|---------|
| `import plotly.express as px` | `px` | High-level chart functions |
| `import plotly.graph_objects as go` | `go` | Low-level figure/trace objects |
| `import plotly.io as pio` | `pio` | I/O, templates, renderers, image export |
| `from plotly.subplots import make_subplots` | — | Subplot grid factory |
| `import plotly.figure_factory as ff` | `ff` | Pre-built chart factories (dendrogram, table, streamline, quiver, trisurf, hexbin map, ternary contour) |
| `import plotly.tools` | — | `mpl_to_plotly` (matplotlib → Plotly converter), `get_subplots` |

### Installation

```bash
pip install plotly                     # core (no numpy needed for go.Figure)
pip install "plotly[express]"          # adds numpy>=1.22 for px
pip install "plotly[kaleido]"          # adds kaleido>=1.3.0 for write_image
pip install jupyterlab anywidget       # for go.FigureWidget in notebooks
```

Requires Python 3.10+ (3.8/3.9 support removed in v7.2.0). Core dependencies are `narwhals>=1.15.1` and `packaging`.

## Usage

### Quick start with Plotly Express

```python
import plotly.express as px

df = px.data.tips()

# Scatter with color/size encoding
fig = px.scatter(df, x="total_bill", y="tip", color="smoker", size="size")
fig.show()

# Bar chart
fig = px.bar(df, x="day", y="total_bill", color="smoker")

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

# Built-in templates include plotly, plotly_white, plotly_dark, ggplot2,
# seaborn, simple_white, presentation, gridon, xgridoff, ygridoff, none
pio.templates.default = "plotly_white"

# Per-figure template
fig.update_layout(template="ggplot2")

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

- **v7 removed the Mapbox traces** — `go.Scattermapbox`, `go.Choroplethmapbox`, `go.Densitymapbox`, `px.scatter_mapbox`, `px.line_mapbox`, `px.choropleth_mapbox`, `px.density_mapbox` are gone (deprecated in v6). Use the MapLibre-based `*map` equivalents with identical attributes. `layout.mapbox` is gone too — use `layout.map`, and `mapbox_style` becomes `map_style` in Express.
- **v7 removed deprecated figure factories** — `create_2d_density`, `create_annotated_heatmap`, `create_bullet`, `create_candlestick`, `create_choropleth`, `create_distplot`, `create_facet_grid`, `create_gantt`, `create_hexbin_mapbox`, `create_ohlc`, `create_scatterplotmatrix`, `create_violin` are gone. Use the px equivalents where they exist (`px.timeline` for Gantt, `px.histogram`, `px.density_heatmap` for annotated heatmaps) or plain `go` traces (`go.Candlestick`, `go.Ohlc`) otherwise. `plotly.tools.FigureFactory` is deprecated; import from `plotly.figure_factory`.
- **Image export is Kaleido-only in v7** — `pip install "plotly[kaleido]"` (requires kaleido>=1.0, use >=1.3). The `engine` argument was removed from `write_image`/`to_image`/`write_images`/`full_figure_for_development` and renderer constructors; Orca support is gone. If Chrome/Chromium is not found, run `plotly_get_chrome`.
- **Color strings now follow CSS Color 4** — `hsv()` strings no longer work (use `hsl()`, `hwb()`, `rgb()`, hex); `rgb(0.5, 0.5, 0.5)` (fractional 0–1 channels) no longer works (now renders near black); hex without leading `#` ("fff") fails; comma-separated hsl without percent units fails. New formats work, e.g. `rgb(255 0 0)`, `rgba(255 0 0 / 0.5)`, `#f00a`, `oklch()`. Unparseable colors silently fall back to the attribute default — check colors when debugging.
- **Maps auto-fit to their data by default** — `layout.geo.fitbounds` defaults to `"locations"` (was `False`) and tile-map subplots get the same via new `layout.map.fitbounds` (default `"locations"`). To get the previous fixed world view, set `fitbounds=False`. Setting `center`/`zoom`/`projection.scale` also disables auto-fitting.
- **`px` requires numpy** — `plotly.express` won't import without numpy. Install with `pip install "plotly[express]"`. The core `go.Figure` works without numpy.
- **`fig.show()` renderer is environment-dependent** — in Jupyter it renders inline; in scripts it opens a browser; in headless servers it may fail. Set explicitly: `pio.renderers.default = "browser"` or `"iframe"`. Use `fig.write_html()` or `fig.write_image()` for deterministic output.
- **`go.FigureWidget` needs `anywidget`** — install separately. It is the anywidget-based widget (the old ipywidgets-based one is gone).
- **Sankey layouts shifted in v7** — the layout algorithm was updated (links cross less) and node/link ordering is auto-optimized by default. Set `node.sort="input"` and `link.sort="input"` to preserve input order (e.g., for stable renders); new `direction` attribute ("forward"/"reversed") controls flow direction.
- **`go.Splom` axes are linked by default** — `axis.matches` defaults to `True` in v7, so row/column axes pan and zoom together. Set `matches=False` for the previous independent behavior.
- **Overlaying axes share ticks by default** — an axis with `yaxis2.overlaying="y"` now defaults `tickmode="sync"` (shared grid positions, own labels). Set `tickmode="auto"` for the previous independent grid.
- **Country name resolution changed** — `locationmode="country names"` now uses the `country-iso-search` library: accepts ISO-3166 codes, UN M49 numeric codes, flag emoji, historical/native names ("Burma", "Türkiye"), ignores case/accents/punctuation, and rejects partial phrases that previously matched by accident. Unrecognized names are logged and skipped. Use `locationmode="ISO-3"` if you need certainty.
- **MathJax v2 is gone** — LaTeX rendering supports MathJax v3 and v4 only. If your environment loads MathJax itself, make sure it is v3+.
- **New `go.Quiver` trace** — v7 adds a native `Quiver` trace type for 2D vector fields, superseding `ff.create_quiver` as the recommended approach.
- **`mpl_to_plotly` is in `plotly.tools`** — `plotly.tools.mpl_to_plotly(fig)` converts matplotlib figures; heavily improved in v7.x (twinned axes, step plots, stairs, path collections, date axes, reference lines). `convert_dash` converts Dash figures too.
- **`append_trace` is legacy** — use `add_trace` (single) or `add_traces` (batch), with `row`/`col` for subplots.
- **`px` is DataFrame-agnostic via Narwhals** — works with pandas, polars, and other Narwhals-compatible frames.
- **`fig.update_layout()` merges, doesn't replace** — each call merges into the existing layout. To fully reset, create a new figure or replace `fig.layout`.
- **`to_html()` output includes `<!doctype html>`** since v7.0.0 — relevant if you embed the returned string into an existing HTML document.
- **Chart Studio config options removed** — `showLink`, `link_text`, `sendData`, `showSources`, `showEditInChartStudio` config options are gone; `showSendToCloud` is enabled by default and adds a "Share chart…" modebar button. The `stream` attribute and all `*src` data-source attributes were also removed.
- **`plotly_get_chrome`** is the console entry point (from `plotly.io._kaleido`) to install Chrome/Chromium when Kaleido can't find one.

## References

Detailed topic guides loaded on demand:

- [01-core-apis](references/01-core-apis.md) — px vs go, Figure hierarchy, data model, Narwhals DataFrame support
- [02-plotly-express](references/02-plotly-express.md) — All px functions, common parameters, trendline, facet, animation, demo datasets
- [03-graph-objects](references/03-graph-objects.md) — go.Figure, go.Layout, trace types, markers, lines, fills
- [04-subplots](references/04-subplots.md) — make_subplots, specs, secondary axes, shared axes, mixed subplot types
- [05-templates-and-styling](references/05-templates-and-styling.md) — pio.templates, built-in themes, custom templates, color sequences
- [06-io-and-export](references/06-io-and-export.md) — write_html, write_image (Kaleido), to_json, renderers, defaults
- [07-annotations-and-shapes](references/07-annotations-and-shapes.md) — add_vline/hline/vrect/hrect, annotations, shapes, rangeslider
- [08-figure-factories](references/08-figure-factories.md) — remaining ff factories in v7, removed factories and replacements, mpl_to_plotly
- [09-interactive-features](references/09-interactive-features.md) — hover, click, relayout events, FigureWidget, callbacks, config
- [10-maps](references/10-maps.md) — MapLibre traces, Mapbox→MapLibre migration, choropleth, geo subplot
- [11-3d-and-specialized](references/11-3d-and-specialized.md) — 3D scatter/surface/mesh, quiver, streamtube, isosurface, sankey
- [12-v7-migration](references/12-v7-migration.md) — Breaking changes from v6 to v7, removed features, changed defaults
