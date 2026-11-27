# Data, metrics, and evaluation

## dspy.Example

The core data type for train/dev/test sets — dict-like rows with attribute access. `Prediction` is a subclass of `Example` (module outputs).

```python
qa = dspy.Example(question="This is a question?", answer="This is an answer.")
qa.question

trainset = [dspy.Example(report=r, summary=s) for r, s in pairs]

# mark which fields are inputs to the program (the rest are labels/metadata)
qa.with_inputs("question")
qa.with_inputs("question", "hint")

article = dspy.Example(article="...", summary="...").with_inputs("article")
article.inputs()   # Example with only input fields
article.labels()   # Example with only non-input fields
```

Modules receive only input fields; unmarked fields (labels) are used by metrics/optimizers, never sent to the LM.

Built-in datasets live in `dspy.datasets` (e.g., `HotPotQA`, `GSM8K`) and load via `dspy.datasets.DataLoader` (e.g., `.from_huggingface(dataset_name=..., fields=..., input_keys=..., split=...)`).

## Metrics

A metric is a Python function `(example, pred, trace=None) -> score` (float, int, or bool; higher is better). It is used both for evaluation and by optimizers to select candidates.

```python
def validate_answer(example, pred, trace=None):
    return example.answer.lower() == pred.answer.lower()
```

### The `trace` convention

`trace` is `None` during plain evaluation and non-None while an optimizer runs (it then contains `(predictor, inputs, outputs)` for every LM call in the program). A common pattern — be strict when bootstrapping demos, fractional when scoring programs:

```python
def validate_context_and_answer(example, pred, trace=None):
    answer_match = example.answer.lower() == pred.answer.lower()
    context_match = any(pred.answer.lower() in c for c in pred.context)
    if trace is None:        # evaluation / optimization scoring
        return (answer_match + context_match) / 2.0
    return answer_match and context_match   # demo bootstrapping: strict
```

Built-ins: `dspy.evaluate.answer_exact_match`, `dspy.evaluate.answer_passage_match`, `dspy.evaluate.EM`, plus module-based metrics `dspy.SemanticF1` and `dspy.CompleteAndGrounded` (they themselves make LM calls, so a configured LM is needed).

### Using `trace` to check intermediate steps

```python
def validate_hops(example, pred, trace=None):
    hops = [example.question] + [outputs.query for *_, outputs in trace if "query" in outputs]
    if max([len(h) for h in hops]) > 100:
        return False
    return True
```

### AI feedback (LLM-as-judge) metrics

For long-form outputs, the metric should check several dimensions, typically with a small DSPy program:

```python
class Assess(dspy.Signature):
    """Assess the quality of a tweet along the specified dimension."""

    assessed_text = dspy.InputField()
    assessment_question = dspy.InputField()
    assessment_answer: bool = dspy.OutputField()

def metric(gold, pred, trace=None):
    tweet = pred.output
    correct = dspy.Predict(Assess)(assessed_text=tweet,
                                   assessment_question=f"The text should answer `{gold.question}` with `{gold.answer}`. Does it?")
    engaging = dspy.Predict(Assess)(assessed_text=tweet,
                                    assessment_question="Does the assessed text make for a self-contained, engaging tweet?")
    score = (int(correct.assessment_answer) + int(engaging.assessment_answer)) if len(tweet) <= 280 else 0
    if trace is not None:
        return score >= 2      # strict when bootstrapping
    return score / 2.0
```

### Program-as-metric

If your metric is itself a DSPy program, you can *compile the metric* against labeled examples — its output is a simple value, so its own metric is trivial to define. Iterate: evaluate, inspect bad outputs, tighten the metric.

## dspy.Evaluate

```python
evaluator = dspy.Evaluate(devset=valset, metric=validate_answer,
                          num_threads=8, display_progress=True, display_table=5)
result = evaluator(program)      # result.score, result.results
```

`Evaluate` supports parallel evaluation (`num_threads`), progress display, a table of sample I/O + scores (`display_table=N`), `max_errors`, `failure_score`, and `save_as_csv`/`save_as_json`. A manual loop works identically:

```python
scores = [metric(x, program(**x.inputs())) for x in devset]
```
