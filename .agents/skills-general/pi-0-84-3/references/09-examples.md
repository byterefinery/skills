# Examples catalog

Repo paths under `packages/coding-agent/examples/`. Try an extension without installing: `pi -e <path>` (temporary for the run); copy to an extensions dir for auto-discovery and `/reload`.

## SDK examples (`examples/sdk/`)

Run with `npx tsx examples/sdk/01-minimal.ts` from `packages/coding-agent/`.

| File | Shows |
|---|---|
| `01-minimal.ts` | Simplest usage, all defaults |
| `02-custom-model.ts` | Select model and thinking level |
| `03-custom-prompt.ts` | Replace or modify system prompt |
| `04-skills.ts` | Discover, filter, or replace skills |
| `05-tools.ts` | Built-in tool allowlists |
| `06-extensions.ts` | Logging, blocking, result modification |
| `07-context-files.ts` | AGENTS.md context files |
| `08-prompt-templates.ts` | File-based slash commands |
| `09-api-keys-and-oauth.ts` | API key resolution, OAuth config |
| `10-settings.ts` | Override compaction, retry, terminal settings |
| `11-sessions.ts` | In-memory, persistent, continue, list sessions |
| `12-full-control.ts` | Replace everything, no discovery |
| `13-session-runtime.ts` | Runtime-backed session replacement (`createAgentSessionRuntime`) |

## Extension examples (`examples/extensions/`)

### Lifecycle & safety

| Example | What it shows |
|---|---|
| `permission-gate.ts` | Confirm before dangerous bash (rm -rf, sudo, ...) |
| `project-trust.ts` | `project_trust` event (user/global + CLI extensions) |
| `protected-paths.ts` | Block writes to `.env`, `.git/`, `node_modules/` |
| `confirm-destructive.ts` | Confirm before destructive session actions |
| `dirty-repo-guard.ts` | Prevent session changes with uncommitted git changes |
| `sandbox/` | OS-level sandboxing via `@anthropic-ai/sandbox-runtime`, per-project config |
| `gondolin/` | Route built-in tools + `!` commands into a Gondolin micro-VM |

### Custom tools

| Example | What it shows |
|---|---|
| `todo.ts` | Todo tool + `/todos` with custom rendering and persisted state |
| `hello.ts` | Minimal custom tool |
| `question.ts` | `ctx.ui.select()` for user questions |
| `questionnaire.ts` | Multi-question input with tab navigation |
| `tool-override.ts` | Override built-in tools (logging/access control on `read`) |
| `dynamic-tools.ts` | Register tools post-startup and at runtime; prompt snippets + guidelines |
| `kimi-deferred-tools.ts` | Progressive tool activation (Kimi deferred-tool protocol) |
| `structured-output.ts` | Final structured-output tool returning `terminate: true` |
| `built-in-tool-renderer.ts` | Compact custom rendering for built-in tools |
| `minimal-mode.ts` | Minimal tool display (calls only, collapsed output) |
| `truncated-tool.ts` | Wrap ripgrep with 50KB/2000-line output truncation |
| `ssh.ts` | Delegate all tools to a remote machine via SSH |
| `subagent/` | Subagents with isolated context windows (below) |

### Commands & UI

| Example | What it shows |
|---|---|
| `preset.ts` | Named presets (model/thinking/tools/instructions) via `--preset` flag + `/preset` |
| `plan-mode/` | Claude Code-style read-only plan mode, `/plan` + step tracking |
| `tools.ts` | Interactive `/tools` enable/disable with session persistence |
| `handoff.ts` | Transfer context to a new focused session via `/handoff <goal>` |
| `qna.ts` | Extract questions from last response into editor |
| `status-line.ts`, `custom-footer.ts`, `custom-header.ts` | `ctx.ui.setStatus/setFooter/setHeader` |
| `github-issue-autocomplete.ts` | `#1234` issue autocomplete stacked onto built-in provider |
| `widget-placement.ts` | Widgets above/below editor |
| `hidden-thinking-label.ts`, `working-indicator.ts` | Customize collapsed thinking label / streaming indicator |
| `model-status.ts` | Model changes in status bar via `model_select` hook |
| `snake.ts`, `tic-tac-toe.ts` | Games while waiting (sequential execution mode for shared state) |
| `doom-overlay/` | DOOM as a 35 FPS overlay |
| `send-user-message.ts` | `pi.sendUserMessage()` |
| `timed-confirm.ts` | AbortSignal auto-dismiss for confirm/select dialogs |
| `rpc-demo.ts` (+ `examples/rpc-extension-ui.ts`) | Every RPC-supported extension UI method |
| `modal-editor.ts`, `rainbow-editor.ts` | Custom editors via `ctx.ui.setEditorComponent()` |
| `notify.ts` | Desktop notifications (OSC 777) when agent finishes |
| `titlebar-spinner.ts` | Braille spinner in terminal title |
| `summarize.ts` | Summarize conversation with a different model in transient UI |
| `overlay-test.ts`, `overlay-qa-tests.ts` | Overlay compositing: anchors, margins, stacking, overflow, animation |
| `shutdown-command.ts` | `ctx.shutdown()` |
| `reload-runtime.ts` | Safe reload flow (`/reload-runtime`) |
| `interactive-shell.ts` | Full-terminal interactive commands (vim, htop) via `user_bash` |
| `inline-bash.ts` | Expand `!{command}` patterns in prompts via `input` transform |
| `input-transform-streaming.ts` | Skip expensive input preprocessing for mid-stream steering |

### Git integration

| Example | What it shows |
|---|---|
| `git-checkpoint.ts` | Git stash checkpoint each turn; restore on branch |
| `auto-commit-on-exit.ts` | Auto-commit on exit using last assistant message |
| `git-merge-and-resolve.ts` | Git merge/resolve workflow |

### System prompt & compaction

| Example | What it shows |
|---|---|
| `pirate.ts` | `systemPromptAppend` dynamic modification |
| `claude-rules.ts` | Scan `.claude/rules/` and list rules in system prompt |
| `custom-compaction.ts` | Custom compaction with a different model |
| `trigger-compact.ts` | Compaction at 100k tokens + `/trigger-compact` |
| `prompt-customizer.ts` | System prompt customization |
| `provider-payload.ts` | Inspect/modify provider payloads |

### System integration, resources, messages

| Example | What it shows |
|---|---|
| `mac-system-theme.ts` | Sync pi theme with macOS dark/light mode |
| `dynamic-resources/` | Load skills/prompts/themes via `resources_discover` |
| `message-renderer.ts` | `registerMessageRenderer` (colors, expandable details) |
| `entry-renderer.ts` | TUI-only entries via `appendEntry` + `registerEntryRenderer` |
| `event-bus.ts` | Inter-extension communication via `pi.events` |
| `session-name.ts`, `bookmark.ts` | `setSessionName`, `setLabel` for `/tree` |
| `file-trigger.ts` | Watch a trigger file, inject contents into conversation |
| `bash-spawn-hook.ts` | Custom bash tool spawn hooks |

### Custom providers

| Example | What it shows |
|---|---|
| `custom-provider-anthropic/` | Custom Anthropic provider: OAuth + custom streaming |
| `custom-provider-gitlab-duo/` | GitLab Duo via pi-ai's built-in Anthropic/OpenAI streaming through a proxy |

### External dependencies

| Example | What it shows |
|---|---|
| `with-deps/` | Extension with own `package.json` + deps (jiti resolution) |

## Subagent example (detailed)

`examples/extensions/subagent/` — delegate tasks to specialized subagents, each in a separate `pi` process with isolated context. Streaming output, parallel execution (max 8 tasks, 4 concurrent), Markdown final output, per-agent usage, Ctrl+C propagation.

**Setup** (symlink from a pi checkout into global dirs):

```bash
mkdir -p ~/.pi/agent/extensions/subagent
ln -sf <repo>/packages/coding-agent/examples/extensions/subagent/index.ts ~/.pi/agent/extensions/subagent/index.ts
ln -sf <repo>/packages/coding-agent/examples/extensions/subagent/agents.ts  ~/.pi/agent/extensions/subagent/agents.ts
mkdir -p ~/.pi/agent/agents ~/.pi/agent/prompts
ln -sf <repo>/.../subagent/agents/*.md   ~/.pi/agent/agents/
ln -sf <repo>/.../subagent/prompts/*.md  ~/.pi/agent/prompts/
```

**Tool modes:** single `{ agent, task }`; parallel `{ tasks: [...] }`; chain `{ chain: [...] }` with `{previous}` placeholder. Workflow prompts: `/implement`, `/scout-and-plan`, `/implement-and-review`. Sample agents: `scout` (fast recon), `planner`, `reviewer`, `worker`.

**Agent definitions:** markdown with frontmatter `name`, `description`, `tools` (comma list), `model` (optional; inherits parent model+thinking when omitted), body = system prompt. Locations: `~/.pi/agent/agents/*.md` (always) and `.pi/agents/*.md` (only with `agentScope: "project"|"both"` — project agents override same-named user agents).

**Security model:** the tool spawns `pi` subprocesses with delegated prompts. Default loads **user-level agents only**; enable project-local agents explicitly (`agentScope`) and only for trusted repos (interactive confirmation by default; `confirmProjectAgents: false` disables it).

## Plan mode and Doom overlay

- `plan-mode/` — Claude Code-style plan mode: read-only exploration phase with `/plan` command and step tracking; a good template for building your own.
- `doom-overlay/` — real-time game rendering as a TUI overlay at 35 FPS; demonstrates the overlay API and performance headroom.
