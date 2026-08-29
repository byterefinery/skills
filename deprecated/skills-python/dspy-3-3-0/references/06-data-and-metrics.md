# Data and Metrics

## Example objects

`dspy.Example` is the core data type (a dict-like with `.field` access and input-key tracking). Modules return `Prediction`, a subclass of `Example`.

```python
qa_pair = dspy.Example(question="This is a question?", answer="This is an answer.")
qa_pair.question            # "This is a question?"
qa_pair.with_inputs("question")          # mark which fields are inputs (rest are labels/metadata)
article.inputs()            # Example with input keys only
article.labels()            # Example with non-input keys only
```

Trainsets are lists of Examples:

```python
trainset = [dspy.Example(report="LONG REPORT 1", summary="short summary 1") for ...]
```

Built-in datasets (HotPotQA, Banking77, etc.) and `dspy.datasets.DataLoader` (HuggingFace, CSV/JSON/parquet) also produce Examples.

**Rule:** `with_inputs` controls what feeds the module — accidentally marking a label as an input leaks the answer into the prompt.

## Metric contract

A metric is a Python function:

```python
def metric(example, pred, trace=None) -> float | int | bool: ...
```

- `example` — the Example from your train/dev/test set (access `example.answer` etc.)
- `pred` — the program's `Prediction`
- `trace` — `None` during plain evaluation/scoring; a list of (module, prediction) steps during **compilation/bootstrapping**

**Dual-mode semantics** — the standard pattern:

```python
def validate_context_and_answer(example, pred, trace=None):
    answer_match = example.answer.lower() == pred.answer.lower()
    context_match = any(pred.answer.lower() in c for c in pred.context)

    if trace is None:        # evaluation / optimization scoring
        return (answer_match + context_match) / 2.0
    return answer_match and context_match    # strict gate when bootstrapping demos
```

With a trace you can validate **intermediate steps** (e.g., inspect generated search queries in a multi-hop program) — something plain evaluation can't see.

Built-in helpers: `dspy.evaluate.metrics.answer_exact_match`, `dspy.evaluate.metrics.answer_passage_match`, `dspy.evaluate.answer_exact_match_str(a, b, frac=0.8)`.

## AI-feedback metrics

For long-form outputs, make the metric a small DSPy program using LM judgment:

```python
class Assess(dspy.Signature):
    """Assess the quality of a tweet along the specified dimension."""

    assessed_text = dspy.InputField()
    assessment_question = dspy.InputField()
    assessment_answer: bool = dspy.OutputField()

def metric(gold, pred, trace=None):
    tweet = pred.output
    correct_q = f"The text should answer `{gold.question}` with `{gold.answer}`. Does it contain this answer?"
    correct = dspy.Predict(Assess)(assessed_text=tweet, assessment_question=correct).assessment_answer
    engaging = dspy.Predict(Assess)(assessed_text=tweet,
                                    assessment_question="Does the assessed text make for a self-contained, engaging tweet?").assessment_answer
    score = (correct + engaging) if correct and len(tweet) <= 280 else 0
    if trace is not None:
        return score >= 2
    return score / 2.0
```

If the metric is itself a DSPy program, you can compile the metric against its own metric — usually easy since metric outputs are simple values.

## GEPA-style feedback metrics

`dspy.GEPA` (and friends) accept metrics returning a `dspy.Prediction` with a `score` and optional textual `feedback`:

```python
def haiku_score_gepa(example, prediction, trace=None, pred_name=None, pred_trace=None):
    text = prediction.haiku.lower()
    if example.season.strip().lower() in text:
        return dspy.Prediction(score=0.0, feedback="Don't reference the input season verbatim.")
    return dspy.Prediction(score=1.0, feedback=None)
```

The feedback is shown to the instruction-writing LM during reflection — that's where GEPA outperforms score-only optimizers.

## Evaluate

```python
from dspy.evaluate import Evaluate

evaluator = Evaluate(devset=devset, num_threads=4, display_progress=True, display_table=5)
score = evaluator(program, metric=validate_answer)   # float in [0, 1]
```

A manual loop works too:

```python
scores = [metric(x, program(**x.inputs())) for x in devset]
```

## Data strategy

- ~20 dev examples is a useful start; ~200 goes a long way.
- Labels are only needed for the **final** output — never for intermediate steps (bootstrapping generates those).
- Many metrics work with inputs alone (no labels) — e.g., format/quality checks.
- Prefer permissively-licensed adjacent datasets (HuggingFace, StackExchange); otherwise hand-label a few or collect from a demo.
