# Browser and Computer Tool Runners (v3.60.0)

The SDK ships **local tool runners**: `BrowserToolset` turns a supplied driver's methods into Responses function tools (it does not add a native browser tool type — the model must support function tools). Screenshots go back as native `input_image` parts in `function_call_output` with an `input_text` state report. The SDK does not install a browser, access profiles, or manage driver sessions — isolation, cleanup, and policy stay in your application.

Imports:

```python
from openai import AsyncOpenAI, ComputerToolset, AsyncComputerToolset, ComputerDriver, AsyncComputerDriver
from openai.lib.browser import AsyncBrowserToolset, BrowserToolset, BrowserError, BrowserState, TabInput, BrowserReadV1
from openai.lib.responses_tool_runner import AsyncResponsesToolRunner, ResponsesToolRunner, RegisteredFunction, AsyncRegisteredFunction
from openai.lib.decisions_tool_runner import AsyncDecisionsToolRunner, DecisionsToolRunner, DecisionObservation, AsyncDecisionCandidate
```

## BrowserDriver contract

A driver implements `state() -> BrowserState` — `tabs` with string `id`, `title`, `url`, Boolean `active`; IDs unique, exactly one active when tabs exist. The SDK provides `browser_list_tabs` from state by default and registers only the named methods the driver implements:

| Driver method | Typed argument | Result |
| --- | --- | --- |
| `navigate` | `NavigateInput`: url, tab_id | string or None |
| `read_page` | `ReadPageInput`: filter ("all"/"interactive"), tab_id | string, `BrowserReadV1` or None |
| `get_page_text` | `TabInput`: tab_id | string, `BrowserReadV1` or None |
| `find` | `FindInput`: query, tab_id | string, `BrowserReadV1` or None |
| `click`, `hover`, `scroll_to` | `ClickInput`: target, tab_id | string or None |
| `type` | `TypeInput`: target, text, tab_id | string or None |
| `key` | `KeyInput`: keys (list), tab_id | string or None |
| `scroll` | `ScrollInput`: direction, amount, tab_id | string or None |
| `wait_for` | `WaitForInput`: text (≤256 bytes normalized), timeout_ms (1–30000), tab_id | string or None |
| `select_option` | `SelectOptionInput`: target, values (list), tab_id | string or None |
| `screenshot` | `TabInput`: tab_id | Responses `input_image` dict |
| `zoom` | `ZoomInput`: tab_id, region `[left, top, right, bottom]` | Responses `input_image` dict |
| `new_tab` | `NewTabInput`: url (null = blank page) | string or None |
| `switch_tab`, `close_tab` | `TabInput`: tab_id (string required) | string or None |

All fields are required in tool calls; most `tab_id` fields accept null for the active tab. History navigation is requested as `back`/`forward`/reload through the URL policy. Optional `cancelled` keyword-only parameter is supported on every driver method and on confirm/url-policy callbacks (passed only when declared).

- **Member selection** — `members=["read_page", "screenshot"]` exposes only those (empty list = no methods); `additional_members=[...]` adds opt-in methods to the defaults (mutually exclusive with `members`). `DEFAULT_BROWSER_MEMBERS` / `BROWSER_MEMBERS` export the vocabulary.
- **Opt-in pointer input** (off by default): `click_at`, `hover_at`, `set_checked`, `drag_path`, `hold_keys`, `read_page_scoped` — the mutators require `confirm` and coordinates are CSS-viewport integers; `read_page_scoped` returns `BrowserScopedReadV1` (adds `scopes`).
- **Opt-in diagnostics/scripts/files** (off by default, each requires `confirm`): `read_diagnostics` (console/network, limit 1–100), `run_script` (page-privilege JS, timeout 1–30000 ms), `upload_file` / `download_file` (caller-issued `grant_id` only, returns `BrowserFileOutcome` with `version`/`status`/`effect`/`cleanup`; only `completed` yields `ok: true`).
- **Structured reads** — the three read methods may return `BrowserReadV1`: `{"version": 1, "text": ..., "elements": [{"ref", "role", "label", ...}], "omitted": [...]}`. Roles: `button`, `textbox`, `combobox`, `checkbox`, `radio`, `slider`, `listbox`; refs/labels ≤256 bytes, values ≤512; `get_page_text` must return empty `elements`.
- **Forms** — drivers may implement `type` (literal field replacement), `click` (current control ref), `select_option`; checkbox/radio may report `checked`, listbox options `selected`. Drivers own field privacy — never expose password/file/private values.
- **Errors** — raise `BrowserError("...")` with your own safe-to-share message for expected failures; other driver exceptions produce a fixed error message. Invalid state reports stop the run.
- **Type protocols** — `BrowserDriver` (state-only), `BrowserReadDriver`, `BrowserNavigationDriver`, `BrowserClickDriver`, `BrowserScreenshotDriver` (+ `Async` prefixes); structural implementations work, no inheritance needed.

## Confirmation and URL policy

If a driver implements any state-changing method, construction requires `confirm(ctx)` (clicks, typing, keyboard, scroll, selection, hover, tab changes, navigation). Navigation/new-tab additionally require `url_policy(ctx, url)`. Both must return exactly `True` to proceed (async variants for async toolsets). `confirm_reads=[...]` extends confirmation to selected read members (`BrowserReadConfirmContext` with `phase="before_read"`). For other operations `BrowserConfirmContext` carries `call_id`, `member`, `arguments`, and a copy of current `state` — a prior observation, not a lock; bind consent to a specific target at execution time when needed. The URL policy is the first line of defense, but the driver must still enforce which domains the browser can reach (redirects, popups, subresources, credential isolation). Treat page content as untrusted.

## ComputerDriver

Implement `screenshot()` (dimensions must match the display used for input coordinates) plus the input methods you need (`click`, `move`, `type`, `keypress`, `scroll`). Wrap in `ComputerToolset` / `AsyncComputerToolset` with a confirmation callback. The registered computer defaults to `{"type": "computer"}` in the mixed runner; `approve_safety_checks` and `before_action` callbacks are passed to the runner as needed (optional `cancelled` keyword supported). Run computer actions in an isolated environment with limited network access. Example: `examples/computer-desktop/` (isolated desktop).

## ResponsesToolRunner

```python
runner = AsyncResponsesToolRunner(browser=browser, computer=computer, functions=[registered])
response = await runner.run(client, params, max_steps=5)
```

- `params` is the Responses request body; `max_steps` counts Responses requests (if the last request still calls a local tool, the runner stops before that action).
- `functions` are `RegisteredFunction` / `AsyncRegisteredFunction` (tool schema + `execute` callable); `from_tool(openai.pydantic_responses_function_tool(Model), execute=...)` validates and parses typed args. Executors receive the decoded JSON object, return a string or Responses function-output content list. Names must be unique and not collide with enabled browser tools.
- **Streaming** — `run(client, params, stream=True, on_event=cb)`; by default waits for the completed response. `eager=True` starts a call when its completed output-item event arrives (an action may finish before a later stream failure — it cannot be undone). The runner never repeats a completed output item.
- **Cancellation** — `cancelled` sync predicate checked before/after dispatch and between stream events; keep it true after requesting a stop. Task cancellation propagates as `ToolRunnerCancelledError`.
- **Errors** — `ToolRunnerError.attempted_call_ids` includes an action that may have changed state before throwing; `completed_call_ids` means the SDK built an output (may include a refused/skipped action). Inspect both before retrying; the runner never retries application actions.
- **`tool_choice`** — preserved for every request, but a choice that always requires a local tool is rejected (the run could never finish): use `auto` or `responses.create` for a single forced request.
- **Image generation** — the runner needs stored responses to continue; it rejects `store=False` with `image_generation`.
- **MCP** — `approve_mcp(request)` callback (returns exactly True/False); requests declaring MCP tools disable automatic SDK retries; with a ledger, checkpoints cannot resume an in-flight request (the server may have applied an effect).
- **`early_execution`** (construction) limits which tools may run before full response inspection; only applies with `stream` + `eager`. `before_early_call(call)` hook returns `"execute"`/`"defer"`.
- **Independent eager functions** — `RegisteredFunction(..., independent=True)` + `max_concurrent_calls=N` (default 2) overlap stateless function calls in local-only eager runs without a ledger.
- **`context_budget`** (per invocation) bounds the next API input: `{"max_input_bytes": N, "max_input_images": N, "keep_recent_screenshots": 1, "compact": policy}`. The policy receives a `ContextBudgetSnapshot` copy and returns a `ContextBudgetDecision` (`drop_call_ids`, `summary`); the SDK always keeps messages, reasoning, latest browser state, and latest computer pair, and adds a receipt for each omitted call. Incompatible with nonempty `context_management` compaction; budget mode requires plain native request data.
- **Iterative control** — `iterate()` pauses on a non-final `ResponsesRunnerTurn`; `turn.append_user_text(...)` adds a user message before advancing. `previous_response_id`, `conversation`, `background`, `params.stream` are rejected — choose streaming on `run()`.
- **Diagnostics** — `on_diagnostic=callback` receives `ToolDiagnostic` events (`api`, `stage`, `reason`, `duration_ms`, `call_id`, `member`, `usage`); no raw args, page text, URLs, screenshots, credentials, or exception text.
- Both runners and both toolsets expose `close()` — stops new calls, returns `{"status": "draining"}` while a call is active, else `{"status": "closed"}`. The helper never closes a caller-owned driver.

## DecisionsToolRunner

Use when your application can enumerate every available action — Decisions selects from your descriptions (it does not generate browser calls or authorize actions):

```python
result = await AsyncDecisionsToolRunner(observe=observe, candidates=candidates, verify=verify).run(
    client, {"model": model, "input": task}, max_steps=8
)
```

- `observe()` returns text or a Decisions iterable of `input_text` / inline `input_image` parts (no external URLs or file IDs).
- `candidates(observation)` returns unique-ID/description candidates; exactly one must be `done: True` with no executor; otherwise 2–255 candidates each with a callable executor.
- Only `verify()` returning exactly `True` on a fresh observation produces `status="verified"`; no verifier → `"unverified"`; model refusal → `"refused"`.
- `max_steps` counts actual Decisions requests; an action selected on the final request does not run. Result carries `decisions`, `attempted_candidate_ids`, `completed_candidate_ids`; `DecisionsToolRunnerError` carries ID evidence and a fixed `reason`.
- Run parameters are `model`, task string `input`, optional `safety_identifier`; Responses flags and streaming are rejected. Decisions errors never fall back to Responses automatically.

## Mixing and examples

Register ordinary functions alongside browser/computer in one runner (`AsyncRegisteredFunction(tool={...}, execute=...)`). `params.tools` also accepts web search, file search, code interpreter, image generation, and MCP declarations, or one computer declaration. A failed/unfinished server result stops further local effects. Examples: `examples/browser/` (Playwright read-only reader), `examples/browser-use-demo/` (Fieldwork reservation form), `examples/computer-desktop/` (isolated desktop). Provider connection/ownership rules: `docs/browser-providers.md` in the repo.
