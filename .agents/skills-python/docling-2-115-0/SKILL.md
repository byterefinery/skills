---
name: docling-2-115-0
description: >
  Docling 2.115.0 — document parsing and conversion library that transforms PDF,
  DOCX, PPTX, XLSX, HTML, images, audio, video, EPUB, LaTeX, and more into a
  unified DoclingDocument representation. Use when converting documents to
  Markdown, JSON, HTML, DocTags, or DocLang; extracting tables, figures, code,
  and formulas; running OCR on scanned documents; processing audio/video with
  Whisper ASR; chunking documents for RAG; or integrating with LangChain,
  LlamaIndex, CrewAI, Haystack, or MCP. Covers DocumentConverter API, pipeline
  options (PDF, VLM, ASR), enrichment models, GPU acceleration, offline mode,
  CLI (docling, docling-tools), API server (docling-serve), and distributed
  processing via Jobkit. Trigger on: docling, document conversion, PDF parsing,
  table extraction, OCR, DoclingDocument, document-to-markdown, DocTags,
  document chunking, RAG pipeline, Whisper transcription, vision language model,
  VLM pipeline, ASR pipeline, picture classification, formula extraction.
license: MIT
compatibility: >
  Python 3.10–3.14. Base package is lightweight (~50MB). Full PDF processing
  requires PyTorch (GPU optional). Audio/video requires ffmpeg on PATH.
  macOS Intel (x86_64) needs PyTorch 2.2.2 and Python ≤3.12.
metadata:
  tags:
    - document-processing
    - pdf
    - ocr
    - nlp
    - rag
    - python
    - ai
---

# docling 2.115.0

## Overview

Docling 2.115.0 parses diverse document formats into a unified `DoclingDocument` representation, then exports to Markdown, JSON, HTML, DocTags, WebVTT, and more. It handles advanced PDF understanding (layout, reading order, table structure, code, formulas, image classification), OCR for scanned content, audio/video transcription via Whisper, and provides integrations with the gen AI ecosystem.

**Core architecture:** `DocumentConverter` orchestrates format-specific backends and pipelines, producing a `ConversionResult` containing a `DoclingDocument`. The document is then exported, chunked, or fed into downstream workflows.

**Key capabilities:**
- **Multi-format parsing** — PDF, DOCX, PPTX, XLSX, HTML, images, audio, video, EPUB, ODF, LaTeX, CSV, WebVTT, email (EML/MSG), Box Notes, DocLang, USPTO patents, JATS, XBRL
- **Advanced PDF understanding** — layout detection, table structure (TableFormer), code/formula extraction, picture classification and description
- **OCR** — multiple engines (Tesseract, EasyOCR, RapidOCR, macOS Vision, Surya, Nemotron)
- **Vision Language Models** — full-page conversion via VLM pipeline (GraniteDocling, SmolDocling, Pixtral, Phi-4, Qwen, and more)
- **Audio/Video** — Whisper-based ASR with MLX/native/WhisperS2T backends; video frame sampling and speaker diarization
- **Chunking** — Hybrid, Line-based token, and Hierarchical chunkers for RAG
- **Export** — Markdown, JSON, HTML, DocLang XML, DocTags, WebVTT, plain text, DocLang archive
- **Deployment** — CLI (`docling`), API server (`docling-serve`), MCP server, distributed Jobkit

## Installation

```bash
# Full package (PDF + standard features)
pip install docling

# Slim base (lightweight, add extras as needed)
pip install docling-slim[convert-core,cli]

# With ASR (audio/video transcription)
pip install "docling[asr]"

# With OCR engines
pip install "docling[easyocr]"          # EasyOCR
pip install "docling[rapidocr]"         # RapidOCR (ONNX)
pip install "docling[tesserocr]"        # Tesseract (linked)
pip install "docling[feat-ocr-nemotron]"  # NVIDIA Nemotron (Linux x86, CUDA 13)

# Video processing (frame sampling + diarization)
pip install "docling-slim[format-video]"
```

## Usage

### Basic conversion (Python)

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document.pdf")  # path or URL
doc = result.document

print(doc.export_to_markdown())
```

### Basic conversion (CLI)

```bash
docling document.pdf                          # PDF → Markdown (default)
docling --to json --to md document.pdf        # Multiple output formats
docling --no-ocr --no-tables document.pdf     # Disable features
docling --pipeline vlm --vlm-model granite_docling document.pdf  # VLM pipeline
```

See reference files for complete API coverage:

- **DocumentConverter** — conversion API, format options, batch processing: [01-document-converter](references/01-document-converter.md)
- **Pipeline options** — PDF, VLM, ASR pipeline configuration: [02-pipeline-options](references/02-pipeline-options.md)
- **DoclingDocument** — document model, iteration, element types: [03-docling-document](references/03-docling-document.md)
- **Export & serialization** — Markdown, JSON, HTML, DocTags, DocLang: [04-export-serialization](references/04-export-serialization.md)
- **Chunking** — Hybrid, Line-based, Hierarchical chunkers: [05-chunking](references/05-chunking.md)
- **Enrichments** — code, formula, picture classification/description: [06-enrichments](references/06-enrichments.md)
- **VLM pipeline** — vision-language model full-page conversion: [07-vlm-pipeline](references/07-vlm-pipeline.md)
- **ASR (audio/video)** — Whisper transcription, frame sampling, diarization: [08-asr-audio-video](references/08-asr-audio-video.md)
- **OCR engines** — engine selection, language configuration: [09-ocr-engines](references/09-ocr-engines.md)
- **GPU acceleration** — device selection, batch sizing, inference servers: [10-gpu-acceleration](references/10-gpu-acceleration.md)
- **CLI reference** — `docling` and `docling-tools` commands: [11-cli-reference](references/11-cli-reference.md)
- **Advanced usage** — binary streams, offline mode, remote services, model prefetching, confidence scores: [12-advanced-usage](references/12-advanced-usage.md)
- **Integrations** — MCP, API server, Jobkit, LangChain, LlamaIndex: [13-integrations](references/13-integrations.md)

## Gotchas

- **`DocumentConverter()` downloads models on first use** — models cache to `~/.cache/docling/models`. For offline/air-gapped environments, prefetch with `docling-tools models download` and set `artifacts_path` or `DOCLING_ARTIFACTS_PATH`.
- **`convert()` is single-file; `convert_all()` is batch** — `converter.convert(path)` returns one `ConversionResult`. `converter.convert_all([paths])` returns an iterator. The v1 naming was reversed.
- **`result.document` not `result.legacy_document`** — the v1 legacy document representation is completely removed. Always use `result.document` (a `DoclingDocument`).
- **`raises_on_error=True` by default** — `convert_all()` aborts on first error. Pass `raises_on_error=False` for resilient batch processing where errors appear per-result.
- **OCR requires `do_ocr=True` in pipeline options** — default `PdfPipelineOptions` has OCR disabled. Enable with `pipeline_options.do_ocr = True` and set `ocr_options`.
- **`enable_remote_services=True` is mandatory for remote APIs** — using remote vision models or cloud services without this flag raises `OperationNotAllowed()`.
- **`--allow-external-plugins` needed for third-party plugins** — both CLI and Python API require explicit opt-in for loading modules from third-party plugins.
- **Table cell spans flatten in Markdown** — Markdown has no span syntax. For accurate table structure (merged headers), use `export_to_html()` or `export_to_dict()`.
- **`HybridChunker` tokenizer warning is a false alarm** — the "sequence length exceeds model max" warning during chunking is expected. The chunker splits oversized sequences; the warning is harmless.
- **GPU batch size must match concurrency** — when using VLM with remote inference, set `settings.perf.page_batch_size >= vlm_options.concurrency` for optimal throughput.
- **`OMP_NUM_THREADS` controls CPU usage** — Docling defaults to 4 CPU threads. Set `OMP_NUM_THREADS` to limit or increase.
- **macOS Intel needs PyTorch 2.2.2** — newer PyTorch dropped macOS x86_64 support. Use `pip install "docling[mac_intel]"` or pin `torch==2.2.2 torchvision==0.17.2` with Python ≤3.12.
- **`opencv-python` vs `opencv-python-headless`** — on headless servers, install `opencv-python-headless` to avoid `libGL.so.1` errors. Never install both.
- **`DocumentStream` for in-memory PDFs** — to convert from a binary stream, wrap in `DocumentStream(name="doc.pdf", stream=BytesIO(data))`.
- **`max_num_pages` and `max_file_size` limit processing** — pass to `convert()` to reject oversized documents early.
- **Confidence grades, not scores** — focus on `result.confidence.mean_grade` and `result.confidence.low_grade` (POOR/FAIR/GOOD/EXCELLENT). Numerical scores are informational and may change.
- **`--to` repeats for multiple outputs** — CLI uses `--to md --to json` (repeatable), not `--to md,json`.
- **Whisper backends auto-select by hardware** — `WHISPER_TURBO` picks MLX on Apple Silicon, native Whisper elsewhere. Use `_MLX`, `_NATIVE`, or `_S2T` suffixes to force a backend.
- **WhisperS2T is not available on Apple Silicon** — the CTranslate2 backend installs only on non-Apple-Silicon platforms.
- **`generate_picture_images=True` needed for picture enrichment** — picture classification/description requires images to be generated first. Set `pipeline_options.generate_picture_images = True`.
- **`images_scale` controls picture resolution** — higher values produce larger images for better VLM description quality but use more memory. Default is 1.
- **Video diarization silently skipped without dependencies** — if `resemblyzer` etc. aren't installed, diarization is skipped but transcription and frame sampling proceed.
- **`docling-slim` vs `docling`** — the package is named `docling-slim` on PyPI but the full-featured meta-package is `docling`. Use `docling` for convenience.
- **`InputFormat` enum controls format routing** — format options are keyed by `InputFormat.PDF`, `InputFormat.DOCX`, etc. Using the wrong enum causes silent fallback to defaults.
- **`SimplePipeline` for declarative formats** — DOCX, PPTX, HTML use `SimplePipeline` by default (no ML models). `StandardPdfPipeline` and `VlmPipeline` are for PDF/images.
- **`--pdf-backend` choices matter** — `docling_parse` (default) vs `pypdfium2` vs `dlparse_v4` can affect text extraction quality on complex PDFs.
- **`--force-ocr` replaces all text** — forces OCR over the entire page, ignoring existing text layer. Useful for corrupted text layers but slower.
- **`--device` auto-detects accelerator** — default `auto` picks CUDA/MPS/XPU when available. Explicit `--device cuda` or `--device mps` forces a specific device.

## References

- [01-document-converter](references/01-document-converter.md) — DocumentConverter API, format options, batch processing, ConversionResult
- [02-pipeline-options](references/02-pipeline-options.md) — PdfPipelineOptions, VlmPipelineOptions, AsrPipelineOptions, table/OCR settings
- [03-docling-document](references/03-docling-document.md) — DoclingDocument model, element types, iteration, hierarchy, provenance
- [04-export-serialization](references/04-export-serialization.md) — export_to_markdown, export_to_dict, export_to_html, DocTags, DocLang, table spans
- [05-chunking](references/05-chunking.md) — HybridChunker, LineBasedTokenChunker, HierarchicalChunker, RAG chunking
- [06-enrichments](references/06-enrichments.md) — code understanding, formula extraction, picture classification, picture description
- [07-vlm-pipeline](references/07-vlm-pipeline.md) — VlmPipeline, local VLM models, remote inference, model presets
- [08-asr-audio-video](references/08-asr-audio-video.md) — Whisper ASR, audio transcription, video pipeline, frame sampling, diarization
- [09-ocr-engines](references/09-ocr-engines.md) — OCR engine selection, Tesseract, EasyOCR, RapidOCR, macOS Vision, language config
- [10-gpu-acceleration](references/10-gpu-acceleration.md) — CUDA/MPS/XPU, batch sizing, inference server setup, performance tuning
- [11-cli-reference](references/11-cli-reference.md) — `docling` CLI flags, `docling-tools models download`, output modes
- [12-advanced-usage](references/12-advanced-usage.md) — binary streams, offline mode, model prefetching, remote services, confidence scores
- [13-integrations](references/13-integrations.md) — MCP server, docling-serve API, Jobkit, LangChain DoclingLoader, LlamaIndex
