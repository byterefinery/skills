# Install, extras, and backends (camelot-py 2.2.0)

## Installation

```bash
pip install "camelot-py"                    # PyPI
conda install -c conda-forge camelot-py     # conda-forge
uvx camelot-py lattice --output t.csv doc.pdf   # ad-hoc CLI, no install
# from source:
git clone https://github.com/camelot-dev/camelot && pip install ./camelot
```

Requires Python 3.11+. Camelot depends on `opencv-python-headless` and uses `pdfium` (pypdfium2) as the default image conversion backend (since v1.0.0).

## Optional extras

| Extra | Installs | Used for |
|---|---|---|
| `[plot]` | matplotlib | Visual debugging via `camelot.plot()` / `-plot` |
| `[ghostscript]` | ghostscript Python package | Optional ghostscript image backend (you must still install Ghostscript itself) |
| `[ml]` | torch, transformers, timm | Neural `flavor='ml'` (Table Transformer) for borderless tables |
| `[ocr]` | rapidocr-onnxruntime | OCR text source that `flavor='ml'` uses on scanned/image-only PDFs |

## OpenCV conflict (headless vs full)

Camelot needs `opencv-python-headless`. If the full `opencv-python` package is also installed, both ship the same `cv2` and shadow each other in site-packages → broken `import cv2` at runtime. Fix:

```bash
pip uninstall opencv-python
pip install camelot-py
```

The `[ocr]` extra makes this worse: `rapidocr-onnxruntime` hard-requires full `opencv-python`, so `pip install "camelot-py[ocr]"` installs **both** builds. RapidOCR only ever does `import cv2`, which the headless build satisfies, so drop the full build:

- **uv** — override in your project's `pyproject.toml`:
  ```toml
  [tool.uv]
  override-dependencies = ["opencv-python ; sys_platform == 'never'"]
  ```
  or ad hoc: `echo 'opencv-python ; sys_platform == "never"' > overrides.txt && uv pip install --override overrides.txt "camelot-py[ocr]"`
- **pdm** — `[tool.pdm.resolution] excludes = ["opencv-python"]`
- **pip** (no override mechanism) — install RapidOCR without deps and supply them yourself:
  ```bash
  pip install "camelot-py"
  pip install --no-deps rapidocr-onnxruntime
  pip install pyclipper "numpy<3" six "shapely!=2.0.4" PyYAML Pillow "onnxruntime>=1.7.0" tqdm
  ```

If both are already installed, reinstall cleanly (removing one deletes `cv2` files the other needs):

```bash
pip uninstall -y opencv-python opencv-python-headless
pip install opencv-python-headless
```

## Image conversion backends (lattice)

The lattice flavor renders PDF pages to images for OpenCV line detection. Choose with `backend=`:

```python
camelot.read_pdf(filename, backend="pdfium")        # default
camelot.read_pdf(filename, backend="ghostscript")   # needs [ghostscript] + system Ghostscript
# custom backend: any object with convert(pdf_path, png_path)
class ConversionBackend:
    def convert(self, pdf_path, png_path): ...
camelot.read_pdf(filename, backend=ConversionBackend())
```

`use_fallback=True` (default) falls back to another backend if the requested one is unavailable.

## Scanned / image-only PDFs → OCR first

Camelot reads the PDF's text operators; an image-only PDF has none and yields zero tables. Recommended workflow: add a text layer with [OCRmyPDF](https://ocrmypdf.readthedocs.io/), then run Camelot.

```bash
pipx install ocrmypdf
ocrmypdf scan.pdf scan-ocr.pdf
camelot lattice --output tables.csv scan-ocr.pdf
```

Python pipeline:

```python
import subprocess, camelot
subprocess.run(["ocrmypdf", "scan.pdf", "scan-ocr.pdf"], check=True)
tables = camelot.read_pdf("scan-ocr.pdf", flavor="lattice")
```

Practical notes:

- **Mixed PDFs** (some text pages, some scanned): `ocrmypdf` skips pages that already have a text layer unless `--force-ocr`.
- **Non-English**: install the Tesseract language pack (e.g. `apt install tesseract-ocr-deu`) then `ocrmypdf -l deu scan.pdf out.pdf`.
- **Fuzzy scans**: `ocrmypdf --image-dpi 300 --redo-ocr` is a reasonable default.
- Ruled (lattice) tables survive OCR well; borderless (stream) tables depend heavily on per-cell text alignment — try `flavor="auto"` or `"hybrid"` and check `Table.parsing_report` (`confidence`).

Alternatively, `flavor='ml'` with the `[ocr]` extra reads scanned pages directly (model structure + OCR text), skipping the separate OCRmyPDF step.

Why OCR isn't built in: Tesseract is a heavyweight system dependency (binary + language packs) and OCR quality varies across versions; keeping it as a preprocessing step lets OCRmyPDF handle image concerns while Camelot focuses on text-to-table conversion.
