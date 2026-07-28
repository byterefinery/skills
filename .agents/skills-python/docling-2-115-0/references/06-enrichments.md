# Enrichments

Enrichment models add extra processing steps for specific document components. They are disabled by default to save processing time.

## Code understanding

Extracts programming language and parses code blocks.

```python
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

pipeline_options = PdfPipelineOptions()
pipeline_options.do_code_enrichment = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("document.pdf")
doc = result.document

for item, _ in doc.iterate_items():
    if hasattr(item, 'code_language'):
        print(f"Code block: language={item.code_language}")
```

CLI: `docling --enrich-code FILE`

Model: [`CodeFormula`](https://huggingface.co/ds4sd/CodeFormula)

## Formula understanding

Extracts LaTeX representation from equation formulas.

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.do_formula_enrichment = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("document.pdf")
doc = result.document

for item, _ in doc.iterate_items():
    if hasattr(item, 'label') and item.label == "formula":
        print(f"Formula: {item.text}")  # LaTeX representation
```

CLI: `docling --enrich-formula FILE`

Model: [`CodeFormula`](https://huggingface.co/ds4sd/CodeFormula)

## Picture classification

Classifies images into categories (chart types, diagrams, logos, signatures, etc.).

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.generate_picture_images = True  # required!
pipeline_options.images_scale = 2                 # higher resolution
pipeline_options.do_picture_classification = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("document.pdf")
doc = result.document

for item, _ in doc.iterate_items():
    if isinstance(item, PictureItem):
        for annotation in item.annotations:
            print(f"Picture class: {annotation.label}")
```

CLI: `docling --enrich-picture-classes FILE`

Model: [`DocumentFigureClassifier-v2.5`](https://huggingface.co/docling-project/DocumentFigureClassifier-v2.5)

## Picture description

Generates natural language captions for images using vision models.

### Local models

```python
from docling.datamodel.pipeline_options import granite_picture_description, smolvlm_picture_description

pipeline_options = PdfPipelineOptions()
pipeline_options.do_picture_description = True

# Granite Vision (2B)
pipeline_options.picture_description_options = granite_picture_description

# SmolVLM (256M) — lighter
pipeline_options.picture_description_options = smolvlm_picture_description
```

### Custom VLM

```python
from docling.datamodel.pipeline_options import PictureDescriptionVlmOptions

pipeline_options.picture_description_options = PictureDescriptionVlmOptions(
    repo_id="your-org/your-vlm",
    prompt="Describe the image in three sentences. Be concise and accurate.",
)
```

### Remote API

```python
from docling.datamodel.pipeline_options import PictureDescriptionApiOptions

pipeline_options.enable_remote_services = True  # required!

pipeline_options.picture_description_options = PictureDescriptionApiOptions(
    url="http://localhost:8000/v1/chat/completions",
    params={"model": "my-vision-model", "max_completion_tokens": 200},
    prompt="Describe the image in three sentences.",
    timeout=90,
    headers={"Authorization": "Bearer ..."},  # optional
    usage_response_key="usage",               # capture API usage metadata
)
```

CLI: `docling --enrich-picture-description FILE`

### Capturing API usage metadata

```python
# After conversion, access usage data from picture descriptions
for item, _ in doc.iterate_items():
    if isinstance(item, PictureItem):
        for ann in item.annotations:
            usage = ann.get_custom_part().get("docling__usage")
            if usage:
                print(f"API usage: {usage}")
```

## Chart extraction

Extracts structured data from bar charts, pie charts, and line plots.

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.do_chart_extraction = True
pipeline_options.generate_picture_images = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})
```

CLI: `docling --enrich-chart-extraction FILE`

## Enabling multiple enrichments

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.do_code_enrichment = True
pipeline_options.do_formula_enrichment = True
pipeline_options.do_picture_classification = True
pipeline_options.do_picture_description = True
pipeline_options.generate_picture_images = True
pipeline_options.images_scale = 2
```

Note: each enabled enrichment adds model inference time. Enable only what you need.

## Developing custom enrichments

See examples in the Docling repository:
- `examples/develop_picture_enrichment.py`
- `examples/develop_formula_understanding.py`

Custom enrichment models implement the enrichment interface and register via the plugin system.
