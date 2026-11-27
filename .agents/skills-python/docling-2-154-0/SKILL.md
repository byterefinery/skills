---
name: docling-2-154-0
description: >
  Docling 2.154.0 — document parsing and conversion library that transforms
  PDF (born-digital or scanned), DOCX, PPTX, XLSX, HTML, Markdown, AsciiDoc,
  CSV, images, audio, video, EPUB, ODF, LaTeX, email, and XML into a unified
  DoclingDocument. Use when converting documents to Markdown, JSON, HTML,
  DocTags, or plain text; extracting tables, figures, code, formulas, or form
  fields; running OCR on scanned documents; transcribing audio/video with ASR;
  pulling typed fields via DocumentExtractor (beta); chunking for RAG; or
  offloading conversion to a remote docling-serve. Covers the docling CLI,
  Python SDK (DocumentConverter + PipelineOptions), standard/VLM/native PDF
  pipelines, OCR engines, enrichments, GPU acceleration, offline models,
  Service Client, and docling-slim install extras. Triggers on docling,
  document conversion, PDF parsing, table extraction, OCR, DoclingDocument,
  document-to-markdown, DocTags, RAG chunking, Whisper ASR, VLM pipeline,
  granite_docling, smoldocling, docling-serve.
license: MIT
compatibility: >
  Python 3.10+. Full `docling` package pulls PyTorch (~50MB base). Audio/video
  needs ffmpeg on PATH. macOS Intel (x86_64) needs PyTorch 2.2.2 and Python
  3.12 or lower.
metadata:
  tags:
    - document-processing
    - pdf
    - ocr
    - rag
    - python
---

# docling 2.154.0

## Overview

Docling converts documents — PDF, DOCX, PPTX, XLSX, HTML, Markdown, AsciiDoc, CSV, images, audio, video, and XML — into a single unified representation, the **`DoclingDocument`**, exportable as **Markdown** (human-readable) or **JSON** (structured, lossless). Reach for it whenever you need to understand the content of a file you cannot read directly, especially PDFs (including scanned ones, via OCR or a vision-language model).

**Three pipeline families for PDF/images:**
- **Standard** (default) — layout + OCR + table structure models; CPU-only OK; best for born-digital and scanned PDFs
- **VLM** — full-page conversion through a vision-language model (GraniteDocling, SmolDocling, Nemotron Parse, Surya, MiniCPM-OCR, …); best for complex layouts, handwriting, formulas
- **Native** — no models at all; dumps text cells and embedded bitmaps as fast as possible; PDF only, no reading order/headings/tables

**Choosing how to use Docling:**

| You need to… | Use | Reference |
|---|---|---|
| Read / convert a file once, from the shell | CLI (`docling …`) | [01-cli](references/01-cli.md) |
| Convert programmatically, tune pipeline, batch, ASR, export images/tables | Python SDK (`DocumentConverter` + `PipelineOptions`) | [02-python-sdk](references/02-python-sdk.md) |
| Pull specific typed fields out of a document (beta) | `DocumentExtractor` | [03-extraction](references/03-extraction.md) |
| Chunk documents for RAG / framework loaders | `HybridChunker`, LangChain/LlamaIndex/Haystack loaders | [04-rag](references/04-rag.md) |
| Offload conversion to a remote docling-serve | Service Client | [05-service-client](references/05-service-client.md) |
| Install only the dependencies you need | `docling-slim` extras | [06-slim-packaging](references/06-slim-packaging.md) |

Rules of thumb: local one-off, no code → CLI. Custom pipeline, chunking, structure analysis, app embedding → Python SDK. Many documents, low latency, no local ML/GPU, scale on demand → Service Client against a `docling-serve` endpoint (self-hosted or managed). Minimal install footprint → docling-slim with targeted extras.

## Installation

```bash
pip install docling                    # batteries-included meta-package
uvx --from docling docling report.pdf --to md --output /tmp/   # run without installing
```

For a minimal footprint use `docling-slim` with targeted extras — see [06-slim-packaging](references/06-slim-packaging.md).

## Usage

### Basic conversion (CLI)

```bash
docling report.pdf --to md --output /tmp/              # Markdown (readable)
docling report.pdf --to json --output /tmp/            # DoclingDocument JSON (lossless)
docling https://arxiv.org/pdf/2408.09869 --to md       # convert a URL
docling report.pdf --pipeline vlm --vlm-model granite_docling --output /tmp/
```

### Basic conversion (Python)

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("report.pdf")  # local path or http(s) URL
doc = result.document                     # a DoclingDocument
print(doc.export_to_markdown())
data = doc.export_to_dict()              # structured / lossless
```

### Chunking for RAG (Python)

```python
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer

tokenizer = HuggingFaceTokenizer.from_pretrained(
    model_name="sentence-transformers/all-MiniLM-L6-v2", max_tokens=512,
)
chunker = HybridChunker(tokenizer=tokenizer, merge_peers=True)
for chunk in chunker.chunk(result.document):
    print(chunker.contextualize(chunk), chunk.meta.headings, chunk.meta.origin.page_no)
```

## Gotchas

- **`format_options` keys must be `InputFormat` enum members** — `{InputFormat.PDF: PdfFormatOption(pipeline_options=PdfPipelineOptions(...))}`. String keys like `{"pdf": PdfPipelineOptions(...)}` fail at runtime with `AttributeError: 'PdfPipelineOptions' object has no attribute 'backend'`.
- **`enable_remote_services=True` is mandatory for any remote model** — Docling blocks outbound HTTP by default; using `ApiVlmOptions`, `KserveV2OcrOptions`, or remote VLM endpoints without it raises an error.
- **PDF headings all come out at `level=1`** unless `HeadingHierarchyOptions(enabled=True)` is set in `PdfPipelineOptions`.
- **`convert()` vs `convert_all()`** — single source returns one `ConversionResult`; `convert_all(sources)` returns an iterator. Default `raises_on_error=True` aborts on the first failure; pass `False` to collect per-result statuses (`SUCCESS`, `PARTIAL_SUCCESS`, `FAILURE`, `SKIPPED`).
- **HybridChunker needs a tokenizer object, not a string** — the tokenizer API changed in docling-core 2.8.0; pass a `BaseTokenizer` (e.g., `HuggingFaceTokenizer.from_pretrained(...)`). Chunking requires the `feat-chunking` extra.
- **Models download on first use** — artifacts cache to the Hugging Face cache dir. For offline/air-gapped runs, prefetch with `docling-tools models download --output-dir /models` and point at them via `artifacts_path` (SDK) or `--artifacts-path` (CLI). Plain `--all` excludes ASR models; add `--asr`.
- **`--vlm-model` implies the VLM pipeline** — combining `--vlm-model NAME` with a different `--pipeline` value is an error. Audio/video use `--asr-model` without `--pipeline`.
- **Native pipeline has no structure** — `--pipeline native --from pdf` gives one text item per native cell and one picture per bitmap, but no reading order, headings, or tables. PDF input only. If the backend ends early you get partial results; `--fail-on partial` exits 1 for them.
- **OCR is on by default in the standard pipeline** — disable with `--no-ocr` (faster) or force full-page re-OCR with `--force-ocr`. `--replace-broken-text-layer` OCRs only pages whose text layer is broken (those pages then report `parse_score` 0).
- **Default OCR auto-selection never picks Tesseract** — without RapidOCR installed, select an engine explicitly (`--ocr-engine tesseract --ocr-lang eng`) or PDFs convert without OCR. The table structure model also needs OpenCV, which RapidOCR otherwise brings in; add `opencv-python-headless` on headless servers (never install both opencv variants).
- **Tables flatten in Markdown** — Markdown has no cell-span syntax; for merged headers use `export_to_html()` or the dict/JSON export. Prefer `table.export_to_dataframe(doc=doc)` / `table.export_to_markdown()` per table item.
- **Re-converting a saved DoclingDocument JSON drops local image references** — paths and `file:` URIs are ignored (with a warning) unless you opt in with `DoclingJSONFormatOption(backend_options=DeclarativeBackendOptions(enable_local_fetch=True))`; embedded `data:` images and http(s) URLs are always kept. Save with `ImageRefMode.EMBEDDED` if the JSON must be self-contained.
- **`extract_form_fields` is not available in the Service Client or DocTags export** — AcroForm field extraction requires local conversion with the docling-parse backend; table cells need `do_table_structure=True`.
- **Video diarization and frame sampling are optional** — video uses `VideoPipeline` (`max_sampled_frames` defaults to 200); when `document_timeout` is set, all FFmpeg calls share that budget and running out yields `PARTIAL_SUCCESS` with a `TIMEOUT` error.
- **DOCX/XLSX/PPTX are size-checked before parsing** — decompressed sizes above the defaults (128 MiB per member, 512 MiB total, 10,000 members) fail with `ArchiveLimitError`; raise via `MsWordBackendOptions` / `MsExcelBackendOptions` / `MsPowerpointBackendOptions`.
- **macOS Intel needs PyTorch 2.2.2** — newer PyTorch dropped x86_64 macOS wheels; pin `torch==2.2.2 torchvision==0.17.2` with Python ≤3.12.
- **CLI exit codes** — exit 1 when a document fails; partially converted documents are still written and exit 0 unless `--fail-on partial`. `--abort-on-error` stops at the first failure.
- **Output conventions** — always report conversion status and (for PDFs) page count. If the user does not specify a format, ask whether they want Markdown (readable) or JSON/DoclingDocument (structured, lossless). A converted PDF that comes back near-empty, repeated, or full of `U+FFFD` is likely scanned or complex layout — retry with OCR or `--pipeline vlm`.

## References

- [01-cli](references/01-cli.md) — `docling` CLI: pipelines, OCR engines, tables/enrichments, offline models, exit codes
- [02-python-sdk](references/02-python-sdk.md) — DocumentConverter, PipelineOptions (standard/native/VLM), OCR engines, ASR, chunking, exports, batch
- [03-extraction](references/03-extraction.md) — DocumentExtractor structured field extraction (beta), Pydantic templates
- [04-rag](references/04-rag.md) — HybridChunker, LangChain/LlamaIndex/Haystack loaders
- [05-service-client](references/05-service-client.md) — DoclingServiceClient, convert/chunk remotely, async and jobs, CLI `convert-remote`
- [06-slim-packaging](references/06-slim-packaging.md) — docling-slim install extras catalog and recipes
