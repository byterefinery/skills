# Providers

Pi supports subscription-based providers via OAuth and API key providers via environment variables or auth file.

## Subscriptions

Use `/login` in interactive mode, then select a provider:

- ChatGPT Plus/Pro (Codex)
- Claude Pro/Max
- GitHub Copilot
- xAI (Grok/X subscription)
- OpenRouter (OAuth-minted API key billed from credits)
- Radius

Use `/logout` to clear credentials. Tokens stored in `~/.pi/agent/auth.json`, auto-refresh when expired.

### OpenAI Codex

Requires ChatGPT Plus or Pro subscription. Officially endorsed by OpenAI.

### Claude Pro/Max

Third-party harness usage draws from [extra usage](https://claude.ai/settings/usage) and is billed per token, not against Claude plan limits.

### GitHub Copilot

If you get "model not supported", enable it in VS Code: Copilot Chat → model selector → select model → "Enable".

### OpenRouter

Run `/login openrouter`, select "Sign in with OpenRouter" for PKCE authorization. Creates a user-controlled API key billed from credits. On remote/headless machines, paste the final redirect URL or authorization code into the login prompt.

## API Keys

Set via environment variable or store in `~/.pi/agent/auth.json` using `/login`. Auth file credentials take priority over environment variables.

| Provider | Environment Variable | `auth.json` key |
|----------|----------------------|------------------|
| Anthropic | `ANTHROPIC_API_KEY` | `anthropic` |
| OpenAI | `OPENAI_API_KEY` | `openai` |
| Google Gemini | `GEMINI_API_KEY` | `google` |
| DeepSeek | `DEEPSEEK_API_KEY` | `deepseek` |
| NVIDIA NIM | `NVIDIA_API_KEY` | `nvidia` |
| Amazon Bedrock | `AWS_BEARER_TOKEN_BEDROCK` | `amazon-bedrock` |
| Mistral | `MISTRAL_API_KEY` | `mistral` |
| Groq | `GROQ_API_KEY` | `groq` |
| Cerebras | `CEREBRAS_API_KEY` | `cerebras` |
| xAI | `XAI_API_KEY` | `xai` |
| OpenRouter | `OPENROUTER_API_KEY` | `openrouter` |
| Vercel AI Gateway | `AI_GATEWAY_API_KEY` | `vercel-ai-gateway` |
| Hugging Face | `HF_TOKEN` | `huggingface` |
| Fireworks | `FIREWORKS_API_KEY` | `fireworks` |
| Together AI | `TOGETHER_API_KEY` | `together` |

### Auth File

Store in `~/.pi/agent/auth.json` (created with `0600` permissions):

```json
{
  "anthropic": { "type": "api_key", "key": "sk-ant-..." },
  "openai": { "type": "api_key", "key": "sk-..." }
}
```

The `key` field supports:
- **Shell command:** `"!command"` — executes and uses stdout (cached for process lifetime)
- **Environment interpolation:** `"$ENV_VAR"` or `"${ENV_VAR}"`
- **Escapes:** `"$$"` emits literal `$`; `"$!"` emits literal `!`
- **Literal value:** Used directly

API key credentials can include provider-scoped environment values:

```json
{
  "cloudflare-ai-gateway": {
    "type": "api_key",
    "key": "$CLOUDFLARE_API_KEY",
    "env": {
      "CLOUDFLARE_API_KEY": "...",
      "CLOUDFLARE_ACCOUNT_ID": "account-id",
      "CLOUDFLARE_GATEWAY_ID": "gateway-id"
    }
  }
}
```

## Cloud Providers

### Azure OpenAI

```bash
export AZURE_OPENAI_API_KEY=...
export AZURE_OPENAI_BASE_URL=https://your-resource.ai.azure.com
# or: export AZURE_OPENAI_RESOURCE_NAME=your-resource
```

### Amazon Bedrock

```bash
# AWS Profile
export AWS_PROFILE=your-profile
# Or IAM keys
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=...
# Or bearer token
export AWS_BEARER_TOKEN_BEDROCK=...
```

For application inference profiles (ARNs without model name), set `AWS_BEDROCK_FORCE_CACHE=1` to enable cache points.

### Cloudflare AI Gateway

Routes to OpenAI, Anthropic, and Workers AI through Cloudflare. Supports unified billing, stored BYOK, and inline BYOK modes.

### Cloudflare Workers AI

Pi automatically sets `x-session-affinity` for prefix caching discounts.

### Google Vertex AI

Uses Application Default Credentials:

```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=your-project
export GOOGLE_CLOUD_LOCATION=us-central1
```

## Resolution Order

1. CLI `--api-key` flag
2. `auth.json` entry (API key or OAuth token)
3. Environment variable
4. Custom provider keys from `models.json`
