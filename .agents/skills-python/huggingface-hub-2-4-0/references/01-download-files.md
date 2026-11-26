# 01 — Download files

Reference for `hf_hub_download`, `snapshot_download`, and the local cache in `huggingface_hub` 2.4.0.

## hf_hub_download

Signature (verified from `file_download.py`):

```python
hf_hub_download(
    repo_id: str,
    filename: str,
    *,
    subfolder: str | None = None,
    repo_type: str | None = None,        # "model" (default), "dataset", "space"
    revision: str | None = None,         # branch, tag, or commit hash
    library_name: str | None = None,
    library_version: str | None = None,
    cache_dir: str | Path | None = None,
    local_dir: str | Path | None = None,
    user_agent: dict | str | None = None,
    force_download: bool = False,
    etag_timeout: float = constants.DEFAULT_ETAG_TIMEOUT,
    token: bool | str | None = None,
    local_files_only: bool = False,
    headers: dict[str, str] | None = None,
    endpoint: str | None = None,
    tqdm_class: type[base_tqdm] | None = None,
    dry_run: Literal[False] = False,
) -> str   # or DryRunFileInfo when dry_run=True
```

Key behaviors:

- Returns the **local path** (`str`) of the downloaded file — not its contents.
- `dry_run=True` returns a `DryRunFileInfo` describing the file that *would* be downloaded, without transferring it.
- `local_dir` downloads directly into the given directory instead of the cache (no symlink indirection).
- `local_files_only=True` resolves from the cache only; no network.
- `force_download=True` re-downloads even if the file is cached.
- `token` accepts a string, `True` (use stored token), or `None`.
- `endpoint` overrides the base URL for this call (default from `HF_ENDPOINT`, `https://huggingface.co`).

Related helper: `hf_hub_url(repo_id, filename, ...)` builds the remote URL without downloading (`ENDPOINT + "/{repo_id}/resolve/{revision}/{filename}"`).

## snapshot_download

Signature (verified from `_snapshot_download.py`):

```python
snapshot_download(
    repo_id: str,
    *,
    repo_type: str | None = None,
    revision: str | None = None,
    cache_dir: str | Path | None = None,
    local_dir: str | Path | None = None,
    allow_patterns: list[str] | str | None = None,
    ignore_patterns: list[str] | str | None = None,
    max_workers: int = 8,
    force_download: bool = False,
    local_files_only: bool = False,
    token: bool | str | None = None,
    dry_run: Literal[False] = False,   # True -> list of DryRunFileInfo
    ...
) -> str
```

Downloads a whole repository (all files, filtered by `allow_patterns`/`ignore_patterns`) in parallel (`max_workers`, default 8) and returns the snapshot directory path.

## Cache layout

- Cache root: `HF_HUB_CACHE` → falls back to legacy `HUGGINGFACE_HUB_CACHE` → `$HF_HOME/hub`.
- `HF_HOME` default: `$XDG_CACHE_HOME/huggingface`, else `~/.cache/huggingface`.
- Each repo gets a `refs`/`snapshots` layout: a **revision** is a folder under `snapshots/` populated with the repo's exact tree, but containing only **symlinks** into shared `blobs/` storage (per the `CachedRevisionInfo` docstring). A revision is referenced by 1+ refs or is "detached".
- Blobs are shared across repos; shared blobs are counted once in cache sizes.

### scan_cache_dir / HFCacheInfo

`scan_cache_dir()` returns an immutable `HFCacheInfo`:

- `size_on_disk` — physical size in bytes; a blob shared across repos is counted once, and store-only shared blobs no longer referenced by any repo are still accounted.
- `repos` — list of `CachedRepoInfo` (`repo_id`, `repo_type` in `{"dataset", "model", "space", "kernel"}`, `repo_path`, …).
- Each repo has `revisions` — list of `CachedRevisionInfo` (`commit_hash`, `size_on_disk`, …).

`try_to_load_from_cache(repo_id, filename, ...)` resolves a cached path without any network access.

## Environment variables (download-related)

| Variable | Effect |
|---|---|
| `HF_HUB_OFFLINE` / `TRANSFORMERS_OFFLINE` | Offline mode — every HTTP request raises `OfflineModeIsEnabled` |
| `HF_HOME` | Base dir (default `~/.cache/huggingface`) |
| `HF_HUB_CACHE` / `HUGGINGFACE_HUB_CACHE` | Cache dir (default `$HF_HOME/hub`) |
| `HF_HUB_ETAG_TIMEOUT` | ETag metadata timeout |
| `HF_HUB_DOWNLOAD_TIMEOUT` | Download request timeout |
| `HF_ENDPOINT` | Base URL (default `https://huggingface.co`; staging `https://hub-ci.huggingface.co`) |
| `HF_HUB_DISABLE_XET` | Disable Xet-based downloads |
| `HF_XET_HIGH_PERFORMANCE` | Change Xet download behavior |
| `HF_HUB_DISABLE_PROGRESS_BARS` | Disable tqdm progress bars |
| `HF_HUB_DISABLE_IMPLICIT_TOKEN` | Stop auto-using the stored token |
| `HF_HUB_DISABLE_TELEMETRY` / `DO_NOT_TRACK` / `DISABLE_TELEMETRY` | Opt out of telemetry |
