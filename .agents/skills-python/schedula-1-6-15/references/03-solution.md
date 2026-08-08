# Solution

## Overview

`Solution` extends `collections.OrderedDict` and stores dispatch results. It contains computed values, the workflow graph used, timing information, and references to sub-dispatcher solutions.

## Attributes

| Attribute | Type | Description |
|---|---|---|
| `sol[key]` | `T` | Computed value for data node `key` |
| `sol.inputs` | `dict` | Input values provided to dispatch |
| `sol.outputs` | `set` | Target output node ids |
| `sol.inputs_dist` | `dict` | Initial distances for input nodes |
| `sol.workflow` | `DiGraph` | Actual DAG executed (nodes + edges with values) |
| `sol.dist` | `dict` | Minimum distances to visited nodes |
| `sol.seen` | `dict` | Best known distances to reachable nodes |
| `sol.fringe` | `list` | Heap queue (set to `None` after dispatch) |
| `sol.sub_sol` | `dict` | Nested Solutions keyed by index tuple |
| `sol._visited` | `set` | Fully processed node ids |
| `sol._errors` | `OrderedDict` | Error messages per failed node |
| `sol._pipe` | `list` | Execution pipe (sequence of visited nodes) |
| `sol.parent` | `Dispatcher` | Parent dispatcher |
| `sol.index` | `tuple` | Index tuple for sub-dispatcher nesting |
| `sol.full_name` | `tuple` | Full path of dispatcher names + node id |
| `sol.verbose` | `bool\|callable` | Verbose logging mode |

## Methods

### `result(timeout=None)`

Resolve all async/parallel futures in the solution.

```python
sol = dsp(executor='async')
sol = sol.result(timeout=30)  # Wait up to 30 seconds
```

### `get_sub_dsp_from_workflow(sources, reverse=False, add_missing=False, check_inputs=True)`

Extract sub-dispatcher from the workflow graph.

```python
# Nodes reachable from 'a' and 'b'
sub = sol.get_sub_dsp_from_workflow(['a', 'b'])

# Nodes needed to produce 'c'
sub = sol.get_sub_dsp_from_workflow(['c'], reverse=True)
```

## Properties

### `pipe`

Returns the full execution pipe — the complete sequence of nodes visited during dispatch, including all sub-dispatcher nodes.

```python
pipe = sol.pipe  # List of (distance, node_id, solution) tuples
```

## Workflow Graph

The `sol.workflow` `DiGraph` contains:

### Node Attributes

| Attribute | Description |
|---|---|
| `type` | `'start'`, `'data'`, `'function'`, `'dispatcher'` |
| `solution` | Computed value (data) or Solution (sub-dispatcher) |
| `solution_domain` | Domain check result for function nodes |
| `solution_filters` | List of filter results |
| `started` | Timestamp when node execution started |
| `duration` | Execution time in seconds |

### Edge Attributes

| Attribute | Description |
|---|---|
| `value` | Data value flowing along the edge |
| `weight` | Edge weight used in distance calculation |

## Accessing Values

```python
# Direct access
value = sol['data_id']

# Check if computed
if 'data_id' in sol:
    value = sol['data_id']

# Iterate all computed values
for key, value in sol.items():
    print(key, value)

# Sub-dispatcher solution
sub = sol.sub_sol[sol.index + node['index']]
```

## Timing

```python
# Node timing from workflow
for node_id, attrs in sol.workflow.nodes.items():
    if 'duration' in attrs:
        print(f"{node_id}: {attrs['duration']:.4f}s")
```

## Errors

```python
# Check for errors
if sol._errors:
    for node_id, msg in sol._errors.items():
        print(f"Error at {node_id}: {msg}")
```
