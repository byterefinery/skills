# 08 — Errors

Exception hierarchy in `huggingface_hub.errors` (verified from `errors.py`).

## Hub / HTTP

- `HfHubHTTPError(HTTPError, OSError)` — base for Hub HTTP failures (carries the HTTP status and response)
- `RepositoryNotFoundError(HfHubHTTPError)` — repo does not exist (or is not accessible)
- `GatedRepoError(RepositoryNotFoundError)` — repo is gated and the token lacks access
- `DisabledRepoError(HfHubHTTPError)` — repo exists but is disabled
- `RevisionNotFoundError(HfHubHTTPError)` — branch/tag/commit not found
- `RevisionResolutionError(Exception)` — revision could not be resolved
- `BadRequestError(HfHubHTTPError, ValueError)` — malformed request
- `HFValidationError(ValueError)` — client-side validation of inputs
- `HfUriError(ValueError)` — invalid `hf://` URI

## Files and cache

- `EntryNotFoundError(Exception)` — base for "entry not found"
- `RemoteEntryNotFoundError(HfHubHTTPError, EntryNotFoundError)` — file missing on the Hub
- `LocalEntryNotFoundError(FileNotFoundError, EntryNotFoundError)` — file missing locally
- `IncompleteSnapshotError(LocalEntryNotFoundError)` — partial download / interrupted snapshot
- `CacheNotFound(Exception)` — no cache found at the given path
- `CorruptedCacheException(Exception)` — cache is corrupted
- `CachedRepoTreeNotFoundError(Exception)` — cached tree missing
- `DryRunError(OSError)` — dry-run resolution failed
- `FileMetadataError(OSError)` — file metadata fetch failed
- `FileDuplicationError(Exception)` — duplicate file conflict

## Offline

- `OfflineModeIsEnabled(ConnectionError)` — raised for any HTTP request when `HF_HUB_OFFLINE` (or `TRANSFORMERS_OFFLINE`) is set

## Auth

- `LocalTokenNotFoundError(EnvironmentError)` — no stored token found
- `OIDCError(Exception)` — OpenID Connect flow failure
- `DeviceCodeError(Exception)` — device-code OAuth failure
- `OAuthErrorCode(str, Enum)` — error codes from the OAuth flow

## Inference

- `InferenceTimeoutError(HTTPError, TimeoutError)`
- `InferenceEndpointError(Exception)` / `InferenceEndpointTimeoutError(InferenceEndpointError, TimeoutError)`
- `TextGenerationError(HTTPError)` — base with `ValidationError`, `GenerationError`, `OverloadedError`, `IncompleteGenerationError`, `UnknownError`

## Safetensors

- `SafetensorsParsingError(Exception)`
- `NotASafetensorsRepoError(Exception)`
- `StrictDataclassError` and subclasses (`StrictDataclassDefinitionError`, `StrictDataclassFieldValidationError`, `StrictDataclassClassValidationError`) — generated inference dataclass validation

## Buckets

- `BucketNotFoundError(HfHubHTTPError)`
- `BucketBatchError(HfHubHTTPError)` — batch bucket operation failure

## Jobs

- `JobNotFoundError(HfHubHTTPError)`

## Xet

- `XetDownloadError(Exception)`

## DDUF (dataset dump format)

- `DDUFError(Exception)` — base
- `DDUFCorruptedFileError(DDUFError)`
- `DDUFExportError(DDUFError)`
- `DDUFInvalidEntryNameError(DDUFExportError)`

## CLI / sandbox

- `CLIError(Exception)`, `ConfirmationError(CLIError)`, `CLIExtensionInstallError(CLIError)`
- `SandboxError(Exception)`, `SandboxCommandError(SandboxError)`
