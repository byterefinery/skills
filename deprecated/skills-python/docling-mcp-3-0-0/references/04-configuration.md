# Configuration

## Overview

All Docling MCP settings use the `DOCLING_MCP_` prefix and can be supplied via environment variables, a `.env` file in the working directory, or the `env` block of an MCP client configuration.

## Configuration Sources (priority order)

1. **Environment variables** — highest priority, set in the shell or process
2. **MCP client `env` block** — set in the client's server configuration
3. **`.env` file** — read from the server's current working directory
4. **Built-in defaults** — lowest priority

Copy `.env.example` from the package as a starting point.

## Conversion Mode

| Variable | Default | Values | Description |
|---|---|---|---|
| `DOCLING_MCP_CONVERSION_MODE` | `remote` | `remote`, `local` | Which converter backend to use |

## Remote Service

Required when `DOCLING_MCP_CONVERSION_MODE=remote`.

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_SERVICE_URL` | — | URL of the Docling Serve instance |
| `DOCLING_MCP_SERVICE_API_KEY` | — | API key for the service |
| `DOCLING_MCP_SERVICE_TIMEOUT` | `300.0` | Request timeout in seconds |
| `DOCLING_MCP_SERVICE_MAX_RETRIES` | `3` | Max retry attempts on failure |
| `DOCLING_MCP_FALLBACK_TO_LOCAL` | `false` | Fall back to local if remote unreachable |

## Conversion Pipeline

Applies to both remote and local modes.

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_KEEP_IMAGES` | `false` | Retain page images in output |
| `DOCLING_MCP_IMAGES_SCALE` | `1.0` | Image scale factor |
| `DOCLING_MCP_DO_OCR` | `true` | Run OCR pipeline |
| `DOCLING_MCP_DO_TABLE_STRUCTURE` | `true` | Detect table structure |

## LlamaIndex RAG

For the `llama-index-rag` tool group.

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_LI_API_BASE` | `http://127.0.0.1:1234/v1` | OpenAI-compatible LLM endpoint |
| `DOCLING_MCP_LI_API_KEY` | `none` | API key for the LLM endpoint |
| `DOCLING_MCP_LI_MODEL_ID` | `ibm/granite-3.2-8b` | LLM model identifier |
| `DOCLING_MCP_LI_EMBEDDING_MODEL` | `BAAI/bge-base-en-v1.5` | HuggingFace embedding model |

## LlamaStack

For the `llama-stack-rag` and `llama-stack-ie` tool groups.

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_LLS_URL` | `http://localhost:8321` | LlamaStack server URL |
| `DOCLING_MCP_LLS_VDB_EMBEDDING` | `all-MiniLM-L6-v2` | Embedding model for vector DB |
| `DOCLING_MCP_LLS_EXTRACTION_MODEL` | `openai/gpt-oss-20b` | Model for structured extraction |

## MCP Client Configuration

### Claude Desktop

Edit `claude_desktop_config.json`:

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

### LM Studio

Edit `mcp.json` or use the direct install button from the MCP registry.

### Custom MCP Client

```json
{
  "mcpServers": {
    "docling": {
      "command": "uvx",
      "args": [
        "--from=docling-mcp",
        "docling-mcp-server",
        "--transport", "streamable-http",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "env": {
        "DOCLING_MCP_CONVERSION_MODE": "local"
      }
    }
  }
}
```

## Transport Selection

| Transport | Use Case | Command |
|---|---|---|
| `stdio` | Claude Desktop, LM Studio, local process | `--transport stdio` |
| `sse` | Llama Stack, event-stream clients | `--transport sse` |
| `streamable-http` | Containers, HTTP-based clients | `--transport streamable-http` (default) |

For `sse` and `streamable-http`, use `--host` and `--port` to configure the bind address (default: `localhost:8000`).

## Gotchas

- **`.env` is read from the working directory** — not from the package directory. Place `.env` where the server process runs.
- **`DOCLING_MCP_FALLBACK_TO_LOCAL` requires `[local]` extra** — the hybrid fallback only works if `docling-mcp[local]` is installed.
- **`DOCLING_MCP_SERVICE_URL` is required for remote mode** — without it, all conversion attempts fail.
- **`DOCLING_MCP_KEEP_IMAGES` affects memory** — keeping page images increases memory usage significantly for large documents.
- **`DOCLING_MCP_IMAGES_SCALE` fixes tensor errors** — if conversion fails with tensor padding errors, increase from `1.0` to `1.5` or higher.
- **LlamaStack requires Python ≥3.12** — the `llama-stack-client` dependency is unavailable on earlier Python versions.
- **`uvx` reads env from the client config** — when launched via MCP client, the `env` block in the config is passed to the `uvx` process.
