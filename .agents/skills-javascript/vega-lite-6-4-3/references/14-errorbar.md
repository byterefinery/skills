# Errorbar

The `errorbar` mark is a composite mark that renders error bars (vertical or horizontal lines with caps). It computes error ranges automatically from raw data using aggregate operations like confidence intervals (`ci`), standard deviation (`stdev`), or interquartile range (`iqr`). Typically used within layer specs.

## Vertical Error Bars (Auto-computed)

Use `errorbar` in a layer spec. Vega-Lite computes the error range automatically from the raw data.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Vertical error bars computed from raw data.",
  "data": {
    "values": [
      {"category": "A", "value": 10}, {"category": "A", "value": 15},
      {"category": "A", "value": 20}, {"category": "A", "value": 25},
      {"category": "A", "value": 30},
      {"category": "B", "value": 30}, {"category": "B", "value": 35},
      {"category": "B", "value": 40}, {"category": "B", "value": 45},
      {"category": "B", "value": 50},
      {"category": "C", "value": 50}, {"category": "C", "value": 55},
      {"category": "C", "value": 60}, {"category": "C", "value": 65},
      {"category": "C", "value": 70}
    ]
  },
  "mark": "errorbar",
  "encoding": {
    "x": {"field": "category", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```

## Error Bars with Points

Layer `point` and `errorbar` marks to show both the mean point and its confidence interval.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Points with error bars.",
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
  "layer": [
    {
      "mark": "errorbar",
      "encoding": {
        "x": {"field": "category", "type": "nominal"},
        "y": {"field": "value", "type": "quantitative"}
      }
    },
    {
      "mark": {"type": "point", "filled": true},
      "encoding": {
        "x": {"field": "category", "type": "nominal"},
        "y": {"aggregate": "mean", "field": "value", "type": "quantitative"}
      }
    }
  ]
}
```

## Horizontal Error Bars

Swap to x-axis encoding for horizontal error bars.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Horizontal error bars.",
  "data": {
    "values": [
      {"row": "X", "value": 10}, {"row": "X", "value": 15},
      {"row": "X", "value": 20}, {"row": "X", "value": 25},
      {"row": "Y", "value": 30}, {"row": "Y", "value": 35},
      {"row": "Y", "value": 40}, {"row": "Y", "value": 45},
      {"row": "Z", "value": 50}, {"row": "Z", "value": 55},
      {"row": "Z", "value": 60}, {"row": "Z", "value": 65}
    ]
  },
  "mark": "errorbar",
  "encoding": {
    "y": {"field": "row", "type": "nominal"},
    "x": {"field": "value", "type": "quantitative"}
  }
}
```

## Error Bars with Custom Extent

Control the error range using `extent` in the mark definition. Options include `"ci"` (confidence interval), `"stdev"`, `"iqr"`, or `"stderr"`.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Error bars with standard deviation extent.",
  "data": {
    "values": [
      {"group": "A", "value": 10}, {"group": "A", "value": 15},
      {"group": "A", "value": 20}, {"group": "A", "value": 25},
      {"group": "A", "value": 30},
      {"group": "B", "value": 40}, {"group": "B", "value": 45},
      {"group": "B", "value": 50}, {"group": "B", "value": 55},
      {"group": "B", "value": 60}
    ]
  },
  "mark": {"type": "errorbar", "extent": "stdev"},
  "encoding": {
    "x": {"field": "group", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```
