---
name: dspy-3-5-0
description: >
  DSPy 3.5.0, a framework for programming language models rather than
  prompting them — declarative signatures, composable modules, LM adapters,
  and prompt optimizers. Use when building LM pipelines with dspy.Predict,
  dspy.ChainOfThought, dspy.ReAct, dspy.RLM, or custom dspy.Modules;
  configuring dspy.LM and dspy.configure; writing dspy.Signatures; composing
  RAG or agent programs; defining evaluation metrics; or optimizing prompts
  with dspy.GEPA, dspy.MIPROv2, BootstrapFewShot, SIMBA, or COPRO. Covers the
  3.5 defaults — XMLAdapter with native function calling, ReActV2-style
  structured History in dspy.ReAct, model_type auto routing, and restricted
  save/load — plus migration notes from 3.4.x.
license: MIT
compatibility: >
  Python 3.10+. `pip install dspy` (base); optional extras `dspy[litellm]`
  for the LiteLLM compatibility engine, `dspy[openai]`/`dspy[numpy,openai]`
  for SDK-dependent features and OpenAI embeddings. An LM API key is required
  for LM calls.
metadata:
  tags:
    - python
    - ml
    - llm
    - dspy
    - prompt-optimization
---

# dspy 3.5.0

DSPy (Declarative Self-improving Python) is a framework for *programming* language models instead of hand-writing prompts. You write Python code with declarative **signatures** (what in/out), composable **modules** (how: chain-of-thought, ReAct, RLM, …), an **adapter** (prompt formatting and parsing), and a **language model**. Optimizers then *learn* the prompts — synthesizing few-shot demos or rewriting instructions — to maximize a metric you define. Think PyTorch for LM pipelines: declare modules, compose them, compile them against data, save the result as an artifact.

## Overview

| Concept | Class | Role |
|---|---|---|
| Signature | `dspy.Signature` | Declarative I/O spec; field names are semantic |
| Module | `dspy.Module`, `dspy.Predict`, `dspy.ChainOfThought`, `dspy.ReAct`, `dspy.RLM` | Prompting technique + learnable parameters |
| Adapter | `dspy.XMLAdapter` (default since 3.5) | Signature → messages → parsed `Prediction` |
| LM | `dspy.LM` | Provider wrapper with caching, history, structured errors |
| Data | `dspy.Example` | dict-like row; `with_inputs()` marks what the module sees |
| Metric | plain function | scores a `Prediction`; GEPA also reads text `feedback` |
| Optimizer | `dspy.GEPA`, `dspy.MIPROv2`, … | `.compile()` tunes instructions, demos, or weights |

## Setup and LM configuration

```python
import dspy

lm = dspy.LM("openai/gpt-5-nano", api_key="YOUR_OPENAI_API_KEY")
dspy.configure(lm=lm)                    # global default for the process

with dspy.context(lm=dspy.LM("anthropic/claude-sonnet-4-5-20250929")):
    ...                                  # scoped, thread-safe override

print(lm("What is the capital of France?"))   # LM calls return lists of strings
```

- Model string format is `"provider/model"`. Native providers include OpenAI, Anthropic (`ANTHROPIC_API_KEY`), Google AI Studio (`GEMINI_API_KEY`), Azure OpenAI, Vertex (`vertex:gemini-2.0-flash`, ADC + `GOOGLE_CLOUD_PROJECT`/`GOOGLE_CLOUD_LOCATION`), and local Ollama (`ollama_chat/llama3.2:1b`).
- 3.5 change: `model_type` defaults to `"auto"`, which selects the Responses API for OpenAI/Azure. Pin `model_type="chat"` for chat-only endpoints, proxies, or Azure deployments; pin `model_type="responses"` for native Responses endpoints. Routing is chosen before inference and never retried through another backend after a provider failure.
- 3.5 change: LiteLLM is optional. The bundled native lm15 engines handle supported routes; install `dspy[litellm]` only if you need the compatibility engine (`engine="litellm"`).
- Caching is enabled by default — identical calls return cached responses. Bypass with a unique `rollout_id` in config (plus non-zero temperature) to force fresh outputs while still caching the new result.

## Signatures

String form for quick programs:

```python
haiku_generator = dspy.Predict("subject -> haiku")
result = haiku_generator(subject="computer science")
print(result.haiku)
```

Multiple fields are comma-separated; types can be inline (`"location, mood -> haiku, haiku_title"` or `"question, num: int -> answer"`). Field names are read by the LM — name them semantically.

Class-based signatures add a docstring (used as task instructions) and per-field descriptions:

```python
class BasicQA(dspy.Signature):
    """Answer questions with short factoid answers."""

    question: str = dspy.InputField()
    answer: str = dspy.OutputField(desc="often between 1 and 5 words")
```

Richer types are supported (`int`, `float`, `bool`, `list[str]`, nested Pydantic models, `dspy.Image`, …). See [01-signatures-and-modules](references/01-signatures-and-modules.md) for field types, constraints, and adapter behavior.

## Modules

Modules define *how* a signature is satisfied. The foundational ones:

- `dspy.Predict(sig)` — one LM call per invocation
- `dspy.ChainOfThought(sig)` — reasoning then answer; in 3.5 the `reasoning` field is `dspy.Reasoning` or `None` (native reasoning preferred, fallback requests a short plan), not always a string. Opt into an explicit text plan with `rationale_field_type=str`.
- `dspy.ReAct(sig, tools=[...], max_iters=N)` — general tool-using agent loop; in 3.5 it uses structured `dspy.History` and a typed `submit` tool (see below)
- `dspy.RLM(sig)` — sandboxed Python REPL reasoning with optional tools; also returns `result.history`
- `dspy.Retrieve(k=N)` — retrieval over the configured retriever (`dspy.configure(rm=...)`)
- `dspy.BestOfN(module, N, reward_fn, threshold)` / `dspy.Refine(...)` — sample-and-select wrappers (replace the old `Suggest`/`Assert`)

Compose modules into programs by subclassing `dspy.Module`: define submodules in `__init__`, control flow in `forward`, return a `dspy.Prediction`. Example pattern:

```python
class HaikuEnsemble(dspy.Module):
    def __init__(self, n: int = 3):
        super().__init__()
        self.writer = dspy.ReAct("location, mood, num_haikus: int -> haikus: list[str]", tools=[...])
        self.judge = dspy.ChainOfThought("location, mood, candidates: list[str] -> best_index: int")

    def forward(self, location: str, mood: str):
        candidates = self.writer(location=location, mood=mood, num_haikus=self.n).haikus
        verdict = self.judge(location=location, mood=mood, candidates=candidates)
        return dspy.Prediction(haiku=candidates[verdict.best_index])
```

## Data, metrics, evaluation

```python
trainset = [dspy.Example(question=q, answer=a).with_inputs("question") for q, a in data]

def my_metric(example, pred, trace=None):
    return 1.0 if example.answer.lower() in pred.answer.lower() else 0.0

from dspy.evaluate import Evaluate
evaluate = Evaluate(devset=devset, metric=my_metric, num_threads=8, display_progress=True)
print(evaluate(program))   # returns (num_successful, num_total)
```

For GEPA, return `dspy.Prediction(score=float, feedback="why it failed")` from the metric so the optimizer's reflection LM can learn from *why*, not just the score. Built-in metrics include `answer_exact_match`, `answer_passage_match`, `SemanticF1`, and `CompleteAndGrounded`.

## Optimization

Every optimizer takes a `metric` and exposes `.compile(student, trainset=...)`, returning a **new** compiled copy (the student is not mutated). Quick map:

| Optimizer | Tunes | Notes |
|---|---|---|
| `LabeledFewShot(k)` | demos only | instant, uses labeled fields as demos |
| `BootstrapFewShot` | demos | runs the student, keeps traces that pass the metric |
| `BootstrapFewShotWithRandomSearch` | demos | random search over demo sets; add `valset` |
| `MIPROv2(metric, auto="light")` | instructions + demos | `auto` in light/medium/heavy tunes budget |
| `COPRO(prompt_model=...)` | instructions | LM-proposed prompt search |
| `SIMBA(metric, max_steps, max_demos)` | instructions + demos | stochastic mini-batch ascent |
| `GEPA` | instructions (and Flex code) | reflective; metric feedback drives rewrites |
| `BootstrapFinetune` | weights | fine-tunes a target model from bootstrapped traces |

Rule of thumb: demo-tuning tends to overfit, instruction-tuning tends to generalize; most teams start prompt-only and graduate to finetune only when prompt-only plateaus. Compile once, save, reload — that's what amortizes optimizer cost. Details in [02-optimization](references/02-optimization.md).

## Saving and loading (3.5 is restrictive)

```python
program.save("v1.json")                          # state-only JSON; diff-friendly default
loaded = MyProgram(); loaded.load("v1.json")     # needs your class definitions

program.save("dir/", save_program=True)          # full program via cloudpickle
restored = dspy.load("dir/")                     # no source needed on load side

# Pickle forms require explicit trust flags:
loaded.load("v1.pkl", allow_pickle=True)
# api_base/base_url/model_list are stripped unless allow_unsafe_lm_state=True
```

API keys are never serialized. 3.5 change: restricted disk loading is the default — unlisted custom types and old NumPy pickles regenerate instead of loading; keep restrictions on and allow only trusted `safe_types`. Old cache entries (v1) miss under canonical v2 caches; budget for recomputation. Full migration notes in [04-migration-3-5](references/04-migration-3-5.md).

## Gotchas

- **Default adapter is now XML** — 3.5's default is `XMLAdapter(use_native_function_calling=True)`, not `ChatAdapter`. Prompts, demos, and parsing change even with the same signature; re-evaluate quality after upgrading. Scalar values are literal text (not XML-escaped); `<value/>` means null for nullable fields, `<value></value>` an empty string.
- **`dspy.ReAct` is not 3.4's ReAct** — `result.trajectory` is gone; use `result.history.messages` and `result.termination_reason`. Multiple tools run sequentially per turn; `max_iters` counts turns, not tool calls. A failed final submission raises. Old optimized agents must be recompiled.
- **Removed in 3.5** — `CodeAct`, `ProgramOfThought`, `lm(messages=...)`, `Image.from_file()`/`Audio.from_file()` (use `from_path()`), `Tool.format_as_litellm_function_call()` (use `as_function_tool()`). `ReActV2` and `TwoStepAdapter` are deprecated for removal in 3.6 — use `dspy.ReAct`; replace TwoStep with `JSONAdapter()`/`XMLAdapter()`.
- **`ChainOfThought.reasoning` is typed, not str** — it's `dspy.Reasoning` or `None`. Update string-based metrics and feedback consumers; opt into text with `rationale_field_type=str` (this opts into a text field, not the old step-by-step prompt).
- **Re-evaluate every optimized program after upgrading** — 3.5 changes prompts, defaults, and integration APIs even when your signature stays the same.
- **`num_retries=0` disables LM retries, not adapter fallback** — Chat/XML adapters can still make an extra JSON-format call after a parse failure; set `use_json_adapter_fallback=False` for strict call budgets.
- **Field descriptions are invisible to optimizers** — optimizers rewrite instructions and demos but never touch field names/descriptions; a poorly chosen name can't be fixed by compilation.
- **`dspy.configure(lm=...)` is process-global** — use `dspy.context(lm=...)` for scoped overrides in multi-model code.

## References

- [01-signatures-and-modules](references/01-signatures-and-modules.md) — signature types, adapters, module variants, tools and ReAct/RLM details
- [02-optimization](references/02-optimization.md) — choosing an optimizer, GEPA in depth, metrics patterns
- [03-data-evaluation](references/03-data-evaluation.md) — Examples, datasets, Evaluate, usage tracking, streaming and async
- [04-migration-3-5](references/04-migration-3-5.md) — 3.4 → 3.5 breaking changes, removed APIs, save/load and caching restrictions
