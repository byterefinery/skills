# Detection Models — Text Localization

Text detection finds word-level bounding boxes in document images. docTR provides three families of detection architectures.

## Detection Predictor

```python
from doctr.models import detection_predictor

model = detection_predictor(
    arch="fast_base",               # architecture name or model instance
    pretrained=True,                 # load pretrained weights
    assume_straight_pages=True,      # fit straight boxes
    preserve_aspect_ratio=True,      # pad to preserve aspect ratio
    symmetric_pad=True,              # symmetric padding
    batch_size=2,                    # processing batch size
)

# Run detection
import numpy as np
from doctr.io import DocumentFile

doc = DocumentFile.from_images("doc.jpg")
result = model(doc)
```

## Architecture Families

### DBNet (Differentiable Binarization)

- `db_resnet34`, `db_resnet50`, `db_mobilenet_v3_large`
- Segmentation-based approach with differentiable thresholding
- Good accuracy, moderate speed
- ResNet backbones are heavier; MobileNet variant is lighter

### LinkNet

- `linknet_resnet18`, `linknet_resnet34`, `linknet_resnet50`
- Encoder-decoder architecture with skip connections
- Good for dense text layouts
- ResNet18 is lightest, ResNet50 is most accurate

### FAST (Fast Artifact Segmentation Text)

- `fast_tiny`, `fast_small`, `fast_base`
- Segmentation-based with reparameterization for fast inference
- **Auto-reparameterized** by the zoo — no manual step needed
- Fastest inference, competitive accuracy
- `fast_base` is the default detection architecture

## Output Format

Detection returns a list of quads (for straight boxes) or rotated boxes (for `assume_straight_pages=False`):

```python
# Straight boxes: list of ((xmin, ymin), (xmax, ymax)) per page
# Rotated boxes: numpy arrays with polygon vertices
for page_result in result:
    for box in page_result:
        print(box)  # ((0.1, 0.2), (0.3, 0.4)) — relative coords
```

## Architecture Selection Guide

| Need | Recommended |
|------|-------------|
| Fastest inference | `fast_tiny` or `fast_small` |
| Best speed/accuracy balance | `fast_base` (default) |
| Highest accuracy | `db_resnet50` |
| Memory constrained | `linknet_resnet18` or `fast_tiny` |
| Dense text / forms | `db_resnet50` or `linknet_resnet34` |

## Custom Model Instance

You can pass a model instance instead of a string:

```python
from doctr.models import detection, detection_predictor

# Build custom model
model = detection.db_resnet50(pretrained=False)

# Use it in predictor
predictor = detection_predictor(arch=model, pretrained=False)
```

Allowed instance types: `DBNet`, `LinkNet`, `FAST`, or compiled modules (`_CompiledModule`).

## Gotchas

- **FAST models auto-reparameterize** — the zoo calls `reparameterize()` automatically. You get fast inference without extra steps.
- **`assume_straight_pages` affects output format** — True returns straight `((xmin, ymin), (xmax, ymax))` tuples; False may return numpy arrays (rotated boxes).
- **Detection-only has no text** — `detection_predictor` returns bounding boxes only. For text content, use `ocr_predictor` or pipe detection output to `recognition_predictor`.
- **`batch_size` controls memory** — larger batch sizes speed up processing but use more GPU memory. Default is 2.
- **`preserve_aspect_ratio=True` is default** — input images are padded before detection. Geometry coordinates are always relative to original dimensions.
