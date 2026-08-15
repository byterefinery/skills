---
name: rapidocr-3-9-2
description: >
  RapidOCR 3.9.2 — ultra-fast, offline, multi-platform OCR engine with 6 inference backends
  (ONNX Runtime, TensorRT, OpenVINO, PaddlePaddle, PyTorch, MNN), PP-OCRv4/v5/v6 models,
  15+ recognition languages, and word-level bounding boxes. Use for text detection,
  classification, and recognition from images, URLs, bytes, or numpy arrays. Supports
  CPU, CUDA, NPU, MPS, DML, and CANN devices.
license: Apache-2.0
compatibility: Requires Python 3.8+. Core deps include rapidocr, onnxruntime, opencv-python, and numpy. GPU engines need tensorrt, openvino, paddlepaddle, torch, or MNN installed separately.
metadata:
  tags:
    - ocr
    - vision
    - text-recognition
    - deep-learning
    - onnx
---

# rapidocr 3.9.2

## Overview

RapidOCR is a high-performance OCR toolkit that converts PaddleOCR models to ONNX format
for fast, offline inference across platforms. Its pipeline has three stages:

1. **Text Detection** — finds text regions (bounding boxes) using DBNet
2. **Text Classification** — detects upside-down text (0°/180°) and rotates crops
3. **Text Recognition** — recognizes characters via CTC decoding

The engine auto-downloads models on first use. Models cache in `rapidocr/models/` or a custom
`model_root_dir`. PP-OCRv6 is the latest model family with unified multilingual detection
and recognition.

## Usage

### Basic

```python
from rapidocr import RapidOCR

engine = RapidOCR()
result = engine("image.jpg")

# result has: boxes, txts, scores
for txt, score, box in zip(result.txts, result.scores, result.boxes):
    print(f"[{score:.2f}] {txt}")

# Visualize and save
result.vis("output.png")
```

### Language Selection

```python
from rapidocr import LangRec, RapidOCR

# English only
engine = RapidOCR(params={"Rec.lang_type": LangRec.EN})

# Japanese
engine = RapidOCR(params={"Rec.lang_type": LangRec.JAPAN})

# Arabic (RTL auto-reordering applied)
engine = RapidOCR(params={"Rec.lang_type": LangRec.ARABIC})
```

### Engine Backend Selection

```python
from rapidocr import EngineType, RapidOCR

# ONNX Runtime with CUDA
engine = RapidOCR(params={
    "Det.engine_type": EngineType.ONNXRUNTIME,
    "Cls.engine_type": EngineType.ONNXRUNTIME,
    "Rec.engine_type": EngineType.ONNXRUNTIME,
    "EngineConfig.onnxruntime.use_cuda": True,
})

# TensorRT (requires tensorrt package)
engine = RapidOCR(params={
    "Det.engine_type": EngineType.TENSORRT,
    "Cls.engine_type": EngineType.TENSORRT,
    "Rec.engine_type": EngineType.TENSORRT,
})

# OpenVINO
engine = RapidOCR(params={
    "Det.engine_type": EngineType.OPENVINO,
    "Cls.engine_type": EngineType.OPENVINO,
    "Rec.engine_type": EngineType.OPENVINO,
})
```

### Model Version and Size

```python
from rapidocr import OCRVersion, RapidOCR

# PP-OCRv5 mobile
engine = RapidOCR(params={
    "Det.ocr_version": OCRVersion.PPOCRV5,
    "Det.model_type": "mobile",
    "Rec.ocr_version": OCRVersion.PPOCRV5,
    "Rec.model_type": "mobile",
})

# PP-OCRv6 medium (best accuracy)
engine = RapidOCR(params={
    "Det.ocr_version": OCRVersion.PPOCRV6,
    "Det.model_type": "medium",
    "Rec.ocr_version": OCRVersion.PPOCRV6,
    "Rec.model_type": "medium",
})
```

### Per-Call Overrides

```python
# Disable detection (treat whole image as text)
result = engine(img, use_det=False)

# Disable classification (skip rotation check)
result = engine(img, use_cls=False)

# Adjust thresholds
result = engine(img, text_score=0.7, box_thresh=0.6)

# Word-level boxes
result = engine(img, return_word_box=True)
```

### Input Types

```python
# File path
result = engine("photo.jpg")

# URL
result = engine("https://example.com/image.png")

# NumPy array (BGR from OpenCV)
import cv2
img = cv2.imread("photo.jpg")
result = engine(img)

# Bytes
with open("photo.jpg", "rb") as f:
    result = engine(f.read())

# PIL Image
from PIL import Image
result = engine(Image.open("photo.jpg"))
```

### Output Formats

```python
# JSON
json_data = result.to_json()
# [{"box": [[x,y],...], "txt": "hello", "score": 0.98}, ...]

# Markdown (layout-aware)
md = result.to_markdown()

# Visualization
vis_img = result.vis("output.png")  # returns ndarray, saves to path

# Direct access
result.boxes    # np.ndarray (N, 4, 2) — polygon corners
result.txts     # tuple of str
result.scores   # tuple of float
result.elapse   # total processing time in seconds
```

### CLI

```bash
# Quick test
python -m rapidocr.main -img photo.jpg

# With visualization
python -m rapidocr.main -img photo.jpg -vis --vis_save_dir ./output

# Word-level boxes
python -m rapidocr.main -img photo.jpg -word

# Generate config file
python -m rapidocr.main config --save_cfg_file my_config.yaml

# Download models ahead of time
python -m rapidocr.main download_models --config my_config.yaml

# Verify installation
python -m rapidocr.main check
```

### Custom Config File

```python
from rapidocr import RapidOCR

# Use a YAML config (full control over all parameters)
engine = RapidOCR(config_path="my_config.yaml")
```

### Pre-download Models

```python
from rapidocr import download_models

# Downloads default models
download_models()

# With custom config
download_models("my_config.yaml")
```

## Gotchas

- **Models download on first use** — the initial `engine(img)` call triggers model download. Use `download_models()` ahead of time to avoid blocking the first inference call.
- **ONNX Runtime is default** — it requires `onnxruntime` installed. Other engines (`tensorrt`, `openvino`, `paddle`, `torch`, `mnn`) need their respective packages installed separately.
- **PP-OCRv6 uses unified multilingual models** — detection and recognition use `multi_PP-OCRv6_*` models that support 50+ languages in a single model. For v4/v5, language-specific models are used.
- **Image input is auto-converted to BGR** — PIL images and file inputs are converted from RGB to BGR internally. If passing numpy arrays directly, ensure they are BGR (OpenCV format).
- **`use_det=False` skips detection** — the entire image is treated as one text region. Useful for pre-cropped text images or batch recognition of known regions.
- **`text_score` filters low-confidence results** — results below the threshold are dropped from output. Default is 0.5. Set higher for precision, lower for recall.
- **RTL languages auto-reorder** — Arabic, Farsi, and Urdu text is automatically reordered for display via `reorder_bidi_for_display`.
- **Config params use dot notation** — `"Rec.lang_type"`, `"Det.engine_type"`, `"EngineConfig.onnxruntime.use_cuda"`. Each param must be an Enum for `engine_type`, `model_type`, `ocr_version`, `task_type`.
- **`model_root_dir` defaults to package `models/`** — models download into the installed package directory. Set `Global.model_root_dir` to control cache location.
- **TensorRT builds engines on first use** — engines are cached after initial build. Set `force_rebuild: false` in config to skip rebuild.
- **`return_word_box=True` requires recognition model with word-level output** — not all model variants support this. It returns per-word bounding boxes within each line.
- **`VisRes` auto-downloads fonts** — visualization picks language-appropriate fonts and downloads them on first use.
- **`cls_image_shape` is version-dependent** — PP-OCRv4 uses `[3, 48, 192]`, PP-OCRv5 uses `[3, 80, 160]`. Set automatically based on `ocr_version`.

## References

- [01-api-reference](references/01-api-reference.md) — Full API surface: classes, methods, parameters, return types
- [02-engines](references/02-engines.md) — Inference backends: ONNX Runtime, TensorRT, OpenVINO, Paddle, PyTorch, MNN
- [03-models-languages](references/03-models-languages.md) — Model versions (PP-OCRv4/v5/v6), languages, model sizes, model matrix
- [04-configuration](references/04-configuration.md) — config.yaml structure, parameter system, engine-specific settings
- [05-advanced-features](references/05-advanced-features.md) — word-level boxes, visualization, output formats, preprocessing, RTL
