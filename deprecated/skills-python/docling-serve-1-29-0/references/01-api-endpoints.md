# API Endpoints

## Convert endpoints

### Synchronous

**`POST /v1/convert/source`** — Convert documents from URL or base64 sources. JSON body with `sources` array.

```json
{
  "sources": [
    {"kind": "http", "url": "https://example.com/doc.pdf"},
    {"kind": "file", "base64_string": "base64data...", "filename": "doc.pdf"}
  ],
  "options": {
    "to_formats": ["md", "json"],
    "do_ocr": true,
    "ocr_lang": ["en"]
  },
  "target": {"kind": "inbody"}
}
```

**`POST /v1/convert/file`** — Convert uploaded files via multipart form. All options are form fields.

```bash
curl -X POST 'http://localhost:5001/v1/convert/file' \
  -F 'files=@document.pdf;type=application/pdf' \
  -F 'to_formats=md' \
  -F 'do_ocr=true' \
  -F 'target_type=inbody'
```

Array fields (like `to_formats`, `from_formats`, `ocr_lang`) are sent as repeated form fields.

### Asynchronous

**`POST /v1/convert/source/async`** — Submit conversion from sources, returns `task_id`.

**`POST /v1/convert/file/async`** — Submit conversion from uploaded files, returns `task_id`.

**`POST /v1/convert/source/batch`** — Batch conversion with multiple sources and targets. Returns `task_id`.

```json
{
  "sources": [
    {"kind": "http", "url": "https://example.com/doc1.pdf"},
    {"kind": "http", "url": "https://example.com/doc2.pdf"}
  ],
  "target": {"kind": "zip"},
  "options": {"to_formats": ["md"]}
}
```

### Async workflow

1. **Submit**: `POST /v1/convert/source/async` → `{"task_id": "...", "task_status": "pending"}`
2. **Poll**: `GET /v1/status/poll/{task_id}?wait=0` → status updates
3. **Fetch**: `GET /v1/result/{task_id}` → conversion result or ZIP

### WebSocket status

**`WS /v1/status/ws/{task_id}?api_key=SECRET`** — Real-time task updates.

WebSocket messages (JSON):

```json
{"message": "connection", "task": {"task_id": "...", "task_status": "pending"}}
{"message": "update", "task": {"task_id": "...", "task_status": "started"}}
{"message": "update", "task": {"task_id": "...", "task_status": "success"}}
{"message": "error", "error": "Task not found."}
```

Client sends any message to request an update. Socket closes on completion.

## Chunking endpoints

### Hybrid chunker

- `POST /v1/chunk/hybrid/source` — sync, from sources
- `POST /v1/chunk/hybrid/file` — sync, from uploaded files
- `POST /v1/chunk/hybrid/source/async` — async, from sources
- `POST /v1/chunk/hybrid/file/async` — async, from uploaded files

### Hierarchical chunker

- `POST /v1/chunk/hierarchical/source` — sync, from sources
- `POST /v1/chunk/hierarchical/file` — sync, from uploaded files
- `POST /v1/chunk/hierarchical/source/async` — async, from sources
- `POST /v1/chunk/hierarchical/file/async` — async, from uploaded files

Chunking request (source):

```json
{
  "sources": [{"kind": "http", "url": "https://example.com/doc.pdf"}],
  "convert_options": {"do_ocr": true},
  "chunking_options": {
    "max_tokens": 512,
    "tokenizer": "sentence-transformers/all-MiniLM-L6-v2",
    "merge_peers": true
  },
  "include_converted_doc": false,
  "target": {"kind": "inbody"}
}
```

## Health and management

- `GET /health` — basic health check
- `GET /ready` — readiness (models loaded + orchestrator healthy)
- `GET /readyz` — Kubernetes readiness probe
- `GET /livez` — Kubernetes liveness probe
- `GET /version` — package versions (gateable via `DOCLING_SERVE_SHOW_VERSION_INFO`)
- `GET /metrics` — Prometheus metrics (gateable via `DOCLING_SERVE_OTEL_ENABLE_PROMETHEUS`)
- `GET /openapi-3.0.json` — OpenAPI 3.0 spec (downgraded from 3.1)
- `GET /openapi.json` — OpenAPI 3.1 spec
- `GET /docs` — ReDoc documentation
- `GET /swagger` — Swagger UI
- `GET /scalar` — Scalar API documentation

## Clear endpoints

- `GET /v1/clear/converters` — offload loaded models from cache
- `GET /v1/clear/results?older_then=3600` — clean old results (seconds)

## Management endpoints

- `GET /v1/memory/stats` — cgroup memory stats (gateable via `DOCLING_SERVE_ENABLE_MANAGEMENT_ENDPOINTS`)
- `GET /v1/memory/counts` — Python GC object counts

## Callback endpoint

- `POST /v1/callback/task/progress` — internal progress callback from workers

## Response schemas

### TaskStatusResponse

```json
{
  "task_id": "uuid",
  "task_type": "convert|chunk",
  "task_status": "pending|started|success|failure",
  "task_position": 1,
  "task_meta": {"total": 10, "converted": 3},
  "error_message": null,
  "failure": null
}
```

### ConvertDocumentResponse

```json
{
  "document": {
    "md_content": "# Title\n\nContent...",
    "json_content": {},
    "html_content": "<html>...",
    "text_content": "Plain text...",
    "doctags_content": "",
    "vtt_content": "",
    "doclang_content": "",
    "dclx_content": "",
    "chunks_content": []
  },
  "status": "success|partial_success|skipped|failure",
  "processing_time": 2.5,
  "timings": {},
  "errors": []
}
```

### ChunkDocumentResponse

```json
{
  "chunks": [
    {
      "text": "chunk content",
      "raw_text": "raw content",
      "metadata": {"page_number": 1, "has_image": false}
    }
  ],
  "status": "success",
  "processing_time": 1.2,
  "errors": []
}
```

## Source kinds

| Kind | Fields | Description |
|------|--------|-------------|
| `http` | `url`, `headers` | Fetch from URL |
| `file` | `base64_string`, `filename` | Inline base64 data |
| `local_path` | `path` | Local file (batch only, never available remotely) |
| Plugin kinds | varies | Third-party connectors (e.g., `filenet`, `gdrive`) |

## Target kinds

| Kind | Description |
|------|-------------|
| `inbody` | JSON response inline (default) |
| `zip` | ZIP archive download |
| `presigned_url` | Upload to artifact storage, return presigned URL |

## Authentication

When `DOCLING_SERVE_API_KEY` is set, all requests require `X-Api-Key` header. WebSocket uses `?api_key=SECRET` query parameter.

## Error responses

- `401` — Missing or invalid API key
- `403` — Management/version endpoints disabled
- `404` — Task not found, tenant mismatch
- `422` — Invalid request (validation errors)
- `503` — Server busy (Redis backpressure), dispatcher unavailable (Ray)
- `504` — Sync timeout (exceeded `DOCLING_SERVE_MAX_SYNC_WAIT`)
