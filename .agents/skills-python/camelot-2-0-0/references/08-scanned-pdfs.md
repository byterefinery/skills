# Scanned PDFs Reference

Working with image-only (scanned) PDFs that lack a text layer.

## The Problem

Camelot extracts tables by reading the PDF's text operators — fonts, positions, kerning. For **image-only PDFs** (scanned pages, faxes, photos exported to PDF), there is no text to read. Every "table" is just pixels, and Camelot reports zero tables found.

## Solution 1: OCRmyPDF (Recommended)

Add a text layer to the scanned PDF, then run Camelot:

```bash
# Install once
pipx install ocrmypdf  # or: pip install ocrmypdf

# Add text layer
ocrmypdf scan.pdf scan-ocr.pdf

# Extract tables
camelot lattice --output tables.csv scan-ocr.pdf
```

Or as a Python pipeline:

```python
import subprocess
import camelot

subprocess.run(["ocrmypdf", "scan.pdf", "scan-ocr.pdf"], check=True)
tables = camelot.read_pdf("scan-ocr.pdf", flavor="lattice")
```

### OCRmyPDF Notes

- **Mixed PDFs** (some text, some scanned) — handled by default; OCRmyPDF skips pages with existing text layer unless `--force-ocr` is passed
- **Non-English** — install language packs: `apt install tesseract-ocr-deu` for German, then `ocrmypdf -l deu scan.pdf scan-ocr.pdf`
- **Table-friendly OCR** — higher resolution helps: `ocrmypdf --image-dpi 300 --redo-ocr`
- **Quality** — lattice-style ruled tables survive OCR well; stream-style borderless tables depend on Tesseract alignment quality

## Solution 2: flavor="ml" with OCR

Camelot's optional neural backend can handle scanned PDFs directly:

```bash
pip install "camelot-py[ml,ocr]"
```

```python
import camelot

# ML flavor with OCR for scanned PDFs
tables = camelot.read_pdf("scan.pdf", flavor="ml", ocr="auto")
```

### How It Works

1. Page is rendered to an image
2. Table Transformer detects table regions and structure
3. OCR reads text from the rendered image (no PDF text layer needed)
4. Cell text comes from OCR, structure from the model

### Trade-offs

- Works without a text layer (unique advantage)
- Slower than heuristic parsers (~1s/page with GPU)
- Pulls PyTorch + OCR dependencies (hundreds of MB)
- OCR quality varies by scan quality and language

## Why Isn't OCR Built Into Camelot?

Tesseract is a heavyweight system dependency (binary install + language packs, hundreds of MB). OCR quality is non-deterministic across versions. Keeping OCR as a separate preprocessing step lets OCRmyPDF handle OCR concerns (image preprocessing, language detection, page rotation) and Camelot focus on text-to-table conversion.

## Quality Assessment for OCR'd PDFs

After OCR + extraction, check `Table.parsing_report`:

```python
for table in tables:
    report = table.parsing_report
    print(f"Page {report['page']}: accuracy={report['accuracy']}, "
          f"whitespace={report['whitespace']}, confidence={report['confidence']}")
```

- `confidence >= 0.8` — reasonable first-cut threshold
- Low accuracy + high whitespace — OCR may have misread text; check scan quality
- Try `flavor="auto"` or `flavor="hybrid"` and compare confidence scores

## Common OCR Issues

| Issue | Fix |
|-------|-----|
| Blurry scans | `ocrmypdf --image-dpi 300 scan.pdf output.pdf` |
| Wrong language | `ocrmypdf -l deu scan.pdf output.pdf` |
| Rotated pages | `ocrmypdf --rotate-pages scan.pdf output.pdf` |
| Double OCR | `ocrmypdf --force-ocr scan.pdf output.pdf` |
| Low contrast | `ocrmypdf --clean scan.pdf output.pdf` |
