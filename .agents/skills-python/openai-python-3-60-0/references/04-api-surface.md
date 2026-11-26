# API Surface (v3.60.0)

Generated from the OpenAI OpenAPI spec. Method signatures: `**params` TypedDicts in, Pydantic models out. The full per-endpoint reference in the repo is `api.md`. Sync paths shown; `AsyncOpenAI` mirrors them with `await`.

## Core resources

| Resource | Key methods |
|---|---|
| `client.responses` | `create`, `retrieve` (with `stream`), `delete`, `cancel`, `compact`, plus `.parse()` / `.stream()` helpers, `.connect()` (WebSocket), `.input_tokens.count()`, `.input_items.list()` |
| `client.chat.completions` | `create`, `retrieve`, `update`, `list`, `delete`, plus `.parse()` / `.stream()` helpers, `.messages.list()` |
| `client.completions` | `create` (legacy completions API) |
| `client.decisions` | `create` — Decisions API; the application supplies all eligible choices and their arguments (see [07-browser-computer-tools](07-browser-computer-tools.md)) |
| `client.embeddings` | `create` |
| `client.files` | `create`, `retrieve`, `list`, `delete`, `content`, `retrieve_content`, `wait_for_processing` |
| `client.images` | `generate`, `edit`, `create_variation` |
| `client.audio.speech` / `.transcriptions` / `.translations` | `create` (speech returns binary; use `with_streaming_response`) |
| `client.audio.voices` / `.voice_consents` | list/retrieve voice resources and consents |
| `client.moderations` | `create` |
| `client.models` | `retrieve`, `list`, `delete` |
| `client.batches` | `create`, `retrieve`, `list`, `cancel` |
| `client.uploads` | `create`, `cancel`, `complete`, `.parts.create`, plus `upload_file_chunked()` convenience |
| `client.conversations` | `create`, `retrieve`, `update`, `delete`, `.items` (add/list items) |
| `client.videos` | `create` (+ `create_and_poll`), status checks |
| `client.containers` | create/retrieve/list/delete, `.files` (upload), `.content` |
| `client.skills` | create/retrieve/list, `.content`, `.versions` (create, list, `.content`) |
| `client.evals` | `create`, `retrieve`, `list`, `.runs` (create, retrieve, list, cancel, `.output_items`) |
| `client.content_provenance_checks` | `create` |
| `client.webhooks` | `unwrap(payload, headers, *, secret)`, `verify_signature(payload, headers, *, secret)` — secret defaults to `OPENAI_WEBHOOK_SECRET` |
| `client.safety.cases` / `client.safety.alerts` | `retrieve` |
| `client.live.sessions` | `accept`, `reject`, `fork`, `refer`, `hangup`, `download_recording` — Live API (WebRTC) call control |
| `client.realtime` | `connect(...)` (WebSocket, e.g., `model="gpt-realtime-2"`), `.calls`, `.client_secrets`, `.sessions`, `.transcription_sessions`, `.translations` |
| `client.admin` | organization admin — `audit_logs`, `admin_api_keys`, `usage`, `invites`, `users`, `groups`, `roles`, `data_retention`, `external_keys`, `workload_identity_providers` (`.federation_rules`), `external_storage`, `spend_limit`, `spend_alerts`, `certificates`, `projects` (users, roles, service accounts, API keys, rate limits, model permissions, service tier settings, hosted tool permissions, groups, data retention, spend limit/alerts, certificates) |

## Fine-tuning and vector stores

- `client.fine_tuning.jobs` — `create`, `retrieve`, `list`, `cancel`, `list_events`, `pause`, `resume`, `.checkpoints.list()`; `client.fine_tuning.checkpoints.permissions` (create/retrieve/list/delete); `client.fine_tuning.alpha.graders` (`run`, `validate`)
- `client.vector_stores` — `create`, `retrieve`, `update`, `list`, `delete`, `search`; `.files` (`create`, `retrieve`, `update`, `list`, `delete`, `content`, `upload`, `poll`, `create_and_poll`, `upload_and_poll`); `.file_batches` (same pattern)

## Beta namespace

`client.beta.*` for APIs still marked beta:

- **Agents** (`client.beta.agents`) — `sessions` (create/stream, `.subagents`, `.artifacts`, `.items`, `.events`, `.traces`, `.turns`), `environments` (`.files`, `.templates`), `vaults` (`.credentials`), `automations` (`.invocations`) — see [08-beta-agents-chatkit](08-beta-agents-chatkit.md)
- **Responses** (`client.beta.responses`) — `input_items.list(response_id)`, `input_tokens.count()`
- **ChatKit** (`client.beta.chatkit`) — `sessions` (`create`, `cancel`), `threads` (`retrieve`, `list`, `delete`, `list_items`); types in `openai.types.beta.chatkit`
- **Assistants** (`client.beta.assistants`) — assistants CRUD, `.files`
- **Threads** (`client.beta.threads`) — `create`, `retrieve`, `update`, `delete`, `runs` (create/retrieve/list/submit_tool_outputs/cancel/delete + `.stream()`/`*_poll()` helpers, `.steps`), `messages` (create/retrieve/list/update/delete, `.content`); see [03-streaming-parsing](03-streaming-parsing.md)
- **Realtime** (`client.beta.realtime`) — retained interface: `sessions.create` (POST `/realtime/sessions`), `transcription_sessions.create`; does not exchange workload-identity tokens or sign Bedrock requests — supply `Authorization` headers yourself

## Type imports

```python
from openai.types import (
    AllModels,
    ChatModel,
    ComparisonFilter,
    CompoundFilter,
    Decision,
    DecisionInputImageParam,
    DecisionInputMessageParam,
    DecisionInputPartUnionParam,
    DecisionInputTextParam,
    DecisionPromptCacheBreakpointParam,
    ErrorObject,
    FunctionDefinition,
    FunctionParameters,
    Metadata,
    OAuthErrorCode,
    Reasoning,
    ReasoningEffort,
    ResponseFormatJSONObject,
    ResponseFormatJSONSchema,
    ResponseFormatText,
    ResponseFormatTextGrammar,
    ResponseFormatTextPython,
    ResponsesModel,
)
```

Per-resource types live under `openai.types` (e.g., `openai.types.beta`, `openai.types.chat`, `openai.types.beta.realtime`), mirroring the resource tree.

## Pagination

List endpoints return auto-paginating iterators; `.has_next_page()`, `.next_page_info()`, `.get_next_page()` for manual control, or read `.data` and `.after` directly.

## Response objects

All object responses expose `.to_dict()`, `.to_json()`, `.model_fields_set`, `.model_extra` (Pydantic), plus the public `_request_id` property from the `x-request-id` header.
