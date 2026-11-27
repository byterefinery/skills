# Data, evaluation, and runtime utilities — DSPy 3.5.0

## Examples and datasets

`dspy.Example` is a dict-like row. `with_inputs(...)` marks which fields are inputs (the rest are treated as labels/outputs):

```python
ex = dspy.Example(question="What is DSPy?", answer="A framework for LM programming").with_inputs("question")
```

Built-in datasets ship with DSPy (see the built-in-datasets docs page); custom data is just a list of `Example`s. Hidden fields can be copied with `.with_hidden(...)`-style helpers; Example copies retain hidden-only data.

## Metrics

A metric is a plain function `(example, pred, trace=None) -> float | bool`, or for GEPA `(example, pred, trace=None, pred_name=None, pred_trace=None) -> dspy.Prediction(score=..., feedback=...)`.

Patterns:

- **Exact/normalized match** — parse and compare (e.g., extract the last numeric token for math).
- **LLM-as-judge** — a `dspy.ChainOfThought` program with a judge signature (`context, question, answer -> factually_correct: bool`) used inside the metric.
- **Program-as-metric** — any DSPy program can serve as the scorer; use `trace` to inspect intermediate predictions when debugging optimization.

Built-in metrics (from `dspy.evaluate`): `answer_exact_match`, `answer_passage_match`, `SemanticF1`, `CompleteAndGrounded`.

## Evaluation

```python
from dspy.evaluate import Evaluate, EvaluationResult

evaluate = Evaluate(devset=devset, metric=my_metric, num_threads=8,
                    display_progress=True, display_table=5)
num_successful, num_total = evaluate(program)
```

`Evaluate` returns per-example `EvaluationResult`s when asked; use them to inspect failures. For optimizer runs, pass the same metric function — optimizers call it with the extra GEPA arguments supported where relevant.

## Usage tracking and costs

```python
dspy.configure(track_usage=True)
result = program(question="What is 2+2?")
print(result.get_lm_usage())   # token usage for the prediction
```

3.5 accounting: canonical `Usage` totals already include cached/tool-use input tokens and reasoning/audio output tokens — don't add those counters again. Low-level `InferencePricing.estimate` takes a `Usage`; unknown cost is `None`, not zero. `n` candidates use sequential single-response calls (seed + candidate index) on every backend — budget the repeated input tokens.

## Streaming and async

```python
import asyncio, dspy

predict = dspy.Predict("question -> answer")
stream_predict = dspy.streamify(
    predict,
    stream_listeners=[dspy.streaming.StreamListener(signature_field_name="answer")],
)

async def main():
    output_stream = stream_predict(question="Why did a chicken cross the kitchen?")
    async for chunk in output_stream:
        print(chunk)

asyncio.run(main())
```

- `dspy.asyncify(module)` wraps any module for async invocation.
- Note from the 3.5 migration notes: LiteLLM text/Responses calls inside `streamify` can complete without token chunks; use native Responses for token streaming.

## Caching and configuration utilities

- Caching is on by default (memory + disk). Configure with `dspy.configure_cache(enable_disk_cache=..., enable_memory_cache=...)`.
- Force fresh outputs: pass `config={"rollout_id": <unique>, "temperature": 1.0}` to a predictor call — bypasses the existing cache entry while caching the new result.
- `dspy.inspect_history(n=1)` shows the last formatted prompt and raw LM response.
- `dspy.configure(...)` sets process-wide defaults (lm, rm, track_usage); `dspy.context(...)` scopes overrides per thread/context manager.
