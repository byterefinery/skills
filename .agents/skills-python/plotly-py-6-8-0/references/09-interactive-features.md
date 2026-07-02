# Interactive Features

## Hover modes

```python
fig.update_layout(
    hovermode="x unified",    # single hover label, sorted by y
    # "x"        — hover on shared x
    # "y"        — hover on shared y
    # "closest"  — hover on nearest point
    # "x unified" — single label for all traces at x
    # "y unified" — single label for all traces at y
    # "false"    — no hover
)

# Sort hover items
fig.update_layout(hoversort="ascending")  # "ascending", "descending" (v6.8+)
```

## Hover templates

```python
# Per-trace
fig.update_traces(
    hovertemplate="%{x}<br>x: %{x:.2f}<br>y: %{y:,.0f}<extra></extra>",
)

# Use custom variables
fig.update_traces(
    hovertemplate="Point: %{customdata[0]}<br>Value: %{y}",
)

# Disable fallback (don't show non-templated data)
fig.update_traces(hovertemplatefallback=False)
```

## Click and hover events (Jupyter)

```python
import plotly.graph_objects as go

fig = go.FigureWidget()
fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 3, 2], mode="markers"))

# Hover callback
def on_hover(trace, points, state):
    print(f"Hovered: {points.point_number}")

fig.on_hover(on_hover)

# Click callback
def on_click(trace, points, state):
    print(f"Clicked: {points.point_number}")

fig.on_click(on_click)

# Relayout callback
def on_relayout(layout, source, state):
    print(f"X range: {layout['xaxis']['range']}")

fig.on_relayout(on_relayout)
```

## Config options

```python
fig.update_layout(
    showlegend=True,
    dragmode="zoom",           # zoom, pan, select, lasso, orbit (3D)
)

# In show() or write_html()
fig.show(config={
    "displayModeBar": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "displaylogo": False,
    "scrollZoom": True,
    "responsive": True,
    "toImageButtonOptions": dict(format="png", width=800, height=600, scale=2),
})
```

## FigureWidget

```python
import plotly.graph_objects as go

# Requires anywidget
fig = go.FigureWidget()
fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 3, 2], mode="lines+markers"))

# Interactive modification
fig.layout.title.text = "Dynamic Title"
fig.data[0].marker.size = 15

# Display in notebook (auto-renders)
fig
```

FigureWidget uses `anywidget` (not ipywidgets). Works in JupyterLab 4+ and Notebook 7+.

## Events anywhere

v6.8.0 (plotly.js 3.6) adds `hoveranywhere` and `clickanywhere` layout attributes to emit events anywhere in the plot area, not just over traces:

```python
fig.update_layout(hoveranywhere=True, clickanywhere=True)
```

## Notifier display

```python
fig.show(config={
    "displayNotifier": "always",  # "always", "never", "auto" (v6.7+)
})
```

## Animation frames

```python
import plotly.graph_objects as go

frames = [
    go.Frame(data=[go.Scatter(x=[1, 2], y=[i, i+1])], name=str(i))
    for i in range(10)
]

fig = go.Figure(
    data=go.Scatter(x=[1, 2], y=[0, 1]),
    frames=frames,
    layout=go.Layout(
        updatemenus=[dict(
            type="buttons",
            buttons=[dict(label="Play", method="animate", args=[None])]
        )],
        sliders=[dict(
            active=0,
            currentvalue=dict(prefix="Frame: "),
            pad=t=dict(l=60),
            steps=[dict(method="animate", args=[[str(i)], dict(mode="immediate", frame=dict(duration=300)]), label=str(i)]
                   for i in range(10)]
        )]
    )
)
```
