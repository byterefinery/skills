# Advanced Usage

## Binary PDF streams

Convert from in-memory binary data instead of files:

```python
from io import BytesIO
from docling.datamodel.base_models import DocumentStream
from docling.document_converter import DocumentConverter

source = DocumentStream(name="my_doc.pdf", stream=BytesIO(binary_pdf_data))
result = DocumentConverter().convert(source)
```

## Offline / air-gapped mode

Prefetch models, then point Docling at the cached dir:

```bash
docling-tools models download -o /local/path/to/models
```

```python
pipeline_options = PdfPipelineOptions(artifacts_path="/local/path/to/models")
```

Or via environment variable `DOCLING_ARTIFACTS_PATH`, or CLI `--artifacts-path`. Programmatic: `docling.utils.model_downloader.download_models()`.

## Remote services

Remote OCR/VLM/API engines require explicit opt-in; otherwise Docling raises `OperationNotAllowed()`:

```python
pipeline_options = PdfPipelineOptions(enable_remote_services=True)
```

Features that require `enable_remote_services=True` include `PictureDescriptionApiOptions`, `KserveV2OcrOptions`, KServe v2 object-detection/image-classification engine options, `ApiVlmEngineOptions`, and `ApiVlmOptions`.

## Resource limits

```python
result = converter.convert(
    source,
    max_num_pages=100,       # reject documents over 100 pages
    max_file_size=20971520,  # reject files over ~20MB
)
```

## Confidence scores

Assess conversion quality via `result.confidence`:

```python
print(result.confidence.mean_grade)   # EXCELLENT / GOOD / FAIR / POOR
print(result.confidence.low_grade)    # worst-performing area
# component scores: layout_score, ocr_score, parse_score (informational)
```

**Focus on quality grades** (`mean_grade`, `low_grade`) rather than numerical scores, which are informational and may change.

## External plugins

Enable third-party plugins (CLI: `--allow-external-plugins`; list with `--show-external-plugins`). Plugin engines appear in `--layout-engine` / `--table-structure-engine` / `--ocr-engine` choices only when allowed.

## HTTP headers for URL sources

```python
result = converter.convert("https://private.example.com/doc.pdf",
                           headers={"Authorization": "Bearer TOKEN"})
# CLI: docling --headers '{"Authorization": "Bearer TOKEN"}' <url>
```

## Batch conversion with error resilience

```python
results = converter.convert_all(["a.pdf", "b.pdf"], raises_on_error=False)
for result in results:
    if result.status.name == "SUCCESS":
        md = result.document.export_to_markdown()
    elif result.status.name == "FAILED":
        print(result.input.file, result.error_message)
```

## PDF password-protected documents

```python
result = converter.convert("protected.pdf", pdf_password="secret")
# CLI: docling --pdf-password "secret" protected.pdf
```

## Common environment variables

| Variable | Purpose |
|----------|---------|
| `DOCLING_ARTIFACTS_PATH` | Local model artifacts directory |
| `OMP_NUM_THREADS` | CPU thread count |
| `TESSDATA_PREFIX` | Tesseract language data path |
| `HF_HOME` | HuggingFace cache directory |
