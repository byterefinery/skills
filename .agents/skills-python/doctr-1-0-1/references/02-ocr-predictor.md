# OCR Predictor — End-to-End OCR

`ocr_predictor()` creates an end-to-end OCR pipeline combining text detection and recognition. It is the primary entry point for most OCR tasks.

## API

```python
from doctr.models import ocr_predictor

model = ocr_predictor(
    det_arch="fast_base",           # detection architecture
    reco_arch="crnn_vgg16_bn",      # recognition architecture
    pretrained=True,                 # load pretrained weights
    pretrained_backbone=True,        # use pretrained backbone
    assume_straight_pages=True,      # assume horizontal text
    preserve_aspect_ratio=True,      # pad to preserve aspect ratio
    symmetric_pad=True,              # pad symmetrically
    export_as_straight_boxes=False,  # output straight vs rotated boxes
    detect_orientation=False,        # detect page rotation
    straighten_pages=False,          # rotate pages before detection
    detect_language=False,           # detect page language
    det_bs=2,                        # detection batch size
    reco_bs=128,                     # recognition batch size
)
```

## Parameters

### Architecture Selection

- **`det_arch`** — detection model. Default: `"fast_base"`. Options:
  - `db_resnet34`, `db_resnet50` — DBNet (accurate, heavier)
  - `db_mobilenet_v3_large` — DBNet with MobileNet (lighter)
  - `linknet_resnet18/34/50` — LinkNet variants
  - `fast_tiny`, `fast_small`, `fast_base` — FAST (fastest, reparameterized)

- **`reco_arch`** — recognition model. Default: `"crnn_vgg16_bn"`. Options:
  - `crnn_vgg16_bn` — CRNN with VGG (default, good accuracy)
  - `crnn_mobilenet_v3_small/large` — CRNN with MobileNet (lighter)
  - `sar_resnet31` — SAR (Self-Attention)
  - `master` — SAR variant
  - `vitstr_small/base` — ViTSTR (Vision Transformer)
  - `parseq` — PARSeq (state-of-the-art accuracy)
  - `viptr_tiny` — VIPTR (Vision-Permutation Transformer)

### Page Handling

- **`assume_straight_pages`** (default `True`) — if True, assumes all text is horizontal. Faster but misses rotated text.
- **`export_as_straight_boxes`** (default `False`) — when `assume_straight_pages=False`, converts rotated boxes to straight axis-aligned boxes in output.
- **`detect_orientation`** (default `False`) — adds page rotation angle to `Page.orientation`. Slight latency cost.
- **`straighten_pages`** (default `False`) — estimates page rotation, rotates image, re-runs detection. Improves accuracy on uniformly-rotated pages but doubles detection time.
- **`detect_language`** (default `False`) — adds predicted language to `Page.language`. Slight latency cost.

### Performance

- **`det_bs`** — detection batch size (default 2). Higher = faster but more memory.
- **`reco_bs`** — recognition batch size (default 128). Higher = faster for many word crops.
- **`preserve_aspect_ratio`** (default `True`) — pads input to preserve aspect ratio before detection.
- **`symmetric_pad`** (default `True`) — pads evenly on all sides instead of bottom-right.

## Usage

```python
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

# Quick start — default model
model = ocr_predictor(pretrained=True)
doc = DocumentFile.from_pdf("invoice.pdf")
result = model(doc)

# Iterate results
for page in result.pages:
    text = page.render()
    print(f"Page {page.page_idx}: {text[:100]}...")

# Custom architecture
model = ocr_predictor(
    det_arch="db_resnet50",
    reco_arch="parseq",
    pretrained=True,
)

# For rotated documents
model = ocr_predictor(
    pretrained=True,
    assume_straight_pages=False,
    export_as_straight_boxes=True,
    detect_orientation=True,
)
result = model(doc)
for page in result.pages:
    print(f"Rotation: {page.orientation['value']}°")

# With language detection
model = ocr_predictor(pretrained=True, detect_language=True)
result = model(doc)
for page in result.pages:
    print(f"Language: {page.language.get('value')}")
```

## Forward Method

```python
result = model(pages: list[np.ndarray], **kwargs) -> Document
```

- **Input:** list of numpy arrays (H×W×3, uint8), one per page
- **Output:** `Document` object with full OCR results
- Runs in `torch.inference_mode()` automatically

## Gotchas

- **First run downloads weights** — pretrained weights fetch from HuggingFace Hub. Subsequent runs use cached weights.
- **Default is `fast_base` + `crnn_vgg16_bn`** — not `db_resnet50`. The README example uses `db_resnet50` explicitly.
- **`straighten_pages` doubles detection** — it runs detection twice (once to estimate rotation, once after rotating). Use only when needed.
- **`detect_orientation` without `straighten_pages`** — orientation is estimated from segmentation map median line, not from a separate model. It's fast but approximate.
- **GPU is automatic** — if CUDA is available, the model runs on GPU. No `.to("cuda")` needed.
- **Batch size vs memory** — `det_bs` controls how many full pages are processed at once. Large pages with high `det_bs` can OOM. Start with default 2.
- **`export_as_straight_boxes` only matters when `assume_straight_pages=False`** — when pages are assumed straight, boxes are always straight.
- **`preserve_aspect_ratio` affects geometry** — if True, bounding box coordinates account for padding. The coordinates are always relative to the original image dimensions.
