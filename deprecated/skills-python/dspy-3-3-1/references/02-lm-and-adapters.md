# LM and adapters

## dspy.LM

`dspy.LM` wraps LiteLLM, so any of its dozens of providers work with the `provider/model` id form. Authentication is via env vars or constructor kwargs.

```python
lm = dspy.LM("openai/gpt-4o-mini")                                   # OPENAI_API_KEY
lm = dspy.LM("anthropic/claude-sonnet-4-5-20250929", api_key="...")  # or ANTHROPIC_API_KEY
lm = dspy.LM("gemini/gemini-2.5-pro-preview-03-25")                  # GEMINI_API_KEY
dspy.configure(lm=lm)
```

### Vertex AI (GCP)

Use the `vertex_ai/` prefix, not `gemini/` (which routes to the Gemini API and wants an API key). Use `vertex_project`/`vertex_location` kwargs — parameters without the `vertex_` prefix are silently ignored.

```python
lm = dspy.LM("vertex_ai/gemini-2.0-flash",
             vertex_credentials=json.dumps(json.load(open("service_account.json"))),
             vertex_project="my-project", vertex_location="us-central1")
```

### Local models

- **SGLang server** — connect as an OpenAI-compatible endpoint: `dspy.LM("openai/<model>", api_base="http://localhost:7501/v1", api_key="", model_type="chat")`.
- **Ollama** — `dspy.LM("ollama_chat/llama3.2", api_base="http://localhost:11434", api_key="")`.
- Any OpenAI-compatible endpoint works with the `openai/` prefix plus `api_base`/`api_key`.

### Responses API

For models that expose a `responses` endpoint (e.g., OpenAI reasoning models), set `model_type="responses"` when constructing the `dspy.LM`.

### Direct calls and history

```python
lm("Say this is a test!", temperature=0.7)        # -> ['This is a test!']
lm(messages=[{"role": "user", "content": "..."}])

lm.history[-1].keys()
# prompt, messages, kwargs, response, outputs, usage, cost, timestamp, uuid, model, ...
```

### Caching and rollouts

LMs are cached by default — identical calls replay the same output. Disable with `cache=False`. To force a fresh request while keeping caching for future calls, pass a unique `rollout_id` *and* a non-zero `temperature` (both are hashed into the cache key; changing only `rollout_id` at `temperature=0` changes nothing). The ID is recorded in `lm.history`.

### Error hierarchy

`dspy.LM` wraps provider/LiteLLM failures in structured exceptions under `dspy.LMError`: `LMAuthError`, `LMRateLimitError` (exposes `retry_after`), `ContextWindowExceededError`, `LMTimeoutError`, `LMProviderError`, `LMServerError`, `LMUnexpectedError`, … All carry a stable `code`; many also expose `model`, `provider`, `status`, `request_id`. Use `dspy.is_retryable_lm_error(e)` to decide whether to back off. Catch `dspy.LMError` broadly, specific subclasses for targeted handling (e.g., shrink the prompt on `ContextWindowExceededError`).

### Multiple LMs

```python
dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))          # global
with dspy.context(lm=dspy.LM("openai/gpt-3.5-turbo")):     # scoped; both are thread-safe
    ...
```

Custom LMs subclass `dspy.BaseLM` (implement `forward`; override `dump_state`/`load_state` and `copy` when you hold extra state). Saved programs serialize LMs via `dump_state`; loading a state that references a custom LM class needs `allow_unsafe_lm_state=True` (trusted files only).

## Adapters

The adapter translates signature + inputs + demos into LM messages, and parses responses back into `dspy.Prediction`. Flow: `Predict.__call__` → `adapter.format()` → `dspy.LM` → `adapter.parse()` → `Prediction`.

Configure globally with `dspy.configure(adapter=dspy.JSONAdapter())` or scoped with `dspy.context(adapter=...)`. The default is `dspy.ChatAdapter`.

### ChatAdapter (default)

Fields are wrapped in `[[ ## field_name ## ]]` markers; non-primitive outputs include their JSON schema. If parsing fails it automatically retries with `JSONAdapter`. Works with every model, but small models may not follow the format, and the boilerplate output tokens add latency.

### JSONAdapter

Prompts the LM for a JSON object of the output fields; uses the provider's native `response_format` when available. Leaner and lower-latency; best for models with structured-output support (weaker on small open models).

### Inspecting prompts

```python
adapter = dspy.ChatAdapter()
adapter.format(signature, demos, inputs)               # full message list
adapter.format_system_message(signature)                # just the system prompt
dspy.inspect_history(n=1)                               # print last LM interaction
```
