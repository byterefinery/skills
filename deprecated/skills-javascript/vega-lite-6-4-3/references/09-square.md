# Square Marks

Square marks render data as squares with uniform width and height. Unlike `circle`, squares tile more efficiently and are useful for scatter plots where circular overlap is undesirable.

## Simple Square Scatter Plot

Map two quantitative fields to x and y. The `square` mark places a square at each data point.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A scatter plot using square marks.",
  "data": {
    "values": [
      {"x": 10, "y": 28}, {"x": 15, "y": 45}, {"x": 20, "y": 39},
      {"x": 25, "y": 61}, {"x": 30, "y": 52}, {"x": 35, "y": 70},
      {"x": 40, "y": 65}, {"x": 45, "y": 82}, {"x": 50, "y": 78}
    ]
  },
  "mark": "square",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"}
  }
}
```

## Colored Square Plot with Size

Combine `color` and `size` encodings for a multi-dimensional square plot.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Square plot with color and size encodings.",
  "data": {
    "values": [
      {"x": 5, "y": 10, "group": "A", "weight": 10},
      {"x": 15, "y": 25, "group": "A", "weight": 20},
      {"x": 25, "y": 40, "group": "B", "weight": 15},
      {"x": 35, "y": 55, "group": "B", "weight": 30},
      {"x": 45, "y": 70, "group": "C", "weight": 25},
      {"x": 55, "y": 85, "group": "C", "weight": 35}
    ]
  },
  "mark": "square",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "color": {"field": "group", "type": "nominal"},
    "size": {"field": "weight", "type": "quantitative"}
  }
}
```

## Filled Square Plot

Use `filled: true` in the mark definition to fill squares with color.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Filled square plot.",
  "data": {
    "values": [
      {"x": 10, "y": 20, "category": "X"},
      {"x": 20, "y": 35, "category": "X"},
      {"x": 30, "y": 50, "category": "Y"},
      {"x": 40, "y": 65, "category": "Y"},
      {"x": 50, "y": 80, "category": "Z"}
    ]
  },
  "mark": {"type": "square", "filled": true, "size": 80},
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```
