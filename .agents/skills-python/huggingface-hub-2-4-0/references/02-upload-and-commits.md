# 02 — Upload and commits

Reference for uploads and atomic commits in `huggingface_hub` 2.4.0.

## upload_file

Signature (verified from `hf_api.py`, `HfApi.upload_file` — also exposed as module-level `upload_file`):

```python
upload_file(
    path_or_fileobj: str | Path | bytes | BinaryIO,
    path_in_repo: str,
    repo_id: str,
    token: str | bool | None = None,
    repo_type: str | None = None,
    revision: str | None = None,
    commit_message: str | None = None,
    commit_description: str | None = None,
    create_pr: bool | None = None,
    parent_commit: str | None = None,
    ...
)
```

Uploads a single file (local path, raw bytes, or file object) as a commit.

## upload_folder

Signature (verified from `hf_api.py`):

```python
upload_folder(
    repo_id: str,
    folder_path: str | Path,
    path_in_repo: str | None = None,
    commit_message: str | None = None,
    commit_description: str | None = None,
    token: str | bool | None = None,
    repo_type: str | None = None,
    revision: str | None = None,
    create_pr: bool | None = None,
    parent_commit: str | None = None,
    allow_patterns: list[str] | str | None = None,
    ignore_patterns: list[str] | str | None = None,
    delete_patterns: list[str] | str | None = None,
    run_as_future: Literal[False] = False,
    ...
)
```

- `path_in_repo` maps the folder contents under a subpath.
- `delete_patterns` additionally deletes matching remote files in the same commit.
- Large folders are handled natively (chunked, resumable) — the 1.x `upload_large_folder` helper is **deprecated/removed** in 2.x.

## create_commit (atomic batch operations)

Signature (verified from `hf_api.py`):

```python
api.create_commit(
    repo_id: str,
    operations: Iterable[CommitOperation],
    *,
    commit_message: str,               # required
    commit_description: str | None = None,
    token: str | bool | None = None,
    repo_type: str | None = None,
    revision: str | None = None,
    create_pr: bool | None = None,
    num_threads: int = 5,
    parent_commit: str | None = None,
    run_as_future: Literal[False] = False,
    ...
) -> CommitInfo   # Future[CommitInfo] when run_as_future=True
```

Operation classes:

- `CommitOperationAdd(path_in_repo, path_or_fileobj)` — add/replace a file
- `CommitOperationDelete(path_in_repo)` — delete a file
- `CommitOperationCopy(...)` — copy within the repo

All operations in one call form a single atomic commit: they all succeed or all fail. `create_pr=True` opens a pull request instead of pushing to the branch. `parent_commit` pins the expected parent commit for optimistic concurrency control.

## Pull requests

- `create_pull_request(...)` — open a PR from a branch
- `merge_pull_request(...)` — merge an open PR

## LFS and Xet storage

- The Hub uses **Xet** as its chunk-deduplicated storage backend (per the README: "Built-in file versioning, even with very large files, made possible by Xet").
- `hf-xet` is a **core dependency** on x86_64/arm64/aarch64 platforms (setup.py marker).
- LFS utilities exposed: `preupload_lfs_files`, `list_lfs_files`, `permanently_delete_lfs_files`, `lfs.py` (Git LFS batch upload), CLI `hf lfs-enable-largefiles`, `hf lfs-multipart-upload`.
- Disable/adjust via `HF_HUB_DISABLE_XET=1`, `HF_XET_HIGH_PERFORMANCE=1`, `HF_HUB_DISABLE_SHARED_BLOBS=1`.
