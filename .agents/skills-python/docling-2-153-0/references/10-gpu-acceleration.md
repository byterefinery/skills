# GPU Acceleration

Docling supports GPU acceleration via CUDA (NVIDIA), MPS (Apple Silicon), and XPU (Intel). See `docs/usage/gpu.md` in the repo for full details.

## Device selection

### Python API

```python
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions

accelerator_options = AcceleratorOptions(
    device=AcceleratorDevice.AUTO,   # auto-detect (default)
    # device=AcceleratorDevice.CUDA / MPS / XPU / CPU to force
)

converter = DocumentConverter(
    accelerator_options=accelerator_options,
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)},
)
```

### CLI

`docling --device auto|cuda|mps|xpu|cpu document.pdf`. `--num-threads` sets CPU threads; `--page-batch-size` sets pages per batch.

## VLM pipeline GPU tuning

For best GPU utilization with VLM, use a local inference server (vLLM) and point Docling at it:

```python
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.datamodel.settings import settings

pipeline_options = VlmPipelineOptions(
    enable_remote_services=True,
    vlm_options={
        "url": "http://localhost:8000/v1/chat/completions",
        "params": {"model": "ibm-granite/granite-docling-258M", "max_tokens": 4096},
        "concurrency": 64,
    }
)
settings.perf.page_batch_size = 64   # must be >= concurrency
```

## CPU thread control

Docling defaults to a small number of CPU threads; set `OMP_NUM_THREADS` to limit or increase CPU usage.

## OCR GPU support

Most OCR engines handle GPU internally (e.g. RapidOCR with torch backend, EasyOCR when PyTorch CUDA is available).

## Notes

- TableFormer on MPS may be disabled for performance — prefer CUDA or CPU for table structure on Apple Silicon.
- Verify current device flags and defaults with `docling convert --help` since they evolve between releases.
