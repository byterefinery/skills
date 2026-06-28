# Specialized Topics Reference

## Sparse Tensors

### Creation

```python
import torch

# COO format (coordinates + values)
indices = torch.tensor([[0, 1, 2], [2, 0, 1]])
values = torch.tensor([1.0, 2.0, 3.0])
sparse = torch.sparse_coo_tensor(indices, values, torch.Size([3, 3]))

# From dense
sparse = dense_tensor.to_sparse()
dense = sparse.to_dense()

# CSR format (row-based)
sparse_csr = torch.sparse_csr_tensor(crow_indices, col_indices, values, torch.Size([3, 3]))

# CSC format (column-based)
sparse_csc = torch.sparse_csc_tensor(ccol_indices, row_indices, values, torch.Size([3, 3]))
```

### Operations

```python
# Matrix multiply with sparse
result = sparse @ dense
result = sparse @ sparse

# Elementwise
result = sparse + sparse
result = sparse * scalar

# Reductions
result = sparse.sum()
result = sparse.norm()

# Indexing
result = sparse[0]  # row slice (returns sparse)
```

### Sparse NN Modules

```python
# Sparse linear layer
linear = nn.Linear(1000, 128)
linear.weight = nn.Parameter(linear.weight.to_sparse())

# Embedding with sparse gradients
emb = nn.Embedding(10000, 300, sparse=True)
```

## Quantization

### Dynamic Quantization

```python
from torch import quantization

# Quantize LSTM/Transformer models (weights quantized, activations dynamic)
quantized_model = quantization.quantize_dynamic(
    model,
    {nn.LSTM, nn.Linear},
    dtype=torch.qint8,
)
```

### Static Quantization

```python
# 1. Add observation points
model.fp16_model = model.float()
model.fp16_model.qconfig = quantization.default_qconfig("fbgemm")  # CPU
# model.fp16_model.qconfig = quantization.default_qconfig("qnnpack")  # mobile

# 2. Prepare (insert observers)
model_prepared = quantization.prepare(model.fp16_model)

# 3. Calibrate (run representative data)
for x, _ in calibration_loader:
    model_prepared(x)

# 4. Convert
model_quantized = quantization.convert(model_prepared)
```

### PTQ (Post-Training Quantization) with torchao

```python
from torchao import quantize_, int8_weight_only

# Int8 weight-only quantization
quantize_(model, int8_weight_only())

# Int4 weight-only
from torchao import int4_weight_only
quantize_(model, int4_weight_only())
```

### QAT (Quantization-Aware Training)

```python
# Prepare for QAT
model_qat = quantization.prepare_qat(model, example_inputs)

# Train normally
for epoch in range(epochs):
    for x, y in loader:
        loss = criterion(model_qat(x), y)
        loss.backward()
        optimizer.step()

# Convert
model_quantized = quantization.convert(model_qat)
```

## torch.func (Functional API)

```python
import torch.func

# Functional call — separate params from module
params = dict(model.named_parameters())
output, tensors_out = torch.func.functional_call(model, params, (x,))

# vmap — vectorize over any dimension
batched_forward = torch.func.vmap(lambda p: functional_call(model, p, (x_single,)))
outputs = batched_forward(batch_params)

# grad — functional gradient
def loss_fn(params):
    output = torch.func.functional_call(model, params, (x,))
    return criterion(output, y)

grads = torch.func.grad(loss_fn)(params)

# jacfwd / jacrev — Jacobians
J = torch.func.jacfwd(loss_fn)(params)
```

## Profiling

### torch.profiler

```python
import torch.profiler as profiler

with profiler.profile(
    activities=[profiler.ProfilerActivity.CPU, profiler.ProfilerActivity.CUDA],
    schedule=profiler.schedule(wait=1, warmup=1, active=3, repeat=1),
    on_trace_ready=profiler.tensorboard_trace_handler("./profiler_logs"),
    record_shapes=True,
    profile_memory=True,
    with_stack=True,
) as prof:
    for i, (x, y) in enumerate(loader):
        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()
        prof.step()

# Analysis
print(prof.key_averages().table(
    sort_by="cuda_time_total",
    row_limit=20,
))

# Export for TensorBoard
prof.export_chrome_trace("trace.json")
```

### Memory Profiling

```python
# Record memory history
torch.cuda.memory._record_memory_history(max_entries=100000)

# ... run code ...

# Dump snapshot
torch.cuda.memory._dump_snapshot("snapshot.pickle")

# Analyze (load snapshot with torch.cuda.memory._MemorySnapshot)
```

### torch.utils.benchmark

```python
import torch.utils.benchmark as benchmark

# Benchmark a function
timer = benchmark.Timer(
    setup="import torch; x = torch.randn(1024, 1024, device='cuda')",
    stmt="y = x @ x",
    iterations=10,
    time_unit=1e-6,  # microseconds
)
measured = timer.blocked_time
print(f"Matmul: {measured * 1e6:.2f} ms")
```

## torch.fx (Program Transformation)

```python
import torch.fx as fx

# Trace a module
graph_module = fx.symbolic_trace(model)

# Inspect graph
print(graph_module.graph)

# Manipulate graph
for node in graph_module.graph.nodes:
    print(f"{node.name}: {node.op} {node.target}")

# Re-compile
graph_module.recompile()
```

### FX Passes

```python
# Custom pass
def fuse_relu_linear(graph_module: fx.GraphModule):
    graph = graph_module.graph
    for node in graph.nodes:
        if (node.op == "call_module" and
            isinstance(dict(graph_module.named_modules())[node.target], nn.ReLU)):
            prev = node.previous_instruction()
            if prev and "linear" in prev.target:
                # Fuse into a single operation
                ...
    graph.lint()
    graph_module.recompile()
```

## ONNX Export

```python
import torch.onnx

# Export to ONNX
torch.onnx.export(
    model,
    x,                              # example input
    "model.onnx",                   # output path
    export_params=True,             # store training weights
    opset_version=17,               # ONNX opset version
    input_names=["input"],          # input tensor names
    output_names=["output"],        # output tensor names
    dynamic_axes={                  # dynamic shapes
        "input": {0: "batch_size"},
        "output": {0: "batch_size"},
    },
)
```

## torch.export (New Export Format)

```python
import torch

# Export
exported_program = torch.export.export(
    model,
    (torch.randn(1, 3, 224, 224),),  # example inputs
    strict=True,                      # strict mode
)

# Save
exported_program.save("model.export")

# Load
loaded = torch.export.load("model.export")

# Inspect
print(exported_program.graph_module.graph)
```

## Autocast Policies

```python
from torch.amp import custom_fwd, custom_bwd, autocast

# Mark a function to run in specific precision
@custom_fwd(device_type="cuda")
def my_forward(x):
    return x.sin()

# Custom autocast behavior
class MyModule(nn.Module):
    @torch.amp.custom_fwd(cast_inputs=torch.float32)
    def forward(self, x):
        return x @ x.T
```

## Functional Norms

```python
from torch.nn.functional import rms_norm

# RMSNorm as functional
output = torch.nn.functional.rms_norm(input, normalized_shape, weight, eps)
```

## torch.compile Config

```python
from torch._inductor import config

# Tuning config
config.coordinate_descent_tuning = True
config.triton.unique_kernel_names = True
config.cuda.enable_autotuning = True
config.cuda.compile_backward = True     # compile backward pass
config.recompile_all_cache = False       # reuse caches
```

## Distributed Tensor Parallelism

```python
from torch.distributed.tensor import DeviceMesh
from torch.distributed.tensor.parallel import parallelize_module, ColwiseParallel, RowwiseParallel

# Create device mesh
mesh = DeviceMesh("cuda", torch.arange(torch.cuda.device_count()))

# Parallelize linear layers
parallelize_module(
    model,
    mesh,
    {
        "fc1": ColwiseParallel(),
        "fc2": RowwiseParallel(),
    },
)
```

## Gotchas

- **Sparse tensors have limited operation support** — not all ops work on sparse tensors. Check documentation before using.
- **Quantized models cannot be fine-tuned** — use QAT for training with quantization. PTQ is inference-only.
- **`torch.func.vmap` differs from `torch.vmap`** — in 2.12, `torch.vmap` is the main API. `torch.func.vmap` is the older namespace.
- **ONNX export may lose operations** — not all PyTorch ops have ONNX equivalents. Check the exported model carefully.
- **`torch.export` is stricter than `torch.jit.trace`** — it requires all operations to be traceable. Use `strict=False` for lenient mode.
- **Memory profiling adds overhead** — `_record_memory_history` slows execution. Only use for debugging.
- **`torch.profiler` with `with_stack=True`** — adds significant overhead. Use only when you need Python stack traces.
- **Quantization-aware training needs calibration data** — the calibration step is critical for accurate quantization. Use representative data.
- **`torch.compile` with `config.cuda.compile_backward = True`** — compiles the backward pass too, but increases compile time. Enable for production inference.
