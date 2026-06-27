# Repeat Specs

Repeat specs systematically vary a dimension (field, mark, encoding) across multiple panels. They are more concise than `concat` when the same spec structure applies to multiple fields. Use `repeat` with an array or `{row, column}` object, and reference repeated dimensions with `{"repeat": "repeat"}` inside the `spec`.

## Column Repeat

Repeat a chart across columns, varying the field used in an encoding. The `repeat` property is an array of field names.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Column-repeat histogram for multiple fields.",
  "repeat": ["a", "b", "c"],
  "columns": 3,
  "spec": {
    "data": {
      "values": [
        {"a": 10, "b": 20, "c": 15}, {"a": 15, "b": 25, "c": 20},
        {"a": 20, "b": 30, "c": 18}, {"a": 25, "b": 35, "c": 22},
        {"a": 30, "b": 40, "c": 25}, {"a": 35, "b": 45, "c": 28}
      ]
    },
    "mark": "bar",
    "encoding": {
      "x": {"field": {"repeat": "repeat"}, "bin": true, "type": "quantitative"},
      "y": {"aggregate": "count", "type": "quantitative"}
    }
  }
}
```

## Row Repeat

Repeat across rows, varying the field in each panel. Use `{row: [...]}` for row-oriented repeat.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Row-repeat line charts for multiple metrics.",
  "repeat": {"row": ["sales", "profit", "orders"]},
  "spec": {
    "data": {
      "values": [
        {"month": 1, "sales": 100, "profit": 20, "orders": 50},
        {"month": 2, "sales": 120, "profit": 25, "orders": 60},
        {"month": 3, "sales": 110, "profit": 22, "orders": 55},
        {"month": 4, "sales": 140, "profit": 30, "orders": 70}
      ]
    },
    "mark": "line",
    "encoding": {
      "x": {"field": "month", "type": "ordinal"},
      "y": {"field": {"repeat": "row"}, "type": "quantitative"}
    }
  }
}
```

## Row and Column Repeat (Grid)

Create a grid of charts by repeating across both rows and columns. Each cell shows a different combination.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Row and column repeat scatter plot matrix.",
  "repeat": {"row": ["x", "y"], "column": ["y", "z"]},
  "spec": {
    "data": {
      "values": [
        {"x": 10, "y": 20, "z": 15}, {"x": 15, "y": 35, "z": 20},
        {"x": 20, "y": 28, "z": 25}, {"x": 25, "y": 42, "z": 18},
        {"x": 30, "y": 38, "z": 30}, {"x": 35, "y": 50, "z": 22}
      ]
    },
    "mark": "circle",
    "encoding": {
      "x": {"field": {"repeat": "column"}, "type": "quantitative"},
      "y": {"field": {"repeat": "row"}, "type": "quantitative"}
    }
  }
}
```

## Repeat with Shared Data and Layers

Combine `repeat` and `layer` to apply the same layered spec across multiple fields. Data can be shared at the top level.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Repeat with layered bar and line marks.",
  "data": {
    "values": [
      {"month": "Jan", "a": 20, "b": 35},
      {"month": "Feb", "a": 30, "b": 45},
      {"month": "Mar", "a": 25, "b": 40},
      {"month": "Apr", "a": 35, "b": 55}
    ]
  },
  "repeat": {"column": ["a", "b"]},
  "spec": {
    "layer": [
      {
        "mark": "bar",
        "encoding": {
          "x": {"field": "month", "type": "ordinal"},
          "y": {"field": {"repeat": "column"}, "type": "quantitative"}
        }
      },
      {
        "mark": {"type": "line", "stroke": "red"},
        "encoding": {
          "x": {"field": "month", "type": "ordinal"},
          "y": {"field": {"repeat": "column"}, "type": "quantitative"}
        }
      }
    ]
  }
}
```
