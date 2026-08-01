# Session Options & Configuration — ONNX Runtime 1.28.0

## Overview

Session options control graph optimization, threading, memory management, quantization behavior, EP configuration, and model loading format. Options are set via `SessionOptions` properties or `add_session_config_entry()` for fine-grained keys.

## Threading

```python
opts = ort.SessionOptions()
opts.inter_op_num_threads = 2   # Parallel ops (independent nodes)
opts.intra_op_num_threads = 4   # Threads within a single op
opts.execution_mode = ort.ExecutionMode.ORT_PARALLEL
```

### Config Keys

| Key | Values | Description |
|---|---|---|
| `session.inter_op.allow_spinning` | `"0"`, `"1"` | Allow threads to spin before blocking |
| `session.intra_op.allow_spinning` | `"0"`, `"1"` | Same for intra-op |
| `session.inter_op.spin_duration_us` | microseconds | Target spin duration (subordinate to allow_spinning) |
| `session.intra_op.spin_duration_us` | microseconds | Same for intra-op |
| `session.inter_op.spin_backoff_max` | int (1-64) | Exponential backoff cap (1 = no backoff) |
| `session.intra_op.spin_backoff_max` | int (1-64) | Same for intra-op |

**Defaults:** spinning enabled (`"1"`) in server builds, disabled (`"0"`) in client builds.

### Single-Threaded Execution

```python
import os
os.environ["OMP_NUM_THREADS"] = "1"

opts = ort.SessionOptions()
opts.inter_op_num_threads = 1
opts.intra_op_num_threads = 1
opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
```

## Graph Optimization

```python
opts.optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
```

### Levels

| Level | Optimizations |
|---|---|
| `ORT_DISABLE_ALL` | No optimizations |
| `ORT_ENABLE_BASIC` | Constant folding, unused node removal |
| `ORT_ENABLE_EXTENDED` | Basic + node fusion (Conv+Bn, MatMul+Bn, etc.) |
| `ORT_ENABLE_ALL` | Extended + ML-specific fusions (Attention, etc.) |

### Config Keys

| Key | Values | Description |
|---|---|---|
| `session.graph_optimizations_loop_level` | `"0"`, `"1"`, `"2"` | Optimization loop: 0=none, 1=Level4-triggered, 2=Level2+ triggered |
| `optimization.disable_specified_optimizers` | comma-separated names | Disable specific optimizers |
| `optimization.constant_folding_max_output_size_in_bytes` | bytes or `"0"` | Max output size per constant-folded node (default: 1 GB) |
| `optimization.enable_gelu_approximation` | `"0"`, `"1"` | Enable GELU approximation (may affect accuracy) |
| `optimization.enable_cast_chain_elimination` | `"0"`, `"1"` | Enable cast chain elimination |
| `session.disable_aot_function_inlining` | `"0"`, `"1"` | Disable AOT function inlining |
| `session.disable_prepacking` | `"0"`, `"1"` | Disable prepacking (default: enabled) |

### Save Optimized Model

```python
opts.optimized_model_path = "optimized_model.onnx"
# Save in ORT format
opts.add_session_config_entry("session.save_model_format", "ORT")
```

## Memory

### Arena Configuration

```python
# Via EP options
providers=[("CUDAExecutionProvider", {
    "arena_extend_strategy": "kSameAsRequested",
    "gpu_mem_limit": "4294967296",  # 4 GB
})]
```

### Config Keys

| Key | Values | Description |
|---|---|---|
| `session.use_env_allocators` | `"0"`, `"1"` | Use environment-level allocators |
| `session.use_device_allocator_for_initializers` | `"0"`, `"1"` | Allocate initializers on device |
| `session.enable_cpu_mem_arena` | `"0"`, `"1"` | Enable CPU memory arena |
| `session.set_denormal_as_zero` | `"0"`, `"1"` | Flush denormals to zero |

### ORT Format Memory Mapping

```python
# Load ORT model with memory mapping (zero-copy initializers)
opts.add_session_config_entry("session.use_memory_mapped_ort_model", "1")
opts.add_session_config_entry("session.use_ort_model_bytes_for_initializers", "1")
```

## Model Loading

| Key | Values | Description |
|---|---|---|
| `session.load_model_format` | `ONNX`, `ORT` | Force model format (auto-detected by default) |
| `session.use_ort_model_bytes_directly` | `"0"`, `"1"` | Use model bytes directly (no copy) |

## Quantization

| Key | Values | Description |
|---|---|---|
| `session.disable_quant_qdq` | `"0"`, `"1"` | Disable QDQ fusion (default: enabled) |
| `session.disable_qdq_constant_folding` | `"0"`, `"1"` | Prevent DequantizeLinear constant folding |
| `session.disable_double_qdq_remover` | `"0"`, `"1"` | Disable Double QDQ removal |
| `session.enable_quant_qdq_cleanup` | `"0"`, `"1"` | Remove QDQ pairs after all handling |
| `session.qdqisint8allowed` | `"0"`, `"1"` | Allow INT8 for QDQ on ARM |

## EP Graph Assignment

```python
# Enable recording of EP assignment info
opts.add_session_config_entry("session.record_ep_graph_assignment_info", "1")

session = ort.InferenceSession("model.onnx", sess_options=opts)
assignment = session.get_provider_graph_assignment_info()
```

## Logging

```python
opts.log_severity_level = 0  # 0=VERBOSE, 1=INFO, 2=WARNING, 3=ERROR, 4=FATAL
opts.log_id = "my_session"

# Global
ort.set_default_logger_severity(0)
```

## Profiling

```python
opts.enable_profiling = True
opts.profiling_file_name = "profile.json"

session = ort.InferenceSession("model.onnx", sess_options=opts)
# ... run inference ...
session.end_profiling()  # Writes to profiling_file_name

start_ns = session.get_profiling_start_time_ns()
```

## Execution Order

```python
opts.execution_order = ort.ExecutionOrder.ORT_EXECUTION_ORDER_TOPOLOGICAL
# or ORT_EXECUTION_ORDER_BREADTH_FIRST
```

## Custom Ops

```python
# Register custom op library
opts.register_custom_ops_library("libcustom_ops.so")

# Register EP context
opts.register_ep_context()

# Register EP library
ort.register_execution_provider_library("libplugin_ep.so")
```

## External Initializers

```python
# When creating session, override initializers at runtime
overridable = session.get_overridable_initializers()
inputs = {session.get_inputs()[0].name: input_data}
for init in overridable:
    inputs[init.name] = new_initializer_data

outputs = session.run(None, inputs)
```

## Memory Optimizer (Training)

```python
# Environment variables (training only)
# export ORTMODULE_MEMORY_OPT_LEVEL=1  # Transformer layerwise recompute
# export ORTMODULE_MEMORY_OPT_CONFIG=mem_opt.json  # User-selected subgraphs

# Config key
opts.add_session_config_entry(
    "optimization.memory_optimizer_config",
    "/path/to/mem_opt.json"
)
```

## Provider Selection Policy

```python
# Auto-select provider based on device preference
opts.set_provider_selection_policy(ort.OrtExecutionProviderDevicePolicy.PREFER_NPU)
# Other policies: PREFER_GPU, PREFER_CPU
```

## Global Thread Pool

```python
# Set global thread pool sizes (applies to all sessions)
ort.set_global_thread_pool_sizes(intra=4, inter=2)
```

## Custom Allocators

```python
memory_info = ort.OrtMemoryInfo("cpu", ort.OrtAllocatorType.DEFAULT)
arena_cfg = ort.OrtArenaCfg(
    chunk_size_standards=[1024, 4096, 16384],
    max_dead_bytes_per_chunk=1024,
    recycling_threshold=0.5,
)
ort.create_and_register_allocator(memory_info, arena_cfg)
```

## Reproducibility

```python
ort.set_seed(42)
```

## Telemetry

```python
ort.disable_telemetry_events()
ort.enable_telemetry_events()
```

## Common Config Key Patterns

| Area | Key Pattern | Example |
|---|---|---|
| Session | `session.<key>` | `session.disable_prepacking` |
| Optimization | `optimization.<key>` | `optimization.enable_gelu_approximation` |
| EP-specific | `ep.<provider>.<key>` | `ep.cuda.enable_cuda_graph` |
| Threading | `session.{inter,intra}_op.<key>` | `session.intra_op.allow_spinning` |

## Gotchas

- **`optimization_level` is the primary control** — config keys fine-tune within the chosen level
- **`session.graph_optimizations_loop_level` defaults to `"1"`** — Level 4 optimizations trigger re-checking of earlier levels
- **Thread spinning** — enabled by default in server builds; disable for power-sensitive workloads
- **`constant_folding_max_output_size_in_bytes`** — protects against malicious models; default 1 GB
- **QDQ fusion** — enabled by default; disable for EPs that handle quantization themselves (DirectML, WebNN)
- **Memory-mapped ORT models** — the file must remain accessible and immutable during session lifetime
- **`use_ort_model_bytes_directly`** — caller must keep model bytes alive for session lifetime
- **Provider selection policy** — only works when providers are not explicitly specified in `InferenceSession()`
