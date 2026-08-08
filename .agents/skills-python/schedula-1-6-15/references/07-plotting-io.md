# Plotting and I/O

## Plotting

Requires Graphviz installed on the system and the `plot` extra: `pip install 'schedula[plot]'`.

### Plot Dispatcher Model

```python
# Plot the full dataflow graph
dsp.plot()

# With options
dsp.plot(
    engine='dot',           # Graphviz layout engine: dot, neato, fdp, twopi, circo
    filename='model.png',   # Output file path
    format='png',           # Output format: png, pdf, svg, etc.
    show=True,              # Display in viewer
    **graph_attr            # Passed to Graphviz (e.g., graph_attr={'ratio': '1'})
)
```

### Plot Workflow

```python
# Plot the actual execution path
sol = dsp(inputs={'a': 1})
sol.plot()

# With node index labels
sol.plot(index=True)

# Plot workflow of dispatcher (from last solution)
dsp.plot(workflow=True, index=True, engine='fdp')
```

### Plot Node Types

- **Data nodes** — displayed with their id and value
- **Function nodes** — displayed with function id
- **Sub-dispatcher nodes** — displayed with dispatcher name
- **Workflow edges** — show data values flowing between nodes

## I/O Utilities

Requires the `io` extra: `pip install 'schedula[io]'`.

### Save/Load Dispatcher

```python
from schedula import save_dispatcher, load_dispatcher

# Save to JSON file
save_dispatcher(dsp, 'model.json')

# Load from JSON file
loaded = load_dispatcher('model.json')
```

### Save/Load Default Values

```python
from schedula import save_default_values, load_default_values

# Save default values
save_default_values(dsp.default_values, 'defaults.json')

# Load default values
defaults = load_default_values('defaults.json')
dsp.default_values = defaults
```

### Save/Load Maps

```python
from schedula import save_map, load_map

# Save a mapping dict
save_map(mapping, 'map.json')

# Load a mapping dict
mapping = load_map('map.json')
```

## Format

All I/O functions use JSON format by default. The Dispatcher is serialized as:

```json
{
    "name": "my_dispatcher",
    "description": "...",
    "raises": false,
    "executor": null,
    "default_values": {...},
    "nodes": {
        "data_id": {"type": "data", ...},
        "func_id": {"type": "function", "inputs": [...], "outputs": [...], ...}
    },
    "edges": [...],
    "sub_dispatchers": {...}
}
```

Note: function objects cannot be serialized. When loading, functions must be re-registered manually.
