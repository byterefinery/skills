# settings.json

Pi uses JSON settings files with project settings overriding global settings. Nested objects are merged.

## Locations

| Location | Scope |
|----------|-------|
| `~/.pi/agent/settings.json` | Global (all projects) |
| `.pi/settings.json` | Project (current directory, overrides global) |

Edit directly or use `/settings` for common options.

## Model & Thinking

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `defaultProvider` | string | — | Default provider (e.g., `"anthropic"`, `"openai"`) |
| `defaultModel` | string | — | Default model ID |
| `defaultThinkingLevel` | string | — | `"off"`, `"minimal"`, `"low"`, `"medium"`, `"high"`, `"xhigh"`, `"max"` |
| `hideThinkingBlock` | boolean | `false` | Hide thinking blocks in output |
| `showCacheMissNotices` | boolean | `false` | Show transcript notices for significant prompt-cache misses |
| `thinkingBudgets` | object | — | Custom token budgets per thinking level |

```json
{
  "thinkingBudgets": {
    "minimal": 1024,
    "low": 4096,
    "medium": 10240,
    "high": 32768
  }
}
```

## UI & Display

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `theme` | string | `"dark"` | Theme name (`"dark"`, `"light"`, or custom) |
| `externalEditor` | string | `$VISUAL` → `$EDITOR` → Notepad/nano | Command for Ctrl+G external editor |
| `quietStartup` | boolean | `false` | Hide startup header |
| `defaultProjectTrust` | string | `"ask"` | Fallback project trust: `"ask"`, `"always"`, `"never"` (global only) |
| `collapseChangelog` | boolean | `false` | Show condensed changelog after updates |
| `enableInstallTelemetry` | boolean | `true` | Anonymous install/update version ping |
| `doubleEscapeAction` | string | `"tree"` | Action for double-escape: `"tree"`, `"fork"`, `"none"` |
| `treeFilterMode` | string | `"default"` | Default `/tree` filter: `"default"`, `"no-tools"`, `"user-only"`, `"labeled-only"`, `"all"` |
| `editorPaddingX` | number | `0` | Horizontal padding for input editor (0-3) |
| `outputPad` | number | `1` | Horizontal padding for messages (0 or 1) |
| `autocompleteMaxVisible` | number | `5` | Max visible items in autocomplete dropdown (3-20) |
| `showHardwareCursor` | boolean | `false` | Show terminal cursor for IME support |
| `tuiMode` | string | `"regular"` | TUI mode: `"regular"` or experimental `"fullscreen"` |
| `fullscreenScrollbar` | string | `"auto"` | Fullscreen scrollbar: `"auto"`, `"always"`, `"hidden"` |

```json
{
  "externalEditor": "code --wait"
}
```

## Network

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `httpProxy` | string | — | HTTP proxy URL (global only) |

```json
{ "httpProxy": "http://127.0.0.1:7890" }
```

## Warnings

```json
{
  "warnings": {
    "anthropicExtraUsage": false
  }
}
```

## Compaction

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `compaction.enabled` | boolean | `true` | Enable auto-compaction |
| `compaction.reserveTokens` | number | `16384` | Tokens reserved for LLM response |
| `compaction.keepRecentTokens` | number | `20000` | Recent tokens to keep (not summarized) |

```json
{
  "compaction": {
    "enabled": true,
    "reserveTokens": 16384,
    "keepRecentTokens": 20000
  }
}
```

## Branch Summary

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `branchSummary.reserveTokens` | number | `16384` | Tokens reserved for branch summarization |
| `branchSummary.skipPrompt` | boolean | `false` | Skip "Summarize branch?" prompt on `/tree` navigation |

## Retry

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `retry.enabled` | boolean | `true` | Enable automatic retry on transient errors |
| `retry.maxRetries` | number | `3` | Maximum agent-level retry attempts |
| `retry.baseDelayMs` | number | `2000` | Base delay for exponential backoff (2s, 4s, 8s) |
| `retry.provider.timeoutMs` | number | SDK default | Provider request timeout in milliseconds |
| `retry.provider.maxRetries` | number | `0` | Provider-level retry attempts |
| `retry.provider.maxRetryDelayMs` | number | `60000` | Max server-requested delay before failing (60s) |

Keep `retry.provider.maxRetries` at `0` unless explicitly needed. Setting it above `0` can block the agent until provider quota resets.

```json
{
  "retry": {
    "enabled": true,
    "maxRetries": 3,
    "baseDelayMs": 2000,
    "provider": {
      "timeoutMs": 3600000,
      "maxRetries": 0,
      "maxRetryDelayMs": 60000
    }
  }
}
```

## Message Delivery

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `steeringMode` | string | `"one-at-a-time"` | Steering messages: `"all"` or `"one-at-a-time"` |
| `followUpMode` | string | `"one-at-a-time"` | Follow-up messages: `"all"` or `"one-at-a-time"` |
| `transport` | string | `"auto"` | Preferred transport: `"sse"`, `"websocket"`, `"websocket-cached"`, `"auto"` |
| `httpIdleTimeoutMs` | number | `300000` | HTTP idle timeout in ms (0 to disable) |
| `websocketConnectTimeoutMs` | number | `15000` | WebSocket connect timeout in ms (0 to disable) |

## Terminal & Images

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `terminal.showImages` | boolean | `true` | Show images in terminal |
| `terminal.imageWidthCells` | number | `60` | Preferred inline image width in cells |
| `terminal.clearOnShrink` | boolean | `false` | Clear empty rows when content shrinks |
| `images.autoResize` | boolean | `true` | Resize images to 2000x2000 max |
| `images.blockImages` | boolean | `false` | Block all images from being sent to LLM |

## Shell

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `shellPath` | string | — | Custom shell path; supports leading `~` |
| `shellCommandPrefix` | string | — | Prefix for every bash command (e.g., `"shopt -s expand_aliases"`) |
| `npmCommand` | string[] | — | Command argv for npm operations |

```json
{
  "npmCommand": ["mise", "exec", "node@20", "--", "npm"]
}
```

## Sessions

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `sessionDir` | string | — | Session storage directory (absolute, relative, or `~`) |

```json
{ "sessionDir": ".pi/sessions" }
```

Precedence: `--session-dir` > `PI_CODING_AGENT_SESSION_DIR` > `sessionDir`.

## Model Cycling

```json
{
  "enabledModels": ["claude-*", "gpt-4o", "gemini-2*"]
}
```

Same format as `--models` CLI flag. Controls Ctrl+P cycling scope.

## Markdown

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `markdown.codeBlockIndent` | string | `"  "` | Indentation for code blocks |
| `markdown.mermaid` | string | `"streaming"` | Mermaid rendering: `"off"`, `"final"`, `"streaming"` |

## Resources

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `packages` | array | `[]` | npm/git packages to load resources from |
| `extensions` | string[] | `[]` | Local extension file paths or directories |
| `skills` | string[] | `[]` | Local skill file paths or directories |
| `prompts` | string[] | `[]` | Local prompt template paths or directories |
| `themes` | string[] | `[]` | Local theme file paths or directories |
| `enableSkillCommands` | boolean | `true` | Register skills as `/skill:name` commands |

Paths in global settings resolve relative to `~/.pi/agent`. Paths in project settings resolve relative to `.pi`. Arrays support glob patterns, `!pattern` exclusions, `+path` force-include, and `-path` force-exclude.

### packages

String form loads all resources:

```json
{ "packages": ["pi-skills", "@org/my-extension"] }
```

Object form filters which resources:

```json
{
  "packages": [
    {
      "source": "pi-skills",
      "skills": ["brave-search", "transcribe"],
      "extensions": []
    }
  ]
}
```

## Example

```json
{
  "defaultProvider": "anthropic",
  "defaultModel": "claude-sonnet-4-20250514",
  "defaultThinkingLevel": "medium",
  "theme": "dark",
  "compaction": {
    "enabled": true,
    "reserveTokens": 16384,
    "keepRecentTokens": 20000
  },
  "retry": {
    "enabled": true,
    "maxRetries": 3
  },
  "enabledModels": ["claude-*", "gpt-4o"],
  "warnings": {
    "anthropicExtraUsage": true
  },
  "packages": ["pi-skills"]
}
```

## Project Overrides

Project settings (`.pi/settings.json`) override global settings. Nested objects merge:

```json
// ~/.pi/agent/settings.json (global)
{
  "theme": "dark",
  "compaction": { "enabled": true, "reserveTokens": 16384 }
}

// .pi/settings.json (project)
{
  "compaction": { "reserveTokens": 8192 }
}

// Result
{
  "theme": "dark",
  "compaction": { "enabled": true, "reserveTokens": 8192 }
}
```
