# API Server

Chonkie can run as a self-hosted REST API server. Requires `chonkie[api]`.

---

## Installation

```bash
pip install "chonkie[api,semantic,code,catsu]"
```

Installs: FastAPI, uvicorn, SQLAlchemy, alembic, aiosqlite, huggingface-hub, jsonschema.

---

## Starting the Server

```bash
# Via CLI
chonkie serve

# With options
chonkie serve --port 3000 --reload --log-level debug

# Via uvicorn
uvicorn chonkie.api.main:app --host 0.0.0.0 --port 8000
```

---

## Docker

```bash
docker compose up
```

---

## Endpoints

### Chunking

```bash
# Token chunking
curl -X POST http://localhost:8000/v1/chunk/token \
  -H "Content-Type: application/json" \
  -d '{"text": "Your document text...", "chunk_size": 512}'

# Recursive chunking
curl -X POST http://localhost:8000/v1/chunk/recursive \
  -H "Content-Type: application/json" \
  -d '{"text": "Your document text...", "chunk_size": 512}'

# Semantic chunking
curl -X POST http://localhost:8000/v1/chunk/semantic \
  -H "Content-Type: application/json" \
  -d '{"text": "Your document text...", "chunk_size": 512}'
```

### Refineries

```bash
# Overlap
curl -X POST http://localhost:8000/v1/refine/overlap \
  -H "Content-Type: application/json" \
  -d '{"chunks": [...], "context_size": 64}'

# Embeddings
curl -X POST http://localhost:8000/v1/refine/embeddings \
  -H "Content-Type: application/json" \
  -d '{"chunks": [...], "embedding_model": "minishlab/potion-retrieval-32M"}'
```

### Pipelines

```bash
# Create a reusable pipeline
curl -X POST http://localhost:8000/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "rag-chunker",
    "steps": [
      {"type": "chunk", "chunker": "semantic", "config": {"chunk_size": 512}},
      {"type": "refine", "refinery": "embeddings", "config": {"embedding_model": "text-embedding-3-small"}}
    ]
  }'

# List pipelines
curl http://localhost:8000/v1/pipelines

# Run a pipeline
curl -X POST http://localhost:8000/v1/pipelines/rag-chunker/run \
  -H "Content-Type: application/json" \
  -d '{"text": "Your document text..."}'
```

Pipelines are stored in a local SQLite database and can be reused across requests.

---

## Interactive Docs

When the server is running, interactive Swagger UI is available at `http://localhost:8000/docs`.

---

## Architecture

- **FastAPI** — web framework
- **uvicorn** — ASGI server
- **SQLAlchemy** — ORM for pipeline persistence
- **alembic** — database migrations
- **aiosqlite** — async SQLite driver

The API server exposes all chunkers, refineries, and pipeline management through REST endpoints. Pipeline configurations are persisted in SQLite for reuse.
