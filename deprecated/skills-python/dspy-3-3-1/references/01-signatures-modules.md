# Signatures and modules in depth

## Signatures

A signature declares *what* a module does (inputs → outputs). It is declarative: it does not specify how the LM is asked to do it — the adapter and optimizer handle that. Field names matter semantically (`question` ≠ `answer`, `sql_query` ≠ `python_code`).

### Inline signatures

```python
"question -> answer"                                  # defaults are str
"sentence -> sentiment: bool"
"context: list[str], question: str -> answer: str"
"question, choices: list[str] -> reasoning: str, selection: int"

# add instructions (may reference runtime variables)
toxicity = dspy.Predict(
    dspy.Signature("comment -> toxic: bool",
                   instructions="Mark as 'toxic' if the comment includes insults, harassment, or sarcastic derogatory remarks.")
)
```

### Class-based signatures

For docstrings, per-field descriptions, and complex types:

```python
from typing import Literal

class Emotion(dspy.Signature):
    """Classify emotion."""

    sentence: str = dspy.InputField()
    sentiment: Literal['sadness', 'joy', 'love', 'anger', 'fear', 'surprise'] = dspy.OutputField()

class CheckCitationFaithfulness(dspy.Signature):
    """Verify that the text is based on the provided context."""

    context: str = dspy.InputField(desc="facts here are assumed to be true")
    text: str = dspy.InputField()
    faithfulness: bool = dspy.OutputField()
    evidence: dict[str, list[str]] = dspy.OutputField(desc="Supporting evidence for claims")
```

### Type resolution

Supported annotations: basic types (`str`, `int`, `bool`, `float`), typing-module types (`list[str]`, `dict[str, int]`, `Optional[float]`, `Union[str, int]`), `Literal[...]`, pydantic `BaseModel` subclasses, dot notation for nested types (`"query: MyContainer.Query -> score: MyContainer.Score"`), and special DSPy types (`dspy.Image`, `dspy.History`, `dspy.Code`). Non-primitive output fields get their JSON schema injected into the prompt automatically.

### Input type checking

DSPy validates passed inputs against the declared types and logs a warning on mismatch (both inline and class signatures). Disable with `dspy.configure(warn_on_type_mismatch=False)`.

### Optional output fields

Output fields are **required** by default: if the LM response lacks a declared output, the adapter raises `AdapterParseError`. A field becomes optional when it has a default value, a `default_factory`, or an annotation allowing `None`. Precedence when the LM omits the field: explicit default → factory result → `None`.

```python
class Extract(dspy.Signature):
    """Extract structured information from text."""

    text: str = dspy.InputField()
    title: str = dspy.OutputField()                            # required
    note: str | None = dspy.OutputField(default="No note")     # missing -> "No note"
    tags: list[str] = dspy.OutputField(default_factory=list)   # missing -> []
    subtitle: str | None = dspy.OutputField()                  # missing -> None
```

Input fields: a missing input with a default is filled into the prompt; an input whose annotation allows `None` is omitted from the prompt; a missing required input logs a warning.

### Style

- Multiple modules (except bare `dspy.Predict`) expand the signature internally — e.g., `ChainOfThought` adds a `reasoning` field.
- Start with plain field names (`document -> summary` is fine); leave keyword hacking to the compiler.

## Built-in modules

| Module | What it does |
|---|---|
| `dspy.Predict` | Basic predictor; signature unmodified; stores instructions and demos |
| `dspy.ChainOfThought` | Injects a `reasoning` field before outputs |
| `dspy.ProgramOfThought` | LM writes code; execution result becomes the answer (needs the `deno` extra) |
| `dspy.CodeAct` | `ReAct` + code sandbox; tools enter the sandbox as Python functions |
| `dspy.ReAct` | Reason+act agent over tools (`max_iters=20` default) |
| `dspy.ReActV2` | Updated ReAct implementation |
| `dspy.MultiChainComparison` | `forward(completions, **kw)` — judges pre-generated drafts |
| `dspy.BestOfN` | Samples a wrapped module N times (rollout IDs), returns best by reward |
| `dspy.Refine` | Best-of-N with auto-generated feedback fed back on failure |
| `dspy.Parallel` | Runner (not a Module): parallel `(module, example)` pairs |
| `dspy.KNN` | kNN demo selection |
| `dspy.RLM` | Experimental recursive LM driving a sandboxed Python REPL |
| `dspy.Flex` | Experimental: optimizer discovers the program structure |
| `dspy.majority` | Function (no LM call): most-frequent normalized value of a prediction list |

`BestOfN` and `Refine` deep-copy the wrapped module per attempt and swap in an LM copy with `rollout_id = start + i` and `temperature=1.0` — the rollout ID defeats the cache, the temperature makes sampling meaningful. Their `reward_fn(args, pred) -> float` is scored at inference time (no gold example needed).

### ReAct and tools

```python
def search(query: str) -> list[str]:
    """Retrieves abstracts from Wikipedia."""
    return dspy.ColBERTv2(url="http://20.102.90.50:2017/wiki17_abstracts")(query, k=3)

react = dspy.ReAct("question -> answer", tools=[search], max_iters=10)
pred = react(question="...")
pred.trajectory   # full history of reasoning + tool calls
```

Tools are plain callables with type hints and docstrings (the docstring is what the LM sees). For manual control instead of `dspy.ReAct`, use the `dspy.Tool`, `dspy.ToolCalls`, and `dspy.ToolCallResults` types in your own signature and execute tool calls yourself.

### `dspy.Refine` (assertions' replacement)

```python
refined = dspy.Refine(module=my_module, N=4, reward_fn=my_reward, threshold=0.8, fail_count=3)
```

Runs the module up to `N` times with different rollout IDs at `temperature=1.0`, returns the first prediction above `threshold` (or the highest-reward one). If none pass, it generates feedback to improve subsequent predictions; after `fail_count` failures it raises.

### Configuration and rollouts

- LM kwargs at init: `dspy.Predict(sig, temperature=1.0, max_tokens=2000)` — defaults for every call.
- Per-call override: `predict(question="...", config={"temperature": 1.0, "rollout_id": 5})`.
- `rollout_id` is forwarded to the LM, included in the cache hash, and stored in `lm.history`.

### Composition

Subclass `dspy.Module`, store predictors in `__init__`, implement `forward` (or `__call__`). Plain Python control flow; `module.batch(examples, num_threads=...)` for datasets. Compiled submodules carry `_compiled=True` so outer optimizers leave them alone — enabling optimize-inner → embed → optimize-outer.
