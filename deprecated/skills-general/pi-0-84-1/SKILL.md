---
name: pi-0-84-1
description: Pi coding agent CLI usage, interactive mode, commands, sessions, tools, packages, and configuration. Use when working with the pi terminal coding agent — running commands, managing sessions, configuring providers, installing packages, or customizing behavior.
license: MIT
compatibility: Requires pi 0.84.1+ installed globally
metadata:
  tags:
    - cli
    - coding-agent
    - terminal
---

# pi 0.84.1

## Overview

Pi is a minimal terminal coding harness that runs in four modes: interactive, print, JSON event stream, and RPC. It ships with four built-in tools (`read`, `write`, `edit`, `bash`) and four read-only tools off by default (`grep`, `find`, `ls`). Extend it with skills, extensions, prompt templates, themes, and pi packages.

## Usage

### Installation

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
# or
curl -fsSL https://pi.dev/install.sh | sh
```

### Basic Modes

```bash
pi                              # Interactive mode
pi "List .ts files in src/"     # Interactive with initial prompt
pi -p "Summarize this codebase" # Print mode (non-interactive, exits after response)
pi --mode json "List files"     # JSON event stream to stdout
pi --mode rpc                   # RPC mode over stdin/stdout
```

Piped stdin merges into the initial prompt in print mode:

```bash
cat README.md | pi -p "Summarize this text"
```

### Model Selection

```bash
pi --provider openai --model gpt-4o "Help me refactor"
pi --model openai/gpt-4o "Help me refactor"          # provider prefix (no --provider needed)
pi --model sonnet:high "Solve this complex problem"   # thinking level shorthand
pi --thinking high "Solve this complex problem"       # explicit thinking level
pi --models "claude-*,gpt-4o"                         # limit Ctrl+P cycling
pi --list-models                                      # list available models
pi --list-models sonnet                               # fuzzy search models
```

Thinking levels: `off`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`.

### File Attachments

Prefix files with `@` to include in the initial message:

```bash
pi @prompt.md "Answer this"
pi -p @screenshot.png "What's in this image?"
pi @code.ts @test.ts "Review these files"
```

### Tool Control

```bash
pi --tools read,grep,find,ls -p "Review the code"     # read-only mode
pi --exclude-tools ask_question                        # disable specific tool
pi --no-tools                                          # disable all tools
pi --no-builtin-tools                                  # disable built-in, keep extension tools
```

### Authentication

Set an environment variable or use `/login` in interactive mode:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
pi
```

Subscription providers (Anthropic Claude Pro/Max, OpenAI ChatGPT Plus/Pro, GitHub Copilot) support OAuth via `/login`.

Print credentials for external clients:

```bash
pi auth print-api-key --provider openai
pi auth print-bearer-token --provider openai-codex
```

### Interactive Mode Commands

Type `/` in the editor to trigger commands:

| Command | Description |
|---------|-------------|
| `/login`, `/logout` | Manage provider credentials |
| `/model` | Switch models |
| `/scoped-models` | Enable/disable models for Ctrl+P cycling |
| `/settings` | Thinking level, theme, message delivery, transport |
| `/resume` | Pick from previous sessions |
| `/new` | Start a new session |
| `/name <name>` | Set session display name |
| `/session` | Show session info (file, ID, messages, tokens, cost) |
| `/tree` | Jump to any point in the session and continue from there |
| `/fork` | Create a new session from a previous user message |
| `/clone` | Duplicate the current active branch into a new session |
| `/compact [prompt]` | Manually compact context |
| `/copy` | Copy last assistant message to clipboard |
| `/export [file]` | Export session to HTML or JSONL |
| `/import <file>` | Import and resume a session from JSONL |
| `/share` | Upload as private GitHub gist with shareable HTML link |
| `/reload` | Reload keybindings, extensions, skills, prompts, themes, context files |
| `/trust` | Save project trust decision for future sessions |
| `/hotkeys` | Show all keyboard shortcuts |
| `/changelog` | Display version history |
| `/quit` | Quit pi |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+C | Clear editor (first) / Quit (second) |
| Escape | Cancel/abort |
| Escape twice | Open `/tree` |
| Ctrl+L | Open model selector |
| Ctrl+P / Shift+Ctrl+P | Cycle scoped models forward/backward |
| Shift+Tab | Cycle thinking level |
| Ctrl+O | Collapse/expand tool output |
| Ctrl+T | Collapse/expand thinking blocks |
| Ctrl+X | Copy the last assistant message |
| Ctrl+G | Open external editor |
| Ctrl+V | Paste image or text (Alt+V on Windows) |

Use `@` to fuzzy-search project files, `!command` to run bash and send output to LLM, `!!command` to run without sending.

### Message Queue

Submit messages while the agent is working:

- **Enter** — queues a *steering* message (delivered after current assistant turn finishes tool calls)
- **Alt+Enter** — queues a *follow-up* message (delivered only after agent finishes all work)
- **Escape** — aborts and restores queued messages to editor
- **Alt+Up** — retrieves queued messages back to editor

Configure delivery with `steeringMode` and `followUpMode` in settings: `"one-at-a-time"` (default) or `"all"`.

### Sessions

```bash
pi -c                          # Continue most recent session
pi -r                          # Browse and select from past sessions
pi --session <path|id>         # Use specific session file or partial UUID
pi --fork <path|id>            # Fork specific session into a new session
pi --name "my task"            # Set session display name
pi --no-session                # Ephemeral mode (don't save)
pi --session-dir <dir>         # Custom session storage directory
pi --export session.jsonl      # Export session to HTML
```

Sessions are JSONL files with tree structure (`id`/`parentId`), enabling in-place branching. Use `/tree` to navigate branches, `/fork` to create new sessions from previous messages, `/clone` to duplicate the active branch.

### Packages

```bash
pi install npm:@foo/pi-tools          # Install npm package
pi install npm:@foo/pi-tools@1.2.3    # Pinned version
pi install git:github.com/user/repo   # Install git repo
pi install git:github.com/user/repo@v1 # Pinned tag
pi install -l npm:@foo/bar            # Project-local install
pi remove npm:@foo/pi-tools           # Remove package
pi list                               # List installed packages
pi config                             # Enable/disable package resources (TUI)
```

Update:

```bash
pi update            # Update pi only
pi update --all      # Update pi and packages
pi update --extensions  # Update packages only
pi update --models     # Refresh model catalogs only
pi update --self --force  # Reinstall even if current
pi update npm:@foo/bar    # Update one package
```

Packages install to `~/.pi/agent/npm/` or `~/.pi/agent/git/`. Use `-l` for project-local (`.pi/npm/`, `.pi/git/`).

### Context Files

Pi loads `AGENTS.md` (or `CLAUDE.md`) from:
- `~/.pi/agent/AGENTS.md` (global)
- Parent directories walking up from cwd
- Current directory

If `AGENTS.override.md` exists in a directory, it replaces `AGENTS.md`/`CLAUDE.md` from that directory only.

Replace the system prompt with `.pi/SYSTEM.md` (project) or `~/.pi/agent/SYSTEM.md` (global). Append without replacing via `APPEND_SYSTEM.md`.

### Resource Discovery

| Resource | Global | Project |
|----------|--------|---------|
| Extensions | `~/.pi/agent/extensions/` | `.pi/extensions/` |
| Skills | `~/.pi/agent/skills/`, `~/.agents/skills/` | `.pi/skills/`, `.agents/skills/` (cwd up to repo root) |
| Prompt Templates | `~/.pi/agent/prompts/` | `.pi/prompts/` |
| Themes | `~/.pi/agent/themes/` | `.pi/themes/` |

Disable discovery with `--no-extensions`, `--no-skills`, `--no-prompt-templates`, `--no-themes`, `--no-context-files`.

### CLI Flags

```bash
pi --extension ./my-ext.ts           # Load extension
pi --skill ./my-skill/SKILL.md       # Load skill
pi --prompt-template ./review.md     # Load prompt template
pi --theme ./my-theme.json           # Load theme
pi --system-prompt "Custom prompt"   # Replace default prompt
pi --append-system-prompt "Extra"    # Append to system prompt
pi --api-key <key>                   # Inline API key
pi --verbose                         # Force verbose startup
pi --offline                         # Disable startup network operations
pi --tui-mode fullscreen             # Experimental fullscreen TUI
pi --approve / --no-approve          # Trust/ignore project-local files
```

## Gotchas

- **`--ignore-scripts` with npm install** — pi does not require install scripts; always use `--ignore-scripts` to avoid dependency lifecycle scripts.
- **Project trust** — pi asks before trusting project-local settings, extensions, and skills. In non-interactive modes, `defaultProjectTrust` in global settings controls fallback (`ask`, `always`, `never`). Use `--approve`/`--no-approve` to override for one run.
- **Print mode reads piped stdin** — `cat file | pi -p "prompt"` merges stdin into the initial prompt automatically.
- **`--no-*` flags combine with explicit flags** — e.g., `--no-extensions -e ./my-ext.ts` loads only that extension, ignoring settings.json.
- **Model pattern syntax** — `--model` supports `provider/id` and optional `:<thinking>` (e.g., `sonnet:high`). `--models` takes comma-separated patterns with glob support (`anthropic/*`, `*sonnet*`).
- **Steering vs follow-up messages** — steering delivers after current turn's tool calls; follow-up delivers only when the agent fully stops. During streaming in RPC/print modes, you must specify `streamingBehavior`.
- **Compaction is lossy** — the full history stays in the JSONL file; use `/tree` to revisit pre-compaction content.
- **`/tree` double-escape** — pressing Escape twice opens `/tree` by default. Configure `doubleEscapeAction` to `"tree"`, `"fork"`, or `"none"`.
- **`pi update` never prompts for project trust** — unlike other commands, `pi update` skips the trust prompt entirely.
- **Shell commands in `models.json`** — `"!command"` prefixed values execute at request time with no built-in caching or TTL. Wrap slow/expensive commands in your own caching script.
- **`enabledModels` in settings** — same format as `--models` CLI flag; controls Ctrl+P cycling scope.
- **`npmCommand` in settings** — used for all npm package operations. When configured, git package dependency installs use plain `install` to avoid npm-specific flags in wrappers.

## References

- [01-rpc-mode](references/01-rpc-mode.md) — RPC mode protocol, commands, events, extension UI
- [02-sdk](references/02-sdk.md) — TypeScript SDK, `createAgentSession`, `AgentSessionRuntime`, run modes
- [03-json-mode](references/03-json-mode.md) — JSON event stream mode, event types, output format
- [04-settings](references/04-settings.md) — settings.json structure, all fields, project overrides
- [05-models](references/05-models.md) — models.json structure, custom providers, model configuration
- [06-environment-variables](references/06-environment-variables.md) — process, bash tool, and provider environment variables
