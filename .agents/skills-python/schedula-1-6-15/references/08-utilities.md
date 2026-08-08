# Utilities

## `selector`

Extract specific keys from a Solution or dict for reuse as inputs:

```python
from schedula import selector

# Extract keys from solution
inputs = selector(('key1', 'key2'), solution)
# Returns {'key1': solution['key1'], 'key2': solution['key2']}

# Use in dispatch
sol2 = dsp(inputs=selector(('a', 'b'), sol1), outputs=['c'])
```

## `combine_dicts`

Merge multiple dicts:

```python
from schedula import combine_dicts

merged = combine_dicts({'a': 1}, {'b': 2}, {'a': 3})
# {'a': 3, 'b': 2} — later dicts override earlier

# With copy (deepcopy values)
merged = combine_dicts({'a': [1]}, {'b': [2]}, copy=True)

# With base dict
merged = combine_dicts({'a': 1}, {'b': 2}, base={'c': 3})
# {'a': 1, 'b': 2, 'c': 3}
```

## `kk_dict`

Create dict with values identical to keys:

```python
from schedula import kk_dict

kk_dict('a', 'b', 'c')           # {'a': 'a', 'b': 'b', 'c': 'c'}
kk_dict('a', 'b', **{'a-c': 'c'})  # {'a': 'a', 'b': 'b', 'a-c': 'c'}
kk_dict({'x': 'y'}, 'z')         # {'x': 'y', 'z': 'z'}
```

## `stlp`

Convert string to tuple (single-element):

```python
from schedula import stlp

stlp('a')    # ('a',)
stlp(('a',)) # ('a',)
```

## `bypass`

Identity function — passes input through unchanged:

```python
from schedula import bypass

bypass(x)  # returns x
```

Used as default estimation function for `SINK` node.

## `summation`

Sum all values:

```python
from schedula import summation

summation({'a': 1, 'b': 2, 'c': 3})  # 6
```

## `map_dict` / `map_list`

Apply function to dict/list values:

```python
from schedula import map_dict, map_list

map_dict(str, {'a': 1, 'b': 2})  # {'a': '1', 'b': '2'}
map_list(str, [1, 2, 3])         # ['1', '2', '3']
```

## `partial`

Like `functools.partial` but adapted for schedula's dataflow:

```python
from schedula import partial

f = partial(func, arg1, kwarg1=value)
```

## `add_args`

Add fixed arguments to a function:

```python
from schedula import add_args

wrapped = add_args(func, fixed_arg)
```

## `replicate_value`

Replicate a value across multiple keys:

```python
from schedula import replicate_value

replicate_value(42, ['a', 'b', 'c'])  # {'a': 42, 'b': 42, 'c': 42}
```

## `stack_nested_keys` / `get_nested_dicts` / `combine_nested_dicts`

Work with nested dictionary structures:

```python
from schedula import stack_nested_keys, get_nested_dicts, combine_nested_dicts

# Stack keys from nested dicts
stacked = stack_nested_keys({'a': {'b': 1}})

# Get nested dicts by key path
nested = get_nested_dicts(data, 'key.path', default={})

# Combine nested dicts
combined = combine_nested_dicts(dict1, dict2)
```

## `are_in_nested_dicts`

Check if keys exist in nested dicts:

```python
from schedula import are_in_nested_dicts

are_in_nested_dicts({'a': {'b': 1}}, 'a.b')  # True
```

## `inf`

Infinity helper for distance calculations:

```python
from schedula import inf

inf(0, -1)  # Formatted infinity value
```

## `parent_func`

Get the parent function of a wrapped callable:

```python
from schedula import parent_func

original = parent_func(wrapped_function)
```

## `run_model`

Run a dispatcher model with given inputs:

```python
from schedula import run_model

result = run_model(dsp, inputs={'a': 1}, outputs=['b'])
```

## `Token`

Create unique singleton tokens (used for special node ids):

```python
from schedula import Token

my_token = Token('my_label')
```

## `counter`

Create an auto-incrementing counter:

```python
from schedula import counter

c = counter()
c()  # 0
c()  # 1
c()  # 2
```

## `counter` (function)

Global counter for node indexing.
