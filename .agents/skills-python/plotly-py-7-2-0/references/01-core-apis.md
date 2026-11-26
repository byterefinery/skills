# Core APIs

## px vs go — when to use which

**Plotly Express (`px`)** is the fast path: pass a DataFrame and column names, get a fully styled figure. Best for exploration, dashboards, and reports where speed matters.

**Graph Objects (`go`)** is the control path: build figures trace-by-trace with full type safety. Best for production code, complex layouts, and when px doesn't support the chart type or customization needed.

They are not mutually exclusive — `px` returns `go.Figure`, so you can start with `px` and refine with `go` methods:

```python
import plotly.express as px

fig = px.scatter(df, x="x", y="y", color="group")
fig.add_hline(y=0, line_dash="dot")    # go method on px figure
fig.update_traces(marker=dict(size=10))
```

## Figure data model

A `go.Figure` is a container with:

- **`data`** (`list[go.Trace]`) — ordered list of traces. Each trace is a typed subclass (`go.Scatter`, `go.Bar`, `go.Quiver`, ...).
- **`layout`** (`go.Layout`) — axes, title, legend, annotations, shapes, template, dimensions, subplots (`geo`, `map`, `polar`, `ternary`, scenes).
- **`frames`** (`list[go.Frame]`) — for animations. Each frame holds `data` and optional `layout` deltas.

```python
fig = go.Figure(data=[trace1, trace2], layout=go.Layout(title="Chart"))
# or incrementally:
fig = go.Figure()
fig.add_trace(trace1)
fig.update_layout(title="Chart")
```

## Trace type resolution

When creating traces via `go.Scatter(x=..., y=...)`, the trace type is inferred from the class name. When using dicts, set `"type"` explicitly:

```python
# Object API (preferred)
go.Scatter(x=[1, 2], y=[3, 4], mode="lines")

# Dict API (valid, less type-safe)
dict(type="scatter", x=[1, 2], y=[3, 4], mode="lines")
```

## Narwhals DataFrame support

Plotly Express (and `px.imshow` for array inputs) uses Narwhals internally, so it accepts pandas, polars, and other Narwhals-compatible DataFrames without code changes. Column name quoting and type coercion follow Narwhals rules. `go` itself does not depend on any DataFrame library.

## Rendering targets

- Jupyter Notebook / JupyterLab / VS Code notebooks / Colab / Kaggle — inline interactive rendering (JupyterLab needs the `anywidget` package)
- Plain Python script — opens a browser tab (default renderer)
- `.html` files via `fig.write_html()` / `fig.to_html()`
- Dash applications — figures are plain JSON-serializable objects
- Static images via Kaleido (`write_image`, `to_image`)

## Version pinning

This skill documents plotly.py 7.2.0 (2026-11-24), which bundles plotly.js 4.1.1. Requires Python 3.10+. If you are on plotly 6.x, see [12-v7-migration](12-v7-migration.md) for the breaking changes (Mapbox traces removed, factories removed, CSS Color 4 color parsing, changed map/sankey/splom defaults).
