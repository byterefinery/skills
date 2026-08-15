# SDK

The SDK provides programmatic access to pi's agent capabilities. Embed pi in applications, build custom interfaces, or integrate with automated workflows.

## Installation

```bash
npm install @earendil-works/pi-coding-agent
```

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

## Core API

### createAgentSession()

```typescript
const { session } = await createAgentSession(); // Minimal
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
  compact(customInstructions?: string): Promise<CompactionResult>;
  abortCompaction(): void;
  abort(): Promise<void>;
  navigateTree(targetId: string, options?: { summarize?: boolean }): Promise<{ editorText?: string; cancelled: boolean }>;
  dispose(): void;

  // State
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

Use for session replacement (new, resume, fork, clone, import):

```typescript
import {
  type CreateAgentSessionRuntimeFactory,
  createAgentSessionFromServices,
  createAgentSessionRuntime,
  createAgentSessionServices,
  getAgentDir,
  SessionManager,
} from "@earendil-works/pi-coding-agent";

const createRuntime: CreateAgentSessionRuntimeFactory = async ({ cwd, sessionManager, sessionStartEvent }) => {
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

// Replacements change runtime.session — re-subscribe after
await runtime.newSession();
await runtime.switchSession("/path/to/session.jsonl");
await runtime.fork("entry-id");
await runtime.fork("entry-id", { position: "at" }); // clone
```

## Prompting

```typescript
await session.prompt("What files are here?");

// With images
await session.prompt("What's in this image?", {
  images: [{ type: "image", source: { type: "base64", mediaType: "image/png", data: "..." } }]
});

// During streaming
await session.prompt("Stop and do this", { streamingBehavior: "steer" });
await session.prompt("After done, check X", { streamingBehavior: "followUp" });

// Explicit queueing
await session.steer("New instruction");
await session.followUp("After done, also do this");
```

`PromptOptions`:
```typescript
interface PromptOptions {
  expandPromptTemplates?: boolean;
  images?: ImageContent[];
  streamingBehavior?: "steer" | "followUp";
  source?: InputSource;
  preflightResult?: (success: boolean) => void;
}
```

## Model Selection

```typescript
import { getModel } from "@earendil-works/pi-ai";

const opus = getModel("anthropic", "claude-opus-4-5");
const customModel = modelRuntime.getModel("my-provider", "my-model");
const available = await modelRuntime.getAvailable();

const cliModel = resolveCliModel({
  cliModel: "anthropic/claude-opus-4-5:high",
  modelRuntime,
});
```

## Authentication

```typescript
const modelRuntime = await ModelRuntime.create();

// Runtime override (not persisted)
await modelRuntime.setRuntimeApiKey("anthropic", "sk-my-temp-key");

// Custom paths
const customRuntime = await ModelRuntime.create({
  authPath: "/my/app/auth.json",
  modelsPath: "/my/app/models.json",
});

// In-memory credentials
import { InMemoryCredentialStore } from "@earendil-works/pi-ai";
const credentials = new InMemoryCredentialStore();
const inMemoryRuntime = await ModelRuntime.create({ credentials });

// Refresh catalogs
const signal = AbortSignal.timeout(15_000);
const result = await modelRuntime.refresh({ providers: ["anthropic"], signal });
```

Resolution priority: runtime overrides → `auth.json` → environment variables → fallback resolver.

## Tools

```typescript
const { session } = await createAgentSession({
  tools: ["read", "grep", "find", "ls"],   // read-only
});

const { session } = await createAgentSession({
  excludeTools: ["ask_question"],  // disable specific
});
```

### Custom Tools

```typescript
import { Type } from "typebox";
import { defineTool } from "@earendil-works/pi-coding-agent";

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
  tools: ["read", "bash", "my_tool"], // include custom tool name
});
```

## Extensions

```typescript
import { DefaultResourceLoader } from "@earendil-works/pi-coding-agent";

const loader = new DefaultResourceLoader({
  additionalExtensionPaths: ["/path/to/my-extension.ts"],
  extensionFactories: [
    (pi) => {
      pi.on("agent_start", () => console.log("Agent starting"));
    },
  ],
});
await loader.reload();
const { session } = await createAgentSession({ resourceLoader: loader });
```

### Named Inline Extensions

```typescript
import type { InlineExtension } from "@earendil-works/pi-coding-agent";

const myProvider: InlineExtension = {
  name: "my-provider",
  factory: (pi) => {
    pi.on("agent_start", () => console.log("[my-provider] Agent starting"));
  },
};
```

### Event Bus

```typescript
import { createEventBus } from "@earendil-works/pi-coding-agent";

const eventBus = createEventBus();
const loader = new DefaultResourceLoader({ eventBus });
await loader.reload();
eventBus.on("my-extension:status", (data) => console.log(data));
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
```

## Prompt Templates

```typescript
import { DefaultResourceLoader, type PromptTemplate } from "@earendil-works/pi-coding-agent";

const customCommand: PromptTemplate = {
  name: "deploy",
  description: "Deploy the application",
  source: "(custom)",
  content: "# Deploy\n\n1. Build\n2. Test\n3. Deploy",
};

const loader = new DefaultResourceLoader({
  promptsOverride: (current) => ({
    prompts: [...current.prompts, customCommand],
    diagnostics: current.diagnostics,
  }),
});
```

## Session Management

```typescript
// In-memory
const { session } = await createAgentSession({
  sessionManager: SessionManager.inMemory(),
});

// Persistent
const { session } = await createAgentSession({
  sessionManager: SessionManager.create(process.cwd()),
});

// Continue most recent
const { session, modelFallbackMessage } = await createAgentSession({
  sessionManager: SessionManager.continueRecent(process.cwd()),
});

// Open specific file
const { session } = await createAgentSession({
  sessionManager: SessionManager.open("/path/to/session.jsonl"),
});

// List sessions
const sessions = await SessionManager.list(process.cwd());
const allSessions = await SessionManager.listAll(process.cwd());
```

### SessionManager Tree API

```typescript
const sm = SessionManager.open("/path/to/session.jsonl");
const entries = sm.getEntries();
const tree = sm.getTree();
const path = sm.getPath();
const leaf = sm.getLeafEntry();
const entry = sm.getEntry(id);
const children = sm.getChildren(id);
const label = sm.getLabel(id);
sm.appendLabelChange(id, "checkpoint");
sm.branch(entryId);
sm.branchWithSummary(id, "Summary...");
sm.createBranchedSession(leafId);
```

## Settings Management

```typescript
import { SettingsManager } from "@earendil-works/pi-coding-agent";

// From files (global + project merged)
const { session } = await createAgentSession({
  settingsManager: SettingsManager.create(),
});

// With overrides
const settingsManager = SettingsManager.create();
settingsManager.applyOverrides({
  compaction: { enabled: false },
  retry: { enabled: true, maxRetries: 5 },
});

// In-memory
const { session } = await createAgentSession({
  settingsManager: SettingsManager.inMemory({ compaction: { enabled: false } }),
  sessionManager: SessionManager.inMemory(),
});

// Custom directories
const { session } = await createAgentSession({
  settingsManager: SettingsManager.create("/custom/cwd", "/custom/agent"),
});
```

## Agent State

```typescript
const state = session.agent.state;
// state.messages, state.model, state.thinkingLevel, state.systemPrompt, state.tools
// state.streamingMessage?, state.errorMessage?

session.agent.state.messages = messages; // replace messages
session.agent.state.tools = tools;       // replace tools
await session.agent.waitForIdle();       // wait for processing
```

## Events

```typescript
session.subscribe((event) => {
  switch (event.type) {
    case "message_update":
      if (event.assistantMessageEvent.type === "text_delta") {
        process.stdout.write(event.assistantMessageEvent.delta);
      }
      break;
    case "tool_execution_start":
      console.log(`Tool: ${event.toolName}`);
      break;
    case "tool_execution_end":
      console.log(`Result: ${event.isError ? "error" : "success"}`);
      break;
    case "agent_start":
    case "agent_end":
    case "turn_start":
    case "turn_end":
    case "message_start":
    case "message_end":
    case "queue_update":
    case "compaction_start":
    case "compaction_end":
    case "auto_retry_start":
    case "auto_retry_end":
      break;
  }
});
```

## Run Modes

### InteractiveMode

```typescript
import { InteractiveMode } from "@earendil-works/pi-coding-agent";

const mode = new InteractiveMode(runtime, {
  migratedProviders: [],
  modelFallbackMessage: undefined,
  initialMessage: "Hello",
  initialImages: [],
  initialMessages: [],
});
await mode.run();
```

### runPrintMode

```typescript
import { runPrintMode } from "@earendil-works/pi-coding-agent";

await runPrintMode(runtime, {
  mode: "text",
  initialMessage: "Hello",
  initialImages: [],
  messages: ["Follow up"],
});
```

### runRpcMode

```typescript
import { runRpcMode } from "@earendil-works/pi-coding-agent";

await runRpcMode(runtime);
```

## Complete Example

```typescript
import { getModel } from "@earendil-works/pi-ai";
import { Type } from "typebox";
import {
  createAgentSession, DefaultResourceLoader, defineTool,
  ModelRuntime, SessionManager, SettingsManager,
} from "@earendil-works/pi-coding-agent";

const modelRuntime = await ModelRuntime.create();
if (process.env.MY_KEY) {
  await modelRuntime.setRuntimeApiKey("anthropic", process.env.MY_KEY);
}

const statusTool = defineTool({
  name: "status", label: "Status", description: "Get system status",
  parameters: Type.Object({}),
  execute: async () => ({
    content: [{ type: "text", text: `Uptime: ${process.uptime()}s` }],
    details: {},
  }),
});

const model = getModel("anthropic", "claude-opus-4-5");
if (!model) throw new Error("Model not found");

const settingsManager = SettingsManager.inMemory({
  compaction: { enabled: false },
  retry: { enabled: true, maxRetries: 2 },
});

const loader = new DefaultResourceLoader({
  cwd: process.cwd(),
  agentDir: "/custom/agent",
  settingsManager,
  systemPromptOverride: () => "You are a minimal assistant. Be concise.",
});
await loader.reload();

const { session } = await createAgentSession({
  cwd: process.cwd(),
  agentDir: "/custom/agent",
  model, thinkingLevel: "off", modelRuntime,
  tools: ["read", "bash", "status"],
  customTools: [statusTool],
  resourceLoader: loader,
  sessionManager: SessionManager.inMemory(),
  settingsManager,
});

session.subscribe((event) => {
  if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
    process.stdout.write(event.assistantMessageEvent.delta);
  }
});

await session.prompt("Get status and list files.");
```

## Exports

```typescript
// Factory
createAgentSession, createAgentSessionRuntime, AgentSessionRuntime

// Auth and Models
ModelRuntime, ModelRegistry, CredentialSynchronizationError,
resolveCliModel, resolveModelScopeWithDiagnostics

// Resource loading
DefaultResourceLoader, type ResourceLoader, createEventBus

// Helpers
CONFIG_DIR_NAME, defineTool, getAgentDir, getPackageDir,
getReadmePath, getDocsPath, getExamplesPath

// Session management
SessionManager, SettingsManager

// Tool factories
createCodingTools, createReadOnlyTools,
createReadTool, createBashTool, createEditTool, createWriteTool,
createGrepTool, createFindTool, createLsTool

// Types
type CreateAgentSessionOptions, CreateAgentSessionResult,
ExtensionFactory, InlineExtension, ExtensionAPI,
ToolDefinition, Skill, PromptTemplate, Tool
```
