# Manipulation tools (docling-mcp 3.5.1)

Inspect and edit a cached `DoclingDocument` by anchor reference.

## Tools

### get_overview_of_document_anchors(document_key)

Return the hierarchical structure of the document with anchor references. Anchors are JSON-pointer-like paths such as `#/texts/2`. Use this first to discover what items exist and their anchors.

### search_for_text_in_document_anchors(document_key, text)

Search for text or keywords in the document and return matching anchors.

### get_text_of_document_item_at_anchor(document_key, document_anchor)

Get the text of the item at a given anchor (e.g., `#/texts/2`).

### update_text_of_document_item_at_anchor(document_key, document_anchor, updated_text)

Update the text of the item at a given anchor.

### delete_document_items_at_anchors(document_key, document_anchors)

Delete items by a list of anchors.

## Anchor model

Anchors are stable, path-based references into the document's internal structure (texts, tables, etc.). The overview tool is the entry point: call it to learn the anchor layout, then use search/get/update/delete with those anchors within the same session. All tools require a `document_key` that is already present in the local cache.
