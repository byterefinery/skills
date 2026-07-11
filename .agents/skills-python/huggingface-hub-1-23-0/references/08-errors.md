# Errors

## Exception hierarchy

```
Exception
├── CacheNotFound                      # Cache directory not found
├── CorruptedCacheException            # Unexpected cache structure
├── CachedRepoTreeNotFoundError        # No tree listing cached for revision
├── LocalTokenNotFoundError            # Local token required but not found
├── OIDCError                          # OIDC auth cannot proceed
├── DeviceCodeError                    # OAuth device flow failed
├── OfflineModeIsEnabled               # HF_HUB_OFFLINE=1, no network
├── HfHubHTTPError                     # Base for all Hub HTTP errors
│   ├── InferenceTimeoutError          # Inference request timed out
│   ├── InferenceEndpointError         # Inference endpoint error
│   ├── InferenceEndpointTimeoutError  # Endpoint timed out
│   ├── BucketNotFoundError            # Bucket not found
│   ├── JobNotFoundError               # Job not found
│   ├── RepositoryNotFoundError        # 404: repo doesn't exist
│   │   └── GatedRepoError             # Repo is gated/private
│   │   └── DisabledRepoError          # Repo is disabled
│   ├── RevisionNotFoundError          # 404: revision doesn't exist
│   ├── RemoteEntryNotFoundError       # 404: file doesn't exist on Hub
│   └── BadRequestError                # 400: invalid request
├── EntryNotFoundError                 # Base for entry not found
│   ├── RemoteEntryNotFoundError       # File missing on Hub
│   └── LocalEntryNotFoundError        # File missing locally
│       └── IncompleteSnapshotError    # Download was interrupted
├── SafetensorsParsingError            # Cannot parse safetensors file
├── NotASafetensorsRepoError           # Repo has no safetensors files
├── TextGenerationError                # Text generation API error
│   ├── ValidationError                # Invalid generation params
│   ├── GenerationError                # Generation failed
│   ├── OverloadedError                # Server overloaded
│   ├── IncompleteGenerationError      # Generation incomplete
│   └── UnknownError                   # Unknown text-gen error
├── HFValidationError                  # Input validation failed
├── HfUriError                         # Invalid HfUri format
├── DryRunError                        # Dry run detected an issue
├── FileMetadataError                  # File metadata problem
├── DDUFError                          # DDUF format error
│   ├── DDUFCorruptedFileError         # Corrupted DDUF file
│   ├── DDUFExportError                # DDUF export failed
│   └── DDUFInvalidEntryNameError      # Invalid entry name
├── StrictDataclassError               # Dataclass validation error
├── XetDownloadError                   # Xet download failed
├── FileDuplicationError               # Duplicate file detected
├── CLIError                           # CLI error
│   ├── ConfirmationError              # User declined confirmation
│   └── CLIExtensionInstallError       # Extension install failed
└── SandboxError                       # Sandbox error
    └── SandboxCommandError            # Sandbox command failed
```

## Common errors and handling

### RepositoryNotFoundError

Raised when a repo doesn't exist or the token lacks access.

```python
from huggingface_hub import hf_hub_download, RepositoryNotFoundError, HfApi

try:
    hf_hub_download("nonexistent/repo", "config.json")
except RepositoryNotFoundError:
    print("Repo doesn't exist or is private without auth")
```

### GatedRepoError

Raised when accessing a gated repo without approval.

```python
from huggingface_hub import GatedRepoError

try:
    api.model_info("meta-llama/Llama-3.3-70B-Instruct")
except GatedRepoError as e:
    print(f"Gated repo: {e}")
    # User needs to request access or use an approved token
```

### RevisionNotFoundError

Raised when a branch/tag/commit doesn't exist.

```python
from huggingface_hub import RevisionNotFoundError

try:
    hf_hub_download("bert-base-uncased", "config.json", revision="nonexistent")
except RevisionNotFoundError:
    print("Revision doesn't exist")
```

### EntryNotFoundError / RemoteEntryNotFoundError

Raised when a file doesn't exist in the repo.

```python
from huggingface_hub import hf_hub_download, RemoteEntryNotFoundError

try:
    hf_hub_download("bert-base-uncased", "nonexistent.json")
except RemoteEntryNotFoundError:
    print("File doesn't exist in the repo")
```

### LocalEntryNotFoundError / IncompleteSnapshotError

Raised when a cached file is incomplete.

```python
from huggingface_hub import IncompleteSnapshotError

try:
    snapshot_download("bert-base-uncased")
except IncompleteSnapshotError as e:
    # Cache was interrupted; re-download
    snapshot_download("bert-base-uncased", force_download=True)
```

### OfflineModeIsEnabled

Raised when `HF_HUB_OFFLINE=1` and a network call is attempted.

```python
from huggingface_hub import OfflineModeIsEnabled

try:
    hf_hub_download("bert-base-uncased", "config.json")
except OfflineModeIsEnabled:
    print("Offline mode is enabled")
```

### HfHubHTTPError

Base HTTP error with request details.

```python
from huggingface_hub import HfHubHTTPError

try:
    api.create_repo("already-exists", token="hf_...")
except HfHubHTTPError as e:
    print(e.request_id)       # Server request ID
    print(e.server_message)   # Server error message
    e.append_to_message("\nAdditional context")
    raise
```

### InferenceTimeoutError

Raised when an inference request times out.

```python
from huggingface_hub import InferenceClient, InferenceTimeoutError

client = InferenceClient(timeout=5)
try:
    client.text_generation("Hello", max_new_tokens=10000)
except InferenceTimeoutError:
    print("Inference timed out")
```

### TextGenerationError and subclasses

```python
from huggingface_hub import (
    TextGenerationError,
    ValidationError,
    GenerationError,
    OverloadedError,
    IncompleteGenerationError,
)

try:
    client.text_generation("...", max_new_tokens=100000)
except OverloadedError:
    print("Server overloaded, retry later")
except ValidationError:
    print("Invalid generation parameters")
except GenerationError:
    print("Generation failed")
```

## Retry strategies

The library handles retries internally for network errors. Configure with environment variables:

```bash
export HF_HUB_HTTP_MAX_RETRIES=3
export HF_HUB_HTTP_RETRY_INTERVAL=0.5
export HF_HUB_HTTP_RETRY_INTERVAL_MAX=5.0
export HF_HUB_DOWNLOAD_MAX_RETRIES=3
```

For application-level retries:

```python
import time
from huggingface_hub import HfHubHTTPError, OverloadedError

def retry_on_error(fn, max_retries=3, backoff=1.0):
    for attempt in range(max_retries):
        try:
            return fn()
        except (HfHubHTTPError, OverloadedError) as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(backoff * (2 ** attempt))
```
