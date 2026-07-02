# 3D and Specialized Charts

## 3D scatter

```python
import plotly.express as px

fig = px.scatter_3d(df, x="x", y="y", z="z",
                    color="category", size="value",
                    opacity=0.8)
fig.update_layout(scene=dict(
    xaxis_title="X", yaxis_title="Y", zaxis_title="Z",
    camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
))
```

## 3D line

```python
fig = px.line_3d(df, x="x", y="y", z="z", color="series")
```

## Surface

```python
import plotly.graph_objects as go
import numpy as np

z = np.outer(np.linspace(-3, 3, 50), np.linspace(-3, 3, 50))
fig = go.Figure(data=go.Surface(z=z, colorscale="Viridis"))
fig.update_layout(scene=dict(aspectmode="data"))
```

## Mesh3d

```python
fig = go.Figure(data=go.Mesh3d(
    x=x_coords, y=y_coords, z=z_coords,
    i=tri_i, j=tri_j, k=tri_k,    # triangle indices
    color="lightblue", opacity=0.5,
))
```

## Cone (vector field in 3D)

```python
fig = go.Figure(data=go.Cone(
    x=x, y=y, z=z,
    u=u, v=v, w=w,                # vector components
    colorscale="Viridis",
    sizemode="absolute",          # "absolute", "scaled", "raw" (v6.6+)
    sizeref=0.1,
))
```

## Streamtube

```python
fig = go.Figure(data=go.Streamtube(
    x=x, y=y, z=z,
    u=u, v=v, w=w,
    colorscale="Viridis",
    arrow_scale=0.5,
    opacity=0.8,
))
```

## Isosurface

```python
fig = go.Figure(data=go.Isosurface(
    x=x, y=y, z=z, value=values,
    isomin=0.5, isomax=0.9,
    colorscale="Viridis",
    caps=dict(x=dict(visible=True), y=dict(visible=True), z=dict(visible=True)),
))
```

## Volume

```python
fig = go.Figure(data=go.Volume(
    x=x, y=y, z=z, value=values,
    isomin=0.2, isomax=0.8,
    opacity=0.1,
    surface_count=20,
))
```

## Sankey diagram

```python
fig = go.Figure(data=go.Sankey(
    node=dict(
        pad=15, thickness=15,
        label=["A", "B", "C", "D"],
        color="blue"
    ),
    link=dict(
        source=[0, 0, 1, 2],
        target=[2, 3, 3, 3],
        value=[8, 4, 2, 6]
    )
))
```

## Parallel coordinates

```python
fig = px.parallel_coordinates(df, color="category",
                              color_continuous_scale="Viridis",
                              labels={"col1": "Label 1", "col2": "Label 2"})
```

## Parallel categories

```python
fig = px.parallel_categories(df, color="category",
                             color_continuous_scale="Viridis")
```

## Indicator (KPI)

```python
fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=75,
    title=dict(text="Performance"),
    delta=dict(reference=80),
    gauge=dict(
        axis=dict(range=[None, 100]),
        bar=dict(color="darkblue"),
        threshold=dict(
            line=dict(color="red", width=4),
            thickness=0.75, value=80
        )
    )
))
```

## Table

```python
fig = go.Figure(data=go.Table(
    header=dict(values=["Col 1", "Col 2", "Col 3"],
                fill_color="paleturquoise", align="center"),
    cells=dict(values=[["A", "B"], [1, 2], [3, 4]],
               fill_color="lavender", align="center")
))
```

## 3D scene camera

```python
fig.update_layout(scene=dict(
    camera=dict(
        eye=dict(x=1.5, y=1.5, z=1.5),
        up=dict(x=0, y=0, z=1),
        projection=dict(type="perspective"),  # or "orthographic"
    ),
    dragmode="orbit",
))
```
