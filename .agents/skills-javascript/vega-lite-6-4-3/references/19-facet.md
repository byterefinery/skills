# Faceted Specs

Faceting creates small multiples (trellis charts) by splitting data into panels. Use `row` and/or `column` encoding channels in a unit spec, or use the dedicated `facet` and `spec` properties for more control.

## Column Facet

Split a chart into columns by a nominal field using the `column` encoding channel. Each panel shares axes and legends.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Column-faceted bar chart.",
  "data": {
    "values": [
      {"category": "A", "group": "X", "value": 20},
      {"category": "B", "group": "X", "value": 35},
      {"category": "C", "group": "X", "value": 25},
      {"category": "A", "group": "Y", "value": 30},
      {"category": "B", "group": "Y", "value": 45},
      {"category": "C", "group": "Y", "value": 40},
      {"category": "A", "group": "Z", "value": 15},
      {"category": "B", "group": "Z", "value": 28},
      {"category": "C", "group": "Z", "value": 22}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "category", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"},
    "column": {"field": "group", "type": "nominal"}
  }
}
```

## Row Facet

Split into rows using the `row` encoding channel. Useful for comparing trends across categories vertically.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Row-faceted line chart.",
  "data": {
    "values": [
      {"month": 1, "product": "A", "sales": 100},
      {"month": 2, "product": "A", "sales": 120},
      {"month": 3, "product": "A", "sales": 115},
      {"month": 4, "product": "A", "sales": 140},
      {"month": 1, "product": "B", "sales": 80},
      {"month": 2, "product": "B", "sales": 95},
      {"month": 3, "product": "B", "sales": 110},
      {"month": 4, "product": "B", "sales": 105},
      {"month": 1, "product": "C", "sales": 60},
      {"month": 2, "product": "C", "sales": 75},
      {"month": 3, "product": "C", "sales": 85},
      {"month": 4, "product": "C", "sales": 90}
    ]
  },
  "mark": "line",
  "encoding": {
    "x": {"field": "month", "type": "ordinal", "title": "Month"},
    "y": {"field": "sales", "type": "quantitative", "title": "Sales"},
    "row": {"field": "product", "type": "nominal"}
  }
}
```

## Row and Column Facet (Grid)

Use both `row` and `column` to create a grid of panels. Each cell shows a subset of the data.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Row and column faceted scatter plot.",
  "data": {
    "values": [
      {"region": "East", "quarter": "Q1", "x": 10, "y": 20},
      {"region": "East", "quarter": "Q1", "x": 15, "y": 35},
      {"region": "East", "quarter": "Q2", "x": 20, "y": 30},
      {"region": "East", "quarter": "Q2", "x": 25, "y": 45},
      {"region": "West", "quarter": "Q1", "x": 12, "y": 25},
      {"region": "West", "quarter": "Q1", "x": 18, "y": 40},
      {"region": "West", "quarter": "Q2", "x": 22, "y": 35},
      {"region": "West", "quarter": "Q2", "x": 28, "y": 50}
    ]
  },
  "mark": "circle",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "row": {"field": "region", "type": "nominal"},
    "column": {"field": "quarter", "type": "nominal"}
  }
}
```

## Facet with Independent Scales

Use `resolve: {scale: {y: "independent"}}` to give each facet panel its own axis scale.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Faceted chart with independent y-axis scales.",
  "data": {
    "values": [
      {"group": "A", "x": 1, "y": 100}, {"group": "A", "x": 2, "y": 200},
      {"group": "A", "x": 3, "y": 150},
      {"group": "B", "x": 1, "y": 5}, {"group": "B", "x": 2, "y": 8},
      {"group": "B", "x": 3, "y": 6}
    ]
  },
  "mark": "line",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "column": {"field": "group", "type": "nominal"}
  },
  "resolve": {
    "scale": {"y": "independent"}
  }
}
```
