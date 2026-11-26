# Beta Agents and ChatKit (v3.60.0)

## Beta Agents sessions

`client.beta.agents.sessions` runs agent sessions. Both the streamed one-turn creation and the follow-up stream helper can collect a final answer:

```python
from openai import OpenAI

with client.beta.agents.sessions.create(
    agent={"model": MODEL},
    environment={"type": "none"},
    input="Explain this policy.",
    stream=True,
) as stream:
    result = stream.get_final_result()

print(result.output_text)
```

- **Creation requires `stream=True`.** `get_final_result()` may also be enabled ahead of iteration via `.with_result_collection()`.
- Follow-up turns: `client.beta.agents.sessions.stream(session_id, input="...", tool_handlers=handlers)` — same `tool_handlers` mapping as creation.
- The result exposes `output_text`, `turn`, final `messages`, `session_id`, and `turn_id`. Collection raises `AgentTurnResultError` when a complete successful answer cannot be established.
- With `AsyncOpenAI`: await creation, use `async with` / `async for`, await `get_final_result()`.

### Typed local tools

```python
from openai.lib.beta.agents import function_tool

@function_tool(name="lookup_item", description="Look up a catalog item.")
def lookup(item_id: str) -> dict[str, str]:
    return {"item_id": item_id, "name": "Notebook"}

with client.beta.agents.sessions.create(
    agent={"model": MODEL, "tools": [lookup.definition]},
    environment={"type": "none"},
    input="Find catalog item A123.",
    stream=True,
    tool_handlers={lookup.name: lookup},
) as stream:
    print(stream.get_final_result().output_text)
```

- `openai.lib.beta.agents.pydantic_function_tool(Model, name=..., handler=...)` binds an existing Pydantic argument model; the handler receives a validated instance.
- Callbacks run after their call event is yielded; async handlers work with `AsyncOpenAI`; existing dict handlers still work.
- **Hosted tool search**: set `defer_loading=True` on the decorator / `pydantic_function_tool()` / `FunctionTool` constructor and include `{"type": "tool_search"}` in `tools`.
- **Tool failures**: `on_tool_error=callback` receives an `AgentToolError` (`tool_name`, `stage`, `call_id`) from `openai.lib.beta.agents`; the model still receives the generic failure, and the SDK does not log automatically. Async observer supported; ordinary observer exceptions are ignored (cancellation is not suppressed).

### Typed output

Pass a Pydantic model (or Pydantic v2 dataclass) as `output_type=` to generate the Agents output schema and parse the completed answer: `result.output_parsed` is the first parsed final text part (every final text part is validated); `result.parse(Model)` re-parses an existing raw result; `AgentOutputParseError.result` retains the raw answer. `output_type` on `sessions.stream()` only selects the local parser — it does not change the session's schema.

### File staging and artifacts

```python
from pathlib import Path

prepared = client.beta.agents.environments.files.prepare({"/workspace/source.pdf": Path("source.pdf")})
session = client.beta.agents.sessions.create(
    agent={"model": MODEL},
    environment={"type": "openai_hosted", "files": prepared.files},
)
# ... run the session, collect result ...
artifacts = client.beta.agents.sessions.artifacts.for_result(result)
report_bytes = artifacts.content("/workspace/outputs/report.md").content
artifact = artifacts.download("/workspace/outputs/report.md", to=Path("downloaded-report.md"))
```

- `prepare_directory("docs", destination="/workspace/docs", include=["**/*.md"])` for a selected directory snapshot (`Path.glob` semantics, unreadable directories skipped); `files.upload(environment_id, file=..., path=...)` stages into an existing environment.
- Uploads remain caller-owned — use `prepared.uploaded_file_ids` with the ordinary Files API to delete them. Preparation errors expose partial uploads via `error.prepared`. A batch of uploads cannot share one explicit `Idempotency-Key`.
- Local path/directory uploads are for static application-owned files — they do not sandbox untrusted path selection or hostile local filesystem writers.
- With `AsyncOpenAI`, await preparation, staging, and artifact downloads.

### Agents resource tree

`client.beta.agents`: `sessions` (`.subagents`, `.artifacts`, `.items`, `.events`, `.traces`, `.turns`), `environments` (`.files`, `.templates`), `vaults` (`.credentials`), `automations` (`.invocations`).

## ChatKit (beta)

- `client.beta.chatkit.sessions` — `create`, `cancel(session_id)`
- `client.beta.chatkit.threads` — `retrieve`, `list`, `delete`, `list_items(thread_id)`
- Types: `openai.types.beta.chatkit` (`ChatSession`, `ChatKitThread`, `ChatKitThreadUserMessageItem`, `ChatKitThreadAssistantMessageItem`, `ChatKitAttachment`, `ChatKitWidgetItem`, ...)
