# Trail Marks

Trail marks connect data points like `line` but with variable width. The width is determined by a quantitative encoding on `size`, making trails ideal for showing magnitude alongside trends.

## Simple Trail Chart

Map a quantitative field to x, another to y, and use `size` for variable width.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A trail chart with variable width.",
  "data": {
    "values": [
      {"x": 1, "y": 20, "width": 2}, {"x": 2, "y": 35, "width": 4},
      {"x": 3, "y": 42, "width": 3}, {"x": 4, "y": 38, "width": 5},
      {"x": 5, "y": 55, "width": 6}, {"x": 6, "y": 61, "width": 4},
      {"x": 7, "y": 58, "width": 3}, {"x": 8, "y": 65, "width": 7}
    ]
  },
  "mark": "trail",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "size": {"field": "width", "type": "quantitative"}
  }
}
```

## Comet Chart

A comet chart uses `trail` to show a time series where the trail width represents volume or intensity.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A comet chart showing trend with variable width.",
  "data": {
    "values": [
      {"month": 1, "value": 20, "volume": 5},
      {"month": 2, "value": 35, "volume": 8},
      {"month": 3, "value": 42, "volume": 6},
      {"month": 4, "value": 38, "volume": 10},
      {"month": 5, "value": 55, "volume": 12},
      {"month": 6, "value": 61, "volume": 9},
      {"month": 7, "value": 58, "volume": 7},
      {"month": 8, "value": 65, "volume": 15}
    ]
  },
  "mark": "trail",
  "encoding": {
    "x": {"field": "month", "type": "ordinal"},
    "y": {"field": "value", "type": "quantitative"},
    "size": {"field": "volume", "type": "quantitative"},
    "color": {"field": "volume", "type": "quantitative"}
  }
}
```

## Multi-Series Trail

Add a `color` encoding with a nominal field to draw separate trails for each group.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Multi-series trail chart.",
  "data": {
    "values": [
      {"x": 1, "y": 10, "group": "A", "w": 2},
      {"x": 2, "y": 20, "group": "A", "w": 3},
      {"x": 3, "y": 25, "group": "A", "w": 4},
      {"x": 4, "y": 30, "group": "A", "w": 5},
      {"x": 1, "y": 40, "group": "B", "w": 3},
      {"x": 2, "y": 45, "group": "B", "w": 4},
      {"x": 3, "y": 50, "group": "B", "w": 6},
      {"x": 4, "y": 55, "group": "B", "w": 7}
    ]
  },
  "mark": "trail",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "size": {"field": "w", "type": "quantitative"},
    "color": {"field": "group", "type": "nominal"}
  }
}
```
