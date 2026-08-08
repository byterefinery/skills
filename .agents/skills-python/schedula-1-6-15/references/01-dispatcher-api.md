# Dispatcher API

## Constructor

```python
Dispatcher(dmap=None, name='', default_values=None, raises=False,
           description='', executor=False)
```

| Parameter | Type | Description |
|---|---|---|
| `dmap` | `DiGraph` | Directed graph storing data & function parameters |
| `name` | `str` | Dispatcher name |
| `default_values` | `dict[str, dict]` | Data node default values used when not specified as inputs |
| `raises` | `bool\|callable\|str` | `True` = stop on error; `""` = log warning; callable = decide per exception |
| `description` | `str` | Dispatcher description (set as `__doc__`) |
| `executor` | `str` | Default executor: `async`, `parallel`, `parallel-pool`, `parallel-dispatch` |

### Attributes

- `dsp.dmap` — the underlying `DiGraph`
- `dsp.nodes` — alias for `dsp.dmap.nodes`
- `dsp.default_values` — dict of default values
- `dsp.raises` — error handling mode
- `dsp.executor` — default executor
- `dsp.solution` — last `Solution` from dispatch
- `dsp.counter` — node index counter

## Adding Data Nodes

```python
dsp.add_data(data_id=None, default_value=EMPTY, initial_dist=0.0,
             wait_inputs=False, wildcard=None, function=None,
             callback=None, description=None, filters=None,
             await_result=None, **kwargs)
```

| Parameter | Description |
|---|---|
| `data_id` | Node id; auto-assigned if `None` (`'unknown<N>'`) |
| `default_value` | Default value used when not provided as input |
| `initial_dist` | Distance weight when default value is used in ArciDispatch |
| `wait_inputs` | Block until all input estimations arrive |
| `wildcard` | If `True`, input+output nodes propagate input but don't treat as computed output. `2` excludes uncomputable nodes |
| `function` | Estimation function: takes dict of estimations, returns single value |
| `callback` | Called after node estimation with the computed value |
| `filters` | List of post-processing functions applied after main computation |
| `await_result` | Wait for async results before assignment; number = timeout |

### Special Data Nodes

- `START` — starting node for initial inputs
- `SINK` — collects unused outputs
- `SELF` — contains the Dispatcher itself
- `PLOT` — auto-plots solution (with `autoplot_callback` and `autoplot_function`)

## Adding Function Nodes

### `add_function` — explicit inputs/outputs

```python
dsp.add_function(function_id=None, function=None, inputs=None, outputs=None,
                 input_domain=None, weight=None, inp_weight=None,
                 out_weight=None, description=None, filters=None,
                 await_domain=None, await_result=None, **kwargs)
```

| Parameter | Description |
|---|---|
| `function_id` | Node id; defaults to `function.__name__` |
| `function` | Callable to execute |
| `inputs` | Ordered list of data node ids (function arguments) |
| `outputs` | Ordered list of data node ids (function return values) |
| `input_domain` | Predicate: same args as function, returns `True`/`False` |
| `weight` | Node weight for shortest-path calculation |
| `inp_weight` | Dict of edge weights from input data nodes to this function |
| `out_weight` | Dict of edge weights from this function to output data nodes |
| `await_domain` | Wait for all inputs before checking domain (async); number = timeout |
| `await_result` | Wait for output results before assignment; number = timeout |

If `inputs` is `None`, defaults to `[START]`. If `outputs` is `None`, defaults to `[SINK]`.

### `add_func` — signature inference

```python
dsp.add_func(function, outputs=None, weight=None, inputs_defaults=False,
             inputs_kwargs=False, filters=None, input_domain=None,
             await_domain=None, await_result=None, inp_weight=None,
             out_weight=None, description=None, inputs=None,
             function_id=None, **kwargs)
```

| Parameter | Description |
|---|---|
| `inputs_defaults` | Create data nodes from function default parameter values |
| `inputs_kwargs` | Include `**kwargs` as an input |
| `inputs` | Explicit input list; if `None`, inferred from function signature |

### `add_function` decorator

```python
@sh.add_function(dsp, outputs=['result'], weight=2)
def my_func(x, y):
    return x + y
```

Auto-extracts parameter names as inputs. Supports all `add_function` kwargs.

## Adding Sub-dispatchers

```python
dsp.add_dispatcher(dsp, inputs=None, outputs=None, dsp_id=None,
                   input_domain=None, weight=None, inp_weight=None,
                   description=None, include_defaults=False,
                   await_domain=None, inputs_prefix='',
                   outputs_prefix='', **kwargs)
```

| Parameter | Description |
|---|---|
| `dsp` | Child Dispatcher or dict for `add_from_lists` |
| `inputs` | Parent-to-child mapping: `{parent_id: child_id}` or tuple of ids |
| `outputs` | Child-to-parent mapping: `{child_id: parent_id}` |
| `dsp_id` | Node id; defaults to `dsp.name` |
| `input_domain` | Dict-taking predicate: `(dict) -> bool` |
| `include_defaults` | Import child's default values into parent |
| `inputs_prefix` / `outputs_prefix` | Prefix added to parent-side node ids |

## Batch Addition

```python
data_ids, fun_ids, dsp_ids = dsp.add_from_lists(data_list, fun_list, dsp_list)
```

Each list contains dicts of kwargs passed to `add_data`, `add_function`, `add_dispatcher` respectively.

## Default Values

```python
dsp.set_default_value(data_id, value=EMPTY, initial_dist=0.0)
```

Set or remove (`EMPTY`) a data node's default value. Default values participate in dispatch with `initial_dist` weight.

## Sub-model Extraction

```python
# By node/edge bunch
sub_dsp = dsp.get_sub_dsp(nodes_bunch, edges_bunch=None)

# From workflow (BFS from sources)
sub_dsp = dsp.get_sub_dsp_from_workflow(
    sources, graph=None, reverse=False, add_missing=False,
    check_inputs=True, blockers=None, wildcard=False,
    _update_links=True, avoid_cycles=False
)
```

`get_sub_dsp` removes function nodes with incomplete inputs and isolated nodes. `get_sub_dsp_from_workflow` uses BFS on the workflow graph; `reverse=True` traces backward from outputs.

## Dispatch

```python
sol = dsp.dispatch(inputs, outputs=None, wildcard=False, initial_dist=0.0,
                   no_call=False, rm_unused_nds=False, wait_in=None,
                   no_domain=False, executor=False, verbose=False,
                   excluded_defaults=(), **kwargs)

# Callable shorthand
sol = dsp(inputs={'a': 1}, outputs=['b'])
```

| Parameter | Description |
|---|---|
| `inputs` | Dict of `{data_id: value}` or list of data ids |
| `outputs` | Target data node ids; if `None`, all reachable nodes computed |
| `wildcard` | Input+output nodes propagate but aren't treated as computed |
| `no_call` | Build workflow without executing functions |
| `rm_unused_nds` | Remove function/sub-dsp nodes with no outputs |
| `no_domain` | Skip all `input_domain` checks |
| `executor` | Override default executor |
| `verbose` | Log start/end of each node; callable for custom logging |

## Copy and Shrink

```python
copy = dsp.copy_structure(**kwargs)  # Copy structure, not data

# Shrink to keep only nodes reachable from given sources
shrink = dsp.shrink_dsp(sources, reverse=False)
```
