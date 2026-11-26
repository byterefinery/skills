---
name: docling-serve-1-29-0
description: >
  Docling Serve 1.29.0 — FastAPI-based document conversion API service. Converts
  PDF, DOCX, PPTX, XLSX, HTML, images, audio, video, EPUB, LaTeX, and more into
  Markdown, JSON, HTML, text, DocTags, DCLX, or chunks. Use when running document
  conversion as a REST API, deploying Docling as a service, setting up async batch
  processing with polling or WebSocket updates, integrating MCP for AI tool use,
  or configuring compute engines (local, RQ/Redis, Ray) for distributed processing.
  Covers sync/async convert endpoints, source/target kinds, VLM presets, picture
  description, code/formula extraction, table structure, OCR, chunking, Gradio UI,
  OpenTelemetry, container images (CPU, CUDA, ROCm), and K8s deployments. Trigger
  on docling-serve, document conversion API, docling REST service, async document
  processing, docling MCP, batch conversion, docling container, docling deployment,
  docling RQ worker, docling Ray engine.
license: MIT
compatibility: >
  Python 3.10–3.13. Requires `docling-serve` Python package or container image.
  GPU variants need NVIDIA drivers >=550.54.14 with nvidia-container-toolkit,
  or AMD ROCm >=6.3. RQ engine requires Redis. Ray engine requires a Ray cluster.
  Container images range from 4.4–11.4 GB depending on variant.
metadata:
  tags:
    - document-processing
    - api
    - pdf
    - ocr
    - fastapi
    - python
    - ai
    - docker
    - kubernetes
---

# docling-serve 1.29.0

## Overview

Docling Serve is a production-ready FastAPI service that exposes [Docling](https://github.com/docling-project/docling) document conversion as a REST API. It supports synchronous and asynchronous conversion of PDF, DOCX, PPTX, XLSX, HTML, images, audio, video, EPUB, LaTeX, and other formats into Markdown, JSON, HTML, text, DocTags, DCLX, or text chunks.

Key capabilities:

- **Two convert endpoints** — `/v1/convert/source` (JSON with URL/base64 sources) and `/v1/convert/file` (multipart file upload)
- **Async processing** — submit jobs, poll status, or subscribe via WebSocket for real-time updates
- **Three compute engines** — local (in-process threads), RQ (Redis-backed workers), Ray (distributed autoscaling)
- **MCP server** — built-in Model Communication Protocol endpoint for AI agent integration
- **Gradio UI** — optional web playground at `/ui`
- **OpenTelemetry** — metrics, traces, and Prometheus `/metrics` endpoint
- **Container images** — PyPI, CPU-only, CUDA 12.8, CUDA 13.0, ROCm variants

## Usage

### Installation and startup

```bash
# Python package
pip install "docling-serve[ui]"
docling-serve run --enable-ui

# Container (PyPI base)
podman run -p 5001:5001 -e DOCLING_SERVE_ENABLE_UI=1 quay.io/docling-project/docling-serve

# CPU-only image (smaller, no GPU)
podman run -p 5001:5001 quay.io/docling-project/docling-serve-cpu

# CUDA 12.8 image
podman run -p 5001:5001 --gpus all quay.io/docling-project/docling-serve-cu128:1.29.0
```

Server endpoints:

- API: `http://127.0.0.1:5001`
- Docs: `http://127.0.0.1:5001/docs`
- Scalar docs: `http://127.0.0.1:5001/scalar`
- UI: `http://127.0.0.1:5001/ui` (when `--enable-ui`)

### Synchronous conversion

**Source endpoint** — send URLs or base64-encoded files as JSON:

```bash
curl -X POST 'http://localhost:5001/v1/convert/source' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "sources": [{"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"}]
  }'
```

**File endpoint** — upload files via multipart form:

```bash
curl -X POST 'http://localhost:5001/v1/convert/file' \
  -H 'accept: application/json' \
  -F 'files=@document.pdf;type=application/pdf' \
  -F 'to_formats=md' \
  -F 'do_ocr=true'
```

**Base64 inline** — for small files, embed directly in JSON:

```bash
B64=$(base64 -w 0 document.pdf)
cat > /tmp/request.json <<EOF
{
  "sources": [{"kind": "file", "base64_string": "${B64}", "filename": "document.pdf"}]
}
EOF
curl -X POST 'http://localhost:5001/v1/convert/source' \
  -H 'Content-Type: application/json' \
  -d @/tmp/request.json
```

### Asynchronous conversion

Submit a job and get a `task_id`:

```bash
curl -X POST 'http://localhost:5001/v1/convert/source/async' \
  -H 'Content-Type: application/json' \
  -d '{
    "sources": [{"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"}]
  }'
# Response: {"task_id": "...", "task_status": "pending", ...}
```

Poll for status:

```bash
curl "http://localhost:5001/v1/status/poll/{task_id}"
```

Fetch result when complete:

```bash
curl "http://localhost:5001/v1/result/{task_id}"
```

Subscribe via WebSocket for real-time updates:

```python
from websockets.sync.client import connect
import json

uri = f"ws://localhost:5001/v1/status/ws/{task_id}"
with connect(uri) as ws:
    for msg in ws:
        payload = json.loads(msg)
        if payload["message"] == "error":
            break
        if payload["message"] == "update":
            status = payload["task"]["task_status"]
            if status in ("success", "failure"):
                break
```

### Conversion options

Common options in the `options` object:

```json
{
  "sources": [{"kind": "http", "url": "https://example.com/doc.pdf"}],
  "options": {
    "from_formats": ["pdf", "docx"],
    "to_formats": ["md", "json"],
    "image_export_mode": "embedded",
    "do_ocr": true,
    "ocr_preset": "auto",
    "ocr_lang": ["en"],
    "pdf_backend": "docling_parse",
    "table_mode": "accurate",
    "do_table_structure": true,
    "include_images": true,
    "images_scale": 2.0,
    "page_range": [1, 10],
    "document_timeout": 300.0,
    "abort_on_error": false,
    "chunking_preset": "granite_embedding_278m"
  }
}
```

Output format target (ZIP archive instead of inline JSON):

```json
{
  "sources": [{"kind": "http", "url": "https://example.com/doc.pdf"}],
  "target": {"kind": "zip"}
}
```

### Authentication

Set an API key and require it on all requests:

```bash
export DOCLING_SERVE_API_KEY=your-secret-key
docling-serve run
```

```bash
curl -X POST 'http://localhost:5001/v1/convert/source' \
  -H 'X-Api-Key: your-secret-key' \
  -H 'Content-Type: application/json' \
  -d '{"sources": [{"kind": "http", "url": "https://example.com/doc.pdf"}]}'
```

### MCP server

Start the MCP server for AI agent integration:

```bash
podman run -p 8000:8000 quay.io/docling-project/docling-serve \
  -- docling-mcp-server --transport streamable-http --port 8000 --host 0.0.0.0
```

Configure in MCP clients (LM Studio, Claude Desktop):

```json
{
  "mcpServers": {
    "docling": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Compute engines

**Local** (default, in-process threads):

```bash
export DOCLING_SERVE_ENG_KIND=local
export DOCLING_SERVE_ENG_LOC_NUM_WORKERS=4
docling-serve run
```

**RQ** (Redis-backed workers, for horizontal scaling):

```bash
# API server
export DOCLING_SERVE_ENG_KIND=rq
export DOCLING_SERVE_ENG_RQ_REDIS_URL=redis://localhost:6379/
docling-serve run

# Separate worker process
docling-serve rq-worker
```

**Ray** (distributed autoscaling):

```bash
export DOCLING_SERVE_ENG_KIND=ray
export DOCLING_SERVE_ENG_RAY_ADDRESS=auto
export DOCLING_SERVE_ENG_RAY_REDIS_URL=redis://localhost:6379/
docling-serve run
```

### Configuration

All settings support environment variables (`DOCLING_SERVE_*`) and YAML/JSON config files:

```bash
export DOCLING_SERVE_CONFIG_FILE=config.yaml
```

```yaml
# config.yaml
enable_ui: true
enable_remote_services: true
max_num_pages: 500
max_file_size: 104857600
options_cache_size: 4
eng_kind: local
eng_loc_num_workers: 4
log_format: json
otel_enable_metrics: true
otel_enable_prometheus: true
```

Priority: environment variables > config file > defaults.

### Model management

Models are loaded from `DOCLING_SERVE_ARTIFACTS_PATH`. Pre-download models for production:

```bash
# Download all models
docling-tools models download --all -o /models

# Container with mounted models
podman run -p 5001:5001 \
  -v $(pwd)/models:/models \
  -e DOCLING_SERVE_ARTIFACTS_PATH=/models \
  quay.io/docling-project/docling-serve
```

For Kubernetes, use a PVC + Job pattern — download models into a persistent volume before starting the deployment.

### Container images

| Image | Description | Size |
|-------|-------------|------|
| `docling-serve` | PyPI base (all architectures) | 4.4–8.7 GB |
| `docling-serve-cpu` | CPU-only PyTorch | 4.4 GB |
| `docling-serve-cu128` | CUDA 12.8 | 11.4 GB |
| `docling-serve-cu130` | CUDA 13.0 | TBD |

CUDA images use explicit version tags only (no `latest`). Always pin: `quay.io/docling-project/docling-serve-cu128:1.29.0`.

## Gotchas

- **`--reload` and `--workers` ignore CLI args** — when uvicorn spawns subprocesses, only environment variables are inherited. Always use `DOCLING_SERVE_*` env vars with reload or multi-worker mode.
- **CUDA images have no `latest` tag** — they follow PyTorch's CUDA lifecycle. Always use explicit version tags like `:1.29.0` to avoid pulling deprecated CUDA versions.
- **`sources` replaces `http_sources`/`file_sources`** — the v1 API unified input into a single `sources` array with `kind` field (`"http"`, `"file"`, or plugin kinds). The old v1alpha fields are gone.
- **`target` replaces `return_as_file`** — to get a ZIP response, use `"target": {"kind": "zip"}` instead of `options.return_as_file`.
- **Models are not auto-downloaded in containers** — if a required model is missing from the artifacts path, Docling Serve raises a runtime error. Pre-download with `docling-tools models download` or mount a volume.
- **`DOCLING_SERVE_ARTIFACTS_PATH` must match mount path** — the env var value must exactly match the container mount point where models are stored.
- **`DOCLING_SERVE_ENABLE_REMOTE_SERVICES=true` required for API-based VLM** — picture description via external API endpoints (OpenAI-compatible, Ollama, vLLM) needs this flag enabled.
- **RQ requires `eng_rq_redis_url`** — the RQ engine validates that the Redis URL is set at startup. Without it, the server fails to start.
- **Ray requires both `eng_ray_address` and `eng_ray_redis_url`** — both must be explicitly set. Use `auto` or `local` for local Ray.
- **Base64 in curl can hit argument length limits** — for large files, write the JSON to a file and use `curl -d @file.json` instead of inline base64.
- **`--enable-ui` requires gradio extra** — install with `pip install "docling-serve[ui]"` or use the base container image (UI is included by default in containers).
- **Gradio file cache cleanup** — Gradio caches output files. Set `GRADIO_TEMP_DIR` to match `DOCLING_SERVE_SCRATCH_PATH` if you need files available beyond 10 hours.
- **`DOCLING_SERVE_SINGLE_USE_RESULTS=true` (default)** — results are removed after one fetch. Set to `false` if clients need to re-fetch results.
- **`/v1/convert/file` uses multipart form** — all options are sent as form fields, not JSON. Array values (like `to_formats`) are repeated fields.
- **Config file priority** — environment variables override config file values, which override defaults. Use config files for complex nested structures (presets, custom configs).

## References

- [01-api-endpoints](references/01-api-endpoints.md) — Full endpoint reference, request/response schemas, async workflow
- [02-configuration](references/02-configuration.md) — Environment variables, config files, compute engine settings, presets
- [03-deployment](references/03-deployment.md) — Container images, Docker Compose, Kubernetes/OpenShift manifests, GPU setups
- [04-models](references/04-models.md) — Model management, artifacts path, pre-download strategies, PVC patterns
- [05-mcp](references/05-mcp.md) — MCP server setup, client configuration, integrations
