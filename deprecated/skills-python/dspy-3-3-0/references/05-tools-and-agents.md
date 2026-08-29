# Tools and Agents

Tools let modules act on the world — search, fetch, compute. Two approaches: the fully managed `dspy.ReAct` agent, or manual tool handling with `dspy.Tool` / `dspy.ToolCalls`.

## Tools as plain functions

`dspy.Tool(fn)` (or passing functions directly to `ReAct`) derives the tool name, parameter schema, and description from the function's name, type hints, and docstring:

```python
def get_weather(city: str, units: str = "celsius") -> str:
    """Get weather information for a specific city.

    Args:
        city: The name of the city.
        units: Temperature units, either 'celsius' or 'fahrenheit'.
    """
    ...

tool = dspy.Tool(get_weather)
tool.name    # "get_weather"
tool.desc    # the docstring
tool.args    # parameter schema
```

Design rules — clear docstrings, explicit type hints, simple parameters (str/int/bool/dict/list or Pydantic models). Untyped or undocumented tools degrade agent tool selection.

## ReAct (fully managed)

```python
react = dspy.ReAct(
    signature="question -> answer",
    tools=[get_weather, search_web],
    max_iters=5,          # default is 20 — set explicitly to bound token cost
)
result = react(question="What's the weather in Tokyo?")
print(result.answer, result.trajectory)
```

Behavior: each turn the LM produces `next_thought`, `next_tool_name` (constrained to the tool names + implicit `finish`), and `next_tool_args` (JSON); observations append to the trajectory. Built-in error recovery for failed tool calls.

`dspy.ReActV2` is the newer variant: same interface, but the final answer is emitted through a reserved `submit(**output_fields)` tool (don't name one of your tools `submit`).

## Manual tool handling

For precise control over execution and error handling:

```python
class ToolSignature(dspy.Signature):
    """Signature for manual tool handling."""
    question: str = dspy.InputField()
    tools: list[dspy.Tool] = dspy.InputField()
    outputs: dspy.ToolCalls = dspy.OutputField()

predictor = dspy.Predict(ToolSignature)
response = predictor(
    question="What's the weather in New York?",
    tools=[dspy.Tool(weather), dspy.Tool(calculator)],
)

for call in response.outputs.tool_calls:
    result = call.execute()                                        # auto-discovers functions by name
    # or explicit:
    result = call.execute(functions={"weather": weather})
    # or: call.execute(functions=[dspy.Tool(weather), dspy.Tool(calculator)])
```

## Native function calling

- `ChatAdapter` defaults to `use_native_function_calling=False` (text parsing).
- `JSONAdapter` defaults to `use_native_function_calling=True`.
- Override either by constructing the adapter explicitly. DSPy auto-falls back to text parsing when the model lacks native support.

## Async tools

```python
import asyncio
import dspy

async def async_weather(city: str) -> str:
    """Get weather information asynchronously."""
    ...

tool = dspy.Tool(async_weather)
result = await tool.acall(city="New York")        # preferred for async tools
```

From synchronous code, enable auto-conversion:

```python
with dspy.context(allow_tool_async_sync_conversion=True):
    result = tool(city="New York")                # __call__ on async tools
```

Async programs: modules expose `acall` — `await react.acall(question=...)`. `dspy.asyncify` / `dspy.syncify` convert programs across sync/async boundaries.

## MCP (Model Context Protocol)

Install `pip install "dspy[mcp]"`. DSPy doesn't manage the MCP connection — use the `mcp` library's client, then convert tools with `dspy.Tool.from_mcp_tool(session, tool)`:

```python
import asyncio
import dspy
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["path/to/your/mcp_server.py"],
        env=None,
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.list_tools()
            dspy_tools = [dspy.Tool.from_mcp_tool(session, t) for t in response.tools]

            react = dspy.ReAct("question -> answer", tools=dspy_tools, max_iters=5)
            result = await react.acall(question="What is 25 + 17?")
            print(result.answer)

asyncio.run(main())
```

Remote servers over HTTP use `mcp.client.streamable_http.streamablehttp_client(url)` with the same pattern. Converted tools preserve name, description, parameter schemas, and async execution.

## Choosing

- `dspy.ReAct` — automatic reasoning + tool selection, multiple tool calls, built-in error recovery.
- Manual `ToolCalls` — precise execution control, custom error handling, lower latency, void-returning tools.
