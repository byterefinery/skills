# Usage — interactive mode, CLI, environment

## Interactive mode layout

Top to bottom:

- **Startup header** — shortcuts (`/hotkeys` for all), loaded AGENTS.md files, prompt templates, skills, extensions
- **Messages** — user messages, assistant responses, tool calls and results, notifications, errors, extension UI
- **Editor** — where you type; border color indicates thinking level
- **Footer** — working directory, session name, token/cache usage (`↑` input, `↓` output, `R` cache read, `W` cache write, `CH` cache hit rate), cost, context usage, current model

The editor can be temporarily replaced by built-in UI (`/settings`) or custom extension UI.

### Editor features

| Feature | How |
|---|---|
| File reference | Type `@` to fuzzy-search project files |
| Path completion | Tab |
| Multi-line | Shift+Enter (Ctrl+Enter on Windows Terminal) |
| External editor | Ctrl+G opens `externalEditor`, then `$VISUAL`, `$EDITOR`, Notepad on Windows, `nano` elsewhere |
| Clipboard | Ctrl+V pastes image or text (Alt+V on Windows); drag images into terminal |
| Shell command | `!command` runs and sends output to the model |
| Hidden shell command | `!!command` runs without sending output |

### Message queue (submit while agent works)

- **Enter** — queues a *steering* message, delivered after the current assistant turn finishes executing its tool calls
- **Alt+Enter** — queues a *follow-up* message, delivered only after the agent finishes all work
- **Escape** — aborts and restores queued messages to the editor
- **Alt+Up** — retrieves queued messages back to the editor

`steeringMode`/`followUpMode` settings: `"one-at-a-time"` (default) or `"all"`.

### Keyboard shortcuts (common)

| Key | Action |
|---|---|
| Ctrl+C | Clear editor; twice quits |
| Escape | Cancel/abort; twice opens `/tree` |
| Ctrl+L | Model selector |
| Ctrl+P / Shift+Ctrl+P | Cycle scoped models forward/back |
| Shift+Tab | Cycle thinking level |
| Ctrl+O | Collapse/expand tool output |
| Ctrl+T | Collapse/expand thinking blocks |
| Ctrl+X | Copy last assistant message (in `/tree`, copies selection) |

Customize in `~/.pi/agent/keybindings.json`; run `/reload` after editing. Key format `modifier+key` with `ctrl`, `shift`, `alt`, `super`.

## Slash commands

| Command | Description |
|---|---|
| `/login`, `/logout` | Manage provider credentials |
| `/llama` | Download, load, unload llama.cpp router models |
| `/model` | Switch models |
| `/scoped-models` | Enable/disable models for Ctrl+P cycling |
| `/settings` | Thinking level, theme, message delivery, transport, TUI mode |
| `/resume` | Pick from previous sessions |
| `/new` | Start a new session |
| `/name <name>` | Set session display name |
| `/session` | Show session file, ID, messages, tokens, cost |
| `/tree` | Jump to any point in the session and continue from there |
| `/trust` | Save project trust decision (restart required) |
| `/fork` | New session from a previous user message |
| `/clone` | Duplicate current active branch into a new session |
| `/compact [prompt]` | Manually compact context |
| `/copy` | Copy last assistant message |
| `/export [file]` | Export session to HTML or JSONL |
| `/import <file>` | Import and resume from JSONL |
| `/share` | Upload as private GitHub gist with shareable HTML link |
| `/reload` | Reload keybindings, extensions, skills, prompts, themes, context files |
| `/hotkeys`, `/changelog`, `/quit` | — |

Extensions register custom commands; skills appear as `/skill:name`; prompt templates as `/templatename`.

## CLI reference

```bash
pi [options] [--] [@files...] [messages...]
```

### Modes

| Flag | Description |
|---|---|
| (default) | Interactive |
| `-p`, `--print` | Print response and exit (reads piped stdin and merges into prompt) |
| `--mode json` | Output all events as JSON lines |
| `--mode rpc` | RPC mode over stdin/stdout |
| `--export <in> [out]` | Export session to HTML |

### Model options

| Option | Description |
|---|---|
| `--provider <name>` | e.g. `anthropic`, `openai`, `google` |
| `--model <pattern>` | Pattern or ID; supports `provider/id` and `:<thinking>` suffix |
| `--api-key <key>` | Overrides env vars |
| `--thinking <level>` | `off` `minimal` `low` `medium` `high` `xhigh` `max` |
| `--models <patterns>` | Comma-separated patterns for Ctrl+P cycling |
| `--list-models [search]` | List available models |

### Session options

`-c`/`--continue`, `-r`/`--resume`, `--session <path|id>`, `--fork <path|id>`, `--session-dir <dir>`, `--no-session` (ephemeral), `--name <name>`/`-n` (display name at startup).

### Tool options

| Option | Description |
|---|---|
| `--tools <list>`, `-t` | Strict allowlist across built-in, extension, custom tools |
| `--exclude-tools <list>`, `-xt` | Disable specific tools |
| `--no-builtin-tools`, `-nbt` | Disable built-ins, keep extension/custom tools |
| `--no-tools`, `-nt` | Disable all tools |

Built-in tools: `read`, `bash`, `powershell` (Windows), `edit`, `write`, `grep`, `find`, `ls`.

### Resource options

`-e`/`--extension <source>` (path, npm, or git; repeatable), `--no-extensions`, `--skill <path>` (repeatable), `--no-skills`, `--prompt-template <path>`, `--no-prompt-templates`, `--theme <path>`, `--no-themes`, `--no-context-files`/`-nc`. Combine `--no-*` with explicit flags to load exactly what you need: `pi --no-extensions -e ./my-ext.ts`.

### Other options

| Option | Description |
|---|---|
| `--system-prompt <text>` | Replace default prompt (context files and skills still appended) |
| `--append-system-prompt <text>` | Append to system prompt |
| `--tui-mode <mode>` | `regular` (default) or experimental `fullscreen` |
| `--use-theme <name[/name]>` | Initial theme for this run only; `light/dark` follows terminal |
| `--verbose` | Force verbose startup |
| `-a`, `--approve` / `-na`, `--no-approve` | Trust / ignore project-local files for this run |
| `--` | Stop option parsing; remaining args are prompts or `@file` inputs |
| `-h`, `-v` | Help / version |

### Package commands

```bash
pi install <source> [-l]      # npm:, git:, URL, or local path; -l = project-local
pi remove|uninstall <source> [-l]
pi update [source|self]       # pi only by default
pi update --all | --extensions | --models | --self [--force]
pi list
pi config                     # enable/disable package resources interactively
```

`pi config` and project package commands accept `--approve`/`--no-approve`; `pi update` never prompts.

### Examples

```bash
pi "List all .ts files in src/"            # interactive with initial prompt
pi -p -- "- Summarize these points"        # prompt starting with a dash
pi --name "release audit" -p "Audit repo"  # named one-shot session
pi --model openai/gpt-4o "Help me refactor"
pi --model sonnet:high "Solve this"
pi --tools read,grep,find,ls -p "Review the code"
pi --exclude-tools ask_question
```

## Environment variables

### Process configuration

| Variable | Description |
|---|---|
| `PI_CODING_AGENT_DIR` | Config dir override (default `~/.pi/agent`) |
| `PI_CODING_AGENT_SESSION_DIR` | Session storage override; precedence: `--session-dir` > this var > `sessionDir` setting |
| `PI_PACKAGE_DIR` | Package dir override (Nix/Guix store paths) |
| `PI_OFFLINE` | `1` disables all startup network operations (update checks, package checks, telemetry) |
| `PI_SKIP_VERSION_CHECK` | `1` disables the `pi.dev` latest-version request |
| `PI_TELEMETRY` | `1/true/yes` or `0/false/no` overrides install/update telemetry and provider attribution headers (does not disable update checks) |
| `PI_CACHE_RETENTION` | `long` extends prompt cache where supported (Anthropic 1h, OpenAI 24h) |
| `PI_SHARE_VIEWER_URL` | Base URL for `/share` |
| `PI_HARDWARE_CURSOR` | `1` shows the hardware cursor |
| `PI_TUI_ESC_TIMEOUT` | ms to wait after a lone ESC before treating it as Escape (default 100 over SSH, 10 otherwise) |
| `VISUAL`, `EDITOR`, `HTTP_PROXY`, `HTTPS_PROXY` | Standard |

Process markers set by the CLI/RPC entry points (inherited by children): `AI_AGENT=pi`, `PI_CODING_AGENT=true`.

### Shell tool session environment (LLM-run `bash`/`powershell` only)

| Variable | Description |
|---|---|
| `PI_SESSION_ID` | Current session ID |
| `PI_SESSION_FILE` | Absolute session JSONL path; unset for ephemeral sessions |
| `PI_PROVIDER` / `PI_MODEL` | Selected provider and model ID |
| `PI_REASONING_LEVEL` | Effective reasoning level |

Resolved at command start, so model/thinking changes apply to the next command. Custom tools from `createBashTool()`/`createPowerShellTool()` expose these by default; disable with `exposeSessionEnvironment: false` (inherited stale values are removed).

## Context files and system prompt

- `AGENTS.md` (or `CLAUDE.md`) loads from `~/.pi/agent/AGENTS.md`, parent directories walking up, and cwd. `AGENTS.override.md` in a directory replaces that directory's `AGENTS.md`/`CLAUDE.md`. Disable with `--no-context-files`.
- Replace the system prompt with `.pi/SYSTEM.md` (project) or `~/.pi/agent/SYSTEM.md` (global); `APPEND_SYSTEM.md` appends instead.

## Project trust

Interactive pi asks before trusting a folder with project-local settings/resources or `.agents/skills` and no saved decision in `~/.pi/agent/trust.json`. Before trust, only context files, user/global extensions, and CLI `-e` extensions load (so they can handle the `project_trust` event). Non-interactive modes follow `defaultProjectTrust` (`ask` default, `always`, `never`). `/trust` saves a decision for future sessions (current session is not reloaded).

## Telemetry and update checks

- **Update check** fetches `https://pi.dev/api/latest-version`; disable with `PI_SKIP_VERSION_CHECK=1`.
- **Install/update telemetry** pings `https://pi.dev/api/report-install` after first install or a changelog-detected update, and gates optional provider attribution headers; opt out with `enableInstallTelemetry: false` in settings or `PI_TELEMETRY=0`.
- `--offline` / `PI_OFFLINE=1` disables all startup network operations.

## Platform and container notes

- **Windows** — `powershell` tool replaces `bash`; Cygwin via `shellPath` in settings; see `docs/windows.md`.
- **Termux (Android)** — has dedicated AGENTS.md conventions (location, clipboard, notifications, sharing, device info); see `docs/termux.md`.
- **tmux** — recommended config enables `csi-u` so pi can map Alt/Mod keys correctly (`update-titles off`, `set -g mouse on`); see `docs/tmux.md`.
- **Terminals** — Kitty, iTerm2, Ghostty, WezTerm, VS Code, Windows Terminal each have setup notes (image protocols, fullscreen mode, key remaps); see `docs/terminal-setup.md`.
- **Containerization** — no built-in sandbox. Patterns: Gondolin extension (tools + `!` commands routed into a local Linux micro-VM, pi/auth stay on host), plain Docker (whole pi in a container), OpenShell (policy-controlled sandbox); see `docs/containerization.md`.
