# Upload and Commits

## upload_file

Upload a single file to a repository.

```python
from huggingface_hub import upload_file

url = upload_file(
    path_or_fileobj="/path/to/model.safetensors",
    path_in_repo="model.safetensors",
    repo_id="username/my-model",
    repo_type="model",
    token="hf_...",
    commit_message="Upload model weights",
    revision="main",
    create_pr=False,
    parent_commit=None,
    skip_if_exists=False,
)
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `path_or_fileobj` | `str \| Path \| bytes \| BinaryIO` | required | Local file path, raw bytes, or file-like object |
| `path_in_repo` | `str` | required | Destination path within the repo |
| `repo_id` | `str` | required | Repository identifier |
| `repo_type` | `str` | `"model"` | `"model"`, `"dataset"`, or `"space"` |
| `token` | `str \| bool \| None` | `None` | Auth token |
| `commit_message` | `str` | from path | Commit message |
| `revision` | `str \| None` | `None` | Branch to push to (default: default branch) |
| `create_pr` | `bool` | `False` | Create a pull request instead of direct push |
| `parent_commit` | `str \| None` | `None` | Parent commit hash (for `create_pr=True`) |
| `skip_if_exists` | `bool` | `False` | Skip upload if file already exists with same content |

### Return value

Returns `str` — the commit URL.

## upload_folder

Upload an entire folder to a repository.

```python
from huggingface_hub import upload_folder

url = upload_folder(
    folder_path="/path/to/model/",
    repo_id="username/my-model",
    repo_type="model",
    token="hf_...",
    commit_message="Upload model folder",
    revision="main",
    create_pr=False,
    parent_commit=None,
    allow_patterns=None,        # include patterns
    ignore_patterns=None,       # exclude patterns
    delete_patterns=None,       # files to delete from repo
    commit_description=None,    # extended commit description
    parent_commit=None,
)
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `folder_path` | `str \| Path` | required | Local folder to upload |
| `repo_id` | `str` | required | Repository identifier |
| `repo_type` | `str` | `"model"` | `"model"`, `"dataset"`, or `"space"` |
| `token` | `str \| bool \| None` | `None` | Auth token |
| `commit_message` | `str` | `"Upload folder"` | Commit message |
| `revision` | `str \| None` | `None` | Target branch |
| `create_pr` | `bool` | `False` | Create a PR instead of direct commit |
| `allow_patterns` | `str \| list[str] \| None` | `None` | fnmatch glob patterns to include |
| `ignore_patterns` | `str \| list[str] \| None` | `None` | fnmatch glob patterns to exclude |
| `delete_patterns` | `str \| list[str] \| None` | `None` | Patterns of files to delete from repo |
| `commit_description` | `str \| None` | `None` | Extended commit description |

### LFS handling

Files larger than 10 MB are automatically uploaded as Git LFS objects. The threshold is configurable via `HF_HUB_LFS_FILE_SIZE` environment variable. LFS files are uploaded in parallel using a thread pool.

## upload_large_folder

Upload very large folders (thousands of files) using a pipelined strategy.

```python
from huggingface_hub import upload_large_folder

url = upload_large_folder(
    folder_path="/path/to/large-dataset/",
    repo_id="username/my-dataset",
    repo_type="dataset",
    token="hf_...",
    commit_message="Upload large dataset",
    num_workers=8,
)
```

This uses a pipelined upload approach that is more efficient for repos with thousands of files. It pre-computes the upload plan and streams files without loading everything into memory.

## create_commit

Create an atomic commit with multiple operations.

```python
from huggingface_hub import HfApi, CommitOperationAdd, CommitOperationDelete, CommitOperationCopy

api = HfApi()

commit_info = api.create_commit(
    repo_id="username/my-model",
    repo_type="model",
    token="hf_...",
    operations=[
        CommitOperationAdd(
            path_in_repo="config.json",
            path_or_fileobj=b'{"architectures": ["MyModel"]}',
        ),
        CommitOperationAdd(
            path_in_repo="model.safetensors",
            path_or_fileobj="/path/to/model.safetensors",
        ),
        CommitOperationDelete(path_in_repo="old_file.txt"),
        CommitOperationCopy(
            source="source-repo",
            path_in_repo="old_weight.bin",
            dest_path_in_repo="weight.bin",
        ),
    ],
    commit_message="Update model with new config",
    revision="main",
    create_pr=False,
    parent_commit=None,
    run_squash=False,
)
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `repo_id` | `str` | required | Repository identifier |
| `repo_type` | `str` | `"model"` | `"model"`, `"dataset"`, or `"space"` |
| `token` | `str \| bool \| None` | `None` | Auth token |
| `operations` | `list[CommitOperation]` | required | List of add/delete/copy operations |
| `commit_message` | `str` | required | Commit message |
| `commit_description` | `str \| None` | `None` | Extended commit description |
| `revision` | `str \| None` | `None` | Target branch |
| `create_pr` | `bool` | `False` | Create a PR instead of direct commit |
| `parent_commit` | `str \| None` | `None` | Expected parent commit (for concurrency control) |
| `run_squash` | `bool` | `False` | Run squash after commit |

### Return value

Returns `CommitInfo` — a string subclass containing the commit URL, with additional attributes `commit_url`, `commit_message`, `commit_description`, `oid`.

## CommitOperation types

### CommitOperationAdd

Upload a file to the repository.

```python
# From local file path
CommitOperationAdd(
    path_in_repo="model.safetensors",
    path_or_fileobj="/path/to/model.safetensors",
)

# From bytes
CommitOperationAdd(
    path_in_repo="config.json",
    path_or_fileobj=b'{"key": "value"}',
)

# From file-like object
with open("model.bin", "rb") as f:
    CommitOperationAdd(
        path_in_repo="model.bin",
        path_or_fileobj=f,
    )

# With upload mode override
CommitOperationAdd(
    path_in_repo="large_file.bin",
    path_or_fileobj="/path/to/large.bin",
    _upload_mode="lfs",       # force LFS | "regular" | None (auto)
)
```

### CommitOperationDelete

Remove a file or folder from the repository.

```python
# Delete a single file
CommitOperationDelete(path_in_repo="old_file.txt")

# Delete a folder (all files under it)
CommitOperationDelete(path_in_repo="old_folder/")
```

### CommitOperationCopy

Copy files between repositories.

```python
CommitOperationCopy(
    source="username/source-repo",
    path_in_repo="weight.bin",
    dest_path_in_repo="weight.bin",
    source_revision=None,
    source_repo_type="model",
)
```

## delete_file / delete_folder / delete_files

Convenience methods on `HfApi`.

```python
api = HfApi()

# Delete a single file
api.delete_file("old_file.txt", repo_id="username/my-model")

# Delete a folder
api.delete_folder("old_folder/", repo_id="username/my-model")

# Delete multiple files
api.delete_files(["file1.txt", "file2.txt"], repo_id="username/my-model")
```

## copy_files

Copy files between repos.

```python
api.copy_files(
    source="username/source-repo/path/to/file.bin",
    destination="username/dest-repo/path/to/file.bin",
    token="hf_...",
)
```

## preupload_lfs_files

Pre-upload LFS files before creating a commit (for very large batches).

```python
api.preupload_lfs_files(
    repo_id="username/my-model",
    lfs_files=[
        {"path": "model.safetensors", "algo": "sha256", "size": 1234567890, "sha256": "..."},
    ],
)
```

## permanently_delete_lfs_files

Permanently delete LFS files from storage (frees up space).

```python
api.permanently_delete_lfs_files(
    repo_id="username/my-model",
    lfs_files_objects=[
        {"oid": "<sha256-hash>", "size": 1234567890},
    ],
)
```

## list_lfs_files

List LFS-tracked files in a repository.

```python
lfs_files = api.list_lfs_files("username/my-model", repo_type="model")
for f in lfs_files:
    print(f.path, f.size, f.sha256)
```
