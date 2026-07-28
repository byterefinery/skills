# Pipeline Options

Pipeline options customize model execution during conversion. Each pipeline type has its own options class.

## PdfPipelineOptions

The standard PDF pipeline options:

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions

options = PdfPipelineOptions()
options.do_ocr = False                    # enable OCR
options.do_table_structure = True         # enable table extraction (default)
options.do_code_enrichment = False        # code block understanding
options.do_formula_enrichment = False     # formula LaTeX extraction
options.do_picture_classification = False # picture type classification
options.do_picture_description = False    # picture captioning
options.generate_picture_images = False   # required for picture enrichment
options.images_scale = 1                  # image resolution multiplier
options.artifacts_path = None             # local model path (offline mode)
options.enable_remote_services = False    # remote API calls
options.allow_external_plugins = False    # third-party plugins
```

### TableFormer mode

```python
from docling.datamodel.pipeline_options import TableFormerMode

options.table_structure_options.mode = TableFormerMode.ACCURATE  # default
options.table_structure_options.mode = TableFormerMode.FAST      # faster, less accurate
options.table_structure_options.do_cell_matching = True          # default: map to PDF cells
options.table_structure_options.do_cell_matching = False         # use model-predicted cells
```

Setting `do_cell_matching = False` can improve output when multiple columns are erroneously merged.

### Threaded pipeline

For GPU batch processing:

```python
from docling.datamodel.pipeline_options import ThreadedPdfPipelineOptions

options = ThreadedPdfPipelineOptions(
    ocr_batch_size=64,       # default 4
    layout_batch_size=64,    # default 4
    table_batch_size=4,      # not using GPU batching
)
```

## VlmPipelineOptions

Vision-Language Model pipeline for full-page conversion:

```python
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.datamodel import vlm_model_specs

options = VlmPipelineOptions(
    vlm_options=vlm_model_specs.GRANITEDOCLING_TRANSFORMERS,  # local model
    enable_remote_services=False,
)

# Remote inference server
options = VlmPipelineOptions(
    enable_remote_services=True,
    vlm_options={
        "url": "http://localhost:8000/v1/chat/completions",
        "params": {"model": "ibm-granite/granite-docling-258M", "max_tokens": 4096},
        "concurrency": 64,
        "prompt": "Convert this page to docling.",
        "timeout": 90,
    }
)
```

### Local VLM model selection

```python
from docling.datamodel import vlm_model_specs

# Transformers framework
options.vlm_options = vlm_model_specs.GRANITEDOCLING_TRANSFORMERS
options.vlm_options = vlm_model_specs.SMOLDOCLING_TRANSFORMERS
options.vlm_options = vlm_model_specs.GRANITE_VISION_TRANSFORMERS
options.vlm_options = vlm_model_specs.PIXTRAL_12B_TRANSFORMERS
options.vlm_options = vlm_model_specs.PHI4_TRANSFORMERS

# MLX framework (Apple Silicon)
options.vlm_options = vlm_model_specs.GRANITEDOCLING_MLX
options.vlm_options = vlm_model_specs.SMOLDOCLING_MLX
options.vlm_options = vlm_model_specs.PIXTRAL_12B_MLX
options.vlm_options = vlm_model_specs.GEMMA3_12B_MLX
```

### Custom VLM model

```python
from docling.datamodel.pipeline_options_vlm_model import (
    InlineVlmOptions, InferenceFramework, TransformersModelType
)
from docling.datamodel.base_models import AcceleratorDevice

options.vlm_options = InlineVlmOptions(
    repo_id="ibm-granite/granite-vision-3.2-2b",
    prompt="Convert this page to markdown. Do not miss any text!",
    response_format=ResponseFormat.MARKDOWN,
    inference_framework=InferenceFramework.TRANSFORMERS,
    transformers_model_type=TransformersModelType.AUTOMODEL_VISION2SEQ,
    supported_devices=[AcceleratorDevice.CPU, AcceleratorDevice.CUDA, AcceleratorDevice.MPS],
    scale=2.0,
    temperature=0.0,
)
```

## AsrPipelineOptions

Audio Speech Recognition pipeline:

```python
from docling.datamodel.pipeline_options import AsrPipelineOptions
from docling.datamodel import asr_model_specs

options = AsrPipelineOptions()
options.asr_options = asr_model_specs.WHISPER_TURBO   # auto-selects backend
options.asr_options = asr_model_specs.WHISPER_LARGE   # larger model
options.asr_options = asr_model_specs.WHISPER_TURBO_MLX     # force MLX backend
options.asr_options = asr_model_specs.WHISPER_TURBO_NATIVE  # force native Whisper
options.asr_options = asr_model_specs.WHISPER_LARGE_V3_S2T  # WhisperS2T (CPU/CUDA)
```

## VideoPipelineOptions

Video processing with frame sampling and diarization:

```python
from docling.datamodel.pipeline_options import VideoPipelineOptions
from docling.utils.video_frame_sampling import VideoFrameSamplingMode

options = VideoPipelineOptions(
    frame_sampling_mode=VideoFrameSamplingMode.SCENE_CHANGE,
    scene_change_prominence=0.03,     # for meetings
    enable_diarization=True,          # speaker attribution
    frame_interval_seconds=10.0,      # for FIXED_INTERVAL mode
    cuts_per_minute=2.0,              # for SCENE_CHANGE mode
    max_sampled_frames=100,           # cap total frames
    generate_frame_images=True,       # set False to skip frame sampling
)
```

## Common options across pipelines

- `artifacts_path` — path to locally cached model weights (offline mode)
- `enable_remote_services` — must be `True` for any remote API calls
- `allow_external_plugins` — must be `True` to load third-party plugins
- `accelerator_options` — device selection (CUDA, MPS, XPU, CPU)

## Applying pipeline options

```python
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline

# Standard PDF pipeline
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

# VLM pipeline
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=VlmPipeline,
            pipeline_options=vlm_pipeline_options,
        )
    }
)
```
