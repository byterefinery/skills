---
name: schedula-1-6-15
description: >
  Schedula 1.6.15 — dynamic flow-based programming library for Python. Use when
  building dataflow pipelines where computation order is determined at runtime
  from a DAG of interdependent functions. Triggers on Dispatcher, dataflow
  scheduling, flow-based programming, ArciDispatch, sub-dispatcher, DAG-based
  computation, automatic control flow, parallel dispatch, or when the user needs
  to model systems of interdependent formulas/functions where inputs/outputs are
  known but execution order depends on available data. Covers Dispatcher creation,
  function/data node registration, dispatching with inputs/outputs, sub-model
  extraction, async/parallel executors, web API deployment, and plotting.
license: EUPL-1.1
compatibility: Requires Python 3.7+. Optional extras need Graphviz (plot), Flask (web), networkx (parallel)
metadata:
  tags:
    - python
    - dataflow
    - scheduling
    - dag
    - flow-based-programming
---

# schedula 1.6.15

## Overview

Schedula is a dynamic flow-based programming environment for Python. It represents
computation as a weighted directed graph where nodes are operations (functions) and
edges are data dependencies. At runtime, given any set of inputs, it automatically
computes the shortest-path DAG (using a modified Dijkstra algorithm called ArciDispatch)
to produce the desired outputs.

### Core Concepts

- **Dispatcher** — the dataflow execution model; a weighted directed graph of data nodes, function nodes, and sub-dispatcher nodes
- **Data node** — stores a value in the solution; executable when it receives one input arc
- **Function node** — invokes a user-defined function; executable when all inputs are satisfied and at least one output is needed
- **Sub-dispatcher node** — nests another Dispatcher as a component, enabling modular, reusable dataflow models
- **Solution** — the dispatch result (dict-like) containing computed values and the workflow graph used
- **Workflow** — the actual DAG executed, extracted from the full model based on provided inputs/outputs

### Special Constants

- **`START`** — starting node identifying initial workflow inputs
- ****SINK** — collects all unused outputs
- **`SELF`** — node containing the Dispatcher itself
- **`PLOT`** — auto-plots the dispatcher solution
- **`EMPTY`** — sentinel for unset values
- **`NONE`** — fake value for calling functions without arguments
- **`END`** — ending node of SubDispatchFunction

### Key Features

- Automatic control flow: DAG determined at runtime from available inputs
- Domain guards: `input_domain` predicates skip functions when inputs don't satisfy conditions
- Alternative paths: on failure or domain mismatch, the algorithm searches alternative routes
- Async/parallel execution: four built-in executors (`async`, `parallel`, `parallel-pool`, `parallel-dispatch`)
- Web API: convert any Dispatcher to a Flask-based REST service via `.web()`
- Visualization: plot the model and workflow graphs (requires Graphviz)
- Sub-model extraction: isolate subsets of nodes for API exposure or reuse

## Usage

```python
import schedula as sh

# Create a dispatcher (dataflow model)
dsp = sh.Dispatcher(name='calculator')

# Add functions with automatic input inference from signature
@sh.add_function(dsp, outputs=['sum'])
def add(a, b):
    return a + b

@sh.add_function(dsp, outputs=['product'])
def multiply(a, b):
    return a * b

# Add a function with an input domain guard
@sh.add_function(dsp, outputs=['log_result'], input_domain=lambda x: x > 0)
def safe_log(x):
    import math
    return math.log(x)

# Add a data node with a default value
dsp.add_data('a', default_value=10)

# Dispatch: compute outputs from given inputs
sol = dsp(inputs={'b': 5}, outputs=['sum', 'product'])
print(sol['sum'])       # 15
print(sol['product'])   # 50

# Dispatch with callable syntax (same as .dispatch())
sol = dsp({'a': 3, 'b': 4}, outputs=['sum'])

# Use selector to reuse solution values as inputs for another dispatch
sol2 = dsp(inputs=sh.selector(('sum',), sol), outputs=['log_result'])
```

### Adding Functions

Three ways to register functions:

```python
# 1. Decorator — auto-extracts parameter names as inputs
@sh.add_function(dsp, outputs=['result'], weight=2)
def my_func(x, y):
    return x + y

# 2. add_func — infers inputs from function signature
def another(a, b, c):
    return a * b + c
dsp.add_func(another, outputs=['result2'])

# 3. add_function — explicit inputs/outputs mapping
dsp.add_function(
    function_id='read_file',
    function=open_file,
    inputs=['filepath'],
    outputs=['content'],
    input_domain=os.path.isfile  # domain guard
)
```

### Sub-dispatchers

Compose dispatchers hierarchically:

```python
# Child dispatcher
child = sh.Dispatcher(name='math_ops')
child.add_function(function=max, inputs=['a', 'b'], outputs=['max_val'])

# Parent dispatcher
parent = sh.Dispatcher(name='pipeline')
parent.add_dispatcher(
    dsp_id='math',
    dsp=child,
    inputs={'X': 'a', 'Y': 'b'},   # parent -> child mapping
    outputs={'max_val': 'Z'}        # child -> parent mapping
)

sol = parent(inputs={'X': 3, 'Y': 7}, outputs=['Z'])
print(sol['Z'])  # 7
```

### Async and Parallel Execution

```python
# Async (same process, threads)
sol = dsp(executor='async')

# Parallel (separate processes, excludes SubDispatch)
sol = dsp(executor='parallel')

# Parallel with process pool
sol = dsp(executor='parallel-pool')

# Parallel including SubDispatch nodes
sol = dsp(executor='parallel-dispatch')

# For async/parallel, call .result() to resolve futures
sol = dsp(executor='async').result()

# Cleanup executors
sh.shutdown_executors()
```

### Sub-model Extraction

Extract a safe sub-model for API exposure:

```python
# Extract sub-dispatcher by node bunch
sub = dsp.get_sub_dsp(['encrypt', 'decrypt', 'key', sh.START])

# Extract from workflow (reachable nodes from sources)
sub = dsp.get_sub_dsp_from_workflow(['input_a', 'input_b'])

# Reverse extraction (nodes needed to produce outputs)
sub = dsp.get_sub_dsp_from_workflow(['output_c'], reverse=True)
```

### Web API Deployment

```python
# Deploy dispatcher as Flask REST API
server = api.web(run=False).site(host='127.0.0.1', port=5000).run()

# POST to dispatch endpoint
import requests
res = requests.post(
    'http://127.0.0.1:5000',
    json={'args': [{'decrypted': 'message'}]}
).json()

# POST to specific function endpoint
res = requests.post(
    'http://127.0.0.1:5000/dsp_name/function_id?data=input,return',
    json={'kwargs': {'key': '...', 'encrypted': '...'}}
).json()

# Shutdown
server.shutdown()
```

### Plotting

```python
# Plot the full model graph
dsp.plot()

# Plot the workflow (actual execution path)
sol = dsp(inputs={'a': 1})
sol.plot(index=True)
dsp.plot(workflow=True)
```

## Gotchas

- **`input_domain` is checked per-input arrival** — the domain function is invoked each time a new data node reaches the function, not just once. Return `True` to allow execution, `False` to skip and search alternative paths.
- **Functions execute only once** — even if the graph has cycles, nodes are computed at most once per dispatch to avoid infinite loops.
- **Weight matters for path selection** — when multiple paths exist, the modified Dijkstra uses edge/node weights to pick the shortest. Default weight is 1; set `weight` on nodes or `inp_weight`/`out_weight` on edges to influence routing.
- **`add_func` infers inputs from signature** — positional params become inputs automatically. Use `inputs_defaults=True` to also create data nodes from default parameter values. Use `inputs_kwargs=True` to include `**kwargs` as an input.
- **`raises` controls error behavior** — `raises=True` (default) stops on first error; `raises=""` logs warnings and continues; `raises=callable` lets you decide per-exception.
- **Sub-dispatcher input_domain takes a dict** — unlike function nodes where domain receives positional args, sub-dispatcher `input_domain` receives a dict of input values.
- **`get_sub_dsp` removes incomplete functions** — function nodes missing any input in the node bunch are automatically dropped from the sub-dispatcher.
- **Async/parallel has overhead** — creating/deleting threads and processes costs time. Only use for genuinely expensive functions.
- **`parallel` and `parallel-pool` exclude SubDispatch** — use `parallel-dispatch` if you need SubDispatch nodes executed in parallel too.
- **Plotting requires Graphviz** — install system Graphviz and ensure `dot` is on PATH. Use `pip install 'schedula[plot]'` for the Python side.
- **Web extra requires Flask** — install with `pip install 'schedula[web]'`. The server shuts down when the server object is garbage collected.
- **`selector` for solution reuse** — use `sh.selector(('key1', 'key2'), solution)` to extract specific values from a previous Solution as inputs for a new dispatch.
- **`wait_inputs` flag** — data nodes with `wait_inputs=True` block until all input estimations arrive. Function nodes always wait for all inputs by default.
- **`default_value` vs input** — default values are used when a node is not provided as input. They participate in the dispatch with `initial_dist` weight. Use `set_default_value()` to set/remove defaults.
- **`wildcard` data nodes** — when a data node is both input and output, `wildcard=True` means the input value propagates to connected functions but is not treated as a computed output.
- **Solution is dict-like** — access computed values with `sol['data_id']`. The `sol.workflow` attribute holds the actual DAG executed.
- **PEP 420 namespace** — schedula uses lazy imports via `__getattr__` for Python 3.7+. For older Python or to force eager imports, set `IMPORT_ALL=True` env var.
- **MicroPython compatible** — core functionality works on MicroPython. IO utilities (save/load) are unavailable there.

## References

- [01-dispatcher-api](references/01-dispatcher-api.md) — Dispatcher constructor, add_data, add_function, add_func, add_dispatcher, add_from_lists, set_default_value
- [02-dispatch-algorithm](references/02-dispatch-algorithm.md) — ArciDispatch algorithm, workflow graph, shortest path, domain guards, alternative paths
- [03-solution](references/03-solution.md) — Solution class, workflow attribute, pipe, result(), get_sub_dsp_from_workflow
- [04-async-parallel](references/04-async-parallel.md) — Executors (async, parallel, parallel-pool, parallel-dispatch), custom executors, Future handling
- [05-subdispatchers](references/05-subdispatchers.md) — SubDispatch, MapDispatch, SubDispatchFunction, SubDispatchPipe, DispatchPipe patterns
- [06-web-api](references/06-web-api.md) — Dispatcher.web(), Flask site, endpoints, JSON request/response format
- [07-plotting-io](references/07-plotting-io.md) — Graphviz plotting, save_dispatcher, load_dispatcher, save/load maps and defaults
- [08-utilities](references/08-utilities.md) — selector, combine_dicts, kk_dict, partial, stlp, bypass, summation, map_dict, map_list, Token, counter
- [09-graph](references/09-graph.md) — DiGraph, node/edge attributes, subgraph, successors, predecessors
- [10-blueprint](references/10-blueprint.md) — BlueDispatcher, Blueprint for declarative model definition
