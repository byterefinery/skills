#!/usr/bin/env python3
"""docling_extract — Extract PDF to Markdown using docling with ONNX Runtime layout.

Usage:
    docling_extract.py INPUT [-o OUTPUT] [--ocr] [--vlm] [--help]

Modes:
    (default)  Standard pipeline with Heron layout via ONNX Runtime, no OCR
    --ocr      Standard pipeline + RapidOCR (ONNX)
    --vlm      VLM pipeline with Granite-Docling-258M
"""

import argparse
import sys
import time
from pathlib import Path

from docling.datamodel.pipeline_options import (
    LayoutObjectDetectionOptions,
    PdfPipelineOptions,
    VlmPipelineOptions,
)
from docling.datamodel.object_detection_engine_options import (
    OnnxRuntimeObjectDetectionEngineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption


def derive_output(input_path: Path, ext: str = "md") -> Path:
    return input_path.with_suffix(f".{ext}")


def extract_standard(input_path: Path, output_path: Path, use_ocr: bool = False) -> None:
    """Standard pipeline with ONNX Runtime layout (Heron)."""
    mode_label = "standard + RapidOCR/ONNX" if use_ocr else "standard, Heron layout/ONNX"
    print(f"  Trying docling ({mode_label})...", file=sys.stderr)

    # Layout via ONNX Runtime
    layout_options = LayoutObjectDetectionOptions.from_preset("layout_heron_default")
    layout_options.engine_options = OnnxRuntimeObjectDetectionEngineOptions()

    pipeline_options = PdfPipelineOptions(
        layout_options=layout_options,
        do_ocr=use_ocr,
        do_table_structure=True,
    )
    if use_ocr:
        from docling.datamodel.pipeline_options import RapidOcrOptions
        pipeline_options.ocr_options = RapidOcrOptions()

    converter = DocumentConverter(
        format_options={
            "pdf": PdfFormatOption(pipeline_options=pipeline_options),
        }
    )

    t0 = time.time()
    result = converter.convert(input_path)
    elapsed = time.time() - t0

    md = result.document.export_to_markdown()
    output_path.write_text(md)

    lines = md.count("\n")
    size_kb = output_path.stat().st_size / 1024
    print(f"  → docling ({lines} lines, {size_kb:.0f}K, {elapsed:.2f}s)", file=sys.stderr)


def extract_vlm(input_path: Path, output_path: Path) -> None:
    """VLM pipeline with Granite-Docling-258M."""
    print(f"  Trying docling (VLM pipeline, Granite-Docling-258M)...", file=sys.stderr)

    pipeline_options = VlmPipelineOptions()

    converter = DocumentConverter(
        format_options={
            "pdf": PdfFormatOption(pipeline_options=pipeline_options),
        }
    )

    t0 = time.time()
    result = converter.convert(input_path)
    elapsed = time.time() - t0

    md = result.document.export_to_markdown()
    output_path.write_text(md)

    lines = md.count("\n")
    size_kb = output_path.stat().st_size / 1024
    print(f"  → docling-vlm ({lines} lines, {size_kb:.0f}K, {elapsed:.2f}s)", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Extract PDF to Markdown via docling")
    parser.add_argument("input", type=Path, help="Input PDF file")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output Markdown file")
    parser.add_argument("--ocr", action="store_true", help="Enable OCR (RapidOCR/ONNX)")
    parser.add_argument("--vlm", action="store_true", help="Use VLM pipeline (Granite-Docling-258M)")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"  error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.ocr and args.vlm:
        print("  error: --ocr and --vlm are mutually exclusive", file=sys.stderr)
        sys.exit(1)

    output = args.output or derive_output(args.input, "md")
    output.parent.mkdir(parents=True, exist_ok=True)

    if args.vlm:
        extract_vlm(args.input, output)
    else:
        extract_standard(args.input, output, use_ocr=args.ocr)


if __name__ == "__main__":
    main()
