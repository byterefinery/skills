# Design Patterns

PocketFlow design patterns are implemented purely through Node/Flow composition. No special pattern classes needed.

## Agent

An agent dynamically decides actions based on context. Implement with branching loops:

### Structure

1. **Context + Action nodes** — supply context and perform actions
2. **Agent node** — LLM decides next action from structured action space
3. **Branching** — connect each action node back to agent, with potential loops

### Action Design Principles

- **Incremental**: Feed content in manageable chunks (500 lines or 1 page), not all at once
- **Overview-zoom-in**: Provide high-level structure first (TOC, summary), then drill into details
- **Parameterized/Programmable**: Enable parameterized actions (columns to select) or programmable actions (SQL queries)
- **Backtracking**: Let agent undo last step instead of restarting entirely

### Agent Prompt Template

```python
prompt = f"""
### CONTEXT
Task: {task_description}
Previous Actions: {previous_actions}
Current State: {current_state}

### ACTION SPACE
[1] search
  Description: Use web search to get results
  Parameters:
    - query (str): What to search for

[2] answer
  Description: Conclude based on the results
  Parameters:
    - result (str): Final answer

### NEXT ACTION
Decide the next action. Output YAML:
```yaml
thinking: |
    <step-by-step reasoning>
action: <action_name>
parameters:
    <parameter_name>: <parameter_value>
```"""
```

### Context Management

- Provide **relevant, minimal context** — LLMs suffer from "lost in the middle" even with large context windows
- Use RAG to retrieve relevant context instead of including entire history
- Avoid overlapping actions (e.g., separate `read_databases` and `read_csvs` — instead import CSVs into the database)

### Example: Search Agent

```python
decide = DecideAction()
search = SearchWeb()
answer = DirectAnswer()

decide - "search" >> search
decide - "answer" >> answer
search - "decide" >> decide  # loop back

flow = Flow(start=decide)
flow.run({"query": "Who won the Nobel Prize in Physics 2024?"})
```

## Workflow

Task decomposition: chain multiple nodes for complex tasks that exceed a single LLM call.

### Granularity Balance

- Tasks **too coarse**: too complex for one LLM call
- Tasks **too granular**: LLM lacks context, results inconsistent across nodes
- Find the sweet spot through iteration; use Agents for tasks with many edge cases

### Example: Article Writing

```python
outline = GenerateOutline()
write = WriteSection()
review = ReviewAndRefine()

outline >> write >> review

writing_flow = Flow(start=outline)
writing_flow.run({"topic": "AI Safety"})
```

## RAG (Retrieval-Augmented Generation)

Two-stage pipeline: offline indexing + online query.

### Stage 1: Offline Indexing

```python
chunk_node = ChunkDocs()      # BatchNode: chunk raw text
embed_node = EmbedDocs()      # BatchNode: embed each chunk
store_node = StoreIndex()     # Node: store in vector DB

chunk_node >> embed_node >> store_node
offline_flow = Flow(start=chunk_node)
```

### Stage 2: Online Query & Answer

```python
embed_q = EmbedQuery()        # embed user question
retrieve = RetrieveDocs()     # search index for top chunks
generate = GenerateAnswer()   # LLM with question + context

embed_q >> retrieve >> generate
online_flow = Flow(start=embed_q)
```

### Agentic RAG

Agent-driven RAG where the agent decides which documents to read:

```python
decide = DecideAction()  # read summary or answer
read = ReadDoc()          # read full document
answer = Answer()

decide - "read" >> read
decide - "answer" >> answer
read - "decide" >> decide

flow = Flow(start=decide)
```

## Map-Reduce

Split tasks into independent map phase, then aggregate in reduce phase.

### When to Use

- Large input data (multiple files to process)
- Large output data (multiple forms to fill)
- Logical way to break task into independent parts

### Example: Document Summarization

```python
class SummarizeAllFiles(BatchNode):
    def prep(self, shared):
        return list(shared["files"].items())

    def exec(self, one_file):
        filename, content = one_file
        return (filename, call_llm(f"Summarize:\n{content}"))

    def post(self, shared, prep_res, exec_res_list):
        shared["file_summaries"] = dict(exec_res_list)

class CombineSummaries(Node):
    def prep(self, shared):
        return shared["file_summaries"]

    def exec(self, file_summaries):
        text = "\n---\n".join(f"{fn}:\n{s}" for fn, s in file_summaries.items())
        return call_llm(f"Combine into one summary:\n{text}")

    def post(self, shared, prep_res, final_summary):
        shared["all_files_summary"] = final_summary

batch = SummarizeAllFiles()
combine = CombineSummaries()
batch >> combine
flow = Flow(start=batch)
```

> **Performance**: Speed up map phase with `AsyncParallelBatchNode` for concurrent LLM calls.

## Structured Output

Get LLMs to output specific structures (lists, dicts, predefined keys).

### Approaches

1. **Prompting** — wrap expected structure in code fences (YAML preferred)
2. **Schema enforcement** — use LLMs with native JSON schema support
3. **Post-processing** — extract structured content from response

### YAML Over JSON

YAML is preferred because LLMs struggle with escaping. Multi-line strings use block literals without quotes or escape characters.

```yaml
# YAML — easy for LLMs
dialogue: |
  Alice said: "Hello Bob.
  How are you?
  I am good."

# JSON — escaping hell
{"dialogue": "Alice said: \"Hello Bob.\\nHow are you?\\nI am good.\""}
```

### Validation

Use `assert` to validate required fields — let Node's retry mechanism handle schema violations:

```python
class SummarizeNode(Node):
    def exec(self, prep_res):
        prompt = f"""Summarize as YAML with exactly 3 bullets:
{prep_res}
Output:
```yaml
summary:
  - bullet 1
  - bullet 2
  - bullet 3
```"""
        response = call_llm(prompt)
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        result = yaml.safe_load(yaml_str)

        assert "summary" in result
        assert isinstance(result["summary"], list)
        return result
```

Alternative: use Pydantic for schema validation.

## Multi-Agent

Multiple agents coordinate via message queues in shared storage.

### When to Use

- Most of the time, you don't need multi-agents — start simple
- Use when tasks genuinely require independent agents with separate decision loops

### Message Queue Pattern

```python
class AgentNode(AsyncNode):
    async def prep_async(self, _):
        message_queue = self.params["messages"]
        message = await message_queue.get()
        return message

agent = AgentNode()
agent >> agent  # self-loop
flow = AsyncFlow(start=agent)
flow.set_params({"messages": asyncio.Queue()})
```

### Interactive Multi-Agent (Taboo Game Example)

Two agents communicate via separate `asyncio.Queue` instances:

```python
shared = {
    "target_word": "nostalgia",
    "forbidden_words": ["memory", "past", "remember"],
    "hinter_queue": asyncio.Queue(),
    "guesser_queue": asyncio.Queue()
}

hinter = AsyncHinter()
guesser = AsyncGuesser()

hinter - "continue" >> hinter
guesser - "continue" >> guesser

hinter_flow = AsyncFlow(start=hinter)
guesser_flow = AsyncFlow(start=guesser)

await asyncio.gather(
    hinter_flow.run_async(shared),
    guesser_flow.run_async(shared)
)
```

### Supervisor Pattern

Wrap an agent flow inside a supervision loop:

```python
agent_flow = create_agent_inner_flow()
supervisor = SupervisorNode()

agent_flow >> supervisor
supervisor - "retry" >> agent_flow

outer_flow = Flow(start=agent_flow)
```

The supervisor checks agent output quality and retries the entire agent flow if the result is invalid.
