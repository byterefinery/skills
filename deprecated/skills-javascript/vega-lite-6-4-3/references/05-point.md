# Point Marks

Point marks render data as geometric shapes. Unlike `circle`, `point` supports multiple shape types (triangle, cross, diamond, etc.) via the `shape` encoding channel.

## Simple Point Plot

Map quantitative fields to x and y. The `point` mark places a shape at each data point.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A simple point plot.",
  "data": {
    "values": [
      {"x": 10, "y": 28}, {"x": 15, "y": 45}, {"x": 20, "y": 39},
      {"x": 25, "y": 61}, {"x": 30, "y": 52}, {"x": 35, "y": 70},
      {"x": 40, "y": 65}, {"x": 45, "y": 82}, {"x": 50, "y": 78}
    ]
  },
  "mark": "point",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"}
  }
}
```

## Points with Shape Encoding

Map a nominal field to `shape` to use different symbols for each category. Vega-Lite supports circle, square, cross, diamond, triangle-up, triangle-right, triangle-down, and star.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Point plot with shape encoding for categories.",
  "data": {
    "values": [
      {"x": 10, "y": 20, "group": "A"}, {"x": 15, "y": 35, "group": "A"},
      {"x": 20, "y": 25, "group": "A"},
      {"x": 12, "y": 50, "group": "B"}, {"x": 18, "y": 60, "group": "B"},
      {"x": 22, "y": 55, "group": "B"},
      {"x": 14, "y": 70, "group": "C"}, {"x": 20, "y": 80, "group": "C"},
      {"x": 26, "y": 75, "group": "C"}
    ]
  },
  "mark": "point",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "shape": {"field": "group", "type": "nominal"},
    "color": {"field": "group", "type": "nominal"}
  }
}
```

## Filled Points

Use `filled: true` in the mark definition to fill point shapes with color instead of just stroking them.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Filled point plot with custom shapes.",
  "data": {
    "values": [
      {"x": 5, "y": 10, "category": "Low"},
      {"x": 15, "y": 25, "category": "Medium"},
      {"x": 25, "y": 40, "category": "High"},
      {"x": 35, "y": 55, "category": "Low"},
      {"x": 45, "y": 70, "category": "Medium"},
      {"x": 55, "y": 85, "category": "High"}
    ]
  },
  "mark": {"type": "point", "filled": true, "size": 100},
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

## 1D Point Distribution

Place points along a single axis to show value distribution. Useful for comparing distributions across categories.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "1D point distribution along y-axis.",
  "data": {
    "values": [
      {"value": 10}, {"value": 12}, {"value": 15}, {"value": 18},
      {"value": 20}, {"value": 22}, {"value": 25}, {"value": 28},
      {"value": 30}, {"value": 32}, {"value": 35}, {"value": 38},
      {"value": 40}, {"value": 42}, {"value": 45}
    ]
  },
  "mark": {"type": "point", "filled": true},
  "encoding": {
    "y": {"field": "value", "type": "quantitative", "title": "Value"}
  }
}
```
