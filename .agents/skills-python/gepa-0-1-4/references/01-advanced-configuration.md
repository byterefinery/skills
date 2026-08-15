# Advanced Configuration

Details on the knobs behind `gepa.optimize` and `optimize_anything` (0.1.4).

## Search behavior

- `candidate_selection_strategy` — `"pareto"` (default; sample from the Pareto frontier), `"current_best"`, `"epsilon_greedy"`, `"top_k_pareto"`.
- `frontier_type` — `"instance"` (default; per validation example), `"objective"`, `"hybrid"`, `"cartesian"` (per example-objective pair) for multi-objective tracking.
- `acceptance_criterion` — `"strict_improvement"` (default) or `"improvement_or_equal"`.
- `perfect_score` (default 1.0) and `skip_perfect_score` (default True) — stop refining a candidate that already scores perfectly on its minibatch.
- `batch_sampler` — `"epoch_shuffled"` (default) or a `BatchSampler` instance; `reflection_minibatch_size` (default 3) is only honored with `epoch_shuffled`.
- `module_selector` — `"round_robin"` (default) or `"all"` for multi-component candidates (dict seeds with several named text components).
- `val_evaluation_policy` — `"full_eval"` (default) or a custom `EvaluationPolicy` for cheaper validation.
- `seed` (default 0) for reproducibility; `cache_evaluation=True` to memoize pair evaluations across runs.

## Proposal strategies (0.1.4)

- `sampling_strategy` — how many (parent, minibatch) proposal tasks per iteration. `SingleMutationSampling` (default; 1 parent, 1 mutation — classic GEPA), `SameParentSampling(n)`, `IndependentSampling(n)`, `PxNSampling(p, n)`.
- `selection_strategy` — which improving proposals enter the pool. `AllImprovements` (default), `BestImprovement`, `TopKImprovements(k)`.
- `reflection_strategy` — a `ReflectionLM` implementation owning how reflective mutation calls the reflection model (stateful sessions, batched `reflect_many`); defaults to a stateless single-call reflector built from `reflection_lm`.
- Parallel engines (`EngineConfig(parallel=..., max_workers=...)`) run proposals concurrently.

## Customizing reflection

- `reflection_prompt_template` — string (all components) or dict per component. Must contain the placeholders `<curr_param>` (the component to evolve) and `<side_info>` (captured execution feedback). Ignored if the adapter provides its own `propose_new_texts`.
- `custom_candidate_proposer` — callable `(candidate, reflective_dataset, components_to_update) -> dict[str, str]`; replaces the LLM reflection step entirely (e.g. to use Claude Code or a CLI agent as the proposer). Mutually exclusive with an adapter-level `propose_new_texts`.
- `RefinerConfig(refiner_lm=..., max_refinements=...)` — an optional second-pass LM that polishes accepted candidates.

## Merge

`use_merge=True` enables system-aware merge of two Pareto-frontier candidates excelling on different task subsets; `max_merge_invocations=5` (budget in merge calls) and `merge_val_overlap_floor=5` (minimum shared validation ids between parents when validation is partial).

## Stop conditions (complete list)

All importable from `gepa`: `MaxMetricCallsStopper(max_metric_calls)`, `MaxCandidateProposalsStopper(max_proposals)`, `TimeoutStopCondition(timeout_seconds)`, `NoImprovementStopper(max_iterations_without_improvement)`, `ScoreThresholdStopper(threshold)`, `FileStopper(stop_file_path)`, `SignalStopper(signals)`, `MaxTrackedCandidatesStopper(max_tracked_candidates)`, `MaxReflectionCostStopper(max_reflection_cost_usd, reflection_lm)`, `CompositeStopper(*stoppers, mode="any")`. Pass one or a list to `stop_callbacks`.

## Callbacks and tracking

- `callbacks` — list of `GEPACallback` objects; events include `on_optimization_start/end`, `on_iteration_start/end`, `on_candidate_selected/accepted/rejected`, `on_evaluation_start/end`, `on_valset_evaluated`, `on_pareto_front_updated`, `on_merge_attempted/accepted/rejected`, `on_budget_updated`, `on_error`, `on_state_saved`.
- `run_dir` — persists state; re-running resumes. Also enables the `gepa.stop` file stopper.
- `use_wandb` / `use_mlflow` (simultaneous OK), with `*_attach_existing=True` to log into a run your outer loop owns; `tracking_key_prefix` / `TrackingConfig(key_prefix=...)` for key namespacing; `track_best_outputs` (default True) stores best per-valset outputs in the result.
- `display_progress_bar` — tqdm progress over metric calls.

## Adapters

A `GEPAAdapter` has two required methods:

1. `evaluate(candidate, batch)` — instantiate your system with the candidate's component texts, run the batch, return per-instance scores plus captured trajectories (rich traces feed reflection).
2. `make_reflective_dataset(candidate, batch, trajectories)` — given captured trajectories, return the textual side information relevant to the component being updated.

Optionally implement `propose_new_texts(...)` to replace the built-in reflection. Built-in adapters: `DefaultAdapter` (single-turn, substring match), `DSPyAdapter`, `DSPyFullProgramAdapter` (evolves whole DSPy programs incl. signatures and control flow), `RAGAdapter` (vector-store-agnostic: ChromaDB, Weaviate, Qdrant, Pinecone), `MCPAdapter` (tool descriptions + system prompts), `TerminalBenchAdapter` (Terminus agent), plus AnyMaths, LangChain (`gepa[langchain]`), and Confidence (`gepa[confidence]`, logprob-aware classification). DSPy's `dspy/teleprompt/gepa/gepa_utils.py` is a good reference implementation.

## gskill (repo-specific coding-agent skills)

`gepa[gskill]` + `mini-swe-agent` + `swebench` + Docker. Pipeline: SWE-smith mines real commits of a target repo, injects bugs, and creates verifiable task instances (problem statement, Docker env, tests); GEPA starts from empty skills, runs the agent on task batches in parallel Docker containers, and feeds pass/fail, traces, and test output to the reflection model until the budget is exhausted. Output is `best_skills.txt` — inject it into the agent's system prompt; skills transfer across agents and models (train on a cheap model, deploy on an expensive one).

```bash
python -m gepa.gskill.train_optimize_anything --smoke-test --model "gpt-5-mini"   # 3-task wiring check
```

See the official [gskill guide](https://gepa-ai.github.io/gepa/guides/gskill/) for full-run flags.
