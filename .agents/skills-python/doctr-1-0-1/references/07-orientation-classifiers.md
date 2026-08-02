# Orientation Classifiers

docTR provides two orientation classification predictors: one for individual word crops and one for full pages.

## Crop Orientation Predictor

Classifies the rotation of individual text crops (word-level).

```python
from doctr.models import crop_orientation_predictor

model = crop_orientation_predictor(
    arch="mobilenet_v3_small_crop_orientation",
    pretrained=True,
    batch_size=128,
)

import numpy as np
crop = (255 * np.random.rand(256, 256, 3)).astype(np.uint8)
result = model([crop])
```

- **Default arch:** `mobilenet_v3_small_crop_orientation`
- **Input:** word crops, typically 256×256
- **Default batch size:** 128
- Used internally when `detect_orientation=True` in `ocr_predictor`

## Page Orientation Predictor

Classifies the rotation of full document pages.

```python
from doctr.models import page_orientation_predictor

model = page_orientation_predictor(
    arch="mobilenet_v3_small_page_orientation",
    pretrained=True,
    batch_size=4,
)

from doctr.io import DocumentFile
pages = DocumentFile.from_pdf("rotated.pdf")
result = model(pages)
```

- **Default arch:** `mobilenet_v3_small_page_orientation`
- **Input:** full page images
- **Default batch size:** 4
- Useful for pre-processing before OCR

## Classification Architectures

The orientation classifiers use these architectures from the classification zoo:

- `mobilenet_v3_small_crop_orientation` — crop-level orientation
- `mobilenet_v3_small_page_orientation` — page-level orientation

The general classification zoo also includes: `magc_resnet31`, `mobilenet_v3_small/large` (with `_r` suffix for rotation), `resnet18/31/34/50`, `resnet34_wide`, `textnet_tiny/small/base`, `vgg16_bn_r`, `vit_s/b`, `vip_tiny/base`.

## Integration with OCR

Orientation detection is built into `ocr_predictor`:

```python
from doctr.models import ocr_predictor

# Automatic orientation detection
model = ocr_predictor(
    pretrained=True,
    detect_orientation=True,      # adds orientation to Page
    straighten_pages=True,         # rotates pages before re-detection
)
result = model(doc)

for page in result.pages:
    angle = page.orientation.get("value")
    print(f"Page {page.page_idx}: {angle}° rotation")
```

- **`detect_orientation=True`** — estimates page rotation from segmentation maps or via classifier
- **`straighten_pages=True`** — uses estimated rotation to rotate pages, then re-runs detection

## Gotchas

- **`crop_orientation_predictor` takes word crops** — not full pages. Input should be ~256×256 crops.
- **`page_orientation_predictor` takes full pages** — not crops. Input is the full rasterized page.
- **These are standalone predictors** — for integrated orientation handling, use `detect_orientation` and `straighten_pages` in `ocr_predictor`.
- **`straighten_pages` is more accurate than `detect_orientation` alone** — it physically rotates the page and re-runs detection, improving both localization and recognition.
- **Orientation values are in degrees** — typically 0°, 90°, 180°, or 270° for standard rotations.
