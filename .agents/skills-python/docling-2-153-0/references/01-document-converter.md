# DocumentConverter

`DocumentConverter` is the main entry point. It maps each input format to a backend (parses the file) plus a pipeline (orchestrates model stages), and returns a `ConversionResult`.

## Basic conversion

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document.pdf")   # local path or URL
doc = result.document                        # DoclingDocument
print(doc.export_to_markdown())
```

`convert()` accepts a file path, a directory, a URL, or a `DocumentStream`. It returns a `ConversionResult`, not the document directly.

## ConversionResult

- `.document` — the `DoclingDocument` (use this; the v1 legacy representation is removed)
- `.status` — a `ConversionStatus` (`SUCCESS`, `FAILED`, `SKIPPED`); check before assuming success
- `.error_message` — populated on failure
- `.input` — the resolved input (e.g. `.file`)
- `.confidence` — quality grades and component scores

## Format options

The converter holds a default format-to-backend/pipeline mapping that is parametrizable via `format_options`, keyed by `InputFormat`:

```python
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions()
converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)
```

Format option classes include `PdfFormatOption`, `ImageFormatOption`, `WordFormatOption`, `PowerpointFormatOption`, `MarkdownFormatOption`, `AsciiDocFormatOption`, `HTMLFormatOption`, `AfpFormatOption`, plus `AudioFormatOption` / `VideoFormatOption` for media. Each accepts `pipeline_cls` and `pipeline_options`.

Using the wrong `InputFormat` enum causes silent fallback to defaults — key options by the correct format enum.

## Batch conversion

```python
results = converter.convert_all(
    ["file1.pdf", "file2.pdf"],
    raises_on_error=False,   # default True aborts on first error
)
for result in results:
    if result.status.name == "SUCCESS":
        md = result.document.export_to_markdown()
    elif result.status.name == "FAILED":
        print(result.input.file, result.error_message)
```

## Resource limits and options to `convert()`

- `max_num_pages` — reject documents over N pages
- `max_file_size` — reject files over N bytes
- `pdf_password` — open password-protected PDFs
- `headers` — HTTP headers for URL sources (e.g. auth)

```python
result = converter.convert("protected.pdf", pdf_password="secret", max_num_pages=100)
```

## SimplePipeline vs StandardPdfPipeline vs VlmPipeline

Declarative formats (DOCX, PPTX, HTML) use `SimplePipeline` by default (no ML models). PDF and images use `StandardPdfPipeline` (layout + table structure + OCR) or `VlmPipeline` for end-to-end vision-language conversion. Select via `pipeline_cls` in the format option.
