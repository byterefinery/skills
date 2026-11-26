# OCR Engines

Docling supports multiple OCR engines for processing scanned PDFs and images. Languages are given as BCP-47 tags (e.g. `["en"]`, `["zh-Hant"]`) unless an engine uses its own codes.

## Engine comparison

| Engine | Installation | Options class | Notes |
|--------|-------------|---------------|-------|
| EasyOCR | `docling[easyocr]` or `pip install easyocr` | `EasyOcrOptions` | GPU-accelerated, many languages |
| Tesseract (linked) | System + `tesserocr` extra | `TesseractOcrOptions` | Efficient via linking |
| Tesseract CLI | System only | `TesseractCliOcrOptions` | No Python binding; needs `tesseract` on PATH |
| RapidOCR | `rapidocr` extra (default in standard) | `RapidOcrOptions` | ONNX/torch backends |
| macOS Vision | System (macOS) | `OcrMacOptions` | Native, excellent quality |
| Nemotron OCR | `docling-slim[feat-ocr-nemotron]` | `NemotronOcrOptions` | Linux x86_64, Python 3.12, CUDA 13 |
| OnnxTR | Plugin `docling-ocr-onnxtr` | `OnnxtrOcrOptions` | ONNX-based |
| Auto | Built-in default | — | Selects best available; never selects Tesseract |

## Enabling OCR

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = TesseractOcrOptions()   # or EasyOcrOptions(), RapidOcrOptions(), ...

converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)
```

The default auto-selection (`OcrAutoOptions`) never selects Tesseract and converts without OCR if nothing selectable is installed (logs "No OCR engine found"). Set `ocr_options` explicitly for determinism.

## Tesseract

System install required, then export `TESSDATA_PREFIX` to the language-data path in the same shell:

```bash
# macOS
brew install tesseract leptonica pkg-config
export TESSDATA_PREFIX="$(brew --prefix)/share/tessdata/"
tesseract --list-langs

# Debian-based
apt-get install tesseract-ocr tesseract-ocr-eng libtesseract-dev libleptonica-dev pkg-config
export TESSDATA_PREFIX="$(dpkg -L tesseract-ocr-eng | grep '/tessdata$')"
```

For linked usage (more efficient), install `tesserocr`; on 64-bit Windows, Tesserocr 2.12+ has prebuilt wheels (`pip install "docling[tesserocr]"`). The CLI variant only needs `tesseract.exe`/`tesseract` on PATH (or full path in the `tesseract_cmd` option).

**Default languages of the Tesseract options are `eng`, `spa`, `fra`, `deu`** — conversion fails if any is missing; set `lang=[...]` to what you installed.

## EasyOCR

```python
from docling.datamodel.pipeline_options import EasyOcrOptions
pipeline_options.ocr_options = EasyOcrOptions(lang=["en", "de"])
```

Prefetch recognition models for offline use: `docling-tools models download easyocr --easyocr-lang iso:zh-Hans --easyocr-lang ja`.

## RapidOCR

Default OCR in `docling-slim[standard]`. Torch backend supports GPU.

```python
from docling.datamodel.pipeline_options import RapidOcrOptions
pipeline_options.ocr_options = RapidOcrOptions()   # configure via --ocr-option on CLI
```

## Nemotron OCR

Linux x86_64, Python 3.12, CUDA 13 only:

```bash
uv pip install docling "docling-slim[feat-ocr-nemotron]" \
  --extra-index-url https://download.pytorch.org/whl/cu130 \
  --index-strategy unsafe-best-match
```

## CLI usage

```bash
docling --ocr document.pdf                          # OCR on (default true)
docling --no-ocr document.pdf                       # disable
docling --ocr-engine tesseract document.pdf         # specific engine
docling --ocr-mode full_page document.pdf           # replaces deprecated --force-ocr
docling --ocr-option model_size=tiny document.pdf   # repeatable engine option (JSON-parsed when possible)
```

Run `docling options ocr <engine>` to list an engine's option keys.
