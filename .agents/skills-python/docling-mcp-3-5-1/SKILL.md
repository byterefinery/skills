---
name: docling-mcp-3-5-1
description: >
  Docling MCP 3.5.1 — Model Context Protocol server that exposes Docling document
  processing as MCP tools. Use when connecting Docling to AI agents via MCP (Claude
  Desktop, LM Studio, Cursor, etc.). Three tool groups — conversion (PDF/DOCX/HTML/image to
  DoclingDocument via remote API or local, plus cache management), generation (create/edit documents
  with titles, headings, paragraphs, lists, tables; per-page export/save), and manipulation (search,
  update, delete items by anchor). Optional groups include llama-index-rag (Milvus), llama-stack-rag,
  llama-stack-ie. Supports remote (Docling Serve API), local, and hybrid modes. Source URIs accept
  http(s), s3, gs, abfs, or local paths. Transports are stdio, SSE, streamable-http. Triggers on
  docling-mcp, MCP server for documents, docling agent tools, MCP document conversion, Claude Desktop
  docling, LM Studio docling, document MCP tools.
license: MIT
compatibility: >
  Python 3.10–3.14. Requires `uv` or `pip`. Remote mode needs a Docling Serve instance.
  Local mode needs `docling-mcp[local]` extra (full Docling stack). LlamaIndex RAG needs
  `docling-mcp[llama-index-rag]`. LlamaStack tools need `docling-mcp[llama-stack]` (Python ≥3.12).
  MCP Python SDK v2+. s3/gs/abfs source URIs need the matching fsspec package installed on the backend.
metadata:
  tags:
    - document-processing
    - mcp
    - pdf
    - rag
    - python
    - ai
---

# docling-mcp 3.5.1

## Overview

Docling MCP 3.5.1 exposes Docling document processing as MCP tools, enabling AI agents to convert, generate, and manipulate documents through the Model Context Protocol. It bridges Docling's document understanding with MCP-compatible clients (Claude Desktop, LM Studio, Cursor, and any MCP client).

**Three core tool groups** load by default:

- **Conversion** — convert PDF/DOCX/HTML/images from local files, http(s) URLs, or s3/gs/abfs URIs into `DoclingDocument` objects stored in a local cache; batch-convert directories; inspect and manage the cache
- **Generation** — create new documents programmatically, add titles, headings, paragraphs, lists, tables; export to Markdown (optionally a single page) or save to disk; generate page thumbnails
- **Manipulation** — inspect document structure via anchors, search text, get/update/delete items by anchor reference

**Optional tool groups** (loaded via `--tools`):

- **`llama-index-rag`** — LlamaIndex-based RAG with Milvus vector store
- **`llama-stack-rag`** — LlamaStack RAG integration
- **`llama-stack-ie`** — LlamaStack structured information extraction

**Three conversion modes:**

- **Remote** (default) — calls a Docling Serve API, lightweight base install
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

All settings use the `DOCLING_MCP_` prefix and can be supplied as environment variables, in a `.env` file in the working directory, or via the `env` block of your MCP client config. Copy `.env.example` as a starting point.

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_CONVERSION_MODE` | `remote` | `remote` or `local` |
| `DOCLING_MCP_SERVICE_URL` | — | Docling Serve URL (required for remote) |
| `DOCLING_MCP_SERVICE_API_KEY` | — | API key for the service |
| `DOCLING_MCP_SERVICE_TIMEOUT` | `300.0` | Request timeout in seconds |
| `DOCLING_MCP_SERVICE_MAX_RETRIES` | `3` | Max retry attempts |
| `DOCLING_MCP_FALLBACK_TO_LOCAL` | `false` | Fall back to local if remote unreachable (needs `[local]`) |
| `DOCLING_MCP_KEEP_IMAGES` | `false` | Retain page images in output |
| `DOCLING_MCP_IMAGES_SCALE` | `1.0` | Image scale factor (increase to avoid tensor padding errors) |
| `DOCLING_MCP_DO_OCR` | `true` | Run OCR pipeline |
| `DOCLING_MCP_OCR_ENGINE` | `auto` | OCR engine by docling kind: `auto`, `easyocr`, `tesseract`, `tesserocr`, `ocrmac`, `rapidocr`; in remote mode sent as the Docling Serve `ocr_preset` |
| `DOCLING_MCP_OCR_LANG` | — | Comma-separated OCR languages, passed to the engine unchanged. `iso:en,iso:de` works with any engine (docling ≥ 2.127); bare codes are engine-specific (`eng` for Tesseract, `en` for EasyOCR). Unset means engine defaults |
| `DOCLING_MCP_DO_TABLE_STRUCTURE` | `true` | Detect table structure |
| `DOCLING_MCP_DO_PICTURE_DESCRIPTION` | `false` | Run a VLM to generate textual descriptions for figures/pictures |
| `DOCLING_MCP_PICTURE_DESCRIPTION_PRESET` | — | Preset ID for the picture-description VLM (e.g., `smolvlm`, `granite_vision`). Only applies when picture description is enabled |
| `DOCLING_MCP_IMAGE_EXPORT_MODE` | `placeholder` | How images render in Markdown: `placeholder` (`<!-- image -->`), `embedded` (base64 data-URI), `referenced` (file path/URL) |
| `DOCLING_MCP_CACHE_MAX_DOCUMENTS` | `10` | Max documents in the in-memory cache; LRU eviction when reached |

### Conversion tools

- `check_document_in_local_cache(document_key)` — check if a document is cached
- `remove_document_from_local_cache(document_key)` — drop a cached document and release its memory
- `list_cached_documents()` — list all document keys currently in the cache
- `convert_document_into_docling_document(source)` — convert a single document (http(s)/s3/gs/abfs URL or local path)
- `convert_directory_files_into_docling_document(source)` — batch-convert all files in a local directory

### Generation tools

- `create_new_docling_document(prompt)` — create a new document from a prompt
- `export_docling_document_to_markdown(document_key, max_size, page_no)` — export to Markdown; set `page_no` (1-based) to export a single page
- `save_docling_document(document_key, page_no)` — save to disk (Markdown + JSON); `page_no` writes a page-specific markdown file while JSON always holds the full document
- `get_page_thumbnail(document_key, page_no, size)` — generate a page thumbnail image
- `add_title_to_docling_document(document_key, title)` — add/update document title
- `add_section_heading_to_docling_document(document_key, section_heading, section_level)` — add a heading
- `add_paragraph_to_docling_document(document_key, paragraph)` — add a paragraph
- `open_list_in_docling_document(document_key)` — open a new list group (nests if a list is already open)
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
then iteratively add section headings and paragraphs. To insert lists, first open a list
with open_list_in_docling_document, add items with add_list_items_to_list_in_docling_document,
then close it with close_list_in_docling_document. Use export_docling_document_to_markdown
to check progress. Save the final document with save_docling_document.
```

## Gotchas

- **`uvx` is the recommended launch method** — `uvx --from docling-mcp docling-mcp-server` handles dependency resolution automatically. No manual `pip install` needed for quick use.
- **Remote mode is default and requires configuration** — `DOCLING_MCP_CONVERSION_MODE=remote` (default) needs `DOCLING_MCP_SERVICE_URL` and optionally `DOCLING_MCP_SERVICE_API_KEY`. Without these, conversion tools will fail.
- **Local mode needs the `[local]` extra** — `pip install docling-mcp[local]` pulls in the full Docling stack. Without it, local conversion is unavailable and hybrid fallback won't work.
- **Tool names changed since 3.0.0** — `is_document_in_local_cache` is now `check_document_in_local_cache`, and `page_thumbnail` is now `get_page_thumbnail`. New tools `remove_document_from_local_cache` and `list_cached_documents` manage the cache.
- **`export`/`save` accept `page_no` (3.4.0+)** — set 1-based `page_no` to export/save a single page; omit for the whole document. For `save_docling_document`, the JSON file always contains the full document even when `page_no` is set.
- **OCR engine and language are configurable (3.5.0+)** — `DOCLING_MCP_OCR_ENGINE` selects the engine (`auto` default) and `DOCLING_MCP_OCR_LANG` passes languages to it unchanged. Use `iso:`-prefixed codes (`iso:en,iso:de`) for engine-independent language selection; bare codes are engine-specific. In remote mode the engine is sent as the Docling Serve `ocr_preset`, so server-defined preset names also work there.
- **Picture description adds a VLM step (3.3.0+)** — `DOCLING_MCP_DO_PICTURE_DESCRIPTION=true` runs a vision-language model on every figure, which can significantly increase conversion time on constrained hardware. Increase `DOCLING_MCP_SERVICE_TIMEOUT` (remote) or the MCP client request timeout (e.g., LM Studio `timeout` in ms).
- **Source URIs include cloud schemes (3.1.0+)** — `convert_document_into_docling_document` accepts `http(s)`, `s3://`, `gs://`, and `abfs://` sources in addition to local paths. Cloud schemes need the matching fsspec package (`s3fs`, `gcsfs`, `adlfs`) installed on the conversion backend.
- **Markdown image rendering is configurable (3.2.0+)** — `DOCLING_MCP_IMAGE_EXPORT_MODE` controls how images appear in exported Markdown: `placeholder` (default, emits `<!-- image -->`), `embedded` (base64 data-URI, needs `DOCLING_MCP_KEEP_IMAGES=true`), or `referenced` (file path/URL).
- **The document cache is bounded by LRU (3.2.1+)** — `DOCLING_MCP_CACHE_MAX_DOCUMENTS` (default 10) caps in-memory documents; the least-recently-used is evicted when the limit is reached. Use `list_cached_documents()` to inspect and `remove_document_from_local_cache()` to free a document explicitly.
- **`--tools` selects tool groups, not individual tools** — pass tool group names as positional arguments: `--tools conversion generation manipulation`. You cannot pick individual tools.
- **Default tools are conversion, generation, manipulation** — if `--tools` is omitted, these three groups load automatically. Optional groups (llama-index-rag, llama-stack-rag, llama-stack-ie) must be explicitly requested.
- **`--transport` must match the client** — `stdio` for Claude Desktop/LM Studio, `sse` for Llama Stack, `streamable-http` for containers and HTTP-based clients. Using the wrong transport causes connection failures.
- **`streamable-http` is the default transport** — if `--transport` is omitted, the server starts on `http://localhost:8000`. Use `--host` and `--port` to customize.
- **Document keys are opaque identifiers** — `convert_document_into_docling_document` returns a `document_key` used by all subsequent tools. Keep this key across tool calls within a session.
- **Stack cache manages document generation state** — when building documents, tools maintain an internal stack. Close lists before adding headings or paragraphs; the tools enforce this and raise errors if the stack is in an inconsistent state. A list opened while another list is open now nests correctly (3.5.1 fix).
- **`get_page_thumbnail` requires `DOCLING_MCP_KEEP_IMAGES=true`** — page images are not generated by default. Set this env var when starting the server for thumbnail support; otherwise the tool raises a ValueError.
- **v3 requires MCP SDK v2** — if your MCP client hasn't migrated to SDK v2, pin `docling-mcp<3.0.0`. The v2 line (latest `v2.2.0`) receives critical fixes but no new features.
- **`DOCLING_MCP_IMAGES_SCALE` avoids tensor padding errors** — if conversion fails with tensor-related errors, increase this value (e.g., `1.5`) to adjust image dimensions.
- **LlamaStack tools require Python ≥3.12** — the `llama-stack-client` dependency is only available on Python 3.12+.
- **`.env` file is checked in the working directory** — the server reads `.env` from its current working directory alongside environment variables and MCP client `env` blocks.
- **`convert_directory_files_into_docling_document` is async with progress** — it processes files sequentially and reports progress via MCP's progress API. Failed files are skipped; the tool continues with remaining files.
- **`export_docling_document_to_markdown` truncation** — use `max_size` to limit output length. Without it, the full document is exported, which can be large for complex documents.
- **`save_docling_document` writes to the cache directory** — files are saved as `{document_key}.md` and `{document_key}.json` in the Docling cache directory (or `{document_key}-p{page_no}.md` when `page_no` is set), not a user-specified path.

## References

- [01-conversion-tools](references/01-conversion-tools.md) — convert_document, convert_directory, cache lookup/remove/list, remote/local/hybrid modes, source URIs
- [02-generation-tools](references/02-generation-tools.md) — create, add title/heading/paragraph/list/table, export/save with page_no, thumbnails
- [03-manipulation-tools](references/03-manipulation-tools.md) — anchor overview, text search, get/update/delete items by anchor
- [04-configuration](references/04-configuration.md) — environment variables, .env file, MCP client config, conversion pipeline and OCR options
- [05-rag-tools](references/05-rag-tools.md) — LlamaIndex RAG with Milvus, LlamaStack RAG and structured extraction
- [06-integrations](references/06-integrations.md) — Claude Desktop, LM Studio, MCP client config patterns, transport selection
