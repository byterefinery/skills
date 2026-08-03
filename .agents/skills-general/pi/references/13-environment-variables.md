# Environment Variables

Pi uses environment variables in three ways:

1. Variables such as `PI_OFFLINE` configure the Pi process
2. Pi sets `PI_CODING_AGENT` so child processes can detect they run inside Pi
3. Commands run by the bash tool receive `PI_*` variables describing the current session

## Process Marker

`PI_CODING_AGENT=true` is set by the CLI and RPC entry points. Child processes inherit it. Not set when Pi is embedded through the SDK.

## Bash Tool Session Environment

Commands run by the LLM-callable bash tool receive:

| Variable | Description |
|----------|-------------|
| `PI_SESSION_ID` | Current session ID |
| `PI_SESSION_FILE` | Absolute path to session JSONL; unset for ephemeral sessions |
| `PI_PROVIDER` | Currently selected model provider |
| `PI_MODEL` | Currently selected model ID |
| `PI_REASONING_LEVEL` | Current effective reasoning level |

These are resolved when each command starts. Not injected into user `!` or `!!` commands.

Inspect current model/provider from within bash:

```bash
printf '%s/%s\n' "$PI_PROVIDER" "$PI_MODEL"
printf 'reasoning=%s session=%s\n' "$PI_REASONING_LEVEL" "$PI_SESSION_ID"
```

## Pi Process Configuration

| Variable | Description |
|----------|-------------|
| `PI_CODING_AGENT_DIR` | Override config directory; default `~/.pi/agent` |
| `PI_CODING_AGENT_SESSION_DIR` | Override session storage; overridden by `--session-dir` |
| `PI_PACKAGE_DIR` | Override package directory, useful for Nix/Guix store paths |
| `PI_OFFLINE` | Disable startup network operations (update checks, package updates, telemetry) |
| `PI_SKIP_VERSION_CHECK` | Disable the pi.dev latest-version request |
| `PI_TELEMETRY` | Override install/update telemetry: `1`/`true`/`yes` or `0`/`false`/`no` |
| `PI_CACHE_RETENTION` | Set to `long` for extended provider prompt caching where supported |
| `PI_SHARE_VIEWER_URL` | Override base URL used by `/share` |
| `PI_HARDWARE_CURSOR` | Set to `1` to show the hardware cursor |
| `PI_TUI_WRITE_LOG` | Capture raw ANSI stream (e.g., `PI_TUI_WRITE_LOG=/tmp/tui-ansi.log`) |
| `VISUAL`, `EDITOR` | External editor fallback when `externalEditor` is unset |
| `HTTP_PROXY`, `HTTPS_PROXY` | Proxy outbound HTTP requests |

Provider credentials (e.g., `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) are documented in [Providers](06-providers.md).
