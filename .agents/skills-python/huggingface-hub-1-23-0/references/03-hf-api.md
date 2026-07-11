# HfApi

The `HfApi` class is the main entry point for all Hub API operations. Instantiate once and reuse:

```python
from huggingface_hub import HfApi

api = HfApi(token="hf_...")    # token optional; resolved from env/stored if omitted
```

Most methods also exist as top-level functions (e.g., `list_models()`, `create_repo()`). The functions create an internal `HfApi` instance.

## Repository management

### create_repo

```python
url = api.create_repo(
    repo_id="username/my-model",
    repo_type="model",           # "model" | "dataset" | "space"
    token="hf_...",
    private=False,
    space_sdk=None,              # for spaces: "gradio" | "streamlit" | "static" | "docker"
    space_storage="default",     # storage tier for spaces
    space_hardware="cpu-basic",  # hardware for spaces
    space_sleep_time=60,         # minutes before sleeping
    space_secrets=[],            # list of {"key": ..., "value": ...}
    space_variables=[],          # list of {"key": ..., "value": ...}
    space_heap_size=None,        # max heap for spaces
    space hardware="cpu-upgrade",
    space_base_size=None,        # storage size
    space_custom_compute_types=None,
    space_show_progress=None,
    space_stage=None,
    space_resource_category=None,
    space_resource_quantity=None,
    space_resource_duration=None,
    space_resource_schedule=None,
    space_resource_scale=None,
    space_resource_max_scale=None,
    space_resource_min_scale=None,
    space_resource_target_gpu_count=None,
    space_resource_target_memory_gib=None,
    space_resource_target_vcpu_count=None,
    space_resource_max_idle_time=None,
    space_resource_max_run_time=None,
    space_resource_min_scale=None,
    space_resource_target_accelerator_count=None,
    space_resource_target_accelerator_type=None,
    space_resource_target_accelerator_memory_gib=None,
    space_resource_target_accelerator_vcpu_count=None,
    space_resource_target_accelerator_memory_gib=None,
    space_resource_target_accelerator_vcpu_count=None,
)
```

### delete_repo

```python
api.delete_repo(repo_id="username/my-model", repo_type="model", token="hf_...")
```

### update_repo_settings

```python
api.update_repo_settings(
    repo_id="username/my-model",
    private=False,
    token="hf_...",
)
```

### move_repo

```python
api.move_repo(
    from_repo_id="username/old-name",
    to_repo_id="username/new-name",
    to_repo_type="model",
    token="hf_...",
)
```

### duplicate_repo / duplicate_space

```python
api.duplicate_repo(
    repo_id="username/source",
    to_repo_id="username/copy",
    to_repo_type="model",
    token="hf_...",
)

api.duplicate_space(
    repo_id="username/source-space",
    to_repo_id="username/copy-space",
    token="hf_...",
    # Space-specific options: hardware, storage, secrets, variables
)
```

## Search and listing

### list_models

```python
models = api.list_models(
    sort="downloads",            # "downloads" | "likes" | "lastModified" | "trending"
    direction=-1,                # -1 = descending, 1 = ascending
    limit=10,
    search="bert",               # keyword search
    author="google",             # filter by author
    library="pytorch",           # filter by library
    task="text-classification",  # filter by task
    trained_datasets=["squad"],  # filter by training dataset
    tags=["safetensors"],        # filter by tags
    pipeline_tag="text-generation",
    full=True,                   # include full metadata
    cardData=True,               # include model card data
    archive="models--archive",   # filter by archive
    token="hf_...",              # for private repos
)
```

Returns `Iterable[ModelInfo]`.

### ModelInfo key attributes

| Attribute | Type | Description |
|---|---|---|
| `id` | `str` | Repo ID |
| `author` | `str` | Author/organization |
| `sha` | `str` | Latest commit hash |
| `lastModified` | `datetime` | Last modification time |
| `downloads` | `int` | Total download count |
| `likes` | `int` | Like count |
| `tags` | `list[str]` | Tags |
| `pipeline_tag` | `str` | Pipeline/task tag |
| `library_name` | `str` | Library name |
| `cardData` | `ModelCardData` | Model card metadata (if `cardData=True`) |
| `siblings` | `list[RepoSibling]` | Files in the repo |
| `safetensors` | `SafeTensorsInfo` | Safetensors metadata |
| `transformersInfo` | `TransformersInfo` | Transformers integration info |

### list_datasets

```python
datasets = api.list_datasets(
    sort="downloads",
    direction=-1,
    limit=10,
    search="glue",
    author="huggingface",
    task_categories=["text-classification"],
    tags=["language:en"],
    benchmark="super_glue",
    language_creators="crowdsourced",
    size_categories=["100K<n<1M"],
    gated="auto",               # "auto" | "manual" | False
    token="hf_...",
)
```

Returns `Iterable[DatasetInfo]`.

### list_spaces

```python
spaces = api.list_spaces(
    search="image-generation",
    sort="likes",
    direction=-1,
    limit=10,
    author="huggingface",
    linked=False,                # only spaces linked to a model
    models=["stabilityai/stable-diffusion"],
    datasets=[],
    tags=[],
    search_models="stable-diffusion",
    search_datasets="coco",
    full=True,
    token="hf_...",
)
```

Returns `Iterable[SpaceInfo]`.

### search_spaces

```python
results = api.search_spaces(
    search="text-to-image",
    sort="likes",
    limit=10,
)
```

## Repo info and inspection

### repo_info / model_info / dataset_info / space_info

```python
info = api.repo_info(repo_id="bert-base-uncased", repo_type="model")
info = api.model_info("bert-base-uncased")
info = api.dataset_info("glue", repo_type="dataset")
info = api.space_info("username/my-space", repo_type="space")
```

### repo_exists / file_exists / revision_exists

```python
api.repo_exists("bert-base-uncased", repo_type="model")  # bool
api.file_exists("bert-base-uncased", "config.json")      # bool
api.revision_exists("bert-base-uncased", revision="main") # bool
```

### list_repo_files

```python
files = api.list_repo_files("bert-base-uncased", repo_type="model")
# ['config.json', 'model.safetensors', 'tokenizer.json', ...]
```

### list_repo_tree

```python
entries = api.list_repo_tree(
    "bert-base-uncased",
    path="model.safetensors",    # optional: specific path
    recursive=False,
    expand=False,                # include metadata (size, LFS info)
    revision="main",
    repo_type="model",
)
```

Returns `Iterable[RepoFile | RepoFolder]`.

### list_repo_commits

```python
commits = api.list_repo_commits("bert-base-uncased", repo_type="model")
for commit in commits:
    print(commit.commit_id, commit.title, commit.message, commit.authors)
```

### list_repo_refs

```python
refs = api.list_repo_refs("bert-base-uncased", repo_type="model")
print(refs.branches)   # list of GitRefInfo
print(refs.tags)       # list of GitRefInfo
```

## Branches and tags

### create_branch

```python
api.create_branch(
    repo_id="username/my-model",
    branch="experimental",
    revision="main",              # source commit/branch
    token="hf_...",
    exist_ok=False,
)
```

### create_tag

```python
api.create_tag(
    repo_id="username/my-model",
    tag="v1.0.0",
    revision="main",
    token="hf_...",
    exist_ok=False,
)
```

### delete_branch / delete_tag

```python
api.delete_branch(repo_id="username/my-model", branch="experimental", token="hf_...")
api.delete_tag(repo_id="username/my-model", tag="v1.0.0", token="hf_...")
```

## Discussions and pull requests

### get_repo_discussions

```python
discussions = api.get_repo_discussions("username/my-model", repo_type="model")
for disc in discussions:
    print(disc.number, disc.title, disc.status, disc.author)
```

### create_discussion / create_pull_request

```python
# Create a discussion
disc = api.create_discussion(
    repo_id="username/my-model",
    title="Fix typo in README",
    description="There's a typo on line 5",
    repo_type="model",
    token="hf_...",
)

# Create a pull request
pr = api.create_pull_request(
    repo_id="username/my-model",
    title="Update config",
    description="Updated model config",
    token="hf_...",
)
```

### Discussion operations

```python
# Get details
details = api.get_discussion_details("username/my-model", discussion_num=42)

# Comment
api.comment_discussion("username/my-model", 42, "Thanks for the fix!")

# Change status
api.change_discussion_status("username/my-model", 42, "closed")

# Rename
api.rename_discussion("username/my-model", 42, "New title")

# Edit comment
api.edit_discussion_comment("username/my-model", 42, comment_id="...", body="Updated comment")

# Merge PR
api.merge_pull_request("username/my-model", 42, token="hf_...")
```

## Spaces management

### Space operations

```python
# Get runtime info
runtime = api.get_space_runtime("username/my-space")

# Restart
api.restart_space("username/my-space")

# Pause
api.pause_space("username/my-space")

# Wait for space to be running
api.wait_for_space("username/my-space", running=True, token="hf_...")

# Fetch logs
logs = api.fetch_space_logs("username/my-space")

# Request hardware change
api.request_space_hardware("username/my-space", "t4-medium")

# Request storage change
api.request_space_storage("username/my-space", size="large")

# Set sleep time
api.set_space_sleep_time("username/my-space", sleep_time=60)

# Dev mode
api.enable_space_dev_mode("username/my-space")
api.disable_space_dev_mode("username/my-space")

# List hardware options
hardware = api.list_spaces_hardware()

# List templates
templates = api.list_space_templates()
```

### Space secrets and variables

```python
# Secrets (encrypted, visible only to the space)
api.add_space_secret("username/my-space", key="API_KEY", value="sk-...")
secrets = api.get_space_secrets("username/my-space")
api.delete_space_secret("username/my-space", key="API_KEY")

# Variables (not encrypted, visible in repo)
api.add_space_variable("username/my-space", key="MODEL_NAME", value="bert")
variables = api.get_space_variables("username/my-space")
api.delete_space_variable("username/my-space", key="MODEL_NAME")
```

## Jobs

### Run a job

```python
from huggingface_hub import HfApi, JobHardware

api = HfApi()

job = api.run_job(
    repo_id="username/my-repo",
    entry_point="train.py",
    job_durations="1h",
    job_hardware=JobHardware.CPU_XLARGE,
    secrets=[{"key": "HF_TOKEN", "value": "hf_..."}],
    token="hf_...",
)

# Wait for completion
api.wait_for_job(job.job_id)

# Fetch logs
logs = api.fetch_job_logs(job.job_id)

# Fetch metrics
metrics = api.fetch_job_metrics(job.job_id)
```

### List and manage jobs

```python
jobs = api.list_jobs(token="hf_...")
info = api.inspect_job(job_id="...")
api.cancel_job(job_id="...")
api.update_job_labels(job_id="...", labels={"team": "ml"})

# Hardware options
hardware = api.list_jobs_hardware()
```

### Scheduled jobs

```python
# Create scheduled job
job = api.create_scheduled_job(
    repo_id="username/my-repo",
    entry_point="daily_train.py",
    schedule="0 0 * * *",         # cron expression
    job_durations="2h",
    job_hardware=JobHardware.CPU_XLARGE,
    token="hf_...",
)

# Manage scheduled jobs
jobs = api.list_scheduled_jobs(token="hf_...")
info = api.inspect_scheduled_job(job_id="...")
api.suspend_scheduled_job(job_id="...")
api.resume_scheduled_job(job_id="...")
api.trigger_scheduled_job(job_id="...")
api.delete_scheduled_job(job_id="...")
```

### uv jobs

```python
api.run_uv_job(
    repo_id="username/my-repo",
    command="uv run train.py",
    job_durations="1h",
    token="hf_...",
)

api.create_scheduled_uv_job(
    repo_id="username/my-repo",
    command="uv run daily_train.py",
    schedule="0 0 * * *",
    token="hf_...",
)
```

## Inference Endpoints

```python
# List endpoints
endpoints = api.list_inference_endpoints(token="hf_...")

# Create from catalog
endpoint = api.create_inference_endpoint_from_catalog(
    name="my-endpoint",
    repository="meta-llama/Llama-3.3-70B-Instruct",
    provider={"provider": "hf-inference", "acc": "gpu"},
    token="hf_...",
)

# Create custom
endpoint = api.create_inference_endpoint(
    name="my-endpoint",
    repository="username/my-model",
    provider={"provider": "hf-inference", "acc": "gpu"},
    space="username/my-space",
    token="hf_...",
)

# Manage
info = api.get_inference_endpoint("my-endpoint")
api.update_inference_endpoint("my-endpoint", scale=0)
api.pause_inference_endpoint("my-endpoint")
api.resume_inference_endpoint("my-endpoint")
api.scale_to_zero_inference_endpoint("my-endpoint")
api.delete_inference_endpoint("my-endpoint")

# List catalog
catalog = api.list_inference_catalog()
```

## Webhooks

```python
# Create
webhook = api.create_webhook(
    webhook_url="https://my-server.com/hook",
    token="hf_...",
    repo_id="username/my-model",
    event="repo.update",
)

# Manage
webhook = api.get_webhook(webhook_id="...")
webhooks = api.list_webhooks()
api.update_webhook(webhook_id="...", webhook_url="https://new-url.com/hook")
api.enable_webhook(webhook_id="...")
api.disable_webhook(webhook_id="...")
api.delete_webhook(webhook_id="...")
```

## Collections

```python
# Create
collection = api.create_collection(
    title="My Favorite Models",
    token="hf_...",
)

# Add items
api.add_collection_item(
    collection_id="username/my-collection",
    repo_id="bert-base-uncased",
    repo_type="model",
)

# Manage
collection = api.get_collection("username/my-collection")
collections = api.list_collections(author="username")
api.update_collection_metadata("username/my-collection", description="Updated")
api.update_collection_item("username/my-collection", item_id="...", description="...")
api.delete_collection_item("username/my-collection", item_id="...")
api.delete_collection("username/my-collection")
```

## Users and organizations

```python
# User info
user = api.get_user_overview("username")
followers = api.list_user_followers("username")
following = api.list_user_following("username")
repos = api.list_user_repos("username")

# Organization info
org = api.get_organization_overview("org-name")
members = api.list_organization_members("org-name")
followers = api.list_organization_followers("org-name")

# Likes
api.like("username/my-model")
api.unlike("username/my-model")
liked = api.list_liked_repos("username")
likers = api.list_repo_likers("username/my-model")
```

## Papers

```python
papers = api.list_papers(search="transformer", limit=10)
paper = api.paper_info("paper-id")
content = api.read_paper("paper-id")
daily = api.list_daily_papers()
```

## Access requests (gated repos)

```python
pending = api.list_pending_access_requests("username/gated-model")
accepted = api.list_accepted_access_requests("username/gated-model")
rejected = api.list_rejected_access_requests("username/gated-model")

api.accept_access_request("username/gated-model", user="user123")
api.reject_access_request("username/gated-model", user="user123")
api.cancel_access_request("username/gated-model", user="user123")
api.grant_access("username/gated-model", users=["user1", "user2"])
```

## Auth check

```python
result = api.auth_check(token="hf_...")
# Returns dict with scopes and permissions
```

## whoami

```python
info = api.whoami(token="hf_...")
# Returns user info dict: name, fullname, email, avatar_url, etc.
```

## Tags

```python
model_tags = api.get_model_tags()
dataset_tags = api.get_dataset_tags()
```

## Dataset parquet files

```python
files = api.list_dataset_parquet_files("username/my-dataset")
```

## Kernel info

```python
info = api.kernel_info("kernel-id")
```

## super_squash_history

```python
api.super_squash_history(
    repo_id="username/my-model",
    revision="main",
    token="hf_...",
)
```
