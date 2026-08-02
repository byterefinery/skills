# Recognition Models — Text Reading

Text recognition reads character sequences from cropped word images. Each model takes a word crop and outputs a text string with confidence.

## Recognition Predictor

```python
from doctr.models import recognition_predictor

model = recognition_predictor(
    arch="crnn_vgg16_bn",    # architecture name or model instance
    pretrained=True,          # load pretrained weights
    symmetric_pad=False,      # asymmetric padding (default)
    batch_size=128,           # processing batch size
)

# Run recognition on word crops
import numpy as np
crop = (255 * np.random.rand(32, 128, 3)).astype(np.uint8)
result = model([crop])
```

## Architecture Families

### CRNN (CNN + RNN)

- `crnn_vgg16_bn` — CRNN with VGG16 backbone (default, good accuracy)
- `crnn_mobilenet_v3_small` — lighter CRNN variant
- `crnn_mobilenet_v3_large` — heavier CRNN variant
- Uses CTC loss for sequence alignment
- Well-established, reliable across languages

### SAR (Show, Attend and Read)

- `sar_resnet31` — self-attention based recognition
- `master` — SAR variant with modified architecture
- Attention-based, handles variable-length text well
- Generally more accurate than CRNN on complex scripts

### ViTSTR (Vision Transformer for STR)

- `vitstr_small` — lightweight transformer
- `vitstr_base` — full transformer
- Pure transformer architecture, no RNN
- Strong on diverse scripts and languages

### PARSeq

- `parseq` — state-of-the-art accuracy
- Parser-based sequence recognition
- Best overall accuracy, heavier compute

### VIPTR

- `viptr_tiny` — Vision-Permutation Transformer
- Permutation-based approach
- Good accuracy with reasonable speed

## Input Format

Recognition models expect pre-cropped word images:

```python
# Expected input: list of numpy arrays, shape (H, W, 3), uint8
# Typical crop size: ~32px height, variable width
crop = np.zeros((32, 128, 3), dtype=np.uint8)
result = model([crop])

# Multiple crops at once
crops = [crop1, crop2, crop3]
result = model(crops)
```

## Output Format

Returns recognition results with text and confidence:

```python
for pred in result:
    print(f"Text: '{pred.x}' Confidence: {pred.y}")
```

## Architecture Selection Guide

| Need | Recommended |
|------|-------------|
| Default / balanced | `crnn_vgg16_bn` |
| Highest accuracy | `parseq` |
| Fast inference | `crnn_mobilenet_v3_small` |
| Multi-language | `vitstr_base` or `parseq` |
| Complex scripts | `sar_resnet31` or `vitstr` |
| Memory constrained | `crnn_mobilenet_v3_small` or `viptr_tiny` |

## Custom Model Instance

```python
from doctr.models import recognition, recognition_predictor

model = recognition.crnn_vgg16_bn(pretrained=False)
predictor = recognition_predictor(arch=model, pretrained=False)
```

Allowed instance types: `CRNN`, `SAR`, `MASTER`, `ViTSTR`, `PARSeq`, `VIPTR`, or compiled modules.

## Gotchas

- **Input must be word crops** — recognition models expect individual word images, not full pages. Use `ocr_predictor` for end-to-end processing.
- **Height normalization** — crops are internally resized to model input height (typically 32px). Aspect ratio is preserved.
- **`batch_size=128` is default** — recognition processes many small crops in parallel. This is much higher than detection batch size.
- **`symmetric_pad=False` is default** — recognition uses asymmetric padding (bottom-right), unlike detection which defaults to symmetric.
- **Vocabulary affects supported characters** — pretrained models are trained on specific character sets. For unusual scripts, retraining may be needed.
