# Auth and CLI

## Authentication

### Token resolution order

When a method accepts `token`, the value is resolved in this order:

1. Explicit `token` argument (string)
2. `token=True` → look up stored token
3. `HF_TOKEN` environment variable
4. Token stored by `hf auth login` / `huggingface-cli login`
5. Google Colab token (if running in Colab)
6. OIDC token (if running in a supported CI environment)

### login()

```python
from huggingface_hub import login

# Interactive login (browser-based OAuth or paste token)
login()

# Login with explicit token
login(token="hf_...")

# Login and add to git credential store
login(token="hf_...", add_to_git_credential=True)

# Force re-login even if already logged in
login(skip_if_logged_in=False)
```

### logout()

```python
from huggingface_hub import logout

logout()
logout(delete_git_credential=True)
```

### whoami() / auth_check()

```python
from huggingface_hub import HfApi

api = HfApi()
info = api.whoami(token="hf_...")
result = api.auth_check(token="hf_...")
```

### get_token()

```python
from huggingface_hub import get_token
token = get_token()
```

## OAuth

```python
from huggingface_hub import login, parse_huggingface_oauth, attach_huggingface_oauth

# Browser-based OAuth (no token needed)
login()

# Parse OAuth token response
info = parse_huggingface_oauth(token_string)

# Attach OAuth to a FastAPI/Starlette app
attach_huggingface_oauth(app, login_url="/login", callback_url="/callback")
```

## OIDC (Trusted Publishers)

For CI/CD, set `HF_OIDC_RESOURCE` to the target repo. The library exchanges an OIDC ID token for a Hub access token automatically.

```bash
export HF_OIDC_RESOURCE=huggingface://api/models/username/model
```

## hf CLI

Entry point: `huggingface_hub.cli.hf:main`.

### Auth

```bash
hf auth login                    # Interactive login
hf auth login --token hf_...     # Login with token
hf auth logout                   # Remove stored token
hf auth switch                   # Switch between stored tokens
hf auth list                     # List stored tokens
hf auth whoami                   # Current user info
```

### System

```bash
hf system info                   # Environment info
hf system clean-cache            # Clean cache
```

### Repos

```bash
hf repos create username/my-model
hf repos create username/my-model --type dataset
hf repos create username/my-model --type space --sdk gradio
hf repos delete username/my-model
hf repos ls
hf repos mv username/old username/new
hf repos duplicate src dest
```

### Models / Datasets / Spaces

```bash
hf models list --author google --limit 10
hf models info bert-base-uncased
hf datasets list --author huggingface
hf datasets info glue
hf spaces list --author huggingface
hf spaces info username/my-space
```

### Download / Upload

```bash
hf download repo-id --include "*.safetensors" --exclude "*.bin"
hf download repo-id --repo-type dataset --local-dir /tmp/model
hf upload file repo-id --file path/to/file --path-in-repo file.txt
hf upload folder repo-id --folder /path/to/folder
hf upload large-folder repo-id --folder /path/to/large
```

### Repo files / Discussions

```bash
hf repo-files list repo-id
hf repo-files delete repo-id --file path/in/repo
hf discussions list repo-id
hf discussions create repo-id --title "Fix" --body "Description"
hf discussions comment repo-id 42 --comment "Thanks!"
hf discussions status repo-id 42 --status closed
```

### Cache / Jobs / Endpoints

```bash
hf cache scan
hf cache clean
hf jobs run repo-id --entry-point train.py --hardware cpu-xlarge
hf jobs list
hf jobs inspect job-id
hf jobs cancel job-id
hf endpoints list
hf endpoints create name --repo model-id --provider hf-inference --acc gpu
hf endpoints delete name
```

### Webhooks / Collections / Papers / Skills

```bash
hf webhooks list
hf webhooks create --url https://my-server.com/hook
hf collections list
hf collections create --title "My Collection"
hf papers list --search transformer
hf skills list
hf skills install skill-name
```

### LFS / Buckets / Sandbox

```bash
hf lfs list repo-id
hf buckets create bucket-name
hf buckets list
hf buckets sync bucket-name --repo repo-id
hf sandbox run repo-id --command "python train.py"
```

## Key environment variables

| Variable | Description |
|---|---|
| `HF_TOKEN` | Default access token |
| `HF_ENDPOINT` | Custom Hub endpoint (default: `https://huggingface.co`) |
| `HF_HUB_CACHE` | Cache directory |
| `HF_HUB_OFFLINE` | Set to `1` to disable network requests |
| `HF_HUB_ENABLE_HF_TRANSFER` | Set to `1` to use hf-transfer for faster downloads |
| `HF_HUB_ETAG_TIMEOUT` | ETag fetch timeout (default: 10s) |
| `HF_HUB_DOWNLOAD_TIMEOUT` | Download timeout (default: 10s) |
| `HF_HUB_LFS_FILE_SIZE` | LFS threshold in bytes (default: 10MB) |
| `HF_HUB_DISABLE_PROGRESS_BARS` | Set to `1` to disable tqdm progress bars |
| `HF_HUB_DISABLE_TELEMETRY` | Set to `1` to disable telemetry |
| `HF_HUB_HTTP_TIMEOUT` | HTTP request timeout (default: 10s) |
| `HF_HUB_ENABLE_XET` | Enable Xet storage protocol |
