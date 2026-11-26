# API Endpoints (v1)

The v1 API provides two convert endpoints — one for URLs/sources, one for files (binary multipart). Both accept the same `ConvertDocumentsOptions`.

## Endpoints

| Method | Path | Payload |
|---|---|---|
| POST | `/v1/convert/source` | JSON: `sources` / `http_sources` / `file_sources` + `options` |
| POST | `/v1/convert/file` | multipart form: `files` + flat option fields |
| POST | `/v1/convert/source/async` | same as source, returns task descriptor |
| POST | `/v1/convert/file/async` | same as file, returns task descriptor |
| GET | `/v1/status/poll/{task_id}` | — |
| WS | `/v1/status/ws/{task_id}` | — |
| GET | `/v1/result/{task_id}` | — |
| GET | `/v1/capabilities` | — (no API key) |

## Source endpoint

JSON payload. `http_sources` fetches URLs (optionally with extra headers); `file_sources` accepts base64-encoded documents. `options` can be partial or omitted entirely.

```json
{
  "http_sources": [{"url": "https://arxiv.org/pdf/2206.01062"}]
}
```

Large files: base64-encode locally and POST via a request-body file to avoid shell argument-length limits:

```sh
B64_DATA=$(base64 -w 0 /path/to/file.pdf)
cat <<EOF > /tmp/request_body.json
{
  "file_sources": [{"base64_string": "${B64_DATA}", "filename": "file.pdf"}]
}
EOF
curl -X POST localhost:5001/v1/convert/source \
     -H "Content-Type: application/json" \
     -d @/tmp/request_body.json
```

## File endpoint

Multipart form; repeatable fields for lists (`from_formats`, `to_formats`, `ocr_lang`, …) and multiple `files`.

```sh
curl -X 'POST' 'http://127.0.0.1:5001/v1/convert/file' \
  -H 'accept: application/json' \
  -F 'files=@document.pdf;type=application/pdf' \
  -F 'to_formats=md' \
  -F 'to_formats=text' \
  -F 'do_ocr=true'
```

### Callbacks

Both `/v1/convert/file` and `/v1/convert/file/async` accept an optional `callbacks` field (repeat once per endpoint). Each value is either a bare URL or a JSON-encoded object with optional headers and CA certificate:

| Format | Example |
|---|---|
| Bare URL | `https://hook.example.com/done` |
| JSON object | `{"url":"https://hook.example.com/done","headers":{"Authorization":"Bearer tok"}}` |

The server sends callbacks from its own network position. Disable with `DOCLING_SERVE_ENABLE_CALLBACKS=false`; per-request limit is `DOCLING_SERVE_MAX_CALLBACKS_PER_REQUEST` (default 5).

## Key convert options

Full field list lives in the live OpenAPI schema (`/openapi.json`). Highlights:

- `from_formats` — input formats (pdf, docx, pptx, xlsx, html, image, md, audio, video, epub, latex, …); defaults to all
- `to_formats` — output formats (`md`, `json`, `yaml`, `html`, `html_split_page`, `text`, `doctags`, `vtt`, `doclang`, `dclx`, `chunks`, `latex`); defaults to Markdown
- `image_export_mode` — `placeholder` (default), `embedded`, `referenced`
- `do_ocr` (default true), `force_ocr` (default false), `ocr_lang` (BCP-47 tags, e.g. `en`, `de-DE`; reserved tag `mul` must be used alone)
- `pdf_backend` — defaults to `docling_parse`
- `table_mode` — `fast` or `accurate` (default)
- `pipeline` — `standard` or `vlm`; admin may restrict via `DOCLING_SERVE_ALLOWED_PIPELINES`
- `page_range` — 1-based page tuple
- `document_timeout` — per-document timeout in seconds
- `do_table_structure` (default true), `include_images` (default true), `include_page_images` (default false), `images_scale` (default 2.0)
- `do_pdf_heading_hierarchy` (default false) + `pdf_heading_hierarchy_options` for section-header level inference
- Enrichment toggles: `do_code_enrichment`, `do_formula_enrichment`, `do_picture_classification`, `do_chart_extraction`, `do_picture_description`
- Preset selectors (preferred over deprecated explicit configs): `vlm_pipeline_preset`, `picture_description_preset`, `code_formula_preset`, `table_structure_preset`, `layout_preset`, `chunking_preset`
- `chunking_options` — Hybrid or Hierarchical chunker options (mutually exclusive with `chunking_preset`)

Deprecated: `ocr_engine`, `picture_description_local`, `picture_description_api`, `vlm_pipeline_model`, `vlm_pipeline_model_local`, `vlm_pipeline_model_api`.

## Response format

Single document → JSON:

```jsonc
{
  "document": {
    "md_content": "",
    "json_content": {},
    "html_content": "",
    "text_content": "",
    "doctags_content": ""
  },
  "status": "<success|partial_success|skipped|failure>",
  "processing_time": 0.0,
  "timings": {},
  "errors": []
}
```

Multiple inputs/outputs (or zip target mode) → a zip file. `processing_time` is Docling processing seconds; `timings` provides per-component breakdown when enabled.

## Async flow

Submission returns:

```jsonc
{
  "task_id": "<task_id>",
  "task_status": "pending|started|success|failure",
  "task_position": 1,
  "task_meta": null
}
```

Polling loop (Python sketch):

```python
while task["task_status"] not in ("success", "failure"):
    response = httpx.get(f"{base_url}/v1/status/poll/{task['task_id']}")
    task = response.json()
    time.sleep(5)
```

WebSocket messages: `{"message": "connection|update|error", "task": {...}, "error": ""}`.

## Capabilities endpoint

`GET /v1/capabilities` (no API key) describes what the deployment accepts: per-stage presets (`stages`), allowed `sources`/`targets`, `output_formats`, `image_export_modes`, `pipelines`, `limits` (e.g. `max_file_size`), and `features` (API key required, artifact storage enabled). Custom presets are listed by id only. Disable with `DOCLING_SERVE_ENABLE_CAPABILITIES_ENDPOINT=false`.
