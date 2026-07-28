# DoclingDocument

`DoclingDocument` is the unified document representation. It is a Pydantic model defined in `docling_core.types.doc`.

## Structure

A `DoclingDocument` has two categories of fields:

### Content items (lists of `DocItem`)

- `texts` — all text items (`TextItem` base class): paragraphs, headings, equations, code, lists
- `tables` — all tables (`TableItem`), with structure annotations
- `pictures` — all pictures (`PictureItem`), with structure annotations
- `key_value_items` — key-value region items

### Content structure (tree)

- `body` — root node of the main document body tree
- `furniture` — root node for headers, footers, margins (non-body items)
- `groups` — container items (lists, chapters) that organize content items

Reading order is encoded in the `body` tree and child ordering within each node.

## Iteration

### Iterate all items in reading order

```python
from docling_core.types.doc import TextItem, TableItem, PictureItem

for item, level in doc.iterate_items():
    if isinstance(item, TextItem):
        print(f"[level={level}] {item.text[:80]}")
    elif isinstance(item, TableItem):
        print(f"Table with {item.data.num_rows} rows, {item.data.num_cols} cols")
    elif isinstance(item, PictureItem):
        print(f"Picture: {item.caption}")
```

### Print element tree

```python
doc.print_element_tree()
```

## Text items

`TextItem` is the base class for all text content. Subtypes:

- `Title` — document title
- `SectionHeader` — section heading
- `Paragraph` — body text
- `CodeItem` — code block (has `code_language` property when enriched)
- `Formula` — mathematical formula (has LaTeX when enriched)
- `ListItem` — list item
- `CheckedListItem` — checkbox item (has `checked` boolean)
- `PictureCaption` — caption for a picture
- `TableCaption` — caption for a table

### Accessing text

```python
for item, _ in doc.iterate_items():
    if isinstance(item, TextItem):
        print(item.text)
        print(item.label)  # "paragraph", "section_header", "code", etc.
```

## Tables

```python
import pandas as pd

for item, _ in doc.iterate_items():
    if isinstance(item, TableItem):
        # Export to DataFrame
        df = item.export_to_dataframe(doc=doc)
        print(df.to_markdown())

        # Access raw table data
        grid = item.data.grid  # 2D array of cells
        for row_idx, row in enumerate(grid):
            for col_idx, cell in enumerate(row):
                print(f"  [{row_idx},{col_idx}] {cell.text}")
                print(f"    row_span={cell.row_span}, col_span={cell.col_span}")
```

## Pictures

```python
for item, _ in doc.iterate_items():
    if isinstance(item, PictureItem):
        # Caption
        if item.caption:
            print(item.caption.text)

        # Annotations (from enrichment models)
        for annotation in item.annotations:
            print(f"Type: {annotation.label}, Confidence: {annotation.confidence}")

        # Picture description (from VLM captioning)
        if item.annotations:
            for ann in item.annotations:
                if hasattr(ann, 'caption'):
                    print(f"Description: {ann.caption}")
```

## Provenance

Each `DocItem` carries provenance information:

```python
for item, _ in doc.iterate_items():
    prov = item.prov
    if prov:
        print(f"Page: {prov.page_no}")
        print(f"Bounding box: {prov.bbox}")  # (x0, y0, x1, y1)
```

## Groups

Groups are structural containers that don't represent content themselves:

```python
for group in doc.groups:
    print(f"Group: {group.label}")  # "list", "chapter", etc.
    for child_ref in group.children:
        print(f"  Child: {child_ref}")  # JSON pointer to child item
```

## Hierarchy navigation

Items reference parents and children through JSON pointers:

- `item.parent` — JSON pointer to parent node
- `NodeItem.children` — list of JSON pointers to children

The `body` tree defines the reading order. The `furniture` tree contains headers, footers, and other non-body elements.

## Model validation

`DoclingDocument` is a Pydantic model:

```python
from docling_core.types.doc import DoclingDocument

# From dict
doc_dict = {"name": "my_doc", "body": {"children": []}}
doc = DoclingDocument.model_validate(doc_dict)

# To dict
doc_dict = doc.model_dump()
```

## Save and reload

```python
import json
from pathlib import Path

# Save
doc = result.document
Path("doc.json").write_text(json.dumps(doc.export_to_dict()))

# Reload
doc_dict = json.loads(Path("doc.json").read_text())
doc = DoclingDocument.model_validate(doc_dict)
```
