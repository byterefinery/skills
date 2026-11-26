# Optimizers (Teleprompters) — Full Reference

All optimizers follow the pattern: `optimizer.compile(student, trainset=..., valset=...)` → returns a new compiled module. The original is never mutated.

## Baseline (no or minimal LM cost)

### dspy.LabeledFewShot(k=16)
- Samples up to `k` labeled examples from trainset as demos per predictor
- No LM calls during compile (zero cost)
- Parameters: `k` (int), `sample` (bool, default True for random sampling)
- Use as honest baseline before reaching for heavier methods

### dspy.BootstrapFewShot(metric=None, metric_threshold=None, teacher_settings=None, max_bootstrapped_demos=4, max_labeled_demos=16, max_rounds=1)
- Runs program on training examples, scores with metric, keeps successful traces as demos
- Mixes up to `max_bootstrapped_demos` bootstrapped traces + `max_labeled_demos` raw labeled examples
- `teacher_settings`: optional dict to use a different LM for bootstrapping (e.g., stronger model)
- `metric_threshold`: minimum score for a trace to be kept (default: >0)
- Almost always beats zero-shot when metric is reliable

## Search across demo sets

### dspy.BootstrapRS (alias: dspy.BootstrapFewShotWithRandomSearch)
```python
dspy.BootstrapRS(
    metric, max_bootstrapped_demos=4, max_labeled_demos=16,
    max_rounds=1, num_candidate_programs=16, num_threads=None, stop_at_score=None
)
```
- Runs BootstrapFewShot `num_candidate_programs` times with different random seeds
- Evaluates each candidate on valset, returns highest-scoring
- `stop_at_score`: short-circuits when a candidate clears target

### dspy.KNNFewShot(k, trainset, vectorizer, **bootstrap_kwargs)
- Demos chosen at *inference* time via nearest-neighbor retrieval
- Trainset embedded at construction via `vectorizer`; on each call, input is embedded and `k` nearest examples become demos
- Use when no single demo set generalizes across the input distribution

## Instruction optimization

### dspy.COPRO(prompt_model=None, metric=None, breadth=10, depth=3, init_temperature=1.4, track_stats=False)
- Breadth-first instruction search
- At each of `depth` levels: generate `breadth` candidate instructions per predictor via `prompt_model`, score against trainset, keep best
- Total LM cost ≈ `breadth × depth × num_predictors`
- Lightweight; good when demos are already strong and only wording needs fixing

### dspy.GEPA(metric, auto=None, max_full_evals=None, max_metric_calls=None, reflection_lm=None, skip_perfect_score=True, instruction_proposer=None, use_merge=True, num_threads=None)
- Evolutionary instruction search guided by per-predictor feedback
- **Requires metric returning `dspy.Prediction(score=..., feedback="...")`**
- Maintains a population of programs; uses `reflection_lm` to propose edits informed by metric feedback
- Returns best candidate from Pareto frontier
- `auto`: `"light"` (~6 candidates), `"medium"`, `"heavy"` — controls budget
- `reflection_lm`: separate (usually stronger) LM for instruction writing
- `max_full_evals`: cap on full trainset evaluations
- `max_metric_calls`: cap on total metric invocations
- Best when you have a strong reflection LM + feedback-rich metric

### dspy.MIPROv2(metric, prompt_model=None, task_model=None, teacher_settings=None, max_bootstrapped_demos=4, max_labeled_demos=4, auto="light", num_candidates=None, num_threads=None, init_temperature=1.0, track_stats=True)
- Bayesian-optimization search over joint instruction + demo space
- `prompt_model`: proposes instructions (often a stronger LM)
- `task_model`: runs the program (your student)
- `auto`: `"light"` / `"medium"` / `"heavy"` → budget for proposals + evaluations
- State of the art when both instructions and demos need tuning together

### dspy.SIMBA(metric, bsize=32, num_candidates=6, max_steps=8, max_demos=4, prompt_model=None, teacher_settings=None, num_threads=None)
- Mini-batch SGD-flavored search
- Each step: sample `bsize` minibatch → find worst-scoring examples → propose rule (instruction patch) or new demo
- Reactive: targets current weak spot each step

### dspy.InferRules(num_candidates=10, num_rules=10, num_threads=None, **bootstrap_kwargs)
- Extends BootstrapFewShot: after bootstrapping demos, asks teacher LM to extract `num_rules` general rules
- Rules appended to predictor instructions (interpretable — you can read them)

## Fine-tuning

### dspy.BootstrapFinetune(metric=None, multitask=True, train_kwargs=None, adapter=None, exclude_demos=False, num_threads=None)
- Bootstraps successful traces, writes as training data, fine-tunes the student LM
- **Requires LM with `.finetune()` method** (OpenAI fine-tuning API, Together AI, local trainer)
- `multitask=True`: one model across all predictors; `False`: separate model per predictor

## Meta / composition

### dspy.BetterTogether(metric, **optimizers)
- Runs a sequence like `"p -> w -> p"` (prompt → weight → prompt)
- `optimizers` kwargs map letters to instances: `p=GEPA(...)`, `w=BootstrapFinetune(...)`
- Defaults: `p=BootstrapRS`, `w=BootstrapFinetune`

### dspy.Ensemble(reduce_fn=None, size=None, deterministic=False)
- Composes already-compiled programs into one
- `.compile(programs)` → module running each input through every program in parallel
- Reduces with `reduce_fn` (default: majority voting via `dspy.majority`)

## Selection decision tree

1. **No budget?** → `LabeledFewShot`
2. **Have reliable metric + labeled data?** → `BootstrapFewShot`
3. **Need better demos, more budget?** → `BootstrapRS` or `KNNFewShot`
4. **Prompt wording is the bottleneck?** → `COPRO` (light) or `GEPA` (heavy, needs feedback metric)
5. **Both instructions and demos need work?** → `MIPROv2`
6. **Can fine-tune the model?** → `BootstrapFinetune` (last resort; marginal lift often small)
7. **Want to combine prompt + weight optimization?** → `BetterTogether`
