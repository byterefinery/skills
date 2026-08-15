---
name: gepa-0-1-4
description: GEPA 0.1.4 - text evolution engine that optimizes any text parameter (prompts, code, agent architectures, configs, SVGs) against arbitrary evaluation metrics using LLM-based reflection over execution traces and Pareto-efficient evolutionary search. Use when optimizing LLM prompts or system components without RL, running gepa.optimize or gepa.optimize_anything, using dspy.GEPA, writing a GEPAAdapter, tuning reflection LMs, budgets, or stop conditions, or learning repo-specific coding-agent skills with gskill. Triggers on gepa, GEPA, reflective prompt evolution, prompt optimization, Actionable Side Information, Pareto frontier, optimize_anything, GEPAAdapter, dspy.GEPA, gskill.
license: MIT
compatibility: >
  Python 3.10-3.14. Base install has no hard deps; the [full] extra adds
  litellm (>=1.83.0, <1.92), tqdm, cloudpickle, datasets, mlflow, wandb.
  Optional extras are gepa[confidence], gepa[langchain], gepa[dspy],
  gepa[gskill].
metadata:
  tags:
    - python
    - ml
    - llm
    - prompt-optimization
---

# gepa 0.1.4

## Overview

GEPA (Genetic-Pareto) is a text evolution engine that optimizes any system with textual parameters — prompts, code, agent architectures, configurations, SVGs — against any evaluation metric. Instead of RL or gradient methods collapsing execution traces into a single scalar reward, GEPA has an LLM *read* the full traces (error messages, profiler output, reasoning logs) to diagnose *why* a candidate failed and propose targeted fixes.

The loop, repeated until the budget is exhausted:

1. **Select** a candidate from the Pareto frontier (candidates excelling on different task subsets)
2. **Execute** it on a training minibatch, capturing full execution traces
3. **Reflect** — the `reflection_lm` reads the traces plus any Actionable Side Information and diagnoses failures
4. **Mutate** — propose an improved candidate
5. **Accept** it if it improves on the validation set; update the Pareto front

**Actionable Side Information (ASI)** is the key concept: diagnostic text your evaluator returns alongside the score (errors, expected vs actual, constraints). It is the text-space analogue of a gradient — the quality of the feedback drives the quality of the optimization.

Where GEPA shines: expensive rollouts (100–500 evaluations vs 10k+ for RL), scarce data (improvements shown with as few as 3 examples), API-only models (no weights access needed), and interpretable runs (human-readable traces show why each change was made).

## Installation

```bash
pip install gepa==0.1.4          # base install, no hard deps
pip install "gepa[full]==0.1.4"  # + litellm, tqdm, cloudpickle, datasets, mlflow, wandb
```

Optional extras: `gepa[confidence]` (logprob-aware classification), `gepa[langchain]`, `gepa[dspy]`, `gepa[gskill]` (learn repo-specific skills for coding agents; also needs `mini-swe-agent`, `swebench`, and a running Docker daemon).

String LMs (e.g. `"openai/gpt-5"`) are resolved through LiteLLM, so use LiteLLM model IDs — this requires the `[full]` extra. Pass a callable instead of a string to use any custom provider.

## Usage

### 1. gepa.optimize — single-turn LLM tasks (DefaultAdapter)

The simplest path. Without an `adapter`, GEPA uses the built-in `DefaultAdapter`: each example is a dict with `input`, `additional_context` (may be `{}`), and `answer`, and the default evaluator scores by substring match against `answer`.

```python
import gepa

trainset = [
    {"input": "What is 2+2?", "additional_context": {}, "answer": "4"},
    {"input": "What is the capital of France?", "additional_context": {}, "answer": "Paris"},
]
valset = [...]  # hold out a separate validation set

result = gepa.optimize(
    seed_candidate={"system_prompt": "You are a helpful assistant."},
    trainset=trainset,
    valset=valset,                  # omit to reuse trainset (more overfitting)
    task_lm="openai/gpt-4.1-mini",  # the model being optimized; use your production model
    reflection_lm="openai/gpt-5",   # strong model that reads traces and proposes fixes
    max_metric_calls=150,
)

print(result.best_candidate["system_prompt"])
print(result.val_aggregate_scores[result.best_idx])
```

For custom scoring on single-turn tasks, pass an `evaluator` alongside `task_lm`; for anything else, implement a `GEPAAdapter` (see the reference file). AIME math examples are bundled: `trainset, valset, _ = gepa.examples.aime.init_dataset()`.

### 2. optimize_anything — any text artifact

The universal API: bring a seed candidate (a `str`, a `dict[str, str]` of named components, or `None` for seedless mode) plus an evaluator that scores candidates and returns ASI; GEPA handles the search. Works for code, agent programs, configs, graphics — no adapter or framework needed.

```python
import gepa.optimize_anything as oa
from gepa.optimize_anything import optimize_anything, GEPAConfig, EngineConfig

def evaluate(candidate: str) -> tuple[float, dict]:
    result = run_my_system(candidate)
    return result.score, {
        "Error": result.stderr,          # ASI — fed directly to the reflection LM
        "Output": result.stdout,
        "Constraint": "Do NOT change the output schema or rating scale.",
    }

result = optimize_anything(
    seed_candidate="<initial artifact>",
    evaluator=evaluate,                  # may return score, (score, dict), or use oa.log
    objective="what you want to optimize for",
    config=GEPAConfig(engine=EngineConfig(max_metric_calls=100)),
)

print(result.best_candidate)
```

Evaluator return conventions: `score`, `(score, side_info_dict)`, or `oa.log("...")` calls captured automatically as ASI. Structured `side_info` keys can also carry rendered images (via `gepa.Image`) for VLM feedback. Mode is determined by `dataset`/`valset`: both `None` = single-task search (one hard problem), `dataset` only = multi-task search with cross-transfer, both = generalization mode (skill that transfers to unseen data).

### 3. dspy.GEPA — DSPy programs

For DSPy pipelines, the metric should return `dspy.Prediction(score=..., feedback=...)` — the textual `feedback` is what makes GEPA's reflection work; a bare float leaves most of the power unused.

```python
import dspy

def metric(example, pred, trace=None):
    correct = example.answer.lower() in pred.answer.lower()
    feedback = (
        "Correct." if correct else
        f"Incorrect. Expected '{example.answer}', got '{pred.answer}'. "
        "Explain the reasoning gap."
    )
    return dspy.Prediction(score=float(correct), feedback=feedback)

optimizer = dspy.GEPA(metric=metric, reflection_lm="openai/gpt-5", auto="light")
optimized = optimizer.compile(my_program, trainset=trainset, valset=valset)
```

### Reading results — GEPAResult

- `result.best_candidate` — optimized text (dict of named components, or `str` when the seed was a `str`)
- `result.best_idx` — index of the best candidate in `result.candidates`
- `result.val_aggregate_scores` — per-candidate average validation score
- `result.total_metric_calls` — evaluations consumed
- `result.per_val_instance_best_candidates` — per-validation-instance Pareto frontier
- `result.run_dir` — state directory, if one was set

### Budget and stop conditions

Provide `max_metric_calls` **or** `stop_callbacks` — one is required; GEPA stops when any stopper triggers.

```python
from gepa import TimeoutStopCondition, NoImprovementStopper, ScoreThresholdStopper

result = gepa.optimize(
    # ...other args...
    max_metric_calls=200,
    stop_callbacks=[
        TimeoutStopCondition(timeout_seconds=3600),
        NoImprovementStopper(max_iterations_without_improvement=10),
        ScoreThresholdStopper(threshold=0.95),
    ],
    run_dir="./gepa_runs/exp1",   # state saved to disk; re-running resumes
    display_progress_bar=True,
)
```

`run_dir` also installs a `FileStopper` — touching a `gepa.stop` file inside it stops the run gracefully. Pass `use_wandb=True` / `use_mlflow=True` for experiment tracking (both can run simultaneously); `use_cloudpickle=True` when state contains dynamically generated DSPy signatures.

## Gotchas

- **Feedback quality is the biggest lever** — a bare scalar score leaves most of GEPA's power unused. Return ASI with errors, expected-vs-actual, sub-scores, and reference solutions when available.
- **Budget scales with the validation set** — plan for at least 15–30x `len(valset)` metric calls so GEPA can propose and evaluate up to 15 new candidates. Each iteration spends several calls (minibatch eval, reflection, minibatch validation, full validation when improved).
- **Always pass a separate valset** — with `valset=None`, GEPA reuses the trainset and overfits. Use an 80/20 split when the total exceeds 200 examples, 50/50 when fewer.
- **Frontier model for `reflection_lm`, production model for `task_lm`** — the reflection LM should be a leading model (GPT-5 / Gemini-3 / Claude Opus class); the task LM should be whatever you deploy. String LMs are LiteLLM IDs; Bedrock needs the `us.` cross-region prefix (`bedrock/us.anthropic....`).
- **Early prompts that copy training examples are normal** — early candidates memorize the first minibatch and generalize only later. To prevent verbatim copying of keywords or phrases, add an anti-overfit instruction to the evaluator's `side_info` (it reaches the reflection LM verbatim).
- **The reflection LM can drift the task definition** — rating scales and output schemas may change mid-run. Pin them with an explicit preservation constraint in `side_info`; for production-critical systems, optimize a fixed set of human-written bullets instead of allowing full rewrites.
- **Base install has no dependencies** — plain `pip install gepa` does not include litellm, so string LM specs fail until you install `gepa[full]`.
- **`max_metric_calls` and `stop_callbacks` are mutually required** — GEPA needs at least one of them to know when to stop.
- **`use_merge=False` by default** — the system-aware merge of two Pareto-frontier candidates (combining strengths on different task subsets) is opt-in.
- **`reflection_minibatch_size` defaults to 3** — the number of training examples each reflection step sees; raise it for noisy tasks or when a single example is too little signal.
- **`optimize_anything` evaluators may be called concurrently** — with parallel engines or `batch_evaluator`, keep evaluation side-effect-free and thread-safe.

## References

- [01-advanced-configuration.md](references/01-advanced-configuration.md) — candidate selection, frontier types, merge, custom proposers and reflection templates, stoppers, callbacks, tracking, adapters, gskill
- [Quick Start](https://gepa-ai.github.io/gepa/guides/quickstart/) — official walkthrough of all three entry points
- [FAQ](https://gepa-ai.github.io/gepa/guides/faq.md) — budget, model selection, overfitting, production patterns
- [Creating Adapters](https://gepa-ai.github.io/gepa/guides/adapters.md) — building a custom GEPAAdapter
- [Paper](https://arxiv.org/abs/2507.19457) — GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning
