# Environment Variables

Pi uses environment variables in three ways: process configuration, child process markers, and bash tool session metadata.

## Process Configuration

| Variable | Description |
|----------|-------------|
| `PI_CODING_AGENT_DIR` | Override config directory (default: `~/.pi/agent`) |
| `PI_CODING_AGENT_SESSION_DIR` | Override session storage (overridden by `--session-dir`) |
| `PI_PACKAGE_DIR` | Override package directory (useful for Nix/Guix) |
| `PI_OFFLINE` | Disable startup network operations when set to `1`/`true`/`yes` |
| `PI_SKIP_VERSION_CHECK` | Disable the `pi.dev` latest-version request |
| `PI_TELEMETRY` | Override install/update telemetry: `1`/`true`/`yes` or `0`/`false`/`no` |
| `PI_CACHE_RETENTION` | Set to `long` for extended prompt caching (Anthropic: 1h, OpenAI: 24h) |
| `PI_SHARE_VIEWER_URL` | Override base URL for `/share` (default: `https://pi.dev/session/`) |
| `PI_HARDWARE_CURSOR` | Set to `1` to show the hardware cursor |
| `VISUAL`, `EDITOR` | External editor fallback when `externalEditor` is unset |
| `HTTP_PROXY`, `HTTPS_PROXY` | Proxy outbound HTTP requests |

## Process Marker

The CLI and RPC entry points set `PI_CODING_AGENT=true`. Child processes inherit it and can use it to detect that they run inside Pi. It is not session-specific and is not set automatically when Pi is embedded through the SDK.

`AI_AGENT` is set to `pi` by the CLI and RPC entry points so generic tooling can attribute child processes.

## Bash Tool Session Environment

Commands run by the LLM-callable bash tool receive:

| Variable | Description |
|----------|-------------|
| `PI_SESSION_ID` | Current session ID |
| `PI_SESSION_FILE` | Absolute session JSONL path; unset for ephemeral sessions |
| `PI_PROVIDER` | Currently selected model provider |
| `PI_MODEL` | Currently selected model ID |
| `PI_REASONING_LEVEL` | Current reasoning level: `off`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max` |

Values are resolved when each command starts. Not injected into user-entered `!` or `!!` commands.

```bash
printf '%s/%s\n' "$PI_PROVIDER" "$PI_MODEL"
printf 'reasoning=%s session=%s\n' "$PI_REASONING_LEVEL" "$PI_SESSION_ID"

if [ -n "$PI_SESSION_FILE" ]; then
  tail -n 1 "$PI_SESSION_FILE"
fi
```

### Custom Bash Tools

Bash tools created with `createBashTool()` expose session environment by default. Disable:

```typescript
const bashTool = createBashTool(cwd, {
  exposeSessionEnvironment: false,
});
```

## Provider API Keys

| Provider | Environment Variable |
|----------|---------------------|
| Anthropic | `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_OAUTH_TOKEN` |
| Ant Ling | `ANT_LING_API_KEY` |
| Azure OpenAI | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_BASE_URL`, `AZURE_OPENAI_RESOURCE_NAME`, `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_DEPLOYMENT_NAME_MAP` |
| OpenAI | `OPENAI_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| NVIDIA NIM | `NVIDIA_API_KEY` |
| Google Gemini | `GEMINI_API_KEY` |
| Amazon Bedrock | `AWS_BEARER_TOKEN_BEDROCK`, `AWS_PROFILE`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` |
| Mistral | `MISTRAL_API_KEY` |
| Groq | `GROQ_API_KEY` |
| Cerebras | `CEREBRAS_API_KEY` |
| Cloudflare AI Gateway | `CLOUDFLARE_API_KEY`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_GATEWAY_ID` |
| Cloudflare Workers AI | `CLOUDFLARE_API_KEY`, `CLOUDFLARE_ACCOUNT_ID` |
| xAI | `XAI_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |
| Vercel AI Gateway | `AI_GATEWAY_API_KEY` |
| ZAI Coding Plan (Global) | `ZAI_API_KEY` |
| ZAI Coding Plan (China) | `ZAI_CODING_CN_API_KEY` |
| OpenCode Zen/Go | `OPENCODE_API_KEY` |
| Hugging Face | `HF_TOKEN` |
| Fireworks | `FIREWORKS_API_KEY` |
| Together AI | `TOGETHER_API_KEY` |
| Baseten | `BASETEN_API_KEY` |
| Kimi For Coding | `KIMI_API_KEY` |
| MiniMax | `MINIMAX_API_KEY`, `MINIMAX_CN_API_KEY` |
| Qwen Token Plan | `QWEN_TOKEN_PLAN_API_KEY`, `QWEN_TOKEN_PLAN_CN_API_KEY` |
| Xiaomi MiMo | `XIAOMI_API_KEY`, `XIAOMI_TOKEN_PLAN_CN_API_KEY`, `XIAOMI_TOKEN_PLAN_AMS_API_KEY`, `XIAOMI_TOKEN_PLAN_SGP_API_KEY` |
| Radius | `RADIUS_API_KEY` |

## Notes

- `PI_OFFLINE=1` disables all startup network operations: update checks, package update checks, and install/update telemetry.
- `PI_TELEMETRY=0` only disables the anonymous install/update ping and provider attribution headers. It does not disable update checks.
- Use `--offline` for one-run offline mode instead of setting `PI_OFFLINE`.
- `PI_SKIP_VERSION_CHECK=1` only disables the version check; pi may still contact `pi.dev` for telemetry unless `PI_TELEMETRY=0` or `PI_OFFLINE=1` is set.
