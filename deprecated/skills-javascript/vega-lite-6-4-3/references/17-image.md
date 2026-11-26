# Image Marks

The `image` mark renders images at data positions. Images can be positioned using x/y encodings and sized with `width` and `height` properties. Supports inline data URLs or external image sources.

## Simple Image Placement

Place an image at a specific position using `x` and `y` encodings with `url` for the image source.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "An image mark at a data position.",
  "data": {
    "values": [
      {"x": 50, "y": 50, "src": "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=identicon&s=100"}
    ]
  },
  "mark": {"type": "image", "width": 50, "height": 50},
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "url": {"field": "src", "type": "nominal"}
  }
}
```

## Image Scatter Plot

Place multiple images at data positions, using x/y to position and `url` for the image source.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Multiple images at scatter plot positions.",
  "data": {
    "values": [
      {"x": 10, "y": 20, "src": "https://www.gravatar.com/avatar/aaaa?d=identicon&s=50"},
      {"x": 30, "y": 40, "src": "https://www.gravatar.com/avatar/bbbb?d=identicon&s=50"},
      {"x": 50, "y": 60, "src": "https://www.gravatar.com/avatar/cccc?d=identicon&s=50"},
      {"x": 70, "y": 80, "src": "https://www.gravatar.com/avatar/dddd?d=identicon&s=50"}
    ]
  },
  "mark": {"type": "image", "width": 30, "height": 30},
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "url": {"field": "src", "type": "nominal"}
  }
}
```

## Image with Tooltip

Add a `tooltip` encoding to show information on hover.

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Image marks with tooltips.",
  "data": {
    "values": [
      {"x": 20, "y": 30, "label": "Item A", "src": "https://www.gravatar.com/avatar/1111?d=identicon&s=50"},
      {"x": 60, "y": 50, "label": "Item B", "src": "https://www.gravatar.com/avatar/2222?d=identicon&s=50"},
      {"x": 100, "y": 70, "label": "Item C", "src": "https://www.gravatar.com/avatar/3333?d=identicon&s=50"}
    ]
  },
  "mark": {"type": "image", "width": 40, "height": 40},
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "url": {"field": "src", "type": "nominal"},
    "tooltip": {"field": "label", "type": "nominal"}
  }
}
```
