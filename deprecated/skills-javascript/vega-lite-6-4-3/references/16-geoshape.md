# Geoshape Marks

The `geoshape` mark renders geographic features from TopoJSON or GeoJSON data. It supports choropleth maps, point-on-map visualizations, and custom projections. Requires a geographic data source with `url` pointing to a TopoJSON file and a `projection` specification.

## Choropleth Map (US States)

Color US states by a quantitative value using `geoshape` with a TopoJSON data source.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A choropleth map of US states.",
  "data": {
    "url": "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
  },
  "mark": "geoshape",
  "encoding": {
    "color": {"value": "#ccc"}
  },
  "projection": {"type": "albersUsa"}
}
```

## World Map with Projection

Render world countries with a geographic projection. Use `projection` to specify the map projection type.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A world map with equirectangular projection.",
  "data": {
    "url": "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
  },
  "mark": "geoshape",
  "encoding": {
    "color": {"value": "#69b3a2"},
    "stroke": {"value": "white"}
  },
  "projection": {"type": "equirectangular"}
}
```

## Geoshape with Circle Overlay

Layer `geoshape` and `circle` marks to show points on a map. The circles use `latitude` and `longitude` encodings.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Map with geoshape and circle overlay.",
  "data": {
    "url": "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
  },
  "layer": [
    {
      "mark": "geoshape",
      "encoding": {
        "color": {"value": "#ddd"},
        "stroke": {"value": "white"}
      }
    },
    {
      "data": {
        "values": [
          {"name": "London", "lat": 51.5, "lon": -0.1, "pop": 8900},
          {"name": "Tokyo", "lat": 35.7, "lon": 139.7, "pop": 13960},
          {"name": "New York", "lat": 40.7, "lon": -74.0, "pop": 8340},
          {"name": "Sydney", "lat": -33.9, "lon": 151.2, "pop": 5310}
        ]
      },
      "mark": "circle",
      "encoding": {
        "latitude": {"field": "lat", "type": "quantitative"},
        "longitude": {"field": "lon", "type": "quantitative"},
        "size": {"field": "pop", "type": "quantitative"}
      }
    }
  ],
  "projection": {"type": "equirectangular"}
}
```
