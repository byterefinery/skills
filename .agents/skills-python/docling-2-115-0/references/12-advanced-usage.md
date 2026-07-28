# Advanced Usage

## Binary PDF streams

Convert from in-memory binary data instead of files:

```python
from io import BytesIO
from docling.datamodel.base_models import DocumentStream
from docling.document_converter import DocumentConverter

buf = BytesIO(binary_pdf_data)
source = DocumentStream(name="my_doc.pdf", stream=buf)

converter = DocumentConverter()
result = converter.convert(source)
```

## Offline / air-gapped mode

### Step 1: Prefetch models

```bash
docling-tools models download
docling-tools models download -o /local/path/to/models
```

For EasyOCR languages:

```bash
docling-tools models download easyocr --easyocr-lang en --easyocr-lang de
```

For arbitrary HuggingFace models:

```bash
docling-tools models download-hf-repo ds4sd/SmolDocling-256M-preview
```

### Step 2: Point to cached models

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions(artifacts_path="/local/path/to/models")

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

Or via environment variable:

```bash
export DOCLING_ARTIFACTS_PATH="/local/path/to/models"
python my_script.py
```

Or via CLI:

```bash
docling --artifacts-path="/local/path/to/models" document.pdf
```

## Remote services

Some features (remote vision models, cloud APIs) require explicit opt-in:

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions(enable_remote_services=True)
```

Without this flag, remote service calls raise `OperationNotAllowed()`.

### Remote picture description

```python
from docling.datamodel.pipeline_options import PictureDescriptionApiOptions

pipeline_options.enable_remote_services = True

pipeline_options.picture_description_options = PictureDescriptionApiOptions(
    url="https://api.example.com/v1/chat/completions",
    headers={"Authorization": "Bearer YOUR_KEY"},
    params={"model": "vision-model", "max_completion_tokens": 200},
    prompt="Describe the image.",
    timeout=90,
)
```

### List of features requiring `enable_remote_services=True`

- `PictureDescriptionApiOptions` — remote vision model API calls
- VLM pipeline with remote inference server
- Any model that sends data to external services

## Resource limits

```python
result = converter.convert(
    source,
    max_num_pages=100,       # reject documents over 100 pages
    max_file_size=20971520,  # reject files over 20MB (20 * 1024 * 1024)
)
```

## Confidence scores

Assess conversion quality:

```python
result = converter.convert("document.pdf")

# Document-level grades
print(result.confidence.mean_grade)  # EXCELLENT, GOOD, FAIR, POOR
print(result.confidence.low_grade)   # worst-performing area

# Component scores
print(result.confidence.layout_score)
print(result.confidence.ocr_score)
print(result.confidence.parse_score)

# Page-level
for page in result.confidence.pages:
    print(f"Page {page.page_no}: {page.mean_grade} (layout: {page.layout_score})")
```

**Focus on quality grades** (`mean_grade`, `low_grade`) rather than numerical scores. Scores are informational and may change.

## External plugins

Enable third-party plugins:

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.allow_external_plugins = True
pipeline_options.ocr_options = YourPluginOcrOptions()
```

CLI:

```bash
docling --allow-external-plugins --ocr-engine plugin_name document.pdf
docling --show-external-plugins  # list available plugins
```

## HTTP headers for URL sources

```python
from requests import Session

converter = DocumentConverter()
result = converter.convert(
    "https://private.example.com/doc.pdf",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
)
```

CLI:

```bash
docling --headers '{"Authorization": "Bearer YOUR_TOKEN"}' https://private.example.com/doc.pdf
```

## Batch conversion with error resilience

```python
results = converter.convert_all(
    ["file1.pdf", "file2.pdf", "file3.pdf"],
    raises_on_error=False,  # don't abort on first error
)

success_count = 0
for result in results:
    if result.status.name == "SUCCESS":
        success_count += 1
        md = result.document.export_to_markdown()
    elif result.status.name == "FAILED":
        print(f"Failed: {result.input.file} — {result.error_message}")
    elif result.status.name == "SKIPPED":
        print(f"Skipped: {result.input.file}")
```

## Programmatic model download

```python
from docling.utils.model_downloader import download_models

download_models()
```

## PDF password-protected documents

```python
result = converter.convert("protected.pdf", pdf_password="secret")
```

CLI:

```bash
docling --pdf-password "secret" protected.pdf
```

## Concurrency settings

```python
from docling.datamodel.settings import settings

# Increase page batch size for GPU processing
settings.perf.page_batch_size = 64  # default: 4
```

## Debug visualizations

```bash
docling --debug-visualize-cells document.pdf    # PDF text cells
docling --debug-visualize-ocr document.pdf      # OCR cells
docling --debug-visualize-layout document.pdf   # layout clusters
docling --debug-visualize-tables document.pdf   # table cells
docling --show-layout document.pdf              # bounding boxes on page images
```

## Common environment variables

| Variable | Purpose |
|----------|---------|
| `DOCLING_ARTIFACTS_PATH` | Local model artifacts directory |
| `OMP_NUM_THREADS` | CPU thread count (default: 4) |
| `DOCLING_CUDA_USE_FLASH_ATTENTION2` | Enable Flash Attention 2 (set to `1`) |
| `TESSDATA_PREFIX` | Tesseract language data path |
| `HF_HOME` | HuggingFace cache directory |
