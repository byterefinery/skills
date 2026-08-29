# Providers and models

Pi maintains a per-provider catalog of tool-capable models; configured catalogs refresh automatically (`pi update --models` forces it). Select with `/model` (Ctrl+L) or `--model provider/id:thinking`.

## Authentication resolution order

1. CLI `--api-key`
2. `~/.pi/agent/auth.json` entry (API key or OAuth token)
3. Environment variable
4. Custom provider keys from `models.json`

## Subscriptions (`/login`)

ChatGPT Plus/Pro (Codex), Claude Pro/Max, GitHub Copilot, xAI (Grok/X), OpenRouter (PKCE flow mints a user-controlled API key billed from credits), Radius. `/logout` clears credentials. OAuth tokens store in `auth.json` and auto-refresh; headless OpenRouter login accepts a pasted redirect URL/code.

Notes: Claude Pro/Max usage from third-party harnesses draws from paid **extra usage**, not plan limits. Copilot "model not supported" → enable the model in VS Code Copilot Chat. Azure/Bedrock/Cloudflare/Vertex details below.

## API keys

Env var or `/login` (stored in `auth.json`, created `0600`). **auth.json beats env vars.**

| Provider | Env var | `auth.json` key |
|---|---|---|
| Anthropic | `ANTHROPIC_API_KEY` | `anthropic` |
| OpenAI | `OPENAI_API_KEY` | `openai` |
| Azure OpenAI Responses | `AZURE_OPENAI_API_KEY` | `azure-openai-responses` |
| Ant Ling | `ANT_LING_API_KEY` | `ant-ling` |
| DeepSeek | `DEEPSEEK_API_KEY` | `deepseek` |
| NVIDIA NIM | `NVIDIA_API_KEY` | `nvidia` |
| Google Gemini | `GEMINI_API_KEY` | `google` |
| Amazon Bedrock | `AWS_BEARER_TOKEN_BEDROCK` | `amazon-bedrock` |
| Mistral | `MISTRAL_API_KEY` | `mistral` |
| Groq | `GROQ_API_KEY` | `groq` |
| Cerebras | `CEREBRAS_API_KEY` | `cerebras` |
| Cloudflare (Gateway + Workers AI) | `CLOUDFLARE_API_KEY` (+`CLOUDFLARE_ACCOUNT_ID`, +`CLOUDFLARE_GATEWAY_ID`) | `cloudflare-ai-gateway`, `cloudflare-workers-ai` |
| xAI | `XAI_API_KEY` | `xai` |
| OpenRouter | `OPENROUTER_API_KEY` | `openrouter` |
| Vercel AI Gateway | `AI_GATEWAY_API_KEY` | `vercel-ai-gateway` |
| ZAI Global / China | `ZAI_API_KEY` / `ZAI_CODING_CN_API_KEY` | `zai` / `zai-coding-cn` |
| OpenCode Zen / Go | `OPENCODE_API_KEY` | `opencode` / `opencode-go` |
| Radius | `RADIUS_API_KEY` | `radius` |
| Hugging Face | `HF_TOKEN` | `huggingface` |
| Fireworks / Together / Baseten | `FIREWORKS_API_KEY` / `TOGETHER_API_KEY` / `BASETEN_API_KEY` | `fireworks` / `together` / `baseten` |
| Kimi For Coding | `KIMI_API_KEY` | `kimi-coding` |
| MiniMax (Intl/CN) | `MINIMAX_API_KEY` / `MINIMAX_CN_API_KEY` | `minimax` / `minimax-cn` |
| Qwen Token Plan (3 variants) | `QWEN_TOKEN_PLAN_API_KEY` (Intl + Individual), `QWEN_TOKEN_PLAN_CN_API_KEY` | `qwen-token-plan[-individual|-cn]` |
| Xiaomi MiMo (+3 token plans) | `XIAOMI_API_KEY`, `XIAOMI_TOKEN_PLAN_{CN,AMS,SGP}_API_KEY` | `xiaomi`, `xiaomi-token-plan-{cn,ams,sgp}` |

Also: Moonshot AI, Vertex AI, GitHub Copilot, OpenAI Codex, any OpenAI-compatible API (Ollama, vLLM, LM Studio).

### auth.json

```json
{
  "anthropic": { "type": "api_key", "key": "sk-ant-..." },
  "cloudflare-ai-gateway": {
    "type": "api_key", "key": "$CLOUDFLARE_API_KEY",
    "env": { "CLOUDFLARE_ACCOUNT_ID": "..." }
  }
}
```

`key` resolution: `!command` (executes, stdout cached per process — pi adds no TTL; wrap slow/expensive commands in your own script), `$ENV_VAR` / `${ENV_VAR}` interpolation, `$$` → literal `$`, `$!` → literal `!`, plain literals (uppercase `MY_API_KEY` is a literal, not an env lookup). Provider-scoped `env` values are used before process env for that provider. OAuth credentials also live here after `/login`.

## Cloud providers

- **Azure OpenAI** — `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_BASE_URL` (root endpoints auto-normalized to `/openai/v1`) or `AZURE_OPENAI_RESOURCE_NAME`; optional `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_DEPLOYMENT_NAME_MAP` (`gpt-4o=my-gpt4o`).
- **Amazon Bedrock** — `/login amazon-bedrock` or ambient AWS creds (`AWS_PROFILE`, IAM keys, `AWS_BEARER_TOKEN_BEDROCK`, ECS/IRSA); `AWS_REGION` defaults us-east-1. Proxy: `AWS_ENDPOINT_URL_BEDROCK_RUNTIME`, `AWS_BEDROCK_SKIP_AUTH=1`, `AWS_BEDROCK_FORCE_HTTP1=1`. Cache points: `AWS_BEDROCK_FORCE_CACHE=1` for application inference profiles.
- **Cloudflare AI Gateway** — routes OpenAI/Anthropic/Workers AI through the gateway; auth is `cf-aig-authorization`; upstream via unified billing, stored BYOK, or inline BYOK (extra `Authorization` header).
- **Cloudflare Workers AI** — model IDs like `@cf/moonshotai/kimi-k2.6`; pi sets `x-session-affinity` for prefix-cache discounts.
- **Google Vertex** — ADC (`gcloud auth application-default login`), `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, or `GOOGLE_APPLICATION_CREDENTIALS`.

## Custom models — `models.json`

Add providers/models without code in `~/.pi/agent/models.json` (or a runtime-specific path). Supported APIs: `openai-completions`, `openai-responses`, `anthropic-messages`, `google-generative-ai`.

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "apiKey": "ollama",
      "api": "openai-completions",
      "models": [
        {
          "id": "qwen3:32b",
          "name": "Qwen3 32B",
          "reasoning": true,
          "input": ["text", "image"],
          "contextWindow": 131072,
          "maxTokens": 8192,
          "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
        }
      ]
    }
  }
}
```

**Provider fields:** `baseUrl`, `api`, `apiKey`, `oauth` (`"radius"` only), `headers`, `authHeader: true` (adds `Authorization: Bearer`), `models`, `modelOverrides` (per-model overrides for built-in/extension models on this provider). Non-built-in providers need `baseUrl` + `api` at provider or model level; `apiKey` is not required to load — models appear once auth exists via `/login`/`auth.json`/`--api-key` (otherwise they load but stay unavailable).

**Model fields:** `id` (required; sent to the API), `name` (matching + detail text; footer always shows `id`), `api` (per-model override), `reasoning`, `input` (`["text"]` or `["text","image"]`), `contextWindow` (default 128000), `maxTokens` (16384), `cost` (per-million rates + optional `tiers` — a tier replaces all rates when total input usage exceeds `inputTokensAbove`; highest matching threshold wins), `samplingParams`, `compat`, `thinkingLevelMap`.

- **`samplingParams`** — merged verbatim into every OpenAI-compatible request body *after* pi's fields, so its keys win (use for `top_k`, `min_p`, temperature). Ignored by other APIs.
- **`thinkingLevelMap`** — keys are pi levels `off`..`max`; values tristate: omitted = provider default (extended `xhigh`/`max` unsupported), string = sent to provider, `null` = unsupported (hidden/clamped). Migrations: old `compat.reasoningEffortMap` moves here.
- **Overriding built-in providers** — `providers: { "anthropic": { "baseUrl": "https://proxy..." } }` keeps all built-in models and auth. Adding a `models` array upserts by `id`: matching ids replace built-ins, new ids are added.

## Custom providers (extensions)

For unsupported APIs or custom OAuth, register a provider from an extension: `pi.registerProvider(name, config)` (see [04-extensions](04-extensions.md)). Key capabilities:

- **OAuth** — `oauth: { name, login(callbacks), refreshToken, getApiKey }` makes the provider appear in `/login`.
- **Custom streaming** — implement `streamSimple` for non-standard APIs; emit the standard event sequence (start, text/thinking/toolcall deltas, done/error) with usage and cost; signal context-window overflow with the dedicated overflow error so compaction/retry can recover.
- **Dynamic catalogs** — `refreshModels({ signal })` for live servers (llama.cpp); persist selectively via generation-checked `context.publish({ persist })`.
- **Full pi-ai Provider** — `createProvider({...})` with native `auth`, `getModels`, `filterModels`, `stream` for complete control; `models.json` overrides still layer above it.

## llama.cpp

Run the llama.cpp router server, then in pi: `/login llama.cpp`, manage downloads/loaded models with `/llama`, pick a loaded model with `/model`. The provider can also be registered dynamically via `refreshModels` (see custom providers).

## Model selection

- `/model` — interactive selector; `/scoped-models` or `enabledModels` setting/`--models` limits the Ctrl+P cycling set.
- `--model provider/id`, `--model id:thinking` (e.g. `sonnet:high`), `--provider` + `--model`, `--list-models [search]`.
- Thinking levels: `off`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max` — clamped to model capability (`thinkingLevelMap`); Shift+Tab cycles in the editor.
