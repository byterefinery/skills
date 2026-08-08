# Cookbook Patterns

Complete coverage of all PocketFlow cookbook tutorials, organized by complexity.

## Dummy (☆☆☆)

### 1. Hello World

Minimal single-node flow. Demonstrates `Node` lifecycle and `Flow.run()`.

```python
class HelloNode(Node):
    def exec(self, _):
        return "Hello, PocketFlow!"
    def post(self, shared, prep_res, exec_res):
        shared["greeting"] = exec_res

flow = Flow(start=HelloNode())
flow.run({})
```

### 2. Chat Bot with History

Multi-turn conversation with message history in shared store.

```python
# Flow: GetQuestion → Retrieve → Answer → (loop back to GetQuestion)
question_node - "retrieve" >> retrieve_node
retrieve_node - "answer" >> answer_node
answer_node - "question" >> question_node
```

Key pattern: self-referencing loop for multi-turn conversation. Messages list accumulates in shared store.

### 3. Structured Output

Extract structured data from text by prompting with YAML template and validating with `assert`.

```python
class ExtractNode(Node):
    def exec(self, prep_res):
        prompt = f"""Extract as YAML:
{prep_res}
Output:
```yaml
name: ...
email: ...
skills:
  - ...
```"""
        result = yaml.safe_load(extract_yaml(call_llm(prompt)))
        assert "name" in result and "email" in result
        return result
```

Uses YAML over JSON (LLMs handle multi-line strings better). `assert` validates schema — Node retries on failure.

### 4. Workflow (Article Writing)

Linear pipeline: `GenerateOutline → WriteContent → ApplyStyle`.

```python
outline >> write >> style
flow = Flow(start=outline)
```

Demonstrates task decomposition for complex tasks exceeding a single LLM call.

### 5. Agent (Search + Answer)

Dynamic branching with loop-back. Agent decides whether to search or answer.

```python
decide - "search" >> search
decide - "answer" >> answer
search - "decide" >> decide  # loop back
```

Agent prompt includes context, action space, and YAML output format.

### 6. RAG (Two-Stage)

**Offline**: `ChunkDocs(BatchNode) → EmbedDocs(BatchNode) → StoreIndex`
**Online**: `EmbedQuery → RetrieveDocs → GenerateAnswer`

BatchNode for chunking and embedding. Separate offline/online flows share the index.

### 7. Batch Processing

`BatchNode` for chunk-based processing. `BatchFlow` for rerunning flows with different params.

```python
class TranslateAll(BatchNode):
    def prep(self, shared):
        return shared["texts"]  # iterable
    def exec(self, text):
        return call_llm(f"Translate to Spanish: {text}")
    def post(self, shared, prep_res, exec_res_list):
        shared["translations"] = exec_res_list
```

### 8. Streaming

Real-time LLM token streaming with user interrupt via `threading.Event`.

```python
class StreamNode(Node):
    def prep(self, shared):
        interrupt_event = threading.Event()
        # Thread waits for ENTER key to set interrupt
        listener = threading.Thread(target=wait_for_interrupt)
        listener.start()
        chunks = stream_llm(shared["prompt"])
        return chunks, interrupt_event, listener

    def exec(self, prep_res):
        chunks, interrupt_event, listener = prep_res
        for chunk in chunks:
            if interrupt_event.is_set():
                break
            print(chunk, end="", flush=True)
```

### 9. Chat Guardrail

Pre-processing validation: guardrail node checks if query is on-topic before processing.

```python
user_input - "validate" >> guardrail
guardrail - "retry" >> user_input     # invalid: loop back
guardrail - "process" >> llm_node
llm_node - "continue" >> user_input   # valid: process, then loop
```

Guardrail uses LLM to classify topic. Returns `"retry"` for off-topic queries.

### 10. Majority Vote

Improve reasoning accuracy by aggregating multiple independent solution attempts.

```python
class MajorityVoteNode(BatchNode):
    def prep(self, shared):
        return [shared["question"] for _ in range(shared["num_tries"])]

    def exec(self, question):
        # Each attempt independently answers the question
        return extract_answer(call_llm(prompt))

    def exec_fallback(self, prep_res, exc):
        return None  # skip failed attempts

    def post(self, shared, prep_res, exec_res_list):
        valid = [r for r in exec_res_list if r is not None]
        best, freq = Counter(valid).most_common(1)[0]
        shared["majority_answer"] = best
```

Uses `exec_fallback` to gracefully skip failed LLM calls. `Counter.most_common()` picks the mode.

### 11. Map-Reduce

`BatchNode` (map) → `Node` (reduce). Process items independently, then aggregate.

```python
class SummarizeAll(BatchNode):
    def prep(self, shared):
        return list(shared["files"].items())
    def exec(self, (filename, content)):
        return (filename, call_llm(f"Summarize: {content}"))
    def post(self, shared, prep_res, exec_res_list):
        shared["summaries"] = dict(exec_res_list)

class Combine(Node):
    def exec(self, summaries):
        return call_llm(f"Combine: {summaries}")

batch >> combine
flow = Flow(start=batch)
```

### 12. CLI HITL (Human-in-the-Loop)

Command-line feedback loop for iterative refinement.

```python
get_topic >> generate_joke >> get_feedback
get_feedback - "Disapprove" >> generate_joke  # regenerate
# "Approve" has no successor → flow ends
```

`GetFeedbackNode.exec()` blocks on `input()`, returns `"yes"`/`"no"`. Disapproved jokes accumulate in `shared["disliked_jokes"]` to guide regeneration.

## Beginner (★☆☆)

### 13. Multi-Agent (Taboo Game)

Two async agents communicate via `asyncio.Queue`:

```python
shared = {
    "target_word": "nostalgia",
    "hinter_queue": asyncio.Queue(),
    "guesser_queue": asyncio.Queue()
}

hinter - "continue" >> hinter
guesser - "continue" >> guesser

await asyncio.gather(
    hinter_flow.run_async(shared),
    guesser_flow.run_async(shared)
)
```

Each agent loops on its own queue, exchanging messages. `asyncio.gather` runs both concurrently.

### 14. Supervisor

Wrap an unreliable agent flow with a supervisor node for quality control.

```python
# Inner agent flow
agent_flow = create_agent_inner_flow()

# Outer supervision
agent_flow >> supervisor
supervisor - "retry" >> agent_flow

outer_flow = Flow(start=agent_flow)
```

Supervisor (LLM-as-judge) checks output quality. Returns `"retry"` to re-run the entire agent flow.

### 15. Parallel Batch

`AsyncParallelBatchNode` for concurrent LLM calls — 3x speedup over sequential.

```python
class ParallelSummaries(AsyncParallelBatchNode):
    async def exec_async(self, text):
        return await call_llm_async(f"Summarize: {text}")
```

Uses `asyncio.gather` internally. Only helps I/O-bound work (Python GIL).

### 16. Parallel Batch Flow

`AsyncParallelBatchFlow` for concurrent sub-flow execution — 8x speedup for image processing.

```python
class ParallelProcess(AsyncParallelBatchFlow):
    async def prep_async(self, shared):
        return [{"image": img} for img in shared["images"]]

sub_flow = AsyncFlow(start=ProcessImage())
parallel = ParallelProcess(start=sub_flow)
await parallel.run_async(shared)
```

### 17. Thinking (Chain-of-Thought)

Self-looping node for iterative reasoning:

```python
cot_node - "continue" >> cot_node
flow = Flow(start=cot_node)
```

Node generates reasoning step, decides whether to continue or produce final answer.

### 18. Memory (Short-term + Long-term)

Chat bot with vector-based long-term memory:

```python
question - "retrieve" >> retrieve    # search long-term memory
retrieve - "answer" >> answer        # generate response
answer - "embed" >> embed            # store old conversations
answer - "question" >> question      # next turn
embed - "question" >> question       # next turn after embedding
```

Short-term: conversation history in shared store. Long-term: embeddings stored in vector DB, retrieved by similarity.

### 19. Text2SQL

Generate SQL with auto-debug loop:

```python
get_schema >> generate_sql >> execute_sql
execute_sql - "error_retry" >> debug_sql
debug_sql >> execute_sql  # retry with fixed SQL
```

`DebugSQL` node analyzes the error, generates corrected SQL, and loops back to execution.

### 20. Code Generator

Test-driven code generation with iterative revision:

```python
generate_tests >> implement >> run_tests
run_tests - "failure" >> revise
revise >> run_tests  # retest after revision
# "success" or "max_iterations" → flow ends
```

- `GenerateTestCases`: LLM generates 5-7 test cases in YAML
- `ImplementFunction`: LLM writes `run_code()` function
- `RunTests` (BatchNode): executes each test case via `exec()`
- `Revise`: LLM analyzes failures, revises function code and/or test cases

### 21. MCP (Model Context Protocol)

Agent using MCP for tool discovery and execution:

```python
get_tools - "decide" >> decide_tool
decide_tool - "execute" >> execute_tool
```

- `GetToolsNode`: retrieves available tools from MCP server
- `DecideToolNode`: LLM picks tool and extracts parameters from question
- `ExecuteToolNode`: calls the selected MCP tool

### 22. Agent Skills

Route requests to reusable markdown skills and apply them:

```python
select_skill >> apply_skill
```

- `SelectSkill`: routes task to appropriate skill file (deterministic or LLM-based)
- `ApplySkill`: injects skill markdown into prompt, LLM follows instructions

Skills are markdown files in a directory. `load_skills()` reads them all.

### 23. A2A (Agent-to-Agent Protocol)

Agent wrapped with A2A protocol for standardized inter-agent communication. Uses task management, push notifications, and structured message passing.

### 24. Streamlit FSM

Streamlit app with finite state machine for human-in-the-loop image generation. State transitions controlled by UI buttons.

```python
class GenerateImageNode(Node):
    def post(self, shared, prep_res, exec_res):
        shared["stage"] = "user_feedback"  # FSM state
```

### 25. FastAPI WebSocket

Real-time chat with streaming LLM responses via WebSocket:

```python
class StreamingChatNode(AsyncNode):
    async def exec_async(self, prep_res):
        messages, websocket = prep_res
        await websocket.send_text(json.dumps({"type": "start"}))
        async for chunk in stream_llm(messages):
            await websocket.send_text(json.dumps({"type": "chunk", "content": chunk}))
        await websocket.send_text(json.dumps({"type": "end"}))
```

### 26. FastAPI Background

Background jobs with real-time progress via Server-Sent Events (SSE):

```python
class WriteContent(BatchNode):
    def exec(self, section):
        content = call_llm(prompt)
        # Send progress via SSE queue
        shared["sse_queue"].put_nowait({
            "step": "content",
            "progress": section_progress,
            "data": {"section": section}
        })
```

### 27. FastAPI HITL

Server-based human-in-the-loop with async review events:

```python
process >> review
review - "approved" >> result
review - "rejected" >> process  # loop back
```

`ReviewNode` is `AsyncNode` that waits on `asyncio.Event`. Frontend triggers event via API when user approves/rejects.

### 28. Gradio HITL

GUI human-in-the-loop with queue-based communication:

```python
decide - "check-weather" >> check_weather >> decide
decide - "book-hotel" >> book_hotel >> decide
decide - "follow-up" >> follow_up     # blocks for user input
decide - "result-notification" >> result_notification
```

Uses `queue.Queue` for Gradio UI ↔ PocketFlow communication. `FollowUp` node pushes question to queue, blocks waiting for user response.

### 29. Voice Chat

Interactive voice pipeline: `CaptureAudio → SpeechToText → QueryLLM → TextToSpeech → (loop back)`.

```python
capture >> stt >> llm >> tts
tts - "next_turn" >> capture
# "end_conversation" → flow ends naturally
```

### 30. Judge (Evaluator-Optimizer)

LLM-as-judge loop for iterative refinement:

```python
generator >> judge
judge - "fail" >> generator  # regenerate if quality insufficient
```

Generator produces content, Judge scores it. Loop until quality threshold met or max retries.

### 31. Debate (Adversarial Reasoning)

Two advocates argue opposing positions, judge decides:

```python
advocate_for >> advocate_against >> judge
```

Each advocate builds arguments. Judge evaluates both sides and produces verdict.

### 32. Agentic RAG

Agent decides which documents to read (not just top-k retrieval):

```python
decide - "read" >> read_doc
decide - "answer" >> answer
read_doc - "decide" >> decide
```

Agent sees document summaries, decides which to read in full, loops until enough context.

### 33. Self-Healing Mermaid

Generate Mermaid diagrams with automatic error recovery:

```python
write_chart >> compile_chart
compile_chart - "fix" >> write_chart  # regenerate on syntax error
```

`CompileChart` attempts to render the diagram. On error, returns `"fix"` to regenerate with error context.

### 34. Heartbeat

Periodic monitoring with nested flows:

```python
# Inner flow: check → process emails
check - "new_email" >> process
email_flow = Flow(start=check)

# Outer loop: wait → email_flow → wait
wait >> email_flow >> wait
# "done" from WaitNode (max_cycles reached) → flow ends
```

`WaitNode` sleeps between polling cycles. After `max_cycles`, returns `"done"` with no successor.

## Intermediate (★★☆)

### 35. Lead Generation

Sales pipeline: `ScrapeLeads → EnrichLeads → ScoreLeads → PersonalizeEmails`.

BatchNodes for per-lead processing. LLM scoring ranks leads 1-10. Personalization generates cold emails for hot leads.

### 36. Newsletter

AI curation: `CurateSources → FilterStories → SummarizeStories → FormatNewsletter`.

Web search for multiple topics → LLM filtering picks top stories → summarization → markdown formatting.

### 37. Invoice Processing

Extract and validate invoice data from PDFs using vision:

```python
extract >> validate
```

Vision LLM extracts fields (date, amount, vendor). Validation node checks consistency (totals match line items, dates valid).

### 38. NotebookLM

Document-to-podcast: `AnalyzeDocs → WriteScript → TextToSpeech`.

Extract key insights from documents → generate conversational two-host script → convert to audio via TTS.

### 39. Deep Research

Recursive map-reduce with iterative refinement:

```python
planner >> researcher >> synthesizer
synthesizer - "research" >> planner  # loop for gap-filling
```

1. `PlannerNode`: generates 3 diverse search queries
2. `ResearcherNode` (BatchNode): searches web for each query, extracts facts
3. `SynthesizerNode`: checks completeness — loops back if gaps remain (max 2 loops)

## Advanced (★★★)

### 40. Coding Agent

Production coding agent with 6 tools, memory, and patch-as-subflow:

```python
# Patch subflow (Flow IS Node)
patch_read >> patch_validate >> patch_apply
patch_flow = PatchFile(start=patch_read)

# Main agent loop
compact = CompactHistory()
decide = DecideAction(max_retries=3)

decide - "retry" >> compact
decide - "list_files" >> ListFiles() >> compact
decide - "grep_search" >> GrepSearch() >> compact
decide - "read_file" >> ReadFile() >> compact
decide - "patch_file" >> patch_flow >> compact
decide - "run_command" >> RunCommand() >> compact
compact >> decide
```

Key patterns:
- **CompactHistory**: compress conversation history to stay within context window
- **Patch as subflow**: `PatchRead → PatchValidate → PatchApply` with error handling
- **Persistent memory**: save session learnings to `.memory.md`
- **Skills loading**: read `AGENTS.md` for project-specific rules
- **Step limit**: max 50 steps to prevent infinite loops

### 41. Browser Agent

Browser automation via Playwright with two modes:

```python
observe - "decide" >> decide
decide - "act" >> act
decide - "done" >> finish
act - "observe" >> observe
```

**DOM mode**: reads page elements as numbered list, clicks by element number. Precise but blind to canvas/native content.

**Vision mode**: takes screenshot, LLM decides click coordinates. Works on anything visible but less precise.

### 42. Tool Patterns

Reusable tool implementations from the cookbook:

| Tool | Description | Pattern |
|---|---|---|
| **Web Crawler** | Crawl websites, extract structured content | `Node` with `requests`/`BeautifulSoup` |
| **Database** | Query databases via SQL | `Node` with `sqlite3`/`duckdb` |
| **Embeddings** | Generate text embeddings | `Node` with OpenAI/other embedding API |
| **PDF Vision** | Extract text from PDFs via vision | `BatchNode` + nested `Flow` per PDF |

PDF Vision pattern:

```python
class ProcessPDFBatchNode(BatchNode):
    def exec(self, item):
        flow = create_single_pdf_flow()  # LoadPDF → ExtractText → Combine
        shared = item.copy()
        flow.run(shared)
        return {"filename": item["pdf_path"], "text": shared["final_text"]}

# Inner flow: load PDF → convert to images → vision extraction → combine
load_pdf >> extract_text >> combine_results
```

## Pattern Cheat Sheet

| Pattern | Core Classes | Key Technique | Cookbook |
|---|---|---|---|
| Simple Pipeline | `Node`, `Flow` | `>>` chaining | Workflow, NotebookLM |
| Conditional Branch | `Node`, `Flow` | `- "action" >>` | Agent, Chat Guardrail |
| Agent Loop | `Node`, `Flow` | Self-referencing via action | Agent, Agentic RAG |
| Batch Processing | `BatchNode` | `prep()` returns iterable | Map-Reduce, Batch |
| Param Rerun | `BatchFlow` | `prep()` returns param dicts | Nested Batch |
| Async I/O | `AsyncNode`, `AsyncFlow` | `async/await` lifecycle | WebSocket, Voice Chat |
| Parallel I/O | `AsyncParallelBatchNode` | `asyncio.gather` | Parallel Batch |
| Parallel Flows | `AsyncParallelBatchFlow` | Concurrent sub-flows | Parallel Flow |
| Nested Flow | `Flow` as `Node` | Subflow composition | Supervisor, Coding Agent, PDF Vision |
| Supervisor | `Flow` + `Node` | Retry entire subflow | Supervisor |
| Multi-Agent | `AsyncNode`, `asyncio.Queue` | Concurrent flows | Multi-Agent, A2A |
| Self-Healing | `Node` loop | Error detection → retry | Self-Healing Mermaid, Text2SQL, Code Generator |
| Memory | `Node` + vector store | Embed + retrieve in flow | Chat Memory |
| Chain-of-Thought | Self-loop `Node` | Continue/refine action | Thinking |
| LLM-as-Judge | `Node` loop | Quality gate with retry | Judge, Debate |
| Map-Reduce | `BatchNode` → `Node` | Split then aggregate | Map-Reduce, Deep Research |
| HITL (CLI) | `Node` + `input()` | Block on user input | CLI HITL |
| HITL (GUI) | `Node` + `queue.Queue` | Queue-based UI communication | Gradio HITL, Streamlit FSM |
| HITL (Server) | `AsyncNode` + `asyncio.Event` | Async wait for review | FastAPI HITL |
| Streaming | `Node` + generator | Token-by-token output | Streaming, FastAPI WebSocket |
| Guardrail | Pre-node validation | Topic check before processing | Chat Guardrail |
| Majority Vote | `BatchNode` + `Counter` | Independent attempts + mode | Majority Vote |
| Browser Agent | `Node` + Playwright | Observe-Decide-Act loop | Browser Agent |
| MCP | `Node` + MCP server | Tool discovery + execution | MCP |
| Agent Skills | `Node` + markdown | Skill routing + application | Agent Skills |
| Heartbeat | Nested `Flow` + sleep | Periodic polling | Heartbeat |
| Background Jobs | `Node` + SSE queue | Progress streaming | FastAPI Background |
