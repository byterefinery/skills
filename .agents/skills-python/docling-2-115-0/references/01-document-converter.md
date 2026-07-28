# DocumentConverter API

## Core API

`DocumentConverter` is the central entry point. It maps input formats to backends and pipelines, then produces `ConversionResult` objects containing `DoclingDocument` instances.

### Basic usage

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document.pdf")        # single file
doc = result.document                             # DoclingDocument
```

### Batch conversion

```python
results = converter.convert_all(
    ["file1.pdf", "file2.docx", "file3.html"],
    raises_on_error=False  # True by default: aborts on first error
)

for result in results:
    if result.status.name == "SUCCESS":
        print(result.document.export_to_markdown())
    else:
        print(f"Failed: {result.error_message}")
```

### From URLs

```python
result = converter.convert("https://arxiv.org/pdf/2408.09869")
```

### From binary streams

```python
from io import BytesIO
from docling.datamodel.base_models import DocumentStream

buf = BytesIO(binary_data)
source = DocumentStream(name="my_doc.pdf", stream=buf)
result = converter.convert(source)
```

## ConversionResult

The `ConversionResult` object contains:

- `document` — the `DoclingDocument` (use this, not `legacy_document`)
- `status` — `ConversionStatus` enum (SUCCESS, SKIPPED, FAILED)
- `error_message` — error details on failure
- `input` — input source info
- `confidence` — `ConfidenceReport` with quality grades
- `pages` — per-page conversion details

### Checking conversion quality

```python
result = converter.convert("document.pdf")

# Document-level quality
print(result.confidence.mean_grade)  # EXCELLENT, GOOD, FAIR, POOR
print(result.confidence.low_grade)   # worst-performing area

# Page-level details
for page in result.confidence.pages:
    print(f"Page {page.page_no}: {page.mean_grade}")
```

## Format Options

Configure per-format behavior via `format_options` dict keyed by `InputFormat`:

```python
from docling.datamodel.base_models import InputFormat
from docling.document_converter import (
    DocumentConverter, PdfFormatOption, WordFormatOption
)
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.pipeline.simple_pipeline import SimplePipeline

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True

converter = DocumentConverter(
    allowed_formats=[InputFormat.PDF, InputFormat.DOCX, InputFormat.HTML],
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,
        ),
        InputFormat.DOCX: WordFormatOption(
            pipeline_cls=SimplePipeline,  # default for office formats
        ),
    },
)
```

### Available format option types

| Format | Option class | Default pipeline |
|--------|-------------|-----------------|
| `InputFormat.PDF` | `PdfFormatOption` | `StandardPdfPipeline` |
| `InputFormat.IMAGE` | `ImageFormatOption` | `StandardPdfPipeline` |
| `InputFormat.DOCX` | `WordFormatOption` | `SimplePipeline` |
| `InputFormat.PPTX` | `PowerpointFormatOption` | `SimplePipeline` |
| `InputFormat.HTML` | `HTMLFormatOption` | `SimplePipeline` |
| `InputFormat.MARKDOWN` | `MarkdownFormatOption` | `SimplePipeline` |
| `InputFormat.AUDIO` | `AudioFormatOption` | `AsrPipeline` |
| `InputFormat.VIDEO` | `VideoFormatOption` | `VideoPipeline` |

### PDF backend selection

```python
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            backend=PyPdfiumDocumentBackend,  # alternative: docling_parse (default)
            pipeline_options=pipeline_options,
        )
    }
)
```

Available PDF backends: `docling_parse` (default), `pypdfium2`, `dlparse_v1`, `dlparse_v2`, `dlparse_v4`.

## Resource limits

```python
result = converter.convert(
    source,
    max_num_pages=100,      # reject documents over 100 pages
    max_file_size=20971520, # reject files over 20MB
    document_timeout=300.0, # timeout per document in seconds
)
```

## Accelerator options

```python
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions

accelerator_options = AcceleratorOptions(
    device=AcceleratorDevice.CUDA,  # or AUTO, CPU, MPS, XPU
)

converter = DocumentConverter(
    accelerator_options=accelerator_options,
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,
        )
    }
)
```

## Threading control

Set `OMP_NUM_THREADS` environment variable to control CPU thread count (default: 4):

```bash
export OMP_NUM_THREADS=8
```

Or in Python:

```python
import os
os.environ["OMP_NUM_THREADS"] = "8"
```
