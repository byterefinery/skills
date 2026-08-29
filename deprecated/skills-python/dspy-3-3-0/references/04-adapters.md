# Adapters

Adapters are the bridge between `dspy.Predict` and the LM. On each call: `Adapter.format()` converts signature + inputs + demos into multi-turn messages; `Adapter.parse()` converts the LM response back into a `dspy.Prediction`.

Configure globally or per-block:

```python
dspy.configure(adapter=dspy.ChatAdapter())        # default — works with all LMs
with dspy.context(adapter=dspy.JSONAdapter()): ...
```

If no adapter is set, each `dspy.Predict.__call__` defaults to `dspy.ChatAdapter`.

## ChatAdapter (default)

Field-based format using `[[ ## field_name ## ]]` markers. For non-primitive output fields, the field's JSON schema is embedded in the prompt so the response is parseable.

- **Universal compatibility** — works with all LMs, though small models may drift off-format.
- **Fallback protection** — on parse failure it automatically retries with `JSONAdapter`.
- **Cost** — more boilerplate output tokens than other adapters; avoid if you are latency-sensitive.
- Native function calling: `use_native_function_calling=False` by default (text-based parsing).

## JSONAdapter

Prompts the LM to return a plain JSON object with the output fields; leverages native `response_format` structured output for reliable parsing and lower latency.

- **Use when** the model natively supports structured output (OpenAI, Anthropic, Gemini, etc.).
- **Avoid when** the model doesn't (small open models on Ollama).
- Native function calling: `use_native_function_calling=True` by default.

## TwoStepAdapter

Splits a multi-output signature into per-field generation steps (one per output field), which helps weaker models that struggle to produce all fields at once.

## Other adapters

`dspy.XMLAdapter` (a `ChatAdapter` subclass using XML field markers) and `dspy.BAMLAdapter` (a `JSONAdapter` subclass) also exist; custom adapters subclass `dspy.Adapter` and implement `format()` / `parse()`.

## Inspecting formatted messages

```python
signature = dspy.Signature("question -> answer")

# All messages the adapter would send
dspy.ChatAdapter().format(signature, demos, inputs)

# Just the system message
dspy.ChatAdapter().format_system_message(signature)

# After a real call — the last conversation (method on the LM or module)
lm.inspect_history(n=1)
program.inspect_history(n=1)
```

## Native function calling

Adapters support the LM's built-in tool-calling API instead of text-parsed tool calls:

```python
dspy.configure(adapter=dspy.ChatAdapter(use_native_function_calling=True))
```

DSPy checks whether the LM actually supports function calling (LiteLLM capability check; custom `BaseLM`s can override `supports_function_calling`) and falls back to text parsing when it doesn't. Note native tool calling does **not** guarantee better quality than text-based.

## Choosing

- Default / robustness → `ChatAdapter`.
- Latency / native structured-output models → `JSONAdapter`.
- Weak models, many output fields → `TwoStepAdapter`.
