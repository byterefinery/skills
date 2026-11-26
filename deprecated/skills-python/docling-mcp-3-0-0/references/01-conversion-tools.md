# Conversion Tools

## Overview

Conversion tools transform documents (PDF, DOCX, PPTX, XLSX, HTML, images, and more) into `DoclingDocument` objects stored in a local cache. Each converted document receives a unique `document_key` used by all subsequent tools.

## Tools

### `is_document_in_local_cache`

Check whether a document with a given key is already in the local cache.

**Parameters:**
- `document_key` (str) — the unique identifier returned by a previous conversion

**Returns:** `IsDoclingDocumentInCacheOutput` with `in_cache: bool`

**Usage:** Call before `convert_document_into_docling_document` to avoid redundant conversions.

### `convert_document_into_docling_document`

Convert a single document from a URL or local file path.

**Parameters:**
- `source` (str) — URL or local file path to the document

**Returns:** `ConversionOutput` with:
- `was_converted: bool` — `False` if newly converted, `True` if already cached (skipped)
- `document_key: str` — unique cache identifier for the document

**Behavior:**
- Uses the configured converter (remote API or local) based on `DOCLING_MCP_CONVERSION_MODE`
- Stores the result in the local document cache
- Skips conversion if the document is already cached (returns `was_converted=True`)
- Runs garbage collection after conversion to free memory

**Supported formats:** PDF, DOCX, PPTX, XLSX, HTML, images (PNG, JPG, TIFF, etc.), EPUB, ODF, LaTeX, CSV, Markdown, EML, MSG, WebVTT, and more.

### `convert_directory_files_into_docling_document`

Batch-convert all files in a local directory.

**Parameters:**
- `source` (str) — path to a local directory

**Returns:** `list[ConversionOutput]` — one result per file

**Behavior:**
- Iterates over all files in the directory (non-recursive)
- Reports progress via MCP's progress API
- Skips files that fail conversion (continues with remaining files)
- Runs garbage collection after batch completion
- Strips surrounding quotes from the source path

**Note:** This is an async tool. It processes files sequentially, not in parallel.

## Conversion Modes

### Remote Mode

The default mode. Sends documents to a Docling Serve API instance.

```bash
export DOCLING_MCP_CONVERSION_MODE=remote
export DOCLING_MCP_SERVICE_URL=https://your-docling-service.example.com
export DOCLING_MCP_SERVICE_API_KEY=your-api-key-here
```

**Advantages:** lightweight install (~50MB), scalable, no model downloads.
**Requirements:** accessible Docling Serve instance.

### Local Mode

Runs conversion locally using the bundled Docling library.

```bash
export DOCLING_MCP_CONVERSION_MODE=local
```

**Advantages:** fully offline, no external service needed.
**Requirements:** `pip install docling-mcp[local]`, model downloads on first use.

### Hybrid Mode

Remote-first with automatic fallback to local.

```bash
export DOCLING_MCP_CONVERSION_MODE=remote
export DOCLING_MCP_FALLBACK_TO_LOCAL=true
```

**Advantages:** uses remote when available, falls back to local on failures.
**Requirements:** `pip install docling-mcp[local]`, remote service credentials configured.

## Pipeline Options

These variables affect both remote and local conversion:

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_KEEP_IMAGES` | `false` | Retain page images in output (needed for thumbnails) |
| `DOCLING_MCP_IMAGES_SCALE` | `1.0` | Image scale factor (increase to avoid tensor padding errors) |
| `DOCLING_MCP_DO_OCR` | `true` | Run OCR pipeline on scanned content |
| `DOCLING_MCP_DO_TABLE_STRUCTURE` | `true` | Detect and extract table structure |

## Remote Service Options

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_SERVICE_TIMEOUT` | `300.0` | Request timeout in seconds |
| `DOCLING_MCP_SERVICE_MAX_RETRIES` | `3` | Maximum retry attempts on failure |

## Gotchas

- **`was_converted` is inverted** — `False` means the document was newly converted; `True` means it was already cached and skipped.
- **Directory conversion is non-recursive** — only files directly in the specified directory are processed. Subdirectories are ignored.
- **Quote stripping** — `convert_directory_files_into_docling_document` removes surrounding `"` or `'` from the source path. This handles cases where the agent wraps paths in quotes.
- **Memory cleanup** — both single and batch conversion tools run `gc.collect()` after processing. Large documents can consume significant memory.
- **Remote mode fails silently without credentials** — if `DOCLING_MCP_SERVICE_URL` is not set, conversion will fail. Check server logs for the error.
