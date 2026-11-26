# Signatures and Modules — Deep Reference

## Signature formats

### String signatures

```python
# Simple
dspy.Predict("question -> answer")

# Multiple inputs/outputs (comma-separated)
dspy.Predict("location, mood -> haiku, haiku_title")

# Typed fields (name: type)
dspy.Predict("location, contains_pun: bool -> haikus:list[str]")

# Supported inline types: str, int, float, bool, list[str], list[int], etc.
```

String signatures are parsed into a Signature class with input/output fields defaulting to `str`. A default instruction is generated: "Given the fields `X`, produce the fields `Y`."

### Class-based signatures

```python
from typing import Literal, Optional
from pydantic import BaseModel

class MyTask(dspy.Signature):
    """One-line task description (becomes the instruction)."""
    input_field: str = dspy.InputField(desc="What this field means")
    constrained: Literal["a", "b", "c"] = dspy.InputField()
    optional_in: Optional[str] = dspy.InputField(default=None)
    output: str = dspy.OutputField(desc="Expected output format")
```

Key rules:
- Class docstring → task instruction in the prompt
- `dspy.InputField(desc=...)` → field description shown to LM
- `dspy.OutputField(desc=...)` → output field description
- `Literal[...]` constrains both call-time validation and response parsing
- Pydantic models, TypedDicts, and dataclasses work as field types for structured outputs
- Field descriptions are NOT touched by optimizers — only the docstring (instruction) is optimized

### Adapter rendering

The default adapter is `XMLAdapter`. It renders signatures into:
1. System message: field list with types/descriptions + output format template + instruction
2. User message: input fields wrapped in XML tags (`<field_name>value</field_name>`)

Other adapters: `JSONAdapter`, `ChatAdapter`, `TwoStepAdapter`. Switch with `dspy.configure(adapter=dspy.adapters.JSONAdapter())` or per-context.

## Module types

| Module | Purpose |
|--------|---------|
| `dspy.Predict(sig)` | Single LM call, no reasoning chain |
| `dspy.ChainOfThought(sig)` | Predict + explicit reasoning field before output |
| `dspy.ReAct(sig, tools=[...])` | Agentic loop with tool calling and `submit` |
| `dspy.Parallel([mods])` | Run modules in parallel, return list of predictions |
| `dspy.Refine(base, refine_sig)` | Generate then iteratively refine output |
| `dspy.BestOfN(mod, n=3)` | Generate N candidates, select best via metric |
| `dspy.MultiChainComparison` | Run multiple module variants, compare |

## Custom module patterns

```python
class MyProgram(dspy.Module):
    def __init__(self):
        super().__init__()
        # Submodules must be dspy.Module instances assigned in __init__
        self.step1 = dspy.ChainOfThought("query -> summary")
        self.step2 = dspy.Predict("summary, question -> answer")

    def forward(self, query: str, question: str) -> dspy.Prediction:
        # Control flow is plain Python
        summary = self.step1(query=query).summary
        if len(summary) < 50:
            # Branching, retry loops, conditionals all work
            summary = self.step1(query=query).summary  # retry
        result = self.step2(summary=summary, question=question)
        return dspy.Prediction(answer=result.answer)
```

Rules:
- Submodules must be assigned in `__init__` (not in `forward`) for optimizer tracking
- `forward` receives the same kwargs as the module is called with
- Return a `dspy.Prediction` with named fields
- Nested modules work — optimizers recurse into `named_parameters()`

## dspy.Example and datasets

```python
# Create examples
example = dspy.Example(question="What is X?", answer="X is Y").with_inputs("question")

# From a list of dicts
examples = [dspy.Example(**row).with_inputs("question") for row in data]

# Split
n = len(examples)
train, val, test = examples[:int(n*0.75)], examples[int(n*0.75):int(n*0.875)], examples[int(n*0.875):]
```

`with_inputs(...)` declares which fields are inputs at call time. All other fields are held for the metric.

## dspy.Evaluate

```python
evaluator = dspy.Evaluate(devset=val, metric=my_metric)
score = evaluator(program)  # returns float (mean score)
```

Also supports `n=...` for confidence intervals and `display=True` for progress.
