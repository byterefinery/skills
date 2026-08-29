---
name: pi-0-84-3
description: Pi (pi-mono) 0.84.3 — minimal, self-extensible terminal coding agent and agent harness. Use when the user wants to install, configure, run, or extend the pi coding agent CLI (interactive, print, JSON, or RPC modes; sessions; extensions; skills; prompt templates; themes; pi packages), or when working with its monorepo packages — pi-ai, pi-agent-core, pi-tui, pi-client, pi-protocol, pi-server, pi-telemetry, the SQLite session backend, or pi evals.
license: MIT
compatibility: Requires Node.js 22.19+ (Bun also works for most packages); network access for npm install and provider APIs
metadata:
  tags:
    - agent-harness
    - coding-agent
    - cli
    - llm
    - typescript
    - monorepo
---

# pi 0.84.3

## Overview

Pi is a minimal terminal coding harness from the pi-mono monorepo (https://github.com/earendil-works/pi). It gives the model four built-in tools by default — `read`, `write`, `edit`, `bash` (plus read-only `grep`, `find`, `ls` available via tool options) — and stays small at the core by design. Everything else is added via TypeScript **extensions**, **skills**, **prompt templates**, **themes**, or shareable **pi packages**.

It runs in four modes:

- **Interactive** (default) — full TUI in the terminal
- **Print / JSON** — `pi -p "..."` prints a response and exits; `--mode json` streams all events as JSON lines
- **RPC** — `pi --mode rpc` speaks a JSONL protocol over stdin/stdout for non-Node integrations
- **SDK** — embed `AgentSession` from `@earendil-works/pi-coding-agent` in Node apps

Intentionally absent (build or install them instead): MCP, sub-agents, permission popups, plan mode, built-in to-dos, background bash. For sandboxing, containerize or run in tmux.

Key locations:

| Path | Purpose |
|---|---|
| `~/.pi/agent/` | Global config: `settings.json`, `auth.json`, `models.json`, `trust.json`, `keybindings.json` |
| `~/.pi/agent/sessions/` | Session JSONL files, organized by working directory |
| `.pi/` (project) | `settings.json`, `extensions/`, `skills/`, `prompts/`, `themes/`, `SYSTEM.md` — loaded only after project trust |
| `~/.pi/agent/{extensions,skills,prompts,themes}/` | Global resource dirs |
| `~/.agents/skills/`, `.agents/skills/` | Agent-Skills-standard dirs, also scanned |

Monorepo packages (all npm, MIT):

| npm package | Purpose |
|---|---|
| `@earendil-works/pi-coding-agent` | Interactive coding agent CLI + SDK (`pi` binary) |
| `@earendil-works/pi-ai` | Unified multi-provider LLM API (30+ providers), tool calling, cost tracking |
| `@earendil-works/pi-agent-core` | Stateful agent runtime: tool loop, events, steering, custom message types |
| `@earendil-works/pi-tui` | Terminal UI library with differential rendering and synchronized output |
| `@earendil-works/pi-client` | Transport-neutral client for remote pi sessions (length-prefixed CBOR) |
| `@earendil-works/pi-protocol` | Experimental wire protocol schemas, CBOR subset, framing |
| `@earendil-works/pi-server` | Experimental session server (Unix-socket preset) |
| `@earendil-works/pi-telemetry` | Vendor-neutral telemetry contracts and typed schemas |
| `@earendil-works/pi-session-backend-sqlite-node` | `node:sqlite` session repository + FTS search for agent-core |
| `@earendil-works/pi-evals` | Model-backed behavioral evals for pi workflows |

## Usage

### Install and authenticate

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
# or: curl -fsSL https://pi.dev/install.sh | sh
```

Then in a project directory:

```bash
pi                       # start interactive session
pi -p "Summarize this codebase"   # one-shot
pi -c                    # continue most recent session
pi -r                    # browse previous sessions
```

Authenticate with an API key (`export ANTHROPIC_API_KEY=...`) or `/login` inside pi for subscription providers (Claude Pro/Max, ChatGPT Plus/Pro Codex, GitHub Copilot) and key providers stored in `~/.pi/agent/auth.json`. Select models with `/model` or `--model provider/id:thinking`.

### Everyday patterns

```bash
pi @README.md "Explain this"                # @file attaches file content
cat err.log | pi -p "Diagnose this"         # stdin merges into prompt
pi --tools read,grep,find,ls -p "Review"    # read-only mode
pi --thinking high "Solve this"             # off|minimal|low|medium|high|xhigh|max
pi -e ./my-extension.ts "..."               # load one extension (temp for this run)
pi install git:github.com/user/repo@v1      # install a pi package
```

In the editor: `@` fuzzy-searches files, `!cmd` runs a shell command and sends output to the model, `!!cmd` runs without sending, Ctrl+G opens the external editor, Ctrl+V pastes images, Shift+Tab cycles thinking level, double-Escape opens `/tree`.

Slash commands (full list in [01-usage](references/01-usage.md)): `/model`, `/settings`, `/resume`, `/new`, `/tree`, `/fork`, `/clone`, `/compact`, `/name`, `/session`, `/export`, `/import`, `/share`, `/reload`, `/hotkeys`, `/login`, `/logout`, `/llama`, `/trust`, plus skills as `/skill:name` and prompt templates as `/templatename`.

### Extending pi

- **Extensions** — TypeScript modules (auto-loaded via jiti, no compile) in `~/.pi/agent/extensions/` or `.pi/extensions/`. Register tools, commands, shortcuts, CLI flags; intercept events like `tool_call` (can block), `context` (rewrite LLM messages), `before_agent_start` (inject prompt), `input`; custom UI via `ctx.ui`; custom providers via `pi.registerProvider()`. See [04-extensions](references/04-extensions.md).
- **Skills** — Agent Skills standard directories with `SKILL.md`, loaded from `~/.pi/agent/skills/`, `~/.agents/skills/`, `.pi/skills/`, `.agents/skills/`. See [05-customization](references/05-customization.md).
- **Prompt templates** — `~/.pi/agent/prompts/review.md` becomes `/review`, with `$1`, `$@`, `${1:-default}` argument substitution.
- **Themes** — JSON files with 51 color tokens; hot-reload when the active theme changes.
- **Pi packages** — bundle the above via `pi install npm:... | git:... | path`; manifest in `package.json` under `pi` key or conventional dirs.

### From source

```bash
git clone https://github.com/earendil-works/pi-mono && cd pi-mono
npm install --ignore-scripts && npm run build
./pi-test.sh          # run pi from sources, from any directory
./test.sh             # non-LLM tests
npm run check         # lint + format + type check
```

## Gotchas

- **Install with `--ignore-scripts`** — the docs always use it; pi does not need lifecycle scripts on normal npm installs.
- **`!cmd` vs `!!cmd`** — `!` sends output into the model context, `!!` does not. Mixing them up pollutes or starves context.
- **Project trust gates project resources** — `.pi/settings.json`, project extensions/skills, and project packages load only after the folder is trusted (`/trust` writes `~/.pi/agent/trust.json`; restart required to take effect). Non-interactive modes (`-p`, `--mode json`, `--mode rpc`) never prompt: without a saved decision they follow `defaultProjectTrust` (`ask` and `never` ignore project resources). Override one run with `-a`/`--approve` or `-na`/`--no-approve`. `pi update` never prompts.
- **RPC framing is LF-only** — split records on `\n` only; Node `readline` is not compliant because it also splits on U+2028/U+2029, which are valid inside JSON strings.
- **Extension factories must not start long-lived resources** — no processes, sockets, watchers, or timers in the factory (it can run without a session). Start them in `session_start`, close them in `session_shutdown` (reload/new/resume/fork all tear down and re-emit `session_start`).
- **`promptGuidelines` are appended flat** to the system prompt's Guidelines section with no tool-name prefix — each bullet must name the tool explicitly ("Use my_tool when…", never "Use this tool when…").
- **Use `StringEnum` from pi-ai** for string-enum tool parameters; `Type.Union` of literals breaks the Google API.
- **`auth.json` credentials beat environment variables.** The `key` field supports `$ENV_VAR` interpolation, `!command` execution (stdout cached per process), and literals — `$$` escapes a dollar, `$!` a bang. Plain uppercase strings are literals, not env lookups.
- **Skill discovery is location-dependent** — root-level `.md` files count as skills in `~/.pi/agent/skills/` and `.pi/skills/`, but are ignored in `~/.agents/skills/` and project `.agents/skills/` (nested `.md` in grouping folders still load). Pi, unlike the Agent Skills standard, allows a skill `name` to differ from its parent directory.
- **`PI_*` session variables are shell-tool-only** — `PI_SESSION_ID`, `PI_SESSION_FILE`, `PI_PROVIDER`, `PI_MODEL`, `PI_REASONING_LEVEL` are injected into LLM-run `bash`/`powershell` commands, not into user `!` commands. To report the running model, read them, don't infer from the prompt.
- **Themes require all 51 color tokens** (few optional with fallbacks). `--use-theme light/dark` follows terminal appearance for one run without saving the setting.
- **Compaction is lossy but reversible** — auto-compaction triggers at `contextTokens > contextWindow - reserveTokens` (default reserve 16384, keep recent 20000). Full history stays in the JSONL file; revisit with `/tree`. Tool results are truncated to 2000 chars when building summary input.
- **Keep `retry.provider.maxRetries` at 0** — nonzero can make provider-level retries swallow out-of-usage-limit errors before pi's recovery path sees them.
- **Pinned git package refs do not move** — `pi update --extensions/--all` reconcile clones to the pinned tag/commit but never advance the ref; reinstall with `pi install git:host/user/repo@new-ref` to move it. Git packages install deps with `npm install --omit=dev`, so runtime deps must be in `dependencies` (bundled pi core packages go in `peerDependencies` with `*` and are never bundled).
- **`pi -e <package source>` is a temp install** for the current run only (useful for trying packages without installing); auto-discovered extensions in `.pi/extensions` can be hot-reloaded with `/reload`.
- **Model shorthand** — `--model provider/id` and `--model id:thinking` (e.g., `sonnet:high`) work without `--provider`. Custom providers in `models.json` need `baseUrl` + `api` unless overriding a built-in provider.
- **Restart or `/reload` after context-file changes** — `AGENTS.md`/`CLAUDE.md` are read at startup; `AGENTS.override.md` in a directory replaces that directory's `AGENTS.md`/`CLAUDE.md`.
- **`pi` runs with the user's full permissions** — there is no built-in permission system. Containerize (Docker, Gondolin micro-VM extension, OpenShell) for boundaries; see containerization notes in [01-usage](references/01-usage.md).

## References

- [01-usage](references/01-usage.md) — Interactive mode, editor, slash commands, shortcuts, CLI reference, environment variables, platform notes
- [02-sessions-compaction](references/02-sessions-compaction.md) — Session storage, branching, `/tree`, fork/clone, compaction internals, session file format
- [03-settings](references/03-settings.md) — Complete `settings.json` reference (global and project), project trust, telemetry flags
- [04-extensions](references/04-extensions.md) — Extension API, event lifecycle, custom tools, custom providers, state persistence
- [05-customization](references/05-customization.md) — Skills, prompt templates, themes, pi packages (sources, manifests, dependencies, filtering)
- [06-providers-models](references/06-providers-models.md) — Provider auth, API keys, `models.json`, custom providers and OAuth, llama.cpp
- [07-sdk-rpc-json](references/07-sdk-rpc-json.md) — SDK (`createAgentSession`), RPC protocol, JSON event stream
- [08-monorepo-packages](references/08-monorepo-packages.md) — pi-ai, pi-agent-core, pi-tui, pi-client, pi-protocol, pi-server, pi-telemetry, SQLite backend, evals
- [09-examples](references/09-examples.md) — `examples/sdk` and `examples/extensions` catalog with setup instructions
