# v6 Migration

## Breaking changes from v5 to v6

### Removed features

- **`pointcloud` and `heatmapgl` traces** — dropped entirely. Use `scattergl` and `heatmap` instead.
- **`bardir` attribute** — use `orientation` instead (`"v"` or `"h"`).
- **`titlefont`, `titleposition`, `titleside`, `titleoffset`** — use `title.font`, `title.x`, `title.y` via `go.layout.Title`.
- **`annotation.ref`** — use `annotation.xref` and `annotation.yref`.
- **Error bar `opacity`** — use alpha channel in the `color` attribute.
- **`gl3d.cameraposition`** — use `gl3d.camera`.
- **`zauto`, `zmin`, `zmax` on surface** — use `zmin`/`zmax` on the scene axis.
- **`autotick` on cartesian axes** — removed.
- **`transforms`** — removed from the API.
- **Jupyter Notebook ≤ 6** — minimum supported version is now 7.0.0.
- **`tenacity` dependency** — dropped.

### Mapbox deprecation

Mapbox-based traces (`scatter_mapbox`, `choropleth_mapbox`, `density_mapbox`) and `create_hexbin_mapbox` are deprecated. Migrate to MapLibre:

| Old (Mapbox) | New (MapLibre) |
|---|---|
| `px.scatter_mapbox()` | `px.scatter_map()` |
| `px.line_mapbox()` | `px.line_map()` |
| `px.choropleth_mapbox()` | `px.choropleth_map()` |
| `ff.create_hexbin_mapbox()` | `ff.create_hexbin_map()` |

### New map functions (v5.24+)

`px.scatter_map()`, `px.line_map()`, `px.choropleth_map()`, `px.density_map()` use MapLibre and need no API key.

### DataFrame-agnostic Express

Plotly Express now uses Narwhals internally, supporting pandas, polars, and other compatible DataFrames without code changes.

### FigureWidget → anywidget

`go.FigureWidget` now uses `anywidget` instead of ipywidgets. Install `anywidget` separately.

### ES6 imports

Plotly.js is loaded via native ES6 imports instead of requirejs.

### Kaleido v1

Image export uses Kaleido ≥ 1.3.0. The legacy `orca` CLI is deprecated. Kaleido v1 bundles Chromium.

### New `plotly[express]` extra

```bash
pip install "plotly[express]"   # installs numpy for px
pip install "plotly[kaleido]"   # installs kaleido for write_image
```

### SRI hashes

`include_plotlyjs="cdn"` now includes Subresource Integrity hashes for security.

### Base64 typed arrays

NumPy arrays use base64 encoding in plotly JSON for precision and performance.

## v6.8.0 specific changes

- `font` parameter added to `make_subplots`
- `color_continuous_scale` no longer ignored when template has `autocolorscale=True`
- Colab renderer uses `COLAB_NOTEBOOK_ID` env var instead of import detection
- Fixed annotation placement for `add_vline`/`add_hline`/`add_vrect`/`add_hrect` on datetime axes
- `js/` directory no longer installed as top-level Python package
- Default headers added for Kaleido to avoid blocked OSM tiles
- `default_height`/`default_width` propagate to `to_html` wrapper div
- `graph_objects.__eq__` returns `NotImplemented` for proper comparison delegation
- plotly.js updated to 3.6.0: per-slice `legendrank` arrays, `hoversort` layout attribute
