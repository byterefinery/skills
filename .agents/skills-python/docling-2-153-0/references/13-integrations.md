# Integrations

Docling integrates with the gen AI ecosystem. See `docs/integrations` and `docs/usage/mcp.md`, `docs/usage/jobkit.md` in the repo for current details.

## When to use what

| Use case | Tool |
|----------|------|
| In-process Python | `DocumentConverter` (Python library) |
| HTTP API from any language | API server (docling-serve) — also `docling convert-remote` |
| Large-scale batch processing | Jobkit |
| AI agent integration | MCP server |

## MCP Server

Docling provides an MCP (Model Context Protocol) server for AI agent integration. See `docs/usage/mcp.md`. Remote mode can delegate to a docling-serve API endpoint with optional fallback to local conversion.

## API Server (docling-serve)

Run Docling as an HTTP service via [docling-serve](https://github.com/docling-project/docling-serve). The CLI's `convert-remote` subcommand targets a running service. Interactive API docs are served at `/docs`.

## Jobkit

Distributed document processing via [Docling Jobkit](https://github.com/docling-project/docling-jobkit) (`uv run docling-jobkit-local config.yaml`). Supports HTTP/S3/Google Drive connectors and Kubeflow/Ray/local pipeline backends. See `docs/usage/jobkit.md`.

## LangChain integration

`langchain_docling` provides a `DoclingLoader` for loading and chunking documents into LangChain:

```python
from langchain_docling import DoclingLoader

loader = DoclingLoader("documents/")
docs = loader.load()   # then embed/index with your vector store
```

See `docs/examples/rag_langchain.ipynb`.

## LlamaIndex integration

Docling integrates with LlamaIndex via the `BaseChunker` interface — any built-in, custom, or third-party chunker implementation works. See `docs/examples/rag_llamaindex.ipynb`.

## Other integrations

RAG examples in the repo cover Azure AI Search, Haystack, Milvus, MongoDB, OpenSearch, Weaviate, Qdrant, and top-k retrieval (`docs/examples/rag_*.ipynb`). Docling also integrates with CrewAI, Langflow, spacy, and more — see the integrations index in the docs.

## Plugin system

Docling uses `pluggy` for extensibility. Third-party developers register capabilities via setuptools entry points; OCR/layout/table engines register model classes plus an options class. Enable with `--allow-external-plugins`.
