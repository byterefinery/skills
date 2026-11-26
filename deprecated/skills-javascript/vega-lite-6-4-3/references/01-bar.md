# Bar Charts

Bar charts encode quantitative values as the length of rectangular bars. They are the most common chart type and support stacking, grouping, horizontal orientation, and many variations.

## Simple Bar Chart

The basic bar chart maps a nominal field to one axis and a quantitative field to the other.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A simple bar chart with embedded data.",
  "data": {
    "values": [
      {"a": "A", "b": 28}, {"a": "B", "b": 55}, {"a": "C", "b": 43},
      {"a": "D", "b": 91}, {"a": "E", "b": 81}, {"a": "F", "b": 53}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "a", "type": "nominal", "axis": {"labelAngle": 0}},
    "y": {"field": "b", "type": "quantitative"}
  }
}
```

## Stacked Bar Chart

When a nominal field is mapped to `color`, bars are automatically stacked. Use `stack: null` to disable stacking and show overlapping bars, or `stack: "center"` for centered stacking.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A stacked bar chart showing population by age and gender.",
  "data": {
    "values": [
      {"age": "0-9", "gender": "M", "people": 15},
      {"age": "0-9", "gender": "F", "people": 14},
      {"age": "10-19", "gender": "M", "people": 20},
      {"age": "10-19", "gender": "F", "people": 18},
      {"age": "20-29", "gender": "M", "people": 25},
      {"age": "20-29", "gender": "F", "people": 23},
      {"age": "30-39", "gender": "M", "people": 22},
      {"age": "30-39", "gender": "F", "people": 21}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "age", "type": "ordinal"},
    "y": {"field": "people", "type": "quantitative", "title": "Population"},
    "color": {"field": "gender", "type": "nominal", "title": "Gender"}
  }
}
```

## Grouped Bar Chart

Group bars side-by-side using `xOffset` (or `yOffset`) with a nominal field. This avoids stacking and places bars next to each other within each group.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A grouped bar chart with side-by-side bars.",
  "data": {
    "values": [
      {"category": "A", "group": "X", "value": 40},
      {"category": "A", "group": "Y", "value": 30},
      {"category": "B", "group": "X", "value": 55},
      {"category": "B", "group": "Y", "value": 25},
      {"category": "C", "group": "X", "value": 35},
      {"category": "C", "group": "Y", "value": 60}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "category", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"},
    "xOffset": {"field": "group", "type": "nominal"},
    "color": {"field": "group", "type": "nominal"}
  }
}
```

## Horizontal Bar Chart

Swap x and y encodings to create horizontal bars. Useful when category labels are long.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A horizontal bar chart.",
  "data": {
    "values": [
      {"country": "China", "population": 1400},
      {"country": "India", "population": 1380},
      {"country": "US", "population": 331},
      {"country": "Indonesia", "population": 273},
      {"country": "Pakistan", "population": 220}
    ]
  },
  "mark": "bar",
  "encoding": {
    "y": {"field": "country", "type": "nominal", "sort": "-x"},
    "x": {"field": "population", "type": "quantitative", "title": "Population (millions)"},
    "color": {"field": "country", "type": "nominal"}
  }
}
```

## Bar Chart with Aggregation

Use `aggregate` to compute counts, sums, means, etc. directly in the encoding.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Bar chart with count aggregation.",
  "data": {
    "values": [
      {"origin": "USA"}, {"origin": "Japan"}, {"origin": "Europe"},
      {"origin": "USA"}, {"origin": "USA"}, {"origin": "Japan"},
      {"origin": "Europe"}, {"origin": "Europe"}, {"origin": "USA"},
      {"origin": "Japan"}, {"origin": "USA"}, {"origin": "Europe"}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "origin", "type": "nominal"},
    "y": {"aggregate": "count", "title": "Count"}
  }
}
```

## Bar Chart with Binning

Bin quantitative data into histogram-style bars using `bin: true`.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A histogram using bar marks with binning.",
  "data": {
    "values": [
      {"value": 12}, {"value": 15}, {"value": 23}, {"value": 28},
      {"value": 34}, {"value": 37}, {"value": 41}, {"value": 45},
      {"value": 50}, {"value": 53}, {"value": 58}, {"value": 62},
      {"value": 67}, {"value": 71}, {"value": 75}, {"value": 80},
      {"value": 84}, {"value": 88}, {"value": 92}, {"value": 96}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "value", "bin": true, "type": "quantitative"},
    "y": {"aggregate": "count", "title": "Frequency"}
  }
}
```

## Bar Chart with Corner Radius

Round the corners of bars using `cornerRadius` in the mark definition.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Bar chart with rounded corners.",
  "data": {
    "values": [
      {"a": "A", "b": 28}, {"a": "B", "b": 55}, {"a": "C", "b": 43},
      {"a": "D", "b": 91}, {"a": "E", "b": 81}
    ]
  },
  "mark": {"type": "bar", "cornerRadius": 5},
  "encoding": {
    "x": {"field": "a", "type": "nominal"},
    "y": {"field": "b", "type": "quantitative"}
  }
}
```

## Normalized (Percent) Stacked Bar Chart

Use `stack: "normalize"` to show proportions that sum to 100% within each group.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Normalized stacked bar chart showing percentages.",
  "data": {
    "values": [
      {"year": 2020, "category": "A", "value": 30},
      {"year": 2020, "category": "B", "value": 50},
      {"year": 2020, "category": "C", "value": 20},
      {"year": 2021, "category": "A", "value": 40},
      {"year": 2021, "category": "B", "value": 35},
      {"year": 2021, "category": "C", "value": 25}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "year", "type": "ordinal"},
    "y": {
      "field": "value",
      "type": "quantitative",
      "stack": "normalize",
      "scale": {"domain": [0, 1]},
      "axis": {"format": ".0%", "title": "Proportion"}
    },
    "color": {"field": "category", "type": "nominal"}
  }
}
```
