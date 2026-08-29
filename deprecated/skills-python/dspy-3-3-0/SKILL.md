---
name: dspy-3-3-0
description: DSPy 3.3.0 — programming, not prompting, foundation models. Use when building modular LLM programs with signatures, Predict/ChainOfThought/ReAct modules, dspy.LM configuration, adapters, tools and agents, metrics and Evaluate, and optimizers like BootstrapFewShot, MIPROv2, GEPA, or BootstrapFinetune. Triggers on dspy, dspy.LM, dspy.configure, signature, ChainOfThought, ReAct agent, MIPROv2, GEPA optimizer, prompt optimization, compile, dspy.ReAct, save/load programs.
license: MIT
compatibility: >
  Python 3.10–3.14. Hard deps — litellm>=1.65.8, openai>=1.66.2, pydantic>=2.0,
  gepa[dspy]==0.1.1, diskcache, tenacity. Optional extras — anthropic, weaviate,
  mcp, langchain, optuna, numpy.
metadata:
  tags:
    - python
    - ml
    - llm
    - prompt-optimization
    - agents
---

# dspy 3.3.0

## Overview

DSPy (Declarative Self-improving Python) is the framework for **programming — rather than prompting — language models**. Instead of hand-tuned prompt strings, you write compositional Python: declarative **signatures** (input/output specs), **modules** (learnable building blocks like `Predict`, `ChainOfThought`, `ReAct`), and a **metric** (a plain Python function that grades outputs). DSPy's optimizers then tune the prompts and/or weights of every step to maximize that metric.

**Core abstractions:**

- **Signatures** — `"question -> answer"` or a class with `dspy.InputField`/`dspy.OutputField`; field names carry semantic meaning
- **Modules** — `dspy.Predict`, `dspy.ChainOfThought`, `dspy.ReAct` (tool-using agent), `dspy.ProgramOfThought`, `dspy.MultiChainComparison`, `dspy.RLM`, `dspy.Refine`, `dspy.Flex`, plus `dspy.majority`/`dspy.Parallel`/`dspy.BestOfN`; composed into bigger `dspy.Module`s
- **`dspy.LM`** — model via LiteLLM `provider/model` strings; any provider works (OpenAI, Anthropic, Gemini, Vertex, Ollama, any OpenAI-compatible endpoint)
- **`dspy.configure` / `dspy.context`** — process-wide defaults vs. scoped overrides (LM, adapter, flags)
- **Adapters** — `ChatAdapter` (default, `[[ ## field ## ]]` markers, universal), `JSONAdapter` (native structured output, lower latency), `TwoStepAdapter`
- **Metrics** — functions `(example, pred, trace=None) -> score`; the trace enables intermediate-step checks during optimization
- **Optimizers** — `BootstrapFewShot`, `BootstrapFewShotWithRandomSearch`, `COPRO`, `MIPROv2`, `GEPA` (reflection with textual feedback), `SIMBA`, `KNNFewShot`, `BootstrapFinetune` (distills prompts into weight updates), `Ensemble`, `BetterTogether`
- **Data** — `dspy.Example` objects with `with_inputs(...)`; `dspy.Evaluate` for parallel evaluation

**Dependencies:** `litellm>=1.65.8`, `openai>=1.66.2`, `pydantic>=2.0`, `gepa[dspy]==0.1.1`, `diskcache>=5.6.0`, `json-repair`, `tenacity>=8.2.3`, `anyio`, `cachetools`, `cloudpickle`, `regex`, `orjson`, `tqdm`, `requests`.

## Installation

```bash
pip install dspy
# extras
pip install "dspy[mcp]"        # MCP server tools
pip install "dspy[anthropic]"  # native Anthropic
pip install "dspy[optuna]"     # Optuna-based search
```

Docs: https://dspy.ai

## Usage

### Setup — configure the LM once

```python
import dspy

lm = dspy.LM("openai/gpt-4o-mini", api_key="sk-...")  # any LiteLLM provider/model string
dspy.configure(lm=lm)                                  # process-wide default
```

Test the connection directly: `lm("Say this is a test!")` returns `['...']`. Scoped overrides: `with dspy.context(lm=..., adapter=...): ...`.

### First program

```python
classify = dspy.Predict("sentence -> sentiment: bool")
resp = classify(sentence="it's a charming journey")
resp.sentiment  # True

# ChainOfThought adds a `reasoning` field before the signature outputs
cot = dspy.ChainOfThought("question -> answer", temperature=0.7)
resp = cot(question="What's great about ColBERT?")
print(resp.reasoning, resp.answer)

# Tool-using agent — plain Python functions with type hints + docstrings
def search_web(query: str) -> str:
    """Search the web for information."""
    ...

react = dspy.ReAct("question -> answer", tools=[search_web], max_iters=5)
react(question="What's the weather in Tokyo?")
```

Compose modules into a program by subclassing `dspy.Module` and calling the submodules in `forward` (or `__call__`) — see [02-modules](references/02-modules.md).

### Metrics, evaluation, and optimization

```python
def validate_answer(example, pred, trace=None):
    return example.answer.lower() == pred.answer.lower()

trainset = [dspy.Example(question=..., answer=...).with_inputs("question") for ...]

# Evaluate
from dspy.evaluate import Evaluate
Evaluate(devset=devset, num_threads=4, display_progress=True, display_table=5)(program, metric=validate_answer)

# Optimize — same interface for all optimizers
optimizer = dspy.MIPROv2(metric=validate_answer, auto="light", num_threads=4)
optimized = optimizer.compile(program, trainset=trainset)
```

Optimizer choice and budgets (typical run ~$2, ~10 min): see [07-optimizers](references/07-optimizers.md). GEPA metrics may return `dspy.Prediction(score=..., feedback="why")` to feed reflective instruction rewriting.

### Save and reload

```python
optimized.save("program.json")          # state only (instructions + demos) — small, diffable
optimized.save("program/", save_program=True)  # full pickled program — contains executable code

loaded = dspy.load("program/")                      # whole-program form
fresh = MyProgram(); fresh.load("program.json")     # state-only form — re-instantiate first
```

The save file never contains LM credentials — reconfigure the LM after loading. Details in [08-saving-loading-async](references/08-saving-loading-async.md).

## Gotchas

- **`dspy.configure` must run before any module call** — otherwise `dspy.LMNotConfiguredError`. And only the thread/async task that first called `dspy.configure` may call it again; from other threads or tasks use `with dspy.context(lm=...)` instead.
- **LM caching is ON by default** — `dspy.LM(..., cache=True)` returns identical outputs for identical inputs. Use `cache=False` for fresh calls, or pass a unique `rollout_id` with a non-zero `temperature` to force a new request while still caching it. Changing only `rollout_id` at `temperature=0` does nothing.
- **Metric `trace` semantics flip** — when `trace is None` (evaluation/optimization scoring) return a float score; when `trace is not None` (bootstrapping demos) return a strict bool gate. Returning the wrong shape silently degrades compiled programs.
- **`dspy.Assert`/`dspy.Suggest` are deprecated and unsupported** — do not write new code against them; use the `dspy.Refine` module (best-of-N with reward feedback) or metric-gated retries instead.
- **`dspy.ChainOfThought` injects a `reasoning` field** — the prediction contains `reasoning` plus your signature outputs; `dspy.Predict` does not add it.
- **Adapter choice matters** — default `ChatAdapter` is universal and retries with `JSONAdapter` on parse failure, but adds boilerplate output tokens (latency). `JSONAdapter` needs native structured-output support (weak on small local models) and is lower-latency. `ChatAdapter` defaults to `use_native_function_calling=False`, `JSONAdapter` to `True`.
- **Vertex AI prefixes and kwargs are exact** — use `vertex_ai/<model>` (not `gemini/`, which routes to the API-key Gemini endpoint) and `vertex_project`/`vertex_location` (bare `project`/`location` are silently ignored by LiteLLM).
- **Tools need type hints and docstrings** — `dspy.Tool(fn)` derives name, parameter schema, and description from the function signature and docstring; untyped parameters and missing docstrings degrade agent tool selection.
- **`ReAct` defaults to `max_iters=20`** — unbounded-looking tool loops burn tokens; set `max_iters` explicitly. An implicit `finish` tool is always added.
- **Optimizer cost scales with data and trials** — a typical small run is ~$2/10 min; large LMs or big trainsets cost tens of dollars. Use `auto="light"` mode and `num_threads` to control budget.
- **GEPA wants feedback, not just scores** — metrics that return `dspy.Prediction(score=..., feedback="...")` let the reflection LM learn *why* outputs fail; plain float scores leave most of GEPA's power unused.
- **Saved programs don't carry LM config** — `save`/`dspy.load` exclude API keys, model choice, and temperature. Configure the LM again after loading; the same checkpoint then targets whichever model you point it at.
- **`save_program=True` contains executable Python** — the directory form pickles your module classes; only `dspy.load` it from trusted sources.
- **Signature field names are prompt content** — names like `question`/`answer` vs `query`/`response` shape model behavior. Pick meaningful names once and let the optimizer tune wording; don't hand-hack keywords.
- **Type mismatches only warn** — calling `predict(number="42")` on an `int` field logs a warning, not an error. Disable with `dspy.configure(warn_on_type_mismatch=False)`.
- **`Example` is not a dict** — access fields via `.` and mark inputs with `.with_inputs("question")`; `inputs()`/`labels()` split the keys. Passing an Example to a module uses its input keys.

## References

- [01-signatures](references/01-signatures.md) — inline and class-based signatures, instructions, field types, type checking
- [02-modules](references/02-modules.md) — Predict, ChainOfThought, ReAct/ReActV2, ProgramOfThought, RLM, Refine, Flex, composition, usage tracking
- [03-language-models](references/03-language-models.md) — dspy.LM providers, configure/context, caching, rollout_id, history, errors, Responses API, custom LMs
- [04-adapters](references/04-adapters.md) — ChatAdapter, JSONAdapter, TwoStepAdapter, native function calling, inspecting formatted messages
- [05-tools-and-agents](references/05-tools-and-agents.md) — dspy.Tool, ToolCalls, manual tool handling, async tools, MCP servers
- [06-data-and-metrics](references/06-data-and-metrics.md) — Example, with_inputs, train/dev/test sets, metric contracts, AI-feedback metrics, Evaluate
- [07-optimizers](references/07-optimizers.md) — all optimizers, choice guidance, compile interface, GEPA feedback, MIPROv2 auto budgets, finetuning
- [08-saving-loading-async](references/08-saving-loading-async.md) — save/load modes, dspy.load, async execution, thread safety, production notes
