---
name: docling-serve-1-40-0
description: >
  Docling Serve 1.40.0 — FastAPI-based document conversion API service built on
  the stable v1 API. Converts PDF, DOCX, PPTX, XLSX, HTML, images, audio, video,
  EPUB, LaTeX, and more into Markdown, JSON, YAML, HTML, text, DocTags, DCLX,
  VTT, chunks, or LaTeX. Use when running document conversion as a REST API,
  deploying Docling as a service, setting up async batch processing with polling
  or WebSocket updates, integrating MCP for AI tool use, or configuring compute
  engines (local, RQ/Redis, Ray) for distributed processing. Covers sync/async
  convert endpoints, source/target kinds, capabilities endpoint, VLM presets,
  picture description, code/formula extraction, table structure, OCR, chunking,
  the /ui playground, OpenTelemetry, container images (CPU, CUDA), and K8s
  deployments. Trigger on docling-serve, document conversion API, docling REST
  service, async document processing, docling MCP, batch conversion, docling
  container, docling deployment, docling RQ worker, docling Ray engine.
license: MIT
compatibility: >
  Python package `docling-serve` or container image (quay.io / ghcr.io
  docling-project/docling-serve). GPU variants need NVIDIA drivers with
  nvidia-container-toolkit. RQ engine requires Redis; Ray engine requires a Ray
  cluster. Container images range from 4.4 GB (CPU) to 11.4 GB (CUDA 12.8).
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

# docling-serve 1.40.0

## Overview

Docling Serve is a FastAPI service that exposes [Docling](https://github.com/docling-project/docling) document conversion as a REST API with a stable `v1` API surface. It converts PDF, DOCX, PPTX, XLSX, HTML, images, audio, video, EPUB, LaTeX, and other formats into Markdown, JSON, YAML, HTML, text, DocTags, DCLX, VTT, chunks, or LaTeX.

Key capabilities:

- **Two convert endpoints** — `/v1/convert/source` (JSON payload with URL or base64 sources) and `/v1/convert/file` (multipart file upload)
- **Async processing** — submit jobs, poll status, or subscribe via WebSocket for real-time updates
- **Three compute engines** — local (in-process threads), RQ (Redis-backed workers), Ray (distributed)
- **MCP server** — the container image ships `docling-mcp-server` for AI agent integration
- **Web UI playground** — optional static app at `/ui`
- **Capabilities endpoint** — `GET /v1/capabilities` describes presets, sources, targets, limits, and features of the running deployment (no API key needed)
- **OpenTelemetry** — metrics, traces, and a Prometheus `/metrics` endpoint

## Usage

### Run the server

```bash
# Python package
pip install docling-serve
docling-serve run --enable-ui

# Container image
podman run -p 5001:5001 -e DOCLING_SERVE_ENABLE_UI=1 quay.io/docling-project/docling-serve
```

Endpoints once running on the default port 5001:

- API <http://127.0.0.1:5001>
- API docs (Swagger/Scalar) <http://127.0.0.1:5001/docs>
- UI playground <http://127.0.0.1:5001/ui>

### Convert from a URL (source endpoint)

```bash
curl -X 'POST' \
  'http://localhost:5001/v1/convert/source' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "sources": [{"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"}]
  }'
```

The payload takes `options` (partially or fully omittable) plus source entries; files can also be sent as base64 strings in the same JSON body. See [01-api-endpoints](references/01-api-endpoints.md) for full option tables, file upload, callbacks, and response formats.

### Convert a local file (file endpoint)

```bash
curl -X 'POST' \
  'http://127.0.0.1:5001/v1/convert/file' \
  -H 'accept: application/json' \
  -F 'files=@document.pdf;type=application/pdf' \
  -F 'to_formats=md' \
  -F 'do_ocr=true'
```

### Async conversion

`POST /v1/convert/source/async` and `POST /v1/convert/file/async` return a task descriptor (`task_id`, `task_status`, `task_position`, `task_meta`). Then:

- Poll with `GET /v1/status/poll/{task_id}`
- Subscribe with WebSocket `/v1/status/ws/{task_id}`
- Fetch the result with `GET /v1/result/{task_id}`

### Authentication

When `DOCLING_SERVE_API_KEY` is set, every API request must send the header `X-Api-Key` with that value. The `/docs`, `/openapi.json`, and `/v1/capabilities` routes need no key.

## Gotchas

- **CLI options are ignored under `--reload` or multiple `--workers`** — uvicorn spawns subprocesses that do not inherit CLI values; use environment variables (`UVICORN_*`, `DOCLING_SERVE_*`) in those deployments.
- **Use 1 worker with the local engine** — with `local` tasks live per worker process, so async task lookups can return 404 across workers. Use `--workers 1` or switch to the RQ engine.
- **Missing models are a runtime error, not an auto-download** — the standard image ships only default models; extra models (smolvlm, granite_vision, easyocr, tableformer, …) must be pre-downloaded into `DOCLING_SERVE_ARTIFACTS_PATH` or fetched via `docling-tools models download`.
- **`picture_description_api` / remote VLMs require `DOCLING_SERVE_ENABLE_REMOTE_SERVICES=true`** — otherwise the server refuses pipeline components that make outbound connections.
- **Custom VLM/picture-description/code-formula configs are off by default** — `*_custom_config` request fields only work when the matching `DOCLING_SERVE_ALLOW_CUSTOM_*_CONFIG` is enabled; otherwise only presets are accepted.
- **CUDA container images have no `latest` tag** — pull explicit versions (e.g., `quay.io/docling-project/docling-serve-cu128:v1.40.0`); only base and `-cpu` images carry `latest`/`main`.
- **Deprecated options still appear in docs** — `ocr_engine`, `picture_description_local/api`, and `vlm_pipeline_model*` are deprecated; prefer `ocr_preset`, `picture_description_preset`/`_custom_config`, and `vlm_pipeline_preset`/`_custom_config`.
- **Results may be single-use** — with the default `DOCLING_SERVE_SINGLE_USE_RESULTS=true`, a task result can be fetched only once; keep `DOCLING_SERVE_RESULT_REMOVAL_DELAY` in mind when retrying.

## References

- [01-api-endpoints](references/01-api-endpoints.md) — convert endpoints, request options, callbacks, async flow, response format
- [02-configuration](references/02-configuration.md) — CLI/env configuration, compute engines (local/RQ/Ray), presets and converter manager controls
- [03-models](references/03-models.md) — making extra models available, artifacts path, K8s model-cache pattern
- [04-mcp](references/04-mcp.md) — running the MCP server from the container image and wiring up MCP clients
