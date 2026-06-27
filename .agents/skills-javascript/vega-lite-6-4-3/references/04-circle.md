# Circle Marks

Circle marks render data as circles, where size can encode a quantitative variable. They are the default mark for scatter plots and support bubble charts when `size` is mapped.

## Simple Scatter Plot

Map two quantitative fields to x and y. The `circle` mark places a circle at each data point.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A simple scatter plot using circle marks.",
  "data": {
    "values": [
      {"x": 10, "y": 28}, {"x": 15, "y": 45}, {"x": 20, "y": 39},
      {"x": 25, "y": 61}, {"x": 30, "y": 52}, {"x": 35, "y": 70},
      {"x": 40, "y": 65}, {"x": 45, "y": 82}, {"x": 50, "y": 78}
    ]
  },
  "mark": "circle",
  "encoding": {
    "x": {"field": "x", "type": "quantitative", "title": "X Axis"},
    "y": {"field": "y", "type": "quantitative", "title": "Y Axis"}
  }
}
```

## Colored Scatter Plot

Map a nominal field to `color` to distinguish groups in a scatter plot.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Scatter plot with color encoding for categories.",
  "data": {
    "values": [
      {"x": 10, "y": 20, "group": "A"}, {"x": 15, "y": 35, "group": "A"},
      {"x": 20, "y": 25, "group": "A"}, {"x": 25, "y": 40, "group": "A"},
      {"x": 12, "y": 50, "group": "B"}, {"x": 18, "y": 60, "group": "B"},
      {"x": 22, "y": 55, "group": "B"}, {"x": 28, "y": 65, "group": "B"},
      {"x": 14, "y": 70, "group": "C"}, {"x": 20, "y": 80, "group": "C"},
      {"x": 26, "y": 75, "group": "C"}, {"x": 30, "y": 85, "group": "C"}
    ]
  },
  "mark": "circle",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "color": {"field": "group", "type": "nominal"}
  }
}
```

## Bubble Chart

Map a quantitative field to `size` to create a bubble chart where circle area represents a third dimension.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A bubble chart with size encoding.",
  "data": {
    "values": [
      {"category": "A", "value": 30, "weight": 10},
      {"category": "B", "value": 50, "weight": 25},
      {"category": "C", "value": 40, "weight": 15},
      {"category": "D", "value": 70, "weight": 40},
      {"category": "E", "value": 60, "weight": 30}
    ]
  },
  "mark": "circle",
  "encoding": {
    "x": {"field": "category", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative", "title": "Value"},
    "size": {"field": "weight", "type": "quantitative", "title": "Weight"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

## Binned 2D Histogram (Hexbin-style)

Bin both x and y axes to create a 2D histogram where circle size represents count density.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A binned 2D histogram using circle marks.",
  "data": {
    "values": [
      {"x": 5, "y": 10}, {"x": 7, "y": 12}, {"x": 8, "y": 11},
      {"x": 10, "y": 15}, {"x": 12, "y": 14}, {"x": 15, "y": 20},
      {"x": 18, "y": 22}, {"x": 20, "y": 25}, {"x": 22, "y": 23},
      {"x": 25, "y": 30}, {"x": 28, "y": 28}, {"x": 30, "y": 35},
      {"x": 32, "y": 33}, {"x": 35, "y": 40}, {"x": 38, "y": 38},
      {"x": 40, "y": 45}, {"x": 6, "y": 11}, {"x": 9, "y": 13},
      {"x": 11, "y": 16}, {"x": 14, "y": 18}
    ]
  },
  "mark": "circle",
  "encoding": {
    "x": {"field": "x", "bin": true, "type": "quantitative"},
    "y": {"field": "y", "bin": true, "type": "quantitative"},
    "size": {"aggregate": "count", "title": "Count"}
  }
}
```

## Dot Plot (Wilkinson-style)

Use `circle` marks with small size for a clean dot plot. Add `opacity` to handle overplotting.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A dot plot with opacity for overplotting.",
  "data": {
    "values": [
      {"category": "A", "value": 10}, {"category": "A", "value": 12},
      {"category": "A", "value": 15}, {"category": "A", "value": 18},
      {"category": "B", "value": 20}, {"category": "B", "value": 22},
      {"category": "B", "value": 25}, {"category": "B", "value": 28},
      {"category": "C", "value": 30}, {"category": "C", "value": 32},
      {"category": "C", "value": 35}, {"category": "C", "value": 38}
    ]
  },
  "mark": {"type": "circle", "opacity": 0.6, "size": 50},
  "encoding": {
    "x": {"field": "category", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```
