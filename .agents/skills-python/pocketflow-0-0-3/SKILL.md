---
name: pocketflow-0-0-3
description: >
  PocketFlow 0.0.3 — 100-line minimalist LLM framework for building Agents, Workflows, RAG,
  Map-Reduce, Multi-Agent systems, and more. Zero dependencies, zero vendor lock-in. Use when
  designing or implementing LLM application architectures with graph-based node/flow composition,
  agentic coding workflows, batch/async/parallel processing, or any LLM pipeline needing lightweight
  orchestration without framework bloat.
license: MIT
compatibility: Requires Python 3.11+. Install via `pip install pocketflow` or copy the single __init__.py (100 lines). No other dependencies needed.
allowed-tools: Bash(pip) Bash(python) Read Write Edit
metadata:
  tags:
    - llm
    - agents
    - workflow
    - rag
    - orchestration
    - graph
---

# pocketflow 0.0.3

PocketFlow is a 100-line minimalist LLM framework that captures the core abstraction of all LLM frameworks: **Graph**. Nodes handle tasks, Flows connect them via labeled edges (Actions), and a Shared Store enables communication. Everything else—Agents, Workflows, RAG, Map-Reduce, Multi-Agent—is built from these primitives.

## Overview

PocketFlow provides a tiny surface area with maximum expressiveness:

- **Core Abstractions**: `Node` (prep→exec→post), `Flow` (orchestrator), `Shared Store` (communication), `BatchNode`/`BatchFlow` (iterative processing), `AsyncNode`/`AsyncFlow` (async I/O), `AsyncParallelBatchNode`/`AsyncParallelBatchFlow` (concurrent I/O)
- **Design Patterns**: Agent (dynamic branching), Workflow (task decomposition chains), RAG (two-stage retrieval), Map-Reduce (split-then-aggregate), Structured Output (YAML/JSON extraction), Multi-Agent (coordinated agents via message queues)
- **Utility Functions**: LLM wrappers, web search, visualization, chunking, embedding, vector databases, text-to-speech — provided as examples, not built-in (no vendor lock-in)
- **Agentic Coding**: 8-step methodology where humans design and AI agents implement

## Usage

### Installation

```bash
pip install pocketflow
# Or copy the single file (100 lines):
# https://github.com/The-Pocket/PocketFlow/blob/main/pocketflow/__init__.py
```

### Quick Start — Minimal Chat Bot

```python
from pocketflow import Node, Flow

class GetQuestionNode(Node):
    def exec(self, _):
        return input("Enter your question: ")
    def post(self, shared, prep_res, exec_res):
        shared["question"] = exec_res

class AnswerNode(Node):
    def prep(self, shared):
        return shared["question"]
    def exec(self, question):
        return call_llm(question)  # implement your own LLM wrapper
    def post(self, shared, prep_res, exec_res):
        shared["answer"] = exec_res

# Wire nodes and create flow
get_question = GetQuestionNode()
answer = AnswerNode()
get_question >> answer
flow = Flow(start=get_question)

# Run
shared = {"question": None, "answer": None}
flow.run(shared)
print(f"Answer: {shared['answer']}")
```

### Conditional Branching

```python
# node_a - "action_name" >> node_b
decide - "search" >> search_node
decide - "answer" >> answer_node
search_node - "decide" >> decide  # loop back
```

### Batch Processing

```python
from pocketflow import BatchNode

class SummarizeFiles(BatchNode):
    def prep(self, shared):
        return list(shared["files"].items())  # iterable of items
    def exec(self, item):
        filename, content = item
        return (filename, call_llm(f"Summarize: {content}"))
    def post(self, shared, prep_res, exec_res_list):
        shared["summaries"] = dict(exec_res_list)
```

### Async + Parallel

```python
from pocketflow import AsyncParallelBatchNode, AsyncFlow

class ParallelSummaries(AsyncParallelBatchNode):
    async def prep_async(self, shared):
        return shared["texts"]
    async def exec_async(self, text):
        return await call_llm_async(f"Summarize: {text}")
    async def post_async(self, shared, prep_res, exec_res_list):
        shared["summaries"] = exec_res_list

node = ParallelSummaries()
flow = AsyncFlow(start=node)
await flow.run_async(shared)
```

## Gotchas

- **Never use `exec()` to access `shared`** — read in `prep()`, write in `post()`. `exec()` is compute-only, must be idempotent for retries.
- **`node.run()` does not follow successors** — it only runs that single node's prep→exec→post. Always use `flow.run()` for full pipeline execution.
- **`post()` returning `None` means `"default"` action** — if `post()` has no return statement, the framework treats it as returning `"default"`.
- **BatchFlow returns param dicts, not data** — `prep()` in BatchFlow returns `[{"key": val}, ...]` which become `self.params` in child nodes, not data to process directly.
- **BatchNode children are regular Nodes** — the batching happens at the BatchNode level; child nodes access items via `exec(item)`, not as BatchNodes themselves.
- **AsyncNode requires AsyncFlow** — sync `Node` can mix into `AsyncFlow`, but `AsyncNode` must run inside `AsyncFlow` via `run_async()`.
- **Parallel only helps I/O-bound work** — Python's GIL prevents true CPU parallelism. Use parallel nodes for LLM calls, API requests, DB queries, file I/O.
- **Watch rate limits with parallel calls** — concurrent LLM calls can trigger rate limits. Use semaphores or throttling.
- **Set params only on the topmost Flow** — child Flow/node params are overwritten by parent. Use Shared Store for most data, params only for Batch identifiers.
- **Avoid `try/except` in utility functions** — let Node's built-in retry mechanism handle failures. Use `exec_fallback()` for graceful degradation.
- **Flow IS Node** — Flows can be nested as nodes within other Flows. This enables powerful composition (subflows, supervision loops).
- **`exec_fallback` runs after all retries exhausted** — override to return a fallback value instead of re-raising. The fallback becomes `exec_res` passed to `post()`.
- **Python GIL limitation** — `AsyncParallelBatchNode` and `AsyncParallelBatchFlow` overlap I/O but cannot parallelize CPU-bound work.
- **Validate structured output with assert** — let Node's retry mechanism handle schema violations. Use YAML over JSON (LLMs handle multi-line strings better).

## References

- [01-core-abstractions](references/01-core-abstractions.md) — Node, Flow, Shared Store, Params, Batch, Async, Parallel
- [02-design-patterns](references/02-design-patterns.md) — Agent, Workflow, RAG, Map-Reduce, Structured Output, Multi-Agent
- [03-utility-functions](references/03-utility-functions.md) — LLM wrappers, web search, visualization, chunking, embedding, vector DBs, TTS
- [04-agentic-coding](references/04-agentic-coding.md) — 8-step methodology: Requirements → Flow → Utilities → Data → Node → Implementation → Optimization → Reliability
- [05-cookbook-patterns](references/05-cookbook-patterns.md) — Real-world patterns: Coding Agent, Deep Research, Supervisor, Text2SQL, Voice Chat, and more
