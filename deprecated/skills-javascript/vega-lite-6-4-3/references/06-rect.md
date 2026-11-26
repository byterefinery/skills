# Rect Marks

Rect (rectangle) marks render data as rectangles. They are the primary mark for heatmaps, 2D binned histograms, and mosaic plots.

## Heatmap

Map two nominal or ordinal fields to x and y, and a quantitative field to `color` to create a heatmap.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A heatmap showing values across two categorical dimensions.",
  "data": {
    "values": [
      {"day": "Mon", "hour": 8, "count": 5}, {"day": "Mon", "hour": 9, "count": 12},
      {"day": "Mon", "hour": 10, "count": 18}, {"day": "Mon", "hour": 11, "count": 15},
      {"day": "Tue", "hour": 8, "count": 7}, {"day": "Tue", "hour": 9, "count": 14},
      {"day": "Tue", "hour": 10, "count": 22}, {"day": "Tue", "hour": 11, "count": 19},
      {"day": "Wed", "hour": 8, "count": 4}, {"day": "Wed", "hour": 9, "count": 10},
      {"day": "Wed", "hour": 10, "count": 16}, {"day": "Wed", "hour": 11, "count": 13}
    ]
  },
  "mark": "rect",
  "encoding": {
    "x": {"field": "hour", "type": "ordinal", "title": "Hour"},
    "y": {"field": "day", "type": "ordinal", "title": "Day"},
    "color": {"field": "count", "type": "quantitative", "title": "Count"}
  }
}
```

## Binned 2D Histogram

Bin both x and y axes and aggregate with `count` to create a density heatmap.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A binned 2D histogram using rect marks.",
  "data": {
    "values": [
      {"x": 5, "y": 10}, {"x": 7, "y": 12}, {"x": 8, "y": 11},
      {"x": 10, "y": 15}, {"x": 12, "y": 14}, {"x": 15, "y": 20},
      {"x": 18, "y": 22}, {"x": 20, "y": 25}, {"x": 22, "y": 23},
      {"x": 25, "y": 30}, {"x": 28, "y": 28}, {"x": 30, "y": 35},
      {"x": 32, "y": 33}, {"x": 35, "y": 40}, {"x": 38, "y": 38},
      {"x": 40, "y": 45}, {"x": 6, "y": 11}, {"x": 9, "y": 13},
      {"x": 11, "y": 16}, {"x": 14, "y": 18}, {"x": 16, "y": 21},
      {"x": 19, "y": 24}, {"x": 21, "y": 26}, {"x": 24, "y": 29},
      {"x": 27, "y": 31}, {"x": 29, "y": 34}, {"x": 31, "y": 36},
      {"x": 34, "y": 39}, {"x": 36, "y": 41}, {"x": 39, "y": 44}
    ]
  },
  "mark": "rect",
  "encoding": {
    "x": {"field": "x", "bin": true, "type": "quantitative"},
    "y": {"field": "y", "bin": true, "type": "quantitative"},
    "color": {"aggregate": "count", "type": "quantitative", "title": "Count"}
  }
}
```

## Heatmap with Text Labels

Layer `rect` and `text` marks to show values inside each cell.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A heatmap with text labels inside each cell.",
  "data": {
    "values": [
      {"row": "A", "col": "X", "value": 10}, {"row": "A", "col": "Y", "value": 25},
      {"row": "A", "col": "Z", "value": 15},
      {"row": "B", "col": "X", "value": 30}, {"row": "B", "col": "Y", "value": 45},
      {"row": "B", "col": "Z", "value": 20},
      {"row": "C", "col": "X", "value": 8}, {"row": "C", "col": "Y", "value": 18},
      {"row": "C", "col": "Z", "value": 12}
    ]
  },
  "layer": [
    {
      "mark": "rect",
      "encoding": {
        "x": {"field": "col", "type": "ordinal"},
        "y": {"field": "row", "type": "ordinal"},
        "color": {"field": "value", "type": "quantitative"}
      }
    },
    {
      "mark": "text",
      "encoding": {
        "x": {"field": "col", "type": "ordinal"},
        "y": {"field": "row", "type": "ordinal"},
        "text": {"field": "value", "type": "quantitative"}
      }
    }
  ]
}
```

## Mosaic Plot

Use `rect` with proportional sizing to create a mosaic plot where area represents magnitude.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A simple mosaic-style rect chart.",
  "data": {
    "values": [
      {"category": "A", "sub": "1", "value": 40},
      {"category": "A", "sub": "2", "value": 20},
      {"category": "B", "sub": "1", "value": 30},
      {"category": "B", "sub": "2", "value": 10}
    ]
  },
  "mark": "rect",
  "encoding": {
    "x": {"field": "category", "type": "nominal"},
    "y": {"field": "sub", "type": "nominal"},
    "color": {"field": "value", "type": "quantitative", "title": "Value"}
  }
}
```
