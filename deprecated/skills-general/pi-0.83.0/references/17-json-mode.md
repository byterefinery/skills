# JSON Event Stream Mode

```bash
pi --mode json "Your prompt"
```

Outputs all session events as JSON lines to stdout. Useful for integrating pi into other tools or custom UIs.

## Event Types

Events are `AgentSessionEvent`:

```typescript
type AgentSessionEvent =
  // Agent lifecycle
  | { type: "agent_start" }
  | { type: "agent_end"; messages: AgentMessage[] }
  // Turn lifecycle
  | { type: "turn_start" }
  | { type: "turn_end"; message: AgentMessage; toolResults: ToolResultMessage[] }
  // Message lifecycle
  | { type: "message_start"; message: AgentMessage }
  | { type: "message_update"; message: AgentMessage; assistantMessageEvent: AssistantMessageEvent }
  | { type: "message_end"; message: AgentMessage }
  // Tool execution
  | { type: "tool_execution_start"; toolCallId: string; toolName: string; args: any }
  | { type: "tool_execution_update"; toolCallId: string; toolName: string; args: any; partialResult: any }
  | { type: "tool_execution_end"; toolCallId: string; toolName: string; result: any; isError: boolean }
  // Queue
  | { type: "queue_update"; steering: readonly string[]; followUp: readonly string[] }
  // Compaction
  | { type: "compaction_start"; reason: "manual" | "threshold" | "overflow" }
  | { type: "compaction_end"; reason: "manual" | "threshold" | "overflow"; result: CompactionResult | undefined; aborted: boolean; willRetry: boolean; errorMessage?: string }
  // Retry
  | { type: "auto_retry_start"; attempt: number; maxAttempts: number; delayMs: number; errorMessage: string }
  | { type: "auto_retry_end"; success: boolean; attempt: number; finalError?: string }
  // Summarization retry
  | { type: "summarization_retry_scheduled"; attempt: number; maxAttempts: number; delayMs: number; errorMessage: string }
  | { type: "summarization_retry_attempt_start"; source: "branchSummary" | "compaction"; reason?: string }
  | { type: "summarization_retry_finished" };
```

## Output Format

Each line is a JSON object. First line is the session header:

```json
{"type":"session","version":3,"id":"uuid","timestamp":"...","cwd":"/path"}
```

Followed by events:

```json
{"type":"agent_start"}
{"type":"turn_start"}
{"type":"message_start","message":{"role":"assistant","content":[],...}}
{"type":"message_update","message":{...},"assistantMessageEvent":{"type":"text_delta","delta":"Hello",...}}
{"type":"message_end","message":{...}}
{"type":"turn_end","message":{...},"toolResults":[]}
{"type":"agent_end","messages":[...]}
```

## Example

```bash
# Filter for message_end events
pi --mode json "List files" 2>/dev/null | jq -c 'select(.type == "message_end")'

# Stream text deltas
pi --mode json "Hello" 2>/dev/null | jq -r 'select(.type == "message_update" and .assistantMessageEvent.type == "text_delta") | .assistantMessageEvent.delta'
```

## Message Types

Base messages from `packages/ai/src/types.ts`:
- `UserMessage` — `role: "user"`
- `AssistantMessage` — `role: "assistant"` with content blocks, usage, stopReason
- `ToolResultMessage` — `role: "toolResult"` with toolCallId, toolName, content

Extended messages from `packages/coding-agent/src/core/messages.ts`:
- `BashExecutionMessage` — `role: "bashExecution"`
- `CustomMessage` — `role: "custom"`
- `BranchSummaryMessage` — `role: "branchSummary"`
- `CompactionSummaryMessage` — `role: "compactionSummary"`
