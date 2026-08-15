---
name: docling-mcp-3-0-0
description: >
  Docling MCP 3.0.0 — Model Context Protocol server that exposes Docling document
  processing as MCP tools. Use when connecting Docling to AI agents via MCP (Claude
  Desktop, LM Studio, Cursor, etc.). Provides three tool groups — conversion (PDF to
  DoclingDocument via remote API or local), generation (create/edit documents with
  titles, headings, paragraphs, lists, tables), and manipulation (search, update,
  delete document items by anchor). Optional tool groups include llama-index-rag (Milvus
  vector search), llama-stack-rag (LlamaStack RAG), llama-stack-ie (structured
  extraction). Supports remote mode (Docling Serve API), local mode (offline),
  and hybrid mode (remote with local fallback). Transports are stdio, SSE, and streamable-http.
  Triggers on docling-mcp, MCP server for documents, docling agent tools, MCP
  document conversion, docling MCP integration, Claude Desktop docling, LM Studio
  docling, document MCP tools.
license: MIT
compatibility: >
  Python 3.10–3.14. Requires `uv` or `pip`. Remote mode needs a Docling Serve
  instance. Local mode needs `docling-mcp[local]` extra (~500MB with models).
  LlamaIndex RAG needs `docling-mcp[llama-index-rag]`. LlamaStack tools need
  `docling-mcp[llama-stack]` (Python ≥3.12). MCP Python SDK v2+.
metadata:
  tags:
    - document-processing
    - mcp
    - pdf
    - rag
    - python
    - ai
---

# docling-mcp 3.0.0

## Overview

Docling MCP 3.0.0 exposes Docling document processing as MCP tools, enabling AI agents to convert, generate, and manipulate documents through the Model Context Protocol. It bridges Docling's document understanding with MCP-compatible clients (Claude Desktop, LM Studio, Cursor, and any MCP client).

**Three core tool groups** load by default:

- **Conversion** — convert PDFs/documents from local files or URLs into `DoclingDocument` objects stored in a local cache; batch-convert entire directories
- **Generation** — create new documents programmatically, add titles, headings, paragraphs, lists, tables; export to Markdown or save to disk; generate page thumbnails
- **Manipulation** — inspect document structure via anchors, search text, get/update/delete items by anchor reference

**Optional tool groups** (loaded via `--tools`):

- **`llama-index-rag`** — LlamaIndex-based RAG with Milvus vector store
- **`llama-stack-rag`** — LlamaStack RAG integration
- **`llama-stack-ie`** — LlamaStack structured information extraction

**Three conversion modes:**

- **Remote** (default) — calls a Docling Serve API, lightweight (~50MB base install)
- **Local** — runs conversion locally, requires `docling-mcp[local]` extra
- **Hybrid** — remote with automatic fallback to local when the service is unreachable

**MCP SDK v2** — v3 requires `mcp>=2.0.0`. Clients not on SDK v2 should pin `docling-mcp<3.0.0`.

## Installation

```bash
# Remote mode (lightweight, default)
pip install docling-mcp

# Local mode (offline conversion)
pip install docling-mcp[local]

# With LlamaIndex RAG
pip install docling-mcp[llama-index-rag]

# With LlamaStack tools (Python ≥3.12)
pip install docling-mcp[llama-stack]
```

## Usage

### Quick start with uvx

```bash
# stdio transport (Claude Desktop, LM Studio)
uvx --from docling-mcp docling-mcp-server --transport stdio

# SSE transport (Llama Stack)
uvx --from docling-mcp docling-mcp-server --transport sse

# Streamable HTTP (containers, default)
uvx --from docling-mcp docling-mcp-server --transport streamable-http
```

### MCP client configuration

Add to your MCP client config (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "docling": {
      "command": "uvx",
      "args": ["--from=docling-mcp", "docling-mcp-server"],
      "env": {
        "DOCLING_MCP_CONVERSION_MODE": "remote",
        "DOCLING_MCP_SERVICE_URL": "https://your-docling-service.example.com",
        "DOCLING_MCP_SERVICE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Tool groups

```bash
# Default tools (conversion, generation, manipulation)
uvx --from docling-mcp docling-mcp-server

# Specific tool groups
uvx --from docling-mcp docling-mcp-server --tools conversion generation

# All tool groups
uvx --from docling-mcp docling-mcp-server --tools conversion generation manipulation llama-index-rag llama-stack-rag llama-stack-ie
```

### Conversion mode

```bash
# Remote mode (default, needs Docling Serve)
export DOCLING_MCP_CONVERSION_MODE=remote
export DOCLING_MCP_SERVICE_URL=https://your-docling-service.example.com
export DOCLING_MCP_SERVICE_API_KEY=your-api-key-here

# Local mode (offline)
export DOCLING_MCP_CONVERSION_MODE=local

# Hybrid (remote with local fallback)
export DOCLING_MCP_CONVERSION_MODE=remote
export DOCLING_MCP_FALLBACK_TO_LOCAL=true
```

### Configuration

All settings use the `DOCLING_MCP_` prefix. Copy `.env.example` as a starting point.

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_CONVERSION_MODE` | `remote` | `remote` or `local` |
| `DOCLING_MCP_SERVICE_URL` | — | Docling Serve URL (required for remote) |
| `DOCLING_MCP_SERVICE_API_KEY` | — | API key for the service |
| `DOCLING_MCP_SERVICE_TIMEOUT` | `300.0` | Request timeout in seconds |
| `DOCLING_MCP_SERVICE_MAX_RETRIES` | `3` | Max retry attempts |
| `DOCLING_MCP_FALLBACK_TO_LOCAL` | `false` | Fall back to local if remote unreachable |
| `DOCLING_MCP_KEEP_IMAGES` | `false` | Retain page images in output |
| `DOCLING_MCP_IMAGES_SCALE` | `1.0` | Image scale factor |
| `DOCLING_MCP_DO_OCR` | `true` | Run OCR pipeline |
| `DOCLING_MCP_DO_TABLE_STRUCTURE` | `true` | Detect table structure |

### Conversion tools

- `is_document_in_local_cache(document_key)` — check if a document is cached
- `convert_document_into_docling_document(source)` — convert a single document (URL or local path)
- `convert_directory_files_into_docling_document(source)` — batch-convert all files in a directory

### Generation tools

- `create_new_docling_document(prompt)` — create a new document from a prompt
- `export_docling_document_to_markdown(document_key, max_size)` — export to Markdown
- `save_docling_document(document_key)` — save to disk (Markdown + JSON)
- `page_thumbnail(document_key, page_no, size)` — generate a page thumbnail image
- `add_title_to_docling_document(document_key, title)` — add/update document title
- `add_section_heading_to_docling_document(document_key, section_heading, section_level)` — add a heading
- `add_paragraph_to_docling_document(document_key, paragraph)` — add a paragraph
- `open_list_in_docling_document(document_key)` — open a new list group
- `close_list_in_docling_document(document_key)` — close a list group
- `add_list_items_to_list_in_docling_document(document_key, list_items)` — add items to an open list
- `add_table_in_html_format_to_docling_document(document_key, html_table, table_captions, table_footnotes)` — add an HTML table

### Manipulation tools

- `get_overview_of_document_anchors(document_key)` — get hierarchical structure with anchor references
- `search_for_text_in_document_anchors(document_key, text)` — search text/keywords in document
- `get_text_of_document_item_at_anchor(document_key, document_anchor)` — get text at an anchor (e.g., `#/texts/2`)
- `update_text_of_document_item_at_anchor(document_key, document_anchor, updated_text)` — update text at an anchor
- `delete_document_items_at_anchors(document_key, document_anchors)` — delete items by anchor list

### Example workflows

**Convert a PDF:**
```
Convert the PDF document at /path/to/file.pdf into DoclingDocument and return its document-key.
```

**Generate a document:**
```
Create a Docling document about the impact of tokenizers on LLM quality.
Start with create_new_docling_document, add a title with add_title_to_docling_document,
then iteratively add section headings and paragraphs. Use export_docling_document_to_markdown
to check progress. Save the final document with save_docling_document.
```

## Gotchas

- **`uvx` is the recommended launch method** — `uvx --from docling-mcp docling-mcp-server` handles dependency resolution automatically. No manual `pip install` needed for quick use.
- **Remote mode is default and requires configuration** — `DOCLING_MCP_CONVERSION_MODE=remote` (default) needs `DOCLING_MCP_SERVICE_URL` and optionally `DOCLING_MCP_SERVICE_API_KEY`. Without these, conversion tools will fail.
- **Local mode needs the `[local]` extra** — `pip install docling-mcp[local]` pulls in the full Docling stack (~500MB). Without it, local conversion is unavailable and hybrid fallback won't work.
- **`--tools` selects tool groups, not individual tools** — pass tool group names as positional arguments: `--tools conversion generation manipulation`. You cannot pick individual tools.
- **Default tools are conversion, generation, manipulation** — if `--tools` is omitted, these three groups load automatically. Optional groups (llama-index-rag, llama-stack-rag, llama-stack-ie) must be explicitly requested.
- **`--transport` must match the client** — `stdio` for Claude Desktop/LM Studio, `sse` for Llama Stack, `streamable-http` for containers and HTTP-based clients. Using the wrong transport causes connection failures.
- **`streamable-http` is the default transport** — if `--transport` is omitted, the server starts on `http://localhost:8000`. Use `--host` and `--port` to customize.
- **Document keys are opaque identifiers** — `convert_document_into_docling_document` returns a `document_key` used by all subsequent tools. Keep this key across tool calls within a session.
- **Stack cache manages document generation state** — when building documents, tools maintain an internal stack. Close lists before adding headings or paragraphs; the tools enforce this and raise errors if the stack is in an inconsistent state.
- **`page_thumbnail` requires `DOCLING_MCP_KEEP_IMAGES=true`** — page images are not generated by default. Set this env var when starting the server for thumbnail support.
- **`add_table_in_html_format_to_docling_document` needs `[local]` extra** — HTML table parsing requires `docling-mcp[local]` because it uses `DocumentConverter` internally.
- **v3 requires MCP SDK v2** — if your MCP client hasn't migrated to SDK v2, pin `docling-mcp<3.0.0`. The v2 line (latest `v2.2.0`) receives critical fixes but no new features.
- **`DOCLING_MCP_IMAGES_SCALE` avoids tensor padding errors** — if conversion fails with tensor-related errors, increase this value (e.g., `1.5`) to adjust image dimensions.
- **LlamaStack tools require Python ≥3.12** — the `llama-stack-client` dependency is only available on Python 3.12+.
- **`.env` file is checked in the working directory** — the server reads `.env` from its current working directory alongside environment variables and MCP client `env` blocks.
- **`convert_directory_files_into_docling_document` is async with progress** — it processes files sequentially and reports progress via MCP's progress API. Failed files are skipped; the tool continues with remaining files.
- **`export_docling_document_to_markdown` truncation** — use `max_size` to limit output length. Without it, the full document is exported, which can be large for complex documents.
- **`save_docling_document` writes to the cache directory** — files are saved as `{document_key}.md` and `{document_key}.json` in the Docling cache directory, not a user-specified path.

## References

- [01-conversion-tools](references/01-conversion-tools.md) — convert_document, convert_directory, cache lookup, remote/local/hybrid modes
- [02-generation-tools](references/02-generation-tools.md) — create, add title/heading/paragraph/list/table, export, save, thumbnails
- [03-manipulation-tools](references/03-manipulation-tools.md) — anchor overview, text search, get/update/delete items by anchor
- [04-configuration](references/04-configuration.md) — environment variables, .env file, MCP client config, conversion pipeline options
- [05-rag-tools](references/05-rag-tools.md) — LlamaIndex RAG with Milvus, LlamaStack RAG and structured extraction
- [06-integrations](references/06-integrations.md) — Claude Desktop, LM Studio, MCP client config patterns, transport selection
