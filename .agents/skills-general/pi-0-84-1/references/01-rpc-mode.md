# RPC Mode

RPC mode enables headless operation of the coding agent via JSON protocol over stdin/stdout. Use it for embedding pi in other applications, IDEs, or custom UIs.

## Starting RPC Mode

```bash
pi --mode rpc [options]
```

Common options: `--provider`, `--model`, `--name`, `--no-session`, `--session-dir`.

## Protocol

- **Commands**: JSON objects sent to stdin, one per line
- **Responses**: JSON objects with `type: "response"` indicating success/failure
- **Events**: Agent events streamed to stdout as JSON lines

Strict JSONL framing — split on `\n` only. Do not use Node `readline` (splits on Unicode separators).

## Commands

### Prompting

```json
{"id": "req-1", "type": "prompt", "message": "Hello, world!"}
```

During streaming, specify `streamingBehavior`:

```json
{"type": "prompt", "message": "New instruction", "streamingBehavior": "steer"}
```

- `"steer"` — delivered after current turn's tool calls
- `"followUp"` — delivered only when agent stops

With images:

```json
{"type": "prompt", "message": "What's in this image?", "images": [{"type": "image", "data": "base64...", "mimeType": "image/png"}]}
```

#### steer

Queue a steering message:

```json
{"type": "steer", "message": "Stop and do this instead"}
```

#### follow_up

Queue a follow-up message:

```json
{"type": "follow_up", "message": "After you're done, also do this"}
```

#### abort

```json
{"type": "abort"}
```

### State

#### get_state

```json
{"type": "get_state"}
```

Response includes `model`, `thinkingLevel`, `isStreaming`, `isCompacting`, `steeringMode`, `followUpMode`, `sessionFile`, `sessionId`, `sessionName`, `autoCompactionEnabled`, `messageCount`, `pendingMessageCount`.

#### get_messages

```json
{"type": "get_messages"}
```

Returns all `AgentMessage` objects.

### Model

```json
{"type": "set_model", "provider": "anthropic", "modelId": "claude-sonnet-4-20250514"}
{"type": "cycle_model"}
{"type": "get_available_models"}
```

### Thinking

```json
{"type": "set_thinking_level", "level": "high"}
{"type": "cycle_thinking_level"}
{"type": "get_available_thinking_levels"}
```

Levels: `off`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`.

### Queue Modes

```json
{"type": "set_steering_mode", "mode": "one-at-a-time"}
{"type": "set_follow_up_mode", "mode": "one-at-a-time"}
```

Modes: `"all"` or `"one-at-a-time"`.

### Compaction

```json
{"type": "compact"}
{"type": "compact", "customInstructions": "Focus on code changes"}
{"type": "set_auto_compaction", "enabled": true}
```

### Retry

```json
{"type": "set_auto_retry", "enabled": true}
{"type": "abort_retry"}
```

### Bash

```json
{"id": "req-1", "type": "bash", "command": "ls -la"}
```

Output streams as `bash_execution_update` events. Bash results reach the LLM on the **next prompt**, not immediately.

```json
{"type": "abort_bash"}
```

### Session

```json
{"type": "new_session"}
{"type": "new_session", "parentSession": "/path/to/parent.jsonl"}
{"type": "switch_session", "sessionPath": "/path/to/session.jsonl"}
{"type": "fork", "entryId": "abc123"}
{"type": "clone"}
{"type": "get_session_stats"}
{"type": "get_fork_messages"}
{"type": "get_entries"}
{"type": "get_entries", "since": "abc123"}
{"type": "get_tree"}
{"type": "get_last_assistant_text"}
{"type": "set_session_name", "name": "my-feature-work"}
{"type": "export_html"}
{"type": "export_html", "outputPath": "/tmp/session.html"}
```

### Commands

```json
{"type": "get_commands"}
```

Returns extension commands, prompt templates, and skills (not built-in TUI commands).

## Events

| Event | Description |
|-------|-------------|
| `agent_start` | Agent begins processing |
| `agent_end` | One low-level agent run completes |
| `agent_settled` | Fully settled; no retry/compaction/continuation remains |
| `turn_start` | New turn begins |
| `turn_end` | Turn completes (assistant message + tool results) |
| `message_start` | Message begins |
| `message_update` | Streaming delta (text/thinking/toolcall) |
| `message_end` | Message completes |
| `bash_execution_update` | Direct RPC bash output chunk |
| `tool_execution_start` | Tool begins execution |
| `tool_execution_update` | Tool progress (streaming output) |
| `tool_execution_end` | Tool completes |
| `queue_update` | Pending steering/follow-up queue changed |
| `compaction_start` | Compaction begins |
| `compaction_end` | Compaction completes |
| `auto_retry_start` | Auto-retry begins |
| `auto_retry_end` | Auto-retry completes |
| `extension_error` | Extension threw an error |

### message_update (Streaming)

Delta-only — no cumulative message. Assemble from `message_start` + deltas using `contentIndex`:

```json
{"type":"message_update","assistantMessageEvent":{"type":"text_start","contentIndex":0}}
{"type":"message_update","assistantMessageEvent":{"type":"text_delta","contentIndex":0,"delta":"Hello"}}
{"type":"message_update","assistantMessageEvent":{"type":"text_delta","contentIndex":0,"delta":" world"}}
{"type":"message_update","assistantMessageEvent":{"type":"text_end","contentIndex":0,"content":"Hello world"}}
```

Delta types: `text_start`, `text_delta`, `text_end`, `thinking_start`, `thinking_delta`, `thinking_end`, `toolcall_start`, `toolcall_delta`, `toolcall_end`.

## Extension UI Protocol

Extensions can request user interaction via dialog and fire-and-forget methods.

### Dialog Methods (stdout → stdin response)

```json
{"type": "extension_ui_request", "id": "uuid-1", "method": "select", "title": "Allow?", "options": ["Allow", "Block"], "timeout": 10000}
{"type": "extension_ui_request", "id": "uuid-2", "method": "confirm", "title": "Clear session?", "message": "All messages lost."}
{"type": "extension_ui_request", "id": "uuid-3", "method": "input", "title": "Enter value", "placeholder": "type..."}
{"type": "extension_ui_request", "id": "uuid-4", "method": "editor", "title": "Edit text", "prefill": "Line 1\nLine 2"}
```

Responses:

```json
{"type": "extension_ui_response", "id": "uuid-1", "value": "Allow"}
{"type": "extension_ui_response", "id": "uuid-2", "confirmed": true}
{"type": "extension_ui_response", "id": "uuid-3", "cancelled": true}
```

### Fire-and-Forget Methods (no response)

```json
{"type": "extension_ui_request", "id": "uuid-5", "method": "notify", "message": "Info", "notifyType": "info"}
{"type": "extension_ui_request", "id": "uuid-6", "method": "setStatus", "statusKey": "my-ext", "statusText": "Running..."}
{"type": "extension_ui_request", "id": "uuid-7", "method": "setWidget", "widgetKey": "my-ext", "widgetLines": ["Line 1"], "widgetPlacement": "aboveEditor"}
{"type": "extension_ui_request", "id": "uuid-8", "method": "setTitle", "title": "pi - project"}
{"type": "extension_ui_request", "id": "uuid-9", "method": "set_editor_text", "text": "prefilled"}
```

## Example: Basic Client (Python)

```python
import subprocess, json

proc = subprocess.Popen(
    ["pi", "--mode", "rpc", "--no-session"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
)

def send(cmd):
    proc.stdin.write(json.dumps(cmd) + "\n")
    proc.stdin.flush()

send({"type": "prompt", "message": "Hello!"})

for line in proc.stdout:
    event = json.loads(line)
    if event.get("type") == "message_update":
        delta = event.get("assistantMessageEvent", {})
        if delta.get("type") == "text_delta":
            print(delta["delta"], end="", flush=True)
    if event.get("type") == "agent_end":
        print()
        break
```

## Example: Interactive Client (Node.js)

```javascript
const { spawn } = require("child_process");
const { StringDecoder } = require("string_decoder");

const agent = spawn("pi", ["--mode", "rpc", "--no-session"]);
const decoder = new StringDecoder("utf8");
let buffer = "";

agent.stdout.on("data", (chunk) => {
    buffer += decoder.write(chunk);
    while (true) {
        const idx = buffer.indexOf("\n");
        if (idx === -1) break;
        let line = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 1);
        if (line.endsWith("\r")) line = line.slice(0, -1);
        const event = JSON.parse(line);
        if (event.type === "message_update") {
            const { assistantMessageEvent } = event;
            if (assistantMessageEvent.type === "text_delta") {
                process.stdout.write(assistantMessageEvent.delta);
            }
        }
    }
});

agent.stdin.write(JSON.stringify({ type: "prompt", message: "Hello" }) + "\n");

process.on("SIGINT", () => {
    agent.stdin.write(JSON.stringify({ type: "abort" }) + "\n");
});
```

## Types

### Model

```json
{
  "id": "claude-sonnet-4-20250514",
  "name": "Claude Sonnet 4",
  "api": "anthropic-messages",
  "provider": "anthropic",
  "baseUrl": "https://api.anthropic.com",
  "reasoning": true,
  "input": ["text", "image"],
  "contextWindow": 200000,
  "maxTokens": 16384,
  "cost": {"input": 3.0, "output": 15.0, "cacheRead": 0.3, "cacheWrite": 3.75}
}
```

### UserMessage

```json
{"role": "user", "content": "Hello!", "timestamp": 1733234567890, "attachments": []}
```

### AssistantMessage

```json
{
  "role": "assistant",
  "content": [
    {"type": "text", "text": "Hello! How can I help?"},
    {"type": "thinking", "thinking": "User is greeting me..."},
    {"type": "toolCall", "id": "call_123", "name": "bash", "arguments": {"command": "ls"}}
  ],
  "api": "anthropic-messages",
  "provider": "anthropic",
  "model": "claude-sonnet-4-20250514",
  "usage": {"input": 100, "output": 50, "cacheRead": 0, "cacheWrite": 0, "cost": {"input": 0.0003, "output": 0.00075, "cacheRead": 0, "cacheWrite": 0, "total": 0.00105}},
  "stopReason": "stop",
  "timestamp": 1733234567890
}
```

Stop reasons: `stop`, `length`, `toolUse`, `error`, `aborted`.

### ToolResultMessage

```json
{
  "role": "toolResult",
  "toolCallId": "call_123",
  "toolName": "bash",
  "content": [{"type": "text", "text": "total 48\n..."}],
  "usage": {"input": 100, "output": 50, "cacheRead": 0, "cacheWrite": 0, "totalTokens": 150, "cost": {"total": 0.00105}},
  "isError": false,
  "timestamp": 1733234567890
}
```

### BashExecutionMessage

```json
{
  "role": "bashExecution",
  "command": "ls -la",
  "output": "total 48\n...",
  "exitCode": 0,
  "cancelled": false,
  "truncated": false,
  "fullOutputPath": null,
  "timestamp": 1733234567890
}
```
