---
name: huggingface-hub-1-23-0
description: >
  Hugging Face Hub Python client (huggingface_hub) version 1.23.0 — download and
  upload model/dataset/space files, manage repos and commits, run inference via
  InferenceClient (chat, text-gen, vision, audio, embedding tasks), manage cache,
  integrate ML frameworks via ModelHubMixin/PyTorchModelHubMixin, handle model
  cards, run Jobs and Inference Endpoints, use HfFileSystem (fsspec), manage
  Spaces, Buckets, webhooks, collections, papers, and discussions. Use this skill
  whenever the user interacts with the Hugging Face Hub programmatically: downloading
  models, pushing checkpoints, calling inference APIs, managing repos, working with
  model cards, or any Hub-related Python task, even if they don't name
  "huggingface_hub" explicitly.
metadata:
  tags:
    - python
    - ml
    - huggingface
    - hub
    - inference
---

# huggingface-hub 1.23.0

## Overview

`huggingface_hub` 1.23.0 is the official Python client for the [Hugging Face Hub](https://huggingface.co/). It provides programmatic access to download/upload model weights and datasets, manage repositories, run inference against deployed models, and integrate custom ML frameworks with the Hub.

### Core modules

| Module | Purpose |
|---|---|
| `hf_hub_download` / `snapshot_download` | Download single files or entire repos into the local cache |
| `upload_file` / `upload_folder` / `create_commit` | Upload files or batches of operations as atomic commits |
| `HfApi` | Full Hub API — repos, models, datasets, spaces, jobs, endpoints, webhooks, discussions, collections |
| `InferenceClient` / `AsyncInferenceClient` | Run inference on deployed models (chat, text, vision, audio, etc.) |
| `ModelHubMixin` / `PyTorchModelHubMixin` | Integrate any ML framework with save/load/push_to_hub |
| `ModelCard` / `DatasetCard` / `SpaceCard` | Read/write model/dataset/space README cards with metadata |
| `HfFileSystem` | fsspec-compatible filesystem for `hf://` URLs |
| `scan_cache_dir` | Inspect and manage the local download cache |

### Authentication

Tokens are resolved in this order: explicit `token` argument → `HF_TOKEN` env var → stored token via `hf auth login` → `huggingface-cli login`. Use `hf auth login` (CLI) or `login()` (Python) to persist credentials. The `HF_ENDPOINT` env var overrides the default `https://huggingface.co` base URL.

### Dependencies

Core: `httpx`, `tqdm`, `pyyaml`, `packaging`, `typing-extensions`, `filelock`, `fsspec`, `click`. Optional extras: `torch`, `safetensors`, `Pillow`, `numpy`, `soundfile`, `authlib` (OAuth), `mcp` (MCP agents), `gradio`.

## Usage

### Download files

```python
from huggingface_hub import hf_hub_download, snapshot_download

# Single file — returns local path
path = hf_hub_download(
    repo_id="meta-llama/Llama-3.3-70B-Instruct",
    filename="config.json",
    repo_type="model",           # default; also "dataset", "space"
    revision="main",             # branch, tag, or commit hash
    cache_dir=None,              # default: ~/.cache/huggingface/hub
    local_dir="/tmp/model",      # optional: direct download to a local dir
)

# Entire repository — returns local directory path
local_dir = snapshot_download(
    repo_id="bert-base-uncased",
    repo_type="model",
    revision="main",
    allow_patterns=["*.safetensors", "config.json"],
    ignore_patterns=["*.bin"],
    max_workers=8,
)
```

### Upload files

```python
from huggingface_hub import upload_file, upload_folder, create_repo

# Create repo if it doesn't exist
create_repo(repo_id="username/my-model", exist_ok=True)

# Single file
upload_file(
    path_or_fileobj="/path/to/model.safetensors",
    path_in_repo="model.safetensors",
    repo_id="username/my-model",
    repo_type="model",
    commit_message="Upload model weights",
    token="hf_...",
)

# Entire folder
upload_folder(
    folder_path="/path/to/model/",
    repo_id="username/my-model",
    commit_message="Upload full model",
    allow_patterns=["*.safetensors", "config.json", "tokenizer*"],
    ignore_patterns=["*.bin", "*.pt"],
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
    commit_message="Update config, remove old file",
)
```

### InferenceClient

```python
from huggingface_hub import InferenceClient

client = InferenceClient(token="hf_...")

# Chat completion (OpenAI-compatible)
messages = [{"role": "user", "content": "Explain quantum computing"}]
response = client.chat_completion(messages, model="meta-llama/Llama-3.3-70B-Instruct")
print(response.choices[0].message.content)

# Streaming chat
for chunk in client.chat_completion(messages, stream=True, model="..."):
    print(chunk.choices[0].delta.content, end="", flush=True)

# Text generation
output = client.text_generation("Continue: The quick brown fox", max_new_tokens=50)

# Image classification
from PIL import Image
image = Image.open("cat.jpg")
result = client.image_classification(image, model="google/vit-base-patch16-224")

# Automatic speech recognition
audio = client.automatic_speech_recognition("/path/to/audio.wav")
```

### ModelHubMixin / PyTorchModelHubMixin

```python
from huggingface_hub import ModelHubMixin, PyTorchModelHubMixin
import torch.nn as nn

# Generic mixin (any framework)
class MyConfig(ModelHubMixin):
    def __init__(self, dim: int = 768, n_layers: int = 12):
        self.dim = dim
        self.n_layers = n_layers

config = MyConfig(dim=512)
config.save_pretrained("/tmp/my-config")
config = MyConfig.from_pretrained("/tmp/my-config")

# PyTorch integration
class MyModel(nn.Module, PyTorchModelHubMixin):
    def __init__(self, hidden_size: int = 768):
        super().__init__()
        self.linear = nn.Linear(hidden_size, hidden_size)

model = MyModel(hidden_size=256)
model.save_pretrained("my-model")
model = MyModel.from_pretrained("my-model")
# Push directly to Hub
model.push_to_hub("username/my-model", token="hf_...")
```

### Cache management

```python
from huggingface_hub import scan_cache_dir

cache_info = scan_cache_dir()
print(f"Revisions: {len(cache_info.repos)}")
print(f"Total size: {cache_info.size_on_disk}")

for repo in cache_info.repos:
    for revision in repo.revisions:
        print(f"  {repo.repo_id}@{revision.commit_hash}: {revision.size_on_disk}")
```

### HfApi — search and repo management

```python
from huggingface_hub import HfApi

api = HfApi()

# Search models
models = list(api.list_models(limit=10, sort="downloads", direction=-1))
models = list(api.list_models(author="google", library="pytorch"))

# Search datasets
datasets = list(api.list_datasets(limit=10, tags=["task_categories:text-classification"]))

# Repo info
info = api.model_info("bert-base-uncased")
print(info.downloads, info.likes, info.tags)

# List repo files
files = api.list_repo_files("bert-base-uncased")

# Check existence
print(api.repo_exists("bert-base-uncased"))
print(api.file_exists("bert-base-uncased", "config.json"))
```

## Gotchas

- **`hf_hub_download` returns a path, not file contents** — it downloads to the cache and returns the local file path as a `str`. Read the file yourself if you need its contents.
- **Cache dir defaults to `~/.cache/huggingface/hub`** — not `~/.cache/huggingface` (that's the old location). Use `cache_dir` parameter or `HF_HUB_CACHE` env var to override.
- **`snapshot_download` with `local_dir` bypasses cache** — files go directly to the specified directory without going through the cache system. Use this for editable local copies.
- **`upload_folder` uses Git LFS for large files** — files over 10 MB are automatically uploaded as LFS objects. The threshold can be changed with `HF_HUB_LFS_FILE_SIZE` env var.
- **`create_commit` operations are atomic** — all `CommitOperationAdd`/`CommitOperationDelete`/`CommitOperationCopy` in a single call succeed or fail together.
- **`InferenceClient` uses serverless inference by default** — free but rate-limited and may have cold starts. For production, use a dedicated provider via `provider` parameter or deploy an Inference Endpoint.
- **`token=True` means "use stored token"** — passing `token=True` to API methods tells the client to look up the stored token automatically. Pass `token=False` or `None` to skip authentication.
- **`repo_type` defaults to `"model"`** — always specify `repo_type="dataset"` or `repo_type="space"` explicitly when working with datasets or spaces to avoid 404 errors.
- **`revision` accepts branches, tags, or commit hashes** — a 40-char hex string is treated as a commit hash; everything else is a branch or tag name. Default is `"main"`.
- **PyTorchModelHubMixin requires `torch`** — the mixin works without PyTorch for `from_pretrained`/`save_pretrained` on config-only classes, but model save/load needs `torch` installed.
- **`InferenceClient.chat_completion` is OpenAI-compatible** — it accepts the same `messages`, `tools`, `response_format` structure. Use it as a drop-in replacement for OpenAI's client when targeting Hub-hosted models.
- **`hf auth login` replaces `huggingface-cli login`** — the new CLI command is `hf auth login`. The old `huggingface-cli login` still works but is deprecated.
- **Offline mode** — set `HF_HUB_OFFLINE=1` to prevent any network calls. All requests will raise `OfflineModeIsEnabled`.
- **`upload_large_folder` for very large uploads** — use `upload_large_folder` instead of `upload_folder` for repos with thousands of files; it uses a pipelined upload strategy.

## References

- [01-download-files](references/01-download-files.md) — hf_hub_download, snapshot_download, cache layout, local_dir mode
- [02-upload-and-commits](references/02-upload-and-commits.md) — upload_file, upload_folder, create_commit, CommitOperation*, upload_large_folder
- [03-hf-api](references/03-hf-api.md) — HfApi class: repos, models, datasets, spaces, jobs, endpoints, webhooks, discussions, collections
- [04-inference-client](references/04-inference-client.md) — InferenceClient, AsyncInferenceClient, all inference tasks, providers, streaming
- [05-mixins-and-serialization](references/05-mixins-and-serialization.md) — ModelHubMixin, PyTorchModelHubMixin, safetensors serialization, state dict utilities
- [06-repocard](references/06-repocard.md) — ModelCard, DatasetCard, SpaceCard, CardData, metadata_load/save/update
- [07-auth-and-cli](references/07-auth-and-cli.md) — login, logout, token resolution, hf CLI commands, OAuth, OIDC
- [08-errors](references/08-errors.md) — Exception hierarchy, error types, retry strategies
- [09-fsspec-and-buckets](references/09-fsspec-and-buckets.md) — HfFileSystem, HfUri, bucket operations, sync
