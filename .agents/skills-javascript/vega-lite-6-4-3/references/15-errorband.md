# Errorband

The `errorband` mark is a composite mark that renders shaded uncertainty regions. Unlike `errorbar` which shows line-based error ranges, `errorband` fills the area between upper and lower bounds. It computes error ranges automatically from raw data.

## Vertical Error Band (Auto-computed)

Use `errorband` in a layer spec. Vega-Lite computes the confidence interval automatically from raw data.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A vertical error band computed from raw data.",
  "data": {
    "values": [
      {"month": "Jan", "value": 10}, {"month": "Jan", "value": 15},
      {"month": "Jan", "value": 20}, {"month": "Jan", "value": 25},
      {"month": "Feb", "value": 30}, {"month": "Feb", "value": 35},
      {"month": "Feb", "value": 40}, {"month": "Feb", "value": 45},
      {"month": "Mar", "value": 40}, {"month": "Mar", "value": 45},
      {"month": "Mar", "value": 50}, {"month": "Mar", "value": 55},
      {"month": "Apr", "value": 35}, {"month": "Apr", "value": 40},
      {"month": "Apr", "value": 45}, {"month": "Apr", "value": 50}
    ]
  },
  "mark": "errorband",
  "encoding": {
    "x": {"field": "month", "type": "ordinal"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```

## Error Band with Line Overlay

Layer a `line` mark over the `errorband` to show the mean trend line through the uncertainty region.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Error band with a line overlay showing the mean.",
  "data": {
    "values": [
      {"month": "Jan", "value": 10}, {"month": "Jan", "value": 15},
      {"month": "Jan", "value": 20},
      {"month": "Feb", "value": 30}, {"month": "Feb", "value": 35},
      {"month": "Feb", "value": 40},
      {"month": "Mar", "value": 40}, {"month": "Mar", "value": 45},
      {"month": "Mar", "value": 50},
      {"month": "Apr", "value": 35}, {"month": "Apr", "value": 40},
      {"month": "Apr", "value": 45}
    ]
  },
  "layer": [
    {
      "mark": {"type": "errorband", "opacity": 0.3},
      "encoding": {
        "x": {"field": "month", "type": "ordinal"},
        "y": {"field": "value", "type": "quantitative"}
      }
    },
    {
      "mark": {"type": "line", "strokeWidth": 2},
      "encoding": {
        "x": {"field": "month", "type": "ordinal"},
        "y": {"aggregate": "mean", "field": "value", "type": "quantitative"}
      }
    }
  ]
}
```

## Horizontal Error Band

Use x-axis encoding for horizontal error bands.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A horizontal error band.",
  "data": {
    "values": [
      {"row": "A", "value": 10}, {"row": "A", "value": 15},
      {"row": "A", "value": 20},
      {"row": "B", "value": 30}, {"row": "B", "value": 35},
      {"row": "B", "value": 40},
      {"row": "C", "value": 50}, {"row": "C", "value": 55},
      {"row": "C", "value": 60}
    ]
  },
  "mark": "errorband",
  "encoding": {
    "y": {"field": "row", "type": "nominal"},
    "x": {"field": "value", "type": "quantitative"}
  }
}
```

## Error Band with Borders and Custom Extent

Use `borders: true` to draw outlines around the error band region. Set `extent` for different error computation methods.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Error band with borders and stdev extent.",
  "data": {
    "values": [
      {"x": 1, "value": 10}, {"x": 1, "value": 15},
      {"x": 1, "value": 20},
      {"x": 2, "value": 30}, {"x": 2, "value": 35},
      {"x": 2, "value": 40},
      {"x": 3, "value": 40}, {"x": 3, "value": 45},
      {"x": 3, "value": 50},
      {"x": 4, "value": 35}, {"x": 4, "value": 40},
      {"x": 4, "value": 45}
    ]
  },
  "mark": {"type": "errorband", "borders": true, "extent": "stdev", "opacity": 0.4},
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```
