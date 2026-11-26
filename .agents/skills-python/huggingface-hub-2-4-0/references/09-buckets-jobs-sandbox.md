# 09 — Buckets, jobs, sandboxes

New-in-2.x surfaces: object-storage buckets, the Jobs API, sandboxes, `hf://` URIs, and Xet storage helpers.

## Buckets

Module-level functions (verified from `__all__`):

- `create_bucket(...)`, `bucket_info(...)`, `list_buckets(...)`, `delete_bucket(...)`
- `move_bucket(...)`, `update_bucket_settings(...)`
- `sync_bucket(...)` — sync a local folder to/from a bucket
- `download_bucket_files(...)`, `batch_bucket_files(...)`, `list_bucket_tree(...)`
- `get_bucket_file_metadata(...)`, `get_bucket_paths_info(...)`
- Types: `BucketInfo`, `BucketUrl`, `BucketFile`, `BucketFileMetadata`, `BucketFolder`, `Volume`
- Errors: `BucketNotFoundError`, `BucketBatchError`

CLI (README example):

```bash
hf buckets sync ./checkpoints hf://buckets/username/my-bucket
```

Top-level `hf sync` is the bucket-sync alias.

## hf URIs and HfFileSystem

- `parse_hf_uri(uri, endpoint=None) -> HfUri` — parse `hf://` URIs into typed `HfUri` components (repo vs bucket, path, endpoint)
- `HfUri` — dataclass representation
- `HfFileSystem` — fsspec-compatible filesystem registered under the `hf` protocol (entry point `fsspec.specs: hf=huggingface_hub.HfFileSystem`)
- `HfFileSystemFile`, `HfFileSystemStreamFile`, `HfFileSystemResolvedPath`
- `hffs` — a ready-made `HfFileSystem()` instance exported at package level (verified: `hffs = HfFileSystem()` in `hf_file_system.py`)

## Jobs API

Run and inspect Jobs on Hugging Face infrastructure (CLI: `hf jobs run python:3.12 python -c "..."`).

- `run_job(...)`, `wait_for_job(...)`, `list_jobs(...)`, `cancel_job(...)`, `rerun_job(...)`
- `inspect_job(...)`, `fetch_job_logs(...)`, `fetch_job_metrics(...)`
- `update_job_labels(...)`, `update_job_expose(...)`
- `list_jobs_hardware(...)` — hardware catalog (`JobHardware`, `JobAccelerator`, `JobNetwork`)
- `run_uv_job(...)` — run a UV-script job
- Scheduled jobs: `create_scheduled_job(...)`, `list_scheduled_jobs(...)`, `inspect_scheduled_job(...)`, `trigger_scheduled_job(...)`, `resume_scheduled_job(...)`, `suspend_scheduled_job(...)`, `delete_scheduled_job(...)`, `update_scheduled_job_labels(...)`, `update_scheduled_job_schedule(...)`
- Types: `JobInfo`, `JobStatus`, `JobStage`, `JobDurations`, `JobOwner`, `JobInitiator`
- Errors: `JobNotFoundError`

## Sandboxes

Short-lived compute sandboxes (CLI group: `hf sandbox`).

- `Sandbox` — a sandbox instance; `SandboxPool` — pool of sandboxes
- `SandboxProcess`, `SandboxCommandResult` — process and command result types
- Errors: `SandboxError`, `SandboxCommandError`
- Hot-reload support for Spaces lives in the `_hot_reload` module (SSE-based client)

## DDUF (dataset dump format)

- `export_folder_as_dduf(...)`, `export_entries_as_dduf(...)` — export to DDUF
- `read_dduf_file(...)` — read a DDUF file
- `DDUFEntry` — typed entry
- Errors: `DDUFError`, `DDUFCorruptedFileError`, `DDUFExportError`, `DDUFInvalidEntryNameError`

## Xet storage helpers

- `get_torch_storage_id(...)`, `get_torch_storage_size(...)` — Xet-backed storage identifiers for torch artifacts
- `XetDownloadError`
- Env vars: `HF_HUB_DISABLE_XET`, `HF_XET_HIGH_PERFORMANCE`, `HF_HUB_DISABLE_SHARED_BLOBS`
