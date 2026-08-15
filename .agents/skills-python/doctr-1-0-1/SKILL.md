---
name: doctr-1-0-1
description: >
  docTR 1.0.1 — open-source OCR toolkit powered by PyTorch for document text
  detection and recognition. Use for OCR on PDFs or images, extracting
  text with bounding-box coords and confidence scores, handling rotated pages,
  detecting page orientation or language, or exporting results as JSON or hOCR XML.
  Two-stage pipeline — text detection (localize words) then recognition (read characters).
  Supports detection architectures (db_resnet34/50, db_mobilenet_v3_large,
  linknet_resnet18/34/50, fast_tiny/small/base) and recognition architectures
  (crnn_vgg16_bn, crnn_mobilenet_v3_small/large, sar_resnet31, master,
  vitstr_small/base, parseq, viptr_tiny). Also provides KIE predictor,
  standalone detection/recognition predictors, and orientation classifiers.
  Triggers on docTR, doctr, python-doctr, OCR, text detection, text recognition,
  document OCR, word bounding boxes, hOCR export, rotated page OCR,
  page orientation, language detection, KIE, ocr_predictor,
  detection_predictor, recognition_predictor, DocumentFile.
license: Apache-2.0
compatibility: >
  Python 3.10–3.12. Requires PyTorch (torch>=2.0,<3.0), torchvision, numpy,
  opencv-python, pypdfium2, scipy, h5py, huggingface-hub, Pillow, shapely, pyclipper.
  Visualization (result.show) needs matplotlib + mplcursors. Web URL input needs
  weasyprint. ONNX export needs onnxruntime. GPU recommended for inference.
metadata:
  tags:
    - python
    - ocr
    - computer-vision
    - pytorch
    - document-processing
    - text-detection
    - text-recognition
---

# doctr 1.0.1

## Overview

docTR is an open-source OCR (Optical Character Recognition) library from Mindee, powered by PyTorch. It uses a two-stage pipeline: **text detection** (localize word bounding boxes) followed by **text recognition** (read characters within each box).

**Core API:**
- **`DocumentFile`** — read documents from PDF (`from_pdf`), images (`from_images`), or web URLs (`from_url`, needs weasyprint). Returns list of numpy arrays (H×W×3 RGB).
- **`ocr_predictor()`** — end-to-end OCR predictor combining detection + recognition. Returns `Document` with nested Page → Block → Line → Word hierarchy.
- **`kie_predictor()`** — key information extraction predictor for multi-class detection (e.g., detect dates, addresses separately).
- **`detection_predictor()`** — standalone text detection (word localization only).
- **`recognition_predictor()`** — standalone text recognition (crop → text string).
- **`crop_orientation_predictor()`** / **`page_orientation_predictor()`** — classify rotation of word crops or full pages.

**Result structure:** `Document` → `Page` → `Block` → `Line` → `Word`. Each element has `geometry` (relative bounding box), `confidence`, and `objectness_score`. Words have `value` (text string). Pages have `orientation` and `language` dicts when detection is enabled.

**Export methods on `Document`/`Page`:**
- `.export()` — nested dict (JSON-serializable)
- `.export_as_xml()` — hOCR XML format
- `.render()` — plain text with block/page breaks
- `.show()` — interactive visualization (needs matplotlib + mplcursors)
- `.synthesize()` — reconstruct synthetic page image from predictions

**Detection architectures:** `db_resnet34`, `db_resnet50`, `db_mobilenet_v3_large`, `linknet_resnet18`, `linknet_resnet34`, `linknet_resnet50`, `fast_tiny`, `fast_small`, `fast_base` (default).

**Recognition architectures:** `crnn_vgg16_bn` (default), `crnn_mobilenet_v3_small`, `crnn_mobilenet_v3_large`, `sar_resnet31`, `master`, `vitstr_small`, `vitstr_base`, `parseq`, `viptr_tiny`.

## Usage

```python
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

# --- Basic OCR ---
model = ocr_predictor(pretrained=True)
doc = DocumentFile.from_pdf("invoice.pdf")
result = model(doc)

# Plain text
text = result.render()

# --- Per-page iteration ---
for page in result.pages:
    print(f"Page {page.page_idx}, dims: {page.dimensions}")
    for block in page.blocks:
        for line in block.lines:
            for word in line.words:
                print(f"  '{word.value}' conf={word.confidence:.2f} geo={word.geometry}")

# --- Export as JSON-friendly dict ---
json_output = result.export()

# --- Export as hOCR XML ---
for xml_bytes, tree in result.export_as_xml():
    with open(f"page_{tree.getroot().attrib}.hocr", "wb") as f:
        f.write(xml_bytes)

# --- Visualize (needs matplotlib, mplcursors) ---
result.show()

# --- Synthesize page from predictions ---
import matplotlib.pyplot as plt
synthetic = result.synthesize()
plt.imshow(synthetic[0]); plt.axis("off"); plt.show()

# --- Custom architectures ---
model = ocr_predictor(
    det_arch="db_resnet50",
    reco_arch="crnn_vgg16_bn",
    pretrained=True,
)

# Lighter model for speed
model = ocr_predictor(
    det_arch="fast_small",
    reco_arch="crnn_mobilenet_v3_small",
    pretrained=True,
)

# --- Handle rotated pages ---
model = ocr_predictor(
    pretrained=True,
    assume_straight_pages=False,     # detect rotated text
    export_as_straight_boxes=True,   # convert back to straight boxes
    detect_orientation=True,          # add page rotation info
    straighten_pages=True,            # re-run detection after rotating
)
result = model(doc)
for page in result.pages:
    print(f"Orientation: {page.orientation}")

# --- Detect language ---
model = ocr_predictor(pretrained=True, detect_language=True)
result = model(doc)
for page in result.pages:
    print(f"Language: {page.language}")

# --- OCR from images ---
doc = DocumentFile.from_images(["page1.jpg", "page2.png"])
result = model(doc)

# --- Standalone detection ---
from doctr.models import detection_predictor
det_model = detection_predictor(arch="db_resnet50", pretrained=True)
doc = DocumentFile.from_images("doc.jpg")
det_result = det_model(doc)

# --- Standalone recognition ---
from doctr.models import recognition_predictor
rec_model = recognition_predictor(arch="crnn_vgg16_bn", pretrained=True)
import numpy as np
crop = (255 * np.random.rand(32, 128, 3)).astype(np.uint8)
rec_result = rec_model([crop])

# --- KIE (Key Information Extraction) ---
from doctr.models import kie_predictor
kie_model = kie_predictor(det_arch="db_resnet50", reco_arch="crnn_vgg16_bn", pretrained=True)
result = kie_model(doc)
for page in result.pages:
    for class_name, predictions in page.predictions.items():
        for pred in predictions:
            print(f"{class_name}: '{pred.value}' conf={pred.confidence:.2f}")

# --- Orientation classification ---
from doctr.models import crop_orientation_predictor, page_orientation_predictor
crop_model = crop_orientation_predictor(pretrained=True)
page_model = page_orientation_predictor(pretrained=True)

# --- Batch size tuning ---
model = ocr_predictor(
    pretrained=True,
    det_bs=4,      # detection batch size (default 2)
    reco_bs=256,   # recognition batch size (default 128)
)

# --- PDF with password ---
doc = DocumentFile.from_pdf("encrypted.pdf", password="secret")
result = model(doc)

# --- PDF rendering scale ---
doc = DocumentFile.from_pdf("doc.pdf", scale=3)  # higher DPI for small text
result = model(doc)
```

## Gotchas

- **`pretrained=True` downloads weights on first use** — models fetch pretrained weights from HuggingFace Hub. First run may be slow. Weights are cached locally afterward.
- **`assume_straight_pages=True` is the default** — it assumes all text is horizontal. For documents with rotated pages or text, set to `False`. This is faster but misses rotated text.
- **`export_as_straight_boxes` only matters when `assume_straight_pages=False`** — when both are False, results include rotated bounding boxes (numpy arrays). Set `export_as_straight_boxes=True` to get axis-aligned boxes even for rotated input.
- **`straighten_pages` re-runs detection** — it estimates page rotation, rotates the page, then runs detection again. Improves accuracy on uniformly-rotated pages but roughly doubles detection time.
- **`detect_orientation` and `detect_language` add latency** — both require extra model passes. Enable only when you need the metadata.
- **`DocumentFile.from_pdf()` returns numpy arrays, not a Document** — it rasterizes PDF pages to images. Pass the result to the predictor to get a `Document` with OCR results.
- **`DocumentFile.from_pdf(scale=2)` is default** — scale 1 = 72 DPI, scale 2 = 144 DPI. For documents with very small text, increase to 3 or 4. Higher scale = slower processing.
- **`DocumentFile.from_url()` needs weasyprint** — install with `pip install weasyprint`. It also needs system dependencies (Pango, etc.) on Linux.
- **`result.show()` needs matplotlib + mplcursors** — not installed by default. Install with `pip install matplotlib mplcursors`.
- **Geometry coordinates are relative** — `word.geometry` uses relative coordinates `(xmin, ymin), (xmax, ymax)` where values are in `[0, 1]` relative to page dimensions. Multiply by `page.dimensions` for pixel coordinates.
- **`fast_*` models are reparameterized by default** — FAST detection models auto-reparameterize for faster inference. This happens in the zoo, no manual step needed.
- **`ocr_predictor` default arch is `fast_base` + `crnn_vgg16_bn`** — not `db_resnet50`. The README example uses `db_resnet50` explicitly; the actual default changed.
- **`Document.render()` joins with `\n\n\n\n` between pages** — use `page.render()` for per-page text. `block.render()` uses `\n\n`, `line.render()` uses space between words.
- **`Page.orientation` is a dict** — `{"value": angle_degrees, "confidence": None}`. Value is `None` if `detect_orientation=False`.
- **`Page.language` is a dict** — `{"value": "en", "confidence": 0.95}`. Value is `None` if `detect_language=False`.
- **`export_as_xml()` only works with straight boxes** — raises `TypeError` if bounding boxes are rotated (numpy arrays). Use `export_as_straight_boxes=True` or `assume_straight_pages=True`.
- **KIE predictor returns `KIEPage` not `Page`** — pages have a `predictions` dict keyed by class name instead of the standard block/line/word hierarchy.
- **`synthesize()` returns list of numpy arrays** — one per page. Use matplotlib or PIL to save/display.
- **GPU usage is automatic** — if CUDA is available and torch was installed with GPU support, models run on GPU. No explicit `.to("cuda")` needed.
- **Large documents: process page by page** — for very large PDFs, consider extracting images first and processing in batches to manage memory.
- **`DocumentFile.from_images()` accepts single file or list** — pass a single path string or a list of paths. Both return a list of numpy arrays.
- **Models are PyTorch-only** — docTR v1.0.1 does not support TensorFlow. ONNX export is available via contrib but requires `onnxruntime`.

## References

- [01-document-file](references/01-document-file.md) — DocumentFile: reading PDFs, images, URLs; rasterization options; password-protected PDFs
- [02-ocr-predictor](references/02-ocr-predictor.md) — ocr_predictor: full API, architecture selection, rotated page handling, orientation and language detection
- [03-detection-models](references/03-detection-models.md) — Detection architectures: DBNet, LinkNet, FAST; detection_predictor API; output format
- [04-recognition-models](references/04-recognition-models.md) — Recognition architectures: CRNN, SAR, MASTER, ViTSTR, PARSeq, VIPTR; recognition_predictor API
- [05-document-structure](references/05-document-structure.md) — Document/Page/Block/Line/Word hierarchy; geometry; confidence; export methods
- [06-kie-predictor](references/06-kie-predictor.md) — KIE predictor: multi-class detection, KIEPage, predictions dict
- [07-orientation-classifiers](references/07-orientation-classifiers.md) — Crop and page orientation predictors; classification architectures
- [08-export-visualization](references/08-export-visualization.md) — Export formats (JSON, hOCR XML), render, show, synthesize
- [09-training](references/09-training.md) — Training custom models; datasets; loss functions; training loops
- [10-performance-tips](references/10-performance-tips.md) — Batch size tuning, GPU usage, model selection, memory management, fast vs accurate tradeoffs
