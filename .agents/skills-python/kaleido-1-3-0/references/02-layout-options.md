# Layout Options — Kaleido 1.3.0

## LayoutOpts dictionary

The `opts` parameter accepts a dictionary with these optional keys:

```python
opts = {
    "format": "png",    # output format
    "scale": 2,         # resolution multiplier
    "width": 800,       # pixel width
    "height": 600,      # pixel height
}
```

## Resolution calculation

The final pixel dimensions are:

```
final_width  = width  * scale
final_height = height * scale
```

Where `width` and `height` follow this priority chain:

1. `opts["width"]` / `opts["height"]` — explicit override
2. `fig.layout.width` / `fig.layout.height` — figure's own layout
3. `fig.layout.template.layout.width` / `.height` — template defaults
4. `700` / `500` — hardcoded defaults

### Examples

```python
# 1400x1000 pixels (700x500 * scale 2)
opts = {"scale": 2}

# 1600x1200 pixels (800x600 * scale 2)
opts = {"width": 800, "height": 600, "scale": 2}

# 800x500 pixels (width=800 from opts, height=500 default)
opts = {"width": 800}
```

## Format coercion

- `format="jpg"` is internally normalized to `"jpeg"`
- Path extensions are recognized: `.png`, `.jpg`, `.jpeg`, `.svg`, `.pdf`, `.webp`, `.json`
- If no format is specified and no path extension, defaults to `"png"`
- Invalid formats raise `ValueError`

## Format-specific behavior

### PNG (default)
- Lossless raster format
- Best for most use cases
- Supports transparency (alpha channel)

### JPG / JPEG
- Lossy compression, smaller file sizes
- No transparency support
- Use for photos or when file size matters more than quality

### SVG
- Vector format — infinite scalability
- No `scale` option has visual effect (vectors scale natively)
- Larger file sizes for complex figures
- Best for publication-quality graphics with simple geometry

### PDF
- Vector format in a document wrapper
- Suitable for embedding in documents
- Like SVG, `scale` has minimal visual effect

### WebP
- Modern compressed format
- Supports both lossy and lossless
- Good balance of quality and file size
- Not universally supported in all image viewers

### JSON
- Not an image — exports the Plotly figure as JSON
- Useful for debugging or transferring figure definitions
- `scale`, `width`, `height` are irrelevant

## Width/height interaction with figure layout

When `opts` specifies `width`/`height`, they **override** the figure's `layout.width`/`layout.height`. This is useful when you want a different render size than the display size:

```python
import plotly.graph_objects as go
import kaleido

# Figure displays at 400x300 but renders at 1600x1200
fig = go.Figure(go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))
fig.update_layout(width=400, height=300)

kaleido.write_fig_sync(
    fig,
    path="high-res.png",
    opts={"width": 1600, "height": 1200},
)
```

## Scale vs explicit dimensions

Prefer `scale` over explicit `width`/`height` when you want to maintain the figure's aspect ratio:

```python
# Maintains aspect ratio, doubles resolution
opts = {"scale": 2}

# May change aspect ratio if width/height don't match layout proportions
opts = {"width": 800, "height": 600}
```

## Performance considerations

- Higher `scale` values increase render time proportionally
- SVG and PDF rendering is generally slower than PNG
- Very large dimensions (e.g., `width=4000, height=3000, scale=3`) may hit Chrome's canvas limits
- For extremely large outputs, consider rendering at a lower scale and upscaling externally
