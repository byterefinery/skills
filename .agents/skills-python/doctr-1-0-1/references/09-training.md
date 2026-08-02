# Training Custom Models

docTR provides reference training scripts and building blocks for training custom detection, recognition, and classification models.

## Datasets

### Built-in Datasets (with auto-download)

```python
from doctr.datasets import (
    FUNSD,          # Form understanding (195 train / 305 test images)
    SROIE,          # Scanned receipt OCR (receipts)
    IMGUR5K,        # 5K natural scene text images
    SVHN,           # Street View House Numbers
    SVT,            # Street View Text
    IC03, IC13,     # ICDAR scene text competitions
    IIIT5K,         # 5K scene text images
    CORD,           # Chemical OCR & Recognition
    SynthText,      # Synthetic text data
    WildReceipt,    # Wild receipt dataset
)

# Auto-download and use
train_set = FUNSD(train=True, download=True)
test_set = FUNSD(train=False, download=True)
img, target = train_set[0]
```

Many datasets support `recognition_task=True` (returns cropped words + labels) and `detection_task=True` (returns full images + bounding boxes).

### Generic Datasets

```python
# Detection — COCO-style annotations
from doctr.datasets import DetectionDataset, OCRDataset

train_set = DetectionDataset(
    img_folder="/path/to/images",
    label_path="/path/to/labels.json",
    use_polygons=False,    # True for rotated boxes
)

# OCR format (doctr's own annotation format)
train_set = OCRDataset(
    img_folder="/path/to/images",
    label_file="/path/to/labels.json",
    use_polygons=False,
)

# Recognition — image + text label
from doctr.datasets import RecognitionDataset

train_set = RecognitionDataset(
    img_folder="/path/to/images",
    labels_path="/path/to/labels.json",
)
```

### Synthetic Data

```python
from doctr.datasets import WordGenerator, VOCABS

# Generate synthetic word images for training
generator = WordGenerator(
    num_gen_images=10000,
    vocab=VOCABS["french"],    # or custom string
    render_backend="pillow",   # or "opencv"
)
```

### VOCABS

Predefined character vocabularies for recognition training:

```python
from doctr.datasets import VOCABS

# Available: "digits", "latin", "french", "russian", "japanese", "korean", etc.
vocab = VOCABS["french"]
```

Build custom vocab: `vocab = "0123456789abcdefghijklmnopqrstuvwxyz .,;:!?-/"`

## Training Detection

Reference script: `references/detection/train.py`

```python
import torch
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from doctr.datasets import DetectionDataset
from doctr.models import detection
from doctr.utils.metrics import LocalizationConfusion
from doctr import transforms as T

# Dataset
train_set = DetectionDataset(img_folder="...", label_path="...")
train_loader = DataLoader(train_set, batch_size=8, shuffle=True, num_workers=4)

# Model
model = detection.db_resnet50(pretrained=False)

# Transform
batch_transforms = T.Compose([
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Optimizer
optimizer = AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
scheduler = CosineAnnealingLR(optimizer, T_max=len(train_loader))

# Metric
metric = LocalizationConfusion(iou_thresh=0.5, match_type="polygon")

# Training loop
model.train()
for images, targets in train_loader:
    optimizer.zero_grad()
    outputs = model(images, targets)
    loss = outputs["loss"]
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 5)
    optimizer.step()
    scheduler.step()
    metric.update(targets, outputs["preds"])
```

## Training Recognition

Reference script: `references/recognition/train.py`

```python
from doctr.datasets import RecognitionDataset, WordGenerator
from doctr.models import recognition
from doctr.utils.metrics import TextMatch

# Dataset
train_set = RecognitionDataset(img_folder="...", labels_path="...")
train_loader = DataLoader(train_set, batch_size=64, shuffle=True, num_workers=4)

# Model with custom vocab
model = recognition.crnn_vgg16_bn(pretrained=False, vocab=my_vocab)

# Generator for training (data augmentation)
generator = WordGenerator(num_gen_images=10000, vocab=my_vocab)

# Metric
metric = TextMatch()

# Training loop
model.train()
for images, targets in train_loader:
    optimizer.zero_grad()
    outputs = model(images, targets)
    loss = outputs["loss"]
    loss.backward()
    optimizer.step()
    metric.update(targets, [pred for pred, _ in outputs["preds"]])
```

## Transforms

```python
from doctr import transforms as T
from torchvision.transforms.v2 import Compose, RandomPhotometricDistort, RandomGrayscale

# Detection transforms
transform = Compose([
    T.Resize(output_size=(1024, 1024)),
    RandomPhotometricDistort(),
    RandomGrayscale(0.1),
    T.Normalize(),
])

# Recognition transforms
transform = Compose([
    T.Resize(output_size=(32, 128)),
    T.InvertIfDepthAlpha(),
    T.Normalize(),
])
```

## HuggingFace Hub

```python
from doctr.models import login_to_hub, push_to_hf_hub

# Login
login_to_hub()

# Push model
push_to_hf_hub(model, model_name="my-model", task="detection")
```

## Metrics

- **`LocalizationConfusion`** — detection metric (precision/recall/F1 at IoU threshold)
- **`TextMatch`** — recognition metric (raw, caseless, anyascii, unicase match rates)
- **`box_iou()`** / **`polygon_iou()`** — IoU computation utilities
- **`nms()`** — non-maximum suppression

## Gotchas

- **`vocab` must match training data** — for recognition models, the vocabulary used at training must cover all characters in the data. Unknown characters at inference time are replaced with a special character.
- **Detection models output dict** — `model(images, targets)` returns `{"loss": ..., "preds": ..., "maps": ...}` during training. During inference, the predictor wraps this.
- **`use_polygons=True` for rotated boxes** — datasets support both straight boxes and rotated polygons. Set `use_polygons=True` if your annotations use polygon format.
- **Gradient clipping is recommended** — the reference scripts use `clip_grad_norm_(parameters, 5)`.
- **AMP (Automatic Mixed Precision)** — reference scripts support `torch.cuda.amp.autocast()` for faster GPU training.
- **DDP support** — reference scripts support DistributedDataParallel for multi-GPU training.
- **Learning rate recording** — use `record_lr()` function from reference scripts to find optimal LR before training.
- **`WordGenerator` for augmentation** — generates synthetic word images with random fonts, backgrounds, and distortions. Useful when training data is limited.
