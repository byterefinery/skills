# Interactive Features

## Hover

- `hovertemplate` on traces: `"<b>%{x}</b>: %{y}<extra>%{name}</extra>"`. `%{...}` variables reference the trace data (`x`, `y`, `customdata`, `text`, `label`, `value`, etc.).
- px fills hover labels automatically from labels; control with `hover_name` (row identifier) and `hover_data` (list of extra columns).
- `hovermode`: `"closest"` (default), `"x"`, `"y"`, `"x unified"`, `"y unified"` — set on layout.
- `hoverlabel` styling: `fig.update_layout(hoverlabel=dict(bgcolor="white", font=dict(size=14)))`.
- To suppress hover on a trace: `hoverinfo="skip"`.

## Selection and brushing

- Box/lasso selection, and zoom/pan, are built into the modebar. Box/lasso select data serialization for multiple subplots was fixed in 7.2.0.
- `fig.select_box(...)` / `fig.select_lasso(...)` on `go.FigureWidget` give programmatic access to selected points.
- Range slider on the x-axis: `fig.update_xaxes(rangeslider_visible=True)`.

## Events and callbacks

Plotly.py figures have no native Python event callbacks (that is a Dash feature). For interactivity in a plain figure, use:

- **Dash** — `dcc.Graph` with `Input`/`Output` callbacks (`plotly.data` events like `clickData`, `relayoutData` arrive as component values). See [09 — Dash](https://plotly.com/python/dash/).
- **FigureWidget** — a `go.FigureWidget` exposes child objects with `.observe()` (anywidget-based) for in-notebook callbacks.

## FigureWidget

```python
from plotly.graph_objects import FigureWidget

fig = FigureWidget(go.Scatter(x=[1, 2, 3], y=[4, 3, 2]))
# fig.data[0] is a Graph Object; observe attribute changes:
fig.data[0].observe(handler, names=["y"])
```

Requires `pip install anywidget`. Works in JupyterLab 4+ and Jupyter Notebook 7+. `FigureWidget` mirrors `go.Figure`'s API (add_trace, update_layout, ...).

## Config (modebar behavior)

`fig.show(config={...})` or `fig.to_html(config={...})` / `fig.write_html(config={...})`:

- `scrollZoom=True`, `scrollToPan=True`
- `displayModeBar=True`, `displaylogo=False`
- `modeBarButtonsToAdd=["toImage", "downloadImage"]`, `modeBarButtonsToRemove=["lasso2d"]`
- `showSendToCloud=True` (default in v7) — adds a "Share chart…" modebar button that creates a Plotly Cloud link
- Removed in v7: `showLink`, `link_text`, `sendData`, `showSources`, `showEditInChartStudio`, `mapboxAccessToken`

v7.1 (plotly.js 4.1) adds an opt-in modebar button for downloading a figure as JSON, `legend.groupdoubleclick` (legend double-click group behavior), and raises the default double-click delay to 500 ms.

## Animations

- px: `animation_frame="year"`, `animation_group="country"` create frames automatically.
- go: build frames manually:

```python
fig.update_frames(
    [dict(data=[go.Scatter(x=..., y=...)], name="2000")],
)
fig.update_layout(updatemenus=[dict(type="buttons", buttons=[...])])
```

- Sliders: `fig.update_layout(sliders=[dict(steps=[dict(method="update", args=[["data[0].x", "data[0].y"]], label="2000"), ...])])`.

## Keyboard and modebar

Built-in modebar buttons: zoom, pan, select, lasso, zoom reset, auto-size, download PNG, share. All are removable per figure via `modeBarButtonsToRemove`.
