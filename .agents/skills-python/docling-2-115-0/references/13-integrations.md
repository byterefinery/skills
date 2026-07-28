# Integrations

## MCP Server

Docling provides an MCP (Model Context Protocol) server for AI agent integration.

### Installation

```bash
# Via uvx (recommended)
uvx --from=docling-mcp docling-mcp-server
```

### Claude Desktop configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docling": {
      "command": "uvx",
      "args": ["--from=docling-mcp", "docling-mcp-server"]
    }
  }
}
```

### LM Studio

Add to `mcp.json` or use the direct install link from the Docling docs.

### Remote mode (delegate to API server)

```bash
export DOCLING_SERVICE_URL=https://your-docling-service.example.com
export DOCLING_SERVICE_API_KEY=your-api-key
export DOCLING_CONVERSION_MODE=remote

# Fallback to local if remote unavailable
export DOCLING_FALLBACK_TO_LOCAL=true
```

Requires `pip install "docling-mcp[local]"` for fallback support.

## API Server (docling-serve)

Run Docling as an HTTP service via [docling-serve](https://github.com/docling-project/docling-serve).

### Quick start

```bash
# Start local server (defaults to http://localhost:5001)
# Interactive API docs at /docs

# Convert via HTTP
curl -X POST "http://localhost:5001/v1/convert/source/async" \
  -H "Content-Type: application/json" \
  -d '{"http_sources": [{"url": "https://arxiv.org/pdf/2501.17887"}]}'
```

### When to use what

| Use case | Tool |
|----------|------|
| In-process Python | `DocumentConverter` (Python library) |
| HTTP API from any language | **API server** (docling-serve) |
| Large-scale batch processing | **Jobkit** |
| AI agent integration | **MCP server** |

## Jobkit

Distributed document processing via [Docling Jobkit](https://github.com/docling-project/docling-jobkit).

### Local execution

```bash
uv run docling-jobkit-local config.yaml
```

### Configuration

```yaml
options:
  do_ocr: false

sources:
  - kind: google_drive
    path_id: 1X6B3j7GWlHfIPSF9VUkasN-z49yo1sGFA9xv55L2hSE
    token_path: "./google_drive_token.json"
    credentials_path: "./google_drive_credentials.json"

target:
  kind: s3
  endpoint: localhost:9000
  verify_ssl: false
  bucket: docling-target
  access_key: minioadmin
  secret_key: minioadmin
```

### Supported connectors

- HTTP endpoints
- S3
- Google Drive

### Pipeline backends

- Kubeflow pipelines
- Ray
- Local execution

## LangChain integration

### DoclingLoader

```python
from langchain_docling import DoclingLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Load and chunk documents
loader = DoclingLoader("documents/")
docs = loader.load()

# Embed and index
vectorstore = FAISS.from_documents(docs, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# Query
results = retriever.invoke("What are the key findings?")
```

### Audio RAG pipeline

```python
# Load all audio files
loader = DoclingLoader("recordings/")
docs = loader.load()

vectorstore = FAISS.from_documents(docs, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

results = retriever.invoke("What did we decide about the auth service?")
```

## LlamaIndex integration

Docling integrates with LlamaIndex via the `BaseChunker` interface. Any built-in, custom, or third-party chunker implementation works.

See the [Docling MCP Server repository](https://github.com/docling-project/docling-mcp) for LlamaIndex and Llama Stack examples.

## Other integrations

Docling provides integrations with:

- **CrewAI** — agentic AI workflows
- **Haystack** — NLP pipeline framework
- **Langflow** — visual LangChain builder
- **InstructLab** — model fine-tuning
- **txtai** — AI-powered semantic search
- **Vectara** — enterprise RAG platform
- **spacy** — NLP processing
- **Prodigy** — data annotation
- **Open WebUI** — chat interface
- **NVIDIA** — AI enterprise platform
- **Quarkus** — Java/Kotlin framework
- **RHEL AI** — Red Hat AI platform
- **Cloudera** — data platform
- **Apify** — web automation
- **And more** — see the [integrations index](https://docling-project.github.io/docling/integrations/)

## Plugin system

Docling uses [pluggy](https://github.com/pytest-dev/pluggy) for extensibility. Third-party developers register capabilities via setuptools entry points:

```toml
# pyproject.toml
[project.entry-points."docling"]
your_plugin_name = "your_package.module"
```

### OCR plugin factory

```python
def ocr_engines():
    return {
        "ocr_engines": [YourOcrModel],
    }
```

`YourOcrModel` must implement `BaseOcrModel` and provide an options class derived from `OcrOptions`.
