# Sub-dispatchers

## Overview

Sub-dispatchers nest one Dispatcher inside another, creating modular, reusable dataflow components. The parent Dispatcher bridges to the child by mapping data nodes between them.

## `add_dispatcher`

```python
dsp.add_dispatcher(dsp=child, inputs={'parent_A': 'child_a'},
                   outputs={'child_b': 'parent_B'})
```

The `inputs` dict maps parent node ids to child node ids. The `outputs` dict maps child node ids to parent node ids.

## SubDispatch Classes

### `SubDispatch`

Wrap a child dispatcher with fixed input/output mappings:

```python
from schedula.utils.dsp import SubDispatch

sub = SubDispatch(
    child_dispatcher,
    inputs={'parent_in': 'child_in'},
    outputs={'child_out': 'parent_out'}
)

dsp.add_dispatcher(dsp=sub, dsp_id='my_sub')
```

### `MapDispatch`

Map multiple child dispatchers with the same structure:

```python
from schedula.utils.dsp import MapDispatch

# Apply the same child dispatcher to multiple input sets
mapped = MapDispatch(child_dispatcher, input_map, output_map)
```

### `SubDispatchFunction`

Wrap a single function as a sub-dispatcher:

```python
from schedula.utils.dsp import SubDispatchFunction

# Converts a function into a dispatcher-like node
sub_func = SubDispatchFunction(func, inputs=['a', 'b'], outputs=['c'])
```

### `SubDispatchPipe`

Chain multiple sub-dispatchers in a pipeline:

```python
from schedula.utils.dsp import SubDispatchPipe

pipe = SubDispatchPipe([sub1, sub2, sub3])
```

### `DispatchPipe`

Create a pipeline from a list of functions:

```python
from schedula.utils.dsp import DispatchPipe

# Each function's output feeds the next function's input
pipe = DispatchPipe([func1, func2, func3])
dsp.add_dispatcher(dsp=pipe, inputs={'in': 'start'}, outputs={'out': 'end'})
```

## Nested Solutions

Sub-dispatcher results are stored in `sol.sub_sol` keyed by index tuples:

```python
# Access sub-dispatcher solution
for dsp_id, node in dsp.dsp_nodes.items():
    sub_index = sol.index + node['index']
    sub_sol = sol.sub_sol[sub_index]
    print(sub_sol)  # Solution of the sub-dispatcher
```

## Remote Links

When a data node is shared between parent and child dispatcher, schedula automatically passes computed values across the bridge:

```python
# Data node 'shared' exists in both parent and child
parent.add_dispatcher(
    child,
    inputs={'shared': 'shared', 'parent_only': 'child_in'},
    outputs={'child_out': 'parent_result', 'shared': 'shared'}
)
```

The `_see_remote_link_node` method handles propagating values from child outputs back to parent consumers.

## Domain on Sub-dispatchers

Sub-dispatcher `input_domain` receives a **dict** of input values (not positional args):

```python
def check_inputs(kwargs):
    return kwargs['temperature'] > 0 and kwargs['pressure'] > 0

dsp.add_dispatcher(
    child,
    inputs={'temp': 'temperature', 'press': 'pressure'},
    outputs={'result': 'output'},
    input_domain=check_inputs  # receives {'temp': value, 'press': value}
)
```

## Include Defaults

```python
# Import child's default values into parent
dsp.add_dispatcher(child, inputs={'A': 'a'}, outputs={'b': 'B'},
                   include_defaults=True)
```

## Prefix Mapping

```python
# Add prefixes to parent-side node ids
dsp.add_dispatcher(
    child,
    inputs={'x': 'a', 'y': 'b'},
    outputs={'c': 'z'},
    inputs_prefix='in_',    # becomes {'in_x': 'a', 'in_y': 'b'}
    outputs_prefix='out_'   # becomes {'c': 'out_z'}
)
```

## Example: Modular Pipeline

```python
import schedula as sh

# Stage 1: data loading
load_dsp = sh.Dispatcher(name='load')
@sh.add_function(load_dsp, outputs=['data'])
def load_data(path):
    return open(path).read()

# Stage 2: processing
proc_dsp = sh.Dispatcher(name='process')
@sh.add_function(proc_dsp, outputs=['processed'])
def process(data):
    return data.upper()

# Stage 3: saving
save_dsp = sh.Dispatcher(name='save')
@sh.add_function(save_dsp, outputs=['saved'])
def save(path, content):
    with open(path, 'w') as f:
        f.write(content)
    return True

# Compose pipeline
pipeline = sh.Dispatcher(name='pipeline')
pipeline.add_dispatcher(load_dsp, inputs={'file_path': 'path'},
                        outputs={'data': 'raw_data'})
pipeline.add_dispatcher(proc_dsp, inputs={'data': 'raw_data'},
                        outputs={'processed': 'result'})
pipeline.add_dispatcher(save_dsp, inputs={'path': 'out_path', 'content': 'result'},
                        outputs={'saved': 'success'})

sol = pipeline(inputs={'file_path': 'input.txt', 'out_path': 'output.txt'})
```
