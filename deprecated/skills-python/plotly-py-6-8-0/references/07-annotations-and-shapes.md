# Annotations and Shapes

## Quick helpers (go.Figure methods)

```python
# Vertical line
fig.add_vline(x=5, line_width=2, line_dash="dash", line_color="red",
              annotation_text="Threshold", annotation_position="top left")

# Horizontal line
fig.add_hline(y=0, line_dash="dot", annotation_text="Baseline")

# Vertical rectangle
fig.add_vrect(x0="2024-01-01", x1="2024-06-01",
              fillcolor="gray", opacity=0.2, layer="below")

# Horizontal rectangle
fig.add_hrect(y0=0, y1=50, fillcolor="yellow", opacity=0.1)
```

All helpers accept `row` and `col` for subplots.

## Annotations

```python
import plotly.graph_objects as go

fig.add_annotation(
    x=5, y=10,
    text="Peak value",
    showarrow=True,
    arrowhead=2,          # 0-7, controls arrow style
    arrowsize=1.5,
    arrowwidth=2,
    arrowcolor="red",
    ax=50, ay=-60,        # arrow offset from text
    bgcolor="white",
    bordercolor="gray",
    borderwidth=1,
    borderpad=4,
    font=dict(size=12, color="darkred"),
    opacity=0.9,
)

# Without arrow (label only)
fig.add_annotation(x=0.5, y=1, xref="paper", yref="paper",
                   text="Source: Dataset", showarrow=False,
                   font=dict(size=10, color="gray"))
```

## Shapes

```python
fig.update_layout(
    shapes=[
        # Rectangle
        dict(type="rect", x0=1, y0=0, x1=3, y1=5,
             fillcolor="rgba(255,0,0,0.1)", line_width=1),

        # Line
        dict(type="line", x0=0, y0=0, x1=10, y1=10,
             line=dict(color="red", width=2, dash="dash")),

        # Circle
        dict(type="circle", x0=2, y0=2, x1=4, y1=4,
             fillcolor="rgba(0,0,255,0.1)", line_width=1),

        # Segment (angle-based)
        dict(type="segment", x0=0, y0=0, x1=5, y1=5),
    ]
)
```

## Reference frames

```python
# Data coordinates (default)
dict(type="rect", x0=1, y0=2, x1=3, y1=4)

# Paper coordinates (0-1, relative to plot area)
dict(type="rect", x0=0, y0=0, x1=1, y1=1, xref="paper", yref="paper")

# Specific axis
dict(type="vline", x0=5, xref="x2")  # references xaxis2
```

## Rangeslider

```python
fig.update_layout(
    xaxis=dict(
        rangeslider=dict(visible=True, thickness=0.08),
        rangeselector=dict(
            buttons=[
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all", label="All"),
            ],
            x=0, y=1.1,
        ),
    )
)
```

## Shapes on datetime axes

v6.8.0 fixes annotation placement for `add_vline`, `add_hline`, `add_vrect`, `add_hrect` on datetime axes. Pass datetime values directly:

```python
from datetime import datetime
fig.add_vline(x=datetime(2024, 1, 1), annotation_text="New Year")
fig.add_vrect(x0=datetime(2024, 1, 1), x1=datetime(2024, 6, 1),
              fillcolor="gray", opacity=0.2)
```
