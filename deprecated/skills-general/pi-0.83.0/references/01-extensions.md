# Extensions

Extensions are TypeScript modules that extend pi's behavior. They subscribe to lifecycle events, register custom tools callable by the LLM, add commands, and more.

## Quick Start

Create `~/.pi/agent/extensions/my-extension.ts`:

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

export default function (pi: ExtensionAPI) {
  pi.on("session_start", async (_event, ctx) => {
    ctx.ui.notify("Extension loaded!", "info");
  });

  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName === "bash" && event.input.command?.includes("rm -rf")) {
      const ok = await ctx.ui.confirm("Dangerous!", "Allow rm -rf?");
      if (!ok) return { block: true, reason: "Blocked by user" };
    }
  });

  pi.registerTool({
    name: "greet",
    label: "Greet",
    description: "Greet someone by name",
    parameters: Type.Object({
      name: Type.String({ description: "Name to greet" }),
    }),
    async execute(toolCallId, params, signal, onUpdate, ctx) {
      return {
        content: [{ type: "text", text: `Hello, ${params.name}!` }],
        details: {},
      };
    },
  });

  pi.registerCommand("hello", {
    description: "Say hello",
    handler: async (args, ctx) => {
      ctx.ui.notify(`Hello ${args || "world"}!`, "info");
    },
  });
}
```

Test with `pi -e ./my-extension.ts`.

## Extension Locations

| Location | Scope |
|----------|-------|
| `~/.pi/agent/extensions/*.ts` | Global (all projects) |
| `~/.pi/agent/extensions/*/index.ts` | Global (subdirectory) |
| `.pi/extensions/*.ts` | Project-local |
| `.pi/extensions/*/index.ts` | Project-local (subdirectory) |

Additional paths via `settings.json` `extensions` array or `packages`.

Put extensions in auto-discovered locations for hot-reload with `/reload`. Use `pi -e ./path.ts` only for quick tests.

## Available Imports

- `@earendil-works/pi-coding-agent` — Extension types (`ExtensionAPI`, `ExtensionContext`, events)
- `typebox` — Schema definitions for tool parameters
- `@earendil-works/pi-ai` — AI utilities (`StringEnum`)
- `@earendil-works/pi-tui` — TUI components for custom rendering
- npm dependencies — add `package.json` next to extension, run `npm install`
- Node.js built-ins (`node:fs`, `node:path`, etc.)

Extensions are loaded via [jiti](https://github.com/unjs/jiti), so TypeScript works without compilation.

## Writing an Extension

Export a default factory function receiving `ExtensionAPI`. The factory can be synchronous or asynchronous. If async, pi awaits it before continuing startup.

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.on("event_name", async (event, ctx) => {
    const ok = await ctx.ui.confirm("Title", "Are you sure?");
    ctx.ui.notify("Done!", "info");
    ctx.ui.setStatus("my-ext", "Processing...");   // Footer status
    ctx.ui.setWidget("my-ext", ["Line 1", "Line 2"]); // Widget above editor
  });

  pi.registerTool({ ... });
  pi.registerCommand("name", { ... });
  pi.registerShortcut("ctrl+x", { ... });
  pi.registerFlag("my-flag", { ... });
}
```

Do not start background resources (processes, sockets, file watchers, timers) from the factory. Defer to `session_start` and register `session_shutdown` handlers for cleanup.

## Events

### Lifecycle Overview

```
pi starts
  ├─► project_trust (user/global and CLI extensions only)
  ├─► session_start { reason: "startup" }
  └─► resources_discover { reason: "startup" }

user sends prompt
  ├─► input (can intercept, transform, or handle)
  ├─► before_agent_start (can inject message, modify system prompt)
  ├─► agent_start
  │   ┌─── turn (repeats while LLM calls tools) ───┐
  │   ├─► turn_start
  │   ├─► context (can modify messages)
  │   ├─► before_provider_headers
  │   ├─► before_provider_request
  │   ├─► after_provider_response
  │   │   tool calls:
  │   │     ├─► tool_execution_start
  │   │     ├─► tool_call (can block)
  │   │     ├─► tool_execution_update
  │   │     ├─► tool_result (can modify)
  │   │     └─► tool_execution_end
  │   └─► turn_end
  ├─► agent_end
  └─► agent_settled

exit
  └─► session_shutdown
```

### Key Events

#### project_trust

Fired before pi decides whether to trust a project. Only user/global and CLI `-e` extensions participate. Return `{ trusted: "yes" | "no" | "undecided" }`. Use `remember: true` to persist.

#### session_start / session_shutdown

`session_start` fires on startup, reload, new session, resume, or fork. `session_shutdown` fires before teardown — use for cleanup.

#### before_agent_start

Fired after user submits prompt, before agent loop. Can inject a persistent message and/or modify the system prompt.

```typescript
pi.on("before_agent_start", async (event, ctx) => {
  return {
    message: {
      customType: "my-extension",
      content: "Additional context for the LLM",
      display: true,
    },
    systemPrompt: event.systemPrompt + "\n\nExtra instructions...",
  };
});
```

#### context

Fired before each LLM call. Modify messages non-destructively.

```typescript
pi.on("context", async (event, ctx) => {
  const filtered = event.messages.filter(m => !shouldPrune(m));
  return { messages: filtered };
});
```

#### tool_call

Fired before tool execution. **Can block.** `event.input` is mutable.

```typescript
import { isToolCallEventType } from "@earendil-works/pi-coding-agent";

pi.on("tool_call", async (event, ctx) => {
  if (isToolCallEventType("bash", event)) {
    event.input.command = `source ~/.profile\n${event.input.command}`;
    if (event.input.command.includes("rm -rf")) {
      return { block: true, reason: "Dangerous command" };
    }
  }
});
```

#### tool_result

Fired after tool execution. **Can modify result.** Handlers chain: each sees the latest result after previous handler changes.

```typescript
pi.on("tool_result", async (event, ctx) => {
  const response = await fetch("https://example.com/summarize", {
    method: "POST",
    body: JSON.stringify({ content: event.content }),
    signal: ctx.signal,
  });
  return { content: [...], details: {...}, isError: false };
});
```

#### input

Fired when user input is received, after extension commands but before skill/template expansion. Can intercept, transform, or handle.

```typescript
pi.on("input", async (event, ctx) => {
  if (event.text.startsWith("?quick "))
    return { action: "transform", text: `Respond briefly: ${event.text.slice(7)}` };
  if (event.text === "ping") {
    ctx.ui.notify("pong", "info");
    return { action: "handled" };
  }
  return { action: "continue" };
});
```

#### model_select / thinking_level_select

Fired when the model or thinking level changes. Notification-only for thinking level.

### Session Events

- `session_before_switch` — before `/new` or `/resume` (can cancel)
- `session_before_fork` — before `/fork` or `/clone` (can cancel)
- `session_before_compact` / `session_compact` — on compaction (can cancel or provide custom summary)
- `session_before_tree` / `session_tree` — on `/tree` navigation (can cancel or provide custom summary)
- `session_info_changed` — when session name changes

## ExtensionContext

All handlers receive `ctx: ExtensionContext`.

### ctx.ui

UI methods for user interaction: `select()`, `confirm()`, `input()`, `editor()`, `notify()`, `setStatus()`, `setWidget()`, `setTitle()`, `setEditorText()`, `custom()` for full TUI components.

### ctx.mode

Current run mode: `"tui"`, `"rpc"`, `"json"`, or `"print"`.

### ctx.hasUI

`true` in TUI and RPC modes. `false` in print and JSON modes. Use to guard dialog methods.

### ctx.sessionManager

Read-only access to session state: `getEntries()`, `getBranch()`, `buildContextEntries()`, `getLeafId()`.

### ctx.model / ctx.thinkingLevel / ctx.scopedModels

Access to active model, thinking level, and scoped model list.

### ctx.signal

Current agent abort signal, or `undefined` when idle. Use for abort-aware nested work.

### ctx.isIdle() / ctx.abort() / ctx.hasPendingMessages()

Control flow helpers.

### ctx.shutdown()

Request graceful shutdown. Deferred until idle in interactive mode.

### ctx.compact()

Trigger compaction without awaiting completion. Use `onComplete` and `onError` callbacks.

### ctx.getSystemPrompt()

Returns Pi's current system prompt string. During `before_agent_start`, reflects chained changes.

## ExtensionCommandContext

Command handlers receive `ExtensionCommandContext`, extending `ExtensionContext` with session control methods (only available in commands to avoid deadlocks):

- `ctx.waitForIdle()` — wait for agent to fully settle
- `ctx.newSession(options?)` — create a new session
- `ctx.fork(entryId, options?)` — fork from a specific entry
- `ctx.navigateTree(targetId, options?)` — navigate to a different point
- `ctx.switchSession(sessionPath, options?)` — switch to a different session
- `ctx.reload()` — run the same reload flow as `/reload`
- `ctx.getSystemPromptOptions()` — base inputs for system prompt building

### Session replacement lifecycle

`withSession` receives a fresh context bound to the replacement session. Captured old `pi`/`ctx` objects are stale after replacement. Only capture plain data (strings, ids, serialized config) that survives shutdown.

```typescript
// Safe pattern
pi.registerCommand("handoff", {
  handler: async (_args, ctx) => {
    const kickoff = "Continue from the replacement session";
    await ctx.newSession({
      withSession: async (ctx) => {
        await ctx.sendUserMessage(kickoff);
      },
    });
  },
});
```

## Custom Tools

```typescript
pi.registerTool({
  name: "my_tool",
  label: "My Tool",
  description: "Does something useful",
  parameters: Type.Object({
    input: Type.String({ description: "Input value" }),
  }),
  async execute(toolCallId, params, signal, onUpdate, ctx) {
    return {
      content: [{ type: "text", text: `Result: ${params.input}` }],
      details: {},
    };
  },
});
```

`pi.registerTool()` works both during extension load and after startup. New tools are refreshed immediately. Use `pi.setActiveTools()` to enable/disable tools at runtime.

## Example Use Cases

- Permission gates (confirm before `rm -rf`, `sudo`, etc.)
- Git checkpointing (stash at each turn, restore on branch)
- Path protection (block writes to `.env`, `node_modules/`)
- Custom compaction (summarize conversation your way)
- Interactive tools (questions, wizards, custom dialogs)
- Stateful tools (todo lists, connection pools)
- External integrations (file watchers, webhooks, CI triggers)
- Games while you wait (see `snake.ts` example)
