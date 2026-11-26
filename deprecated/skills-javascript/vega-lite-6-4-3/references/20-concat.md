# Concatenated Specs

Concatenation composes independent specs side-by-side or stacked vertically. Unlike faceting, each concatenated spec can have completely different data, marks, and encodings. Use `hconcat` for horizontal layout, `vconcat` for vertical, and `concat` for a grid.

## Horizontal Concatenation (hconcat)

Place two independent charts side by side using `hconcat`.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Two charts side by side using hconcat.",
  "hconcat": [
    {
      "data": {
        "values": [
          {"a": "A", "b": 28}, {"a": "B", "b": 55}, {"a": "C", "b": 43}
        ]
      },
      "mark": "bar",
      "encoding": {
        "x": {"field": "a", "type": "nominal"},
        "y": {"field": "b", "type": "quantitative"}
      }
    },
    {
      "data": {
        "values": [
          {"month": 1, "value": 20}, {"month": 2, "value": 35},
          {"month": 3, "value": 42}, {"month": 4, "value": 38}
        ]
      },
      "mark": "line",
      "encoding": {
        "x": {"field": "month", "type": "ordinal"},
        "y": {"field": "value", "type": "quantitative"}
      }
    }
  ]
}
```

## Vertical Concatenation (vconcat)

Stack charts vertically using `vconcat`. Each spec is independent.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Two charts stacked vertically using vconcat.",
  "vconcat": [
    {
      "data": {
        "values": [
          {"category": "A", "value": 40},
          {"category": "B", "value": 25},
          {"category": "C", "value": 15},
          {"category": "D", "value": 20}
        ]
      },
      "mark": "arc",
      "encoding": {
        "theta": {"field": "value", "type": "quantitative"},
        "color": {"field": "category", "type": "nominal"}
      }
    },
    {
      "data": {
        "values": [
          {"x": 10, "y": 28}, {"x": 20, "y": 45},
          {"x": 30, "y": 39}, {"x": 40, "y": 61}
        ]
      },
      "mark": "circle",
      "encoding": {
        "x": {"field": "x", "type": "quantitative"},
        "y": {"field": "y", "type": "quantitative"}
      }
    }
  ]
}
```

## Nested Concatenation

Nest `hconcat` and `vconcat` to create complex grid layouts.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Nested concatenation creating a 2x2 grid.",
  "vconcat": [
    {
      "hconcat": [
        {
          "data": {"values": [{"a": "X", "b": 30}, {"a": "Y", "b": 50}]},
          "mark": "bar",
          "encoding": {
            "x": {"field": "a", "type": "nominal"},
            "y": {"field": "b", "type": "quantitative"}
          }
        },
        {
          "data": {"values": [{"x": 1, "y": 5}, {"x": 2, "y": 10}, {"x": 3, "y": 8}]},
          "mark": "line",
          "encoding": {
            "x": {"field": "x", "type": "quantitative"},
            "y": {"field": "y", "type": "quantitative"}
          }
        }
      ]
    },
    {
      "hconcat": [
        {
          "data": {"values": [{"cat": "A", "val": 20}, {"cat": "B", "val": 40}]},
          "mark": "area",
          "encoding": {
            "x": {"field": "cat", "type": "nominal"},
            "y": {"field": "val", "type": "quantitative"}
          }
        },
        {
          "data": {"values": [{"x": 5, "y": 15}, {"x": 10, "y": 25}, {"x": 15, "y": 20}]},
          "mark": "circle",
          "encoding": {
            "x": {"field": "x", "type": "quantitative"},
            "y": {"field": "y", "type": "quantitative"}
          }
        }
      ]
    }
  ]
}
```

## Concat with Shared Data Reference

Use a named data source and reference it across concatenated specs.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Concatenated specs sharing a data source.",
  "data": {
    "name": "shared",
    "values": [
      {"month": "Jan", "value": 20}, {"month": "Feb", "value": 35},
      {"month": "Mar", "value": 42}, {"month": "Apr", "value": 38}
    ]
  },
  "hconcat": [
    {
      "mark": "bar",
      "encoding": {
        "x": {"field": "month", "type": "ordinal"},
        "y": {"field": "value", "type": "quantitative"}
      }
    },
    {
      "mark": "line",
      "encoding": {
        "x": {"field": "month", "type": "ordinal"},
        "y": {"field": "value", "type": "quantitative"}
      }
    }
  ]
}
```
