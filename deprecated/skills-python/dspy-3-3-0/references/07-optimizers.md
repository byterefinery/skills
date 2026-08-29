# Optimizers

An optimizer tunes a program's learnable parameters (instructions, few-shot demos, or LM weights) to maximize your metric. All share the same interface:

```python
optimizer = dspy.<Name>(metric=your_metric, **hyperparams)
optimized = optimizer.compile(program, trainset=trainset)
```

Inputs: your program (single module or composed `dspy.Module`), a metric, and a trainset of Examples (inputs alone suffice; labels help). Small data works — 5–10 examples can yield strong results.

## Available optimizers (3.3.0)

**Few-shot (demo synthesis):**
- `LabeledFewShot` — builds demos directly from labeled trainset examples (`k`, `trainset`).
- `BootstrapFewShot` — a `teacher` (defaults to your program) generates full multi-step demos, filtered by the metric. Params: `max_bootstrapped_demos`, `max_labeled_demos`.
- `BootstrapFewShotWithRandomSearch` — runs `BootstrapFewShot` `num_candidate_programs` times with randomized demo sets, keeps the best on a dev set.
- `KNNFewShot` — demos selected by k-nearest-neighbor similarity to the input at runtime.

**Instruction optimization:**
- `COPRO` — generates/refines per-step instructions, hill-climbs with the metric (`depth`).
- `MIPROv2` — optimizes instructions **and** demos jointly via Bayesian optimization over mini-batches. Budget presets `auto="light" | "medium" | "heavy"` (set trials and evals for you); or set `num_trials`, `max_bootstrapped_demos`, `max_labeled_demos`, `num_threads` manually.
- `GEPA` — reflective prompt evolution: the LM reflects on execution trajectories (and your metric's textual feedback) to propose new instructions; Pareto candidate selection and merge-based improvement. Params: `auto=`, `max_full_evals`, `max_metric_calls`, `reflection_minibatch_size`, `candidate_selection_strategy`, `reflection_lm`, `num_threads`, `use_wandb`, etc. Accepts feedback metrics (`dspy.Prediction(score=..., feedback=...)`).
- `SIMBA` — identifies high-variability hard examples, introspects failures, adds self-reflective rules/demos.

**Finetuning:**
- `BootstrapFinetune` — distills a prompted program into weight updates (e.g., trains a small model per step). Output program has the same steps but finetuned LMs.

**Transformations / meta:**
- `Ensemble` — combines multiple programs (full set or random subset) into one.
- `BetterTogether` — meta-optimizer sequencing prompt optimization and finetuning (e.g., prompt → weight → prompt).
- Also present: `BootstrapFewShotWithOptuna` (Optuna search, needs `dspy[optuna]`), `AvatarOptimizer`, `InferRules`.

## Choosing

- ~10 examples → `BootstrapFewShot`.
- 50+ examples → `BootstrapFewShotWithRandomSearch`.
- 0-shot instruction optimization only → `MIPROv2` (0-shot config).
- Larger budget (40+ trials, 200+ examples to avoid overfitting) → `MIPROv2` full.
- Want textual feedback to drive improvement → `GEPA`.
- Need a small/cheap/fast serving model → `BootstrapFinetune` (typically after prompt optimization on a large LM).

Optimizers compose — run `MIPROv2` then feed its output into `GEPA` or `BootstrapFinetune`; or ensemble the top candidates.

## Examples

```python
# ReAct agent + MIPROv2 (light budget)
from dspy.datasets import HotPotQA

dspy.configure(lm=dspy.LM('openai/gpt-4o-mini'))
trainset = [x.with_inputs('question') for x in HotPotQA(train_seed=2024, train_size=500).train]

react = dspy.ReAct("question -> answer", tools=[search])
tp = dspy.MIPROv2(metric=dspy.evaluate.answer_exact_match, auto="light", num_threads=24)
optimized_react = tp.compile(react, trainset=trainset)
```

```python
# GEPA with feedback metric
optimizer = dspy.GEPA(metric=haiku_score_gepa, auto="light", num_threads=8)
optimized = optimizer.compile(program, trainset=trainset)
```

```python
# Finetune a small model
optimizer = dspy.BootstrapFinetune(metric=lambda x, y, trace=None: x.label == y.label, num_threads=24)
optimized = optimizer.compile(classify, trainset=trainset)
```

## Cost guidance

A typical small run is on the order of **$2 and ~10 minutes**; costs range from cents to tens of dollars depending on LM, dataset size, and budget. Guard expensive runs with `auto="light"`, modest `trainset`, and `num_threads` matched to your rate limits.

## Saving output

`optimized.save(path.json)` writes a human-readable JSON of all parameters/steps — always save compiled programs. Reload pattern in [08-saving-loading-async](08-saving-loading-async.md).
