# ReAct Agents and Tools — Deep Reference

## Tool authoring

A DSPy tool is a standard Python function with:
- Type-hinted parameters
- A docstring (becomes the tool description in the prompt)
- A meaningful name (the LM reads it)

```python
def search_database(query: str, limit: int = 10) -> list[dict]:
    """Search the database for records matching the query.

    Args:
        query: The search term or phrase.
        limit: Maximum number of results to return.
    """
    # implementation
    ...
```

DSPy reads the function name, parameter names/types, and docstring to assemble the tool schema presented to the LM. The active adapter renders this as native function-calling metadata or formatted prompt text.

Rules:
- Parameter names matter — `query` is better than `q`
- Docstrings should explain what the tool does, not just repeat the name
- Return types should be JSON-serializable (str, int, float, list, dict)
- Tools can be synchronous or async (use `await agent.acall(...)` for async)

## ReAct execution model

```python
agent = dspy.ReAct(
    MySignature,                    # string or class-based signature
    tools=[tool1, tool2],           # list of callable functions
    max_iters=10,                   # cap on model turns (default: 10)
)
result = agent(input_field=value)
```

Loop:
1. Model receives signature + available tools
2. Each turn: model reasons and may request one or more tool calls
3. DSPy executes requested tools sequentially, appends results to history
4. Model calls internal `submit` tool with typed output fields to end the loop
5. If `max_iters` exhausted before submit → one final submission attempt → raises if it fails

Returned `Prediction` contains:
- All signature output fields (e.g., `result.answer`)
- `history`: a `dspy.History` object with structured events
- `termination_reason`: how the loop ended

## Inspecting history

```python
result = agent(question="What is X?")

# Print all events
for event in result.history.messages:
    print(event)

# Access specific parts
print(result.termination_reason)  # "submit" or error info
```

History contains structured events with thoughts, tool calls (name + args), and tool results. This is the first thing to read when an agent does something surprising.

## MCP integration

DSPy supports MCP (Model Context Protocol) tools for connecting to external tool servers. See the `dspy.tools` module and the MCP tutorial for setup details.

## Async usage

```python
import asyncio

async def main():
    agent = dspy.ReAct(MySignature, tools=[my_async_tool])
    result = await agent.acall(input_field=value)

asyncio.run(main())
```

`acall` is the async equivalent of calling the module directly. Works with both sync and async tools.

## Common patterns

### Multi-tool research agent
```python
class ResearchAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.agent = dspy.ReAct(
            "question -> answer, sources:list[str]",
            tools=[web_search, fetch_page, calculator],
            max_iters=15,
        )

    def forward(self, question: str):
        return self.agent(question=question)
```

### Agent with constrained output
```python
from typing import Literal

class Classifier(dspy.Signature):
    """Classify the input into a category."""
    text: str = dspy.InputField()
    category: Literal["positive", "negative", "neutral"] = dspy.OutputField()
    confidence: float = dspy.OutputField(desc="0.0 to 1.0")

agent = dspy.ReAct(Classifier, tools=[sentiment_tool], max_iters=5)
```

## Migration notes (3.x → 3.5)

- Structured-history execution is now canonical `dspy.ReAct`
- Old trajectory, extractor, and truncation APIs are **removed**
- `dspy.ReActV2` is a deprecated compatibility subclass (warns on construction, removed in 3.6)
- Old optimized state must be **recompiled** for the new predictor schema
- ReAct does NOT add an extractor-generated `reasoning` field; declare it explicitly in your signature if you want one
