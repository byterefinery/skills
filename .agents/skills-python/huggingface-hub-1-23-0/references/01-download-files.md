# Download Files

## hf_hub_download

Download a single file from the Hub into the local cache.

```python
from huggingface_hub import hf_hub_download

path = hf_hub_download(
    repo_id="bert-base-uncased",
    filename="config.json",
    repo_type="model",           # "model" | "dataset" | "space"
    revision="main",             # branch, tag, or commit hash
    cache_dir=None,              # default: HF_HUB_CACHE or ~/.cache/huggingface/hub
    force_download=False,        # re-download even if cached
    force_filename=None,         # override local filename
    resume_download=True,        # resume interrupted downloads
    local_dir=None,              # if set, download directly to this dir (bypasses cache)
    local_dir_use_symlinks=True, # when local_dir set: True=symlinks to cache, "auto", False=copy
    token=None,                  # token for gated repos
    endpoint=None,               # custom HF endpoint
)
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `repo_id` | `str` | required | `"{namespace}/{repo_name}"` or `"{repo_name}"` for anonymous repos |
| `filename` | `str` | required | Path within the repo (e.g., `"config.json"`, `"pytorch_model.bin"`) |
| `repo_type` | `str` | `"model"` | `"model"`, `"dataset"`, or `"space"` |
| `revision` | `str` | `"main"` | Branch name, tag, or commit hash |
| `cache_dir` | `str \| Path \| None` | `None` | Cache directory; defaults to `HF_HUB_CACHE` env var or `~/.cache/huggingface/hub` |
| `force_download` | `bool` | `False` | Re-download even if file exists in cache |
| `force_filename` | `str \| None` | `None` | Override the local filename |
| `resume_download` | `bool` | `True` | Resume interrupted downloads (uses range requests) |
| `local_dir` | `str \| Path \| None` | `None` | If set, download directly to this local directory instead of cache |
| `local_dir_use_symlinks` | `bool \| "auto"` | `True` | When `local_dir` is set: create symlinks to cache blobs (`True`), copy files (`False`), or auto-detect (`"auto"`) |
| `token` | `str \| bool \| None` | `None` | Auth token for gated/private repos; `True` uses stored token |
| `endpoint` | `str \| None` | `None` | Custom Hub endpoint URL |

### Return value

Returns `str` — the local file path. If the file doesn't exist on the Hub and `local_dir` is not set, returns `_CACHED_NO_EXIST` sentinel.

### Cache layout

```
~/.cache/huggingface/hub/
└── modules/
    └── models/
        └── --username--repo-name/
            └── blobs/
                └── <sha256>/          # actual file content
            └── refs/
                └── main               # commit hash
            └── snapshots/
                └── <commit-hash>/
                    └── config.json    → ../../blobs/<sha256>/ (symlink)
```

Files are stored once by content hash (deduplicated). Snapshots are symlinks to blobs, organized by commit hash.

## snapshot_download

Download an entire repository (all files) into the local cache or a local directory.

```python
from huggingface_hub import snapshot_download

local_dir = snapshot_download(
    repo_id="bert-base-uncased",
    repo_type="model",
    revision="main",
    cache_dir=None,
    local_dir="/tmp/bert",
    local_dir_use_symlinks=True,
    allow_patterns=None,          # e.g., ["*.safetensors", "config.json"]
    ignore_patterns=None,         # e.g., ["*.bin", "*.pt"]
    max_workers=8,                # parallel download threads
    tqdm_class=None,              # custom tqdm class for progress bars
    force_download=False,
    token=None,
    endpoints=None,
)
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `repo_id` | `str` | required | Repository identifier |
| `repo_type` | `str` | `"model"` | `"model"`, `"dataset"`, or `"space"` |
| `revision` | `str` | `"main"` | Branch, tag, or commit hash |
| `cache_dir` | `str \| Path \| None` | `None` | Cache directory |
| `local_dir` | `str \| Path \| None` | `None` | If set, download directly to this directory |
| `local_dir_use_symlinks` | `bool \| "auto"` | `True` | Symlink to cache vs copy |
| `allow_patterns` | `str \| list[str] \| None` | `None` | fnmatch patterns to include (e.g., `"*.safetensors"`) |
| `ignore_patterns` | `str \| list[str] \| None` | `None` | fnmatch patterns to exclude |
| `max_workers` | `int` | `8` | Number of parallel download threads |
| `force_download` | `bool` | `False` | Force re-download |
| `token` | `str \| bool \| None` | `None` | Auth token |

### Return value

Returns `str` — the local directory path (cache snapshot or `local_dir`).

### Usage patterns

```python
# Download only model weights (safetensors format)
snapshot_download(
    "meta-llama/Llama-3.3-70B-Instruct",
    allow_patterns=["*.safetensors"],
    max_workers=16,
)

# Download to editable local directory (no symlinks)
snapshot_download(
    "bert-base-uncased",
    local_dir="/tmp/bert-editable",
    local_dir_use_symlinks=False,
)

# Download dataset parquet files only
snapshot_download(
    "username/my-dataset",
    repo_type="dataset",
    allow_patterns="*.parquet",
)
```

## try_to_load_from_cache

Check if a file is already in the cache without making network calls.

```python
from huggingface_hub import try_to_load_from_cache

cached_path = try_to_load_from_cache(
    repo_id="bert-base-uncased",
    filename="config.json",
    cache_dir=None,
    revision="main",
)
# Returns str (cached path) if found, None if not cached
```

## get_cached_repo_tree

List files in a cached repository snapshot without network access.

```python
from huggingface_hub import get_cached_repo_tree

entries = get_cached_repo_tree(
    repo_id="bert-base-uncased",
    revision="main",
    recursive=True,
)
for entry in entries:
    print(entry.path, entry.file_size)
```

## get_hf_file_metadata

Get file metadata (size, ETag) without downloading the file.

```python
from huggingface_hub import get_hf_file_metadata

metadata = get_hf_file_metadata(
    repo_id="bert-base-uncased",
    filename="pytorch_model.bin",
    revision="main",
    token=None,
)
print(metadata.size, metadata.etag)
```

## hf_hub_url

Generate the direct download URL for a file on the Hub.

```python
from huggingface_hub import hf_hub_url

url = hf_hub_url(
    repo_id="bert-base-uncased",
    filename="config.json",
    repo_type="model",
    revision="main",
    endpoint=None,
)
# "https://huggingface.co/bert-base-uncased/resolve/main/config.json"
```

## scan_cache_dir

Inspect the local download cache.

```python
from huggingface_hub import scan_cache_dir

cache_info = scan_cache_dir(cache_dir=None)

# Top-level info
print(cache_info.size_on_disk)        # total bytes used
print(len(cache_info.repos))          # number of cached repos

# Iterate repos
for repo in cache_info.repos:
    print(repo.repo_id, repo.repo_type)
    for revision in repo.revisions:
        print(f"  {revision.commit_hash}: {revision.size_on_disk} bytes")
        for file in revision.files:
            print(f"    {file.file_path}: {file.file_size}")
```

### HFCacheInfo attributes

| Attribute | Type | Description |
|---|---|---|
| `repos` | `list[CachedRepoInfo]` | List of cached repositories |
| `size_on_disk` | `int` | Total cache size in bytes |

### CachedRepoInfo attributes

| Attribute | Type | Description |
|---|---|---|
| `repo_id` | `str` | Repository identifier |
| `repo_type` | `str` | `"model"`, `"dataset"`, or `"space"` |
| `repo_path` | `Path` | Local path to the cached repo |
| `revisions` | `list[CachedRevisionInfo]` | Cached revisions |
| `size_on_disk` | `int` | Total size in bytes |

### CachedRevisionInfo attributes

| Attribute | Type | Description |
|---|---|---|
| `revision_id` | `str` | The revision (branch/tag name) |
| `commit_hash` | `str` | Git commit hash |
| `files` | `set[CachedFileInfo]` | Cached files in this revision |
| `last_accessed_at` | `datetime` | Last access time |
| `last_modified_at` | `datetime` | Last modification time |
| `size_on_disk` | `int` | Size in bytes |

## Environment variables

| Variable | Description |
|---|---|
| `HF_HUB_CACHE` | Override default cache directory |
| `HF_HUB_OFFLINE` | Set to `1` to disable all network requests |
| `HF_HUB_ENABLE_HF_TRANSFER` | Set to `1` to use `hf-transfer` for faster downloads (requires `pip install hf-transfer`) |
| `HF_HUB_ETAG_TIMEOUT` | Timeout for ETag/metadata fetch (default: 10s) |
| `HF_HUB_DOWNLOAD_TIMEOUT` | Timeout for file downloads (default: 10s) |
