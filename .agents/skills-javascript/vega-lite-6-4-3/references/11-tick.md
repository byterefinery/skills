# Tick Marks

Tick marks render data as small line segments (ticks). They are useful for 1D distributions, strip plots, and compact representations of categorical counts.

## 1D Tick Distribution

Place ticks along a single axis to show the distribution of values. Compact alternative to histograms.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "1D tick distribution along the y-axis.",
  "data": {
    "values": [
      {"value": 5}, {"value": 8}, {"value": 12}, {"value": 15},
      {"value": 18}, {"value": 20}, {"value": 22}, {"value": 25},
      {"value": 28}, {"value": 30}, {"value": 33}, {"value": 35},
      {"value": 38}, {"value": 40}
    ]
  },
  "mark": "tick",
  "encoding": {
    "y": {"field": "value", "type": "quantitative", "title": "Value"}
  }
}
```

## Grouped Ticks by Category

Map a nominal field to `color` and use the other axis for grouping. Shows distribution within each category.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Grouped tick marks by category.",
  "data": {
    "values": [
      {"category": "A", "value": 10}, {"category": "A", "value": 15},
      {"category": "A", "value": 20}, {"category": "A", "value": 25},
      {"category": "B", "value": 30}, {"category": "B", "value": 35},
      {"category": "B", "value": 40}, {"category": "B", "value": 45},
      {"category": "C", "value": 50}, {"category": "C", "value": 55},
      {"category": "C", "value": 60}, {"category": "C", "value": 65}
    ]
  },
  "mark": "tick",
  "encoding": {
    "x": {"field": "category", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

## Tick Histogram

Use `bin` with `tick` marks for a compact histogram representation.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A tick histogram with binning.",
  "data": {
    "values": [
      {"value": 5}, {"value": 8}, {"value": 12}, {"value": 15},
      {"value": 18}, {"value": 20}, {"value": 22}, {"value": 25},
      {"value": 28}, {"value": 30}, {"value": 33}, {"value": 35},
      {"value": 38}, {"value": 40}, {"value": 42}, {"value": 45},
      {"value": 48}, {"value": 50}, {"value": 52}, {"value": 55}
    ]
  },
  "mark": "tick",
  "encoding": {
    "x": {"field": "value", "bin": true, "type": "quantitative"},
    "y": {"aggregate": "count", "title": "Frequency"}
  }
}
```

## Horizontal Strip Plot

Use `tick` marks oriented horizontally for a strip plot showing values along the x-axis.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Horizontal strip plot using tick marks.",
  "data": {
    "values": [
      {"group": "X", "value": 10}, {"group": "X", "value": 20},
      {"group": "X", "value": 35}, {"group": "X", "value": 45},
      {"group": "Y", "value": 15}, {"group": "Y", "value": 30},
      {"group": "Y", "value": 50}, {"group": "Y", "value": 60},
      {"group": "Z", "value": 25}, {"group": "Z", "value": 40},
      {"group": "Z", "value": 55}, {"group": "Z", "value": 70}
    ]
  },
  "mark": {"type": "tick", "thickness": 3},
  "encoding": {
    "y": {"field": "group", "type": "nominal"},
    "x": {"field": "value", "type": "quantitative"},
    "color": {"field": "group", "type": "nominal"}
  }
}
```
