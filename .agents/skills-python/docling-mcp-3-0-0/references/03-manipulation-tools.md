# Manipulation Tools

## Overview

Manipulation tools inspect and modify existing Docling documents in the local cache. Documents are addressed by `document_key`, and individual elements within documents are addressed by anchor references (e.g., `#/texts/2`, `#/tables/1`).

## Anchor System

Each element in a Docling document has a content reference (`cref`) that serves as its anchor. Anchors follow JSON Pointer syntax:

- `#/texts/0` — first text element
- `#/texts/2` — third text element
- `#/tables/1` — second table
- `#/groups/0` — first group

Use `get_overview_of_document_anchors` to discover available anchors in a document.

## Tools

### `get_overview_of_document_anchors`

Retrieve the hierarchical structure of a document with anchor references.

**Parameters:**
- `document_key` (str) — cache key of the document

**Returns:** `DocumentAnchorOutput` with `structure: str`

**Output format:** Indented text showing the document hierarchy. Each line includes the anchor reference and item label:

```
[anchor:#/texts/0] title: Document Title
  [anchor:#/texts/1] section-header-1: Introduction
    [anchor:#/texts/2] text
    [anchor:#/texts/3] text
  [anchor:#/texts/4] section-header-1: Methods
    [anchor:#/groups/0] list
      [anchor:#/texts/5] list-item
      [anchor:#/texts/6] list-item
```

**Element types shown:**
- `title` — document title
- `section-header-N` — section heading at level N
- `text` — paragraph text
- `list` — list group
- `list-item` — list item
- `table` — table element

### `search_for_text_in_document_anchors`

Search for text or keywords within a document.

**Parameters:**
- `document_key` (str) — cache key of the document
- `text` (str) — text to search for

**Returns:** `TextSearchOutput` with `result: str`

**Search behavior:**
1. **Exact match** — case-insensitive search for the exact text string. Returns anchors where the full text appears.
2. **Keyword fallback** — if no exact match, splits the search text on non-alphanumeric characters and searches for individual keywords. Returns anchors with keyword match counts.
3. **No match** — reports that no matches were found.

**Output examples:**
- Exact: `Found exact text matches in the following anchors:\n[anchor:#/texts/2]`
- Keywords: `No exact text matches were found. Found individual keyword matches...\n[anchor:#/texts/3] keyword matches (2 total): machine (1 occurrences), learning (1 occurrences)`
- None: `No exact text matches nor individual keyword matches found for 'xyz'...`

### `get_text_of_document_item_at_anchor`

Retrieve the text content of a specific document item.

**Parameters:**
- `document_key` (str) — cache key of the document
- `document_anchor` (str) — anchor reference (e.g., `#/texts/2`)

**Returns:** `DocumentItemText` with `text: str`

**Constraint:** The anchor must point to a `TextItem` (title, heading, paragraph, list item). Tables and groups are not text items.

### `update_text_of_document_item_at_anchor`

Modify the text content of a document item.

**Parameters:**
- `document_key` (str) — cache key of the document
- `document_anchor` (str) — anchor reference (e.g., `#/texts/6`)
- `updated_text` (str) — new text content

**Returns:** `UpdateDocumentOutput` with `document_key`

**Behavior:** Directly modifies the `text` attribute of the resolved item. The change is immediate and affects subsequent exports.

**Constraint:** The anchor must point to a `TextItem`. Updating tables or groups raises an error.

### `delete_document_items_at_anchors`

Delete multiple items from a document.

**Parameters:**
- `document_key` (str) — cache key of the document
- `document_anchors` (list[str]) — list of anchor references (e.g., `["#/texts/2", "#/tables/1"]`)

**Returns:** `UpdateDocumentOutput` with `document_key`

**Behavior:** Resolves each anchor to its item, then calls `doc.delete_items()` with all items at once. Deletion is permanent within the session.

## Workflow Pattern

```
1. Convert a document → get document_key
2. get_overview_of_document_anchors(document_key) → see structure
3. search_for_text_in_document_anchors(document_key, "search term") → find relevant sections
4. get_text_of_document_item_at_anchor(document_key, "#/texts/5") → read specific content
5. update_text_of_document_item_at_anchor(document_key, "#/texts/5", "new text") → modify content
6. delete_document_items_at_anchors(document_key, ["#/texts/3"]) → remove sections
7. export_docling_document_to_markdown(document_key) → verify changes
8. save_docling_document(document_key) → persist
```

## Gotchas

- **Anchors are session-scoped** — the anchor references are valid within the server session. After a restart, cached documents are lost and anchors become invalid.
- **`search_for_text` only searches TextItems** — the search tool only looks at text elements, not table cells, captions, or footnotes.
- **Keyword search splits on non-alphanumeric** — `"machine-learning"` becomes `["machine", "learning"]`. Hyphens, underscores, and special characters are split points.
- **`update_text` modifies in-place** — the change is immediate. There is no undo. Export or save after modifications.
- **`delete_document_items` takes a list** — pass multiple anchors in a single call for efficiency. Each anchor is resolved independently.
- **Anchor format is JSON Pointer** — anchors use `#/type/index` format. `#/texts/0` is the first text element, not `#/texts/1`.
- **Non-text anchors fail on text tools** — `get_text_of_document_item_at_anchor` and `update_text_of_document_item_at_anchor` only work on `TextItem` elements. Tables and groups raise `ValueError`.
- **`get_overview` shows indentation for nesting** — use the indentation level to understand the document hierarchy. Section headers set the base indent level for their children.
