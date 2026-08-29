# SDK, RPC mode, JSON mode

## SDK

`npm install @earendil-works/pi-coding-agent` — the SDK is in the main package. Use it to embed pi, build custom UIs, automated pipelines, or test agent behavior. Node apps should prefer the SDK over spawning the CLI.

```typescript
import { createAgentSession, ModelRuntime, SessionManager } from "@earendil-works/pi-coding-agent";

const modelRuntime = await ModelRuntime.create();
const { session } = await createAgentSession({
  sessionManager: SessionManager.inMemory(),
  modelRuntime,
});
session.subscribe((event) => {
  if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
    process.stdout.write(event.assistantMessageEvent.delta);
  }
});
await session.prompt("What files are in the current directory?");
```

### createAgentSession() options

| Option | Default | Description |
|---|---|---|
| `modelRuntime` | Runtime using `agentDir/auth.json` + `models.json` | Canonical model/auth runtime |
| `cwd` | `process.cwd()` | Working directory |
| `agentDir` | `~/.pi/agent` | Config directory |
| `model` | From settings / first available | Model to use |
| `thinkingLevel` | From settings / `"off"` | Thinking level |
| `tools` | Built-ins `read`, `bash`, `edit`, `write` | Allowlist across built-in, extension, custom tools |
| `customTools` | `[]` | Additional tool definitions |
| `resourceLoader` | `DefaultResourceLoader` | Extensions, skills, prompts, themes, context files |
| `sessionManager` | `SessionManager.create(cwd)` | Persistence |
| `settingsManager` | `SettingsManager.create(cwd, agentDir)` | Settings overrides |

`DefaultResourceLoader` accepts `systemPromptOverride`, `extensionFactories`, `skillsOverride`, `agentsFilesOverride`, `promptsOverride`, `themesOverride` — use them to filter or fully replace discovery (call `await loader.reload()` after constructing). `ModelRuntime.create({ authPath, modelsPath })` relocates config; `setRuntimeApiKey(provider, key)` injects keys programmatically.

### AgentSession

```typescript
session.prompt(text, { expandPromptTemplates?, images?, streamingBehavior?, preflightResult? });
session.steer(text); session.followUp(text);     // queue while streaming
session.subscribe(listener);                     // returns unsubscribe
session.setModel(model); session.setThinkingLevel(level);
session.cycleModel(); session.cycleThinkingLevel();
session.navigateTree(targetId, { summarize?, customInstructions?, label? });
session.compact(customInstructions?); session.abortCompaction();
session.abort(); session.dispose();
// state: sessionFile, sessionId, agent, model, thinkingLevel, messages, isStreaming
```

- `prompt()` resolves only after the full accepted run finishes (including retries); `preflightResult(true/false)` reports acceptance vs rejection before that.
- While streaming, `prompt()` requires `streamingBehavior: "steer" | "followUp"` (or use `steer()`/`followUp()`); extension commands cannot be queued (they execute immediately when passed to `prompt()`).
- `steer`/`followUp` expand file-based prompt templates but error on extension commands.

### AgentSessionRuntime (session replacement)

Use `createAgentSessionRuntime(factory, { cwd, agentDir, sessionManager })` when you need `newSession()`, `switchSession()`, `fork()`, clone (`fork(entryId, { position: "at" })`), or `importFromJsonl()`. The same layer the interactive/print/RPC modes use. After replacement, `runtime.session` changes — **re-subscribe and re-run `bindExtensions(...)`**; failures throw for the caller to handle. `createAgentSessionServices({ cwd })` builds cwd-bound services when you assemble the runtime yourself.

### Tools

Built-in tools are factories: `createReadTool(cwd)`, `createBashTool(cwd, { exposeSessionEnvironment, spawnHook })`, `createEditTool`, `createWriteTool`, `createGrepTool`, `createFindTool`, `createLsTool`, `createPowerShellTool`. Custom tools are plain `AgentTool` objects (`name`, `label`, `description`, TypeBox `parameters`, `execute`, optional `executionMode`, `promptSnippet`, `promptGuidelines`, renderers).

### Events

Agent events (`agent_start/end/settled`, `turn_start/end`, `message_start/update/end`, `tool_execution_start/update/end`) plus session events (`queue_update`, `compaction_start/end`, `auto_retry_start/end`, `summarization_*`, `extension_error`, session replacement events). See `docs/sdk.md` for the full list and `docs/json.md` for the wire shapes.

## RPC mode

`pi --mode rpc [options]` — headless JSON protocol over stdin/stdout for non-Node integrations (IDEs, custom UIs). Node/TypeScript users should use the SDK instead; a subprocess TS client reference lives in `src/modes/rpc/rpc-client.ts`.

**Framing (strict):** commands are JSON objects, one per line on stdin; responses have `type: "response"`; events stream to stdout as JSON lines. Records are delimited by `\n` **only** — strip a trailing `\r` if present. Node `readline` is not compliant (splits on U+2028/U+2029). All commands accept an optional `id` echoed back in the response for correlation.

### Commands

| Area | Commands |
|---|---|
| Prompting | `prompt` (with `images`, `streamingBehavior`), `steer`, `follow_up`, `abort` |
| Sessions | `new_session` (optional `parentSession`), `switch_session`, `fork`, `clone`, `get_fork_messages`, `get_entries`, `get_tree`, `get_session_stats`, `get_last_assistant_text`, `set_session_name`, `export_html` |
| State | `get_state`, `get_messages` |
| Model | `set_model`, `cycle_model`, `get_available_models` |
| Thinking | `set_thinking_level`, `cycle_thinking_level`, `get_available_thinking_levels` |
| Queue modes | `set_steering_mode`, `set_follow_up_mode` |
| Compaction | `compact`, `set_auto_compaction` |
| Retry | `set_auto_retry`, `abort_retry` |
| Bash | `bash`, `abort_bash` |
| Commands | `get_commands` |

`prompt` during streaming requires `streamingBehavior`; `success: true` means accepted/queued/handled — later failures come through the event stream, not a second response for the same id. Extension commands in `prompt` execute immediately even mid-stream.

**Events:** `agent_start/end/settled`, `turn_start/end`, `message_start/update/end`, `tool_execution_start/update/end`, `bash_execution_update` (carries originating command `id`), `queue_update`, `compaction_start/end`, `auto_retry_*`, `summarization_retry_*`, `extension_error`.

**Extension UI over RPC:** extension dialogs appear on stdout as requests (`select`, `confirm`, `input`, `editor`, `notify`, `setStatus`, `setWidget`, `setTitle`, `set_editor_text`); the client answers on stdin with a value/confirmation response. `examples/extensions/rpc-demo.ts` + `examples/rpc-extension-ui.ts` exercise the full surface.

## JSON mode

`pi --mode json "prompt"` — print mode with all session events as JSON lines on stdout. Wire events use `JsonAgentSessionEvent`: same as `AgentSessionEvent` except `message_update` omits cumulative snapshots and toolcall starts carry `id`/`toolName`. Includes `queue_update`, `compaction_start/end`, and the base `AgentEvent` set.

Message types: `UserMessage`, `AssistantMessage` (content blocks: text, thinking, toolCall; `stopReason`, `usage` with cost), `ToolResultMessage` (text/image content, `isError`, `details`).

**When to use what:**
- One-shot output → `pi -p`
- Machine-readable events in a shell pipeline → `--mode json`
- Long-lived integration with command control → `--mode rpc`
- Same-process Node integration → SDK
