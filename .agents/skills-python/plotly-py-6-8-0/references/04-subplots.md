# Subplots

## make_subplots

```python
from plotly.subplots import make_subplots

# Basic grid
fig = make_subplots(rows=2, cols=2)

# With titles
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("Top Left", "Top Right", "Bottom Left", "Bottom Right"),
)

# Horizontal/vertical titles
fig = make_subplots(
    rows=2, cols=3,
    horizontal_spacing=0.1,
    vertical_spacing=0.15,
    column_titles=["Col 1", "Col 2", "Col 3"],
    row_titles=["Row 1", "Row 2"],
)
```

## Specs — mixed subplot types

```python
fig = make_subplots(
    rows=2, cols=2,
    specs=[
        [{"type": "xy"},       {"type": "polar"}],
        [{"type": "domain"},   {"type": "xy"}],
    ],
)

fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]), row=1, col=1)
fig.add_trace(go.Scatterpolar(r=[1, 2], theta=[45, 90]), row=1, col=2)
fig.add_trace(go.Pie(labels=["A", "B"], values=[3, 4]), row=2, col=1)
fig.add_trace(go.Bar(x=["A", "B"], y=[1, 2]), row=2, col=2)
```

Supported `type` values: `"xy"`, `"polar"`, `"scene"` (3D), `"geo"`, `"ternary"`, `"domain"` (pie/sunburst/treemap), `"map"` (MapLibre), `"mapbox"`.

## Secondary axes

```python
fig = make_subplots(specs=[{"secondary_y": True}])

fig.add_trace(go.Scatter(y=[1, 3, 2], name="Left"), secondary_y=False)
fig.add_trace(go.Bar(y=[100, 200, 150], name="Right"), secondary_y=True)

fig.update_yaxes(title="Left Axis", secondary_y=False)
fig.update_yaxes(title="Right Axis", secondary_y=True)
```

## Shared axes

```python
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)

fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]), row=1, col=1)
fig.add_trace(go.Scatter(x=[1, 2], y=[5, 6]), row=2, col=1)
```

## Adding traces to subplots

```python
# By row/col
fig.add_trace(trace, row=1, col=1)

# Batch with rows/cols
fig.add_traces(
    [trace1, trace2, trace3],
    rows=[1, 1, 2],
    cols=[1, 2, 1],
)

# Convenience methods
fig.add_scatter(x=[1, 2], y=[3, 4], row=1, col=1)
fig.add_bar(x=["A"], y=[1], row=2, col=1)
```

## Column/row alignment

```python
fig = make_subplots(
    rows=2, cols=2,
    column_widths=[0.3, 0.7],   # relative widths
    row_heights=[0.7, 0.3],     # relative heights
)
```

## Multiple x/y axes on same subplot

```python
fig = make_subplots(specs=[{"secondary_y": True}])

fig.add_trace(go.Scatter(y=[1, 2], name="Y1"), secondary_y=False)
fig.add_trace(go.Scatter(y=[10, 20], name="Y2"), secondary_y=True)

# Third axis (x-axis)
fig.add_trace(go.Scatter(x=[5, 6], y=[1, 2], xaxis="x3", name="X3"))
fig.update_layout(xaxis3=dict(domain=[0, 0.5], anchor="y"))
```

## Shared y-axes with secondary axes

v6.8.0 supports `shared_yaxes` with secondary axes, allowing synchronized twin-y across subplots.
