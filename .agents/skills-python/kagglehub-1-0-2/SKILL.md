---
name: kagglehub-1-0-2
description: >
  Kagglehub 1.0.2 — download, upload, and load Kaggle models, datasets, competitions, and notebook outputs
  from Python. Use when the user needs to access Kaggle resources (models, datasets, competitions, notebook
  outputs, utility scripts, or packages) programmatically, or when working with Kaggle's caching and
  authentication mechanisms.
---

# kagglehub 1.0.2

## Overview

`kagglehub` is the official Kaggle Python client for downloading, uploading, and loading Kaggle resources. It supports models, datasets, competitions, notebook outputs, utility scripts, and Kaggle Packages. The library auto-detects Kaggle notebook and Colab environments, using shared caches instead of local disk when available.

Install with `pip install kagglehub`. Optional extras: `kagglehub[pandas-datasets]`, `kagglehub[hf-datasets]`, `kagglehub[polars-datasets]`, `kagglehub[signing]`.

## Usage

### Authentication

Authenticated by default in Kaggle notebooks. Outside notebooks, authenticate via one of:

- `kagglehub.login()` — interactive prompt (notebook widget or terminal)
- `KAGGLE_API_TOKEN` environment variable
- `~/.kaggle/access_token` file
- Colab secret named `KAGGLE_API_TOKEN`
- Legacy `~/.kaggle/kaggle.json`

Check identity with `kagglehub.whoami()` → `{"username": "..."}`.

### Handle Formats

Handles identify Kaggle resources:

- **Models**: `owner/model/framework/variation` or `owner/model/framework/variation/version`
- **Datasets**: `owner/dataset` or `owner/dataset/versions/version`
- **Competitions**: `competition-name` (no slashes)
- **Notebooks**: `owner/notebook` or `owner/notebook/versions/version`

### Downloading Resources

All download functions return the local path (string) and share common parameters:

```python
import kagglehub

# Models — handle: owner/model/framework/variation[/version]
path = kagglehub.model_download("google/bert/tensorFlow2/answer-equivalence-bem")
path = kagglehub.model_download("google/bert/tensorFlow2/answer-equivalence-bem/1")
path = kagglehub.model_download("google/bert/tensorFlow2/answer-equivalence-bem", path="variables/variables.index")
path = kagglehub.model_download("google/bert/tensorFlow2/answer-equivalence-bem", force_download=True)
path = kagglehub.model_download("google/bert/tensorFlow2/answer-equivalence-bem", output_dir="./models")

# Datasets — handle: owner/dataset[/versions/version]
path = kagglehub.dataset_download("bricevergnou/spotify-recommendation")
path = kagglehub.dataset_download("bricevergnou/spotify-recommendation/versions/1")
path = kagglehub.dataset_download("bricevergnou/spotify-recommendation", path="data.csv")

# Competitions — handle: competition-name
path = kagglehub.competition_download("digit-recognizer")
path = kagglehub.competition_download("digit-recognizer", path="train.csv")

# Notebook outputs — handle: owner/notebook[/versions/version]
path = kagglehub.notebook_output_download("alexisbcook/titanic-tutorial")
path = kagglehub.notebook_output_download("alexisbcook/titanic-tutorial", path="submission.csv")
```

Common parameters across all download functions:
- `path` — download a single file within the resource
- `force_download` — bypass cache, re-download even if cached
- `output_dir` — write to a custom directory instead of the default cache

### Uploading Resources

```python
# Upload a model — handle must NOT include version
kagglehub.model_upload(
    "username/my-model/tensorFlow2/my-variation",
    "./local-model-dir",
    version_notes="improved accuracy",
    license_name="Apache 2.0",
    ignore_patterns=["original/", "*.tmp"],
)

# Upload a dataset — handle must NOT include version
kagglehub.dataset_upload(
    "username/my-dataset",
    "./local-dataset-dir",
    version_notes="improved data",
    ignore_patterns=["original/", "*.tmp"],
)
```

Default ignore patterns for uploads: `.git/`, `*/.git/`, `.cache/`, `.huggingface/`.

### Loading Datasets Into Memory

`dataset_load()` loads a file from a Kaggle dataset directly into a Python object. Requires optional extras.

```python
from kagglehub import KaggleDatasetAdapter

# Pandas DataFrame
df = kagglehub.dataset_load(
    KaggleDatasetAdapter.PANDAS,
    "unsdsn/world-happiness/versions/1",
    "2016.csv",
)

# Pandas with kwargs (passed to pd.read_*)
df = kagglehub.dataset_load(
    KaggleDatasetAdapter.PANDAS,
    "robikscube/textocr-text-extraction-from-images-dataset",
    "annot.parquet",
    pandas_kwargs={"columns": ["image_id", "bbox", "points", "area"]},
)

# Pandas from SQLite (sql_query required for .sqlite/.db files)
df = kagglehub.dataset_load(
    KaggleDatasetAdapter.PANDAS,
    "wyattowalsh/basketball",
    "nba.sqlite",
    sql_query="SELECT person_id, player_name FROM draft_history",
)

# Hugging Face Dataset
dataset = kagglehub.dataset_load(
    KaggleDatasetAdapter.HUGGING_FACE,
    "unsdsn/world-happiness/versions/1",
    "2016.csv",
)

# Polars LazyFrame (default) or DataFrame
lf = kagglehub.dataset_load(
    KaggleDatasetAdapter.POLARS,
    "unsdsn/world-happiness/versions/1",
    "2016.csv",
)
```

File type support by adapter:

| Adapter | Supported Extensions |
|---|---|
| PANDAS | `.csv`, `.tsv`, `.json`, `.jsonl`, `.xml`, `.parquet`, `.feather`, `.sqlite*`, `.xls*`, `.ods` |
| HUGGING_FACE | Same as PANDAS (built via `Dataset.from_pandas`) |
| POLARS | `.csv`, `.tsv`, `.json`, `.jsonl`, `.parquet`, `.feather`, `.sqlite*`, `.xls*`, `.ods` |

For Polars, use `polars_frame_type=PolarsFrameType.DATA_FRAME` to get a DataFrame instead of the default LazyFrame.

### Utility Scripts and Packages

```python
# Install a utility script (adds to sys.path)
kagglehub.utility_script_install("bjoernjostein/physionet-challenge-utility-script")

# Import a Kaggle Package (downloads + imports as Python module)
pkg = kagglehub.package_import("owner/package-name")
# Add bypass_confirmation=True to skip the untrusted code warning
```

### Cache Control

Default cache: `~/.cache/kagglehub/`. Override with `KAGGLEHUB_CACHE` environment variable.

In Kaggle notebooks, resources are served from the shared Kaggle cache (not local disk). In Colab, the Colab cache is used. Disable caches with `DISABLE_KAGGLE_CACHE=1` or `DISABLE_COLAB_CACHE=1`.

### Logging

Set `KAGGLE_LOGGING_ENABLED=1` for file-based logging. Default log paths:
- Linux/macOS: `~/.kaggle/logs/kagglehub.log`
- Windows: `C:\Users\%USERNAME%\.kaggle\logs\kagglehub.log`

Override with `KAGGLE_LOGGING_ROOT_DIR`. Console log level via `KAGGLEHUB_VERBOSITY` (debug, info, warning, error, critical).

## Gotchas

- **Upload handles must not include a version** — `model_upload` and `dataset_upload` raise `ValueError` if the handle contains a version segment. The library creates a new version automatically.
- **SQLite files require `sql_query`** — when loading `.sqlite`, `.db`, etc. via `dataset_load`, omitting `sql_query` raises `ValueError`.
- **`dataset_load` needs optional extras** — calling it without the corresponding pip extra installed raises `ImportError` with the exact extra name needed (e.g., `pip install kagglehub[pandas-datasets]`).
- **TSV and JSONL get auto-kwargs** — `.tsv` files get `sep="\t"` and `.jsonl` gets `lines=True` automatically for the PANDAS adapter. These can be overridden via `pandas_kwargs`.
- **Hugging Face adapter cannot handle multi-DataFrame results** — if `pandas_kwargs` produce multiple DataFrames (e.g., Excel with multiple sheets), the HUGGING_FACE adapter raises an exception since `Dataset.from_pandas` accepts only one DataFrame.
- **`package_import` prompts for confirmation** — outside Kaggle/Colab, importing a package from another user triggers a y/n prompt. Use `bypass_confirmation=True` to skip. The prompt is suppressed for packages owned by the logged-in user.
- **`output_dir` with existing files** — if `output_dir` already has files and `force_download` is not set, a `FileExistsError` is raised. Use `force_download=True` to overwrite.
- **Model downloads use parallel file fetch for ≤25 files** — models with 25 or fewer files are downloaded individually in parallel (max 8 threads). Larger models use archive download + extraction.
- **`load_dataset` is deprecated** — use `dataset_load` instead. `load_dataset` will be removed in a future version.
- **Colab cache resolver is always last** — the resolver chain is HTTP → Kaggle Cache → Colab Cache. Colab cache only works inside Colab notebooks.
- **`whoami()` raises on unauthenticated** — use `get_username()` (returns `str | None`) if you need a non-raising check.
- **Signing requires extra** — `model_upload(sigstore=True)` requires `pip install kagglehub[signing]` and the user must be an admin/editor of the model.
