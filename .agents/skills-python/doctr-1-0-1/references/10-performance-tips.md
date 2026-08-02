# Performance Tips

Guidance for optimizing docTR inference speed, memory usage, and accuracy tradeoffs.

## Model Selection

### Fastest Pipeline

```python
model = ocr_predictor(
    det_arch="fast_tiny",         # lightest detection
    reco_arch="crnn_mobilenet_v3_small",  # lightest recognition
    pretrained=True,
    assume_straight_pages=True,   # skip rotation handling
)
```

### Best Accuracy

```python
model = ocr_predictor(
    det_arch="db_resnet50",       # most accurate detection
    reco_arch="parseq",           # state-of-the-art recognition
    pretrained=True,
    assume_straight_pages=False,  # handle rotated text
)
```

### Balanced (Default)

```python
model = ocr_predictor(pretrained=True)
# det_arch="fast_base", reco_arch="crnn_vgg16_bn"
```

## Batch Size Tuning

```python
# Increase detection batch size (default: 2)
model = ocr_predictor(pretrained=True, det_bs=4)

# Increase recognition batch size (default: 128)
model = ocr_predictor(pretrained=True, reco_bs=256)
```

- **`det_bs`** — processes full pages. Limited by GPU memory and page resolution. Start with 2, increase if memory allows.
- **`reco_bs`** — processes word crops. Small crops fit many in batch. 128–512 is typical.

## GPU Usage

- Models run on GPU automatically if CUDA is available
- No explicit `.to("cuda")` needed
- Check: `torch.cuda.is_available()`

For CPU-only inference, install CPU PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cpu`

## PDF Rasterization

```python
# Higher DPI for small text (slower, more accurate)
doc = DocumentFile.from_pdf("doc.pdf", scale=3)

# Lower DPI for speed (faster, less accurate on small text)
doc = DocumentFile.from_pdf("doc.pdf", scale=1)
```

- `scale=1` = 72 DPI (fastest)
- `scale=2` = 144 DPI (default, good balance)
- `scale=3` = 216 DPI (for small text)
- `scale=4` = 288 DPI (for very fine print)

## Memory Management

```python
# Process large documents page-by-page
import pypdfium2 as pdfium
from doctr.models import ocr_predictor

model = ocr_predictor(pretrained=True)
pdf = pdfium.PdfDocument("large.pdf")

for page in pdf:
    img = page.render(scale=2).to_numpy()
    result = model([img])
    # Process result immediately, don't accumulate
    text = result.render()
    print(text)

pdf.close()
```

## Orientation Handling Tradeoffs

| Option | Speed | Accuracy on rotated pages |
|--------|-------|--------------------------|
| `assume_straight_pages=True` (default) | Fastest | Poor for rotated text |
| `assume_straight_pages=False` | Medium | Good |
| `+ straighten_pages=True` | Slowest (2× detection) | Best |
| `+ detect_orientation=True` | Slight overhead | Adds metadata |

## Caching Weights

Pretrained weights are downloaded from HuggingFace Hub on first use and cached locally. Subsequent runs load from cache.

Cache location: `~/.cache/huggingface/hub/` (default HF cache).

To pre-warm cache:

```python
from doctr.models import ocr_predictor
# Trigger download
model = ocr_predictor(pretrained=True)
```

## Production Tips

- **Reuse the model** — create the predictor once, run inference many times. Model initialization (weight loading) is expensive.
- **Use `fast_*` detection models** — they are reparameterized for fast inference.
- **Set `assume_straight_pages=True`** if you know your documents are not rotated.
- **Process in batches** — pass multiple pages to `model([page1, page2, ...])` instead of one at a time.
- **Avoid `.show()` in production** — it imports matplotlib and blocks execution.
- **Use `.export()` for JSON, `.render()` for text** — avoid materializing the full object tree if you only need text.

## Gotchas

- **First inference is slow** — weight loading + model initialization happens on first call. Pre-warm by running on a dummy image.
- **Large pages eat memory** — a 4000×6000 page at scale=3 is a huge tensor. Consider downsampling or tiling.
- **`det_bs` is the main memory bottleneck** — detection processes full-page images. Recognition processes small crops and is less memory-intensive.
- **FAST models are already reparameterized** — no manual step needed. The zoo handles it.
- **`straighten_pages` doubles detection time** — it literally runs detection twice. Only use when accuracy on rotated pages is critical.
- **CPU inference is slow** — docTR is designed for GPU. CPU inference works but is significantly slower, especially for ResNet-based models.
