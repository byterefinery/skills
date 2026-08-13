# Generation Tools

## Overview

Generation tools create and build Docling documents programmatically. The workflow follows a stack-based model: create a document, then iteratively add structural elements (title, headings, paragraphs, lists, tables). The internal stack tracks the current context for proper nesting.

## Document Lifecycle

1. **Create** — `create_new_docling_document(prompt)` creates an empty document and returns a `document_key`
2. **Build** — Add elements using the generation tools (title, headings, paragraphs, lists, tables)
3. **Inspect** — `export_docling_document_to_markdown(document_key)` to check current content
4. **Save** — `save_docling_document(document_key)` writes to disk in Markdown and JSON

## Tools

### `create_new_docling_document`

Create a new empty document.

**Parameters:**
- `prompt` (str) — prompt text describing the document (stored as furniture content)

**Returns:** `NewDoclingDocumentOutput` with `document_key` and `prompt`

**Behavior:** Creates a `DoclingDocument` named "Generated Document", adds the prompt as furniture text, pushes the item onto the internal stack, and assigns a UUID-based key.

### `add_title_to_docling_document`

Add or update the document title.

**Parameters:**
- `document_key` (str) — cache key of the document
- `title` (str) — title text

**Returns:** `UpdateDocumentOutput` with `document_key`

**Constraint:** Cannot be called while a list is open. Close the list first with `close_list_in_docling_document`.

### `add_section_heading_to_docling_document`

Add a section heading at a specific level.

**Parameters:**
- `document_key` (str) — cache key of the document
- `section_heading` (str) — heading text
- `section_level` (int) — heading level (1 = highest/H1, 2 = H2, etc.)

**Returns:** `UpdateDocumentOutput` with `document_key`

**Constraint:** Cannot be called while a list is open.

### `add_paragraph_to_docling_document`

Add a paragraph of text.

**Parameters:**
- `document_key` (str) — cache key of the document
- `paragraph` (str) — paragraph text

**Returns:** `UpdateDocumentOutput` with `document_key`

**Constraint:** Cannot be called while a list is open.

### `open_list_in_docling_document`

Open a new list group.

**Parameters:**
- `document_key` (str) — cache key of the document

**Returns:** `UpdateDocumentOutput` with `document_key`

**Behavior:** Creates a `GroupItem` with label `LIST` and pushes it onto the stack. Subsequent `add_list_items` calls add items to this list. Nested lists are created by calling `open_list` again while a list is already open.

### `add_list_items_to_list_in_docling_document`

Add items to the currently open list.

**Parameters:**
- `document_key` (str) — cache key of the document
- `list_items` (list[ListItem]) — list of `{list_item_text, list_marker_text}` objects

**Returns:** `UpdateDocumentOutput` with `document_key`

**Constraint:** A list must be open. The parent on the stack must be a `LIST` or `ORDERED_LIST` group.

### `close_list_in_docling_document`

Close the currently open list.

**Parameters:**
- `document_key` (str) — cache key of the document

**Returns:** `UpdateDocumentOutput` with `document_key`

**Behavior:** Pops the top item from the stack. Requires stack size > 1.

### `add_table_in_html_format_to_docling_document`

Add a table from an HTML string.

**Parameters:**
- `document_key` (str) — cache key of the document
- `html_table` (str) — HTML `<table>` string (supports `colspan`, `rowspan`)
- `table_captions` (list[str] | None) — optional caption strings
- `table_footnotes` (list[str] | None) — optional footnote strings

**Returns:** `UpdateDocumentOutput` with `document_key`

**Behavior:** Wraps the HTML in `<html><body>...</body></html>`, converts via `DocumentConverter` with HTML format, extracts the first table, and adds it to the document. Captions and footnotes are added as text items with appropriate labels.

**Requirement:** Needs `docling-mcp[local]` extra (uses `DocumentConverter` internally).

### `export_docling_document_to_markdown`

Export the document to Markdown format.

**Parameters:**
- `document_key` (str) — cache key of the document
- `max_size` (int | None) — maximum number of characters to return (optional)

**Returns:** `ExportDocumentMarkdownOutput` with `document_key` and `markdown`

**Behavior:** Calls `doc.export_to_markdown()`. If `max_size` is set, truncates the output.

### `save_docling_document`

Save the document to disk.

**Parameters:**
- `document_key` (str) — cache key of the document

**Returns:** `SaveDocumentOutput` with:
- `md_file` (str) — path to the saved Markdown file
- `json_file` (str) — path to the saved JSON file

**Behavior:** Saves both Markdown (text width 72) and JSON versions in the cache directory. Filenames are `{document_key}.md` and `{document_key}.json`.

### `page_thumbnail`

Generate a thumbnail image for a specific page.

**Parameters:**
- `document_key` (str) — cache key of the document
- `page_no` (int) — page number (1-indexed, default: 1)
- `size` (int) — thumbnail width in pixels (default: 300)

**Returns:** `MCPImage` — the thumbnail image

**Requirement:** Server must be started with `DOCLING_MCP_KEEP_IMAGES=true`.

## Document Generation Pattern

```
1. create_new_docling_document("Write about X")
   → document_key = "abc123..."

2. add_title_to_docling_document(abc123, "Title")
3. add_section_heading_to_docling_document(abc123, "Introduction", 1)
4. add_paragraph_to_docling_document(abc123, "Intro text...")

5. open_list_in_docling_document(abc123)
6. add_list_items_to_list_in_docling_document(abc123, [{"list_item_text": "Item 1", "list_marker_text": "-"}])
7. close_list_in_docling_document(abc123)

8. add_section_heading_to_docling_document(abc123, "Conclusion", 1)
9. add_paragraph_to_docling_document(abc123, "Conclusion text...")

10. export_docling_document_to_markdown(abc123) — check progress
11. save_docling_document(abc123) — save to disk
```

## Stack Management

The generation tools maintain an internal stack (`local_stack_cache`) that tracks the current context:

- After `create_new_docling_document`, the stack has one item (the prompt text)
- `add_title`, `add_section_heading`, `add_paragraph` replace the top of the stack
- `open_list` pushes a new `GroupItem` onto the stack
- `close_list` pops the top item from the stack
- Adding content while a list is open raises an error — close the list first

## Gotchas

- **Lists must be closed before adding headings/paragraphs** — the tools enforce this. Call `close_list_in_docling_document` before `add_section_heading` or `add_paragraph`.
- **Nested lists:** open another list while one is already open. Close in reverse order (innermost first).
- **`add_table_in_html_format_to_docling_document` requires `[local]`** — it uses `DocumentConverter` for HTML parsing, which is only available with the local extra.
- **`page_thumbnail` needs `DOCLING_MCP_KEEP_IMAGES=true`** — page images are not generated by default.
- **`save_docling_document` writes to cache dir** — the output path is in the Docling cache directory, not a user-specified location.
- **`export_docling_document_to_markdown` can be large** — use `max_size` to limit output for large documents.
- **Table HTML must be valid** — the tool wraps the HTML in `<html><body>` tags. Malformed HTML causes a parse error.
- **`list_marker_text` is the bullet/number** — e.g., `"-"` for unordered, `"1."` for ordered lists.
