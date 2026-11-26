# Authentication and Providers (v3.60.0)

## API key

Default. `api_key=` constructor option or the `OPENAI_API_KEY` environment variable. `client.webhooks` uses `OPENAI_WEBHOOK_SECRET` for signature verification.

## Workload identity

For cloud-managed environments — short-lived tokens from cloud identity providers instead of long-lived API keys:

```python
from openai import OpenAI
from openai.auth import k8s_service_account_token_provider

client = OpenAI(
    workload_identity={
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": k8s_service_account_token_provider("/var/run/secrets/kubernetes.io/serviceaccount/token"),
    },
)
```

Providers in `openai.auth`:

- `k8s_service_account_token_provider(token_path)` — Kubernetes service account tokens
- `azure_managed_identity_token_provider(resource="https://management.azure.com/")` — Azure managed identity
- `gcp_id_token_provider(audience="https://api.openai.com/v1")` — GCP compute metadata
- Custom: `{"token_type": "jwt", "get_token": callable_returning_jwt}`

`refresh_buffer_seconds` customizes the token refresh buffer (default 1200 s = 20 minutes before expiration).

## X.509 workload identity (mTLS)

`openai.auth.x509_workload_identity(identity_provider_id=..., service_account_id=..., refresh_buffer_seconds=...)` plus a `DefaultHttpx2Client(verify=ssl_context, follow_redirects=False)`. Defaults to `https://mtls.api.openai.com/v1`; HTTP-only (no Realtime/WebSocket); no Azure support; identity captured at construction. See [02-http-httpx2](02-http-httpx2.md) for constraints.

## Azure OpenAI

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2023-07-01-preview",
    azure_endpoint="https://example-endpoint.openai.azure.com",
)
completion = client.chat.completions.create(
    model="deployment-name",
    messages=[{"role": "user", "content": "How do I output all files in a directory using Python?"}],
)
```

Options: `azure_endpoint` (`AZURE_OPENAI_ENDPOINT`), `azure_deployment`, `api_version` (`OPENAI_API_VERSION`), `azure_ad_token` (`AZURE_OPENAI_AD_TOKEN`), `azure_ad_token_provider`; the API key comes from `AZURE_OPENAI_API_KEY`. Entra ID example: `examples/azure_ad.py`. Caveat: the Azure API shape differs from core — static types for responses/params are not always correct.

## Amazon Bedrock

The standard clients connect to Bedrock's OpenAI-compatible endpoints via `openai.providers.bedrock`:

```python
pip install 'openai[bedrock]'   # botocore + urllib3, for SigV4

from openai import OpenAI
from openai.providers import bedrock

client = OpenAI(provider=bedrock(region="us-west-2"))   # Mantle endpoint, default AWS credential chain
response = client.responses.create(model="openai.gpt-5.4", input="Say hello!")
```

Endpoint selection (region from `region`, `AWS_REGION`, `AWS_DEFAULT_REGION`, or the selected AWS profile):

| `endpoint` | Default API root | SigV4 signing service |
| --- | --- | --- |
| `"mantle"` (default) | `https://bedrock-mantle.<region>.api.aws/openai/v1` | `bedrock-mantle` |
| `"runtime"` | `https://bedrock-runtime.<region>.amazonaws.com/openai/v1` | `bedrock` |

- Canonical Mantle/Runtime URLs select the endpoint and signing service automatically; custom/proxy URLs keep Mantle signing unless `endpoint="runtime"`.
- `base_url=` or `AWS_BEDROCK_BASE_URL` overrides the derived API root; AWS's Runtime Chat Completions docs describe a `/v1` route — override `base_url` when needed (SDK default is `/openai/v1`).
- Runtime Chat Completions uses inference-profile model IDs such as `us.openai.gpt-5.6-sol` / `us.openai.gpt-5.6-terra` / `us.openai.gpt-5.6-luna`; bare model IDs are not accepted by these deployments. Global profiles (`global.openai.gpt-5.6-sol`) need matching AWS account permissions.
- Authentication precedence: explicit bearer/static AWS credentials/profile/credential provider → `AWS_BEARER_TOKEN_BEDROCK` (unless `api_key=None` disables it) → default AWS credential chain. Explicit bearer and AWS credential modes are mutually exclusive. `token_provider=` is called before every request attempt, including retries (async callables supported).
- Signed requests require replayable bodies and do not auto-follow redirects; canonical endpoints must be HTTPS and match the configured endpoint family and region.
- Streaming works with `stream=True`. Examples: `examples/bedrock.py`, `examples/bedrock_runtime.py`.
- Legacy `BedrockOpenAI` / `AsyncBedrockOpenAI` clients still work (delegate to the same provider); the module client honors `openai.api_type = "amazon-bedrock"` / `OPENAI_API_TYPE=amazon-bedrock`.

## Google Cloud Vertex AI

The standard clients send Responses API requests to Vertex AI via `openai.providers.vertex`:

```python
pip install 'openai[vertex]'   # google-auth[requests]

from openai import OpenAI
from openai.providers import vertex

client = OpenAI(provider=vertex(project="my-google-project", location="us-east5"))
response = client.responses.create(model="your-enabled-model", input="Hello", store=False)
```

- `project` / `location` can come from `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION` instead.
- Configure Application Default Credentials for a Google Cloud project with access to the target model; `credentials=` supplies existing Google credentials.
- `token_provider=` supplies a bearer-token callback per request attempt (works without the `vertex` extra); with `AsyncOpenAI` it may return an awaitable, runs on the event loop, must not block, and is bounded by the read timeout (`APITimeoutError` if it finishes late).
- Google auth uses the configured connect and read timeouts separately; waiting on a shared credential refresh uses the pool timeout; async caller cancellation stops waiting (in-progress Google credential work finishes in its worker thread).
- `base_url=` only when you trust the full API root to receive Google credentials; Google endpoints require HTTPS and redirects are disabled.
