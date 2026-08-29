# Optimizers

An optimizer tunes a DSPy program's learnable parameters — the per-predictor **instructions**, the **few-shot demos**, and/or the LM **weights** — to maximize your metric. Optimizers were formerly called "teleprompters".

## Shared interface

```python
optimizer = dspy.SomeOptimizer(metric=my_metric, **hyperparameters)
compiled = optimizer.compile(program, trainset=trainset, valset=valset)
```

- `metric` — same shape as evaluation metrics (`(example, pred, trace=None)`; GEPA needs the 5-arg feedback form).
- `trainset` — `dspy.Example` list with inputs marked. Small is fine (5-50 examples often enough for few-shot methods).
- `.compile()` deep-copies the student (`reset_copy()`); the original is never mutated. It sets `_compiled=True` on the result so it is skipped when embedded in a larger program and re-optimized.

## Catalog

**Automatic few-shot learning** (tunes demos):

- `dspy.LabeledFewShot(k, trainset)` — random `k` labeled examples as demos.
- `dspy.BootstrapFewShot(metric, max_labeled_demos, max_bootstrapped_demos, teacher=...)` — runs the teacher program on labeled data and keeps metric-passing full trajectories as demos.
- `dspy.BootstrapFewShotWithRandomSearch(..., num_candidate_programs)` — repeated bootstrap + random search over demo sets, keeps the best.
- `dspy.KNNFewShot` — selects demos by k-nearest neighbors to the input.

**Instruction optimization** (rewrites natural-language instructions; 0-shot friendly):

- `dspy.COPRO(metric, max_bootstrapped_demos, verbose)` — coordinate-ascent hill climbing over generated instructions.
- `dspy.MIPROv2(metric, auto=..., num_trials=..., num_candidates=...)` — Bayesian search over instruction/demo combinations per module; `auto` presets `light`/`medium`/`heavy`.
- `dspy.SIMBA` — mini-batch sampling to find high-variability examples, then self-reflective rule generation.
- `dspy.GEPA` — reflective, feedback-driven evolutionary search; the pick for feedback-rich tasks (see [05-gepa-deep-dive](05-gepa-deep-dive.md)).

**Weight optimization**:

- `dspy.BootstrapFinetune(metric, ...)` — distills the program into fine-tuned model weights (needs a fine-tunable LM).

**Meta / transformations**:

- `dspy.BetterTogether` — sequences prompt optimization and fine-tuning (e.g., prompt → weight → prompt).
- `dspy.Ensemble` — combines several compiled programs into one (scales inference-time compute).

## Which one to use

- ~10 examples → `BootstrapFewShot`.
- 50+ examples → `BootstrapFewShotWithRandomSearch`.
- Want 0-shot / instructions only → `MIPROv2` configured for 0-shot.
- Long runs (40+ trials) with 200+ examples (to avoid overfitting) → `MIPROv2`.
- Feedback-rich task (you can explain *why* an output failed) → `GEPA`, usually with a stronger `reflection_lm` than the task model.
- Prompt-only methods work with any LM (closed-source included); finetune needs a tunable model.
- Instruction tuning tends to generalize better than demo tuning when the eval set is small or skewed; demo sets learned on 50 examples describe *those* 50 examples.
- Most teams start prompt-only and treat finetuning as the last lever.

## Cost and composition

A simple optimization run costs a few dollars and ~10 minutes; bigger runs reach tens of dollars. Optimizers compose: feed one optimizer's output into another, or into `BetterTogether`, or build a `dspy.Ensemble` of the top candidates. Compile once per program version, then serve the saved artifact — that is what amortizes the cost.

## Saving optimizer output

```python
compiled.save("program.json")                # plain-text JSON: parameters + steps
loaded = YourProgramClass()
loaded.load("program.json")
```

The file is human-readable — you can always inspect what instructions and demos the optimizer produced.
