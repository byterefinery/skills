# Conversion tools (docling-mcp 3.5.1)

Convert documents from a source into `DoclingDocument` objects stored in the local cache, plus cache management.

## Tools

### check_document_in_local_cache(document_key)

Check whether a document is already converted and present in the local cache. Returns a boolean. Read-only.

### remove_document_from_local_cache(document_key)

Remove a document from the local cache and release its memory. Call when a client is finished with a document. Returns `dropped` (True if the key was present and removed, False if not found). Destructive.

### list_cached_documents()

Return the keys of all documents currently held in the local cache. Use to discover which documents are available before calling any tool that requires a `document_key`. An empty list means nothing is cached yet. Read-only.

### convert_document_into_docling_document(source)

Convert a document from a URL or local path into a Docling document using the configured converter (remote API or local). Stores the result in the local cache and returns an output with a boolean plus the document's unique cache key. If the document was already cached, conversion is skipped and the boolean is set to True.

`source` accepts:
- http(s) URLs
- `s3://`, `gs://`, `abfs://` cloud URIs (need the matching fsspec package on the backend)
- local file paths (PDF, DOCX, HTML, image, etc.)

### convert_directory_files_into_docling_document(source)

Convert all files from a local directory path and store them in the local cache. `source` is a local directory path. Async; processes files sequentially and reports progress via MCP's progress API. Returns a list of conversion outputs (one per file). Failed files are skipped; processing continues with the remaining files.

## Conversion modes

- **Remote** (`DOCLING_MCP_CONVERSION_MODE=remote`, default) — calls a Docling Serve API. Requires `DOCLING_MCP_SERVICE_URL` and optionally `DOCLING_MCP_SERVICE_API_KEY`.
- **Local** (`DOCLING_MCP_CONVERSION_MODE=local`) — runs conversion locally. Requires the `docling-mcp[local]` extra.
- **Hybrid** — remote mode with `DOCLING_MCP_FALLBACK_TO_LOCAL=true`; falls back to local when the service is unreachable (requires `[local]`).

The pipeline options (`DO_OCR`, `OCR_ENGINE`, `OCR_LANG`, `DO_TABLE_STRUCTURE`, picture description, etc.) apply to both modes. In remote mode they are sent to Docling Serve as conversion parameters.

## Cache behavior

- The in-memory cache is bounded by `DOCLING_MCP_CACHE_MAX_DOCUMENTS` (default 10); the least-recently-used document is evicted when the limit is reached.
- Conversions are keyed by file content and conversion config, so identical inputs reuse cached results.
- Use `list_cached_documents()` to inspect and `remove_document_from_local_cache()` to free memory explicitly.
