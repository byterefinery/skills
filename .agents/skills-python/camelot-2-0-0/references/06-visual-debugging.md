# Visual Debugging Reference

Plotting methods, coordinate space conversion, and bbox overlay techniques.

## camelot.plot()

Generate matplotlib visualizations of detected elements. Requires `camelot-py[plot]` (matplotlib).

```python
import camelot

tables = camelot.read_pdf("doc.pdf")
camelot.plot(tables[0], kind="text").show()
```

### Plot Kinds

| Kind | Flavor | Description |
|------|--------|-------------|
| `"text"` | all | All text on the page with coordinates |
| `"grid"` | all | Detected table grid |
| `"contour"` | all | Table boundaries (contours) |
| `"line"` | lattice/hybrid | Detected line segments |
| `"joint"` | lattice/hybrid | Line intersections (joints) |
| `"textedge"` | stream/hybrid | Relevant text edges |

### Saving Plots

```python
# Save to file
camelot.plot(tables[0], kind="text", filename="debug_text.png").show()
camelot.plot(tables[0], kind="grid", filename="debug_grid.png").show()
```

### CLI Plotting

```bash
# Lattice
camelot lattice -plot text doc.pdf
camelot lattice -plot grid doc.pdf
camelot lattice -plot contour doc.pdf
camelot lattice -plot line doc.pdf
camelot lattice -plot joint doc.pdf

# Stream
camelot stream -plot text doc.pdf
camelot stream -plot contour doc.pdf
camelot stream -plot textedge doc.pdf
```

### Interactive Coordinates

The `"text"` plot shows x-y coordinates that update as you hover over the image. Use this to note coordinates for `table_areas` and `columns` parameters.

## Coordinate Space Conversion

### PDF Coordinate Space

- Origin: **bottom-left** corner of the page
- Y axis: increases **upward**
- Units: **points** (1/72 inch)

### Image Coordinate Space

- Origin: **top-left** corner of the image
- Y axis: increases **downward**
- Units: **pixels**

### Converting PDF Coords to Image Coords

```python
import camelot
import cv2

tables = camelot.read_pdf("foo.pdf", flavor="lattice")
table = tables[0]

img = table.get_pdf_image()          # rendered raster (BGR)
image_h, image_w = img.shape[:2]
pdf_w, pdf_h = table.pdf_size

# Scale factors
scale_x = image_w / pdf_w
scale_y = image_h / pdf_h

# Convert PDF bbox to image coordinates
x0, y0, x1, y1 = table._bbox         # PDF coords (origin bottom-left)
top_left = (round(x0 * scale_x), round((pdf_h - y1) * scale_y))
bottom_right = (round(x1 * scale_x), round((pdf_h - y0) * scale_y))

# Draw on image
cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 3)
cv2.imwrite("foo_bbox.jpg", img)
```

Key transformations:
- **Scale**: PDF points → image pixels via `image_dim / pdf_dim`
- **Flip Y**: `image_y = (pdf_h - pdf_y) * scale_y`

### Converting Image Coords to PDF Coords

When you have table coordinates from an image-based detector and need to pass them to `table_areas`:

```python
import camelot

# Box from image detector: (left, top, right, bottom) in pixels
# on a page rendered at `dpi`
x0_img, y0_img, x1_img, y1_img = detected_box
dpi = 200  # whatever you passed to your renderer

# Image px -> PDF points
s = 72.0 / dpi
pdf_x0, pdf_x1 = x0_img * s, x1_img * s

# Flip y: image top-left -> PDF bottom-left
page_h_pts = image_height_px * s
pdf_top = page_h_pts - y0_img * s       # image top -> larger PDF y
pdf_bottom = page_h_pts - y1_img * s    # image bot -> smaller PDF y

# table_areas format: "x1,y1,x2,y2" = top-left, bottom-right (PDF space)
area = f"{pdf_x0},{pdf_top},{pdf_x1},{pdf_bottom}"
tables = camelot.read_pdf("doc.pdf", flavor="lattice", table_areas=[area])
```

**Important**: Use the DPI of **your own render**, not Camelot's internal 300 DPI. If you rasterised with `pdf2image` at `dpi=D`, the scale is `72 / D`.

### Converting from Camelot's Own Image

If your detector ran on an image Camelot produced (rather than your own render):

```python
# Use table.pdf_size and the rendered image size
img = table.get_pdf_image()
image_h, image_w = img.shape[:2]
pdf_w, pdf_h = table.pdf_size

scale_x = image_w / pdf_w
scale_y = image_h / pdf_h

# Image coord -> PDF coord
pdf_x = image_x / scale_x
pdf_y = pdf_h - (image_y / scale_y)
```

## Debugging Workflow

1. **Run extraction** with default settings
2. **Check `parsing_report`** — low accuracy or high whitespace indicates issues
3. **Plot `"text"`** to see text positions and note coordinates
4. **Plot `"grid"` or `"contour"`** to check if table boundaries are correct
5. **Plot `"line"`** (lattice) to check if lines are detected
6. **Plot `"joint"`** (lattice) to check line intersections
7. **Plot `"textedge"`** (stream) to check text edge detection
8. **Tune parameters** based on visual feedback:
   - Lines not detected? Try `engine="combined"` or increase `line_scale`
   - Table area wrong? Use `table_areas` with coordinates from text plot
   - Columns wrong? Use `columns` with x-coordinates from text plot
   - Rows merged? Adjust `row_tol`
   - Gaps in lines? Use `iterations` + `erode_iterations`
