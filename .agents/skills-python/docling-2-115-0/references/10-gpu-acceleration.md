# GPU Acceleration

Docling supports GPU acceleration via CUDA (NVIDIA), MPS (Apple Silicon), and XPU (Intel).

## Device selection

### Python API

```python
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions

accelerator_options = AcceleratorOptions(
    device=AcceleratorDevice.AUTO,   # auto-detect (default)
    # device=AcceleratorDevice.CUDA,  # force NVIDIA GPU
    # device=AcceleratorDevice.MPS,   # force Apple Silicon
    # device=AcceleratorDevice.XPU,   # force Intel GPU
    # device=AcceleratorDevice.CPU,   # force CPU
)

converter = DocumentConverter(
    accelerator_options=accelerator_options,
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
    }
)
```

### CLI

```bash
docling --device auto document.pdf     # default
docling --device cuda document.pdf
docling --device mps document.pdf
docling --device xpu document.pdf
docling --device cpu document.pdf
```

## Standard pipeline GPU tuning

```python
from docling.datamodel.pipeline_options import ThreadedPdfPipelineOptions

pipeline_options = ThreadedPdfPipelineOptions(
    ocr_batch_size=64,       # default 4
    layout_batch_size=64,    # default 4
    table_batch_size=4,      # not using GPU batching
)
```

Higher `page_batch_size` runs layout detection in GPU batch inference mode.

### CPU thread control

```bash
export OMP_NUM_THREADS=8  # default is 4
```

## VLM pipeline GPU tuning

For best GPU utilization with VLM, use a local inference server.

### Start vLLM server

```bash
vllm serve ibm-granite/granite-docling-258M \
  --host 127.0.0.1 --port 8000 \
  --max-num-seqs 512 \
  --max-num-batched-tokens 8192 \
  --enable-chunked-prefill \
  --gpu-memory-utilization 0.9
```

### Configure Docling

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

# page_batch_size must be >= concurrency
settings.perf.page_batch_size = 64
```

## Flash Attention

Enable Flash Attention 2 for CUDA devices:

```bash
# Environment variable
export DOCLING_CUDA_USE_FLASH_ATTENTION2=1
```

```python
from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.pipeline_options import VlmPipelineOptions

pipeline_options = VlmPipelineOptions(
    accelerator_options=AcceleratorOptions(cuda_use_flash_attention2=True)
)
```

Requires `flash-attn` package:

```bash
# Pre-built wheels
FLASH_ATTENTION_SKIP_CUDA_BUILD=TRUE pip install flash-attn

# From source (needs CUDA dev environment)
pip install flash-attn
```

Flash Attention 2 requires Ampere+ GPUs (RTX 30xx+). Flash Attention 3 requires Hopper (H100+).

## OCR GPU support

Most OCR engines handle GPU internally:

```python
# RapidOCR with torch backend (GPU)
from docling.datamodel.pipeline_options import RapidOcrOptions

pipeline_options.ocr_options = RapidOcrOptions(backend="torch")
```

EasyOCR uses GPU when PyTorch CUDA is available.

## Performance reference

| Pipeline | g6e.2xlarge (L40S) | RTX 5090 | RTX 5070 |
|----------|-------------------|----------|----------|
| Standard (no OCR) | 3.1 pages/s | 7.9 pages/s | 4.2 pages/s |
| Standard (with OCR) | — | 1.6 pages/s | 1.1 pages/s |
| VLM (GraniteDocling) | 2.4 pages/s | 3.8 pages/s | 2.0 pages/s |

CPU-only timings (16 PyTorch threads): ~1.2–1.5 pages/s for standard pipeline.

## TableFormer GPU note

MPS is currently disabled for TableFormer due to performance issues. Use CUDA or CPU for table structure recognition on Apple Silicon.
