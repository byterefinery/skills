# Language Models

## dspy.LM

`dspy.LM` wraps LiteLLM, so any `provider/model` string works. Key constructor args: `model`, `model_type` (`"chat"`, `"text"`, `"responses"`), `temperature`, `max_tokens`, `cache` (default `True`), `num_retries` (default 3, exponential backoff), `callbacks`, plus pass-through kwargs (`api_key`, `api_base`, provider-specific options).

```python
import dspy

lm = dspy.LM("openai/gpt-4o-mini", api_key="sk-...")
dspy.configure(lm=lm)
```

### Providers

| Provider | Model string / auth |
|---|---|
| OpenAI | `openai/gpt-4o-mini`, `OPENAI_API_KEY` or `api_key=` |
| Anthropic | `anthropic/claude-sonnet-4-5-20250929`, `ANTHROPIC_API_KEY` |
| Gemini | `gemini/gemini-2.5-pro-preview-03-25`, `GEMINI_API_KEY` |
| Vertex AI | `vertex_ai/gemini-2.0-flash` + `vertex_credentials`/`vertex_project`/`vertex_location`, or `GOOGLE_APPLICATION_CREDENTIALS`/`VERTEXAI_PROJECT`/`VERTEXAI_LOCATION` env |
| Databricks | `databricks/<model>`, `DATABRICKS_API_KEY` + `DATABRICKS_API_BASE` |
| Ollama (local) | `ollama_chat/llama3.2`, `api_base='http://localhost:11434'`, `api_key=''` |
| SGLang (GPU server) | OpenAI-compatible — `openai/<model>`, `api_base="http://localhost:7501/v1"`, `model_type='chat'` |
| Azure | `azure/<deployment>` + `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION` env |

Any OpenAI-compatible endpoint: prefix `openai/` and pass `api_base` + `api_key`.

**Vertex gotcha:** use `vertex_ai/` prefix (not `gemini/` — that routes to the API-key Gemini endpoint) and `vertex_project`/`vertex_location` kwargs (bare `project`/`location` are silently ignored and LiteLLM falls back to defaults, possibly in the wrong region).

### Calling the LM directly

```python
lm("Say this is a test!", temperature=0.7)                      # => ['...']
lm(messages=[{"role": "user", "content": "..."}])               # => ['...']
```

### Caching and rollouts

- Caching is on by default; repeat calls return the same output. `cache=False` disables.
- To force a fresh request while keeping caching: pass a unique `rollout_id` **and** a non-zero `temperature`. The cache key hashes inputs + `rollout_id`. At `temperature=0`, changing only `rollout_id` changes nothing.
- `rollout_id` is forwarded to the module (`dspy.Predict(..., rollout_id=1)` sets a default; per-call `config={"rollout_id": 5}` overrides) and recorded in `lm.history`.

### History and debugging

Every `LM` keeps full history — inputs, outputs, token usage, cost, timestamp, uuid, model:

```python
len(lm.history)
lm.history[-1].keys()
# dict_keys(['prompt', 'messages', 'kwargs', 'response', 'outputs', 'usage',
#            'cost', 'timestamp', 'uuid', 'model', 'response_model', 'model_type'])
```

`dspy.inspect_history()` prints the last formatted conversation (system message, user turn, response) — the fastest way to see what the adapter actually sent.

### Error handling

DSPy wraps provider/LiteLLM failures in a structured hierarchy:

```python
try:
    answer = qa(question="...")
except dspy.ContextWindowExceededError:
    # shrink prompt, passages, or demos
    raise
except dspy.LMRateLimitError as e:
    print(f"rate limited by {e.provider}; retry after {e.retry_after}s")
except dspy.LMError as e:
    print(f"LM failed: code={e.code}, model={e.model}, request_id={e.request_id}")
```

Subclasses include `LMAuthError`, `LMBillingError`, `LMTimeoutError`, `LMRateLimitError`, `LMNotConfiguredError`, `LMUnexpectedError`, etc. All expose a stable `code`.

### Responses API

For OpenAI reasoning models or providers with a `responses` endpoint:

```python
dspy.configure(lm=dspy.LM("openai/gpt-5-mini", model_type="responses", temperature=1.0, max_tokens=16000))
```

Not all models/providers support it — check LiteLLM docs.

## configure vs context

```python
dspy.configure(lm=..., adapter=..., track_usage=True)   # process-wide; one owning thread/task

with dspy.context(lm=dspy.LM("openai/gpt-3.5-turbo")):   # scoped override, any thread/task
    result = qa(question="...")
```

`dspy.configure` may only be called again from the thread/async task that first called it — from elsewhere, `dspy.context` is the only safe option. Both are thread-safe for reads.

## Custom LMs

Subclass `dspy.BaseLM` and implement `forward`. Saved programs serialize each attached LM via `lm.dump_state()`/`load_state` — override both if your LM has extra state. Custom LM classes reload from their module-qualified path (must be importable at load time) and require trusted opt-in: `program.load("program.json", allow_unsafe_lm_state=True)`. `lm.copy(...)` shares provider clients by reference but isolates `history`, `callbacks`, and `kwargs` — override `copy()` if you add mutable state that shouldn't be shared.
