# VLM Pipeline

The `VlmPipeline` converts documents end-to-end using a Vision-Language Model. It processes each page as an image and generates structured output (DocTags or Markdown). Docling supports VLMs that output DocTags (preferred), Markdown, or HTML.

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

CLI: `docling --pipeline vlm FILE` (or simply `--vlm-model <preset>`, which selects the VLM pipeline). The default VLM preset is `granite_docling`. Run `docling models --vlm` to list presets.

## Local model presets

Presets live in `docling.datamodel.vlm_model_specs`. Each has `_TRANSFORMERS`, and often `_MLX` / `_VLLM` variants, plus `ApiVlmOptions` presets for remote endpoints (`_VLLM_API`, `_OLLAMA`, etc.).

Representative presets (verify the full list with `docling models --vlm`):

| Preset family | Output | Notes |
|---------------|--------|-------|
| `GRANITEDOCLING_*` | DocTags | Default; most structured output |
| `SMOLDOCLING_*` | DocTags | Lighter (~256M) |
| `SMOLVLM256_*` | — | SmolVLM 256M variant |
| `GRANITE_VISION_*` | Markdown | Granite Vision |
| `PIXTRAL_12B_*` | Markdown | Pixtral 12B |
| `PHI4_TRANSFORMERS` | Markdown | Phi-4 Multimodal |
| `QWEN25_VL_3B_MLX` | Markdown | Qwen2.5-VL 3B (Apple Silicon) |
| `NANONETS_OCR2_*` | Markdown | Nanonets OCR2 3B |
| `GEMMA3_12B_MLX` / `GEMMA3_27B_MLX` | Markdown | Gemma 3 (Apple Silicon) |

DocTags-output models (GraniteDocling, SmolDocling) produce the most structured output; Markdown-output models are more human-readable.

```python
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.datamodel import vlm_model_specs

pipeline_options = VlmPipelineOptions(
    vlm_options=vlm_model_specs.GRANITEDOCLING_TRANSFORMERS,  # or _MLX, etc.
)
```

## Remote inference servers

Offload VLM inference to a remote server (vLLM, Ollama, LM Studio, or any OpenAI-compatible API). Use the `ApiVlmOptions` presets or pass a URL/params dict; set `enable_remote_services=True`.

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

Ollama endpoint: `http://localhost:11434/v1/chat/completions`. Models must be in GGUF format for llama.cpp-based runtimes (Ollama, LM Studio).

## CLI usage

```bash
docling --pipeline vlm FILE                          # default VLM preset
docling --vlm-model granite_docling FILE             # selects the VLM pipeline
docling models --vlm                                 # list presets
```

Combining `--vlm-model` with a different `--pipeline` value produces an error.

## Output formats

VLM models produce either **DocTags** (structured, preferred for downstream processing) or **Markdown** (human-readable). DocTags-output models are recommended for production pipelines where structured output matters.
