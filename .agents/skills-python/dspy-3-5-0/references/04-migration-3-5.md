# Migrating to DSPy 3.5.0

Condensed from the official "Upgrading from DSPy 3.4.1 to 3.5" guide. Headline: **re-evaluate optimized programs** — prompts, defaults, and integration APIs changed even when your signature stays the same.

## Changed defaults

### XML is the default adapter

Default is now `XMLAdapter(use_native_function_calling=True)`, not `ChatAdapter`. Prompts, demonstrations, output instructions, and parsing change with the same signature. Re-evaluate quality and rebuild format-dependent fixtures. To retain chat field delimiters, configure `dspy.ChatAdapter()` explicitly (this does not undo the other changes). Explicit `dspy.XMLAdapter()` still defaults native function calling **off**.

Scalar values are literal text, not XML-escaped. `<value/>` means null for a nullable field; `<value></value>` means empty string. Prefer concrete annotations over ambiguous `Any` or string/container unions.

### Reasoning and explicit plans

CoT/RLM prefer native reasoning; the fallback requests a short plan. `reasoning` is now `dspy.Reasoning` or `None`, not always a string — update string-based metrics and feedback consumers. Opt into an explicit text field with `dspy.ChainOfThought(sig, rationale_field_type=str)` (this opts into text, not the old step-by-step prompt). Re-evaluate saved demos and reasoning-dependent optimization.

### API routing defaults to auto

`model_type` defaults to `"auto"`, selecting Responses for OpenAI/Azure — even with `engine="litellm"` (engine and API-family choices are independent). Pin a Chat-only route:

```python
lm = dspy.LM("openai/gpt-4o", model_type="chat")
```

Saved explicit `"chat"` stays Chat. Auto string calls return lists of strings; explicit `"responses"` retains its dictionary convention. Routing is chosen before inference, not retried through another backend after a provider failure.

## Removed APIs

| Removed | Use instead |
|---|---|
| `lm(messages=...)`, `BaseLM.forward`/`aforward`, `LegacyEngine`/`AsyncLegacyEngine`, `complete_legacy`, legacy LM response hooks | Canonical `Request`/`Response` engines (bundled lm15) |
| `Tool.format_as_litellm_function_call()` | `Tool.as_function_tool()` |
| `CodeAct`, `ProgramOfThought` | Rebuild with `RLM` and re-optimize; no compatibility alias for old saved programs |
| `Image.from_file()`, `Audio.from_file()` | `from_path()` |
| `Image.from_PIL()` | `Image(pil_image)` |
| Image constructor `download`/`verify` options | Explicit `from_path()` / `from_url()` |
| Experimental `TypeSafe` client/module/extra | `dspy.LM("typesafe:jev-latest", ...)` |
| Bundled lm15 callable-tool derivation helpers (`tool`, `derive_tool`, ...) | `FunctionTool` schemas plus callable execution in your application; `dspy.Tool` remains available |

Deprecated (removed in 3.6): `ReActV2` (use `dspy.ReAct`), `TwoStepAdapter` (replace with `JSONAdapter()` or `XMLAdapter()` and re-evaluate the former extraction-LM pipeline).

## ReAct migration

`dspy.ReAct` now uses structured History and a typed `submit` tool, not a trajectory dictionary plus extractor:

```python
# Before (3.4)                       # After (3.5)
trace = result.trajectory            messages = result.history.messages
                                     termination = result.termination_reason
```

Recompile old optimized agents. Multiple tools run sequentially per turn; `max_iters` counts turns, not calls. Failed final submission raises; automatic trajectory truncation is gone. Avoid conflicting names: inputs `history`, `tools`, `turn_budget`; outputs `history`, `termination_reason`; a tool named `submit`.

## RLM migration

Ordered History replaces flat action context; re-evaluate saved internal predictors and prompt fixtures. Continue conversations with returned History:

```python
saved = result.history.model_dump_json()
history = dspy.History.model_validate_json(saved)
result = rlm(question="What changes next?", history=history)
```

History replays conversation evidence but does **not** restore live Python variables. Reserved names: `history`, `repl_entry`, `variables_info`, `iteration` (plus input `history_processor`). Input History is not mutated.

## Dependencies and embeddings

- LiteLLM and the OpenAI SDK are optional. Install `dspy[litellm]` for compatibility routes or `dspy[openai]` for SDK-dependent features.
- Hosted embeddings: install `dspy[numpy,openai]`. The Embedder uses the OpenAI SDK for OpenAI/Azure/compatible endpoints; other protocols need a callable. Installing LiteLLM does not restore embedding routing. Preserve model, dimensions, normalization, and query/document modes when keeping an index.

## Caches regenerate and load restrictively

- Ordinary old entries and typed v1 records miss under canonical v2 caches — budget recomputation.
- Restricted disk loading is the default: unlisted custom types and old NumPy pickles regenerate. Plain arrays use data-only storage; object arrays/subclasses are not persisted in restricted mode. Keep restrictions enabled; allow only trusted `safe_types`.
- LM credentials/endpoints still do not partition cache keys — separate cache/rollout identities when results depend on them. Sync/async caches remain separate.

## Candidates and accounting

- `n` candidates use sequential single-response calls (seed + candidate index) on every backend; budget repeated input tokens. Adapter candidates cache independently; direct-string `n` remains grouped, without partial caching on failure.
- Canonical Usage totals include cached/tool-use input and reasoning/audio output — don't double-count.
- `num_retries=0` disables LM retries, not adapter fallback: Chat/XML can make an extra JSON-format call after a parse failure. Set `use_json_adapter_fallback=False` for strict call budgets.

## Save/load restrictions

State-only saves to `.json` (default, diff-friendly) or `.pkl`; full-program mode is `save(path_dir/, save_program=True)` → `program.pkl` + `metadata.json`, loaded with `dspy.load(path)`. Pickle loads require `allow_pickle=True`. `api_base`/`base_url`/`model_list` are stripped on load unless `allow_unsafe_lm_state=True`. API keys are never serialized. `load_state` is transactional (deep-copy trial first). Callbacks and history are excluded from saved state. Version mismatches warn, don't block. `modules_to_serialize=[...]` embeds user classes by value in full-program pickles.

## Other 3.5 changes worth knowing

- `metric_threshold=0` accepts scores ≥ 0; use `None` for metric truthiness.
- Bundled lm15 moves from 1.0.0rc3 to patched 2.2.0: set explicit Claude output caps and SSE limits where needed (omitted caps increase; SSE caps become unbounded). Review structured `Response.text`, stricter errors/schema/options, and changed subscription/Vertex credential resolution.
- Install constraints: base `certifi>=2026.10.19`; GEPA `>=0.1.4,<0.2.0`.
- Custom engines implement `complete(Request) -> Response` (or async); there is no new `generate()` API. Import canonical types from bundled `dspy.lm15`, not a separately installed lm15 package. `Adapter.format()` returns `dspy.adapters.Prompt`, not OpenAI message dicts.
