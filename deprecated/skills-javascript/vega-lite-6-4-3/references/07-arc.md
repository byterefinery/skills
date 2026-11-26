# Arc Marks

Arc marks render data as circular arcs. They are used for pie charts, donut charts, and radial visualizations. Arcs require `theta` encoding for the angle span and optionally `radius` or `innerRadius`/`outerRadius`.

## Pie Chart

The classic pie chart uses `arc` mark with `theta` encoding. Map a quantitative field to `theta` and a nominal field to `color`.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A simple pie chart.",
  "data": {
    "values": [
      {"category": "A", "value": 40},
      {"category": "B", "value": 25},
      {"category": "C", "value": 15},
      {"category": "D", "value": 10},
      {"category": "E", "value": 10}
    ]
  },
  "mark": "arc",
  "encoding": {
    "theta": {"field": "value", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

## Donut Chart

Set `innerRadius` in the mark definition to create a donut (ring) chart.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A donut chart with inner radius.",
  "data": {
    "values": [
      {"category": "Desktop", "value": 55},
      {"category": "Mobile", "value": 30},
      {"category": "Tablet", "value": 15}
    ]
  },
  "mark": {"type": "arc", "innerRadius": 50},
  "encoding": {
    "theta": {"field": "value", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

## Pie Chart with Labels

Layer `arc` and `text` marks to show category labels and values on the pie chart.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A pie chart with labels.",
  "data": {
    "values": [
      {"category": "A", "value": 40},
      {"category": "B", "value": 25},
      {"category": "C", "value": 15},
      {"category": "D", "value": 20}
    ]
  },
  "layer": [
    {
      "mark": "arc",
      "encoding": {
        "theta": {"field": "value", "type": "quantitative"},
        "color": {"field": "category", "type": "nominal"}
      }
    },
    {
      "mark": {"type": "text", "radius": 1.1},
      "encoding": {
        "theta": {"field": "value", "type": "quantitative"},
        "text": {"field": "category", "type": "nominal"}
      },
      "transform": [
        {"calculate": "datum.value / sum(datum.value) * 100", "as": "percent"}
      ]
    }
  ]
}
```

## Radial Histogram

Use `theta` for binning and `radius` for count to create a radial histogram.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A radial histogram using arc marks.",
  "data": {
    "values": [
      {"angle": 10, "value": 5}, {"angle": 25, "value": 8},
      {"angle": 40, "value": 3}, {"angle": 55, "value": 12},
      {"angle": 70, "value": 7}, {"angle": 85, "value": 15},
      {"angle": 100, "value": 6}, {"angle": 115, "value": 10},
      {"angle": 130, "value": 4}, {"angle": 145, "value": 9},
      {"angle": 160, "value": 11}, {"angle": 175, "value": 2}
    ]
  },
  "mark": "arc",
  "encoding": {
    "theta": {"field": "angle", "type": "quantitative"},
    "radius": {"field": "value", "type": "quantitative"},
    "color": {"field": "angle", "type": "quantitative"}
  }
}
```
