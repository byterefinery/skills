# Export & Serialization

`DoclingDocument` provides multiple export methods. Each serializer makes format-specific trade-offs.

## Export methods

```python
doc = result.document

# Markdown (default CLI output)
md = doc.export_to_markdown()

# JSON (lossless)
json_str = json.dumps(doc.export_to_dict())

# HTML
html = doc.export_to_html()

# Plain text (no markdown markers)
text = doc.export_to_text()

# DocTags (structured markup for document understanding)
doctags = doc.export_to_doctags()

# WebVTT (timed text, for audio/video)
vtt = doc.save_as_vtt("output.vtt")
```

## Image export modes

For formats that support images (Markdown, JSON, HTML):

| Mode | Behavior |
|------|----------|
| `placeholder` | Only marks image position in output |
| `embedded` | Embeds image as base64 string (default) |
| `referenced` | Exports image as separate PNG file, references from document |

```python
# Via export_to_markdown
md = doc.export_to_markdown(image_mode="referenced")

# Via CLI
docling --image-export-mode referenced document.pdf
```

## Table cell spans

How table cell spanning (rowspan/colspan) is handled per format:

| Format | Span handling |
|--------|--------------|
| JSON | **Preserved** — full `TableData` with all span fields |
| DocLang XML | **Preserved** — OTSL with `LCEL`/`UCEL`/`XCEL` tokens |
| DocTags | **Preserved** — OTSL natively encodes spans |
| HTML | **Preserved** — native `rowspan`/`colspan` attributes |
| Markdown | **Flattened** — cell text at origin position only, other positions empty |
| LaTeX | **Flattened** — no `\multirow`/`\multicolumn` |
| WebVTT | **N/A** — tables not serialized |

**Rule:** If downstream workflow depends on accurate table structure (e.g. merged header cells), prefer `export_to_html()` or `export_to_dict()` over `export_to_markdown()`.

## Custom serializers

Docling defines a serialization class hierarchy:

- `BaseDocSerializer` — document-level serialization
- `BaseTextSerializer`, `BaseTableSerializer`, `BasePictureSerializer` — component-level
- `BaseSerializerProvider` — strategy abstraction

```python
from docling_core.transforms.serializer.markdown import MarkdownDocSerializer

serializer = MarkdownDocSerializer(doc)
text = serializer.serialize()
```

Override component serializers by subclassing (e.g., `BaseTableSerializer`) and passing to the document serializer.

## CLI output formats

```bash
docling --to md document.pdf          # Markdown (default)
docling --to json document.pdf        # JSON
docling --to yaml document.pdf        # YAML
docling --to html document.pdf        # HTML
docling --to html_split_page document.pdf  # HTML, one file per page
docling --to text document.pdf        # Plain text
docling --to doctags document.pdf     # DocTags
docling --to vtt audio.mp3            # WebVTT (audio/video)
docling --to doclang document.pdf     # DocLang XML
docling --to dclx document.pdf        # DocLang archive (zipped with images)

# Multiple outputs
docling --to md --to json document.pdf

# Chunks for RAG
docling --to chunks --chunks-type hybrid --chunks-max-tokens 512 document.pdf
```

## DocLang format

DocLang is an XML schema for document representation:

```bash
# XML serialization
docling --to doclang document.pdf

# Zipped archive with page images
docling --to dclx document.pdf
```

DocLang supports: `.dclg`, `.dclg.xml`, generic `.xml` with `<doclang>` root, and `.dclx` archives.

## Chunks output (JSONL)

For RAG pipelines, the CLI can output chunked documents:

```bash
docling --to chunks \
  --chunks-type hybrid \
  --chunks-max-tokens 512 \
  --chunks-tokenizer cl100k_base \
  document.pdf
```

Chunk types: `hybrid`, `line`, `hierarchical`.
