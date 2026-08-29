# Modules

A module is a building block with **learnable parameters** (instructions, few-shot demos, optionally LM weights) that is invoked with inputs and returns a `dspy.Prediction`. Built-in modules abstract prompting techniques generalized over any signature; all are built on `dspy.Predict`.

## Built-in modules

| Module | Behavior |
|---|---|
| `dspy.Predict` | Basic predictor; does not modify the signature. Stores instructions + demos. |
| `dspy.ChainOfThought` | Injects a `reasoning` step before the signature outputs. |
| `dspy.ProgramOfThought` | LM outputs code whose execution result dictates the response. |
| `dspy.ReAct` | Agent loop: interleaves `next_thought` / `next_tool_name` / `next_tool_args` with a trajectory; auto-adds a `finish` tool. `max_iters` default 20. |
| `dspy.ReActV2` | Newer agent loop with a reserved `submit(**outputs)` tool for the final answer; `submit` name is reserved in `tools`. |
| `dspy.MultiChainComparison` | Runs `ChainOfThought` several times and compares outputs into a final prediction. |
| `dspy.RLM` | Recursive Language Model — explores large contexts via a sandboxed Python REPL with recursive sub-LLM calls; use when context is too large to fit in the prompt. |
| `dspy.Refine` | Runs a wrapped module up to `N` times (varying `rollout_id` at `temperature=1.0`), returns the first prediction above `threshold` or the best by `reward_fn`. Replaces the deprecated `dspy.Assert`/`dspy.Suggest` flow. |
| `dspy.Flex` | (experimental, 3.3.0) Module whose implementation is optimizable **code**, not just a prompt. Starts as a baseline delegating to `dspy.Predict` (or `dspy.RLM` when tools are given); `dspy.GEPA` recognizes `Flex` instances and rewrites their source into decomposed predictors + plain Python. Optimizer-authored code runs in a sandboxed interpreter (`dspy.PythonInterpreter`, Deno-based) — never in the host process. |

Function-style: `dspy.majority` (vote across predictions), `dspy.Parallel`, `dspy.BestOfN`, `dspy.KNN`.

## Usage

```python
# Declare with a signature; pass generation config at init
cot = dspy.ChainOfThought("question -> answer", temperature=0.7)

# Call with input kwargs; read output fields from the Prediction
resp = cot(question="What's something great about ColBERT?")
print(resp.reasoning, resp.answer)

# Per-call config override
cot(question="...", config={"rollout_id": 5, "temperature": 1.0})
```

`dspy.Predict` does not add `reasoning`; `ChainOfThought` and similar do.

## Composing programs

Subclass `dspy.Module`, store submodules as attributes in `__init__`, and orchestrate in `forward` (or `__call__`):

```python
class Hop(dspy.Module):
    def __init__(self, num_docs=10, num_hops=4):
        super().__init__()
        self.generate_query = dspy.ChainOfThought('claim, notes -> query')
        self.append_notes = dspy.ChainOfThought('claim, notes, context -> new_notes: list[str], titles: list[str]')

    def forward(self, claim: str):
        notes, titles = [], []
        for _ in range(self.num_hops):
            query = self.generate_query(claim=claim, notes=notes).query
            context = search(query, k=self.num_docs)
            prediction = self.append_notes(claim=claim, notes=notes, context=context)
            notes.extend(prediction.new_notes)
            titles.extend(prediction.titles)
        return dspy.Prediction(notes=notes, titles=list(set(titles)))

hop = Hop()
hop(claim="Stephen Curry is the best 3 pointer shooter ever")
```

Rules of thumb:

- Start with a single `dspy.ChainOfThought` module; decompose only when you observe specific failure modes.
- Keep each submodule independently inspectable, swappable, and optimizable — that is what makes optimization work.
- Submodules assigned in `__init__` are what the optimizer traces at compile time.

## LM usage tracking

```python
dspy.configure(track_usage=True)
resp = program(question="...")
resp.get_lm_usage()   # {model: {prompt_tokens, completion_tokens, total_tokens, ...}}
```

Cached responses don't count toward usage — a second identical call returns `{}`.

## Retrievers

`dspy.Retrieve(k=3)` wraps the retriever registered as `dspy.settings.rm` (set with `dspy.settings.configure(rm=my_search_fn)`; raises if unset), and `dspy.ColBERTv2(url=...)` targets the hosted Wikipedia index:

```python
def search(query: str, k=3):
    results = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')(query, k=k)
    return [x['text'] for x in results]
```
