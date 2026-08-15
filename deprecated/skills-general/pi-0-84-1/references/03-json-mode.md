# JSON Mode

JSON event stream mode outputs all session events as JSON lines to stdout. Use it for integrating pi into other tools or custom UIs without a full RPC client.

## Usage

```bash
pi --mode json "Your prompt"
```

## Output Format

Each line is a JSON object. First line is the session header:

```json
{"type":"session","version":3,"id":"uuid","timestamp":"...","cwd":"/path"}
```

Followed by events as they occur:

```json
{"type":"agent_start"}
{"type":"turn_start"}
{"type":"message_start","message":{"role":"assistant","content":[],...}}
{"type":"message_update","assistantMessageEvent":{"type":"text_delta","contentIndex":0,"delta":"Hello"}}
{"type":"message_end","message":{...}}
{"type":"turn_end","message":{...},"toolResults":[]}
{"type":"agent_end","messages":[...]}
```

`message_update` is delta-only — no cumulative `message` field, no `assistantMessageEvent.partial`. Use `contentIndex` and `delta` to assemble live text. `message_end` is authoritative.

## Event Types

### Agent Lifecycle

```typescript
| { type: "agent_start" }
| { type: "agent_end"; messages: AgentMessage[] }
```

### Turn Lifecycle

```typescript
| { type: "turn_start" }
| { type: "turn_end"; message: AgentMessage; toolResults: ToolResultMessage[] }
```

### Message Lifecycle

```typescript
| { type: "message_start"; message: AgentMessage }
| { type: "message_update"; assistantMessageEvent: AssistantMessageEvent }
| { type: "message_end"; message: AgentMessage }
```

### Tool Execution

```typescript
| { type: "tool_execution_start"; toolCallId: string; toolName: string; args: any }
| { type: "tool_execution_update"; toolCallId: string; toolName: string; args: any; partialResult: any }
| { type: "tool_execution_end"; toolCallId: string; toolName: string; result: any; isError: boolean }
```

### Session Events

```typescript
| { type: "queue_update"; steering: string[]; followUp: string[] }
| { type: "compaction_start"; reason: "manual" | "threshold" | "overflow" }
| { type: "compaction_end"; reason: string; result: CompactionResult | null; aborted: boolean; willRetry: boolean }
| { type: "auto_retry_start"; attempt: number; maxAttempts: number; delayMs: number; errorMessage: string }
| { type: "auto_retry_end"; success: boolean; attempt: number; finalError?: string }
```

## Message Types

### UserMessage

```typescript
{
  role: "user",
  content: string | (TextContent | ImageContent)[],
  timestamp: number,
  attachments: Attachment[]
}
```

### AssistantMessage

```typescript
{
  role: "assistant",
  content: (TextContent | ThinkingContent | ToolCallContent)[],
  api: string,
  provider: string,
  model: string,
  usage: Usage,
  stopReason: "stop" | "length" | "toolUse" | "error" | "aborted",
  timestamp: number
}
```

### ToolResultMessage

```typescript
{
  role: "toolResult",
  toolCallId: string,
  toolName: string,
  content: (TextContent | ImageContent)[],
  usage?: Usage,
  isError: boolean,
  timestamp: number
}
```

### Extended Messages

- `BashExecutionMessage` — created by RPC `bash` command
- `CustomMessage` — arbitrary custom messages
- `BranchSummaryMessage` — branch navigation summaries
- `CompactionSummaryMessage` — compaction summaries

## Example

Filter for message completions:

```bash
pi --mode json "List files" 2>/dev/null | jq -c 'select(.type == "message_end")'
```

Stream text deltas:

```bash
pi --mode json "Hello" 2>/dev/null | jq -r 'select(.type == "message_update" and .assistantMessageEvent.type == "text_delta") | .assistantMessageEvent.delta'
```

## Notes

- JSON mode is non-interactive; use with `--no-session` for ephemeral runs
- Stderr contains diagnostics and errors; pipe `2>/dev/null` for clean stdout
- Events match `AgentSessionEvent` from the SDK except streaming updates omit cumulative snapshots
