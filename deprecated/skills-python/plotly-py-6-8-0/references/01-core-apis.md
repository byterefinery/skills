# Core APIs

## px vs go — when to use which

**Plotly Express (`px`)** is the fast path: pass a DataFrame and column names, get a fully styled figure. Best for exploration, dashboards, and reports where speed matters.

**Graph Objects (`go`)** is the control path: build figures trace-by-trace with full type safety. Best for production code, complex layouts, and when px doesn't support the chart type or customization needed.

They are not mutually exclusive — `px` returns `go.Figure`, so you can start with `px` and refine with `go` methods:

```python
import plotly.express as px
import plotly.graph_objects as go

fig = px.scatter(df, x="x", y="y", color="group")
fig.add_hline(y=0, line_dash="dot")          # go method on px figure
fig.update_traces(marker=dict(size=10))       # go method
```

## Figure data model

A `go.Figure` is a container with:

- **`data`** (`list[go.Trace]`) — ordered list of traces. Each trace is a typed subclass (`go.Scatter`, `go.Bar`, etc.).
- **`layout`** (`go.Layout`) — axes, title, legend, annotations, shapes, template, dimensions.
- **`frames`** (`list[go.Frame]`) — for animations. Each frame holds `data` and optional `layout` deltas.

```python
fig = go.Figure(data=[trace1, trace2], layout=go.Layout(title="Chart"))
# or incrementally:
fig = go.Figure()
fig.add_trace(trace1)
fig.add_trace(trace2)
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

Since v6.0, `px` functions accept any Narwhals-compatible DataFrame (pandas, polars, etc.) via the `narwhals` dependency. Column names are used as strings; Narwhals handles type coercion internally.

```python
import polars as pl
df = pl.DataFrame({"x": [1, 2], "y": [3, 4]})
fig = px.scatter(df, x="x", y="y")  # works
```

No special handling needed — just pass the frame.

## Figure cloning and merging

```python
# Clone a figure (deep copy)
fig2 = fig.copy()

# Merge two figures' data
fig.add_traces(other_fig.data)

# Merge layouts
fig.update_layout(other_fig.layout)
```

## Accessing figure internals

```python
# JSON-serializable dict
fig_dict = fig.to_dict()

# Access layout attributes
fig.layout.title.text
fig.layout.xaxis.title.text

# Iterate traces
for i, trace in enumerate(fig.data):
    print(trace.name, trace.x[:3])
```
