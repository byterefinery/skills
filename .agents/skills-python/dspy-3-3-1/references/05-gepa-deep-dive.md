# GEPA in depth

`dspy.GEPA` implements "GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning" (Agrawal et al., 2025, arXiv:2507.19457). It evolves the *textual* parameters (instructions) of your program using an LM reflection step over execution traces plus textual feedback, with Pareto-frontier candidate selection. It internally uses the `gepa-ai/gepa` package (a hard dependency of dspy 3.x).

## Algorithm

1. **Initialize** the candidate pool with the unoptimized program.
2. **Iterate** until budget is exhausted:
   - Sample a candidate from the per-example **Pareto frontier** (candidates that score best on at least one example; sampling probability ∝ coverage) — keeps diverse strategies instead of collapsing to one.
   - Sample a minibatch from the trainset; **roll out** the candidate, collecting traces + metric feedback.
   - **Select a predictor** to update (round-robin by default).
   - **Reflect**: the `reflection_lm` reads the low-scoring traces + feedback and proposes a new instruction for that predictor.
   - **Evaluate** the mutated candidate on the minibatch; if improved, evaluate on the Pareto validation set and add to the pool.
   - **Merge** (optional): combine instructions from two candidates that each win on different examples.
3. **Return** the candidate with the highest aggregate validation score.

The scalar score gates acceptance and selects the winner; the textual feedback drives *what* to change.

## The metric contract

GEPA's metric must accept five positional arguments (checked at construction — `TypeError` otherwise) and should return `dspy.Prediction(score=..., feedback=...)`:

```python
def metric(gold, pred, trace=None, pred_name=None, pred_trace=None):
    ...
    return dspy.Prediction(score=0.8, feedback="The answer contradicts the cited context ...")
```

- `trace` — full execution trace of the program for this example (list of `(predictor, inputs, outputs)`).
- `pred_name` / `pred_trace` — when GEPA asks for feedback about a specific predictor, these carry its name and sub-trace. The metric is called **twice per example** during optimization: once module-level (`pred_name=None`) for the aggregate, once per targeted predictor. Returning the same score for both is fine; `warn_on_score_mismatch=True` (default) logs divergence.
- Returning a bare float still works, but the reflection prompt only receives the generic caption "This trajectory got a score of X" — the concrete failure modes never reach the proposer.
- `failure_score=0.0` is assigned when the metric raises; `perfect_score=1.0` with `skip_perfect_score=True` drops fully-solved examples from the reflective minibatch (reflection focuses on what's broken). Lower `perfect_score` if your metric saturates below 1.0.
- `add_format_failure_as_feedback=True` feeds adapter parse failures to reflection as feedback.
- `program_trace` (sixth optional arg, supported in 3.x) is the full trace populated at *scoring* time — useful when optimizing a `dspy.Flex` submodule on how the answer was produced, not just whether it is correct.

### Writing good feedback

The feedback string is the optimization signal — treat it like a gradient in text form:

- **Reuse existing artifacts**: logs, unit tests, evaluation scripts, profiler output.
- **Decompose outcomes** into per-objective components (correctness, latency, cost, safety) and attribute errors to specific steps.
- **Expose trajectories**: label pipeline stages with pass/fail and salient errors.
- **Ground in checks**: automatic validators or an LLM-as-judge for non-verifiable tasks.
- **Be concrete**: expected vs. actual, the violated constraint, and a reference solution when one exists.

Examples from the tutorials: for retrieval, list which documents were correctly/incorrectly retrieved and which were missed (not just recall); for multi-objective tasks, break the aggregate score into sub-components so the reflection LM sees the tradeoff; for stacked pipelines (parse → compile → run → evaluate), report stage-specific failures.

## Reflection configuration

- `reflection_lm` — required unless you pass a custom `instruction_proposer`. Standard practice: a **strong** LM (e.g., `dspy.LM("openai/gpt-5", temperature=1.0, max_tokens=32000)`) reflecting over a cheap task model. It is called once to a few times per mutation, serially — `num_threads` does not parallelize it. Reflection cost often dominates the run: a `medium` budget on a 2-predictor/100-example task is ~12 mutations → ~12-36 reflection calls.
- `reflection_minibatch_size=3` — how many low-scoring examples the reflection LM sees per mutation. Larger = richer proposals, longer prompts.
- Default proposer template: the current instruction, a markdown block of example inputs/outputs/feedback, and "write a new instruction within ``` blocks".

### Custom instruction proposers

Implement the `ProposalFn` protocol from `gepa.core.adapter`:

```python
from gepa.core.adapter import ProposalFn
from dspy.teleprompt.gepa.gepa_utils import ReflectiveExample

class WordLimitProposer(ProposalFn):
    def __init__(self, max_words: int = 1000):
        self.max_words = max_words
        self.improver = dspy.ChainOfThought(MyProposerSignature)

    def __call__(self, candidate, reflective_dataset, components_to_update):
        # candidate: {predictor_name: current_instruction}
        # reflective_dataset: {predictor_name: [ReflectiveExample]}
        #   each ReflectiveExample: {"Inputs": ..., "Generated Outputs": ..., "Feedback": ...}
        # return {predictor_name: new_instruction} for the components being updated
        ...

gepa = dspy.GEPA(metric=metric, reflection_lm=..., instruction_proposer=WordLimitProposer(700), auto="medium")
```

Use a custom proposer for multimodal inputs, length/format constraints on instructions, domain knowledge injection, or coordinated multi-component updates. `MultiModalInstructionProposer` (in `dspy.teleprompt.gepa.instruction_proposal`) handles `dspy.Image` inputs. Build proposers from DSPy modules rather than raw LM calls.

### Custom component selectors

`component_selector` picks which predictor(s) to mutate per iteration: `"round_robin"` (default), `"all"`, or a custom `ReflectionComponentSelector` (from `gepa.proposer.reflective_mutation.base`) — a callable `(state, trajectories, subsample_scores, candidate_idx, candidate) -> list[str]` of component names. Use custom selectors for dependency-aware updates (e.g., always update a classifier and its formatter together) or LLM-driven selection.

## Budget

Exactly one of:

- `auto="light" | "medium" | "heavy"` → `num_candidates` 6/12/18; the metric-call budget is derived from predictor count, candidate count, and valset size (initial full eval + `5 × num_candidates` bootstrap calls + minibatch evals + periodic full evals every 5 steps). On a 2-predictor/100-example task: light ≈ 1330, medium ≈ 1740, heavy ≈ 2045 metric calls.
- `max_full_evals=N` → `N × (len(trainset) + len(valset))` metric calls.
- `max_metric_calls=N` → raw ceiling; use for hard dollar caps.

## Population and search knobs

- `candidate_selection_strategy` — `"pareto"` (default; stochastic sampling from the per-example frontier) or `"current_best"` (greedy local search — converges faster on simple tasks, less robust).
- `use_merge=True` / `max_merge_invocations=5` — merges find instruction combinations the proposer never suggests; set `max_merge_invocations=None` to disable.
- `seed=0` — reproducible runs.
- `num_threads` — parallelizes metric calls within each evaluation pass, not the mutation loop.

## Inspecting runs

- `track_stats=True` → the compiled program's `.detailed_results` (a `DspyGEPAResult`): `candidates` (every proposed module), `parents` (lineage), `val_aggregate_scores`, `val_subscores` (per-candidate per-example), `per_val_instance_best_candidates`, `discovery_eval_counts` (budget spent before each candidate appeared), `best_idx`, `best_candidate`, plus `total_metric_calls`. Convert with `.to_dict()`.
- `log_dir` — per-iteration artifacts on disk (candidates, scores, proposed instructions).
- `use_wandb` / `use_mlflow` — stream per-candidate aggregate scores.
- The winner's instructions overwrite the student's `signature.instructions`; demos, callbacks, and structure are preserved. `program.save(path)` writes them.

### Inference-time search

Point `valset` at your *evaluation batch* and set `track_best_outputs=True` (requires `track_stats=True`): GEPA then records, per task, the best output ever found during search — turning the optimizer into a best-of-search sampler.

```python
prog = dspy.GEPA(metric=metric, track_stats=True, track_best_outputs=True, auto="light")
new_prog = prog.compile(student, trainset=tasks, valset=tasks)
new_prog.detailed_results.highest_score_achieved_per_val_task
new_prog.detailed_results.best_outputs_valset
```

## Multi-objective frontiers

Metrics may return named objectives alongside the scalar:

```python
return dspy.Prediction(score=(quality + privacy) / 2,
                       objective_scores={"quality": quality, "privacy": privacy},
                       feedback="...")

gepa = dspy.GEPA(metric=metric, gepa_kwargs={"frontier_type": "objective"}, track_stats=True)
```

`frontier_type` (via `gepa_kwargs`): `"instance"` (default), `"objective"`, `"hybrid"`, or `"cartesian"`. Objectives affect parent/merge selection only — the scalar score still gates acceptance and picks the winner. Each objective is maximized and averaged over the examples reporting it; `objective_pareto_front` holds the independent per-objective maxima.

## Practical notes

- A small student model optimized with GEPA against a strong `reflection_lm` frequently matches or beats a hand-prompted frontier model, at much lower cost (the haiku tutorial lifted a nano model from 78.1% → 90.1% against a full constraint metric; AIME: GPT-4.1-mini 46.6% → 56.6% with just `auto="light"`).
- The same program optimizes to *different* instructions per model — recompile when you swap LMs.
- `dspy.GEPA` refuses `max_reflection_cost` and `reflection_prompt_template` in `gepa_kwargs` (the DSPy adapter implements its own reflection prompt; use `instruction_proposer` instead).
- Full tutorials: `gepa_ai_program` (AIME math), `gepa_papillon` (privacy delegation, LLM-as-judge feedback), `gepa_facilitysupportanalyzer` (structured extraction with predictor-level feedback), `gepa_trusted_monitor` (comparative metric).
