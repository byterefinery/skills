# Graph Objects

## Figure construction

```python
import plotly.graph_objects as go

# Empty figure
fig = go.Figure()

# With data and layout
fig = go.Figure(data=[trace1, trace2], layout=go.Layout(title="Chart"))

# From dict
fig = go.Figure({
    "data": [{"type": "scatter", "x": [1, 2], "y": [3, 4]}],
    "layout": {"title": {"text": "Chart"}}
})
```

## Trace types

### Cartesian traces
`go.Scatter`, `go.Bar`, `go.Histogram`, `go.Box`, `go.Violin`, `go.Area`, `go.Heatmap`, `go.Contour`, `go.Image`, `go.Table`, `go.Waterfall`, `go.Ohlc`, `go.Candlestick`

### Polar traces
`go.Scatterpolar`, `go.Barpolar`

### 3D traces
`go.Scatter3d`, `go.Mesh3d`, `go.Surface`, `go.Cone`, `go.Streamtube`, `go.Isosurface`, `go.Volume`

### Map traces
`go.Scattermap`, `go.Choroplethmap`, `go.Densitymap`, `go.Scattergeo`, `go.Choropleth`

### Hierarchical traces
`go.Pie`, `go.Sunburst`, `go.Treemap`, `go.Icicle`, `go.Funnel`, `go.Funnelarea`

### Special traces
`go.Sankey`, `go.Parcoords`, `go.Parcats`, `go.Splom`, `go.Indicator`, `go.Scatterternary`, `go.Scattercarpet`, `go.Contourcarpet`

## Scatter modes

```python
go.Scatter(x=[1, 2], y=[3, 4], mode="markers")       # points only
go.Scatter(x=[1, 2], y=[3, 4], mode="lines")          # line only
go.Scatter(x=[1, 2], y=[3, 4], mode="lines+markers")  # both
go.Scatter(x=[1, 2], y=[3, 4], mode="text")           # text labels
go.Scatter(x=[1, 2], y=[3, 4], mode="lines+text")     # line with labels
```

## Markers

```python
go.Scatter(
    x=[1, 2, 3], y=[4, 5, 6],
    marker=dict(
        size=[10, 15, 20],
        color=[1, 2, 3],
        colorscale="Viridis",
        showscale=True,
        symbol="circle",           # circle, square, diamond, star, x, +
        line=dict(width=2, color="black"),
        opacity=0.8,
        cornerradius=0.3,          # rounded corners (v6.2+)
    )
)
```

## Lines

```python
go.Scatter(
    x=[1, 2, 3], y=[4, 5, 6],
    line=dict(
        color="rgb(100, 150, 200)",
        width=3,
        dash="dash",   # solid, dash, dot, dashdot, dotted
    )
)
```

## Fills

```python
# Fill to zero
go.Scatter(x=[1, 2], y=[3, 4], fill="tozeroy")

# Fill between two traces
fig = go.Figure()
fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4], fill=None, name="Upper"))
fig.add_trace(go.Scatter(x=[1, 2], y=[1, 2], fill="tonexty", name="Lower"))
```

## Adding traces

```python
# Single trace
fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]))

# Convenience methods (auto-create trace type)
fig.add_scatter(x=[1, 2], y=[3, 4], mode="lines")
fig.add_bar(x=["A", "B"], y=[1, 2])
fig.add_histogram(x=[1, 2, 3, 2, 1])

# Batch add
fig.add_traces([trace1, trace2], rows=[1, 2], cols=[1, 1])

# With subplot targeting
fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]), row=2, col=1)
```

## Layout structure

```python
go.Layout(
    title=go.layout.Title(text="Chart", x=0.5, font=dict(size=20)),
    xaxis=go.layout.XAxis(title="X", tickformat=".2f"),
    yaxis=go.layout.YAxis(title="Y", rangemode="tozero"),
    legend=go.layout.Legend(x=0, y=1, itemsizing="constant"),
    margin=go.layout.Margin(l=60, r=30, t=50, b=50),
    hovermode="x unified",      # "x", "y", "closest", "x unified"
    barmode="group",            # "group", "overlay", "stack", "relative"
    template="plotly_white",
    height=500,
    width=700,
)
```

## Updating

```python
# Update layout
fig.update_layout(title="New Title", height=600)

# Update specific axis
fig.update_xaxes(title="Time", tickformat="%Y-%m-%d")
fig.update_yaxes(title="Value", rangemode="tozero")

# Update all traces
fig.update_traces(marker=dict(size=8), opacity=0.8)

# Update specific trace(s)
fig.update_traces(selector=dict(name="Series A"), marker=dict(color="red"))

# Apply function to each trace
fig.for_each_trace(lambda t: t.update(hovertemplate="%{x}: %{y}"))
```

## Selectors

```python
# Filter traces by property
fig.update_traces(
    selector=dict(type="scatter", mode="markers"),
    marker=dict(symbol="diamond")
)
```
