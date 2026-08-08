# Core Abstractions

PocketFlow's entire framework fits in 100 lines. It provides these core building blocks:

## Node

The smallest unit. Each Node has three phases: `prep(shared) → exec(prep_res) → post(shared, prep_res, exec_res)`.

### Three-Phase Lifecycle

1. **`prep(shared)`** — Read and preprocess data from the shared store. Return `prep_res`.
   - Examples: query DB, read files, serialize data into a string
   - This is the **only** place to read from `shared`

2. **`exec(prep_res)`** — Execute compute logic. Return `exec_res`.
   - Examples: LLM calls, remote APIs, tool use
   - Must **not** access `shared` — compute only
   - Must be **idempotent** when retries are enabled
   - Defer exception handling to Node's built-in retry mechanism

3. **`post(shared, prep_res, exec_res)`** — Postprocess and write back to shared. Return an **action string**.
   - Examples: update DB, change states, log results
   - Return value determines next node (`"default"` if `None`)
   - This is the **only** place to write to `shared`

### Fault Tolerance

```python
my_node = MyNode(max_retries=3, wait=10)  # retry 3 times, 10s between retries
```

- `max_retries` (int): Max attempts. Default `1` (no retry).
- `wait` (int/float): Seconds between retries. Default `0`.
- `self.cur_retry`: Current retry count (0-based), accessible in `exec()`.

### Graceful Fallback

Override `exec_fallback(prep_res, exc)` to handle failures after all retries:

```python
class MyNode(Node):
    def exec_fallback(self, prep_res, exc):
        return "fallback result"  # becomes exec_res passed to post()
```

Default behavior: re-raise the exception.

### Operators

- `node_a >> node_b` — default transition (equivalent to `node_a - "default" >> node_b`)
- `node_a - "action_name" >> node_b` — named action transition

## Flow

Orchestrates a graph of Nodes. Executes from `start_node`, follows action transitions until no next node exists.

```python
node_a >> node_b
flow = Flow(start=node_a)
result = flow.run(shared)  # executes full pipeline
```

### Action-Based Transitions

Each Node's `post()` returns an action string. Flows follow these:

```python
review - "approved" >> payment
review - "needs_revision" >> revise
review - "rejected" >> finish
revise >> review  # loop back
payment >> finish
flow = Flow(start=review)
```

### Nested Flows (Flow IS Node)

Flows can be used as nodes within other Flows:

```python
# Subflow
node_a >> node_b
subflow = Flow(start=node_a)

# Parent flow uses subflow as a node
subflow >> node_c
parent_flow = Flow(start=subflow)
```

- Flow runs `prep()` and `post()` but **not** `exec()`
- `post()` receives `None` for `exec_res` — read results from shared store
- Params merge across all parent levels

### Flow `prep()` and `post()`

```python
class MyFlow(Flow):
    def prep(self, shared):
        # Setup before child nodes run
        shared["counter"] = 0

    def post(self, shared, prep_res, exec_res):
        # exec_res is None; read results from shared
        return shared.get("final_action")
```

## Shared Store

The primary communication mechanism between nodes. Typically an in-memory dictionary:

```python
shared = {
    "user": {"id": "user123", "context": {...}},
    "results": {},
    "history": [],
}
```

Can also contain file handlers, DB connections, or any state. Design the data structure upfront.

### Separation of Concerns

Use Shared Store for almost all communication. `params` is syntax sugar for Batch mode only.

## Params

Per-node/per-flow ephemeral config. Set by parent Flow, immutable during a node's run cycle.

```python
class SummarizeFile(Node):
    def prep(self, shared):
        filename = self.params["filename"]  # from parent
        return shared["data"].get(filename, "")
```

- **Only set params on the topmost Flow** — child params are overwritten
- Good for identifiers (filenames, IDs) in Batch mode
- Think of Shared Store as **heap** (shared by all), Params as **stack** (assigned by caller)

## BatchNode

Processes an iterable of items. `prep()` returns an iterable, `exec()` runs once per item, `post()` receives list of results.

```python
class MapSummaries(BatchNode):
    def prep(self, shared):
        content = shared["data"]
        chunks = [content[i:i+10000] for i in range(0, len(content), 10000)]
        return chunks  # iterable

    def exec(self, chunk):  # called once per chunk
        return call_llm(f"Summarize: {chunk}")

    def post(self, shared, prep_res, exec_res_list):  # list of all results
        shared["summary"] = "\n".join(exec_res_list)
```

### BatchNode vs BatchFlow

| | BatchNode | BatchFlow |
|---|---|---|
| `prep()` returns | Data items to process | Param dicts `[{"key": val}, ...]` |
| `exec()` receives | Each data item | N/A (orchestrates child Flow) |
| Child nodes | Regular Nodes (called per item) | Regular Nodes (access `self.params`) |
| Use case | Chunk processing, per-item transforms | Rerunning a Flow with different params |

## BatchFlow

Runs a Flow multiple times with different params:

```python
class SummarizeAllFiles(BatchFlow):
    def prep(self, shared):
        return [{"filename": fn} for fn in shared["files"]]

# Child node accesses filename via self.params
class LoadFile(Node):
    def prep(self, shared):
        filename = self.params["filename"]
        return open(filename).read()

load = LoadFile()
summarize = SummarizeNode()
load >> summarize
per_file_flow = Flow(start=load)

batch = SummarizeAllFiles(start=per_file_flow)
batch.run(shared)
```

### Nested Batches

Params merge across all parent levels:

```python
class FileBatch(BatchFlow):
    def prep(self, shared):
        directory = self.params["directory"]  # from outer batch
        return [{"filename": f} for f in os.listdir(directory)]

class DirBatch(BatchFlow):
    def prep(self, shared):
        return [{"directory": d} for d in directories]

# Inner node sees: {"directory": "/pathA", "filename": "file1.txt"}
```

## AsyncNode

Async version of Node with `prep_async()`, `exec_async()`, `exec_fallback_async()`, `post_async()`.

```python
class AsyncSummarize(AsyncNode):
    async def prep_async(self, shared):
        return await read_file_async(shared["path"])

    async def exec_async(self, prep_res):
        return await call_llm_async(f"Summarize: {prep_res}")

    async def post_async(self, shared, prep_res, exec_res):
        shared["summary"] = exec_res
```

- Must be wrapped in `AsyncFlow`
- `AsyncFlow` can include sync Nodes (they run synchronously within the async flow)
- Call via `await flow.run_async(shared)`

## AsyncBatchNode

Like BatchNode but async. Processes items sequentially:

```python
class AsyncBatchSummaries(AsyncBatchNode):
    async def prep_async(self, shared):
        return shared["texts"]

    async def exec_async(self, text):
        return await call_llm_async(f"Summarize: {text}")

    async def post_async(self, shared, prep_res, exec_res_list):
        shared["summaries"] = exec_res_list
```

## AsyncParallelBatchNode

Like AsyncBatchNode but runs `exec_async()` concurrently via `asyncio.gather`:

```python
class ParallelSummaries(AsyncParallelBatchNode):
    async def prep_async(self, shared):
        return shared["texts"]

    async def exec_async(self, text):
        return await call_llm_async(f"Summarize: {text}")

    async def post_async(self, shared, prep_res, exec_res_list):
        shared["summaries"] = exec_res_list
```

## AsyncFlow

Async version of Flow. Can mix sync and async nodes:

```python
async_node = AsyncSummarize()
sync_node = RegularNode()

async_node >> sync_node

flow = AsyncFlow(start=async_node)
await flow.run_async(shared)
```

## AsyncBatchFlow

Async version of BatchFlow. Runs sub-flows sequentially with different params:

```python
class AsyncSummarizeFiles(AsyncBatchFlow):
    async def prep_async(self, shared):
        return [{"filename": f} for f in shared["files"]]

sub_flow = AsyncFlow(start=LoadAndSummarize())
batch = AsyncSummarizeFiles(start=sub_flow)
await batch.run_async(shared)
```

## AsyncParallelBatchFlow

Runs sub-flows concurrently:

```python
class ParallelSummarizeFiles(AsyncParallelBatchFlow):
    async def prep_async(self, shared):
        return [{"filename": f} for f in shared["files"]]

sub_flow = AsyncFlow(start=LoadAndSummarize())
parallel = ParallelSummarizeFiles(start=sub_flow)
await parallel.run_async(shared)
```

> **Warning**: Parallel calls can trigger rate limits on LLM services. Use throttling or single-node batch APIs when available.
