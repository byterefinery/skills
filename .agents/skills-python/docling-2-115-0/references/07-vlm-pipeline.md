# VLM Pipeline

The `VlmPipeline` converts documents end-to-end using a Vision-Language Model. It processes each page as an image and generates structured output (DocTags or Markdown).

## Basic usage

```python
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_cls=VlmPipeline),
    }
)

doc = converter.convert(source="document.pdf").document
```

CLI: `docling --pipeline vlm FILE`

## Local models

### Preset models

```python
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.datamodel import vlm_model_specs

# Default: GraniteDocling (DocTags output)
pipeline_options = VlmPipelineOptions(
    vlm_options=vlm_model_specs.GRANITEDOCLING_TRANSFORMERS,
)

# SmolDocling (DocTags, lighter)
pipeline_options = VlmPipelineOptions(
    vlm_options=vlm_model_specs.SMOLDOCLING_TRANSFORMERS,
)

# MLX variants (Apple Silicon)
pipeline_options = VlmPipelineOptions(
    vlm_options=vlm_model_specs.GRANITEDOCLING_MLX,
)
```

### Available local models

| Preset | Model | Framework | Output |
|--------|-------|-----------|--------|
| `GRANITEDOCLING_TRANSFORMERS` | Granite-Docling-258M | Transformers | DocTags |
| `GRANITEDOCLING_MLX` | Granite-Docling-258M | MLX | DocTags |
| `SMOLDOCLING_TRANSFORMERS` | SmolDocling-256M | Transformers | DocTags |
| `SMOLDOCLING_MLX` | SmolDocling-256M | MLX | DocTags |
| `GRANITE_VISION_TRANSFORMERS` | Granite-Vision-3.2-2B | Transformers | Markdown |
| `PIXTRAL_12B_TRANSFORMERS` | Pixtral-12B | Transformers | Markdown |
| `PIXTRAL_12B_MLX` | Pixtral-12B | MLX | Markdown |
| `PHI4_TRANSFORMERS` | Phi-4-Multimodal | Transformers | Markdown |
| `NANONETS_OCR2_TRANSFORMERS` | Nanonets-OCR2-3B | Transformers | Markdown |
| `GEMMA3_12B_MLX` | Gemma-3-12B | MLX | Markdown |
| `GEMMA3_27B_MLX` | Gemma-3-27B | MLX | Markdown |
| `QWEN25_VL_3B_MLX` | Qwen2.5-VL-3B | MLX | Markdown |
| `NANONETS_OCR2_MLX` | Nanonets-OCR2-3B | MLX | Markdown |

DocTags-output models (GraniteDocling, SmolDocling) produce the most structured output. Markdown-output models are more human-readable.

## Remote inference servers

Offload VLM inference to a remote server (vLLM, Ollama, LM Studio, or any OpenAI-compatible API):

```python
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.datamodel.settings import settings

pipeline_options = VlmPipelineOptions(
    enable_remote_services=True,
    vlm_options={
        "url": "http://localhost:8000/v1/chat/completions",
        "params": {"model": "ibm-granite/granite-docling-258M", "max_tokens": 4096},
        "concurrency": 64,
        "prompt": "Convert this page to docling.",
        "timeout": 90,
    }
)

# Match page_batch_size to concurrency
settings.perf.page_batch_size = 64

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=VlmPipeline,
            pipeline_options=pipeline_options,
        )
    }
)
```

### Inference server setup (vLLM)

```bash
vllm serve ibm-granite/granite-docling-258M \
  --host 127.0.0.1 --port 8000 \
  --max-num-seqs 512 \
  --max-num-batched-tokens 8192 \
  --enable-chunked-prefill \
  --gpu-memory-utilization 0.9
```

### Ollama / LM Studio endpoints

- Ollama: `http://localhost:11434/v1/chat/completions`
- LM Studio: `http://localhost:1234/v1/chat/completions`

Models must be in GGUF format for llama.cpp-based runtimes (Ollama, LM Studio).

## Custom VLM configuration

```python
from docling.datamodel.pipeline_options_vlm_model import (
    InlineVlmOptions, InferenceFramework, TransformersModelType
)
from docling.datamodel.base_models import AcceleratorDevice
from docling.datamodel.pipeline_options import ResponseFormat

pipeline_options = VlmPipelineOptions(
    vlm_options=InlineVlmOptions(
        repo_id="your-org/custom-vlm",
        prompt="Convert this page to markdown. Do not miss any text!",
        response_format=ResponseFormat.MARKDOWN,
        inference_framework=InferenceFramework.TRANSFORMERS,
        transformers_model_type=TransformersModelType.AUTOMODEL_VISION2SEQ,
        supported_devices=[
            AcceleratorDevice.CPU,
            AcceleratorDevice.CUDA,
            AcceleratorDevice.MPS,
        ],
        scale=2.0,          # image scale factor
        temperature=0.0,    # deterministic output
    )
)
```

## Performance tuning

### GPU with remote inference

```python
from docling.datamodel.settings import settings

# Set batch size >= concurrency
settings.perf.page_batch_size = 64

pipeline_options = VlmPipelineOptions(
    enable_remote_services=True,
    vlm_options={
        "url": "http://localhost:8000/v1/chat/completions",
        "params": {"model": "ibm-granite/granite-docling-258M", "max_tokens": 4096},
        "concurrency": 64,
    }
)
```

### GPU performance reference

| Pipeline | g6e.2xlarge (L40S) | RTX 5090 | RTX 5070 |
|----------|-------------------|----------|----------|
| Standard (no OCR) | 3.1 pages/s | 7.9 pages/s | 4.2 pages/s |
| Standard (with OCR) | — | 1.6 pages/s | 1.1 pages/s |
| VLM (GraniteDocling) | 2.4 pages/s | 3.8 pages/s | 2.0 pages/s |

## CLI usage

```bash
# Default VLM (GraniteDocling)
docling --pipeline vlm FILE

# Specific model preset
docling --pipeline vlm --vlm-model smoldocling FILE
docling --pipeline vlm --vlm-model granite_docling FILE
docling --pipeline vlm --vlm-model granite_vision FILE
docling --pipeline vlm --vlm-model pixtral FILE
docling --pipeline vlm --vlm-model phi4 FILE
docling --pipeline vlm --vlm-model qwen FILE
docling --pipeline vlm --vlm-model nanonets_ocr2 FILE
```

## Output formats

VLM models produce either:
- **DocTags** — structured XML-like format, preferred for downstream processing
- **Markdown** — human-readable, suitable for display

DocTags-output models (GraniteDocling, SmolDocling) are recommended for production pipelines where structured output matters.
