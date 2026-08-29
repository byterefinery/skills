# Extensions

Extensions are TypeScript modules (loaded via jiti, no compile step) that extend pi: custom tools, event interception, commands, shortcuts, CLI flags, UI, and providers.

> **Security:** extensions run with your full system permissions. Only install from sources you trust.

## Locations and loading

| Location | Scope |
|---|---|
| `~/.pi/agent/extensions/*.ts` (and `*/index.ts`) | Global |
| `.pi/extensions/*.ts` (and `*/index.ts`) | Project-local (loaded only after project trust) |
| `settings.json` `extensions` array | Extra paths |
| `pi -e <path|npm|git>` | Temporary for one run |

Styles: single file; directory with `index.ts` entry + helper modules; package with its own `package.json` + `node_modules/` (deps resolve automatically).

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

export default function (pi: ExtensionAPI) {
  pi.on("session_start", async (_e, ctx) => ctx.ui.notify("Loaded", "info"));
  pi.registerTool({ name: "greet", description: "Greet someone",
    parameters: Type.Object({ name: Type.String() }),
    async execute(_id, params) { return { content: [{ type: "text", text: `Hello, ${params.name}!` }], details: {} }; } });
  pi.registerCommand("hello", { description: "Say hello", handler: async (args, ctx) => ctx.ui.notify(`Hi ${args || "world"}`) });
}
```

**Rules of thumb:**
- The default export factory may be `async`; pi awaits it before startup continues (fetch remote config, discover models, then `pi.registerProvider()`).
- Never start long-lived resources (processes, sockets, watchers, timers) in the factory — it can run in invocations that never start a session. Start in `session_start`, close in `session_shutdown` (idempotent).
- `pi.registerTool()` works at any time (load, `session_start`, command handlers); new tools refresh immediately without `/reload`.

## Event lifecycle

```
startup:  project_trust → session_start → resources_discover
prompt:   input → before_agent_start → agent_start
          per turn: turn_start → context → before_provider_headers →
                    before_provider_request → after_provider_response →
                    LLM → tool_execution_start → tool_call (can block) →
                    tool_execution_update → tool_result (can modify) →
                    tool_execution_end → turn_end
          agent_end → agent_settled (nothing left to auto-run)
session replacement (/new /resume): session_before_switch → session_shutdown → session_start
fork/clone:  session_before_fork → session_shutdown → session_start { reason: "fork" }
compaction:  session_before_compact → session_compact | session_compact_failed
tree nav:    session_before_tree → session_tree
model:       thinking_level_select → model_select
exit:        session_shutdown
```

Do cleanup in `session_shutdown`, rebuild in-memory state in `session_start`.

### Notable events

- **`project_trust`** — user/global + CLI `-e` extensions only, before project resources load. Must return `{ trusted: "yes"|"no"|"undecided", remember?: boolean }`; first yes/no wins and suppresses the built-in prompt; check `ctx.hasUI` before prompting.
- **`resources_discover`** — return `{ skillPaths, promptPaths, themePaths }` to contribute resource paths (reason `startup` | `reload`).
- **`before_agent_start`** — after user submits, before the agent loop. Return `{ message, systemPrompt }` to inject a persistent message and/or replace the chained system prompt. `event.systemPromptOptions` exposes the structured data pi used to build the prompt (customPrompt, selectedTools, toolSnippets, promptGuidelines, appendSystemPrompt, cwd, contextFiles, skills).
- **`context`** — before each LLM call; `event.messages` is a deep copy, return `{ messages }` to modify.
- **`tool_call`** — return `{ block: true, reason }` to stop execution; `terminate: true` on the blocked result skips the follow-up LLM call.
- **`tool_result`** — can modify the result.
- **`message_end`** — can return `{ message }` replacing the finalized message (same role).
- **`input`** — intercept/transform user input before commands are checked.
- **`user_bash`** — user `!` commands.
- **Provider hooks** — `before_provider_headers` (mutate `event.headers`; `null` deletes), `before_provider_request` (inspect/replace payload; payload changes are not reflected in `ctx.getSystemPrompt()`), `after_provider_response` (status + headers before stream consume).
- **Model events** — `model_select`, `thinking_level_select`.
- **Agent events** — `agent_start`/`agent_end` bound a low-level run; `agent_settled` fires when pi will not continue running automatically (use for status integrations).

## ExtensionContext (`ctx`)

- `ctx.ui` — `notify(text, "info"|"warn"|"error")`, `confirm(title, message)`, `select(title, options)`, `input(title, message)`, `setStatus(key, text)` (footer), `setWidget(key, lines, placement)` (above/below editor), `setHeader/setFooter/setWorkingIndicator/setHiddenThinkingLabel/setEditorComponent`, `custom(...)` for full TUI components
- `ctx.mode`, `ctx.hasUI`, `ctx.cwd`
- `ctx.isProjectTrusted()`
- `ctx.sessionManager` — `getBranch()`, `getEntries()`, `getSessionFile()`, `getSessionId()`, `getLabel(entryId)`, ...
- `ctx.modelRegistry`, `ctx.model`, `ctx.thinkingLevel`, `ctx.scopedModels`
- `ctx.signal` — AbortSignal for the current operation
- `ctx.isIdle()`, `ctx.abort()`, `ctx.hasPendingMessages()`, `ctx.shutdown()`
- `ctx.getContextUsage()`, `ctx.compact()`, `ctx.getSystemPrompt()`

**ExtensionCommandContext** (in command handlers) additionally: `getSystemPromptOptions()`, `waitForIdle()`, `newSession()`, `fork(entryId)`, `navigateTree(targetId)`, `switchSession(path)`, `reload()`.

## ExtensionAPI (`pi`)

- `pi.on(event, handler)`
- `pi.registerTool(def)` — see Custom tools below
- `pi.sendMessage(message, { deliverAs: "steer"|"followUp"|"nextTurn", triggerTurn? })` — custom message that participates in LLM context
- `pi.sendUserMessage(content, { deliverAs?, expandPromptTemplates? })` — real user message; always triggers a turn; `deliverAs` required while streaming
- `pi.appendEntry(customType, data?)` — durable TUI-only state (not sent to LLM); pair with `pi.registerEntryRenderer()` for in-transcript rendering
- `pi.setSessionName(name)` / `pi.getSessionName()` / `pi.setLabel(entryId, label|undefined)`
- `pi.registerCommand(name, { description, handler, getArgumentCompletions? })` — duplicate names get `:1`, `:2` suffixes
- `pi.getCommands()` — invokable commands with `source` and `sourceInfo` provenance (use `sourceInfo`, don't infer from names)
- `pi.registerMessageRenderer(customType, renderer)`, `pi.registerEntryRenderer(customType, renderer)`, `pi.registerMarkdownTransformer(fn)` (display-only, sync, runs on streaming and width changes)
- `pi.registerShortcut("ctrl+x", { description, handler })`
- `pi.registerFlag(name, { description, type, default })` + `pi.getFlag(name)`
- `pi.exec(command, args, { signal, timeout })`
- `pi.getActiveTools()` / `pi.getAllTools()` / `pi.setActiveTools(names)` — runtime tool enable/disable (built-in + extension + sdk)
- `pi.setModel(model)` — returns `false` if no API key
- `pi.getThinkingLevel()` / `pi.setThinkingLevel(level)`
- `pi.events` — extension-to-extension event bus
- `pi.registerProvider(name, config)` / `pi.unregisterProvider(name)` — immediate after initial load; no `/reload` needed

## Custom tools

```typescript
pi.registerTool({
  name: "my_tool",
  label: "My Tool",               // UI display
  description: "What it does",
  promptSnippet: "One-line entry in the Available tools section",  // omit = excluded from that section
  promptGuidelines: ["Use my_tool when ..."],  // flat append to Guidelines; MUST name the tool
  parameters: Type.Object({ ... }),  // TypeBox
  prepareArguments(args) { return args; },     // optional pre-validation shim
  async execute(toolCallId, params, signal, onUpdate, ctx) {
    onUpdate?.({ content: [{ type: "text", text: "Working..." }], details: {} }); // stream progress
    return { content: [{ type: "text", text: "Done" }], details: { ... } };       // details persist in session
  },
  renderCall(args, theme, ctx) { /* optional */ },
  renderResult(result, options, theme, ctx) { /* optional */ },
});
```

- **String enums:** use `StringEnum` from `@earendil-works/pi-ai` — `Type.Union` of literals breaks Google.
- **Throw on failure** in `execute`; don't return errors as content. Thrown errors become `isError: true` tool results for the LLM.
- **`terminate: true`** (from `execute`, blocked `beforeToolCall`, or `afterToolCall`) skips the automatic follow-up LLM call only when every finalized tool result in the batch sets it (used e.g. for structured-output tools).
- **Overriding built-in tools:** register a tool with the same name as a built-in (`read`, `bash`, ...) to replace it (e.g. add logging/access control, remote execution via SSH).
- **Output truncation:** wrap large tool output at ~50KB / 2000 lines with a truncation marker (see `truncated-tool.ts` example using ripgrep).
- **Dynamic tools:** register in `session_start` or at runtime; enable with `pi.setActiveTools([...])` (see `dynamic-tools.ts`, `kimi-deferred-tools.ts`).

## State management

Store state in tool-result `details` so it survives branching; reconstruct on `session_start` by walking `ctx.sessionManager.getBranch()`:

```typescript
let items: string[] = [];
pi.on("session_start", async (_e, ctx) => {
  items = [];
  for (const entry of ctx.sessionManager.getBranch()) {
    if (entry.type === "message" && entry.message.role === "toolResult" && entry.message.toolName === "my_tool") {
      items = entry.message.details?.items ?? [];
    }
  }
});
```

## Custom providers (extension side)

`pi.registerProvider(name, config)` supports a legacy object form and a full pi-ai `Provider`:

- **Legacy fields:** `name`, `baseUrl` (required when defining models), `apiKey` (literal, `$ENV_VAR`, or `!command`; `$$` and `$!` escapes), `api` (`anthropic-messages`, `openai-completions`, `openai-responses`, ...), `headers`, `authHeader`, `models` (replaces all for the provider), `refreshModels` (dynamic discovery; generation-checked `context.publish({ persist })`), `oauth` (`login(callbacks)`, `refreshToken`, `getApiKey` — appears in `/login`), `streamSimple` (custom streaming).
- **Override a built-in provider:** `pi.registerProvider("anthropic", { baseUrl: "https://proxy..." })` keeps all models and existing auth.
- **Full provider:** `import { createProvider, openAICompletionsApi } from "@earendil-works/pi-ai"` for native auth, filtering, refresh, and stream behavior.
- `pi.unregisterProvider(name)` restores overridden built-ins.

See [06-providers-models](06-providers-models.md) for models.json (no-code path) and custom streaming details.

## Mode behavior

Extensions load in interactive, print, JSON, and RPC modes. `ctx.hasUI` is false in headless modes — guard UI calls. `ctx.ui` dialogs (confirm/select/input) work in RPC mode when a client attaches.
