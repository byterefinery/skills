# RPC Mode

RPC mode enables headless operation of the coding agent via a JSON protocol over stdin/stdout.

## Starting RPC Mode

```bash
pi --mode rpc [options]
```

Common options: `--provider <name>`, `--model <pattern>`, `--name <name>`, `--no-session`, `--session-dir <path>`.

## Protocol

- **Commands**: JSON objects sent to stdin, one per line
- **Responses**: JSON objects with `type: "response"` indicating success/failure
- **Events**: Agent events streamed to stdout as JSON lines

All commands support optional `id` field for correlation. Split records on `\n` only; do not use `readline` (it splits on Unicode separators).

## Commands

### Prompting

```json
{"id": "req-1", "type": "prompt", "message": "Hello, world!"}
```

With images:
```json
{"type": "prompt", "message": "What's in this image?", "images": [{"type": "image", "data": "base64...", "mimeType": "image/png"}]}
```

During streaming, specify `streamingBehavior`:
```json
{"type": "prompt", "message": "New instruction", "streamingBehavior": "steer"}
```

- `"steer"`: delivered after current turn's tool calls
- `"followUp"`: delivered when agent finishes

### steer / follow_up

```json
{"type": "steer", "message": "Stop and do this instead"}
{"type": "follow_up", "message": "After you're done, also do this"}
```

### abort

```json
{"type": "abort"}
```

### State

```json
{"type": "get_state"}
```

Response includes: `model`, `thinkingLevel`, `isStreaming`, `isCompacting`, `steeringMode`, `followUpMode`, `sessionFile`, `sessionId`, `sessionName`, `autoCompactionEnabled`, `messageCount`, `pendingMessageCount`.

```json
{"type": "get_messages"}
```

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

Levels: `"off"`, `"minimal"`, `"low"`, `"medium"`, `"high"`, `"xhigh"`, `"max"`.

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
{"type": "abort_bash"}
```

Bash output streams as `bash_execution_update` events. Results reach the LLM on the next `prompt`.

### Session

```json
{"type": "new_session"}
{"type": "new_session", "parentSession": "/path/to/parent-session.jsonl"}
{"type": "switch_session", "sessionPath": "/path/to/session.jsonl"}
{"type": "fork", "entryId": "abc123"}
{"type": "clone"}
{"type": "get_fork_messages"}
{"type": "get_entries"}
{"type": "get_entries", "since": "abc123"}
{"type": "get_tree"}
{"type": "get_last_assistant_text"}
{"type": "set_session_name", "name": "my-feature-work"}
{"type": "get_session_stats"}
{"type": "export_html"}
{"type": "export_html", "outputPath": "/tmp/session.html"}
{"type": "get_commands"}
```

## Events

Events stream to stdout as JSON lines:

| Event | Description |
|-------|-------------|
| `agent_start` | Agent begins processing |
| `agent_end` | One low-level agent run completes |
| `agent_settled` | Fully settled; no auto retry/compaction/follow-up remains |
| `turn_start` / `turn_end` | Turn lifecycle |
| `message_start` / `message_update` / `message_end` | Message lifecycle |
| `bash_execution_update` | Direct RPC bash output chunk |
| `tool_execution_start` / `tool_execution_update` / `tool_execution_end` | Tool execution |
| `queue_update` | Pending steering/follow-up queue changed |
| `compaction_start` / `compaction_end` | Compaction |
| `auto_retry_start` / `auto_retry_end` | Auto-retry |
| `summarization_retry_scheduled` / `summarization_retry_attempt_start` / `summarization_retry_finished` | Summarization retry |
| `extension_error` | Extension threw an error |

### message_update (Streaming)

```json
{
  "type": "message_update",
  "message": {...},
  "assistantMessageEvent": {
    "type": "text_delta",
    "contentIndex": 0,
    "delta": "Hello ",
    "partial": {...}
  }
}
```

Delta types: `start`, `text_start`, `text_delta`, `text_end`, `thinking_start`, `thinking_delta`, `thinking_end`, `toolcall_start`, `toolcall_delta`, `toolcall_end`, `done`, `error`.

## Extension UI Protocol

Extensions can request user interaction via `ctx.ui.select()`, `ctx.ui.confirm()`, etc. In RPC mode, these translate to a request/response sub-protocol.

### Dialog Methods (require response)

`select`, `confirm`, `input`, `editor` — emit `extension_ui_request` on stdout, block until client sends `extension_ui_response` on stdin.

```json
// Request
{"type": "extension_ui_request", "id": "uuid-1", "method": "select", "title": "Choose:", "options": ["A", "B"]}

// Response
{"type": "extension_ui_response", "id": "uuid-1", "value": "A"}
// Or cancel
{"type": "extension_ui_response", "id": "uuid-1", "cancelled": true}
```

### Fire-and-Forget Methods

`notify`, `setStatus`, `setWidget`, `setTitle`, `set_editor_text` — emit `extension_ui_request` but do not expect a response.

### Unsupported in RPC Mode

`custom()` returns `undefined`. `setWorkingMessage()`, `setWorkingIndicator()`, `setFooter()`, `setHeader()`, `setEditorComponent()`, `setToolsExpanded()` are no-ops. `getEditorText()` returns `""`. `getAllThemes()` returns `[]`.

## Example: Python Client

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
