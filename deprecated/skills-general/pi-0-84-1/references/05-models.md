# models.json

Add custom providers and models (Ollama, vLLM, LM Studio, proxies) via `~/.pi/agent/models.json`. The file reloads each time you open `/model` — no restart needed.

## Minimal Example

For local models, only `id` is required:

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "models": [
        { "id": "llama3.1:8b" },
        { "id": "qwen2.5-coder:7b" }
      ]
    }
  }
}
```

Keep a dummy `apiKey` for keyless servers so pi treats them as authenticated.

## Full Example

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "models": [
        {
          "id": "llama3.1:8b",
          "name": "Llama 3.1 8B (Local)",
          "reasoning": false,
          "input": ["text"],
          "contextWindow": 128000,
          "maxTokens": 32000,
          "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
        }
      ]
    }
  }
}
```

## Supported APIs

| API | Description |
|-----|-------------|
| `openai-completions` | OpenAI Chat Completions (most compatible) |
| `openai-responses` | OpenAI Responses API |
| `anthropic-messages` | Anthropic Messages API |
| `google-generative-ai` | Google Generative AI |

## Provider Configuration

| Field | Description |
|-------|-------------|
| `baseUrl` | API endpoint URL |
| `api` | API type (see above) |
| `apiKey` | API key config (supports `$ENV`, `!command`, literals) |
| `oauth` | Dynamic OAuth type. Currently `"radius"` |
| `headers` | Custom headers (same value resolution as `apiKey`) |
| `authHeader` | Set `true` to add `Authorization: Bearer <apiKey>` automatically |
| `models` | Array of model configurations |
| `modelOverrides` | Per-model overrides for built-in models on this provider |
| `compat` | Provider-level compatibility flags |

### Value Resolution

- **Shell command:** `"!command"` executes and uses stdout
  ```json
  "apiKey": "!security find-generic-password -ws 'anthropic'"
  ```
- **Environment interpolation:** `"$ENV_VAR"` or `"${ENV_VAR}"`
  ```json
  "apiKey": "$MY_API_KEY"
  "apiKey": "${KEY_PREFIX}_${KEY_SUFFIX}"
  ```
- **Escapes:** `"$$"` → literal `$`, `"$!"` → literal `!`
- **Literal value:** Used directly

Shell commands resolve at request time with no built-in caching or TTL.

## Model Configuration

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `id` | Yes | — | Model identifier (passed to the API) |
| `name` | No | `id` | Human-readable label (used for matching and display) |
| `api` | No | provider's `api` | Override provider's API for this model |
| `reasoning` | No | `false` | Supports extended thinking |
| `thinkingLevelMap` | No | omitted | Maps pi thinking levels to provider values |
| `input` | No | `["text"]` | Input types: `["text"]` or `["text", "image"]` |
| `contextWindow` | No | `128000` | Context window size in tokens |
| `maxTokens` | No | `16384` | Maximum output tokens |
| `samplingParams` | No | omitted | Free-form params merged into every request body |
| `cost` | No | all zeros | Per-million-token rates with optional tiers |
| `compat` | No | provider `compat` | Compatibility overrides |

### Cost Tiers

```json
{
  "cost": {
    "input": 5,
    "output": 30,
    "cacheRead": 0.5,
    "cacheWrite": 6.25,
    "tiers": [
      {
        "inputTokensAbove": 272000,
        "input": 10,
        "output": 45,
        "cacheRead": 1,
        "cacheWrite": 12.5
      }
    ]
  }
}
```

### Thinking Level Map

```json
{
  "id": "deepseek-v4-pro",
  "reasoning": true,
  "thinkingLevelMap": {
    "minimal": null,
    "low": null,
    "medium": null,
    "high": "high",
    "xhigh": null,
    "max": "max"
  }
}
```

Values: omitted (standard/default), string (supported, sends this value), `null` (unsupported, hidden).

### Sampling Parameters

```json
{
  "id": "deepseek-v4-flash",
  "samplingParams": {
    "temperature": 1.0,
    "top_p": 0.95,
    "top_k": 0,
    "min_p": 0.0
  }
}
```

Only OpenAI-compatible APIs apply it. Keys override pi's named request fields.

## Overriding Built-in Providers

Route through a proxy without redefining models:

```json
{
  "providers": {
    "anthropic": {
      "baseUrl": "https://my-proxy.example.com/v1"
    }
  }
}
```

Merge custom models into a built-in provider:

```json
{
  "providers": {
    "anthropic": {
      "baseUrl": "https://my-proxy.example.com/v1",
      "apiKey": "$ANTHROPIC_API_KEY",
      "api": "anthropic-messages",
      "models": [{ "id": "custom-model", "reasoning": true }]
    }
  }
}
```

Merge semantics: built-in models kept, custom models upserted by `id`. Matching `id` replaces built-in; new `id` adds alongside.

## Per-model Overrides

```json
{
  "providers": {
    "openrouter": {
      "modelOverrides": {
        "anthropic/claude-sonnet-4": {
          "name": "Claude Sonnet 4 (Bedrock Route)",
          "compat": {
            "openRouterRouting": {
              "only": ["amazon-bedrock"]
            }
          }
        }
      }
    }
  }
}
```

Supported fields: `name`, `reasoning`, `thinkingLevelMap`, `input`, `cost` (partial), `contextWindow`, `maxTokens`, `samplingParams` (merged per key), `headers`, `compat`.

## OpenAI Compatibility

```json
{
  "providers": {
    "local-llm": {
      "baseUrl": "http://localhost:8080/v1",
      "api": "openai-completions",
      "compat": {
        "supportsDeveloperRole": false,
        "supportsReasoningEffort": false,
        "supportsUsageInStreaming": false,
        "maxTokensField": "max_tokens"
      },
      "models": [...]
    }
  }
}
```

| Field | Description |
|-------|-------------|
| `supportsStore` | Provider supports `store` field |
| `supportsDeveloperRole` | Use `developer` vs `system` role |
| `supportsReasoningEffort` | Support for `reasoning_effort` parameter |
| `supportsUsageInStreaming` | Supports `stream_options: { include_usage: true }` (default: `true`) |
| `supportsFinishReason` | Streamed responses include `finish_reason` (default: `true`) |
| `maxTokensField` | Use `max_completion_tokens` or `max_tokens` |
| `requiresToolResultName` | Include `name` on tool result messages |
| `requiresAssistantAfterToolResult` | Insert assistant message before user after tool results |
| `requiresThinkingAsText` | Convert thinking blocks to plain text |
| `requiresReasoningContentOnAssistantMessages` | Include empty `reasoning_content` on replayed messages |
| `thinkingFormat` | `reasoning_effort`, `openrouter`, `deepseek`, `together`, `baseten`, `zai`, `qwen`, `chat-template`, `qwen-chat-template` |
| `chatTemplateKwargs` | `chat_template_kwargs` for `thinkingFormat: "chat-template"` |
| `chatTemplateArgs` | `chat_template_args` for `thinkingFormat: "baseten"` |
| `cacheControlFormat` | Anthropic-style `cache_control` markers (`"anthropic"`) |
| `sendSessionAffinityHeaders` | Send session-affinity headers when caching enabled (default: `false`) |
| `sessionAffinityFormat` | `openai`, `openai-nosession`, `openrouter` |
| `supportsStrictMode` | Accepts strict JSON-schema function tool definitions |
| `supportsOpenAIGrammarTools` | Emits custom Lark/regex grammar tools (default: `false`) |
| `deferredToolsMode` | Provider-specific deferred tool serialization (currently `"kimi"`) |
| `supportsLongCacheRetention` | Accepts long cache retention (default: `true`) |
| `openRouterRouting` | OpenRouter provider routing preferences |
| `vercelGatewayRouting` | Vercel AI Gateway routing config (`only`, `order`) |

## Anthropic Messages Compatibility

```json
{
  "providers": {
    "anthropic-proxy": {
      "baseUrl": "https://proxy.example.com",
      "api": "anthropic-messages",
      "apiKey": "$ANTHROPIC_PROXY_KEY",
      "compat": {
        "supportsEagerToolInputStreaming": false,
        "supportsLongCacheRetention": true,
        "forceAdaptiveThinking": true,
        "allowEmptySignature": true,
        "supportsStrictTools": true
      }
    }
  }
}
```

| Field | Description |
|-------|-------------|
| `supportsEagerToolInputStreaming` | Accepts per-tool `eager_input_streaming` (default: `true`) |
| `supportsLongCacheRetention` | Accepts `cache_control.ttl: "1h"` (default: `true`) |
| `sendSessionAffinityHeaders` | Send `x-session-affinity` from session id (default: auto) |
| `supportsCacheControlOnTools` | Accepts `cache_control` on tool definitions (default: `true`) |
| `forceAdaptiveThinking` | Send adaptive thinking (`thinking.type: "adaptive"`) (default: `false`) |
| `allowEmptySignature` | Replay empty thinking signatures (default: `false`) |
| `supportsStrictTools` | Accepts strict JSON-schema tool definitions (default: `false`) |

## Google AI Studio Example

```json
{
  "providers": {
    "my-google": {
      "baseUrl": "https://generativelanguage.googleapis.com/v1beta",
      "api": "google-generative-ai",
      "apiKey": "$GEMINI_API_KEY",
      "models": [
        {
          "id": "gemma-4-31b-it",
          "name": "Gemma 4 31B",
          "input": ["text", "image"],
          "contextWindow": 262144,
          "reasoning": true
        }
      ]
    }
  }
}
```

`baseUrl` is required for custom `google-generative-ai` models.
