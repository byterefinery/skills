# Optimization — DSPy 3.5.0

## Choosing an optimizer

Every optimizer tunes one or more of: **instructions** (signature docstring), **demos** (few-shot examples), or **weights** (finetuning). `.compile()` returns a new compiled copy; the original student is not mutated. Compiled sub-modules carry `_compiled=True` so later optimizers leave them alone — you can compose optimizers (e.g., compile one part with MIPROv2, then GEPA over the whole).

Decision axes:

- **Prompt-only vs finetune** — prompt-only works with any LM; finetune needs a tunable target model. Most teams start prompt-only and graduate to finetune only when it plateaus.
- **Demos vs instructions** — demo-tuning tends to overfit; instruction-tuning tends to generalize.
- **There is no LM-based auto-selection** — you choose the optimizer.

## Optimizer quick reference

| Optimizer | Tunes | Typical use |
|---|---|---|
| `LabeledFewShot(k)` | demos | instant baseline from labeled fields; no metric needed |
| `BootstrapFewShot(metric=..., max_bootstrapped_demos, max_labeled_demos, max_rounds)` | demos | run student on trainset, keep traces that pass the metric; supports `teacher_settings=dict(lm=...)` for a stronger teacher LM |
| `BootstrapFewShotWithRandomSearch(metric=..., num_candidate_programs, valset=...)` | demos | random search over demo sets with validation |
| `MIPROv2(metric=..., auto="light"|"medium"|"heavy")` | instructions + demos | Bayesian-ish search; `auto` scales the budget. `max_bootstrapped_demos=0, max_labeled_demos=0` for instructions-only (0-shot) |
| `COPRO(prompt_model=..., metric=..., breadth, depth)` | instructions | LM-proposed prompt exploration |
| `SIMBA(metric=..., max_steps, max_demos)` | instructions + demos | stochastic introspective mini-batch ascent |
| `GEPA` | instructions (and Flex code) | reflective optimization driven by metric feedback |
| `KNNFewShot(k, trainset, vectorizer=...)` | dynamic demos | retrieve nearest training examples at call time |
| `BootstrapFinetune(metric=..., target=..., epochs, ...)` | weights | fine-tunes a model from bootstrapped traces |
| `Ensemble(reduce_fn=dspy.majority)` | — | combine several compiled programs |

## GEPA in depth

GEPA (Genetic-Pareto) is the flagship reflective optimizer. Key mechanics:

- **The metric is the feedback channel** — return `dspy.Prediction(score=float, feedback="...")` so the reflection LM learns *why* a prediction failed, not just that it did. GEPA is the only optimizer that reads per-predictor `Prediction(score, feedback)`.
- **Reflection proposes, evaluation selects** — an instruction-writing LM rewrites instructions using accumulated feedback; candidates are evaluated on data and kept via a Pareto frontier (per-example scores); the aggregate score picks the winner.
- **Budget**: set exactly one of `auto`, `max_full_evals`, or `max_metric_calls`.
- Per-predictor feedback arrives through `pred_name` / `pred_trace` metric arguments; `skip_perfect_score=True` keeps reflection focused on failures; `use_merge=True` combines successful candidates; default component selection is round-robin across predictors.
- `detailed_results` is the audit trail of the run. The winner's instructions overwrite the student's signatures in the returned copy.
- **Reflection LM cost dominates** — use a cheaper `reflection_lm` if your eval LM is expensive, and budget accordingly.

Minimal GEPA metric:

```python
def my_metric(example, pred, trace=None, pred_name=None, pred_trace=None):
    if example.answer.lower() not in pred.answer.lower():
        return dspy.Prediction(score=0.0, feedback="Answer missing the expected fact.")
    return dspy.Prediction(score=1.0, feedback=None)
```

## Compile / save / evaluate loop

```python
from dspy.teleprompt import MIPROv2

teleprompter = MIPROv2(metric=my_metric, auto="light")
optimized = teleprompter.compile(program.deepcopy(), trainset=trainset,
                                 max_bootstrapped_demos=3, max_labeled_demos=4)
optimized.save("mipro_optimized.json")

evaluate(optimized, devset=devset[:])   # Evaluate(devset=..., metric=...) instance
```

Compile once, save, reload — optimizer cost amortizes across deployments. Note `metric_threshold=0` now accepts scores ≥ 0 (use `None` for truthiness checks).
