# API Surface (v3.19.2)

Generated from the OpenAI OpenAPI spec. Method signatures: `**params` TypedDicts in, Pydantic models out. The full per-endpoint reference in the repo is `api.md`. Below is the resource map — sync paths shown; `AsyncOpenAI` mirrors them with `await`.

## Core resources

| Resource | Key methods |
|---|---|
| `client.responses` | `create`, `retrieve` (with `stream`, `starting_after`), `delete`, `cancel`, `compact`, plus `.parse()` / `.stream()` helpers, `.connect()` (WebSocket), `.input_tokens.count()`, `.input_items.list()` |
| `client.chat.completions` | `create`, `retrieve`, `update`, `list`, `delete`, plus `.parse()` / `.stream()` helpers, `.messages.list()` |
| `client.completions` | `create` (legacy completions API) |
| `client.embeddings` | `create` |
| `client.files` | `create`, `retrieve`, `list`, `delete`, `content`, `retrieve_content`, `wait_for_processing` |
| `client.images` | `generate`, `edit`, `create_variation` |
| `client.audio.speech` | `create` (returns binary content; use `with_streaming_response` + `stream_to_file`) |
| `client.audio.transcriptions` | `create` |
| `client.audio.translations` | `create` |
| `client.moderations` | `create` |
| `client.models` | `retrieve`, `list`, `delete` |
| `client.content_provenance_checks` | `create` |
| `client.batches` | `create`, `retrieve`, `list`, `cancel` |
| `client.uploads` | `create`, `cancel`, `complete`, `.parts.create`, plus `upload_file_chunked()` convenience |
| `client.conversations` | `create`, `retrieve`, `update`, `delete`, `.items` (add/list items) |
| `client.videos` | `create` (+ `create_and_poll`), status checks |
| `client.containers` | create/retrieve/list/delete, `.files` (upload), `.content` |
| `client.skills` | create/retrieve/list, `.content`, `.versions` (create, list, `.content`) |
| `client.evals` | `create`, `retrieve`, `list`, `.runs` (create, retrieve, list, cancel, `.output_items`) |
| `client.webhooks` | `unwrap(payload, headers, *, secret)`, `verify_signature(payload, headers, *, secret, tolerance)` |
| `client.safety.alerts` / `client.safety.cases` | `retrieve` |
| `client.admin` | organization admin — `audit_logs`, `admin_api_keys`, `usage` (costs, completions, embeddings, images, audio, ...), `invites`, `users`, `groups`, `roles`, `data_retention`, `external_storage`, `spend_limit`, `spend_alerts`, `certificates`, `projects` (users, roles, service accounts, API keys, rate limits, model permissions, ...) |

## Fine-tuning and vector stores

- `client.fine_tuning.jobs` — `create`, `retrieve`, `list`, `cancel`, `list_events`, `pause`, `resume`, `.checkpoints.list()`; `client.fine_tuning.checkpoints.permissions` (create/retrieve/list/delete); `client.fine_tuning.alpha.graders` (`run`, `validate`)
- `client.vector_stores` — `create`, `retrieve`, `update`, `list`, `delete`, `search`; `.files` (`create`, `retrieve`, `update`, `list`, `delete`, `content`, `upload`, `poll`, `create_and_poll`, `upload_and_poll`); `.file_batches` (same pattern)

## Beta namespace

`client.beta.*` for APIs still marked beta:

- **Agents** — `client.beta.agents` (create/retrieve/update/list/delete), `.environments` (retrieve, `.files`, `.templates`), `.vaults` (create/retrieve/list/delete, `.credentials`), `.sessions` (create/retrieve/update/list/delete, `.items`, `.events` (create, `stream`), `.turns`, `.artifacts`, `.subagents` (items/turns))
- **Responses (beta)** — `client.beta.responses` mirrors `client.responses` plus `compact`, with `?beta=true` routing and extra tool types (computer use, shell, apply patch, MCP, file search, web search)
- **Assistants** — `client.beta.assistants` (CRUD)
- **Threads** — `client.beta.threads` (CRUD, `create_and_run` + poll/stream), `.runs` (create/retrieve/update/list/cancel/`submit_tool_outputs` + `*_and_poll`/`stream` variants, `.steps`), `.messages` (CRUD)
- **Realtime (beta)** — `client.beta.realtime.sessions`, `client.beta.realtime.transcription_sessions`
- **ChatKit** — `client.beta.chatkit.sessions` (create, cancel), `.threads` (retrieve, list, delete, `list_items`)

## WebSocket namespaces (see 06-realtime-live-websockets)

- `client.realtime` — `connect(model=...)` Realtime API WebSocket
- `client.live` — `connect()` Live API WebSocket
- `client.responses.connect()` — Responses-over-WebSocket with `ResponsesWebSocketSession` lanes

## Type imports

- Shared: `from openai.types import (Completion, ChatModel, Embedding, FileObject, Image, Model, Batch, Upload, Metadata, Reasoning, ReasoningEffort, ResponseFormatJSONObject, ResponseFormatText, ...)`
- Per-domain: `from openai.types.chat import ChatCompletion, ChatCompletionChunk, ...`; `from openai.types.audio import Transcription, ...`; `from openai.types.fine_tuning import FineTuningJob, ...`; `from openai.types.beta import ...` (agents/assistants/threads), `from openai.types.responses import ...`
- Param TypedDicts follow the pattern `XxxCreateParams` in the same module, e.g. `openai.types.chat.completion_create_params`.

## Response objects

- Pydantic models: `.to_dict()`, `.to_json()`, `.model_dump()`, field access with autocomplete.
- `response._request_id` — public; the `x-request-id` from the response header.
- `None` ambiguity: an explicitly-null and a missing field both read as `None`; check `'field' in response.model_fields_set`.
- Undocumented properties: `response.unknown_prop` or `response.model_extra`.
- List endpoints return page objects that are themselves iterable (auto-pagination): `.data`, `.has_next_page()`, `.next_page_info()`, `.get_next_page()`, cursor fields like `.after`.
