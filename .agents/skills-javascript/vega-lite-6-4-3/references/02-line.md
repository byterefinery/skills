# Line Charts

Line charts connect data points with straight line segments, ideal for showing trends over time or ordered sequences.

## Simple Line Chart

Map a temporal field to x and a quantitative field to y. The `line` mark connects points in order of the x-axis by default.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A simple line chart showing values over time.",
  "data": {
    "values": [
      {"month": "Jan", "value": 20}, {"month": "Feb", "value": 35},
      {"month": "Mar", "value": 42}, {"month": "Apr", "value": 38},
      {"month": "May", "value": 55}, {"month": "Jun", "value": 61},
      {"month": "Jul", "value": 58}, {"month": "Aug", "value": 65}
    ]
  },
  "mark": "line",
  "encoding": {
    "x": {"field": "month", "type": "ordinal"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```

## Multi-Series Line Chart

Add a `color` encoding with a nominal field to draw separate lines for each group. Use `detail` to ensure correct ordering within each line.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Multi-series line chart with multiple lines.",
  "data": {
    "values": [
      {"month": 1, "product": "A", "sales": 100},
      {"month": 2, "product": "A", "sales": 120},
      {"month": 3, "product": "A", "sales": 115},
      {"month": 4, "product": "A", "sales": 140},
      {"month": 5, "product": "A", "sales": 160},
      {"month": 1, "product": "B", "sales": 80},
      {"month": 2, "product": "B", "sales": 95},
      {"month": 3, "product": "B", "sales": 110},
      {"month": 4, "product": "B", "sales": 105},
      {"month": 5, "product": "B", "sales": 130}
    ]
  },
  "mark": "line",
  "encoding": {
    "x": {"field": "month", "type": "ordinal", "title": "Month"},
    "y": {"field": "sales", "type": "quantitative", "title": "Sales"},
    "color": {"field": "product", "type": "nominal", "title": "Product"}
  }
}
```

## Line with Points

Combine `line` and `point` marks using a mark definition with `point: true`, or layer them.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Line chart with point markers at each data point.",
  "data": {
    "values": [
      {"month": 1, "value": 20}, {"month": 2, "value": 35},
      {"month": 3, "value": 42}, {"month": 4, "value": 38},
      {"month": 5, "value": 55}, {"month": 6, "value": 61}
    ]
  },
  "mark": {"type": "line", "point": true},
  "encoding": {
    "x": {"field": "month", "type": "ordinal"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```

## Line Chart with Temporal Data

Use `temporal` type for date fields. Vega-Lite automatically handles date parsing and formatting.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Line chart with temporal x-axis.",
  "data": {
    "values": [
      {"date": "2023-01-01", "value": 10},
      {"date": "2023-02-01", "value": 25},
      {"date": "2023-03-01", "value": 40},
      {"date": "2023-04-01", "value": 35},
      {"date": "2023-05-01", "value": 50},
      {"date": "2023-06-01", "value": 65}
    ]
  },
  "mark": "line",
  "encoding": {
    "x": {"field": "date", "type": "temporal", "title": "Date"},
    "y": {"field": "value", "type": "quantitative", "title": "Value"}
  }
}
```

## Line with Time Unit

Extract year-month from dates using `timeUnit` for aggregated temporal views.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Line chart with year-month time unit aggregation.",
  "data": {
    "values": [
      {"date": "2023-01-15", "value": 10}, {"date": "2023-01-20", "value": 12},
      {"date": "2023-02-10", "value": 18}, {"date": "2023-02-25", "value": 20},
      {"date": "2023-03-05", "value": 25}, {"date": "2023-03-18", "value": 30}
    ]
  },
  "mark": "line",
  "encoding": {
    "x": {"timeUnit": "yearmonth", "field": "date", "type": "temporal"},
    "y": {"aggregate": "mean", "field": "value", "type": "quantitative"}
  }
}
```

## Dashed Line Style

Customize the line appearance using `strokeDash` in the mark definition.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Line chart with dashed stroke style.",
  "data": {
    "values": [
      {"x": 1, "y": 20}, {"x": 2, "y": 35}, {"x": 3, "y": 42},
      {"x": 4, "y": 38}, {"x": 5, "y": 55}
    ]
  },
  "mark": {"type": "line", "strokeDash": [6, 4], "strokeWidth": 2},
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"}
  }
}
```

## Slope Chart

A slope chart compares two points (e.g., before/after) across categories. Use `detail` to connect the right pairs.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A slope chart comparing before and after values.",
  "data": {
    "values": [
      {"name": "A", "before": 10, "after": 30},
      {"name": "B", "before": 25, "after": 20},
      {"name": "C", "before": 40, "after": 55},
      {"name": "D", "before": 15, "after": 35}
    ]
  },
  "mark": "line",
  "encoding": {
    "x": {"field": "metric", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"},
    "color": {"field": "name", "type": "nominal"},
    "detail": {"field": "name", "type": "nominal"}
  },
  "transform": [
    {"fold": ["before", "after"], "as": ["metric", "value"]}
  ]
}
```
