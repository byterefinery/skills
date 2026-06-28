# TorchScript Reference

## Overview

TorchScript serializes PyTorch models into a format independent of Python. Use it for deployment to production servers, mobile (LibTorch), or interoperability with C++.

Two approaches:
- **Tracing** — record operations by running the model with example inputs
- **Scripting** — parse Python code directly (supports control flow)

## Tracing

### `torch.jit.trace(func, example_inputs, ...)`

```python
import torch
import torch.jit as jit

model = MyModel().eval()

# Trace with example input
traced = jit.trace(model, example_inputs=torch.randn(1, 3, 224, 224))

# Run traced model
output = traced(torch.randn(1, 3, 224, 224))

# Save
traced.save("model.pt")

# Load
loaded = jit.load("model.pt")
output = loaded(torch.randn(1, 3, 224, 224))
```

**Limitation:** Tracing cannot capture dynamic control flow (if/else on tensor values, variable-length loops). Use scripting for those cases.

### `torch.jit.trace_module(module, inputs, ...)`

```python
# Trace multiple entry points
traced = jit.trace_module(
    model,
    inputs={
        "forward": (torch.randn(1, 3, 224, 224),),
        "encode": (torch.randn(1, 3, 224, 224),),
    }
)
```

## Scripting

### `torch.jit.script(func)`

```python
@torch.jit.script
def my_function(x: torch.Tensor) -> torch.Tensor:
    if x.sum() > 0:
        return x.relu()
    else:
        return x.sigmoid()

# Script a module
class MyModel(torch.nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x.relu()

scripted = torch.jit.script(MyModel())
```

### Scripting Rules

- Types must be annotatable (tensors, lists, dicts, tuples, primitives)
- No dynamic Python features (setattr, getattr, eval, exec)
- No arbitrary Python objects
- Control flow must be based on tensor values or compile-time constants

```python
@torch.jit.script
def process(x: torch.Tensor, threshold: float) -> torch.Tensor:
    # OK: control flow on tensor value
    if x.mean() > threshold:
        return x * 2
    return x

# List operations
@torch.jit.script
def sum_list(tensors: List[torch.Tensor]) -> torch.Tensor:
    result = tensors[0]
    for t in tensors[1:]:
        result = result + t
    return result
```

## Saving and Loading

```python
# Save
scripted.save("model.pt")

# Load (with map_location for device placement)
loaded = torch.jit.load("model.pt", map_location="cpu")
loaded = torch.jit.load("model.pt", map_location="cuda:0")

# Load with weights_only (PyTorch 2.1+)
loaded = torch.jit.load("model.pt", weights_only=True)
```

## Inspection

```python
# Print the script
print(scripted.code())

# Print the graph
print(scripted.graph)

# Get named parameters
for name, param in scripted.named_parameters():
    print(name, param.shape)

# Get named buffers
for name, buf in scripted.named_buffers():
    print(name, buf.shape)
```

## Optimization

### `torch.jit.optimize_for_inference`

```python
# Optimize for inference (fuses operations)
optimized = torch.jit.optimize_for_inference(scripted)
```

### `torch.jit.freeze`

```python
# Freeze constants — folds constant parameters into the graph
frozen = torch.jit.freeze(scripted)
# Parameters are no longer accessible (model is read-only)
```

## Mobile Deployment

```python
from torch.utils.mobile_optimizer import optimize_for_mobile

# Optimize for mobile
optimized = optimize_for_mobile(scripted)
optimized._save_for_lite_interpreter("model.lite.pt")

# The .lite.pt file can be loaded by TorchScript Lite on Android/iOS
```

## Custom Classes

```python
@torch.jit.script
class MyConfig:
    hidden_size: int
    num_layers: int

    def __init__(self, hidden_size: int, num_layers: int):
        self.hidden_size = hidden_size
        self.num_layers = num_layers

@torch.jit.script
def use_config(config: MyConfig, x: torch.Tensor) -> torch.Tensor:
    result = x
    for _ in range(config.num_layers):
        result = result.relu()
    return result
```

## Tensor Properties

```python
# Scripted tensor operations
@torch.jit.script
def tensor_props(x: torch.Tensor) -> Tuple[int, int]:
    return x.size(0), x.size(1)

# Dict operations
@torch.jit.script
def dict_ops(d: Dict[str, torch.Tensor]) -> torch.Tensor:
    return d["key1"] + d["key2"]
```

## Interoperability

### With torch.compile

```python
# torch.compile is preferred over TorchScript for PyTorch environments
model = torch.compile(model)

# TorchScript is preferred for C++ deployment and mobile
scripted = torch.jit.script(model)
```

### Export (new format)

```python
# torch.export — newer serialization format (PyTorch 2.0+)
exported = torch.export.export(model, (torch.randn(1, 3, 224, 224),))
exported.save("model.export")
```

## Common Patterns

### Conditional Forward

```python
class ConditionalModel(torch.nn.Module):
    def forward(self, x: torch.Tensor, mode: str) -> torch.Tensor:
        if mode == "train":
            return self.training_forward(x)
        else:
            return self.inference_forward(x)

# Scripting handles the string comparison
scripted = torch.jit.script(ConditionalModel())
```

### Variable-Length Sequences

```python
@torch.jit.script
def variable_length_forward(
    embeddings: torch.Tensor,
    lengths: torch.Tensor,
) -> torch.Tensor:
    outputs = []
    for i in range(embeddings.size(0)):
        seq_len = lengths[i].item()
        outputs.append(embeddings[i, :seq_len])
    return torch.stack(outputs)
```

## Gotchas

- **Tracing ignores control flow** — `if x > 0` inside a traced function is evaluated once with the example input and baked in. Use scripting for dynamic behavior.
- **`script` is stricter than `trace`** — scripting requires type annotations and has more restrictions on Python features.
- **`jit.load` deserializes with pickle** — use `weights_only=True` when loading untrusted models.
- **Scripted modules are immutable** — you cannot call `register_module()` or modify parameters after scripting.
- **`optimize_for_mobile` changes the IR** — the optimized model may not be loadable by standard `jit.load()` on all platforms.
- **List/dict operations have limited support** — only basic operations (append, extend, indexing) are supported in TorchScript.
