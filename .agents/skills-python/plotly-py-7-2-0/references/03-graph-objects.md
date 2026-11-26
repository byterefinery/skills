# Graph Objects

## go.Figure

```python
import plotly.graph_objects as go

fig = go.Figure(
    data=[go.Scatter(x=[1, 2, 3], y=[4, 3, 2], mode="lines+markers")],
    layout=go.Layout(title="Example"),
)

# Incremental construction
fig = go.Figure()
fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4], name="A"))
fig.add_traces([go.Bar(x=[1, 2], y=[5, 6]), go.Box(y=[1, 2, 3])])  # batch
fig.update_layout(title="Example", width=800, height=500)
```

Key methods:

- `add_trace(trace, row=None, col=None)` / `add_traces(traces, row, col)` — append traces; `row`/`col` target subplots
- `update_layout(**kwargs)` — merge into layout
- `update_traces(prop, value, selector)` / `for_each_trace(func)` — bulk trace updates
- `update_xaxes(**kwargs)` / `update_yaxes(**kwargs)` / `update_scenes(**kwargs)` — bulk axis updates (`update_yaxes(overlaying="y")` targets all overlaying-y axes)
- `add_annotation(...)`, `add_hline(...)`, `add_vline(...)`, `add_hrect(...)`, `add_vrect(...)`, `add_shape(...)`
- `show(renderer=None)` — display via renderers framework
- `write_html`, `write_image`, `to_image`, `to_json`, `write_json`, `to_plotly_json`

## Trace types (selection)

Cartesian: `Scatter` (incl. `scattergl`), `Bar`, `Heatmap`, `Contour`, `Contourcarpet`, `Candlestick`, `Ohlc`, `Box`, `Violin`, `Parcoords`, `Sankey`, `Waterfall`, `Funnelarea`, `Splom`, `Quiver` (new in v7), `Carpet`, `Pipette`-related via layout.

Maps: `Scattergeo`, `Choropleth` (geo subplot); `Scattermap`, `Choroplethmap`, `Densitymap` (MapLibre tile maps). Mapbox traces (`Scattermapbox`, `Choroplethmapbox`, `Densitymapbox`) were removed in v7.

3D: `Scatter3d`, `Surface` (`Mesh3d`), `Volume`, `Cone`, `Streamtube`, `Isosurface`, `Parcoords` (3d variant), `Points`-free.

Polar/ternary: `Scatterpolar`, `Barpolar`, `Scatterternary`.

Financial: `Candlestick`, `Ohlc`, `Waterfall`.

Note: `pointcloud` and `heatmapgl` were removed in v6 (use `scattergl`, `heatmap`).

## Markers, lines, fills

```python
go.Scatter(
    x=..., y=...,
    mode="lines+markers",
    marker=dict(size=8, color="crimson", symbol="circle", line=dict(width=2)),
    line=dict(color="crimson", width=3, dash="dash"),
    fill="tozeroy",              # "tozeroy" | "tonexty" | "none"
    fillcolor="rgba(255,0,0,0.1)",
    hovertemplate="<b>%{x}</b><br>%{y}<extra></extra>",
)
```

Color values follow CSS Color 4 in v7 (see Gotchas in SKILL.md): no `hsv()`, no fractional `rgb(0.5, ...)`, hex needs `#`.

## Layout essentials

```python
fig.update_layout(
    title=dict(text="Main", subtitle="Details"),
    xaxis_title="X label", yaxis_title="Y label",
    xaxis=dict(range=[0, 10], tickformat=".1f", zeroline=True, type="log"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=40, t=60, b=40),
    hovermode="closest",          # or "x unified", "y unified"
    template="plotly_white",
)
```

## Figure serialization

- `fig.to_json()` / `fig.write_json(path)` / `pio.from_json(value)` / `pio.read_json(path)` — JSON round-trip; `orjson` is used automatically if installed.
- `fig.to_plotly_json()` — plain dict without validation overhead.
- Figures are plain Python objects; any JSON-serializable figure can be embedded in Dash `dcc.Graph` or sent over the wire.

## v7 notes

- `go.Quiver(x=..., y=..., u=..., v=...)` is the native 2D vector-field trace (supersedes `ff.create_quiver`).
- New sankey attributes: `node.sort`, `link.sort` (`"auto"` default, or `"input"`), and `direction` (`"forward"`/`"reversed"`).
- `Splom` axes are linked by default (`axis.matches=True` in v7).
- The `stream` attribute and `*src` attributes (`xsrc`, `ysrc`, ...) no longer exist in the schema.
