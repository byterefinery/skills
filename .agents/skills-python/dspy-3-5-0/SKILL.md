---
name: dspy-3-5-0
description: Framework for programming language models with declarative signatures, composable modules, ReAct agents, and prompt optimizers (GEPA, MIPROv2). Use when building DSPy programs, optimizing prompts, or composing LM pipelines.
license: MIT
compatibility: Requires Python 3.10+; install via `pip install dspy` or `uv add dspy`. Optional LiteLLM compatibility engine via `dspy[litellm]`.
---

# dspy 3.5.0

## Overview

DSPy (Declarative Self-improving Python) is a framework for _programming—rather than prompting—language models_. Instead of brittle prompts, you write compositional Python code and use DSPy to teach your LM to deliver high-quality outputs. It supports building simple classifiers, sophisticated RAG pipelines, and agent loops, with built-in algorithms for optimizing prompts and weights.

Core abstractions:
- **Signature** — declarative task definition (inputs → outputs), like a function type
- **Module** — composable unit that implements a call-time strategy (`Predict`, `ChainOfThought`, `ReAct`, custom)
- **LM** — language model connection (`dspy.LM("provider/model")`)
- **Optimizer (Teleprompter)** — algorithm that improves instructions, demos, or weights automatically

## Usage

### Installation and LM setup

```python
import dspy

# Configure a language model globally
lm = dspy.LM("openai/gpt-5-nano", api_key="YOUR_OPENAI_API_KEY")
dspy.configure(lm=lm)

# Or for Anthropic, Gemini, etc.
dspy.configure(lm=dspy.LM("anthropic/claude-sonnet-4-5-20250929"))
dspy.configure(lm=dspy.LM("gemini/gemini-2.5-pro"))

# Override locally with context
with dspy.context(lm=dspy.LM("openai/gpt-5.4")):
    result = some_module(...)
```

Supported native providers: OpenAI, Anthropic, Google AI Studio (`gemini/`), Azure OpenAI (`azure/`), Vertex AI (`vertex:`), Ollama (`ollama_chat/`). For OpenAI-compatible servers, pass `api_base=` and `api_key=`.

### First program — string signature + Predict

```python
haiku_gen = dspy.Predict("subject -> haiku")
result = haiku_gen(subject="computer science")
print(result.haiku)
```

String signatures use `"input1, input2 -> output1, output2"` format. Field names matter — the LM reads them. Add types with `name: type`:

```python
bot = dspy.Predict("location, mood, contains_pun: bool -> haikus:list[str]")
```

### Class-based signatures

For richer control (docstrings, field descriptions, custom types):

```python
from typing import Literal

class HaikuBot(dspy.Signature):
    """Write a classical haiku given the provided inputs."""
    location: str = dspy.InputField(desc="The setting of the poem")
    mood: str = dspy.InputField()
    season: Literal["spring", "summer", "autumn", "winter"] = dspy.InputField()
    haiku: str = dspy.OutputField()

bot = dspy.Predict(HaikuBot)
result = bot(location="a quiet library", mood="mysterious", season="autumn")
```

The class docstring becomes the task instruction. Field descriptions add nuance. `Literal` types constrain both input and output parsing.

### Composing modules

Custom modules subclass `dspy.Module` with `__init__` (define submodules) and `forward` (control flow):

```python
class HaikuEnsemble(dspy.Module):
    def __init__(self, n: int = 3):
        super().__init__()
        self.writer = dspy.ChainOfThought("location, mood -> haikus:list[str]")
        self.judge = dspy.ChainOfThought(
            "location, mood, candidates:list[str] -> best_index:int"
        )

    def forward(self, location: str, mood: str) -> dspy.Prediction:
        candidates = self.writer(location=location, mood=mood).haikus
        verdict = self.judge(location=location, mood=mood, candidates=candidates)
        return dspy.Prediction(haiku=candidates[verdict.best_index])
```

Built-in module variants: `dspy.Predict`, `dspy.ChainOfThought`, `dspy.ReAct`, `dspy.Parallel`, `dspy.Refine`, `dspy.BestOfN`, `dspy.MultiChainComparison`.

### ReAct agents with tools

Tools are plain Python functions with type hints and docstrings:

```python
import wikipedia

def wikipedia_search(query: str) -> list[str]:
    """Search Wikipedia for the given query and return a list of page titles."""
    return wikipedia.search(query)

def get_wikipedia_page(title: str) -> str:
    """Get the content of a Wikipedia page given its title."""
    return wikipedia.page(title).content

agent = dspy.ReAct(HaikuBot, tools=[wikipedia_search, get_wikipedia_page], max_iters=5)
result = agent(location="Camp Meeker", mood="pensive", season="summer")
```

ReAct returns the signature's typed outputs plus `history` (a `dspy.History` with structured events) and `termination_reason`. The model calls an internal `submit` tool to end the loop. `max_iters` limits model turns, not individual tool calls. For async tools use `await agent.acall(...)`.

### Evaluation metrics

A metric is a Python function `(example, prediction) -> float` (0.0–1.0):

```python
def my_metric(example, prediction) -> float:
    if example.answer.lower() in prediction.answer.lower():
        return 1.0
    return 0.0
```

For GEPA specifically, return `dspy.Prediction(score=..., feedback="...")` to provide text feedback that guides instruction rewriting.

Prepare examples with `dspy.Example(...).with_inputs("field1", "field2")`. Split into train/val/test before compiling.

### Optimization (compiling)

All optimizers call `.compile(student, trainset=..., valset=...)` and return a new compiled copy (original is not mutated):

```python
# Simple baseline — no LM calls during compile
optimizer = dspy.LabeledFewShot(k=16)
compiled = optimizer.compile(program, trainset=train)

# Bootstrap successful traces as demos
optimizer = dspy.BootstrapFewShot(metric=my_metric, max_bootstrapped_demos=4)
compiled = optimizer.compile(program, trainset=train, valset=val)

# GEPA — evolutionary instruction search with reflection (needs feedback metric)
optimizer = dspy.GEPA(
    metric=gepa_metric,       # returns Prediction(score, feedback)
    reflection_lm=dspy.LM("openai/gpt-5.4"),
    auto="light",             # "light" | "medium" | "heavy"
    num_threads=2,
)
compiled = optimizer.compile(program, trainset=train, valset=val)

# MIPROv2 — Bayesian search over instructions + demos
optimizer = dspy.MIPROv2(metric=my_metric, auto="light")
compiled = optimizer.compile(program, trainset=train, valset=val)
```

Optimizer selection guide:
- **LabeledFewShot** — zero-cost baseline; sample labeled examples as demos
- **BootstrapFewShot / BootstrapRS** — run program on trainset, keep successful traces as demos
- **COPRO** — breadth-first instruction search (lightweight)
- **GEPA** — reflective instruction evolution; needs `Prediction(score, feedback)` metric + strong `reflection_lm`
- **MIPROv2** — joint instruction + demo optimization via Bayesian search
- **BootstrapFinetune** — fine-tunes the LM on bootstrapped traces (needs `.finetune()` support)

### Saving and loading

```python
# State-only (default) — small JSON, requires re-instantiating the class
compiled.save("program.json")
fresh = MyProgram()
fresh.load("program.json")

# Whole program — pickled directory, no class definition needed at load time
compiled.save("program_dir/", save_program=True)
loaded = dspy.load("program_dir/")
```

Prefer state-only JSON: small, human-readable, diffable in version control. Use `save_program=True` only when the loading environment won't have your Python class definitions.

### Inspecting calls

```python
# View the last N LM calls (prompt + response)
dspy.inspect_history(n=1)
```

## Gotchas

- **Field names are prompts** — the LM reads field names to infer intent. `research_request` outperforms `request`. Naming is the cheapest optimization available; rename freely since signatures are easy to edit.
- **`with_inputs()` controls what's passed at call time** — for a QA dataset with `(question, answer)`, call `.with_inputs("question")` so only the question goes to the program and `answer` is held back for the metric. Forgetting this leaks labels into inference.
- **GEPA requires `Prediction(score, feedback)` metric shape** — returning a bare float works for most optimizers but GEPA specifically reads `feedback` to guide instruction rewriting. Using a scalar-only metric with GEPA wastes its main advantage.
- **`.compile()` returns a new copy** — the original student module is never mutated. You can run multiple optimizers on the same student and compare results. The `_compiled=True` flag on submodules prevents nested re-optimization.
- **`dspy.context()` does not propagate to `threading.Thread`** — context overrides use `contextvars`, which copy across `asyncio.create_task` but NOT across raw threads or `ThreadPoolExecutor`. Use `dspy.Parallel` for thread-safe parallelism, or manually capture and re-set `dspy.settings.thread_local_overrides.get()`.
- **ReAct 3.5 breaking changes** — the old trajectory/extractor/truncation APIs are gone. `dspy.ReActV2` is a deprecated compatibility subclass that warns on construction and will be removed in 3.6. Old optimized state must be recompiled for the new predictor schema.
- **No LiteLLM runtime dependency in 3.5** — the current LM integration uses bundled native lm15 engines. `engine="auto"` (default) prefers native and may select optional LiteLLM for unsupported routes. The `dspy[litellm]` extra is only needed for compatibility paths.
- **Compile once, save, reload** — `.compile()` can spend hundreds of dollars in LM calls. The economics work only when you compile once per program version and serve the saved artifact many times. Don't recompile on every deployment.
- **Demo-tuning overfits; instruction-tuning generalizes** — demos learned on 50 examples describe that specific trainset. Instruction rewrites capture patterns at a higher level. If your evaluation set is small or skewed, lean toward instruction optimizers (GEPA, COPRO, MIPROv2).
- **`max_iters` limits model turns, not tool calls** — each turn can request multiple tools which execute sequentially. If the budget runs out before `submit`, ReAct makes one final submission attempt and raises if that fails.

## References

- [01-signatures-and-modules](references/01-signatures-and-modules.md) — Signature types, field typing, module composition patterns
- [02-optimizers](references/02-optimizers.md) — Full optimizer reference with parameters and selection criteria
- [03-react-and-tools](references/03-react-and-tools.md) — ReAct agent loop, tool authoring, history inspection
