# Configuration

## Environment variable prefix

All Docling Serve settings use `DOCLING_SERVE_` prefix. Uvicorn settings use `UVICORN_` prefix.

## Config file support

Load settings from YAML or JSON:

```bash
export DOCLING_SERVE_CONFIG_FILE=config.yaml
```

Priority: environment variables > config file > defaults.

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
```

## Webserver settings (Uvicorn)

| ENV | Default | Description |
|-----|---------|-------------|
| `UVICORN_HOST` | `0.0.0.0` (run), `127.0.0.1` (dev) | Bind address |
| `UVICORN_PORT` | `5001` | Port |
| `UVICORN_RELOAD` | `false` (run), `true` (dev) | Auto-reload on code change |
| `UVICORN_WORKERS` | `1` | Worker processes |
| `UVICORN_ROOT_PATH` | `""` | Path prefix behind proxy |
| `UVICORN_PROXY_HEADERS` | `true` | Trust X-Forwarded-* headers |
| `UVICORN_TIMEOUT_KEEP_ALIVE` | `60` | Keep-alive timeout (seconds) |
| `UVICORN_SSL_CERTFILE` | | SSL certificate path |
| `UVICORN_SSL_KEYFILE` | | SSL key path |
| `UVICORN_SSL_KEYFILE_PASSWORD` | | SSL key password |

## Core settings

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_ENABLE_UI` | `false` | Enable Gradio UI at `/ui` |
| `DOCLING_SERVE_API_KEY` | | API key for `X-Api-Key` auth |
| `DOCLING_SERVE_ARTIFACTS_PATH` | | Directory for model weights |
| `DOCLING_SERVE_STATIC_PATH` | | Directory for offline docs assets |
| `DOCLING_SERVE_SCRATCH_PATH` | | Scratch workspace for results |
| `DOCLING_SERVE_LOAD_MODELS_AT_BOOT` | `true` | Pre-load default models at startup |
| `DOCLING_SERVE_OPTIONS_CACHE_SIZE` | `2` | Cached DocumentConverter instances |
| `DOCLING_SERVE_ENABLE_REMOTE_SERVICES` | `false` | Allow remote API calls (VLM, etc.) |
| `DOCLING_SERVE_ALLOW_EXTERNAL_PLUGINS` | `false` | Allow third-party connectors |
| `DOCLING_SERVE_SHOW_VERSION_INFO` | `true` | Show `/version` endpoint |
| `DOCLING_SERVE_ENABLE_MANAGEMENT_ENDPOINTS` | `false` | Enable `/v1/memory/*` endpoints |
| `DOCLING_SERVE_DEBUG_ERROR_DETAILS` | `false` | Return raw exception details |
| `DOCLING_SERVE_SINGLE_USE_RESULTS` | `true` | Remove results after one fetch |
| `DOCLING_SERVE_RESULT_REMOVAL_DELAY` | `300` | Delay before result removal (seconds) |
| `DOCLING_SERVE_MAX_DOCUMENT_TIMEOUT` | `604800` | Max processing time (7 days) |
| `DOCLING_SERVE_MAX_NUM_PAGES` | unlimited | Max pages per document |
| `DOCLING_SERVE_MAX_FILE_SIZE` | unlimited | Max file size (bytes) |
| `DOCLING_SERVE_MAX_SYNC_WAIT` | `120` | Sync endpoint timeout (seconds) |
| `DOCLING_SERVE_SYNC_POLL_INTERVAL` | `2` | Poll interval in sync wait (seconds) |

## CORS settings

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_CORS_ORIGINS` | `["*"]` | Allowed origins |
| `DOCLING_SERVE_CORS_METHODS` | `["*"]` | Allowed HTTP methods |
| `DOCLING_SERVE_CORS_HEADERS` | `["*"]` | Allowed request headers |

## Logging

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_LOG_LEVEL` | `WARNING` | `WARNING`, `INFO`, `DEBUG` |
| `DOCLING_SERVE_LOG_FORMAT` | `text` | `text` (colored) or `json` (structured) |
| `DOCLING_SERVE_LOG_HEADER_PREFIX` | `X-Docling-Log-` | Header prefix for log propagation |

Headers matching the prefix are extracted and included in all logs during the request. E.g., `X-Docling-Log-RequestID: req-123` appears as `"RequestID": "req-123"` in JSON logs.

## Compute engine: Local

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_ENG_KIND` | `local` | Set to `local`, `rq`, or `ray` |
| `DOCLING_SERVE_ENG_LOC_NUM_WORKERS` | `2` | Thread workers |
| `DOCLING_SERVE_ENG_LOC_SHARE_MODELS` | `false` | Share models across threads |

## Compute engine: RQ (Redis Queue)

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_ENG_RQ_REDIS_URL` | (required) | Redis connection URL |
| `DOCLING_SERVE_ENG_RQ_QUEUE_NAME` | `convert` | RQ queue name |
| `DOCLING_SERVE_ENG_RQ_RESULTS_PREFIX` | `docling:results` | Redis key prefix for results |
| `DOCLING_SERVE_ENG_RQ_SUB_CHANNEL` | `docling:updates` | Pub/sub channel |
| `DOCLING_SERVE_ENG_RQ_RESULTS_TTL` | `14400` | Result TTL (4 hours) |
| `DOCLING_SERVE_ENG_RQ_REDIS_MAX_CONNECTIONS` | `50` | Connection pool size |
| `DOCLING_SERVE_ENG_RQ_REDIS_SOCKET_TIMEOUT` | | Socket timeout (seconds) |
| `DOCLING_SERVE_ENG_RQ_REDIS_SOCKET_CONNECT_TIMEOUT` | | Connect timeout (seconds) |

RQ worker process: `docling-serve rq-worker`

Scaling: set `REDIS_MAX_CONNECTIONS` to 100 for 5-10 workers, 150-200 for 10+ workers.

## Compute engine: Ray

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_ENG_RAY_ADDRESS` | (required) | Ray cluster address (`auto`, `local`, or URL) |
| `DOCLING_SERVE_ENG_RAY_REDIS_URL` | (required) | Redis for Ray pub/sub |
| `DOCLING_SERVE_ENG_RAY_NAMESPACE` | `docling` | Ray namespace |
| `DOCLING_SERVE_ENG_RAY_MIN_ACTORS` | `1` | Minimum serve replicas |
| `DOCLING_SERVE_ENG_RAY_MAX_ACTORS` | `10` | Maximum serve replicas |
| `DOCLING_SERVE_ENG_RAY_TARGET_REQUESTS_PER_REPLICA` | `1.0` | Autoscaling target |
| `DOCLING_SERVE_ENG_RAY_UPSCALE_DELAY_S` | `30.0` | Delay before scaling up |
| `DOCLING_SERVE_ENG_RAY_DOWNSCALE_DELAY_S` | `600.0` | Delay before scaling down |
| `DOCLING_SERVE_ENG_RAY_MAX_CONCURRENT_TASKS` | `5` | Max concurrent tasks per user |
| `DOCLING_SERVE_ENG_RAY_MAX_QUEUED_TASKS` | | Max queued tasks per user |
| `DOCLING_SERVE_ENG_RAY_TASK_TIMEOUT` | `3600.0` | Task timeout (seconds) |
| `DOCLING_SERVE_ENG_RAY_MAX_TASK_RETRIES` | `3` | Max retries per task |
| `DOCLING_SERVE_ENG_RAY_RETRY_DELAY` | `5.0` | Retry delay (seconds) |
| `DOCLING_SERVE_ENG_RAY_CONVERTER_ACTOR_NUM_CPUS` | `1.0` | CPUs per converter actor |
| `DOCLING_SERVE_ENG_RAY_CONVERTER_ACTOR_MEMORY_REQUEST` | | Memory request per actor |
| `DOCLING_SERVE_ENG_RAY_ENABLE_PDF_PAGE_SLICE_FANOUT` | `false` | Enable page-level parallelism |
| `DOCLING_SERVE_ENG_RAY_MAX_PAGE_SLICE_SIZE` | `32` | Max pages per slice |
| `DOCLING_SERVE_ENG_RAY_TENANT_ID_HEADER` | `X-Tenant-Id` | Header for tenant isolation |

## Preset controls

### VLM Pipeline

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_DEFAULT_VLM_PRESET` | `granite_docling` | Default VLM preset |
| `DOCLING_SERVE_ALLOWED_VLM_PRESETS` | all | Allowed preset IDs (JSON array or comma-separated) |
| `DOCLING_SERVE_CUSTOM_VLM_PRESETS` | `{}` | Custom presets (JSON object) |
| `DOCLING_SERVE_ALLOWED_VLM_ENGINES` | all | Allowed engine types |
| `DOCLING_SERVE_ALLOW_CUSTOM_VLM_CONFIG` | `false` | Allow fully custom VLM config |

### Picture Description

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_DEFAULT_PICTURE_DESCRIPTION_PRESET` | `smolvlm` | Default preset |
| `DOCLING_SERVE_ALLOWED_PICTURE_DESCRIPTION_PRESETS` | all | Allowed presets |
| `DOCLING_SERVE_CUSTOM_PICTURE_DESCRIPTION_PRESETS` | `{}` | Custom presets |
| `DOCLING_SERVE_ALLOW_CUSTOM_PICTURE_DESCRIPTION_CONFIG` | `false` | Allow custom config |

### Code/Formula

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_DEFAULT_CODE_FORMULA_PRESET` | `default` | Default preset |
| `DOCLING_SERVE_ALLOWED_CODE_FORMULA_PRESETS` | all | Allowed presets |
| `DOCLING_SERVE_CUSTOM_CODE_FORMULA_PRESETS` | `{}` | Custom presets |
| `DOCLING_SERVE_ALLOW_CUSTOM_CODE_FORMULA_CONFIG` | `false` | Allow custom config |

### Table Structure

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_DEFAULT_TABLE_STRUCTURE_KIND` | `docling_tableformer` | Default kind |
| `DOCLING_SERVE_DEFAULT_TABLE_STRUCTURE_PRESET` | `tableformer_v1_accurate` | Default preset |
| `DOCLING_SERVE_ALLOWED_TABLE_STRUCTURE_KINDS` | all | Allowed kinds |
| `DOCLING_SERVE_ALLOWED_TABLE_STRUCTURE_PRESETS` | all | Allowed presets |
| `DOCLING_SERVE_CUSTOM_TABLE_STRUCTURE_PRESETS` | `{}` | Custom presets |

### Layout

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_DEFAULT_LAYOUT_KIND` | `docling_layout_default` | Default kind |
| `DOCLING_SERVE_DEFAULT_LAYOUT_PRESET` | `docling_layout_default` | Default preset |
| `DOCLING_SERVE_ALLOWED_LAYOUT_KINDS` | all | Allowed kinds |
| `DOCLING_SERVE_ALLOWED_LAYOUT_PRESETS` | all | Allowed presets |
| `DOCLING_SERVE_CUSTOM_LAYOUT_PRESETS` | `{}` | Custom presets |

### OCR

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_DEFAULT_OCR_PRESET` | `auto` | Default preset |
| `DOCLING_SERVE_DEFAULT_OCR_KIND` | `auto` | Default kind |
| `DOCLING_SERVE_ALLOWED_OCR_PRESETS` | all | Allowed presets |
| `DOCLING_SERVE_ALLOWED_OCR_KINDS` | all | Allowed kinds |

### Chunking

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_DEFAULT_CHUNKING_PRESET` | `granite_embedding_278m` | Default preset |
| `DOCLING_SERVE_ALLOWED_CHUNKING_PRESETS` | all | Allowed presets |

### Picture Classification

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_DEFAULT_PICTURE_CLASSIFICATION_PRESET` | `document_figure_classifier_v2` | Default preset |

## Batch source/target control

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_ALLOWED_SOURCE_TYPES` | built-in API sources | Allowed batch source kinds |
| `DOCLING_SERVE_ALLOWED_TARGET_TYPES` | built-in API targets | Allowed target kinds |

Accept JSON arrays or comma-separated strings. Plugin sources/targets require explicit inclusion. `local_path` is never available remotely.

## Artifact storage (Presigned URLs)

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_ARTIFACT_STORAGE_ENABLED` | `false` | Enable artifact storage |
| `DOCLING_SERVE_ARTIFACT_STORAGE_ENDPOINT` | | S3-compatible endpoint |
| `DOCLING_SERVE_ARTIFACT_STORAGE_BUCKET` | | Bucket name |
| `DOCLING_SERVE_ARTIFACT_STORAGE_ACCESS_KEY` | | Access key |
| `DOCLING_SERVE_ARTIFACT_STORAGE_SECRET_KEY` | | Secret key |
| `DOCLING_SERVE_ARTIFACT_STORAGE_KEY_PREFIX` | `converted/` | Key prefix |
| `DOCLING_SERVE_ARTIFACT_STORAGE_PRESIGN_TTL_SECONDS` | `3600` | Presign URL TTL |
| `DOCLING_SERVE_ARTIFACT_STORAGE_VERIFY_SSL` | `true` | Verify TLS certificates |

## OpenTelemetry

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_OTEL_ENABLE_METRICS` | `true` | Enable metrics collection |
| `DOCLING_SERVE_OTEL_ENABLE_TRACES` | `false` | Enable trace collection |
| `DOCLING_SERVE_OTEL_ENABLE_PROMETHEUS` | `true` | Enable `/metrics` endpoint |
| `DOCLING_SERVE_OTEL_ENABLE_OTLP_METRICS` | `false` | Export metrics via OTLP |
| `DOCLING_SERVE_OTEL_SERVICE_NAME` | `docling-serve` | Service name |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | | OTLP endpoint URL |
| `DOCLING_SERVE_METRICS_PORT` | | Separate port for `/metrics` |

## Docling runtime settings

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_NUM_THREADS` | `4` | CPU threads for torch |
| `DOCLING_DEVICE` | auto | `cpu`, `cuda`, `mps`, `cuda:0`, etc. |
| `DOCLING_PERF_PAGE_BATCH_SIZE` | `4` | Pages per batch |
| `DOCLING_PERF_ELEMENTS_BATCH_SIZE` | `8` | Elements per batch |
| `DOCLING_DEBUG_PROFILE_PIPELINE_TIMINGS` | `false` | Detailed timing info |

## Threading pipeline

| ENV | Default | Description |
|-----|---------|-------------|
| `DOCLING_SERVE_QUEUE_MAX_SIZE` | | Pages queue size |
| `DOCLING_SERVE_OCR_BATCH_SIZE` | | OCR batch size |
| `DOCLING_SERVE_LAYOUT_BATCH_SIZE` | | Layout detection batch size |
| `DOCLING_SERVE_TABLE_BATCH_SIZE` | | Table structure batch size |
| `DOCLING_SERVE_BATCH_POLLING_INTERVAL_SECONDS` | | Wait time before stage processing |

## List parsing

List-type settings accept either JSON arrays or comma-separated strings:

```bash
# JSON array
export DOCLING_SERVE_ALLOWED_VLM_PRESETS='["granite_docling", "custom"]'

# Comma-separated
export DOCLING_SERVE_ALLOWED_VLM_PRESETS="granite_docling,custom"
```

Dict-type settings accept JSON objects:

```bash
export DOCLING_SERVE_CUSTOM_VLM_PRESETS='{"my_preset": {"engine": "openai", "model": "gpt-4-vision"}}'
```
