# Rule Marks

Rule marks render data as straight lines (vertical, horizontal, or diagonal). They are used for annotations, reference lines, and range indicators.

## Vertical Reference Lines

Use `rule` with y encoding to draw vertical lines spanning the full height of the chart. Set `y` to an aggregated value for reference lines at specific positions.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Vertical reference lines at specific positions.",
  "data": {
    "values": [
      {"x": 10, "y": 20}, {"x": 15, "y": 35}, {"x": 20, "y": 28},
      {"x": 25, "y": 42}, {"x": 30, "y": 38}, {"x": 35, "y": 50}
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
      "mark": {"type": "rule", "color": "red", "strokeDash": [4, 4]},
      "encoding": {
        "x": {"aggregate": "mean", "field": "x", "type": "quantitative"}
      }
    }
  ]
}
```

## Horizontal Range Lines

Map quantitative fields to both x and y, with x2/y2 for the end points to draw diagonal rules.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Diagonal rule marks connecting two points.",
  "data": {
    "values": [
      {"x1": 5, "y1": 10, "x2": 15, "y2": 40},
      {"x1": 10, "y1": 20, "x2": 25, "y2": 35},
      {"x1": 20, "y1": 15, "x2": 30, "y2": 45}
    ]
  },
  "mark": "rule",
  "encoding": {
    "x": {"field": "x1", "type": "quantitative"},
    "x2": {"field": "x2"},
    "y": {"field": "y1", "type": "quantitative"},
    "y2": {"field": "y2"}
  }
}
```

## Annotating a Bar Chart with Rules

Layer rules on top of bars to show targets or thresholds.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Bar chart with a horizontal threshold rule.",
  "data": {
    "values": [
      {"category": "A", "value": 28}, {"category": "B", "value": 55},
      {"category": "C", "value": 43}, {"category": "D", "value": 91},
      {"category": "E", "value": 30}
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
      "mark": {"type": "rule", "color": "red", "strokeWidth": 2},
      "encoding": {
        "y": {"value": 50}
      }
    }
  ]
}
```

## Slope Lines Between Two Points

Use `rule` to draw lines connecting before/after values for each category.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Slope lines using rule marks.",
  "data": {
    "values": [
      {"name": "A", "before": 10, "after": 30},
      {"name": "B", "before": 25, "after": 20},
      {"name": "C", "before": 40, "after": 55}
    ]
  },
  "transform": [
    {"fold": ["before", "after"], "as": ["metric", "value"]}
  ],
  "mark": "rule",
  "encoding": {
    "x": {"field": "metric", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"},
    "color": {"field": "name", "type": "nominal"},
    "detail": {"field": "name", "type": "nominal"}
  }
}
```
