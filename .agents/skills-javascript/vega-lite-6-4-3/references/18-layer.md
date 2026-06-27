# Layered Specs

Layered specs combine multiple mark layers on shared data using the `layer` property. Each layer can have its own mark type, encoding, and transforms. Layers share the same view, axes, and legends by default.

## Bar with Line Overlay

Combine `bar` and `line` marks to show both individual values and a trend line.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Bar chart with a line overlay showing the mean.",
  "data": {
    "values": [
      {"month": "Jan", "value": 20}, {"month": "Feb", "value": 35},
      {"month": "Mar", "value": 42}, {"month": "Apr", "value": 38},
      {"month": "May", "value": 55}, {"month": "Jun", "value": 61}
    ]
  },
  "layer": [
    {
      "mark": "bar",
      "encoding": {
        "x": {"field": "month", "type": "ordinal"},
        "y": {"field": "value", "type": "quantitative"}
      }
    },
    {
      "mark": {"type": "line", "stroke": "red", "strokeWidth": 2},
      "encoding": {
        "x": {"field": "month", "type": "ordinal"},
        "y": {"aggregate": "mean", "type": "quantitative"}
      }
    }
  ]
}
```

## Scatter Plot with Regression Line

Layer `circle` marks with a `rule` or `line` mark showing a regression or trend.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Scatter plot with a trend line.",
  "data": {
    "values": [
      {"x": 1, "y": 2}, {"x": 2, "y": 4.5}, {"x": 3, "y": 4},
      {"x": 4, "y": 7}, {"x": 5, "y": 8}, {"x": 6, "y": 9},
      {"x": 7, "y": 11}, {"x": 8, "y": 13}, {"x": 9, "y": 12}
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
      "mark": {"type": "line", "color": "red", "strokeWidth": 2},
      "transform": [
        {"regression": "y", "on": "x", "groupby": []}
      ],
      "encoding": {
        "x": {"field": "x", "type": "quantitative"},
        "y": {"field": "y", "type": "quantitative"}
      }
    }
  ]
}
```

## Dual Axis Chart

Use independent `y` encodings in different layers to create a dual-axis chart with two scales.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Dual axis chart with bar and line.",
  "data": {
    "values": [
      {"month": "Jan", "sales": 100, "profit": 20},
      {"month": "Feb", "sales": 120, "profit": 25},
      {"month": "Mar", "sales": 110, "profit": 22},
      {"month": "Apr", "sales": 140, "profit": 30},
      {"month": "May", "sales": 160, "profit": 28}
    ]
  },
  "layer": [
    {
      "mark": "bar",
      "encoding": {
        "x": {"field": "month", "type": "ordinal"},
        "y": {"field": "sales", "type": "quantitative", "title": "Sales"}
      }
    },
    {
      "mark": {"type": "line", "color": "red"},
      "encoding": {
        "x": {"field": "month", "type": "ordinal"},
        "y": {"field": "profit", "type": "quantitative", "title": "Profit", "axis": {"orient": "right"}}
      }
    }
  ]
}
```

## Layered Histogram with Mean Line

Show a histogram with a vertical line marking the mean value.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Histogram with a mean reference line.",
  "data": {
    "values": [
      {"value": 5}, {"value": 8}, {"value": 12}, {"value": 15},
      {"value": 18}, {"value": 20}, {"value": 22}, {"value": 25},
      {"value": 28}, {"value": 30}, {"value": 33}, {"value": 35},
      {"value": 38}, {"value": 40}, {"value": 42}, {"value": 45}
    ]
  },
  "layer": [
    {
      "mark": "bar",
      "encoding": {
        "x": {"field": "value", "bin": true, "type": "quantitative"},
        "y": {"aggregate": "count", "title": "Frequency"}
      }
    },
    {
      "mark": {"type": "rule", "color": "red", "strokeWidth": 2},
      "transform": [
        {"aggregate": [{"op": "mean", "field": "value", "as": "mean"}]}
      ],
      "encoding": {
        "x": {"field": "mean", "type": "quantitative"}
      }
    }
  ]
}
```
