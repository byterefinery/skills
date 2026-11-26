# Configuration

Configuration comes from CLI options, environment variables, and optionally a YAML/JSON config file (`DOCLING_SERVE_CONFIG_FILE`). Priority: **environment variables > config file > defaults**.

Warning — with `--reload` or multiple `--workers`, uvicorn spawns subprocesses that ignore CLI values; use environment variables.

## Webserver (uvicorn) options

| CLI option | ENV | Default |
|---|---|---|
| `--host` | `UVICORN_HOST` | `0.0.0.0` for `run`, `localhost` for `dev` |
| `--port` | `UVICORN_PORT` | `5001` |
| `--reload` | `UVICORN_RELOAD` | `false` (`run`) / `true` (`dev`) |
| `--workers` | `UVICORN_WORKERS` | `1` |
| `--root-path` | `UVICORN_ROOT_PATH` | `""` |
| `--proxy-headers` | `UVICORN_PROXY_HEADERS` | `true` |
| `--timeout-keep-alive` | `UVICORN_TIMEOUT_KEEP_ALIVE` | `60` |
| `--ssl-certfile` / `--ssl-keyfile` / `--ssl-keyfile-password` | `UVICORN_SSL_*` | — |

## Core app options (selection)

| ENV | Default | Description |
|---|---|---|
| `DOCLING_SERVE_LOG_LEVEL` | `WARNING` | CLI `-v` = INFO, `-vv` = DEBUG; CLI wins over ENV |
| `DOCLING_SERVE_LOG_FORMAT` | `text` | `text` or `json` (recommended for production) |
| `DOCLING_SERVE_LOG_HEADER_PREFIX` | `X-Docling-Log-` | Request headers with this prefix are propagated into logs (`Authorization`, cookies, `X-Api-Key` never are) |
| `--artifacts-path` / `DOCLING_SERVE_ARTIFACTS_PATH` | unset | Directory model weights load from |
| `DOCLING_SERVE_STATIC_PATH` | unset | Static assets for docs/UI |
| `DOCLING_SERVE_SCRATCH_PATH` | temp dir | Scratch workspace, e.g. results before fetch |
| `--enable-ui` / `DOCLING_SERVE_ENABLE_UI` | `false` | Serve web UI at `/ui` |
| `DOCLING_SERVE_ENABLE_API_DOCS` | `true` | Serve `/openapi.json`, `/docs`, `/scalar` (no API key needed) |
| `DOCLING_SERVE_ENABLE_CAPABILITIES_ENDPOINT` | `true` | Serve `/v1/capabilities` |
| `DOCLING_SERVE_DEBUG_ERROR_DETAILS` | `false` | Return raw internal exception detail |
| `DOCLING_SERVE_ENABLE_REMOTE_SERVICES` | `false` | Allow pipeline components with remote connections (VLM APIs) |
| `DOCLING_SERVE_ALLOW_EXTERNAL_PLUGINS` | `false` | Allow third-party connector plugins |
| `DOCLING_SERVE_SINGLE_USE_RESULTS` | `true` | Results accessible only once |
| `DOCLING_SERVE_RESULT_REMOVAL_DELAY` | `300` | Delay before removing single-use results |
| `DOCLING_SERVE_MAX_DOCUMENT_TIMEOUT` | `604800` | Max per-document processing time (s) |
| `DOCLING_SERVE_MAX_NUM_PAGES` / `DOCLING_SERVE_MAX_FILE_SIZE` | unset | Input limits |
| `DOCLING_SERVE_ENABLE_CALLBACKS` | `true` | Accept `callbacks` in requests |
| `DOCLING_SERVE_MAX_CALLBACKS_PER_REQUEST` | `5` | Callback limit per request |
| `DOCLING_SERVE_ALLOWED_SOURCE_TYPES` / `DOCLING_SERVE_ALLOWED_TARGET_TYPES` | built-ins | Allowed batch source/target kinds (JSON array or comma-separated); plugin kinds require explicit inclusion; `local_path` never available remotely |
| `DOCLING_SERVE_DEFAULT_PIPELINE` | `standard` | Pipeline when a request omits `pipeline`; must be within allowed set |
| `DOCLING_SERVE_ALLOWED_PIPELINES` | all (`standard`, `vlm`) | Pipelines requests may select |
| `DOCLING_SERVE_SYNC_POLL_INTERVAL` | `2` | Sleep between polls in sync endpoints (s) |
| `DOCLING_SERVE_MAX_SYNC_WAIT` | `120` | Max wait for task completion on sync endpoints (s) |
| `DOCLING_SERVE_LOAD_MODELS_AT_BOOT` | `True` | Warm up default pipeline models at boot |
| `DOCLING_SERVE_IDLE_UNLOAD_SECONDS` | `0` | Release converter/allocator caches after N idle seconds (local engine only; `0` disables) |
| `DOCLING_SERVE_OPTIONS_CACHE_SIZE` | `2` | Cached DocumentConverter objects (with models) |
| `DOCLING_SERVE_CORS_ORIGINS` / `_METHODS` / `_HEADERS` | `["*"]` | CORS settings |
| `DOCLING_SERVE_API_KEY` | unset | If set, all API requests need header `X-Api-Key` |
| `DOCLING_SERVE_ENG_KIND` | `local` | Compute engine: `local`, `rq`, or `ray` |

### Artifact storage (managed presigned URLs)

Enable with `DOCLING_SERVE_ARTIFACT_STORAGE_ENABLED=true`; backend `s3` or `azure`. Key vars: `..._ENDPOINT`, `..._REGION` (needed for real AWS S3 outside us-east-1), `..._VERIFY_SSL`, `..._BUCKET`, `..._ACCESS_KEY`, `..._SECRET_KEY`, `..._KEY_PREFIX` (default `converted/`), `..._PRESIGN_TTL_SECONDS` (default 3600, range 60–604800). Azure uses a connection string (`AccountName` + `AccountKey`) plus container/account/prefix vars.

### Docling performance env vars

| ENV | Default | Description |
|---|---|---|
| `DOCLING_NUM_THREADS` | `4` | Torch CPU threads |
| `DOCLING_DEVICE` | auto | `cpu`, `cuda`, `mps`, or `cuda:N` |
| `DOCLING_PERF_PAGE_BATCH_SIZE` | `4` | Pages per batch |
| `DOCLING_PERF_ELEMENTS_BATCH_SIZE` | `8` | Elements per enrichment batch |
| `DOCLING_DEBUG_PROFILE_PIPELINE_TIMINGS` | `false` | Detailed timings in responses |

## Compute engines

### Local (default)

| ENV | Default | Description |
|---|---|---|
| `DOCLING_SERVE_ENG_LOC_NUM_WORKERS` | `2` | Worker threads for tasks |
| `DOCLING_SERVE_ENG_LOC_SHARE_MODELS` | `False` | Share model instances across worker threads |

### RQ (Redis)

| ENV | Default | Description |
|---|---|---|
| `DOCLING_SERVE_ENG_RQ_REDIS_URL` | required | e.g. `redis://localhost:6373/` |
| `DOCLING_SERVE_ENG_RQ_QUEUE_NAME` | `convert` | Queue name; comma-separated list routes API to first, workers drain in order |
| `DOCLING_SERVE_ENG_RQ_RESULTS_PREFIX` | `docling:results` | Redis key prefix for results |
| `DOCLING_SERVE_ENG_RQ_SUB_CHANNEL` | `docling:updates` | Update channel between workers and API |
| `DOCLING_SERVE_ENG_RQ_RESULTS_TTL` | `14400` | Result TTL in Redis (s) |
| `DOCLING_SERVE_ENG_RQ_JOB_TIMEOUT` | `14400` | Max runtime of a single job (s); `-1` disables; set on API instances, not workers; never `0` |
| `DOCLING_SERVE_ENG_RQ_REDIS_MAX_CONNECTIONS` | `50` | Connection pool size (raise to 100–200 for many workers) |

### Ray

| ENV | Default | Description |
|---|---|---|
| `DOCLING_SERVE_ENG_RAY_TASK_TIMEOUT` | `3600` | Max seconds per task; exceeded tasks are cancelled including in-flight converter calls |
| `DOCLING_SERVE_ENG_RAY_DOCUMENT_TIMEOUT` | `300` | Per-document timeout for orchestrator checks (e.g. converter recycling safety); keep equal to the effective request document timeout |
| `DOCLING_SERVE_ENG_RAY_GRACEFUL_SHUTDOWN_TIMEOUT_S` | Ray Serve default (20 s) | Max wait for a draining replica before force-kill |
| `DOCLING_SERVE_ENG_RAY_CONVERTER_REQUEST_TIMEOUT` | disabled | Hard per-document limit on coordinator→converter calls; set well above the document timeout as a backstop |
| `DOCLING_SERVE_ENG_RAY_RECYCLE_CONVERTER_ON_ABANDONED_CONVERSION` | `true` | Replace converter replicas still running after a cancelled conversion exceeds grace |
| `DOCLING_SERVE_ENG_RAY_ABANDONED_CONVERSION_GRACE_S` | document timeout + 60 s | Grace before an abandoned conversion marks its replica unhealthy |
| `DOCLING_SERVE_ENG_RAY_TASK_METADATA_TTL` | `604800` | Seconds finished task metadata is kept in Redis (`0` = forever) |
| `DOCLING_SERVE_ENG_RAY_TENANT_METRICS_REFRESH_INTERVAL` | `30` | Refresh interval for per-tenant Prometheus metrics (one process, elected via Redis lock) |

## Converter manager / preset controls

Per-stage pattern: `DOCLING_SERVE_DEFAULT_<STAGE>_PRESET`, `DOCLING_SERVE_ALLOWED_<STAGE>_PRESETS` (JSON array or comma list), `DOCLING_SERVE_CUSTOM_<STAGE>_PRESETS` (JSON object of id → options), `DOCLING_SERVE_ALLOWED_<STAGE>_ENGINES`, and `DOCLING_SERVE_ALLOW_CUSTOM_<STAGE>_CONFIG`.

Stages: VLM pipeline (default preset `granite_docling`), picture description (default `smolvlm`), code/formula (default `granite_docling`), table structure (default kind `docling_tableformer`, preset `tableformer_v1_accurate`), layout (default kind/preset `docling_layout_default`).

## Telemetry

| ENV | Default | Description |
|---|---|---|
| `DOCLING_SERVE_OTEL_ENABLE_METRICS` | `true` | Metrics collection |
| `DOCLING_SERVE_OTEL_ENABLE_TRACES` | `false` | Trace collection (needs `OTEL_EXPORTER_OTLP_ENDPOINT`) |
| `DOCLING_SERVE_OTEL_ENABLE_PROMETHEUS` | `true` | Prometheus exporter + `/metrics` on API port |
| `DOCLING_SERVE_METRICS_PORT` | unset | Serve `/metrics` on a separate port |

## JSON logging and request propagation

Set `DOCLING_SERVE_LOG_FORMAT=json` for structured logs. Headers prefixed with `X-Docling-Log-` (configurable) become structured log fields for the request lifetime, e.g. `X-Docling-Log-RequestID: req-123` → field `RequestID`.
