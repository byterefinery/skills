# SDK

The SDK provides programmatic access to pi's agent capabilities. Embed pi in other applications, build custom interfaces, or integrate with automated workflows.

## Quick Start

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

## Core Concepts

### createAgentSession()

Main factory function for a single `AgentSession`. Uses `ResourceLoader` to supply extensions, skills, prompt templates, themes, and context files.

```typescript
// Minimal: defaults with DefaultResourceLoader
const { session } = await createAgentSession();

// Custom: override specific options
const { session } = await createAgentSession({
  model: myModel,
  tools: ["read", "bash"],
  sessionManager: SessionManager.inMemory(),
});
```

### AgentSession

```typescript
interface AgentSession {
  prompt(text: string, options?: PromptOptions): Promise<void>;
  steer(text: string): Promise<void>;
  followUp(text: string): Promise<void>;
  subscribe(listener: (event: AgentSessionEvent) => void): () => void;
  setModel(model: Model): Promise<void>;
  setThinkingLevel(level: ThinkingLevel): void;
  cycleModel(): Promise<ModelCycleResult | undefined>;
  cycleThinkingLevel(): ThinkingLevel | undefined;
  navigateTree(targetId: string, options?: { summarize?: boolean; customInstructions?: string }): Promise<{ editorText?: string; cancelled: boolean }>;
  compact(customInstructions?: string): Promise<CompactionResult>;
  abort(): Promise<void>;
  dispose(): void;

  sessionFile: string | undefined;
  sessionId: string;
  agent: Agent;
  model: Model | undefined;
  thinkingLevel: ThinkingLevel;
  messages: AgentMessage[];
  isStreaming: boolean;
}
```

### createAgentSessionRuntime()

Use the runtime API when you need to replace the active session and rebuild cwd-bound runtime state:

```typescript
import {
  createAgentSessionFromServices,
  createAgentSessionRuntime,
  createAgentSessionServices,
  getAgentDir,
  SessionManager,
} from "@earendil-works/pi-coding-agent";

const createRuntime = async ({ cwd, sessionManager, sessionStartEvent }) => {
  const services = await createAgentSessionServices({ cwd });
  return {
    ...(await createAgentSessionFromServices({ services, sessionManager, sessionStartEvent })),
    services,
    diagnostics: services.diagnostics,
  };
};

const runtime = await createAgentSessionRuntime(createRuntime, {
  cwd: process.cwd(),
  agentDir: getAgentDir(),
  sessionManager: SessionManager.create(process.cwd()),
});

// Replace the active session
await runtime.newSession();
await runtime.switchSession("/path/to/session.jsonl");
await runtime.fork("entry-id");
```

After replacement, `runtime.session` changes. Re-subscribe to events and rebind extensions.

## Prompting and Message Queueing

```typescript
// Basic prompt
await session.prompt("What files are here?");

// With images
await session.prompt("What's in this image?", {
  images: [{ type: "image", source: { type: "base64", mediaType: "image/png", data: "..." } }]
});

// During streaming: must specify how to queue
await session.prompt("Stop and do this instead", { streamingBehavior: "steer" });
await session.prompt("After you're done, also check X", { streamingBehavior: "followUp" });

// Explicit queueing
await session.steer("New instruction");
await session.followUp("After you're done, also do this");
```

## Model

```typescript
import { getModel } from "@earendil-works/pi-ai";
import { ModelRuntime } from "@earendil-works/pi-coding-agent";

const modelRuntime = await ModelRuntime.create();

// Find built-in model
const opus = getModel("anthropic", "claude-opus-4-5");

// Find any model by provider/id, including custom models from models.json
const customModel = modelRuntime.getModel("my-provider", "my-model");

// Get only models with valid authentication
const available = await modelRuntime.getAvailable();

// Runtime API key override (not persisted)
modelRuntime.setRuntimeApiKey("anthropic", "sk-my-temp-key");

// CLI-style model resolution
import { resolveCliModel } from "@earendil-works/pi-coding-agent";
const cliModel = resolveCliModel({
  cliModel: "anthropic/claude-opus-4-5:high",
  modelRuntime,
});
```

## Tools

```typescript
// Read-only mode
const { session } = await createAgentSession({
  tools: ["read", "grep", "find", "ls"],
});

// Custom tool
import { defineTool } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

const myTool = defineTool({
  name: "my_tool",
  label: "My Tool",
  description: "Does something useful",
  parameters: Type.Object({
    input: Type.String({ description: "Input value" }),
  }),
  execute: async (_toolCallId, params) => ({
    content: [{ type: "text", text: `Result: ${params.input}` }],
    details: {},
  }),
});

const { session } = await createAgentSession({
  customTools: [myTool],
  tools: ["read", "bash", "my_tool"],
});
```

## Extensions

```typescript
import { DefaultResourceLoader } from "@earendil-works/pi-coding-agent";

const loader = new DefaultResourceLoader({
  additionalExtensionPaths: ["/path/to/my-extension.ts"],
  extensionFactories: [
    (pi) => {
      pi.on("agent_start", () => {
        console.log("[Inline Extension] Agent starting");
      });
    },
  ],
});
await loader.reload();

const { session } = await createAgentSession({ resourceLoader: loader });
```

Named inline extensions:

```typescript
import type { InlineExtension } from "@earendil-works/pi-coding-agent";

const myProvider: InlineExtension = {
  name: "my-provider",
  factory: (pi) => { pi.on("agent_start", () => {}); },
};
```

## Skills

```typescript
import { DefaultResourceLoader, type Skill } from "@earendil-works/pi-coding-agent";

const customSkill: Skill = {
  name: "my-skill",
  description: "Custom instructions",
  filePath: "/path/to/SKILL.md",
  baseDir: "/path/to",
  source: "custom",
};

const loader = new DefaultResourceLoader({
  skillsOverride: (current) => ({
    skills: [...current.skills, customSkill],
    diagnostics: current.diagnostics,
  }),
});
await loader.reload();
```

## Context Files

```typescript
const loader = new DefaultResourceLoader({
  agentsFilesOverride: (current) => ({
    agentsFiles: [
      ...current.agentsFiles,
      { path: "/virtual/AGENTS.md", content: "# Guidelines\n\n- Be concise" },
    ],
  }),
});
await loader.reload();
```

## System Prompt

```typescript
const loader = new DefaultResourceLoader({
  systemPromptOverride: () => "You are a helpful assistant.",
});
await loader.reload();
```

## Session Management

```typescript
// In-memory (no persistence)
const { session } = await createAgentSession({
  sessionManager: SessionManager.inMemory(),
});

// New persistent session
const { session: persisted } = await createAgentSession({
  sessionManager: SessionManager.create(process.cwd()),
});

// Continue most recent
const { session: continued } = await createAgentSession({
  sessionManager: SessionManager.continueRecent(process.cwd()),
});

// Open specific file
const { session: opened } = await createAgentSession({
  sessionManager: SessionManager.open("/path/to/session.jsonl"),
});

// List sessions
const sessions = await SessionManager.list(process.cwd());
const allSessions = await SessionManager.listAll(process.cwd());
```

### SessionManager Tree API

```typescript
const sm = SessionManager.open("/path/to/session.jsonl");
const entries = sm.getEntries();           // All entries (excludes header)
const tree = sm.getTree();                 // Full tree structure
const path = sm.getPath();                 // Path from root to current leaf
const leaf = sm.getLeafEntry();            // Current leaf entry
const entry = sm.getEntry(id);             // Get entry by ID
sm.branch(entryId);                        // Move leaf to earlier entry
sm.branchWithSummary(id, "Summary...");    // Branch with context summary
sm.createBranchedSession(leafId);          // Extract path to new file
```

## Settings Management

```typescript
import { SettingsManager } from "@earendil-works/pi-coding-agent";

// Default: loads from files (global + project merged)
const { session } = await createAgentSession({
  settingsManager: SettingsManager.create(),
});

// With overrides
const settingsManager = SettingsManager.create();
settingsManager.applyOverrides({
  compaction: { enabled: false },
  retry: { enabled: true, maxRetries: 5 },
});

// In-memory (no file I/O, for testing)
const { session } = await createAgentSession({
  settingsManager: SettingsManager.inMemory({ compaction: { enabled: false } }),
  sessionManager: SessionManager.inMemory(),
});
```

## Run Modes

### InteractiveMode

Full TUI interactive mode:

```typescript
import { InteractiveMode } from "@earendil-works/pi-coding-agent";

const mode = new InteractiveMode(runtime, {
  initialMessage: "Hello",
});
await mode.run();
```

### runPrintMode

Single-shot mode:

```typescript
import { runPrintMode } from "@earendil-works/pi-coding-agent";

await runPrintMode(runtime, {
  mode: "text",
  initialMessage: "Hello",
  messages: ["Follow up"],
});
```

### runRpcMode

JSON-RPC mode:

```typescript
import { runRpcMode } from "@earendil-works/pi-coding-agent";

await runRpcMode(runtime);
```

## Key Exports

```typescript
// Factory
createAgentSession, createAgentSessionRuntime, AgentSessionRuntime

// Auth and Models
ModelRuntime, ModelRegistry, resolveCliModel, resolveModelScopeWithDiagnostics

// Resource loading
DefaultResourceLoader, createEventBus

// Helpers
CONFIG_DIR_NAME, defineTool, getAgentDir, getPackageDir

// Session management
SessionManager, SettingsManager

// Tool factories
createCodingTools, createReadOnlyTools, createReadTool, createBashTool, createEditTool, createWriteTool
createGrepTool, createFindTool, createLsTool

// Types
type CreateAgentSessionOptions, type ExtensionAPI, type ToolDefinition, type Skill, type PromptTemplate
```
