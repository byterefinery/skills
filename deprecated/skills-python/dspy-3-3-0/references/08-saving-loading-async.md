# Saving, Loading, Async, Production

## Save modes

`.save(path)` has two modes:

```python
# State only — a .json file with learned instructions + few-shot demos (not structure)
optimized.save("haiku_bot.json")

# Whole program — a directory with the pickled module, structure and state
optimized.save("haiku_bot/", save_program=True)
```

State-only is the default choice: small, human-readable, diffable in version control. The JSON contains optimized instructions, demos, and signature metadata — **never** LM client config (API keys, provider, temperature). Reconfigure the LM after loading; the same checkpoint then targets whichever model you point it at.

Use `save_program=True` when the loader won't have your Python class definitions (shipping to another team, serving from a different repo). **Warning:** the directory contains executable Python — only load it from trusted sources.

## Reloading

```python
# Whole program — one call, no class definition needed
loaded = dspy.load("haiku_bot/")

# State only — re-instantiate, then apply the saved state
fresh = dspy.ReAct(HaikuBot, tools=[wikipedia_search, get_wikipedia_page])
fresh.load("haiku_bot.json")

# Custom LM state in saved programs requires trusted opt-in
program.load("program.json", allow_unsafe_lm_state=True)
```

## Async

- Modules expose `acall` for async invocation: `await react.acall(question=...)`.
- `dspy.asyncify(program)` / `dspy.syncify(coroutine)` convert programs across sync/async boundaries.
- Async tools: `await tool.acall(...)` is the recommended path; from sync code use `with dspy.context(allow_tool_async_sync_conversion=True)` so `tool(...)` works on async tools.
- `dspy.configure(async_max_workers=...)` controls the worker pool for async execution.

## Thread safety

`dspy.configure` and `dspy.context` are thread-safe for reads. But `dspy.configure` may only be called again from the thread/async task that first called it — other threads or tasks must use `dspy.context(...)`. Programs themselves are safe to share across threads.

## LM usage tracking

```python
dspy.configure(track_usage=True)
pred = program(question=...)
pred.get_lm_usage()
# {'openai/gpt-4o-mini': {'prompt_tokens': ..., 'completion_tokens': ..., 'total_tokens': ...}}
```

Cached responses return `{}` (no usage).

## Production notes

- **Observability** — MLflow tracing (OpenTelemetry-based) covers LM calls and module spans; `lm.callbacks` lets you hook before/after any request.
- **Reproducibility** — MLflow integration logs programs, metrics, configs, and environments.
- **Deployment** — DSPy programs deploy via MLflow Model Serving; the `save_program=True` directory form is what you serve when class definitions won't be available at the endpoint.
- **Caching** — the default in-memory/disk LM cache (`cache=True`) cuts cost on repeated inputs; `rollout_id` + non-zero temperature forces fresh requests.
- DSPy is in production at Shopify, Databricks, Dropbox, JetBlue, Moody's, Replit, AWS, Sephora, and others.

## Debugging checklist

1. `lm.inspect_history(n=1)` (or `program.inspect_history(n=1)`) — what did the adapter actually send?
2. `lm.history[-1]` — kwargs, usage, cost, raw response of the last call.
3. `resp.reasoning` — for `ChainOfThought`-style modules, the step before the answer.
4. Type-mismatch warnings — input values not matching declared signature types (warn only, not errors).
