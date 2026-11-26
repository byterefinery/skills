---
name: huggingface-hub-2-4-0
description: >
  Hugging Face Hub Python client and CLI (huggingface_hub) version 2.4.0 —
  download and upload model, dataset and space files with Xet storage, manage
  repos, refs, PRs and discussions, run inference via InferenceClient across
  19 providers (chat, text, vision, audio tasks), manage buckets and hf URIs,
  run Jobs on HF infrastructure, use sandboxes, integrate ML frameworks via
  ModelHubMixin/PyTorchModelHubMixin, handle model cards, webhooks, collections
  and papers. Use whenever the user works with the Hugging Face Hub
  programmatically or via the hf CLI — downloading models, pushing
  checkpoints, calling inference APIs, syncing buckets, running jobs, or any
  Hub-related Python task, even without naming huggingface_hub explicitly.
metadata:
  tags:
    - python
    - ml
    - huggingface
    - hub
    - inference
---

# huggingface-hub 2.4.0

## Overview

`huggingface_hub` 2.4.0 is the official Python client for the [Hugging Face Hub](https://huggingface.co/). It ships one package with two interfaces — the `hf` CLI for the terminal and the `huggingface_hub` library for Python — both designed to work for humans and AI agents. Python 3.10+.

### Core modules

| Module | Purpose |
|---|---|
| `hf_hub_download` / `snapshot_download` | Download single files or entire repos into the local cache |
| `upload_file` / `upload_folder` | Upload files or folders as atomic commits (large/resumable uploads built in) |
| `HfApi` | Full Hub API — repos, models, datasets, spaces, jobs, endpoints, webhooks, discussions, collections, papers |
| `InferenceClient` / `AsyncInferenceClient` | Run inference on 29 tasks across 19 providers (chat, text, vision, audio) |
| `ModelHubMixin` / `PyTorchModelHubMixin` | Integrate any ML framework with save/load/push_to_hub |
| `ModelCard` / `DatasetCard` / `SpaceCard` | Read/write repo README cards with YAML metadata |
| `HfFileSystem` / `HfUri` / `parse_hf_uri` | fsspec-compatible filesystem and `hf://` URI parsing |
| Bucket functions (`create_bucket`, `sync_bucket`, …) | Object-storage buckets, `hf://buckets/` URLs |
| Job functions (`run_job`, `wait_for_job`, …) | Run and inspect Jobs on HF infrastructure |
| `scan_cache_dir` | Inspect and manage the local download cache |

### Authentication

Tokens resolve from the `HF_TOKEN` env var or the stored token written by `login()` / `hf auth login` (the env var wins). `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` stops the client from auto-using the stored token. In 2.x, calling `login()` without a token starts a browser-based OAuth flow (open a URL, enter a short code); pass `token=...` to persist a token directly.

### Dependencies

Core: `click`, `filelock`, `fsspec`, `hf-xet` (auto-installed on x86_64/arm64/aarch64), `httpx2`, `packaging`, `pyyaml`, `tomli` (<3.11), `tqdm`, `typing-extensions`. Extras: `[torch]` (torch + safetensors), `[fastai]`, `[oauth]` (authlib, fastapi, itsdangerous), `[mcp]` (mcp ≥ 1.9.4), `[hf_xet]`.

## Usage

### CLI quick start

```bash
# Install the hf CLI (standalone)
curl -LsSf https://hf.co/cli/install.sh | bash

# Or with pip (also installs the CLI)
pip install huggingface_hub

# Log in
hf auth login                      # or --token $HF_TOKEN non-interactively

# Find models served by Inference Providers
hf models ls --warm

# Download a model
hf download Qwen/Qwen3-0.6B

# Upload files to your own repo
hf upload username/my-cool-model ./model.safetensors

# Sync a local folder to a storage bucket
hf buckets sync ./checkpoints hf://buckets/username/my-bucket

# Run a job on Hugging Face infrastructure
hf jobs run python:3.12 python -c "print('Hello from the cloud!')"

# Discover everything else
hf --help
```

CLI groups: `auth`, `buckets`, `cache`, `collections`, `datasets`, `discussions`, `endpoints`, `extensions`, `jobs`, `models`, `papers`, `repos`, `sandbox`, `skills`, `spaces`, `webhooks`; plus top-level `hf download`, `hf upload`, `hf cp`, `hf sync`, `hf env`. `hf --skills` prints the generated `hf` CLI skill for coding agents; `hf skills add` installs it.

### Download files

```python
from huggingface_hub import hf_hub_download, snapshot_download

# Single file — returns the local cache path (str)
path = hf_hub_download(
    repo_id="meta-llama/Llama-3.3-70B-Instruct",
    filename="config.json",
    repo_type="model",           # "model" (default), "dataset", "space"
    revision="main",             # branch, tag, or commit hash
    cache_dir=None,              # default: $HF_HOME/hub (~/.cache/huggingface/hub)
    local_dir="/tmp/model",      # optional: direct download into a directory
    local_files_only=False,      # True = never touch the network
)

# Entire repository — returns the local directory path
local_dir = snapshot_download(
    repo_id="sentence-transformers/all-MiniLM-L6-v2",
    allow_patterns=["*.safetensors", "config.json"],
    ignore_patterns=["*.bin"],
    max_workers=8,               # default
)
```

### Upload files

```python
from huggingface_hub import create_repo, upload_file, upload_folder

# Create repo if it doesn't exist (returns a RepoUrl)
create_repo(repo_id="username/my-model", exist_ok=True, private=False)

# Single file
upload_file(
    path_or_fileobj="/path/to/model.safetensors",   # path, bytes, or BinaryIO
    path_in_repo="model.safetensors",
    repo_id="username/my-model",
    commit_message="Upload model weights",
)

# Entire folder (handles very large folders with resumable uploads)
upload_folder(
    folder_path="/path/to/model/",
    repo_id="username/my-model",
    commit_message="Upload full model",
    allow_patterns=["*.safetensors", "config.json"],
    ignore_patterns=["*.bin"],
    delete_patterns=["*.tmp"],   # also delete matching remote files
)
```

### Atomic commits with HfApi

```python
from huggingface_hub import HfApi, CommitOperationAdd, CommitOperationDelete

api = HfApi()
api.create_commit(
    repo_id="username/my-model",
    operations=[
        CommitOperationAdd(path_in_repo="config.json", path_or_fileobj=b'{"architectures": ["MyModel"]}'),
        CommitOperationDelete(path_in_repo="old_file.txt"),
    ],
    commit_message="Update config, remove old file",   # required
    create_pr=False,        # True opens a PR instead of pushing
    parent_commit=None,     # pin the parent for concurrency control
    num_threads=5,          # default
)
```

### InferenceClient

```python
from huggingface_hub import InferenceClient

# provider = "auto" | "hf-inference" | "openai" | "groq" | "together" | ... (19 providers)
client = InferenceClient(model="meta-llama/Llama-3.3-70B-Instruct", provider="auto")

# Chat completion
messages = [{"role": "user", "content": "Explain quantum computing"}]
response = client.chat_completion(messages)
print(response.choices[0].message.content)

# Text generation
output = client.text_generation("Continue: The quick brown fox", max_new_tokens=50)

# Vision / audio tasks (29 task methods in total)
result = client.image_classification(open("cat.jpg", "rb"))
audio = client.automatic_speech_recognition("/path/to/audio.wav")
```

### HfApi — search and repo management

```python
from huggingface_hub import HfApi

api = HfApi()

# Search
models = list(api.list_models(limit=10, sort="downloads", direction=-1))
datasets = list(api.list_datasets(limit=10, tags=["task_categories:text-classification"]))

# Info and existence
info = api.model_info("bert-base-uncased")
print(api.repo_exists("bert-base-uncased"))
print(api.file_exists("bert-base-uncased", "config.json"))

# Files, tree, refs, commits
print(api.list_repo_files("bert-base-uncased"))
print(api.list_repo_refs("bert-base-uncased"))
print(list(api.list_repo_commits("bert-base-uncased")))
```

### ModelHubMixin / PyTorchModelHubMixin

```python
from huggingface_hub import ModelHubMixin, PyTorchModelHubMixin
import torch.nn as nn

class MyConfig(ModelHubMixin):
    def __init__(self, dim: int = 768):
        self.dim = dim

config = MyConfig(dim=512)
config.save_pretrained("/tmp/my-config")
config = MyConfig.from_pretrained("/tmp/my-config")

class MyModel(nn.Module, PyTorchModelHubMixin):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(768, 768)

model = MyModel()
model.save_pretrained("/tmp/my-model")          # saves weights with PyTorchModelHubMixin
model = MyModel.from_pretrained("/tmp/my-model")
model.push_to_hub("username/my-model")          # push straight to the Hub
```

### Cache management

```python
from huggingface_hub import scan_cache_dir

cache_info = scan_cache_dir()
print(f"Total size: {cache_info.size_on_disk}")
for repo in cache_info.repos:
    for revision in repo.revisions:
        print(f"  {repo.repo_id}@{revision.commit_hash}")
```

## Gotchas

- **`hf_hub_download` returns a path, not contents** — it downloads into the cache and returns the local file path as `str`. Read the file yourself.
- **`login()` without a token opens a browser OAuth flow in 2.x** — it no longer just prompts for a token. Pass `token=...` to store one directly; in notebooks use `notebook_login()` or `interpreter_login()`.
- **The 2.x package ships only the `hf` console script** — `huggingface-cli` is gone; entry points are `hf` and `tiny-agents` (plus the `hf` fsspec spec).
- **`upload_large_folder` is gone** — deprecated; `upload_folder` now handles large/resumable uploads natively.
- **`create_commit` requires `commit_message`** and all `operations` are atomic — `CommitOperationAdd`/`CommitOperationCopy`/`CommitOperationDelete` succeed or fail together.
- **Default cache is `$HF_HOME/hub`** — `HF_HOME` defaults to `$XDG_CACHE_HOME/huggingface` or `~/.cache/huggingface`. Override with `HF_HUB_CACHE` (or legacy `HUGGINGFACE_HUB_CACHE`).
- **Offline mode** — `HF_HUB_OFFLINE=1` (or `TRANSFORMERS_OFFLINE=1`) makes every HTTP request raise `OfflineModeIsEnabled`.
- **`dry_run=True` on downloads returns `DryRunFileInfo`, not a path** — `hf_hub_download(..., dry_run=True)` and `snapshot_download(..., dry_run=True)` skip the actual transfer.
- **Xet is the storage backend and is installed by default** on x86_64/arm64/aarch64 (`hf-xet` is a core dependency). Set `HF_HUB_DISABLE_XET=1` to disable it; `HF_XET_HIGH_PERFORMANCE=1` changes its download behavior.
- **InferenceClient `provider` takes hyphenated strings or `"auto"`** — e.g. `fal-ai`, `fireworks-ai`, `hf-inference`, `zai-org`; not the module file names (`fal_ai.py`). `"auto"` picks a provider per task/model.
- **`repo_type` values are `model`, `dataset`, `space`, `kernel`** — the cached-repo model includes `kernel`; pass the right type explicitly to avoid 404s on non-model repos.
- **`HF_TOKEN` env var overrides the stored token** — after `login()`, an existing `HF_TOKEN` in the environment still wins; `hf auth` commands print a note when that happens.
- **Telemetry is on by default** — opt out with `HF_HUB_DISABLE_TELEMETRY=1`, `DO_NOT_TRACK=1`, or `DISABLE_TELEMETRY=1`.
- **`hf` CLI errors hide tracebacks** — set `HF_DEBUG=1` to get full tracebacks from CLI failures.

## References

- [01-download-files](references/01-download-files.md) — hf_hub_download, snapshot_download, dry_run, cache layout, env vars
- [02-upload-and-commits](references/02-upload-and-commits.md) — upload_file, upload_folder, create_commit, CommitOperation*, LFS/Xet
- [03-hf-api](references/03-hf-api.md) — HfApi surface: repos, models, datasets, spaces, refs, PRs, discussions, collections, papers, webhooks
- [04-inference-client](references/04-inference-client.md) — InferenceClient, AsyncInferenceClient, 29 task methods, 19 providers, streaming
- [05-mixins-and-serialization](references/05-mixins-and-serialization.md) — ModelHubMixin, PyTorchModelHubMixin, safetensors metadata and state-dict utilities
- [06-repocard](references/06-repocard.md) — ModelCard, DatasetCard, SpaceCard, CardData, metadata_load/save/update
- [07-auth-and-cli](references/07-auth-and-cli.md) — login, OAuth flow, whoami, token resolution, hf CLI commands
- [08-errors](references/08-errors.md) — exception hierarchy
- [09-buckets-jobs-sandbox](references/09-buckets-jobs-sandbox.md) — buckets, hf URIs, Jobs API, sandboxes, DDUF, Xet storage helpers
