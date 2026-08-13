# RAG Tools

## Overview

Docling MCP provides optional RAG (Retrieval-Augmented Generation) tool groups that integrate with LlamaIndex and LlamaStack ecosystems. These tools are not loaded by default — they must be explicitly requested via `--tools`.

## LlamaIndex RAG (`--tools llama-index-rag`)

Integrates Docling with LlamaIndex for document indexing and retrieval using Milvus as the vector store.

### Installation

```bash
pip install docling-mcp[llama-index-rag]
```

### Configuration

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_LI_API_BASE` | `http://127.0.0.1:1234/v1` | OpenAI-compatible LLM endpoint |
| `DOCLING_MCP_LI_API_KEY` | `none` | API key for the LLM endpoint |
| `DOCLING_MCP_LI_MODEL_ID` | `ibm/granite-3.2-8b` | LLM model identifier |
| `DOCLING_MCP_LI_EMBEDDING_MODEL` | `BAAI/bge-base-en-v1.5` | HuggingFace embedding model |

### Dependencies

- `llama-index` — core indexing framework
- `llama-index-embeddings-huggingface` — embedding models
- `llama-index-embeddings-openai` — OpenAI embeddings
- `llama-index-llms-openai-like` — OpenAI-compatible LLMs
- `llama-index-node-parser-docling` — Docling node parser
- `llama-index-readers-docling` — Docling reader
- `llama-index-readers-file` — file readers
- `llama-index-vector-stores-milvus` — Milvus vector store

### Launch

```bash
uvx --from docling-mcp docling-mcp-server --tools conversion generation manipulation llama-index-rag
```

## LlamaStack RAG (`--tools llama-stack-rag`)

Integrates with LlamaStack for RAG workflows.

### Installation

```bash
pip install docling-mcp[llama-stack]
```

### Configuration

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_LLS_URL` | `http://localhost:8321` | LlamaStack server URL |
| `DOCLING_MCP_LLS_VDB_EMBEDDING` | `all-MiniLM-L6-v2` | Embedding model for vector DB |

### Launch

```bash
uvx --from docling-mcp docling-mcp-server --tools conversion generation manipulation llama-stack-rag
```

## LlamaStack Structured Extraction (`--tools llama-stack-ie`)

Uses LlamaStack for structured information extraction from documents.

### Installation

```bash
pip install docling-mcp[llama-stack]
```

### Configuration

| Variable | Default | Description |
|---|---|---|
| `DOCLING_MCP_LLS_URL` | `http://localhost:8321` | LlamaStack server URL |
| `DOCLING_MCP_LLS_EXTRACTION_MODEL` | `openai/gpt-oss-20b` | Model for structured extraction |

### Launch

```bash
uvx --from docling-mcp docling-mcp-server --tools conversion generation manipulation llama-stack-ie
```

## Gotchas

- **RAG tools are not loaded by default** — they must be explicitly requested via `--tools`. The default tool groups are `conversion`, `generation`, and `manipulation`.
- **LlamaStack requires Python ≥3.12** — the `llama-stack-client` dependency is only available on Python 3.12+.
- **Milvus must be running for LlamaIndex RAG** — the vector store connection fails silently if Milvus is not accessible.
- **LlamaStack server must be running** — both `llama-stack-rag` and `llama-stack-ie` require an active LlamaStack server at the configured URL.
- **Embedding models download on first use** — HuggingFace embedding models are downloaded and cached on first use.
- **`llama-index-rag` is heavy** — the extra pulls in many dependencies including Milvus client, embedding models, and LLM connectors.
- **Tool groups can be combined** — multiple tool groups can be specified: `--tools conversion generation manipulation llama-index-rag llama-stack-rag`.
