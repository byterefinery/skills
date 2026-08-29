---
name: dspy-3-3-1
description: >
  DSPy 3.3.1, a framework for programming language models rather than
  prompting them — declarative signatures, composable modules, LM adapters,
  and prompt optimizers. Use when building LM pipelines with dspy.Predict,
  dspy.ChainOfThought, dspy.ReAct, or custom dspy.Modules; configuring
  dspy.LM and dspy.configure; writing dspy.Signatures; composing RAG or
  agent programs; defining evaluation metrics; or optimizing prompts with
  dspy.GEPA, dspy.MIPROv2, or BootstrapFewShot. Emphasizes the basic
  building blocks (LM, signatures, modules, adapters, data, metrics) and
  GEPA reflective prompt optimization (feedback metrics, reflection_lm,
  budgets, Pareto search, detailed_results).
license: MIT
compatibility: >
  Python 3.10-3.14. `pip install dspy==3.3.1`; pulls in litellm, pydantic,
  and gepa[dspy]==0.1.4 (hard dependency powering dspy.GEPA). An LM API key
  is required for LM calls and GEPA reflection.
metadata:
  tags:
    - python
    - ml
    - llm
    - dspy
    - prompt-optimization
    - gepa
---

# dspy 3.3.1

DSPy (Declarative Self-improving Python) is a framework for *programming* language models instead of hand-writing prompts. You write Python code with declarative **signatures** (what in/out), composable **modules** (how: chain-of-thought, ReAct, …), **adapters** (prompt formatting and parsing), and a **language model**. Optimizers then *learn* the prompts — synthesizing few-shot demos or rewriting instructions — to maximize a metric you define. Think PyTorch for LM pipelines: declare modules, compose them, compile them against data, save the result as an artifact.

## Overview

| Concept | Class | Role |
|---|---|---|
| Signature | `dspy.Signature` | Declarative I/O spec; field names are semantic |
| Module | `dspy.Module`, `dspy.Predict`, `dspy.ChainOfThought`, `dspy.ReAct` | Prompting technique + learnable parameters |
| Adapter | `dspy.ChatAdapter` (default), `dspy.JSONAdapter` | Signature → messages → parsed `Prediction` |
| LM | `dspy.LM` | LiteLLM wrapper with caching, history, structured errors |
| Data | `dspy.Example` | dict-like row; `with_inputs()` marks what the module sees |
| Metric | plain function | scores a `Prediction`; GEPA needs text feedback too |
| Optimizer | `dspy.GEPA`, `dspy.MIPROv2`, … | `.compile()` tunes instructions, demos, or weights |

Install: `pip install dspy` (3.3.x needs Python 3.10-3.14 and pulls in `gepa[dspy]==0.1.4`, which `dspy.GEPA` requires).

## Basic building blocks

### 1. Configure the LM (first step of any program)

```python
import dspy

lm = dspy.LM("openai/gpt-4o-mini")            # any LiteLLM provider/model id
dspy.configure(lm=lm)                          # global default

with dspy.context(lm=dspy.LM("openai/gpt-4o")):  # scoped override (thread-safe)
    ...
```

LM kwargs (`temperature`, `max_tokens`, `stop`, `cache`) are set at init or per call. `dspy.configure` and `dspy.context` are thread-safe. Call the LM directly via `lm("text")` or `lm(messages=[...])`; `lm.history` holds inputs, outputs, token usage, and cost per call. Errors raise `dspy.LMError` subclasses (`LMRateLimitError`, `ContextWindowExceededError`, `LMTimeoutError`, …) — catch the base class for any LM failure.

### 2. Signatures

Inline string or class:

```python
qa = dspy.Predict("question -> answer")        # default type is str
rag = dspy.ChainOfThought("context: list[str], question -> answer")

class Emotion(dspy.Signature):
    """Classify emotion."""                     # docstring becomes the instructions
    sentence: str = dspy.InputField()
    sentiment: Literal['sadness', 'joy', 'love', 'anger', 'fear', 'surprise'] = dspy.OutputField()
```

Keep field names semantically meaningful but plain; do not hand-tune keywords — optimizers rewrite instructions on your data and that transfers better across LMs. Add free-form guidance with the `instructions=` kwarg on inline signatures and `desc=` on fields. Types: `str`/`int`/`bool`/`float`, `list[...]`, `dict[...]`, `Optional[...]`, `Literal[...]`, pydantic models, `dspy.Image`. Output fields are required unless they declare a default, a `default_factory`, or a `None`-able annotation — a missing required output raises `AdapterParseError`.

### 3. Modules

Declare with a signature, call with inputs, read outputs off the returned `dspy.Prediction`:

```python
classify = dspy.ChainOfThought("sentence -> sentiment: bool", temperature=0.7)
pred = classify(sentence="...")
pred.sentiment, pred.reasoning   # ChainOfThought injects `reasoning`
```

- `dspy.Predict` — basic predictor, signature unmodified
- `dspy.ChainOfThought` — reason step-by-step first; usually just better
- `dspy.ProgramOfThought` / `dspy.CodeAct` — LM writes and executes code (Deno WASM sandbox)
- `dspy.ReAct(signature, tools=[...], max_iters=20)` — tool-calling agent; `pred.trajectory` records reasoning + calls
- `dspy.MultiChainComparison` — judge multiple drafts; `dspy.BestOfN` / `dspy.Refine` — sample and keep the best
- `dspy.majority(predictions)` — plain function, no LM call
- `dspy.RLM` — experimental recursive LM for contexts too large to fit in a prompt
- `dspy.Refine(module, N, reward_fn, threshold)` — inference-time best-of-N with feedback retry; the replacement for the deprecated `dspy.Assert`/`dspy.Suggest`

LM kwargs given at init (`dspy.Predict(sig, temperature=1.0)`) are defaults for every call; override a single call with `config={...}`. A unique `rollout_id` plus non-zero `temperature` forces a fresh, uncached LM call (diverse outputs).

### 4. Compose programs

```python
class Hop(dspy.Module):
    def __init__(self, num_hops=4):
        self.num_hops = num_hops
        self.generate_query = dspy.ChainOfThought("claim, notes -> query")
        self.append_notes = dspy.ChainOfThought("claim, notes, context -> new_notes: list[str]")

    def forward(self, claim: str):
        notes = []
        for _ in range(self.num_hops):
            query = self.generate_query(claim=claim, notes=notes).query
            context = search(query)
            notes.extend(self.append_notes(claim=claim, notes=notes, context=context).new_notes)
        return dspy.Prediction(notes=notes)
```

Programs are plain Python — loops, conditionals, other modules — with LM calls traced internally at compile time. `module.batch(examples)` runs a dataset through one module in parallel.

### 5. Data and metrics

```python
trainset = [dspy.Example(question=q, answer=a).with_inputs("question") for q, a in pairs]

def validate_answer(example, pred, trace=None):
    return example.answer.lower() == pred.answer.lower()

evaluator = dspy.Evaluate(devset=valset, metric=validate_answer,
                          num_threads=8, display_table=5)
evaluator(program)
```

`with_inputs(...)` marks which fields go to the module; the rest are labels. The third `trace` argument is non-None only while an optimizer runs, exposing intermediate predictor calls. Built-in metrics: `dspy.evaluate.answer_exact_match`, `dspy.evaluate.answer_passage_match`, and `dspy.SemanticF1` (itself a DSPy module).

### 6. Adapters

`dspy.ChatAdapter` (the default) wraps fields in `[[ ## field ## ]]` markers and automatically retries with `JSONAdapter` when parsing fails; `JSONAdapter` is leaner and better for models with native structured output. Switch via `dspy.configure(adapter=...)` or `dspy.context(adapter=...)`. See what actually reaches the LM with `dspy.inspect_history()`.

## GEPA optimization

GEPA (Genetic-Pareto) is a *reflective* instruction optimizer. It maintains a population of candidate programs, scores them, and uses a separate strong LM to read low-scoring execution traces plus **textual feedback from your metric**, then rewrites one predictor's instructions per iteration. Because the feedback is natural language, GEPA usually finds high-performing prompts in far fewer rollouts than scalar-only optimizers — and it shines when you can explain *why* an output failed.

### The metric contract (the important part)

The metric must accept five positional arguments and return `dspy.Prediction(score=..., feedback=...)`:

```python
def metric(example, prediction, trace=None, pred_name=None, pred_trace=None):
    correct = int(example.answer)
    try:
        llm_answer = int(prediction.answer)
    except ValueError:
        return dspy.Prediction(score=0.0,
                               feedback=f"The final answer must be a valid integer; got '{prediction.answer}'.")
    score = float(correct == llm_answer)
    feedback = (f"Correct. The answer is {correct}." if score else
                f"Wrong. Predicted {llm_answer}, correct is {correct}."
                + (f" Reference solution:\n{example.solution}" if example.get("solution") else ""))
    return dspy.Prediction(score=score, feedback=feedback)
```

`feedback` reaches the reflection prompt verbatim — it is the optimization signal. Make it concrete: what failed, expected vs. actual, violated constraints, reference solutions. A plain-float metric still works, but GEPA then only sees a generic "got a score of X" caption — a much weaker optimizer. `pred_name`/`pred_trace` let you also emit per-predictor feedback when GEPA targets a specific predictor.

### Running it

```python
optimizer = dspy.GEPA(
    metric=metric,
    reflection_lm=dspy.LM("openai/gpt-5", temperature=1.0, max_tokens=32000),
    auto="light",                    # or max_full_evals=... / max_metric_calls=... (exactly one)
    num_threads=8,
    track_stats=True,
)
optimized = optimizer.compile(program, trainset=trainset, valset=valset)
```

- **Budget** — exactly one of `auto` (`light`/`medium`/`heavy` = 6/12/18 candidates), `max_full_evals`, or `max_metric_calls`.
- **`reflection_lm`** — required (unless you pass a custom `instruction_proposer`). Use a strong LM: it is called once or a few times per mutation and often dominates total cost, while the *program itself* runs on the cheap configured LM.
- `.compile()` returns a **new** module — the student is never mutated. The winner's instructions are baked into each predictor's `signature.instructions`; demos and structure are unchanged.
- Search dynamics: candidates are sampled from a per-example Pareto frontier (keeps diverse strategies), predictors are updated round-robin by default, and complementary candidates can be merged (5 merges by default).
- With `track_stats=True`, `optimized.detailed_results` holds every candidate, its lineage, per-example validation scores, and the `best_idx`/`best_candidate` (convert with `.to_dict()`).

Full mechanics — budget math, per-predictor feedback, inference-time search, multi-objective frontiers, custom proposers/selectors — are in [GEPA deep dive](references/05-gepa-deep-dive.md).

## Saving and loading

```python
optimized.save("program.json", save_program=False)   # state only (signatures, demos, LM config)
new = SameProgramClass()                             # recreate, then
new.load("program.json")

optimized.save("./program/", save_program=True)      # whole program (directory)
loaded = dspy.load("./program/")                     # no recreation needed
```

Prefer JSON (readable, auditable, safe); pickle files can execute arbitrary code on load.

## Gotchas

- **GEPA metrics need the 5-arg signature** `(gold, pred, trace, pred_name, pred_trace)` — `dspy.GEPA` checks this at construction and raises `TypeError` otherwise.
- **Assertions are deprecated** — `dspy.Assert`/`dspy.Suggest` are not supported in 3.x; use `dspy.Refine` for inference-time constraint retry.
- **Labels leak without `with_inputs()`** — modules only receive fields marked as inputs; unmarked fields (labels) never reach the prompt.
- **Don't hand-tune signature keywords** — optimizers rewrite instructions on your data and transfer better across LMs; manual field-name/description hacking is wasted effort.
- **`.compile()` returns a copy** — the student you pass in is untouched (deepcopy via `reset_copy()`); compiled submodules get `_compiled=True` so later optimizers skip them.
- **Budget is one-of-three** — setting both `auto="light"` and `max_metric_calls` fails an assert in the `GEPA` constructor.
- **`dspy.GEPA` requires a `reflection_lm`** or a custom `instruction_proposer`; construction asserts this.
- **LMs are cached by default** — repeated identical calls replay from cache; use `cache=False` or a unique `rollout_id` with non-zero temperature for diverse outputs.
- **Required outputs are strict** — a missing output field raises `AdapterParseError`; make fields optional via a default, `default_factory`, or `None`-able annotation.
- **`dspy.majority` is a function, not a module** — no LM call, no signature, no serialization.
- **`ReAct` defaults to `max_iters=20`** — docs examples often show 10 or 5; the source default is 20.
- **Pickle save/load executes code** — prefer `.json`; loading a `.pkl` with `allow_pickle=True` is a trust decision.
- **`dspy.configure` is global** — use `dspy.context(...)` when a block of code needs a different LM or adapter.

## References

- [01-signatures-modules](references/01-signatures-modules.md) — signatures in depth (types, defaults, optional outputs), full built-in module list, tools and ReAct
- [02-lm-and-adapters](references/02-lm-and-adapters.md) — providers and auth, direct LM calls, history, error hierarchy, adapters, Responses API
- [03-data-metrics-eval](references/03-data-metrics-eval.md) — Example, with_inputs, dspy.Evaluate, metric patterns (AI feedback, program-as-metric, trace access)
- [04-optimizers](references/04-optimizers.md) — optimizer catalog, which one to pick, the compile interface, costs, BetterTogether and Ensemble
- [05-gepa-deep-dive](references/05-gepa-deep-dive.md) — GEPA internals: budget math, the reflective loop, Pareto dynamics, detailed_results, custom proposers and selectors, multi-objective frontiers
- [06-save-load](references/06-save-load.md) — state vs whole-program saving, loading on another machine, the `_compiled` flag, custom LM state
