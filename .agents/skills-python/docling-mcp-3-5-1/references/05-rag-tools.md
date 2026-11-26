# RAG tools (docling-mcp 3.5.1)

Optional tool groups for retrieval-augmented generation and structured extraction. Load them explicitly with `--tools`; they are not part of the default set.

## llama-index-rag

LlamaIndex-based RAG backed by a Milvus vector store. Install with `pip install docling-mcp[llama-index-rag]`. Configure via the `DOCLING_MCP_LI_` prefix (see [04-configuration](04-configuration.md)): `LI_API_BASE`, `LI_API_KEY`, `LI_MODEL_ID`, `LI_EMBEDDING_MODEL`.

## llama-stack-rag

LlamaStack RAG integration. Install with `pip install docling-mcp[llama-stack]` (Python ≥ 3.12). Configure via the `DOCLING_MCP_LLS_` prefix: `LLS_URL`, `LLS_VDB_EMBEDDING`.

## llama-stack-ie

LlamaStack structured information extraction. Same extra and config as `llama-stack-rag`; uses `LLS_EXTRACTION_MODEL` for the extraction model.

See the repo's `examples/llama-index`, `examples/llama-stack`, and `docs/applications/llama_index_rag.md` for full notebooks and setup.
