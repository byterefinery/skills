# openai-python 3.6.0 — Authentication and Cloud Providers

## API keys

- Default: `OPENAI_API_KEY` environment variable.
- Explicit: `OpenAI(api_key="sk-...")`.
- Refreshable: `api_key` may be a zero-arg callable returning a string, invoked per request.
- Prefer `.env` (e.g. via python-dotenv) over hardcoding keys in source.
- `api_key` and `workload_identity` are mutually exclusive.

## Workload identity authentication

For cloud-managed environments (Kubernetes, Azure, GCP), exchange short-lived identity-provider tokens instead of using long-lived API keys:

```python
from openai import OpenAI
from openai.auth import k8s_service_account_token_provider

client = OpenAI(workload_identity={
    "identity_provider_id": "idp-123",
    "service_account_id": "sa-456",
    "provider": k8s_service_account_token_provider(
        "/var/run/secrets/kubernetes.io/serviceaccount/token"
    ),
})
```

Built-in providers (all in `openai.auth`):

- `k8s_service_account_token_provider(token_path)` — Kubernetes service account token file
- `azure_managed_identity_token_provider(resource="https://management.azure.com/")` — Azure managed identity
- `gcp_id_token_provider(audience="https://api.openai.com/v1")` — GCP compute metadata
- Custom: pass `{"token_type": "jwt", "get_token": my_zero_arg_callable}`

Tokens are cached and refreshed automatically; `refresh_buffer_seconds` (default 1200) sets how long before expiration a refresh happens. Identity settings are captured when the client is constructed — create a new client to change identity.

## X.509 workload identity (mutual TLS)

For certificate-backed token exchange, configure an `ssl.SSLContext` on a custom HTTPX2 client and pass only the identity IDs:

```python
import os
import ssl
from openai import OpenAI, DefaultHttpx2Client
from openai.auth import x509_workload_identity

tls_context = ssl.create_default_context(cafile=os.getenv("OPENAI_MTLS_CA_BUNDLE"))
tls_context.load_cert_chain(
    certfile=os.environ["OPENAI_MTLS_CERTIFICATE_CHAIN"],  # leaf first, then intermediates
    keyfile=os.environ["OPENAI_MTLS_PRIVATE_KEY"],
    password=os.getenv("OPENAI_MTLS_PRIVATE_KEY_PASSWORD"),
)

client = OpenAI(
    workload_identity=x509_workload_identity(
        identity_provider_id=os.environ["OPENAI_IDENTITY_PROVIDER_ID"],
        service_account_id=os.environ["OPENAI_SERVICE_ACCOUNT_ID"],
    ),
    http_client=DefaultHttpx2Client(verify=tls_context, follow_redirects=False),
)
```

Constraints:

- Defaults to `https://mtls.api.openai.com/v1` when no `base_url` / `OPENAI_BASE_URL` is set.
- Requests must stay HTTPS on the configured origin; the `Host` header must match.
- API-key headers and proxy-only headers cannot be sent alongside X.509 auth.
- Azure clients do not support X.509 workload identity.
- Supports HTTP APIs only — Realtime/WebSockets excluded.
- Use `AsyncOpenAI` + `DefaultAsyncHttpx2Client` for async; see `examples/x509_workload_identity.py` (sync) and `examples/x509_workload_identity_async.py` (async).

## API-key mutual TLS (mTLS)

For API-key authenticated requests over mTLS, the certificate belongs to the HTTP client, not the base URL:

```python
import os
import ssl
from openai import OpenAI, DefaultHttpx2Client

ssl_context = ssl.create_default_context(cafile=os.environ.get("OPENAI_MTLS_CA_BUNDLE"))
ssl_context.load_cert_chain(
    certfile=os.environ["OPENAI_MTLS_CERTIFICATE_CHAIN"],
    keyfile=os.environ["OPENAI_MTLS_PRIVATE_KEY"],
    password=os.environ.get("OPENAI_MTLS_PRIVATE_KEY_PASSWORD"),
)

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ.get("OPENAI_BASE_URL", "https://mtls.api.openai.com/v1"),
    http_client=DefaultHttpx2Client(verify=ssl_context, follow_redirects=False),
)
```

Operational rules:

- A certificate-bearing client is transport-wide — dedicate it to the mTLS origin. Do not pass it through `with_options()` with a different `base_url`, or reuse it for unrelated services.
- `load_cert_chain()` fails fast on unreadable/malformed files or a key that does not match the leaf.
- Provide a complete leaf-first client-chain PEM (OpenAI does not fetch missing intermediates via AIA).
- For rotation, build a new `SSLContext`, HTTP client, and SDK client; close the old client after in-flight requests finish — existing TLS connections do not renegotiate.

## Webhook verification

`client.webhooks` verifies that incoming webhook POSTs came from OpenAI. The `webhook_secret` comes from the `OPENAI_WEBHOOK_SECRET` env var by default. **The `body` argument must be the raw JSON string as sent by the server — do not parse it first.**

```python
from openai import OpenAI
from flask import Flask, request

app = Flask(__name__)
client = OpenAI()  # OPENAI_WEBHOOK_SECRET env var used by default

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_data(as_text=True)  # raw JSON string
    try:
        event = client.webhooks.unwrap(body, request.headers)  # verify + parse
    except Exception as e:
        return "Invalid signature", 400
    if event.type == "response.completed":
        print(event.data)
    return "ok"
```

- `client.webhooks.unwrap(body, headers)` — verify signature and parse into an event object; raises on invalid signature
- `client.webhooks.verify_signature(body, headers)` — verify only; parse the body yourself afterwards

## Azure OpenAI

Use `AzureOpenAI` (async: `AsyncAzureOpenAI`) for Azure-hosted OpenAI. The Azure API shape differs from the core API, so static response/param types are not always correct.

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://example-endpoint.openai.azure.com",
    api_version="2023-07-01-preview",
)

completion = client.chat.completions.create(
    model="deployment-name",  # deployment, not model id
    messages=[{"role": "user", "content": "Hello"}],
)
```

Options and env vars:

- `azure_endpoint` / `AZURE_OPENAI_ENDPOINT`
- `api_version` / `OPENAI_API_VERSION`
- `api_key` / `AZURE_OPENAI_API_KEY`
- `azure_ad_token` / `AZURE_OPENAI_AD_TOKEN` (Microsoft Entra ID)
- `azure_ad_token_provider` (refreshable AD tokens)
- `azure_deployment` (default deployment name)

An explicit credential takes precedence over Azure credential env vars.

## Amazon Bedrock

Use the standard `OpenAI` client with the Bedrock provider for Bedrock's OpenAI-compatible Mantle endpoint:

```sh
pip install 'openai[bedrock]'
```

```python
from openai import OpenAI
from openai.providers import bedrock

client = OpenAI(provider=bedrock(region="us-west-2"))

response = client.responses.create(model="openai.gpt-5.4", input="Say hello!")
print(response.output_text)
```

- The provider configures AWS SigV4 auth and the `https://bedrock-mantle.<region>.api.aws/openai/v1` endpoint while keeping normal SDK resources, retries, streaming, and error handling.
- Region can come from `AWS_REGION`, `AWS_DEFAULT_REGION`, or the AWS profile instead of the `region` argument.
- Named profile: `bedrock(profile="my-profile")`. Explicit credentials: `access_key_id`, `secret_access_key`, optional `session_token`, or a refreshable `credential_provider` returning botocore-compatible credentials.
- Bearer tokens (Bedrock API keys) remain available: `bedrock(region=..., token_provider=lambda: refresh_token())`, or set `AWS_BEARER_TOKEN_BEDROCK`. Without explicit auth, `AWS_BEARER_TOKEN_BEDROCK` wins over the default credential chain for backwards compatibility.
- Endpoint override: `base_url` argument to `bedrock(...)` or `AWS_BEDROCK_BASE_URL`; custom URLs keep Mantle signing by default, `endpoint="runtime"` switches to Runtime signing.
- `provider=...` cannot be combined with top-level `api_key`, `admin_api_key`, `workload_identity`, or `base_url` — move those into `bedrock(...)`.

Legacy clients `BedrockOpenAI` / `AsyncBedrockOpenAI` (`client = BedrockOpenAI(aws_region="us-west-2", aws_profile="my-profile")`, or module-level `openai.api_type = "amazon-bedrock"`) still work but new code should prefer `OpenAI(provider=bedrock(...))`.
