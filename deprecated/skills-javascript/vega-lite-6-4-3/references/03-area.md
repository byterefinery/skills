# Area Charts

Area charts fill the area between a line and an axis (or between two lines). They are useful for showing magnitude of change over time.

## Simple Area Chart

Map a temporal or ordinal field to x and a quantitative field to y. The area fills from the axis to the data line.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A simple area chart.",
  "data": {
    "values": [
      {"month": "Jan", "value": 20}, {"month": "Feb", "value": 35},
      {"month": "Mar", "value": 42}, {"month": "Apr", "value": 38},
      {"month": "May", "value": 55}, {"month": "Jun", "value": 61},
      {"month": "Jul", "value": 58}, {"month": "Aug", "value": 65}
    ]
  },
  "mark": "area",
  "encoding": {
    "x": {"field": "month", "type": "ordinal"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```

## Stacked Area Chart

Like stacked bars, mapping a nominal field to `color` automatically stacks area marks.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A stacked area chart.",
  "data": {
    "values": [
      {"month": "Jan", "category": "A", "value": 10},
      {"month": "Jan", "category": "B", "value": 15},
      {"month": "Feb", "category": "A", "value": 12},
      {"month": "Feb", "category": "B", "value": 20},
      {"month": "Mar", "category": "A", "value": 18},
      {"month": "Mar", "category": "B", "value": 14},
      {"month": "Apr", "category": "A", "value": 15},
      {"month": "Apr", "category": "B", "value": 25}
    ]
  },
  "mark": "area",
  "encoding": {
    "x": {"field": "month", "type": "ordinal"},
    "y": {"field": "value", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

## Area Chart with y2 (Range)

Use `y` and `y2` to shade the area between two values, such as a temperature range.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Area chart showing a range between two values.",
  "data": {
    "values": [
      {"month": "Jan", "min": -5, "max": 5},
      {"month": "Feb", "min": -2, "max": 8},
      {"month": "Mar", "min": 3, "max": 15},
      {"month": "Apr", "min": 8, "max": 22},
      {"month": "May", "min": 12, "max": 28},
      {"month": "Jun", "min": 15, "max": 32}
    ]
  },
  "mark": "area",
  "encoding": {
    "x": {"field": "month", "type": "ordinal"},
    "y": {"field": "min", "type": "quantitative", "title": "Temperature (C)"},
    "y2": {"field": "max"}
  }
}
```

## Normalized Area Chart

Use `stack: "normalize"` to show proportional areas that sum to 100%.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Normalized stacked area chart (100%).",
  "data": {
    "values": [
      {"month": "Jan", "category": "A", "value": 20},
      {"month": "Jan", "category": "B", "value": 30},
      {"month": "Jan", "category": "C", "value": 10},
      {"month": "Feb", "category": "A", "value": 25},
      {"month": "Feb", "category": "B", "value": 20},
      {"month": "Feb", "category": "C", "value": 15},
      {"month": "Mar", "category": "A", "value": 30},
      {"month": "Mar", "category": "B", "value": 25},
      {"month": "Mar", "category": "C", "value": 10}
    ]
  },
  "mark": "area",
  "encoding": {
    "x": {"field": "month", "type": "ordinal"},
    "y": {
      "field": "value",
      "type": "quantitative",
      "stack": "normalize",
      "scale": {"domain": [0, 1]},
      "axis": {"format": ".0%"}
    },
    "color": {"field": "category", "type": "nominal"}
  }
}
```

## Layered Area with Line Overlay

Combine area and line marks in a layer to show both the filled region and the boundary.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Area chart with line overlay.",
  "data": {
    "values": [
      {"month": "Jan", "value": 20}, {"month": "Feb", "value": 35},
      {"month": "Mar", "value": 42}, {"month": "Apr", "value": 38},
      {"month": "May", "value": 55}
    ]
  },
  "layer": [
    {
      "mark": {"type": "area", "opacity": 0.3},
      "encoding": {
        "x": {"field": "month", "type": "ordinal"},
        "y": {"field": "value", "type": "quantitative"}
      }
    },
    {
      "mark": {"type": "line", "strokeWidth": 2},
      "encoding": {
        "x": {"field": "month", "type": "ordinal"},
        "y": {"field": "value", "type": "quantitative"}
      }
    }
  ]
}
```
