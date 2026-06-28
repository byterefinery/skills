# CUDA Reference

## Device Management

### Querying Devices

```python
import torch

# Check availability
torch.cuda.is_available()  # True if CUDA is available

# Device count
torch.cuda.device_count()  # number of GPUs

# Current device
torch.cuda.current_device()  # index of current device

# Device name
torch.cuda.get_device_name(0)  # "NVIDIA A100-SXM4-80GB"

# Compute capability
torch.cuda.get_device_capability(0)  # (8, 0) for A100

# Memory info
torch.cuda.memory_allocated(0)    # bytes currently allocated
torch.cuda.memory_reserved(0)     # bytes reserved by cache
torch.cuda.max_memory_allocated(0)  # peak allocation
torch.cuda.max_memory_reserved(0)   # peak reservation
```

### Device Context

```python
# Set current device
torch.cuda.set_device(0)

# Device context manager
with torch.cuda.device(1):
    x = torch.randn(3, 4)  # allocated on GPU 1

# Device object
device = torch.device("cuda:0")
device = torch.device("cuda:1")
device = torch.device("cuda")    # current device
device = torch.device("cpu")

# Tensor on specific device
x = torch.randn(3, 4, device="cuda:0")
x = torch.randn(3, 4, device=torch.device("cuda:1"))
```

### Multi-GPU Patterns

```python
# Manual multi-GPU
device0, device1 = torch.device("cuda:0"), torch.device("cuda:1")
x0 = torch.randn(3, 4, device=device0)
x1 = torch.randn(3, 4, device=device1)

# Transfer between GPUs
x0_to_1 = x0.to(device1)

# Cross-device operations (auto-transfer in some ops)
result = x0 + x0_to_1  # both on device1
```

## Streams

### Creating and Using Streams

```python
# Default stream
default_stream = torch.cuda.current_stream()

# Create stream
stream = torch.cuda.Stream()

# Use stream
with torch.cuda.stream(stream):
    x = torch.randn(1000, 1000, device="cuda")
    y = x @ x.T

# Stream synchronization
stream.wait_stream(torch.cuda.current_stream())
torch.cuda.current_stream().wait_stream(stream)

# Multiple streams for overlap
stream1 = torch.cuda.Stream()
stream2 = torch.cuda.Stream()

with torch.cuda.stream(stream1):
    compute_task1()

with torch.cuda.stream(stream2):
    compute_task2()

# Wait for both
stream1.synchronize()
stream2.synchronize()
```

### Stream with DataLoader

```python
# DataLoader with non-blocking transfer
stream = torch.cuda.Stream()

for x, y in loader:
    with torch.cuda.stream(stream):
        x = x.cuda(non_blocking=True)
        y = y.cuda(non_blocking=True)
    stream.synchronize()
    # Compute on default stream while next batch transfers
```

## Memory Management

### Manual Management

```python
# Cache info
print(torch.cuda.memory_summary())  # detailed summary

# Empty cache (rarely needed)
torch.cuda.empty_cache()

# Memory snapshot
from torch.cuda import memory_stats, memory_summary
stats = memory_stats(device="cuda:0")
summary = memory_summary(device="cuda:0", expanded=True)
```

### Memory Fragmentation

```python
# Check fragmentation
allocated = torch.cuda.memory_allocated()
reserved = torch.cuda.memory_reserved()
print(f"Fragmentation: {(reserved - allocated) / reserved * 100:.1f}%")

# Reduce fragmentation
torch.cuda.empty_cache()  # frees unused cached memory
```

**Rule:** `empty_cache()` is rarely needed. PyTorch's CUDA cache allocator is efficient. Only call when doing dynamic model switching or explicit memory management.

## CUDA Graphs

### Basic Usage

```python
# Record
graph = torch.cuda.CUDAGraph()
stream = torch.cuda.Stream()

# Warmup (required before recording)
output = model(warmup_input)

# Record phase
with torch.cuda.graph(graph, stream=stream):
    input_tensor.fill_(7)  # must reuse same tensor
    output = model(input_tensor)

# Replay phase
for _ in range(100):
    input_tensor.fill_(7)
    stream.wait_stream(torch.cuda.current_stream())
    with torch.cuda.stream(stream):
        graph.replay()
    torch.cuda.current_stream().wait_stream(stream)
```

### Graph Constraints

- Input tensors must be reused (same memory)
- Output tensors are cached (cannot be freed)
- Graph is device-specific
- Dynamic shapes require separate graphs per shape

## cuDNN

```python
# Benchmark mode — lets cuDNN choose fastest algorithm
torch.backends.cudnn.benchmark = True

# Deterministic mode — reproducible but potentially slower
torch.backends.cudnn.deterministic = True

# Check version
print(torch.backends.cudnn.version())

# Enable/disable
torch.backends.cudnn.enabled = True
```

**Rule:** Set `benchmark = True` for fixed input sizes (faster). Set `deterministic = True` for reproducibility. Both cannot be True simultaneously in some cases.

## Custom CUDA Kernels

### torch.cuda.compile_nvfuser

```python
# NVFuser fuses pointwise operations
from torch._inductor import compile_fx
```

### Custom Kernel with torch.library

```python
import torch
import torch.library

# Define custom op
@torch.library.impl("my_lib::my_op", "CUDA")
def my_op_cuda(x: torch.Tensor) -> torch.Tensor:
    # CUDA kernel implementation
    return x * 2

# Register
torch.library.define("my_lib::my_op", "(Tensor) -> Tensor")
```

### CUDA Kernel with triton

```python
import triton
import triton.language as tl

@triton.jit
def add_kernel(x_ptr, y_ptr, output_ptr, n_elements, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(axis=0)
    block_start = pid * BLOCK_SIZE
    offsets = block_start + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_elements
    x = tl.load(x_ptr + offsets, mask=mask)
    y = tl.load(y_ptr + offsets, mask=mask)
    tl.store(output_ptr + offsets, x + y, mask=mask)

# Launch
n = x.numel()
grid = lambda meta: (triton.cdiv(n, meta["BLOCK_SIZE"]),)
output = torch.empty_like(x)
add_kernel[grid](x, y, output, n, BLOCK_SIZE=1024)
```

## Profiling

```python
import torch.profiler as profiler

# Profiler
with profiler.profile(
    activities=[
        profiler.ProfilerActivity.CPU,
        profiler.ProfilerActivity.CUDA,
    ],
    schedule=profiler.schedule(wait=1, warmup=1, active=3, repeat=1),
    on_trace_ready=profiler.tensorboard_trace_handler("./logs"),
    record_shapes=True,
    profile_memory=True,
) as prof:
    for i, (x, y) in enumerate(loader):
        output = model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()
        prof.step()

# Print timeline
print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))
```

### Memory Profiling

```python
# Track memory allocations
torch.cuda.memory._record_memory_history(max_entries=100000)

# ... run code ...

# Dump snapshot
torch.cuda.memory._dump_snapshot("memory_snapshot.pickle")

# Analyze with nvidia-smi or PyTorch Memory Profiler
```

## Synchronization

```python
# Device synchronization (blocks until all ops complete)
torch.cuda.synchronize()

# Stream synchronization
stream.synchronize()

# Event-based timing
start = torch.cuda.Event(record_timing=True)
end = torch.cuda.Event(record_timing=True)

start.record()
# ... operations ...
end.record()
torch.cuda.synchronize()
print(f"Time: {start.elapsed_time(end)} ms")
```

## Tensor Cores

```python
# Check if tensor cores are available
print(torch.cuda.get_device_properties(0).major >= 7)  # Volta+

# tf32 (Ampere+)
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# bfloat16 (Volta+)
x = torch.randn(3, 4, dtype=torch.bfloat16, device="cuda")
```

**Rule:** Enable `allow_tf32` for faster matmul on Ampere+ GPUs with minimal precision loss. Disable for strict reproducibility.

## Gotchas

- **`.cuda()` vs `.to("cuda")`** — `.to("cuda")` is device-agnostic. Use it for portable code.
- **`non_blocking=True`** — only works with pinned memory tensors. DataLoader with `pin_memory=True` provides pinned tensors.
- **CUDA errors are deferred** — errors may surface on the next CUDA operation or `synchronize()`. Use `torch.cuda.synchronize()` after suspect operations.
- **Memory leaks from closures** — tensors captured in closures keep memory alive. Detach or delete references explicitly.
- **`torch.cuda.empty_cache()` does not free used memory** — it only releases unused cached memory back to the OS.
- **Cross-device operations auto-transfer** — `cuda_tensor + cpu_tensor` transfers CPU tensor to GPU. Be explicit about device placement.
- **CUDA graph input must be reused** — cannot create new tensors during replay. Use `.fill_()` or `.copy_()` on the recorded tensor.
- **`benchmark = True` with dynamic shapes** — cuDNN re-benchmarks on shape change, adding overhead. Use `False` for highly dynamic workloads.
