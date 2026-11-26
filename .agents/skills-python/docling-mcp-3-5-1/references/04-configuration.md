# Configuration (docling-mcp 3.5.1)

All settings use the `DOCLING_MCP_` prefix and can be supplied as environment variables, in a `.env` file in the working directory, or via the `env` block of your MCP client config. Copy `.env.example` as a starting point.

## Conversion mode

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_CONVERSION_MODE` | `remote` | `remote` or `local` |

## Remote service (required when `CONVERSION_MODE=remote`)

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_SERVICE_URL` | — | URL of the Docling Serve instance |
| `DOCLING_MCP_SERVICE_API_KEY` | — | API key for the service |
| `DOCLING_MCP_SERVICE_TIMEOUT` | `300.0` | Timeout in seconds for a whole conversion job |
| `DOCLING_MCP_SERVICE_MAX_RETRIES` | `3` | Max retry attempts |
| `DOCLING_MCP_FALLBACK_TO_LOCAL` | `false` | Fall back to local if service is unreachable (requires `docling-mcp[local]`) |

## Conversion pipeline (applies to both modes)

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_KEEP_IMAGES` | `false` | Retain page images in output. Required for `get_page_thumbnail` and `image_export_mode=embedded` |
| `DOCLING_MCP_IMAGES_SCALE` | `1.0` | Image scale factor (increase to avoid tensor padding errors) |
| `DOCLING_MCP_DO_OCR` | `true` | Run OCR pipeline |
| `DOCLING_MCP_OCR_ENGINE` | `auto` | OCR engine by docling kind: `auto`, `easyocr`, `tesseract` (system binary), `tesserocr` (Python bindings), `ocrmac`, `rapidocr`. The engine must be installed on the conversion backend. In remote mode it is sent as the Docling Serve `ocr_preset`, so server-defined preset names also work there |
| `DOCLING_MCP_OCR_LANG` | — | Comma-separated OCR languages, passed to the engine unchanged. `iso:en,iso:de` works with any engine (docling ≥ 2.127, recommended with `auto`); bare codes are engine-specific (`eng` for Tesseract, `en` for EasyOCR or Docling Serve). Unset means the engine's defaults |
| `DOCLING_MCP_DO_TABLE_STRUCTURE` | `true` | Detect table structure |
| `DOCLING_MCP_DO_PICTURE_DESCRIPTION` | `false` | Run a vision-language model to generate textual descriptions for figures and pictures |
| `DOCLING_MCP_PICTURE_DESCRIPTION_PRESET` | — | Preset ID for the picture-description VLM (e.g., `smolvlm`, `granite_vision`). When unset the backend default is used. Only applies when picture description is enabled |

> Enabling `DOCLING_MCP_DO_PICTURE_DESCRIPTION=true` adds a VLM inference step for every figure. On resource-constrained hardware this can significantly increase conversion time. Increase `DOCLING_MCP_SERVICE_TIMEOUT` (remote) or the MCP client request timeout (e.g., LM Studio `timeout` field in ms).

## Markdown export

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_IMAGE_EXPORT_MODE` | `placeholder` | How images are rendered in Markdown output: `placeholder` (emits `<!-- image -->`), `embedded` (base64 data-URI), `referenced` (file path / URL) |

## Cache

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_CACHE_MAX_DOCUMENTS` | `10` | Maximum number of documents to keep in the in-memory cache. When the limit is reached the least-recently-used document is evicted |

## LlamaIndex RAG (`--tools llama-index-rag`)

Prefix `DOCLING_MCP_LI_`.

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_LI_API_BASE` | `http://127.0.0.1:1234/v1` | OpenAI-compatible LLM endpoint |
| `DOCLING_MCP_LI_API_KEY` | `none` | API key for the LLM endpoint |
| `DOCLING_MCP_LI_MODEL_ID` | `ibm/granite-3.2-8b` | LLM model identifier |
| `DOCLING_MCP_LI_EMBEDDING_MODEL` | `BAAI/bge-base-en-v1.5` | HuggingFace embedding model |

## LlamaStack (`--tools llama-stack-rag` / `--tools llama-stack-ie`)

Prefix `DOCLING_MCP_LLS_`.

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_LLS_URL` | `http://localhost:8321` | LlamaStack server URL |
| `DOCLING_MCP_LLS_VDB_EMBEDDING` | `all-MiniLM-L6-v2` | Embedding model for vector DB |
| `DOCLING_MCP_LLS_EXTRACTION_MODEL` | `openai/gpt-oss-20b` | Model used for structured extraction |

## MCP client config example

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

The `.env` file is read from the server's current working directory, alongside environment variables and MCP client `env` blocks.
