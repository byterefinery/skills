# KIE Predictor — Key Information Extraction

The KIE (Key Information Extraction) predictor extends OCR with multi-class detection. Instead of detecting all text uniformly, it classifies detected regions into semantic categories (e.g., "date", "address", "amount").

## API

```python
from doctr.models import kie_predictor

model = kie_predictor(
    det_arch="db_resnet50",
    reco_arch="crnn_vgg16_bn",
    pretrained=True,
    assume_straight_pages=True,
    preserve_aspect_ratio=True,
    symmetric_pad=True,
    detect_orientation=False,
    straighten_pages=False,
    detect_language=False,
)

from doctr.io import DocumentFile
doc = DocumentFile.from_pdf("invoice.pdf")
result = model(doc)
```

Parameters are the same as `ocr_predictor()`. The difference is in the output structure.

## Output Structure

KIE returns `KIEDocument` with `KIEPage` elements. Instead of the standard block → line → word hierarchy, each page has a `predictions` dict keyed by class name:

```python
for page in result.pages:
    # page is a KIEPage
    for class_name, predictions in page.predictions.items():
        print(f"Class: {class_name}")
        for pred in predictions:
            print(f"  '{pred.value}' conf={pred.confidence:.2f} geo={pred.geometry}")
```

Each prediction is a `Prediction` element (extends `Word`) with:
- **`value`** — recognized text
- **`confidence`** — recognition confidence
- **`geometry`** — bounding box
- **`objectness_score`** — detection confidence
- **`crop_orientation`** — rotation info

## KIEPage

- **`predictions`** — dict mapping class names to lists of `Prediction` objects
- **`page_idx`** — page index
- **`dimensions`** — page size (height, width)
- **`orientation`** — rotation info dict
- **`language`** — language detection dict
- **`.export_as_xml()`** — hOCR export (straight boxes only)
- **`.synthesize()`** — reconstructed page image
- **`.show()`** — visualization

## Use Cases

- Invoice processing (extract dates, amounts, vendor names)
- Form parsing (field labels and values)
- Receipt OCR (item names, prices, totals)
- Document classification by detected entities

## Gotchas

- **`KIEPage` replaces `Page`** — it has `predictions` dict instead of `blocks`. Do not iterate `page.blocks` on KIE results.
- **Class names are model-dependent** — the detected classes depend on what the detection model was trained on. Pretrained models use their own class taxonomy.
- **Custom KIE requires custom training** — to detect your own classes (e.g., "patient_name", "diagnosis"), train a custom detection model with multi-class annotations.
- **Same architectures as OCR** — KIE uses the same detection and recognition model families. Architecture selection follows the same guidelines.
- **`export_as_xml()` works on KIEPage** — but only with straight bounding boxes.
