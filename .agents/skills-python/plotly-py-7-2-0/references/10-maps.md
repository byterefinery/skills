# Maps (v7 — MapLibre-based)

## Trace families

- **Outline maps** (`geo` subplot): `go.Scattergeo`, `go.Choropleth`, `go.Line` with geo — country/region outlines, GeoJSON
- **Tile maps** (`map` subplot, MapLibre): `go.Scattermap`, `go.Choroplethmap`, `go.Densitymap` — raster tile underlays, no API key needed for built-in styles
- Express: `px.scatter_geo`, `px.line_geo`, `px.choropleth`, `px.scatter_map`, `px.line_map`, `px.choropleth_map`, `px.density_map`
- Factories: `ff.create_hexbin_map` (the Mapbox hexbin factory is removed)

## Mapbox → MapLibre migration (v7 hard break)

| Removed | Use instead |
|---|---|
| `go.Scattermapbox` | `go.Scattermap` |
| `go.Choroplethmapbox` | `go.Choroplethmap` |
| `go.Densitymapbox` | `go.Densitymap` |
| `px.scatter_mapbox` | `px.scatter_map` |
| `px.line_mapbox` | `px.line_map` |
| `px.choropleth_mapbox` | `px.choropleth_map` |
| `px.density_mapbox` | `px.density_map` |
| `layout.mapbox` | `layout.map` (identical nested attributes) |
| `mapbox_style` (px) | `map_style` (px) |
| `mapboxAccessToken` (config) | gone — Plotly-provided styles need no API key |

Built-in `map_style` names kept: `basic`, `streets`, `outdoors`, `light`, `dark`, `satellite`, `satellite-streets` — now served by Carto/ESRI, slightly different appearance. External MapLibre styles remain supported.

## v7 changed defaults: maps fit your data

- `layout.geo.fitbounds` defaults to `"locations"` (was `False`) — geo subplots auto-fit the initial view to plotted locations.
- Tile-map subplots get the same via new `layout.map.fitbounds` (default `"locations"`).
- Setting your own view attributes turns auto-fitting off: on `geo`, `center` and `projection.scale` always do (plus `projection.rotation`, `lonaxis.range`, `lataxis.range` except on a scoped subplot with a clipped projection); on `map`, `center` or `zoom` does.
- For the previous fixed world view: `fig.update_layout(geo=dict(fitbounds=False))`.

```python
import plotly.graph_objects as go

fig = go.Figure(go.Choropleth(locations=["CAN", "MEX"], z=[1, 2], showscale=False))
fig.update_layout(geo=dict(fitbounds=False))   # previous world view
```

## Country/location name resolution

`locationmode="country names"` now resolves via the `country-iso-search` library: accepts ISO-3166 codes, UN M49 numeric codes, flag emoji, historical and native names (`"Burma"`, `"Türkiye"`), ignores case/accents/punctuation, rejects partial phrases that previously matched by accident. Unrecognized names are logged and skipped. Use `locationmode="ISO-3"` for certainty.

## Choropleth essentials

```python
import plotly.express as px

df = px.data.gapminder().query("year == 2007")
fig = px.choropleth(
    df, locations="iso_a3", color="gdpPercap",
    color_continuous_scale="Viridis",
    labels={"gdpPercap": "GDP per capita"},
)
```

- `locations` + `locationmode`: `"ISO-3"`, `"ISO-A3"` (alias), `"USA-state"`-style modes, `"country names"`, custom GeoJSON via `locations` as a column of FeatureCollections
- Custom GeoJSON: pass a GeoJSON dict/URL as the last positional or via `locations` when using `go.Choropleth`

## Tile map essentials

```python
fig = px.scatter_map(
    df, lat="lat", lon="lon", color="category",
    map_style="light",            # basic, streets, outdoors, light, dark, satellite, satellite-streets
    zoom=3,
)
```

v7 rendering details for `go.Scattermap`:
- Marker icons are tinted with `marker.color` (previously always black)
- Maki icon set updated from v2.1 to 8.2 — a few icon names were removed between versions
- Legend swatches always draw a circle, regardless of `marker.symbol`

`px.*_map()` auto-fits when `zoom` and `center` are not specified (improved in 7.0.0).

## Map subplots

Multiple map/geo subplots in one figure: use `make_subplots(specs=[[{"type": "geo"}, {"type": "map"}]])` and add traces with `row`/`col`. `map` subplot type is required for MapLibre traces.
