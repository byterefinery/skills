# Maps

## MapLibre maps (preferred, v6.0+)

MapLibre-based traces replaced Mapbox traces. No API key needed.

```python
import plotly.express as px

# Scatter map
fig = px.scatter_map(df, lat="lat", lon="lon", color="value")

# Line map
fig = px.line_map(df, lat="lat", lon="lon", color="route")

# Choropleth map
fig = px.choropleth_map(
    df,
    geojson=geojson_data,
    locations="id",
    color="value",
    color_continuous_scale="Viridis",
)

# Density map
fig = px.density_map(df, lat="lat", lon="lon", radius=10)
```

## Geo (SVG-based)

```python
# Scatter geo
fig = px.scatter_geo(df, lat="lat", lon="lon", color="value",
                     projection="natural earth")

# Line geo
fig = px.line_geo(df, lat="lat", lon="lon", color="route")

# Choropleth (countries/US states)
fig = px.choropleth(df, locations="iso_alpha", locationmode="country codes",
                    color="value", scope="europe")
```

Projection options: `"equirectangular"`, `"mercator"`, `"orthographic"`, `"natural earth"`, `"kavrayskiy7"`, `"mollweide"`, `"hammer"`, `"loberezhnikov"`.

## Mapbox (deprecated)

`scatter_mapbox`, `line_mapbox`, `choropleth_mapbox`, and `create_hexbin_mapbox` are deprecated. They still work but require `config.mapboxAccessToken`:

```python
import plotly.express as px
from plotly.express import set_mapbox_access_token

set_mapbox_access_token("YOUR_TOKEN")
fig = px.scatter_mapbox(df, lat="lat", lon="lon")
```

## Choropleth location modes

```python
# Country codes (ISO-3)
px.choropleth(df, locations="iso_alpha", locationmode="country names")

# US states
px.choropleth(df, locations="state", locationmode="USA-states", scope="usa")

# FIPS codes
px.choropleth(df, locations="fips", locationmode="USA-fips", scope="usa")

# Custom geojson
px.choropleth_map(df, geojson=geojson, locations="id", color="value")
```

## Center and zoom

```python
fig.update_layout(
    map=dict(
        center=dict(lat=40, lon=-100),
        zoom=4,
        style="light",        # light, dark, satellite, satellite-streets
    )
)
```

For geo plots:
```python
fig.update_layout(
    geo=dict(
        projection_type="natural earth",
        center=dict(lat=40, lon=-100),
        zoom=4,
        showland=True,
        landcolor="rgb(217, 217, 217)",
    )
)
```

## Density map radius

```python
fig = px.density_map(df, lat="lat", lon="lon", radius=20)
# radius: kernel size in pixels
```
