# Generation tools (docling-mcp 3.5.1)

Create and edit `DoclingDocument` objects, export to Markdown, save to disk, and generate page thumbnails.

## Tools

### create_new_docling_document(prompt)

Create a new document from a prompt and return its `document_key`.

### export_docling_document_to_markdown(document_key, max_size=None, page_no=None)

Export a cached document to Markdown.
- `max_size` — maximum number of characters to return (truncates output).
- `page_no` — 1-based page number to export; omit to export all pages (added in 3.4.0).

Image rendering follows `DOCLING_MCP_IMAGE_EXPORT_MODE`.

### save_docling_document(document_key, page_no=None)

Save a cached document to disk in both Markdown and JSON formats, returning the file paths.
- `page_no` — when set, only that page is written to a page-specific markdown file (`{document_key}-p{page_no}.md`); the JSON file always contains the full document (added in 3.4.0).
- Files are written to the Docling cache directory, not a user-specified path.

### get_page_thumbnail(document_key, page_no=1, size=300)

Generate a thumbnail image for the requested page. `page_no` is 1-based; `size` is the width in pixels (default 300). Requires `DOCLING_MCP_KEEP_IMAGES=true` at server start — otherwise raises a ValueError because the document has no page images.

### add_title_to_docling_document(document_key, title)

Add or update the document title.

### add_section_heading_to_docling_document(document_key, section_heading, section_level)

Add a section heading at the given level.

### add_paragraph_to_docling_document(document_key, paragraph)

Add a paragraph.

### open_list_in_docling_document(document_key)

Open a new list group. If a list is already open, the new list nests inside it (fixed in 3.5.1).

### close_list_in_docling_document(document_key)

Close the currently open list group. Must be called before adding headings or paragraphs; the tools enforce stack consistency and raise errors otherwise.

### add_list_items_to_list_in_docling_document(document_key, list_items)

Add items to the currently open list.

### add_table_in_html_format_to_docling_document(document_key, html_table, table_captions=None, table_footnotes=None)

Add a table from an HTML string, with optional captions and footnotes.

## Typical generation flow

1. `create_new_docling_document`
2. `add_title_to_docling_document`
3. Iterate: `add_section_heading_to_docling_document`, `add_paragraph_to_docling_document`; for lists, `open_list_in_docling_document` → `add_list_items_to_list_in_docling_document` → `close_list_in_docling_document` (nest by repeating the open/add/close sequence)
4. Check progress with `export_docling_document_to_markdown`
5. `save_docling_document` and return the file path
