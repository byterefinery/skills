# Timing Summary

Benchmark results for PDF-to-Markdown extraction on a 129-page financial report PDF (~2MB).

**Test environment:** CPU-only (no GPU), docling v2.116.0.

## Results

| Engine | Mode | Time | Lines | Size | Notes |
|--------|------|------|-------|------|-------|
| poppler | `--poppler` | 1.1s | 6634 | 390K | Fastest, text layer only |
| pypdf | `--pypdf` | 2.0s | 5123 | 293K | Compact output, text layer only |
| ghostscript | `--gs` | 6.2s | 4856 | 439K | Text layer only |
| docling standard | `--docling` / `--layout` | 182s | 3764 | 385K | Heron layout via ONNX Runtime |
| docling + OCR | `--ocr` | 207s | 4314 | 415K | Standard + RapidOCR (ONNX) |
| docling VLM | `--vlm` | >1800s | — | — | Granite-Docling-258M, timed out on CPU |

## Key takeaways

- **For text-layer PDFs**: poppler/pypdf are fastest (1–2s). Use when you don't need layout-aware extraction.
- **For structured extraction**: docling standard (ONNX layout) gives ~2x speedup over the CLI default (Transformers), at ~182s for 129 pages.
- **For scanned pages**: `--ocr` (RapidOCR) adds ~25s overhead over standard mode and produces more content. `--vlm` requires GPU — impractical on CPU.
- **ONNX Runtime matters**: Switching layout from Transformers to ONNX Runtime cuts time from ~388s to ~182s (2.1x faster).

## Test file

`demo1/report.pdf` — Yettel Bank annual financial report 2025 (129 pages, ~2MB).
