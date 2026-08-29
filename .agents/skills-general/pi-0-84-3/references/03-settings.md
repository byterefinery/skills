# Settings reference

JSON settings files; project overrides global. Edit directly or via `/settings`.

| Location | Scope |
|---|---|
| `~/.pi/agent/settings.json` | Global (all projects) |
| `.pi/settings.json` | Project (overrides global) |

Nested objects are merged (project wins per-key). Path values in global settings resolve relative to `~/.pi/agent`; in project settings relative to `.pi`; absolute paths and `~` always work.

## Model & thinking

| Setting | Type | Default | Description |
|---|---|---|---|
| `defaultProvider` | string | - | e.g. `"anthropic"`, `"openai"` |
| `defaultModel` | string | - | Default model ID |
| `defaultThinkingLevel` | string | - | `off` `minimal` `low` `medium` `high` `xhigh` `max` |
| `hideThinkingBlock` | boolean | `false` | Hide thinking blocks in output |
| `showCacheMissNotices` | boolean | `false` | Notices for significant prompt-cache misses and compaction/branch-summary usage |
| `thinkingBudgets` | object | - | Token budgets per thinking level; used natively by Anthropic/Google/Bedrock, by OpenAI-compatible models when `compat.thinkingTokenBudgetField` is set |

## UI & display

| Setting | Type | Default | Description |
|---|---|---|---|
| `theme` | string | `"dark"` | `"dark"`, `"light"`, or custom |
| `externalEditor` | string | `$VISUAL` then `$EDITOR`, then Notepad/nano | Ctrl+G editor; e.g. `"code --wait"` for VS Code |
| `quietStartup` | boolean | `false` | Hide startup header |
| `defaultProjectTrust` | string | `"ask"` | `ask` / `always` / `never`; global only |
| `collapseChangelog` | boolean | `false` | Condensed changelog after updates |
| `enableInstallTelemetry` | boolean | `true` | Anonymous install/update ping (does not control update checks) |
| `enableAnalytics` | boolean | `false` | Opt-in analytics (experimental first-time setup only) |
| `doubleEscapeAction` | string | `"tree"` | `tree` / `fork` / `none` |
| `treeFilterMode` | string | `"default"` | `default` / `no-tools` / `user-only` / `labeled-only` / `all` |
| `editorPaddingX` | number | `0` | Editor horizontal padding 0-3 |
| `outputPad` | number | `1` | Horizontal padding for messages 0 or 1 |
| `autocompleteMaxVisible` | number | `5` | Autocomplete dropdown items 3-20 |
| `showHardwareCursor` | boolean | `false` | Terminal cursor for IME support |
| `tuiMode` | string | `"regular"` | `regular` or experimental `fullscreen`; `/settings` applies immediately, `--tui-mode` overrides at startup |
| `fullscreenExitOutput` | string | `"transcript"` | `transcript` prints final transcript; `resume-hint` restores previous screen with only the resume hint |
| `fullscreenScrollbar` | string | `"auto"` | `auto` / `always` / `hidden` |

## Telemetry, network, warnings

- `enableInstallTelemetry: false` or `PI_TELEMETRY=0` — opt out of install/update ping. Update checks remain unless `PI_SKIP_VERSION_CHECK=1`. `--offline`/`PI_OFFLINE=1` kills all startup network ops.
- `httpProxy` (global only) — applied as `HTTP_PROXY`/`HTTPS_PROXY`.
- `warnings.anthropicExtraUsage` (default `true`) — warn when Anthropic subscription auth may use paid extra usage.

## Compaction, branch summary, retry

```json
{
  "compaction": { "enabled": true, "reserveTokens": 16384, "keepRecentTokens": 20000 },
  "branchSummary": { "reserveTokens": 16384, "skipPrompt": false },
  "retry": {
    "enabled": true,
    "maxRetries": 3,
    "baseDelayMs": 2000,
    "provider": { "timeoutMs": 3600000, "maxRetries": 0, "maxRetryDelayMs": 60000 }
  }
}
```

- `retry.enabled` (default `true`), `maxRetries` (3), `baseDelayMs` (2000; exponential 2s/4s/8s)
- `retry.provider.timeoutMs` — SDK request timeout; `maxRetries` (0) — keep at 0 so out-of-usage-limit errors reach pi's recovery path; `maxRetryDelayMs` (60000) — fail fast if a provider requests a longer retry delay; `0` disables the limit

## Message delivery

| Setting | Default | Description |
|---|---|---|
| `steeringMode` | `"one-at-a-time"` | `all` or `one-at-a-time` |
| `followUpMode` | `"one-at-a-time"` | `all` or `one-at-a-time` |
| `transport` | `"auto"` | `sse` / `websocket` / `websocket-cached` / `auto` |
| `httpIdleTimeoutMs` | `300000` | HTTP idle timeout; `0` disables |
| `websocketConnectTimeoutMs` | `15000` | WS handshake timeout; `0` disables |

## Terminal, images, shell

| Setting | Default | Description |
|---|---|---|
| `terminal.showImages` | `true` | Show images if terminal supports |
| `terminal.imageWidthCells` | `60` | Preferred inline image width |
| `terminal.clearOnShrink` | `false` | Clear empty rows on shrink (can flicker) |
| `images.autoResize` | `true` | Resize images to 2000x2000 max (`@file`, `read`, tool images) |
| `images.blockImages` | `false` | Block all images from being sent to the LLM |
| `shellPath` | - | Custom shell (Cygwin etc.); supports leading `~`; Windows JSON paths need `/` or escaped `\` |
| `shellCommandPrefix` | - | Prefix for every bash command |
| `npmCommand` | - | argv for npm operations, e.g. `["mise", "exec", "node@20", "--", "npm"]`; when set, git packages install deps with plain `install` |

## Tools and sessions

| Setting | Default | Description |
|---|---|---|
| `defaultTools` | - (standard set) | Built-ins enabled at startup; empty array = none (extension/custom tools stay enabled). `--tools` is a strict allowlist that replaces this; project array replaces global |
| `sessionDir` | - | Session file directory; precedence `--session-dir` > `PI_CODING_AGENT_SESSION_DIR` > this |
| `enabledModels` | - | Patterns for Ctrl+P cycling, same format as `--models` |

## Markdown

`markdown.codeBlockIndent` (default `"  "`); `markdown.mermaid` — `"off"` / `"final"` / `"streaming"` (default).

## Resources

Arrays of files or directories; support glob patterns, `!pattern` exclusion, `+path` force-include, `-path` force-exclude.

| Setting | Loads |
|---|---|
| `packages` | npm/git packages; string form loads all resources, object form `{ "source": "...", "skills": [...], "extensions": [...] }` filters |
| `extensions` | Local extension files/dirs |
| `skills` | Local skill files/dirs (e.g. point at `~/.claude/skills` to reuse Claude Code skills) |
| `prompts` | Local prompt template files/dirs |
| `themes` | Local theme files/dirs |
| `enableSkillCommands` | `true` — register skills as `/skill:name` |

## Example

```json
{
  "defaultProvider": "anthropic",
  "defaultModel": "claude-sonnet-4-20250514",
  "defaultThinkingLevel": "medium",
  "theme": "dark",
  "compaction": { "enabled": true, "reserveTokens": 16384, "keepRecentTokens": 20000 },
  "retry": { "enabled": true, "maxRetries": 3 },
  "enabledModels": ["claude-*", "gpt-4o"],
  "warnings": { "anthropicExtraUsage": true },
  "packages": ["pi-skills"]
}
```
