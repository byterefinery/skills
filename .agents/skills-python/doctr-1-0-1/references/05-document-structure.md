# Document Structure — Result Hierarchy

The OCR result is a nested `Document` object with a hierarchical structure. Each level has geometry, confidence, and export capabilities.

## Hierarchy

```
Document
└── Page (list)
    └── Block (list)
        ├── Line (list)
        │   └── Word (list)
        └── Artefact (list)
```

## Word

Leaf element containing recognized text.

- **`value`** — recognized text string
- **`confidence`** — recognition confidence (0–1)
- **`geometry`** — bounding box `((xmin, ymin), (xmax, ymax))` in relative coords
- **`objectness_score`** — detection confidence (0–1)
- **`crop_orientation`** — dict with word crop rotation info
- **`.render()`** — returns the text value
- **`.export()`** — returns dict of all fields

```python
for page in result.pages:
    for block in page.blocks:
        for line in block.lines:
            for word in line.words:
                print(f"'{word.value}' conf={word.confidence:.2f}")
                print(f"  geometry: {word.geometry}")
```

## Line

Collection of words forming a text line.

- **`words`** — list of `Word` elements
- **`geometry`** — enclosing bounding box (auto-computed from words)
- **`objectness_score`** — mean of word objectness scores
- **`.render()`** — words joined with spaces
- **`.export()`** — dict with geometry, objectness_score, and words

## Block

Collection of lines and artefacts forming a text block.

- **`lines`** — list of `Line` elements
- **`artefacts`** — list of `Artefact` elements (non-textual regions)
- **`geometry`** — enclosing bounding box
- **`objectness_score`** — mean of all word scores in block
- **`.render(line_break="\n")`** — lines joined with newlines

## Artefact

Non-textual element detected by the model (e.g., images, charts, signatures).

- **`type`** — artefact type string
- **`confidence`** — detection confidence
- **`geometry`** — bounding box
- **`.render()`** — returns `"[TYPE]"` placeholder

## Page

Single page with blocks and metadata.

- **`page`** — original image as numpy array (H×W×3, uint8)
- **`page_idx`** — zero-based page index
- **`dimensions`** — `(height, width)` in pixels
- **`orientation`** — `{"value": angle, "confidence": None}` (None if not detected)
- **`language`** — `{"value": "en", "confidence": 0.95}` (None if not detected)
- **`blocks`** — list of `Block` elements
- **`.render(block_break="\n\n")`** — blocks joined with double newlines
- **`.show()`** — interactive visualization (needs matplotlib + mplcursors)
- **`.synthesize()`** — reconstruct page image from predictions
- **`.export_as_xml()`** — hOCR XML export
- **`.export()`** — full dict export (without the image)

## Document

Top-level container for all pages.

- **`pages`** — list of `Page` elements
- **`.render(page_break="\n\n\n\n")`** — all pages as plain text
- **`.show()`** — visualize all pages
- **`.synthesize()`** — list of synthesized page images
- **`.export_as_xml()`** — list of (bytes, ElementTree) per page
- **`.export()`** — nested dict, JSON-serializable

## Geometry Coordinates

All `geometry` fields use **relative coordinates**: `(xmin, ymin), (xmax, ymax)` where each value is in `[0, 1]` relative to page dimensions.

```python
# Convert to pixel coordinates
page_h, page_w = page.dimensions
(xmin, ymin), (xmax, ymax) = word.geometry

pixel_xmin = int(xmin * page_w)
pixel_ymin = int(ymin * page_h)
pixel_xmax = int(xmax * page_w)
pixel_ymax = int(ymax * page_h)
```

For rotated boxes (`assume_straight_pages=False`), geometry is a numpy array with polygon vertices instead of the `(corner, corner)` tuple format.

## Export

```python
# Full JSON-serializable dict
json_output = result.export()

# Per-page
page_dict = result.pages[0].export()

# Reconstruct from dict
from doctr.io.elements import Document, Page
restored = Document.from_dict(json_output)
```

## Gotchas

- **Geometry is relative, not absolute** — always multiply by `page.dimensions` for pixel coordinates.
- **`Page.page` holds the image** — it's a numpy array, not included in `.export()`. This keeps exports lightweight.
- **`orientation` and `language` are dicts** — not simple values. Access via `page.orientation["value"]`.
- **`export_as_xml()` only works with straight boxes** — raises `TypeError` for rotated geometries.
- **`Artefact` is not text** — it represents detected non-textual regions. Its `.render()` returns a placeholder like `"[IMAGE]"`.
- **`from_dict()` reconstructs structure** — but not the page images. Images are lost in export/import.
- **`Page.dimensions` is `(height, width)`** — not `(width, height)`. Order matters for coordinate conversion.
