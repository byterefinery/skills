# Annotations and Shapes

## Convenience shape/annotation methods on Figure

```python
import plotly.graph_objects as go

fig = go.Figure()

# Full-height/width lines and rectangles, with optional labels
fig.add_vline(x=5, line_dash="dash", line_color="red",
              annotation_text="Threshold", annotation_position="top")
fig.add_hline(y=0.5, line_color="gray", annotation_text="mean")
fig.add_vrect(x0=1, x1=2, fillcolor="red", opacity=0.1, line_width=0)
fig.add_hrect(y0=0, y1=3, fillcolor="gray", opacity=0.2)

# For subplots: pass row=/col= to target a specific subplot
fig.add_vline(x=5, row=1, col=1)
```

`add_vline`/`add_hline`/`add_vrect`/`add_hrect` each accept `annotation_text`, `annotation_position` ("inside", "outside", "top", "bottom", "left", "right"), `annotation_font`, `line_*` styling, and `row`/`col` for subplot targeting. v7.2.0 fixed shape dropping on empty subplots when `row`/`col` select a single subplot.

## Manual annotations

```python
fig.add_annotation(
    x=1, y=5, text="Peak",
    arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="black",
    ax=30, ay=-40,            # arrow offset
    xref="x", yref="y",       # or "paper", "x domain", ...
    showarrow=False,          # plain text box
    bgcolor="rgba(255,255,255,0.8)", bordercolor="black", font=dict(size=12),
)
```

Multiple annotations: pass a list to `fig.update_layout(annotations=[...])` or use `go.layout.Annotation(...)`.

## Shapes

```python
fig.add_shape(
    type="line",               # line, rect, circle, path
    x0=0, y0=0, x1=1, y1=1,
    line=dict(color="red", width=2, dash="dot"),
    xref="x", yref="y",
    fillcolor="rgba(0,0,0,0.1)",  # for rect/circle
    opacity=0.5,
)

# path type: freehand
fig.add_shape(
    type="path", path="M 10,10 L 50,50 L 100,10",
    line=dict(width=2, color="green"),
    xref="x", yref="y",
)
```

## Rangeslider and rangeselector

```python
# Time-axis brush slider
fig.update_xaxes(rangeslider=dict(visible=True, thickness=0.15))

# Quick-range buttons
fig.update_layout(
    updatemenus=[dict(
        type="buttons",
        buttons=[
            dict(label="1mo", method="relayout",
                 xaxis_range=["2025-10-01", "2025-11-01"]),
            dict(label="6mo", method="relayout",
                 xaxis_range=["2025-05-01", "2025-11-01"]),
            dict(label="All", method="relayout", xaxis_range=None),
        ],
    )],
)
```

## Marginal and inset plots

- px: `marginal="box" | "violin" | "histogram" | "ecdf"`, `marginal_x=`, `marginal_y=` (since 7.1.0, `marginal_x`/`marginal_y="heatmap"` works on `density_heatmap`, drawing a strip colored by the same z aggregate and sharing the main color scale)
- `go` subplots: use `make_subplots` with tiny subplot domains, or overlay with `xaxis2.overlaying="x"`
