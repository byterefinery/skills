# Export & serialization

Docling exports the `DoclingDocument` to multiple formats. Call export methods on the document, or use the CLI `--to` flag.

## Output formats

| Format | Notes |
|--------|-------|
| Markdown | Default CLI output; table spans flattened |
| JSON | Lossless serialization of the DoclingDocument |
| HTML | Preserves `rowspan`/`colspan`; image embedding or referencing |
| DocLang XML | CLI name `doclang`; OTSL encodes spans |
| DocTags | Layout-aware markup; spans preserved |
| Plain text | No Markdown markers |
| WebVTT | Timed text (audio/video) |
| LaTeX | Standalone `.tex`; images emitted as placeholders, spans flattened |
| DocLang archive | CLI name `dclx`; zipped with page images |
| Chunks (JSONL) | RAG output via chunkers |

## Image export mode

For image-capable outputs (JSON, YAML, HTML, Markdown), `--image-export-mode` / `image_mode`:

- `placeholder` — only the position of the image is marked
- `embedded` — image embedded as base64 (default)
- `referenced` — image exported as PNG and referenced from the document

```python
md = doc.export_to_markdown(image_mode="referenced")
# CLI: docling --image-export-mode referenced document.pdf
```

Text, DocTags, and WebVTT outputs do not export images.

## Table cell spans

How table cell spanning (rowspan/colspan) is handled per format:

| Format | Span handling |
|--------|--------------|
| JSON | Preserved — full `TableData` with all span fields |
| DocLang XML | Preserved — OTSL tokens |
| DocTags | Preserved — OTSL natively encodes spans |
| HTML | Preserved — native `rowspan`/`colspan` attributes |
| Markdown | Flattened — cell text at origin position only |
| LaTeX | Flattened — no `\multirow`/`\multicolumn` |
| WebVTT | N/A — tables not serialized |

**Rule:** if downstream workflow depends on accurate table structure (merged header cells), prefer `export_to_html()` or `export_to_dict()` over `export_to_markdown()`.

## CLI output formats

```bash
docling --to md document.pdf          # Markdown (default)
docling --to json document.pdf        # JSON
docling --to html document.pdf        # HTML
docling --to text document.pdf        # Plain text
docling --to doctags document.pdf     # DocTags
docling --to doclang document.pdf     # DocLang XML
docling --to dclx document.pdf        # DocLang archive
docling --to vtt recording.mp3        # WebVTT (audio/video)
docling --to md --to json document.pdf  # multiple outputs (repeatable)

# Chunks for RAG
docling --to chunks --chunks-type hybrid --chunks-max-tokens 512 document.pdf
```

Chunk types: `hybrid`, `hierarchical`. `--chunks-tokenizer` defaults to `sentence-transformers/all-MiniLM-L6-v2`.

## Custom serializers

Docling defines a serialization class hierarchy (`BaseDocSerializer`, component-level `BaseTextSerializer`/`BaseTableSerializer`/`BasePictureSerializer`, and `BaseSerializerProvider`). Override component serializers by subclassing and passing them to the document serializer.
