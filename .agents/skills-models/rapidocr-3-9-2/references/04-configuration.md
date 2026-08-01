# Configuration — RapidOCR 3.9.2

## Config System

RapidOCR uses OmegaConf with YAML config files. Three ways to configure:

1. **Built-in default** — `config.yaml` shipped with the package
2. **Custom YAML file** — `RapidOCR(config_path="my_config.yaml")`
3. **Programmatic params** — `RapidOCR(params={"Rec.lang_type": LangRec.EN})`

Params can override config file values. Dot notation is used for nested keys.

## Global Settings

```yaml
Global:
  text_score: 0.5            # Min confidence to include in output
  use_det: true               # Enable text detection
  use_cls: true               # Enable text classification
  use_rec: true               # Enable text recognition

  use_preprocess_img: true    # Resize large images before processing
  min_side_len: 30            # Minimum side length after resize
  max_side_len: 2000          # Maximum side length after resize

  use_vertical_padding: true  # Pad image vertically for better detection
  min_height: 30              # Minimum padded height
  width_height_ratio: 8       # Max width/height ratio before padding

  return_word_box: false      # Return per-word bounding boxes
  return_single_char_box: false  # Return per-character boxes

  font_path: null             # Custom font for visualization
  log_level: "info"           # debug / info / warning / error / critical

  model_root_dir: null        # Custom model cache dir (null = package default)
```

## Detection (Det) Section

```yaml
Det:
  engine_type: "onnxruntime"  # onnxruntime | openvino | paddle | torch | tensorrt | mnn
  lang_type: "ch"             # ch | en | multi
  model_type: "small"         # mobile | server | tiny | small | medium
  ocr_version: "PP-OCRv6"     # PP-OCRv4 | PP-OCRv5 | PP-OCRv6
  task_type: "det"

  model_path: null            # Custom model file (skips auto-download)
  model_dir: null             # Custom model directory

  limit_side_len: 736         # Max dimension for detection input
  limit_type: min             # min = use limit_side_len as minimum

  std: [0.5, 0.5, 0.5]       # Normalization std
  mean: [0.5, 0.5, 0.5]      # Normalization mean

  thresh: 0.3                 # Binary threshold for DBNet output
  box_thresh: 0.5             # Box confidence threshold
  max_candidates: 1000        # Max candidate boxes
  unclip_ratio: 1.6           # Box expansion ratio
  use_dilation: true          # Apply dilation to DBNet output
  score_mode: fast            # fast | slow (score computation mode)
```

**Detection preprocessing:** Adaptive sizing based on input image. If `limit_type: min`, uses `limit_side_len`. If image max dimension > 960, scales to 960; > 1500, scales to 1500; > 2000, stays at 2000.

## Classification (Cls) Section

```yaml
Cls:
  engine_type: "onnxruntime"
  lang_type: "ch"
  model_type: "mobile"        # mobile | server
  ocr_version: "PP-OCRv4"     # PP-OCRv4 | PP-OCRv5
  task_type: "cls"

  model_path: null
  model_dir: null

  cls_image_shape: [3, 48, 192]  # Auto-set by ocr_version (v4: 48x192, v5: 80x160)
  cls_batch_num: 6              # Batch size for classification
  cls_thresh: 0.9               # Threshold for rotation decision
  label_list: ["0", "180"]      # Classification labels
```

## Recognition (Rec) Section

```yaml
Rec:
  engine_type: "onnxruntime"
  lang_type: "ch"              # ch | en | japan | korean | arabic | ...
  model_type: "small"          # mobile | server | tiny | small | medium
  ocr_version: "PP-OCRv6"
  task_type: "rec"

  model_path: null
  model_dir: null

  rec_keys_path: null          # Custom character dictionary file
  rec_img_shape: [3, 48, 320]  # Input shape (C, H, W)
  rec_batch_num: 6             # Batch size for recognition
```

## Engine Config Section

```yaml
EngineConfig:
  onnxruntime:
    intra_op_num_threads: -1
    inter_op_num_threads: -1
    enable_cpu_mem_arena: false
    cpu_ep_cfg:
      arena_extend_strategy: "kSameAsRequested"
    use_cuda: false
    cuda_ep_cfg:
      device_id: 0
      arena_extend_strategy: "kNextPowerOfTwo"
      cudnn_conv_algo_search: "EXHAUSTIVE"
      do_copy_in_default_stream: true
    use_dml: false
    use_cann: false
    use_coreml: false

  openvino:
    inference_num_threads: -1
    performance_hint: null
    performance_num_requests: -1

  paddle:
    cpu_math_library_num_threads: -1
    use_cuda: false
    use_npu: false

  torch:
    use_cuda: false
    use_npu: false
    use_mps: false

  tensorrt:
    device_id: 0
    use_fp16: true
    use_int8: false
    workspace_size: 1073741824
    cache_dir: null
    force_rebuild: false

  mnn: {}
```

## Parameter Override (Programmatic)

Use dot notation with `params` dict. Enum fields require actual Enum instances:

```python
from rapidocr import RapidOCR, EngineType, LangRec, OCRVersion

engine = RapidOCR(params={
    # Global
    "Global.text_score": 0.7,
    "Global.use_det": True,
    "Global.return_word_box": True,
    "Global.model_root_dir": "/custom/cache",

    # Detection
    "Det.engine_type": EngineType.ONNXRUNTIME,
    "Det.lang_type": "multi",
    "Det.model_type": "small",
    "Det.ocr_version": OCRVersion.PPOCRV6,

    # Recognition
    "Rec.engine_type": EngineType.ONNXRUNTIME,
    "Rec.lang_type": LangRec.CH,
    "Rec.model_type": "small",
    "Rec.ocr_version": OCRVersion.PPOCRV6,

    # Engine config
    "EngineConfig.onnxruntime.use_cuda": True,
    "EngineConfig.onnxruntime.cuda_ep_cfg.device_id": 0,
})
```

**Validation rules:**
- Keys must be valid dot-notation paths (e.g., `"Rec.lang_type"`)
- `engine_type`, `model_type`, `ocr_version`, `task_type` must be Enum instances
- Unknown keys raise `ValueError`
- Wrong type for enum fields raises `TypeError`

## Generating Config

```python
# Copy default config to a file
python -m rapidocr.main config --save_cfg_file my_config.yaml
```

Then edit the YAML directly and load with `RapidOCR(config_path="my_config.yaml")`.

## Per-Stage Engine Mixing

Each stage can use a different engine:

```python
engine = RapidOCR(params={
    "Det.engine_type": EngineType.TENSORRT,    # GPU detection
    "Cls.engine_type": EngineType.ONNXRUNTIME,  # CPU classification
    "Rec.engine_type": EngineType.OPENVINO,     # CPU recognition
})
```

This is useful when different engines perform better for different model sizes or tasks.
