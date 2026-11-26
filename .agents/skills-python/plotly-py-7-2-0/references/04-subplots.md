# Subplots

## make_subplots

```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go

fig = make_subplots(
    rows=2, cols=2,
    shared_xaxes=False, shared_yaxes=False,   # "all", "first row", ...
    horizontal_spacing=0.15, vertical_spacing=0.2,
    subplot_titles=("A", "B", "C", "D"),
    specs=[[{"type": "xy"}, {"type": "xy"}],
           [{"type": "xy"}, {"type": "pie"}]],
    # for 3D: specs=[...{"type": "scatter3d"}...]
    # for maps: specs=[...{"type": "geo"}...], rows/cols as needed
)

fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]), row=1, col=1)
fig.add_trace(go.Bar(x=[1, 2], y=[3, 4]), row=1, col=2)
```

- `type` per subplot cell: `"xy"`, `"domain"` (pie/sunburst), `"scatter3d"`, `"surface3d"`, `"ternary"`, `"polar"`, `"geo"`, `"map"`.
- Omitting `row`/`col` in `add_trace` targets `row=1, col=1`.
- `secondary_y=True` in `specs` creates a twin-y axis for that cell (`yaxis2`/`yaxis4`/...).

## v7: overlaying axes share ticks by default

An axis that overlays another (`yaxis2.overlaying="y"`) now defaults `tickmode` to `"sync"`: it draws ticks and gridlines at the base axis's positions, labeled from its own range, so the two axes share one grid. Set `tickmode="auto"` on the overlaying axis for the previous behavior of two independent grids.

## Secondary y axis (twin axes)

```python
fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=[1, 2], y=[10, 20], name="left"), row=1, col=1, secondary_y=False)
fig.add_trace(go.Scatter(x=[1, 2], y=[0.1, 0.2], name="right"), row=1, col=1, secondary_y=True)
```

## Mixed subplot types

Specs let you mix cartesian, pie (`"domain"`), 3D (`"scatter3d"`), geo, and map cells in one figure. Trace-to-subplot targeting is always by `row`/`col` in `add_trace`.

## v7.2.0 fix

`add_hline`, `add_vline`, `add_hrect`, `add_vrect` no longer drop the shape on an empty subplot when `row` and `col` select a single subplot (fixed in 7.2.0).

## Sizing

`make_subplots(rows=..., cols=...)` computes subplot positions automatically; you can post-adjust with `fig.update_layout()` margins or `fig.update_xaxes(domain=[...])` / `fig.update_yaxes(domain=[...])` for manual control.
