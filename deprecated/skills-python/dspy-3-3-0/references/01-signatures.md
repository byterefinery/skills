# Signatures

A signature is a declarative specification of a DSPy module's input/output behavior. It tells the LM *what* to do, not *how* to ask. Field names carry semantic roles — `question` ≠ `query`, `sql_query` ≠ `python_code` — so pick meaningful names once and leave wording to the optimizer.

## Inline signatures

```python
dspy.Predict("question -> answer")                          # default type is str
dspy.Predict("sentence -> sentiment: bool")
dspy.Predict("context: list[str], question: str -> answer: str")
dspy.Predict("question, choices: list[str] -> reasoning: str, selection: int")
```

Instructions can be attached inline via the `instructions` kwarg (may use runtime variables):

```python
toxicity = dspy.Predict(
    dspy.Signature(
        "comment -> toxic: bool",
        instructions="Mark as 'toxic' if the comment includes insults, harassment, or sarcastic derogatory remarks.",
    )
)
```

## Class-based signatures

Use these to document the task (docstring) and annotate fields with `desc`:

```python
from typing import Literal

class Emotion(dspy.Signature):
    """Classify emotion."""

    sentence: str = dspy.InputField()
    sentiment: Literal['sadness', 'joy', 'love', 'anger', 'fear', 'surprise'] = dspy.OutputField()

classify = dspy.Predict(Emotion)
classify(sentence="i started feeling a little vulnerable...")
```

`desc=` on an `InputField` hints at the input's nature; on an `OutputField` it constrains the output:

```python
class CheckCitationFaithfulness(dspy.Signature):
    """Verify that the text is based on the provided context."""

    context: str = dspy.InputField(desc="facts here are assumed to be true")
    text: str = dspy.InputField()
    faithfulness: bool = dspy.OutputField()
    evidence: dict[str, list[str]] = dspy.OutputField(desc="Supporting evidence for claims")
```

Class-based signatures support `.append(...)` to add fields programmatically and `.with_updated_fields('label', type_=Literal[...])` to change a field's type on a copy.

## Supported field types

- Basic types: `str`, `int`, `bool`, `float`
- `typing` generics: `list[str]`, `dict[str, int]`, `Optional[float]`, `Union[str, int]`
- `typing.Literal['a', 'b']` — constrained output values
- Custom types: any Pydantic `BaseModel` (e.g., `result: QueryResult`)
- Dot notation for nested types (`MyContainer.Query`)
- Special DSPy types: `dspy.Image`, `dspy.Audio`, `dspy.File`, `dspy.History`, `dspy.Tool`, `dspy.ToolCalls`, `dspy.Code`, `dspy.Reasoning`

Non-primitive output fields get their JSON schema embedded in the prompt by the adapter.

## Multimodal inputs

```python
class DogPictureSignature(dspy.Signature):
    """Output the dog breed of the dog in the image."""
    image_1: dspy.Image = dspy.InputField(desc="An image of a dog")
    answer: str = dspy.OutputField()

classify = dspy.Predict(DogPictureSignature)
classify(image_1=dspy.Image("https://picsum.photos/id/237/200/300"))
```

## Type checking

DSPy validates values passed to input fields against the declared types and **logs a warning** (not an error) on mismatch — `predictor(number="42")` against `number: int` warns. Disable globally with:

```python
dspy.configure(warn_on_type_mismatch=False)
```

## Anti-patterns

- Don't hand-tune signature keywords ("Please be careful and...") — the optimizer does this better and transfers across LMs.
- Don't mark labels as inputs by accident — `with_inputs(...)` controls what feeds the module.
