# Text Marks

Text marks render strings at data positions. They are used for labels, annotations, and data value displays. Combine with other marks via layering for labeled charts.

## Basic Text Labels

Place text at x/y coordinates using the `text` encoding channel to specify what string to display.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Text labels at data positions.",
  "data": {
    "values": [
      {"x": 10, "y": 20, "label": "A"},
      {"x": 25, "y": 40, "label": "B"},
      {"x": 40, "y": 60, "label": "C"},
      {"x": 55, "y": 80, "label": "D"}
    ]
  },
  "mark": "text",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "text": {"field": "label", "type": "nominal"}
  }
}
```

## Bar Chart with Value Labels

Layer `text` marks on top of `bar` marks to show values above each bar. Use `dy` to offset text vertically.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Bar chart with value labels on top.",
  "data": {
    "values": [
      {"category": "A", "value": 28}, {"category": "B", "value": 55},
      {"category": "C", "value": 43}, {"category": "D", "value": 91},
      {"category": "E", "value": 81}
    ]
  },
  "layer": [
    {
      "mark": "bar",
      "encoding": {
        "x": {"field": "category", "type": "nominal"},
        "y": {"field": "value", "type": "quantitative"}
      }
    },
    {
      "mark": {"type": "text", "dy": -10},
      "encoding": {
        "x": {"field": "category", "type": "nominal"},
        "y": {"field": "value", "type": "quantitative"},
        "text": {"field": "value", "type": "quantitative"}
      }
    }
  ]
}
```

## Formatted Text with Colors

Use `color` encoding to style text and `fontSize` in the mark definition for sizing.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Colored text marks with custom font size.",
  "data": {
    "values": [
      {"x": 10, "y": 20, "status": "Good", "label": "OK"},
      {"x": 30, "y": 40, "status": "Warning", "label": "WARN"},
      {"x": 50, "y": 60, "status": "Error", "label": "ERR"}
    ]
  },
  "mark": {"type": "text", "fontSize": 16},
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "text": {"field": "label", "type": "nominal"},
    "color": {"field": "status", "type": "nominal"}
  }
}
```

## Scatter Plot with Labels

Overlay text labels on a scatter plot to identify individual points.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Scatter plot with text labels for each point.",
  "data": {
    "values": [
      {"x": 10, "y": 28, "name": "Alpha"},
      {"x": 20, "y": 45, "name": "Beta"},
      {"x": 30, "y": 39, "name": "Gamma"},
      {"x": 40, "y": 61, "name": "Delta"},
      {"x": 50, "y": 52, "name": "Epsilon"}
    ]
  },
  "layer": [
    {
      "mark": "circle",
      "encoding": {
        "x": {"field": "x", "type": "quantitative"},
        "y": {"field": "y", "type": "quantitative"}
      }
    },
    {
      "mark": {"type": "text", "dx": 8, "dy": -8},
      "encoding": {
        "x": {"field": "x", "type": "quantitative"},
        "y": {"field": "y", "type": "quantitative"},
        "text": {"field": "name", "type": "nominal"}
      }
    }
  ]
}
```
