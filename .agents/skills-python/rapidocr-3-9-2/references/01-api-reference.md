# API Reference — RapidOCR 3.9.2

## RapidOCR (Main Class)

### Constructor

```python
RapidOCR(
    config_path: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None
)
```

- **`config_path`** — path to YAML config file. If not provided, uses built-in `config.yaml`.
- **`params`** — dict of dot-notation parameter overrides. Keys like `"Rec.lang_type"`, `"Det.engine_type"`. Enum-valued params must use actual Enum instances, not strings.

### Call

```python
engine(
    img_content: Union[str, np.ndarray, bytes, Path, Image.Image],
    use_det: Optional[bool] = None,
    use_cls: Optional[bool] = None,
    use_rec: Optional[bool] = None,
    return_word_box: Optional[bool] = None,
    return_single_char_box: Optional[bool] = None,
    text_score: Optional[float] = None,
    box_thresh: Optional[float] = None,
    unclip_ratio: Optional[float] = None,
) -> Union[TextDetOutput, TextClsOutput, TextRecOutput, RapidOCROutput]
```

Per-call overrides:

| Param | Default | Effect |
|---|---|---|
| `use_det` | `True` | Run text detection. `False` treats whole image as text region |
| `use_cls` | `True` | Run text classification (0°/180° rotation) |
| `use_rec` | `True` | Run text recognition |
| `return_word_box` | `False` | Return per-word bounding boxes within each line |
| `return_single_char_box` | `False` | Return per-character boxes (requires `return_word_box=True`) |
| `text_score` | `0.5` | Minimum confidence threshold for results |
| `box_thresh` | `0.5` | Detection box confidence threshold |
| `unclip_ratio` | `1.6` | Expansion ratio for detected boxes |

**Return types depend on which stages ran:**
- All three stages → `RapidOCROutput`
- Detection only → `TextDetOutput`
- Classification only → `TextClsOutput`
- Recognition only (no detection) → `TextRecOutput`

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `text_det` | `TextDetector` | Detection sub-module |
| `text_cls` | `TextClassifier` | Classification sub-module |
| `text_rec` | `TextRecognizer` | Recognition sub-module |
| `cfg` | `DictConfig` | Full parsed configuration |
| `text_score` | `float` | Confidence threshold |
| `use_det` | `bool` | Whether detection is enabled |
| `use_cls` | `bool` | Whether classification is enabled |
| `use_rec` | `bool` | Whether recognition is enabled |

## Output Types

### RapidOCROutput

Full pipeline result (detection + classification + recognition).

| Attribute | Type | Description |
|---|---|---|
| `img` | `np.ndarray` | Original input image (BGR) |
| `boxes` | `np.ndarray` | Shape `(N, 4, 2)` — polygon corners for each text region |
| `txts` | `Tuple[str]` | Recognized text for each region |
| `scores` | `Tuple[float]` | Confidence scores |
| `word_results` | `Tuple` | Per-word results (when `return_word_box=True`) |
| `elapse` | `float` | Total processing time in seconds |
| `elapse_list` | `List[float]` | Per-stage times: `[det, cls, rec]` |
| `viser` | `VisRes` | Visualization helper |

**Methods:**

```python
result.to_json() -> List[Dict]
# [{"box": [[x,y],...], "txt": "text", "score": 0.98}, ...]

result.to_markdown() -> str
# Layout-aware markdown reconstruction

result.vis(save_path: Optional[str] = None) -> Optional[np.ndarray]
# Draw boxes + text on image, optionally save

len(result) -> int
# Number of text regions found
```

### TextDetOutput

Detection-only result.

| Attribute | Type |
|---|---|
| `img` | `Optional[np.ndarray]` |
| `boxes` | `Optional[np.ndarray]` — `(N, 4, 2)` |
| `scores` | `Optional[Tuple[float]]` |
| `elapse` | `Optional[float]` |

### TextClsOutput

Classification-only result.

| Attribute | Type |
|---|---|
| `img_list` | `Optional[List[np.ndarray]]` — rotated images |
| `cls_res` | `Optional[List[Tuple[str, float]]]` — `(label, score)` pairs |
| `elapse` | `Optional[float]` |

### TextRecOutput

Recognition-only result (when detection is disabled).

| Attribute | Type |
|---|---|
| `imgs` | `Optional[List[np.ndarray]]` |
| `txts` | `Optional[Tuple[str]]` |
| `scores` | `List[float]` |
| `word_results` | `Tuple` |
| `elapse` | `Optional[float]` |
| `viser` | `Optional[VisRes]` |

**Methods:**

```python
result.vis(save_path: Optional[str] = None) -> Optional[np.ndarray]
```

## VisRes (Visualization)

```python
VisRes(
    text_score: float = 0.5,
    lang_type: Union[LangRec, None, str] = None,
    font_path: Optional[str] = None,
)
```

```python
viser(
    img_content: InputType,
    dt_boxes: np.ndarray,
    txts: Optional[Union[List[str], Tuple[str]]] = None,
    scores: Optional[List[float]] = None,
) -> np.ndarray
```

- Draws colored polygon boxes with text labels on the image
- Auto-selects font based on `lang_type` (downloads on first use)
- Handles vertical text layout
- Returns BGR numpy array

**Static methods:**

```python
VisRes.concat_imgs(imgs: List[np.ndarray], direction: str) -> np.ndarray
# Concatenate images horizontally or vertically
```

## Utility Functions

### download_models

```python
download_models(config_path: Union[str, Path, None] = None) -> None
```

Pre-download models specified in config. Reads `use_det`, `use_cls`, `use_rec` flags to know which models to fetch. Saves to `model_root_dir` (default: `rapidocr/models/`).

### Enum Types

```python
from rapidocr import (
    EngineType,    # ONNXRUNTIME, OPENVINO, PADDLE, TORCH, TENSORRT, MNN
    LangRec,       # CH, EN, JAPAN, KOREAN, ARABIC, CYRILLIC, LATIN, ...
    LangDet,       # CH, EN, MULTI
    LangCls,       # CH
    ModelType,     # MOBILE, SERVER, TINY, SMALL, MEDIUM
    OCRVersion,    # PPOCRV4, PPOCRV5, PPOCRV6
    TaskType,      # DET, CLS, REC
    DeviceType,    # CPU, CUDA, NPU, XPU, MLU, DCU, GCU, MPS
)
```

### Exceptions

- `LoadImageError` — raised when image cannot be loaded
- `RapidOCRError` — raised when a pipeline stage produces empty results
- `ONNXRuntimeError` — raised by ONNX Runtime inference session
