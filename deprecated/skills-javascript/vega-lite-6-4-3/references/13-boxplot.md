# Boxplot

The `boxplot` mark is a composite mark that renders a box-and-whisker plot. It automatically computes quartiles, median, and outliers. It can be used as a shorthand for layered specs with multiple primitive marks.

## Simple Vertical Boxplot

Map a nominal field to x and a quantitative field to y. Vega-Lite computes the statistics automatically.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A simple vertical boxplot.",
  "data": {
    "values": [
      {"group": "A", "value": 10}, {"group": "A", "value": 12},
      {"group": "A", "value": 15}, {"group": "A", "value": 18},
      {"group": "A", "value": 20}, {"group": "A", "value": 22},
      {"group": "A", "value": 45},
      {"group": "B", "value": 25}, {"group": "B", "value": 28},
      {"group": "B", "value": 30}, {"group": "B", "value": 32},
      {"group": "B", "value": 35}, {"group": "B", "value": 38},
      {"group": "B", "value": 60},
      {"group": "C", "value": 40}, {"group": "C", "value": 42},
      {"group": "C", "value": 45}, {"group": "C", "value": 48},
      {"group": "C", "value": 50}, {"group": "C", "value": 52},
      {"group": "C", "value": 55}
    ]
  },
  "mark": "boxplot",
  "encoding": {
    "x": {"field": "group", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```

## Horizontal Boxplot

Swap x and y encodings for a horizontal boxplot orientation.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A horizontal boxplot.",
  "data": {
    "values": [
      {"group": "X", "value": 10}, {"group": "X", "value": 15},
      {"group": "X", "value": 20}, {"group": "X", "value": 25},
      {"group": "X", "value": 30},
      {"group": "Y", "value": 40}, {"group": "Y", "value": 45},
      {"group": "Y", "value": 50}, {"group": "Y", "value": 55},
      {"group": "Y", "value": 60},
      {"group": "Z", "value": 70}, {"group": "Z", "value": 75},
      {"group": "Z", "value": 80}, {"group": "Z", "value": 85},
      {"group": "Z", "value": 90}
    ]
  },
  "mark": "boxplot",
  "encoding": {
    "y": {"field": "group", "type": "nominal"},
    "x": {"field": "value", "type": "quantitative"}
  }
}
```

## Boxplot with Color

Add a `color` encoding to distinguish boxplots by a second nominal dimension.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Boxplot with color encoding.",
  "data": {
    "values": [
      {"category": "A", "sub": "1", "value": 10},
      {"category": "A", "sub": "1", "value": 15},
      {"category": "A", "sub": "1", "value": 20},
      {"category": "A", "sub": "1", "value": 25},
      {"category": "A", "sub": "2", "value": 30},
      {"category": "A", "sub": "2", "value": 35},
      {"category": "A", "sub": "2", "value": 40},
      {"category": "A", "sub": "2", "value": 45},
      {"category": "B", "sub": "1", "value": 50},
      {"category": "B", "sub": "1", "value": 55},
      {"category": "B", "sub": "1", "value": 60},
      {"category": "B", "sub": "1", "value": 65},
      {"category": "B", "sub": "2", "value": 70},
      {"category": "B", "sub": "2", "value": 75},
      {"category": "B", "sub": "2", "value": 80},
      {"category": "B", "sub": "2", "value": 85}
    ]
  },
  "mark": "boxplot",
  "encoding": {
    "x": {"field": "category", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"},
    "color": {"field": "sub", "type": "nominal"},
    "xOffset": {"field": "sub", "type": "nominal"}
  }
}
```

## Boxplot with Custom Extent

Control whisker extent using the `extent` property in the mark definition. Options include `"min-max"`, `"iqr"`, or a numeric value.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Boxplot with min-max extent.",
  "data": {
    "values": [
      {"group": "A", "value": 5}, {"group": "A", "value": 10},
      {"group": "A", "value": 15}, {"group": "A", "value": 20},
      {"group": "A", "value": 25}, {"group": "A", "value": 50},
      {"group": "B", "value": 30}, {"group": "B", "value": 35},
      {"group": "B", "value": 40}, {"group": "B", "value": 45},
      {"group": "B", "value": 50}, {"group": "B", "value": 80}
    ]
  },
  "mark": {"type": "boxplot", "extent": "min-max"},
  "encoding": {
    "x": {"field": "group", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```
