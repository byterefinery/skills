# torch.compile Reference

## Overview

`torch.compile` is the PyTorch 2.x compilation stack. It uses `torch._dynamo` (FX-based tracer) to capture Python code as a graph, then compiles it with a backend (default: Inductor). It accelerates models without changing the API.

```python
import torch

# Compile a model
model = torch.compile(model)

# Compile a function
@torch.compile
def my_function(x, y):
    return torch.sin(x) @ torch.cos(y)

# With options
model = torch.compile(
    model,
    backend="inductor",       # compiler backend
    fullgraph=False,          # allow partial graphs
    dynamic=True,             # dynamic shape support
)
```

## Backends

| Backend | Description |
|---------|-------------|
| `"inductor"` (default) | Triton-based codegen, best performance on CUDA |
| `"aot_eager"` | Trace only, no optimization (debugging) |
| `"eager"` | No compilation (baseline) |
| `"cudagraphs"` | CUDA graph capture (replay optimization) |
| Custom | Any function `(fx_graph, example_inputs) -> callable` |

## Options

```python
model = torch.compile(
    model,
    backend="inductor",
    fullgraph=False,           # False: allow partial graphs with fallbacks
    dynamic=True,              # True: support dynamic shapes (default in 2.12)
    mode="default",            # "default", "reduce-overhead", "max-autotune"
    fullgraph=True,            # True: error if any op falls back
    disable=False,             # True: disable compilation (for testing)
    ir="aten",                 # "aten" (default) or "hvm"
)
```

### Modes

| Mode | Description |
|------|-------------|
| `"default"` | Standard compilation |
| `"reduce-overhead"` | Optimizes for small batch sizes, reduces kernel launch overhead |
| `"max-autotune"` | Extensive autotuning, slower compile, best runtime |

## Dynamic Shapes

```python
# Dynamic shapes (default in 2.12)
model = torch.compile(model, dynamic=True)

# Run with different batch sizes
output1 = model(torch.randn(1, 3, 224, 224))
output2 = model(torch.randn(8, 3, 224, 224))  # same compiled graph

# Static shapes (faster compile, no shape flexibility)
model = torch.compile(model, dynamic=False)

# Symbolic shapes
from torch._dynamo import symbolic_context
# Shapes are symbolic — any value matches
```

## Debugging

### Explain

```python
from torch._dynamo import explain

result = explain(model, example_input)
print(result.graph)           # captured FX graph
print(result.missed_reasons)  # why some ops fell back
print(result.compile_times)   # compilation time breakdown
```

### Logging

```python
import logging
logging.getLogger("torch._dynamo").setLevel(logging.DEBUG)
logging.getLogger("torch._inductor").setLevel(logging.DEBUG)
```

### Verbose

```python
import os
os.environ["TORCH_LOGS"] = "+dynamo,+inductor,+graph,+shape"
# Or: TORCHDYNAMO_VERBOSE=1
```

### Relaxed Testing

```python
# Allow any fallback without error
model = torch.compile(model, backend="aot_eager")

# Check what was captured
from torch._dynamo import reset_code_cache
reset_code_cache()
```

## Fallbacks

Operations that cannot be compiled fall back to eager execution. Common causes:

- Dynamic control flow not captured by Dynamo
- Custom C++ extensions without autograd registration
- Some third-party operations
- Python side effects (print, file I/O)

```python
# Force full graph — errors on any fallback
model = torch.compile(model, fullgraph=True)

# Check for fallbacks
from torch._dynamo import count_dynamo_graph_breaks
```

## CUDA Graphs

```python
# cudagraphs backend — captures CUDA kernel sequences for replay
model = torch.compile(model, backend="cudagraphs")

# Manual CUDA graph
graph = torch.cuda.CUDAGraph()
stream = torch.cuda.Stream()

with torch.cuda.graph(graph, stream=stream):
    output = model(input_tensor)

# Replay
stream.wait_stream(torch.cuda.current_stream())
with torch.cuda.stream(stream):
    model(input_tensor)
graph.replay()
torch.cuda.current_stream().wait_stream(stream)
```

## Custom Backends

```python
from torch._inductor import compile_fx

def my_backend(gm: torch.fx.GraphModule, example_inputs):
    # Custom compilation logic
    print(gm.graph)
    return gm.forward

model = torch.compile(model, backend=my_backend)
```

## Interaction with Other Features

### With AMP

```python
model = torch.compile(model)

for x, y in loader:
    with torch.amp.autocast("cuda"):
        output = model(x)
        loss = criterion(output, y)
    loss.backward()
    optimizer.step()
```

### With Distributed

```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP

model = FSDP(model)
model = torch.compile(model)  # compile AFTER wrapping with FSDP
```

### With Gradient Checkpointing

```python
from torch.utils.checkpoint import checkpoint

# Use use_reentrant=False for torch.compile compatibility
output = checkpoint(block, x, use_reentrant=False)
```

## Performance Tips

- **Warmup** — first forward pass triggers compilation. Run a dummy pass before benchmarking.
- **Batch size matters** — `mode="reduce-overhead"` helps with small batches.
- **Static shapes compile faster** — use `dynamic=False` when shapes are fixed.
- **`max-autotune` for production** — longer compile, best runtime.
- **Avoid graph breaks** — use `fullgraph=True` to find and fix fallbacks.
- **Cache compiled models** — compilation result is cached per unique input shape.

## torch._dynamo

```python
import torch._dynamo as dynamo

# Disable for specific functions
@torch._dynamo.disable
def non_compilable(x):
    return x + 1

# Mark subgraph for compilation
graph = dynamo.convert_frame(...)

# Check status
print(dynamo.get_compiler("inductor"))
```

## torch._inductor

```python
from torch._inductor import config

# Config options
config.coordinate_descent_tuning = True  # enable CD tuning
config.triton.unique_kernel_names = True
config.cuda.enable_autotuning = True
```
