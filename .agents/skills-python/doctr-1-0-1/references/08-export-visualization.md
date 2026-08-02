# Export & Visualization

docTR provides multiple ways to export OCR results and visualize predictions.

## Text Rendering

```python
# Full document as plain text
text = result.render()                    # pages separated by \n\n\n\n

# Per page
text = result.pages[0].render()           # blocks separated by \n\n

# Per block
text = block.render()                     # lines separated by \n

# Per line
text = line.render()                      # words separated by space

# Per word
text = word.render()                      # the text value
```

Customize separators: `page.render(block_break="\n")`, `result.render(page_break="\n---\n")`.

## JSON Export

```python
# Full document as nested dict
json_output = result.export()

# Per page
page_dict = result.pages[0].export()

# Per block
block_dict = block.export()

# Serialize to JSON
import json
with open("output.json", "w") as f:
    json.dump(result.export(), f, indent=2)

# Reconstruct from dict
from doctr.io.elements import Document
restored = Document.from_dict(json_output)
```

The exported dict is fully JSON-serializable (no numpy arrays in geometry — they are converted to lists). Page images are excluded from export.

## hOCR XML Export

```python
# Per document
xml_results = result.export_as_xml()
for xml_bytes, tree in xml_results:
    with open("page.hocr", "wb") as f:
        f.write(xml_bytes)

# Per page
xml_bytes, tree = result.pages[0].export_as_xml()
```

Follows the [hOCR 1.2 specification](https://github.com/kba/hocr-spec/blob/master/1.2/spec.md). Compatible with OCR readers and PDF/A conversion tools.

## Visualization

```python
# Interactive visualization
result.show()
result.pages[0].show()

# Non-interactive
result.pages[0].show(interactive=False)

# With aspect ratio preservation
result.pages[0].show(preserve_aspect_ratio=True)
```

Requires `matplotlib` and `mplcursors` (`pip install matplotlib mplcursors`).

## Page Synthesis

Reconstruct a synthetic page image from OCR predictions (useful for verifying output quality):

```python
import matplotlib.pyplot as plt

# Synthesize all pages
synthetic_pages = result.synthesize()

# Display first page
plt.imshow(synthetic_pages[0])
plt.axis("off")
plt.show()

# Per page
synthetic = result.pages[0].synthesize()
plt.imshow(synthetic)
plt.axis("off")
plt.show()
```

Returns numpy arrays with the OCR text rendered onto blank pages at the detected positions.

## Export Comparison

| Method | Output | Use Case |
|--------|--------|----------|
| `.render()` | Plain text | Quick reading, text extraction |
| `.export()` | Nested dict | JSON serialization, programmatic access |
| `.export_as_xml()` | hOCR XML | PDF/A, OCR toolchains |
| `.show()` | Matplotlib plot | Interactive inspection |
| `.synthesize()` | numpy image | Quality verification |

## Gotchas

- **`.export_as_xml()` requires straight boxes** — raises `TypeError` if any bounding box is rotated (numpy array). Use `assume_straight_pages=True` or `export_as_straight_boxes=True`.
- **`.show()` needs extra packages** — `matplotlib` and `mplcursors` are not installed by default.
- **`.export()` excludes page images** — the `Page.page` numpy array is not included in the exported dict. This keeps exports lightweight.
- **`.synthesize()` returns blank-background images** — the synthesized page has text rendered on a blank background, not the original image.
- **`.render()` separators are configurable** — default page break is `\n\n\n\n`, block break is `\n\n`, line break is `\n`, word separator is space.
- **`from_dict()` loses images** — reconstructed documents have no page images. Geometry and text are preserved.
- **hOCR XML is per-page** — `Document.export_as_xml()` returns a list; `Page.export_as_xml()` returns a single tuple.
- **JSON serialization needs `default` handler for numpy** — if you have numpy values in the dict, use `json.dumps(data, default=str)` or ensure `.export()` has converted them (it does for geometry).
