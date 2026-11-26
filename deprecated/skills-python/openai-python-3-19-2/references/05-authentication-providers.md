# Authentication and Providers

## API keys

`OpenAI(api_key=...)` or the `OPENAI_API_KEY` environment variable (recommended: keep keys out of source control, e.g., via `python-dotenv` / `.env`). The value may also be a callable that returns a key (refreshed per request). `admin_api_key` / `OPENAI_ADMIN_KEY` authenticate admin endpoints. Organization and project selection: `organization`/`OPENAI_ORG_ID`, `project`/`OPENAI_PROJECT_ID`.

## Workload identity (short-lived tokens)

For automated environments (Kubernetes, Azure, GCP) instead of long-lived API keys:

```python
from openai import OpenAI
from openai.auth import k8s_service_account_token_provider

client = OpenAI(
    workload_identity={
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": k8s_service_account_token_provider(
            "/var/run/secrets/kubernetes.io/serviceaccount/token"
        ),
    },
)
```

Built-in subject-token providers (from `openai.auth`): `k8s_service_account_token_provider(token_path)`, `azure_managed_identity_token_provider(resource=...)`, `gcp_id_token_provider(audience=...)`. A custom provider is a dict `{"token_type": "jwt", "get_token": callable}`. Tokens are exchanged (default endpoint `https://auth.openai.com/oauth/token`), cached in memory, and refreshed automatically; the default refresh buffer is 1200s before expiration — tune with `refresh_buffer_seconds`. `workload_identity` and `api_key` are mutually exclusive.

## X.509 workload identity (mutual TLS)

For X.509 federation, pass `x509_workload_identity(identity_provider_id=..., service_account_id=...)` plus an HTTP client carrying the client certificate (`DefaultHttpx2Client(verify=tls_context, follow_redirects=False)`). The client defaults to `https://mtls.api.openai.com/v1` when no `base_url`/`OPENAI_BASE_URL` is set; token exchange is pinned to the mTLS auth origin. Certificates, keys, and trust remain application/transport concerns. See 02-http-httpx2 for the full recipe.

## Data residency

`OpenAI(data_residency="us")` selects a fixed regional endpoint (`"global"` → api.openai.com, `"us"` → us.api.openai.com, `"eu"` → eu.api.openai.com, `"ae"` → ae.api.openai.com) and cannot be combined with `base_url`, `websocket_base_url`, or `provider`.

## Azure OpenAI

Use `AzureOpenAI` (or `AsyncAzureOpenAI`):

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://example-endpoint.openai.azure.com",  # or AZURE_OPENAI_ENDPOINT
    api_version="2023-07-01-preview",                            # or OPENAI_API_VERSION
)  # api key from AZURE_OPENAI_API_KEY; azure_ad_token / azure_ad_token_provider also supported
completion = client.chat.completions.create(
    model="deployment-name",  # deployment name, not model ID
    messages=[{"role": "user", "content": "..."}],
)
```

Options: `azure_endpoint`, `azure_deployment`, `api_version`, `azure_ad_token`, `azure_ad_token_provider` (plus their env-var forms; `azure_endpoint` + `base_url` are mutually exclusive). The Azure API shape differs from the core API, so static response/param types are not always correct. See `examples/azure_ad.py` in the repo for Microsoft Entra ID (Azure AD) authentication. Azure clients do not support X.509 workload identity.

## Amazon Bedrock

The Bedrock provider connects the standard `OpenAI`/`AsyncOpenAI` clients to Bedrock's OpenAI-compatible endpoints. Bearer tokens work with no extra dependencies; SigV4 requires `pip install 'openai[bedrock]'` (botocore).

```python
from openai import OpenAI
from openai.providers import bedrock

client = OpenAI(provider=bedrock(region="us-west-2"))   # Mantle endpoint + SigV4 by default
response = client.responses.create(model="openai.gpt-5.4", input="Say hello!")
```

- **Endpoints** — `"mantle"` (default): `https://bedrock-mantle.<region>.api.aws/openai/v1`, SigV4 service `bedrock-mantle`; `"runtime"`: `https://bedrock-runtime.<region>.amazonaws.com/openai/v1` (partition-aware DNS suffixes), SigV4 service `bedrock`. Canonical URLs of either family select the matching signing service automatically; custom URLs default to Mantle signing — pass `endpoint="runtime"` when a custom host needs Runtime signing. Override the derived root with `base_url=...` on `bedrock(...)` or `AWS_BEDROCK_BASE_URL`.
- **Region** — explicit `region`, else `AWS_REGION` / `AWS_DEFAULT_REGION`, else the selected profile.
- **Auth precedence** — explicit bearer credentials / static AWS credentials / named `profile` / `credential_provider` first; then `AWS_BEARER_TOKEN_BEDROCK` env (for backwards compatibility) — unless `api_key=None`, which disables the env-bearer fallback and forces SigV4; otherwise the default AWS credential chain (env, shared config/profiles, SSO, assume-role, ECS/EKS/EC2 workload credentials). Explicit bearer and AWS credential modes are mutually exclusive. A stale `AWS_BEARER_TOKEN_BEDROCK` shadows the credential chain — unset it or pass `api_key=None`.
- **Token providers** — `token_provider=callable` (sync or async for `AsyncOpenAI`) is invoked before every request attempt, including retries.
- **Constraints** — SigV4 requires replayable, fully serialized request bodies (standard JSON is fine; streaming responses unaffected); signed requests do not automatically follow redirects. Canonical endpoints must be HTTPS and region-consistent; credentials are never attached to other origins.
- **Models** — use inference-profile IDs (e.g., `us.openai.gpt-5.6-sol`); bare model IDs are not accepted by those deployments. AWS controls which routes/models/features are supported; unsupported calls surface as normal HTTP errors through the SDK.

Legacy clients: `BedrockOpenAI(aws_region=..., aws_profile=...)` / `AsyncBedrockOpenAI` still work and delegate to the same provider; `openai.api_type = "amazon-bedrock"` (or `OPENAI_API_TYPE`) uses them via the module client. New code should prefer `OpenAI(provider=bedrock(...))`.
