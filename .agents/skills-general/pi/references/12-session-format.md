# Session Format

Sessions are stored as JSONL files. Each line is a JSON object with a `type` field. Entries form a tree via `id`/`parentId` fields.

## File Location

```
~/.pi/agent/sessions/--<path>--/<timestamp>_<uuid>.jsonl
```

Where `<path>` is the working directory with `/` replaced by `-`.

## Entry Types

### SessionHeader

First line. Metadata only, not part of the tree:

```json
{"type":"session","version":3,"id":"uuid","timestamp":"2024-12-03T14:00:00.000Z","cwd":"/path/to/project"}
```

### SessionMessageEntry

```json
{"type":"message","id":"a1b2c3d4","parentId":"prev1234","timestamp":"...","message":{"role":"user","content":"Hello"}}
```

### ModelChangeEntry

```json
{"type":"model_change","id":"d4e5f6g7","parentId":"c3d4e5f6","timestamp":"...","provider":"openai","modelId":"gpt-4o"}
```

### ThinkingLevelChangeEntry

```json
{"type":"thinking_level_change","id":"e5f6g7h8","parentId":"d4e5f6g7","timestamp":"...","thinkingLevel":"high"}
```

### CompactionEntry

```json
{"type":"compaction","id":"f6g7h8i9","parentId":"e5f6g7h8","timestamp":"...","summary":"...","firstKeptEntryId":"c3d4e5f6","tokensBefore":50000}
```

Newer compactions may include `retainedTail` (materialized `AgentMessage[]`) instead of `firstKeptEntryId`.

### BranchSummaryEntry

```json
{"type":"branch_summary","id":"g7h8i9j0","parentId":"a1b2c3d4","timestamp":"...","fromId":"f6g7h8i9","summary":"Branch explored approach A..."}
```

### CustomEntry

Extension state persistence. Does NOT participate in LLM context:

```json
{"type":"custom","id":"h8i9j0k1","parentId":"g7h8i9j0","timestamp":"...","customType":"my-extension","data":{"count":42}}
```

### CustomMessageEntry

Extension-injected messages that DO participate in LLM context:

```json
{"type":"custom_message","id":"i9j0k1l2","parentId":"h8i9j0k1","timestamp":"...","customType":"my-extension","content":"Injected context...","display":true}
```

### LabelEntry

```json
{"type":"label","id":"j0k1l2m3","parentId":"i9j0k1l2","timestamp":"...","targetId":"a1b2c3d4","label":"checkpoint-1"}
```

### SessionInfoEntry

```json
{"type":"session_info","id":"k1l2m3n4","parentId":"j0k1l2m3","timestamp":"...","name":"Refactor auth module"}
```

## Message Types

### Content Blocks

```typescript
interface TextContent { type: "text"; text: string; }
interface ImageContent { type: "image"; data: string; mimeType: string; }
interface ThinkingContent { type: "thinking"; thinking: string; }
interface ToolCall { type: "toolCall"; id: string; name: string; arguments: Record<string, any>; }
```

### Base Messages

```typescript
interface UserMessage {
  role: "user";
  content: string | (TextContent | ImageContent)[];
  timestamp: number;
}

interface AssistantMessage {
  role: "assistant";
  content: (TextContent | ThinkingContent | ToolCall)[];
  api: string; provider: string; model: string;
  usage: Usage;
  stopReason: "stop" | "length" | "toolUse" | "error" | "aborted";
  errorMessage?: string;
  timestamp: number;
}

interface ToolResultMessage {
  role: "toolResult";
  toolCallId: string; toolName: string;
  content: (TextContent | ImageContent)[];
  details?: any; usage?: Usage;
  isError: boolean; timestamp: number;
}
```

### Extended Messages

```typescript
interface BashExecutionMessage {
  role: "bashExecution"; command: string; output: string;
  exitCode?: number; cancelled: boolean; truncated: boolean;
  fullOutputPath?: string; excludeFromContext?: boolean; timestamp: number;
}

interface CustomMessage {
  role: "custom"; customType: string;
  content: string | (TextContent | ImageContent)[];
  display: boolean; details?: any; timestamp: number;
}

interface BranchSummaryMessage {
  role: "branchSummary"; summary: string; fromId: string; timestamp: number;
}

interface CompactionSummaryMessage {
  role: "compactionSummary"; summary: string; tokensBefore: number; timestamp: number;
}
```

## Tree Structure

Entries form a tree with `parentId` links. The "leaf" is the current position:

```
[user msg] ─── [assistant] ─── [user msg] ─── [assistant] ─┬─ [user msg] ← current leaf
                                                            │
                                                            └─ [branch_summary] ─── [user msg] ← alternate
```

## SessionManager API

### Static Creation

- `SessionManager.create(cwd, sessionDir?)` — new session
- `SessionManager.open(path, sessionDir?)` — open existing
- `SessionManager.continueRecent(cwd, sessionDir?)` — continue most recent or create new
- `SessionManager.inMemory(cwd?)` — no file persistence
- `SessionManager.forkFrom(sourcePath, targetCwd, sessionDir?)` — fork from another project

### Static Listing

- `SessionManager.list(cwd, sessionDir?)` — list sessions for a directory
- `SessionManager.listAll()` — list all sessions

### Instance Methods

- `getEntries()` — all entries (excluding header)
- `getTree()` — full tree structure
- `getPath()` — path from root to current leaf
- `getLeafEntry()` / `getLeafId()` — current position
- `getEntry(id)` — get entry by ID
- `getChildren(parentId)` — direct children
- `getLabel(id)` — get label for entry
- `branch(entryId)` — move leaf to earlier entry
- `branchWithSummary(entryId, summary)` — branch with context summary
- `createBranchedSession(leafId)` — extract path to new file
- `buildContextEntries()` — active branch entries with compaction applied
- `buildSessionContext()` — messages, thinkingLevel, and model for LLM
- `getSessionName()` / `getSessionId()` / `getSessionFile()` / `getCwd()` / `getSessionDir()`

### Appending (all return entry ID)

- `appendMessage(message)` — add message
- `appendThinkingLevelChange(level)` — record thinking change
- `appendModelChange(provider, modelId)` — record model change
- `appendCompaction(summary, firstKeptEntryId, tokensBefore, details?, fromHook?)` — add compaction
- `appendCustomEntry(customType, data?)` — extension state (not in context)
- `appendSessionInfo(name)` — set session display name
- `appendCustomMessageEntry(customType, content, display, details?)` — extension message (in context)
- `appendLabelChange(targetId, label)` — set/clear label

## Parsing Example

```typescript
import { readFileSync } from "fs";

const lines = readFileSync("session.jsonl", "utf8").trim().split("\n");

for (const line of lines) {
  const entry = JSON.parse(line);
  switch (entry.type) {
    case "session": console.log(`Session v${entry.version}: ${entry.id}`); break;
    case "message": console.log(`[${entry.id}] ${entry.message.role}`); break;
    case "compaction": console.log(`[${entry.id}] Compaction: ${entry.tokensBefore} tokens`); break;
    case "branch_summary": console.log(`[${entry.id}] Branch from ${entry.fromId}`); break;
    case "custom": console.log(`[${entry.id}] Custom (${entry.customType})`); break;
    case "label": console.log(`[${entry.id}] Label "${entry.label}" on ${entry.targetId}`); break;
    case "model_change": console.log(`[${entry.id}] Model: ${entry.provider}/${entry.modelId}`); break;
  }
}
```
