# Enrichments

Enrichment models add extra processing steps for specific document components. They are disabled by default to save processing time; each enabled enrichment adds model inference time, so enable only what you need.

## Code understanding

Extracts programming language and parses code blocks.

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.do_code_enrichment = True
# CLI: docling --enrich-code FILE
```

Model: `CodeFormula`.

## Formula understanding

Extracts LaTeX representation from equation formulas.

```python
pipeline_options.do_formula_enrichment = True
# CLI: docling --enrich-formula FILE
```

Model: `CodeFormula`.

## Picture classification

Classifies images into categories (chart types, diagrams, logos, signatures, etc.). Requires generating picture images first.

```python
pipeline_options.generate_picture_images = True  # required!
pipeline_options.images_scale = 2                # higher resolution
pipeline_options.do_picture_classification = True
# CLI: docling --enrich-picture-classes FILE
```

## Picture description

Generates natural language captions for images using vision models.

### Local models

```python
from docling.datamodel.pipeline_options import granite_picture_description, smolvlm_picture_description

pipeline_options.do_picture_description = True
pipeline_options.picture_description_options = granite_picture_description  # or smolvlm_picture_description
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
)
```

CLI: `docling --enrich-picture-description FILE`

## Chart extraction

Extracts structured data from bar charts, pie charts, and line plots.

```python
pipeline_options.do_chart_extraction = True
pipeline_options.generate_picture_images = True
# CLI: docling --enrich-chart-extraction FILE
```

For VLM pipelines, chart enrichment can be enabled on the CLI, e.g.:

```bash
docling --from image --to dclx IMAGE.png --vlm-model mineru2_pro --enrich-chart-extraction
```

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

## Developing custom enrichments

See examples in the Docling repository: `docs/examples/develop_picture_enrichment.py`, `docs/examples/develop_formula_understanding.py`. Custom enrichment models implement the enrichment interface and register via the plugin system.
