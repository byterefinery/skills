# Signatures, adapters, and modules — DSPy 3.5.0

## Signatures

Signatures are Pydantic-backed: `dspy.Signature` subclasses validate fields with Pydantic semantics. Two equivalent declaration styles exist (string `"a, b -> c"` or class-based); the class form adds a docstring (becomes the task instructions) and per-field `desc=` descriptions.

Key properties:

- **Field order is meaningful** — inputs then outputs, in declaration order.
- **The docstring becomes the instruction text** rendered into prompts; field descriptions are appended to each field's schema line.
- **Instructions live on the signature, not the module** — optimizers rewrite them there.
- **Signatures are immutable by deepcopy** — "mutating" a signature (e.g., `sig.with_instructions(...)`) returns a new object.
- **Types are declared in the signature but coerced at parse time** — the adapter/LM output is coerced to the declared type when the response is parsed.
- **Field names and descriptions are inert to optimizers** — compilation never renames fields or edits descriptions; choose them well up front.
- Custom types (your own Pydantic models) are resolved by walking the caller's stack frames at render time — define them in module scope, not inside `forward`, for reliable resolution.

Useful field type examples: `str`, `int`, `float`, `bool`, `list[str]`, `dict`, nested Pydantic models, `dspy.Image` / `dspy.Audio` media types. For nullable fields under the XML adapter, `<value/>` parses as null and `<value></value>` as empty string — prefer concrete annotations over ambiguous `Any` or string/container unions.

## Adapters (3.5)

The default adapter is now `XMLAdapter(use_native_function_calling=True)` (changed from `ChatAdapter` in 3.4). The adapter renders the signature + inputs into a prompt and parses the LM response back into typed fields.

- `dspy.XMLAdapter()` — explicit XML; defaults native function calling **off** unless you pass `use_native_function_calling=True`.
- `dspy.ChatAdapter()` — chat-style field delimiters; use explicitly to retain 3.4-style formatting (other 3.5 changes still apply).
- `dspy.JSONAdapter()` — JSON rendering/parsing; the fallback used after a parse failure unless disabled with `use_json_adapter_fallback=False`.
- Scalars are literal text in XML output, not XML-escaped — review custom completions/parsers if you had any.

## Built-in modules

| Module | Behavior |
|---|---|
| `dspy.Predict(sig)` | single LM call; the foundational module |
| `dspy.ChainOfThought(sig)` | reasoning then answer; `reasoning` is `dspy.Reasoning` or `None` in 3.5 (native reasoning preferred, fallback requests a short plan). Pass `rationale_field_type=str` to opt into an explicit text plan field |
| `dspy.ReAct(sig, tools=[...], max_iters=N)` | tool-using agent loop with structured `History` and typed `submit` (below) |
| `dspy.RLM(sig)` | sandboxed Python REPL reasoning; returns `result.history`; reserved names: `history`, `repl_entry`, `variables_info`, `iteration` (plus input `history_processor`) |
| `dspy.Retrieve(k=N)` | retrieval over the retriever set via `dspy.configure(rm=...)`; e.g. `dspy.ColBERTv2(url=...)`. Result has `.passages` |
| `dspy.Parallel(num_threads=N)` | run many `(module, example)` pairs concurrently |
| `dspy.BestOfN(module, N, reward_fn, threshold)` | sample N times (distinct rollout IDs, bypassing cache), return best by `reward_fn` or first passing `threshold` |
| `dspy.Refine(...)` | like BestOfN but feeds generated feedback into subsequent attempts; `fail_count` controls error tolerance |

## ReAct in 3.5

```python
agent = dspy.ReAct("question -> answer", tools=[lookup], max_iters=10)
result = agent(question="What is DSPy?")
# result.answer, result.history.messages, result.termination_reason
```

- The model submits typed outputs via a `submit` tool — no separate extraction pass (3.4's `finish` + extractor is gone).
- A turn may request multiple tool calls; they execute sequentially and each keeps its call ID.
- `max_iters` counts **turns**, not tool calls. If the model reaches it without submitting, ReAct makes one final submission attempt and raises if that fails.
- Continue conversations by passing the returned history: `agent(question=..., history=result.history)`. Native assistant/tool messages retain IDs, forming reusable prefixes for provider prompt caching.
- Reserved/conflicting names to avoid in your signature or tools: inputs `history`, `tools`, `turn_budget`; outputs `history`, `termination_reason`; a tool named `submit`.
- `dspy.ReActV2` is a deprecated compatibility subclass (removed in 3.6) — construct `dspy.ReAct` directly.

## RLM in 3.5

```python
rlm = dspy.RLM("question -> answer")
result = rlm(question="...")
# result.answer, result.history
```

- Ordered `History` replaces the flat action context from earlier versions; saved internal predictors and prompt fixtures change — re-evaluate saved RLM programs.
- Persist/restore history as JSON: `json.dumps(result.history.model_dump_json())` / `dspy.History.model_validate_json(saved)`. History replays conversation evidence but does **not** restore live Python variables.
- The public factory creates an interpreter per invocation and shuts it down afterward; input History is not mutated.

## Tools

Define tools as plain functions with type hints and docstrings:

```python
def search_web(query: str) -> str:
    """Search the web for information."""
    return ...

tool = dspy.Tool(search_web)   # or pass the bare function to tools=[...]
result = tool(query="Python programming")
```

- Schema and metadata are inferred from the signature/docstring; arguments are validated before execution.
- Adapters choose text vs native function-call formatting based on the adapter/LM capabilities.
- Structured `dspy.ToolCalls` / `ToolCallResults` objects retain call IDs, results, and continuations in serialized history.
- MCP tools can be imported into DSPy (see the docs' MCP tutorial); `Tool.as_function_tool()` is the 3.5 replacement for the removed `format_as_litellm_function_call()`.
