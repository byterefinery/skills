# Dispatch Algorithm

## ArciDispatch Overview

The ArciDispatch algorithm is a modified Dijkstra shortest-path algorithm that determines the control flow (workflow DAG) at runtime. It operates on the weighted directed graph (`dmap`) of the Dispatcher.

### Execution Flow

1. **Initialization** — `START` node places input data onto key arcs with initial distances
2. **Fringe heap** — maintains `(distance, wait_flag, (node_id, solution))` tuples; closest node processed first
3. **Node visitation** — when a node is visited:
   - **Data node**: computes estimation (single value or aggregation via `function` attribute), sets output value
   - **Function node**: checks `input_domain`, evaluates function, places results on output arcs
   - **Sub-dispatcher node**: initializes child Solution, passes mapped inputs
4. **Target check** — algorithm terminates when all output targets are visited
5. **Alternative paths** — on domain mismatch or function failure, the algorithm continues searching other routes

### Distance Calculation

The distance to a node `w` from node `v` is:

```
dist[w] = dist[v] + edge_weight(v->w) + node_weight(w)
```

- `edge_weight` — from `inp_weight`/`out_weight` on function nodes, or edge attributes
- `node_weight` — from `weight` attribute on function nodes (default 1)
- `initial_dist` — added when a default value is used as input

### Key Data Structures

| Structure | Purpose |
|---|---|
| `fringe` | Min-heap of `(distance, virtual_dist, (node_id, solution))` |
| `dist` | Minimum distance to each visited node |
| `seen` | Best known distance to each reachable node |
| `_meet` | Maximum distance view (for wildcard handling) |
| `_visited` | Set of fully processed nodes |
| `workflow` | `DiGraph` of the actual execution path |
| `sub_sol` | Dict mapping index tuples to nested Solutions |

### Domain Guards

`input_domain` is checked **each time** a new input reaches the node, not just once. The function receives the same arguments as the main function (for function nodes) or a dict of inputs (for sub-dispatcher nodes).

```python
# Function node domain — receives positional args
dsp.add_function('log', log_func, inputs=['x'], outputs=['result'],
                 input_domain=lambda x: x > 0)

# Sub-dispatcher domain — receives dict
dsp.add_dispatcher(child, inputs={'A': 'a'}, outputs={'b': 'B'},
                   input_domain=lambda kwargs: kwargs['A'] > 0)
```

When domain returns `False`, the node is skipped and the algorithm searches alternative paths. The `solution_domain` attribute on the workflow node records the domain check result.

### Error Handling

Three modes controlled by `raises`:

| Mode | Behavior |
|---|---|
| `True` (default) | Stop dispatch on first error, raise `DispatcherError` |
| `""` (empty string) | Log error as warning, continue dispatch |
| `callable` | Call with exception; raise or skip based on return |

Errors are recorded in `sol._errors[node_id]` regardless of mode.

### Wait Inputs

Data nodes with `wait_inputs=True` block until all input estimations arrive. Function nodes always wait for all inputs. Use `_wait_in` dict to override per-node.

```python
# Data node waits for all inputs before computing
dsp.add_data('avg', wait_inputs=True, function=lambda est: sum(est.values()) / len(est))
```

### Wildcard Nodes

When `wildcard=True` on a data node that is both input and output:
- The input value propagates to connected functions
- The node is not treated as a computed output
- `wildcard=2` additionally excludes nodes that cannot be calculated

Set via `dispatch(wildcard=True)` or per-node in `add_data(wildcard=True)`.

### Virtual Distance

The fringe heap uses virtual distance `(wait, str(node_id), index_tuple)` for tie-breaking:
- `wait` — 0 for ready nodes, 1 for nodes waiting inputs
- `str(node_id)` — lexicographic ordering for determinism
- `index_tuple` — node creation order for sub-dispatcher resolution

### No-Call Mode

`dispatch(no_call=True)` builds the workflow graph without executing any functions. Useful for:
- Inspecting which functions would be called
- Extracting sub-models with `get_sub_dsp_from_workflow`
- Validating the dataflow structure

```python
# Build workflow without execution
sol = dsp(inputs={'a': 1}, outputs=['c'], no_call=True)
# sol.workflow contains the planned DAG
# sol values are all NONE
```
