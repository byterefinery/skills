# Advanced Features — RapidOCR 3.9.2

## Word-Level Bounding Boxes

Enable per-word (and per-character) bounding boxes within each recognized line:

```python
result = engine(img, return_word_box=True)

# result.word_results is a tuple of tuples
# Each outer tuple = one line
# Each inner tuple = list of (word_text, score, box_coords)
for line_idx, line_words in enumerate(result.word_results):
    for word_text, word_score, word_box in line_words:
        print(f"  Line {line_idx}: [{word_score:.2f}] '{word_text}' at {word_box}")
```

**Box coordinates:** `word_box` is `List[List[int]]` — polygon corners `[x, y]` relative to the original image (mapped back from cropped region).

### Single Character Boxes

```python
result = engine(img, return_word_box=True, return_single_char_box=True)
```

Returns individual character bounding boxes within each word.

### Word Type Classification

Words are classified by type:

| Type | Value | Description |
|---|---|---|
| `WordType.CN` | `"cn"` | Chinese characters |
| `WordType.EN` | `"en"` | English letters |
| `WordType.NUM` | `"num"` | Numbers |
| `WordType.EN_NUM` | `"en&num"` | Mixed English + numbers |

## Visualization

### Basic Visualization

```python
# Via result object (uses stored image + viser)
result.vis("output.png")

# Via standalone VisRes
from rapidocr import VisRes

viser = VisRes(text_score=0.5, lang_type="ch", font_path=None)
vis_img = viser(img_path, result.boxes, result.txts, result.scores)

# Save
import cv2
cv2.imwrite("output.png", vis_img)
```

### Visualization Features

- Colored polygon overlays on detected text regions
- Text labels with confidence scores
- Language-appropriate fonts (auto-downloaded)
- Vertical text support (character-by-character rendering)
- Score filtering — boxes below `text_score` are not drawn

### Font Handling

VisRes auto-selects fonts based on `lang_type`:

- Chinese → bundled `FZYTK.TTF`
- Other languages → language-specific fonts downloaded from ModelScope
- Custom font → pass `font_path` directly

Fonts are cached in `rapidocr/models/` directory.

## Output Formats

### JSON

```python
json_data = result.to_json()
# [
#   {"box": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]], "txt": "hello", "score": 0.98},
#   ...
# ]
```

### Markdown (Layout-Aware)

```python
md = result.to_markdown()
```

Reconstructs approximate original layout from bounding box coordinates:

- Groups text items into lines based on vertical overlap
- Sorts lines top-to-bottom, items left-to-right within lines
- Inserts spaces proportional to horizontal gaps
- Inserts blank lines for large vertical gaps (paragraph breaks)

### Direct Access

```python
result.boxes    # np.ndarray (N, 4, 2)
result.txts     # tuple of str
result.scores   # tuple of float
result.elapse   # float — total time
result.elapse_list  # [det_time, cls_time, rec_time]
```

## Image Preprocessing

### Auto-Resize

```yaml
Global:
  use_preprocess_img: true
  min_side_len: 30
  max_side_len: 2000
```

Large images are resized before detection to speed up processing. Boxes are mapped back to original coordinates.

### Vertical Padding

```yaml
Global:
  use_vertical_padding: true
  min_height: 30
  width_height_ratio: 8
```

When image width/height ratio exceeds `width_height_ratio`, vertical padding is applied to improve detection of horizontally elongated text.

### Input Image Handling

`LoadImage` handles multiple input formats:

| Input | Conversion |
|---|---|
| File path / URL | PIL → ndarray, RGB→BGR |
| NumPy (3-channel, from file) | RGB→BGR |
| NumPy (3-channel, from OpenCV) | No conversion (already BGR) |
| NumPy (2-channel: gray+alpha) | Gray→BGR + alpha blend |
| NumPy (4-channel: RGBA) | Auto background + alpha blend |
| NumPy (1-channel: grayscale) | Gray→BGR |
| Bytes | PIL → ndarray, RGB→BGR |
| PIL Image | ndarray, RGB→BGR |

**RGBA handling:** Background color is auto-selected based on foreground luminance — white background for dark text, black background for light text.

**EXIF orientation:** Images loaded from files have EXIF orientation applied automatically.

## RTL Language Support

Arabic, Farsi, and Urdu text is automatically reordered for display:

```python
engine = RapidOCR(params={"Rec.lang_type": "arabic"})
result = engine(img)
# result.txts contains correctly ordered text for display
```

The `reorder_bidi_for_display` utility handles visual ordering of bidirectional text.

## Detection-Only / Recognition-Only Modes

### Detection Only

```python
engine = RapidOCR(params={"Global.use_cls": False, "Global.use_rec": False})
result = engine(img)
# Returns TextDetOutput with boxes and scores
```

### Recognition Only (No Detection)

```python
result = engine(img, use_det=False)
# Entire image treated as one text region
# Returns TextRecOutput with txts and scores
```

Useful for pre-cropped text regions or when you already know the text area.

### Classification Only

```python
engine = RapidOCR(params={"Global.use_det": False, "Global.use_rec": False})
result = engine(img)
# Returns TextClsOutput — checks if image needs 180° rotation
```

## Batch Processing

Engine instance is reusable across calls:

```python
engine = RapidOCR()

for img_path in image_paths:
    result = engine(img_path)
    # Process result
```

The engine caches model sessions — no reload between calls.

## Performance Tuning

### Thread Control

```yaml
EngineConfig:
  onnxruntime:
    intra_op_num_threads: 4    # Threads within ops
    inter_op_num_threads: 2    # Threads between ops
```

### Batch Size

```yaml
Cls:
  cls_batch_num: 6    # More = faster on GPU, more memory

Rec:
  rec_batch_num: 6    # More = faster on GPU, more memory
```

### Model Size vs Speed

- `tiny` — fastest, lowest accuracy
- `mobile` — good balance, default
- `small` — better accuracy (v6)
- `medium` — best accuracy (v6)
- `server` — best accuracy (v4/v5)

### TensorRT FP16/INT8

```yaml
EngineConfig:
  tensorrt:
    use_fp16: true     # ~2x speedup on modern GPUs
    use_int8: false    # Requires calibration data
```

## Docker

```bash
# Build with ONNX Runtime CPU
make build-onnxruntime-cpu
make test-onnxruntime-cpu

# Build with TensorRT
make build-tensorrt
make shell-tensorrt

# Other engines: onnxruntime-gpu, openvino, paddle, pytorch, mnn
```

See `docker/README.md` in the repo for full GPU configuration and troubleshooting.
