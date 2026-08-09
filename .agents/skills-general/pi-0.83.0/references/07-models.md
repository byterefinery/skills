# Custom Models

Add custom providers and models (Ollama, vLLM, LM Studio, proxies) via `~/.pi/agent/models.json`.

## Minimal Example

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

The `apiKey` value is a placeholder — Ollama ignores it. Keep a dummy value so models appear in `/model`.

For servers that don't support `developer` role or `reasoning_effort`:

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "compat": {
        "supportsDeveloperRole": false,
        "supportsReasoningEffort": false
      },
      "models": [
        { "id": "gpt-oss:20b", "reasoning": true }
      ]
    }
  }
}
```

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

The file reloads each time you open `/model`. Edit during session; no restart needed.

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
| `api` | API type |
| `apiKey` | API key config (supports `$ENV_VAR`, `!command`, literals) |
| `headers` | Custom headers (same value resolution as apiKey) |
| `authHeader` | Set `true` to add `Authorization: Bearer <apiKey>` automatically |
| `models` | Array of model configurations |
| `modelOverrides` | Per-model overrides for built-in models on this provider |

## Model Configuration

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `id` | Yes | — | Model identifier |
| `name` | No | `id` | Human-readable label |
| `api` | No | provider's `api` | Override provider's API |
| `reasoning` | No | `false` | Supports extended thinking |
| `thinkingLevelMap` | No | omitted | Maps pi thinking levels to provider values |
| `input` | No | `["text"]` | Input types: `["text"]` or `["text", "image"]` |
| `contextWindow` | No | `128000` | Context window in tokens |
| `maxTokens` | No | `16384` | Maximum output tokens |
| `cost` | No | all zeros | Per-million-token rates |
| `compat` | No | provider `compat` | Provider compatibility overrides |

### Thinking Level Map

Use `thinkingLevelMap` for model-specific thinking controls. Keys are pi levels: `off`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`. Values: string (supported, sent to provider), `null` (unsupported, hidden/skipped), or omitted (standard levels use default; `xhigh`/`max` unsupported).

```json
{
  "id": "deepseek-v4-pro",
  "reasoning": true,
  "thinkingLevelMap": {
    "minimal": null, "low": null, "medium": null,
    "high": "high", "xhigh": null, "max": "max"
  }
}
```

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

To merge custom models into a built-in provider, include `models`. Built-in models are kept; custom models are upserted by `id`.

## Per-model Overrides

```json
{
  "providers": {
    "openrouter": {
      "modelOverrides": {
        "anthropic/claude-sonnet-4": {
          "name": "Claude Sonnet 4 (Bedrock Route)",
          "compat": {
            "openRouterRouting": { "only": ["amazon-bedrock"] }
          }
        }
      }
    }
  }
}
```

## Compatibility

### Anthropic Messages

| Field | Description |
|-------|-------------|
| `supportsEagerToolInputStreaming` | Accepts per-tool `eager_input_streaming`. Default: `true` |
| `supportsLongCacheRetention` | Accepts `cache_control.ttl: "1h"`. Default: `true` |
| `forceAdaptiveThinking` | Send adaptive thinking for this model. Default: `false` |
| `allowEmptySignature` | Replay empty thinking signatures. Default: `false` |
| `supportsStrictTools` | Accepts strict JSON-schema tool definitions. Default: `false` |

### OpenAI Completions

| Field | Description |
|-------|-------------|
| `supportsDeveloperRole` | Use `developer` vs `system` role |
| `supportsReasoningEffort` | Support for `reasoning_effort` parameter |
| `supportsUsageInStreaming` | Supports `include_usage: true`. Default: `true` |
| `maxTokensField` | `max_completion_tokens` or `max_tokens` |
| `requiresToolResultName` | Include `name` on tool result messages |
| `thinkingFormat` | `openai`, `openrouter`, `deepseek`, `together`, `zai`, `qwen`, `chat-template`, `qwen-chat-template` |
| `cacheControlFormat` | `anthropic` for Anthropic-style `cache_control` markers |
| `supportsStrictMode` | Accepts strict JSON-schema function tool definitions |
