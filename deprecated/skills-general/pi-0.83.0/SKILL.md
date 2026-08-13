---
name: pi
description: Pi coding agent v0.83.0 — interactive terminal coding harness with extensions, skills, prompt templates, themes, and pi packages. Use for questions about pi's CLI, interactive mode, sessions, settings, keybindings, providers, models, authentication, tools, context files, compaction, RPC/JSON modes, SDK, extensions, TUI components, packages, containerization, and platform setup.
license: MIT
compatibility: Requires Node.js 20+; pi installed via npm or standalone binary
metadata:
  tags:
    - coding-agent
    - cli
    - tui
    - ai
    - llm
    - terminal
---

# pi

Pi is a minimal terminal coding harness. It stays small at the core and extends through TypeScript extensions, skills, prompt templates, themes, and pi packages.

## Overview

Pi provides an interactive terminal interface for AI-assisted coding. The agent runs with four default tools — `read`, `write`, `edit`, `bash` — plus optional read-only tools (`grep`, `find`, `ls`). It supports multiple providers through OAuth subscriptions (`/login`) or API keys, manages conversations as tree-structured sessions with branching and compaction, and exposes SDK, RPC, and JSON event modes for programmatic integration.

## Installation

Install globally via npm:

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
```

Or use the installer on Linux/macOS:

```bash
curl -fsSL https://pi.dev/install.sh | sh
```

Uninstall: `npm uninstall -g @earendil-works/pi-coding-agent` (works for both npm and curl installs).

## Authentication

Subscription login — start pi and run `/login`, then select a provider. Built-in subscriptions include Claude Pro/Max, ChatGPT Plus/Pro (Codex), GitHub Copilot, xAI (Grok), OpenRouter, and Radius.

API key — set an environment variable before launching:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
pi
```

Or use `/login` to store the key in `~/.pi/agent/auth.json`. Auth file credentials take priority over environment variables.

## Interactive Mode

Start pi in a project directory:

```bash
cd /path/to/project
pi
```

The interface has four areas: startup header (shortcuts, context files, skills, extensions), messages (user, assistant, tool calls, results, notifications), editor (input area with thinking-level border color), and footer (cwd, session name, token/cache usage, cost, context usage, model).

### Editor Features

- Type `@` to fuzzy-search project files
- Tab for path completion
- Shift+Enter for multi-line input (Ctrl+Enter on Windows Terminal)
- Ctrl+X copies the last assistant message
- Ctrl+V (Alt+V on Windows) pastes images; drag images into supported terminals
- `!command` runs a shell command and sends output to the model
- `!!command` runs without adding output to model context
- Ctrl+G opens external editor (`$VISUAL`, `$EDITOR`, Notepad, or `nano`)

### Message Queue

Submit messages while the agent is working:

- Enter queues a steering message (delivered after current turn's tool calls)
- Alt+Enter queues a follow-up (delivered after the agent finishes all work)
- Escape aborts and restores queued messages to the editor
- Alt+Up retrieves queued messages back to the editor

### Slash Commands

Type `/` for command completion. Extensions register custom commands, skills appear as `/skill:name`, and prompt templates expand via `/templatename`.

Key commands: `/login`, `/logout`, `/model`, `/settings`, `/resume`, `/new`, `/tree`, `/fork`, `/clone`, `/compact`, `/copy`, `/export`, `/import`, `/share`, `/reload`, `/hotkeys`, `/quit`.

## Sessions

Sessions auto-save to `~/.pi/agent/sessions/`, organized by working directory. Each session is a JSONL file with a tree structure enabling in-place branching.

```bash
pi -c                  # Continue most recent session
pi -r                  # Browse and select from past sessions
pi --no-session        # Ephemeral mode; do not save
pi --name "my task"    # Set session display name
pi --session <path|id> # Open a specific session
pi --fork <path|id>    # Fork a session into a new file
```

Session commands: `/resume`, `/new`, `/name <name>`, `/session`, `/tree` (navigate session tree), `/fork` (create new session from earlier prompt), `/clone` (duplicate active branch), `/compact` (summarize older context), `/export [file]` (HTML export), `/share` (private GitHub gist).

## Context Files

Pi loads `AGENTS.md` or `CLAUDE.md` at startup from:

- `~/.pi/agent/AGENTS.md` for global instructions
- Parent directories, walking up from cwd
- The current directory

Disable with `--no-context-files` or `-nc`. Restart pi or run `/reload` after changing context files.

System prompt files replace or append to the default prompt: `.pi/SYSTEM.md` (project) or `~/.pi/agent/SYSTEM.md` (global) for replacement; `APPEND_SYSTEM.md` in either location to append.

## Settings

JSON settings files with project settings overriding global settings:

- `~/.pi/agent/settings.json` — global (all projects)
- `.pi/settings.json` — project (current directory)

Edit directly or use `/settings` for common options. Nested objects merge: project settings override individual keys without replacing the whole object.

Key settings: `defaultProvider`, `defaultModel`, `defaultThinkingLevel`, `theme`, `compaction`, `retry`, `enabledModels`, `packages`, `externalEditor`, `shellCommandPrefix`.

## Tools

Built-in tools: `read`, `bash`, `edit`, `write`, `grep`, `find`, `ls`. Default: `read`, `bash`, `edit`, `write`.

```bash
pi --tools read,grep,find,ls -p "Review the code"    # Read-only mode
pi --exclude-tools ask_question                       # Disable one tool
pi --no-builtin-tools                                 # Disable built-ins, keep extension tools
pi --no-tools                                         # Disable all tools
```

## CLI Reference

```bash
pi [options] [@files...] [messages...]
```

Modes: default (interactive), `-p`/`--print` (one-shot), `--mode json` (JSON events), `--mode rpc` (JSON-RPC subprocess integration).

Model options: `--provider <name>`, `--model <pattern>` (supports `provider/id` and `:<thinking>`), `--api-key <key>`, `--thinking <level>`, `--models <patterns>`, `--list-models [search]`.

File arguments: prefix with `@` to include in the message. `pi @README.md "Summarize this"`.

Resource options: `-e`/`--extension <source>`, `--skill <path>`, `--prompt-template <path>`, `--theme <path>`. Combine `--no-*` flags with explicit flags for exact control.

## Keybindings

All shortcuts customizable via `~/.pi/agent/keybindings.json`. Run `/reload` after editing.

Key shortcuts: Ctrl+L (model selector), Ctrl+P/Shift+Ctrl+P (cycle models), Shift+Tab (cycle thinking level), Ctrl+O (expand/collapse tool output), Ctrl+X (copy message), Ctrl+G (external editor), Escape (abort), Ctrl+C (clear editor), Ctrl+D (exit when editor empty).

## Design Principles

Pi keeps the core small. It intentionally does not include built-in MCP, sub-agents, permission popups, plan mode, to-dos, or background bash. Build or install those workflows as extensions or packages. Use external tools such as containers and tmux for isolation.

## Gotchas

- `--ignore-scripts` is recommended for npm installs — pi does not require install lifecycle scripts
- On Windows, pi needs a bash shell (Git Bash, Cygwin, MSYS2, or WSL). Configure `shellPath` in settings if needed
- In tmux, add `set -g extended-keys on` and `set -g extended-keys-format csi-u` to `~/.tmux.conf` for reliable modifier key detection
- Windows Terminal binds Alt+Enter to fullscreen by default — remap it in settings.json `actions` to use pi's follow-up queueing
- Project trust controls loading of `.pi/settings.json`, `.pi` resources, and project `.agents/skills`. Use `/trust` to save a decision or `--approve`/`--no-approve` for one-run override
- Extensions run with full system permissions — only install from trusted sources
- Skills can instruct the model to perform any action — review skill content before use
- `pi update` never prompts for project trust; use `--approve` for one-run trust
- Non-interactive modes (`-p`, `--mode json`, `--mode rpc`) do not show trust prompts; they use `defaultProjectTrust` from settings
- `pi --list-models` lists available models without starting a session
- `/reload` hot-reloads extensions in auto-discovered locations (`~/.pi/agent/extensions/` or `.pi/extensions/`); use `-e` flag only for quick tests
- The `edit` tool returns `details.diff` for TUI display and `details.patch` as a standard unified patch for SDK consumers
- Context files (`AGENTS.md`, `CLAUDE.md`) are loaded regardless of project trust unless context loading is disabled
- `retry.provider.maxRetries` should stay at `0` — provider-level retries can mask out-of-usage-limit errors
- `PI_OFFLINE=1` disables all startup network operations including update checks and telemetry
- `PI_CODING_AGENT=true` is set in the environment so child processes can detect they run inside pi

## References

- [01-extensions](references/01-extensions.md) — TypeScript modules for tools, commands, events, custom UI
- [02-skills](references/02-skills.md) — Agent Skills standard, locations, commands, structure, frontmatter
- [03-prompt-templates](references/03-prompt-templates.md) — Reusable prompts that expand from slash commands
- [04-themes](references/04-themes.md) — Terminal color themes, format, color tokens, creating custom themes
- [05-packages](references/05-packages.md) — Pi packages, npm/git sources, install, filtering, dependencies
- [06-providers](references/06-providers.md) — Subscription and API-key providers, auth file, cloud providers, custom providers
- [07-models](references/07-models.md) — Custom models via models.json, provider config, compatibility overrides
- [08-sdk](references/08-sdk.md) — Embed pi in Node.js applications, AgentSession, events, session management
- [09-rpc](references/09-rpc.md) — JSON-RPC mode over stdin/stdout, commands, events, extension UI protocol
- [10-tui](references/10-tui.md) — TUI components for extensions, overlays, keyboard input, theming, patterns
- [11-compaction](references/11-compaction.md) — Context compaction and branch summarization mechanics
- [12-session-format](references/12-session-format.md) — JSONL session file format, entry types, SessionManager API
- [13-environment-variables](references/13-environment-variables.md) — Pi process config, bash tool session environment
- [14-security](references/14-security.md) — Project trust, containerization, Gondolin, Docker, OpenShell
- [15-platforms](references/15-platforms.md) — Windows, Termux on Android, tmux, terminal setup, shell aliases
- [16-llama-cpp](references/16-llama-cpp.md) — llama.cpp router server, model management, Hugging Face downloads
- [17-json-mode](references/17-json-mode.md) — JSON event stream output, event types, integration examples
