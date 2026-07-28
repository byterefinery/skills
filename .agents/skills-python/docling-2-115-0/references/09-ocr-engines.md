# OCR Engines

Docling supports multiple OCR engines for processing scanned PDFs and images.

## Engine comparison

| Engine | Installation | Options class | Notes |
|--------|-------------|---------------|-------|
| EasyOCR | `docling[easyocr]` | `EasyOcrOptions` | GPU-accelerated, 80+ languages |
| Tesseract | System + `docling[tesserocr]` | `TesseractOcrOptions` | 100+ languages, linked via tesserocr |
| Tesseract CLI | System only | `TesseractCliOcrOptions` | No Python binding needed |
| RapidOCR | `docling[rapidocr]` | `RapidOcrOptions` | ONNX/OpenVINO/Paddle backends |
| macOS Vision | System (macOS) | `OcrMacOptions` | Native, excellent quality |
| Nemotron | `docling[feat-ocr-nemotron]` | `NemotronOcrOptions` | NVIDIA, Linux x86_64, CUDA 13 |
| SuryaOCR | Plugin | `SuryaOcrOptions` | Modern, good for complex layouts |
| OnnxTR | Plugin (`docling-ocr-onnxtr`) | `OnnxtrOcrOptions` | ONNX-based |
| Auto | Built-in | — | Automatically selects best available |

## Enabling OCR

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True  # enable OCR

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

## Tesseract

### Installation

```bash
# macOS (Homebrew)
brew install tesseract leptonica pkg-config
export TESSDATA_PREFIX=/opt/homebrew/share/tessdata/

# Debian-based
apt-get install tesseract-ocr tesseract-ocr-eng libtesseract-dev libleptonica-dev pkg-config
export TESSDATA_PREFIX=$(dpkg -L tesseract-ocr-eng | grep tessdata$)

# RHEL
dnf install tesseract tesseract-devel tesseract-langpack-eng tesseract-osd leptonica-devel
export TESSDATA_PREFIX=/usr/share/tesseract/tessdata/
```

### Usage

```python
from docling.datamodel.pipeline_options import TesseractOcrOptions

pipeline_options.do_ocr = True
pipeline_options.ocr_options = TesseractOcrOptions(lang=["eng", "deu"])
```

For linked usage (more efficient), install tesserocr:

```bash
pip uninstall tesserocr
pip install --no-binary :all: tesserocr
```

If installation fails, try the CLI variant:

```python
from docling.datamodel.pipeline_options import TesseractCliOcrOptions

pipeline_options.ocr_options = TesseractCliOcrOptions(lang=["eng"])
```

## EasyOCR

```bash
pip install "docling[easyocr]"
```

```python
from docling.datamodel.pipeline_options import EasyOcrOptions

pipeline_options.do_ocr = True
pipeline_options.ocr_options = EasyOcrOptions(lang=["en", "de", "fr", "es"])
```

Prefetch models for offline use:

```bash
docling-tools models download easyocr --easyocr-lang ch_sim --easyocr-lang ja
```

## RapidOCR

```bash
pip install "docling[rapidocr]"
```

```python
from docling.datamodel.pipeline_options import RapidOcrOptions

pipeline_options.do_ocr = True
pipeline_options.ocr_options = RapidOcrOptions(backend="torch")  # or "onnxruntime"
```

RapidOCR with torch backend supports GPU acceleration.

## macOS Vision (OcrMac)

Native macOS OCR, no extra installation needed:

```python
from docling.datamodel.pipeline_options import OcrMacOptions

pipeline_options.do_ocr = True
pipeline_options.ocr_options = OcrMacOptions()
```

## Nemotron OCR

NVIDIA's OCR engine, Linux x86_64 only, Python 3.12, CUDA 13:

```bash
pip install "docling[feat-ocr-nemotron]" \
  --extra-index-url https://download.pytorch.org/whl/cu130 \
  --index-strategy unsafe-best-match
```

```python
from docling.datamodel.pipeline_options import NemotronOcrOptions

pipeline_options.do_ocr = True
pipeline_options.ocr_options = NemotronOcrOptions()
```

## Language configuration

Each engine uses its own language codes:

```python
# EasyOCR: ISO 639-2 codes
pipeline_options.ocr_options = EasyOcrOptions(lang=["en", "de", "fr", "es"])

# Tesseract: tesseract language codes
pipeline_options.ocr_options = TesseractOcrOptions(lang=["eng", "deu", "fra", "spa"])
```

See each engine's documentation for supported language lists.

## CLI usage

```bash
# Auto-select OCR engine
docling --ocr document.pdf

# Specific engine
docling --ocr --ocr-engine tesseract document.pdf
docling --ocr --ocr-engine easyocr document.pdf
docling --ocr --ocr-engine rapidocr document.pdf

# With language
docling --ocr --ocr-engine tesseract --ocr-lang eng,deu document.pdf

# Force OCR (replace existing text layer)
docling --force-ocr document.pdf

# Page segmentation mode (Tesseract)
docling --ocr --ocr-engine tesseract --psm 6 document.pdf
```
