# HfFileSystem and Buckets

## HfFileSystem

fsspec-compatible filesystem for `hf://` URLs. Registered as `hf` protocol.

```python
from huggingface_hub import HfFileSystem, hffs

fs = HfFileSystem(token="hf_...")
# Or use the singleton
fs = hffs
```

### Basic operations

```python
# Read a file
with fs.open("hf://models/bert-base-uncased/config.json") as f:
    data = f.read()

# List files
files = fs.ls("hf://models/bert-base-uncased/")
for info in files:
    print(info["name"], info["size"], info["type"])

# Check existence
print(fs.exists("hf://models/bert-base-uncased/config.json"))

# Get info
info = fs.info("hf://models/bert-base-uncased/config.json")

# Read as bytes
data = fs.cat("hf://models/bert-base-uncased/config.json")

# Walk directory
for dirpath, dirs, files in fs.walk("hf://models/bert-base-uncased/"):
    for f in files:
        print(fs.sep.join([dirpath, f]))
```

### URL format

```
hf://<repo_type>/<repo_id>@<revision>/<path>
```

- `repo_type`: `models` (default), `datasets`, `spaces`
- `repo_id`: `username/repo-name`
- `revision`: branch, tag, or commit hash (default: `main`)
- `path`: file path within the repo

Examples:
- `hf://bert-base-uncased/config.json` → models, main branch
- `hf://datasets/glue@main/README.md` → dataset, main branch
- `hf://spaces/user/space@app/main/gradio_app.py` → space, app branch

### HfFileSystemFile / HfFileSystemStreamFile

```python
# Regular file (buffered)
with fs.open("hf://models/bert-base-uncased/config.json", "rb") as f:
    content = f.read()

# Streaming file (for large files)
with fs.open("hf://models/bert-base-uncased/model.safetensors", "rb", mode="stream") as f:
    for chunk in iter(lambda: f.read(8192), b""):
        process(chunk)
```

### Integration with other libraries

```python
# With pandas
import pandas as pd
df = pd.read_csv("hf://datasets/glue@main/sst2/train.csv")

# With fsspec.open
import fsspec
with fsspec.open("hf://models/bert-base-uncased/config.json") as f:
    data = f.read()

# With Dask
import dask.dataframe as dd
df = dd.read_csv("hf://datasets/glue@main/sst2/*.csv")
```

## HfUri

Parse and construct Hub URIs.

```python
from huggingface_hub import HfUri, parse_hf_uri

uri = HfUri("hf://models/bert-base-uncased@main/config.json")
print(uri.repo_type)    # "model"
print(uri.repo_id)      # "bert-base-uncased"
print(uri.revision)     # "main"
print(uri.path)         # "config.json"

# Parse string
parsed = parse_hf_uri("hf://datasets/glue@main/README.md")
```

## Buckets

Hugging Face Buckets provide object storage for datasets and model artifacts.

### Bucket management

```python
from huggingface_hub import HfApi

api = HfApi()

# Create
api.create_bucket("my-bucket", token="hf_...")

# List
buckets = api.list_buckets(token="hf_...")

# Info
info = api.bucket_info("my-bucket", token="hf_...")

# Delete
api.delete_bucket("my-bucket", token="hf_...")

# Move
api.move_bucket("old-bucket", "new-bucket", token="hf_...")
```

### Bucket file operations

```python
# Upload files
api.batch_bucket_files(
    bucket_name="my-bucket",
    files=[
        {"path": "data/train.csv", "content": b"col1,col2\n1,2\n"},
        {"path": "data/test.csv", "content": b"col1,col2\n3,4\n"},
    ],
    token="hf_...",
)

# List files
entries = api.list_bucket_tree("my-bucket", token="hf_...")

# Get file info
info = api.get_bucket_paths_info("my-bucket", paths=["data/train.csv"], token="hf_...")

# Download
api.download_bucket_files(
    bucket_name="my-bucket",
    local_dir="/tmp/downloaded",
    token="hf_...",
)
```

### Sync bucket with repo

```python
# Sync bucket to a Hub repo
api.sync_bucket(
    bucket_name="my-bucket",
    repo_id="username/my-dataset",
    repo_type="dataset",
    token="hf_...",
)
```

### Bucket file metadata

```python
from huggingface_hub import BucketFile, BucketFolder, BucketInfo

# BucketFile attributes
file = BucketFile(...)
print(file.path)       # path in bucket
print(file.size)       # file size in bytes
print(file.last_modified)

# BucketInfo attributes
info = BucketInfo(...)
print(info.name)       # bucket name
print(info.size)       # total size
print(info.file_count) # number of files
```

### Sync operations

```python
from huggingface_hub import SyncOperation, SyncPlan

# Check sync plan
plan = api.sync_bucket(
    bucket_name="my-bucket",
    repo_id="username/my-dataset",
    repo_type="dataset",
    token="hf_...",
    dry_run=True,
)
# plan is a SyncPlan with summary of operations
print(plan.summary())  # {"adds": 5, "deletes": 2, "updates": 3}
```

## CommitScheduler

Schedule periodic commits to a repo.

```python
from huggingface_hub import CommitScheduler

scheduler = CommitScheduler(
    repo_id="username/my-model",
    folder_path="/path/to/local/model",
    commit_every="1h",           # time interval
    commit_message="Auto-commit",
    token="hf_...",
)

# Start scheduling
scheduler.start()

# Stop
scheduler.stop()

# Use as context manager
with CommitScheduler(...) as scheduler:
    # commits happen automatically
    pass
```
