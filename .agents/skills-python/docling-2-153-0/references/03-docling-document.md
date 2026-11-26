# DoclingDocument

`DoclingDocument` is Docling v2's unified document representation, defined as a pydantic type in `docling_core.types.doc`. It expresses text, tables, pictures, hierarchy, layout (bounding boxes), and provenance.

## Top-level content fields

Content items:

- `texts` — all items with a text representation (paragraph, heading, equation, ...); base class `TextItem`
- `tables` — all tables (`TableItem`), can carry structure annotations
- `pictures` — all pictures (`PictureItem`), can carry structure annotations
- `key_value_items` — key-value items

All are lists of items inheriting from `DocItem`, referencing parents/children via JSON pointers.

Content structure:

- `body` — root node of the main document body tree; reading order is encoded by child ordering
- `furniture` — root node for items not in the body (headers, footers)
- `groups` — container items that group other content (e.g. a list, a chapter)

These hold `NodeItem` instances referencing children/parents through JSON pointers.

## Iterating items

```python
for item, level in doc.iterate_items():
    # item is the DocItem, level is its nesting depth
    ...
```

Check item type to access type-specific fields (e.g. `item.code_language` for code blocks, `item.annotations` for picture labels).

## Export methods

The document exposes export methods directly:

```python
doc.export_to_markdown()   # Markdown text
doc.export_to_dict()       # JSON-serializable dict (lossless)
# plus HTML, DocTags, plain text exports
```

For RAG, feed the `DoclingDocument` to a native chunker rather than re-chunking exported Markdown.

## Provenance and layout

Each item can carry provenance (which page/origin it came from) and bounding-box layout information when available, enabling visual debugging (`docling --show-layout`) and spatial reasoning downstream.
