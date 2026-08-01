# Python API Reference — ONNX Runtime 1.28.0

## InferenceSession

The main class for running ONNX models.

### Constructor

```python
ort.InferenceSession(
    path_or_bytes: str | bytes | os.PathLike,
    sess_options: SessionOptions | None = None,
    providers: Sequence[str | tuple[str, dict]] | None = None,
    provider_options: Sequence[dict] | None = None,
)
```

- `path_or_bytes` — path to `.onnx` or `.ort` file, or raw model bytes
- `providers` — ordered by precedence; can be strings or `(name, options_dict)` tuples
- Model format auto-detected from extension (`.ort` = ORT format, else ONNX)

### Key Methods

| Method | Description |
|---|---|
| `run(output_names, input_feed, run_options=None)` | Execute inference, return list of numpy arrays |
| `run_async(output_names, input_feed, callback, user_data, run_options=None)` | Async execution in separate C++ thread |
| `run_with_ort_values(output_names, input_dict_ort_values, run_options=None)` | Run with OrtValue inputs, return OrtValue outputs |
| `run_with_iobinding(iobinding, run_options=None)` | Execute with pre-bound IO |
| `io_binding()` | Create an IOBinding for zero-copy inference |
| `set_providers(providers, provider_options)` | Re-create session with different providers |
| `get_inputs()` | List of `NodeArg` for model inputs |
| `get_outputs()` | List of `NodeArg` for model outputs |
| `get_overridable_initializers()` | Initializers that can be overridden at runtime |
| `get_modelmeta()` | `ModelMetadata` with producer_name, version, etc. |
| `get_providers()` | Active execution providers after partitioning |
| `get_provider_graph_assignment_info()` | Subgraph-to-EP assignment (requires config) |
| `end_profiling()` | Write profiling results to file |
| `get_profiling_start_time_ns()` | Nanosecond timestamp when profiling started |
| `set_ep_dynamic_options(options: dict[str, str])` | Set runtime EP options |
| `get_tuning_results()` / `set_tuning_results(results)` | EP auto-tuning results |

### Fallback Behavior

By default, if an EP fails during `run()`, ORT falls back to CPU (or CUDA if GPU was intended). Disable with `session.disable_fallback()`.

## SessionOptions

Configure session-level behavior.

### Properties

| Property | Type | Description |
|---|---|---|
| `inter_op_num_threads` | int | Threads for parallel execution of independent ops (default: auto) |
| `intra_op_num_threads` | int | Threads within a single op (default: auto) |
| `execution_mode` | `ExecutionMode` | `ORT_SEQUENTIAL` or `ORT_PARALLEL` |
| `optimization_level` | `GraphOptimizationLevel` | `ORT_DISABLE_ALL`, `ORT_ENABLE_BASIC`, `ORT_ENABLE_EXTENDED`, `ORT_ENABLE_ALL` |
| `enable_profiling` | bool | Enable timing profiling |
| `profiling_file_start_time` | int | Start time for profiling (ns) |
| `optimized_model_path` | str | Save optimized model after loading |
| `log_severity_level` | int | 0=VERBOSE, 1=INFO, 2=WARNING (default), 3=ERROR, 4=FATAL |
| `execution_order` | `ExecutionOrder` | `ORT_EXECUTION_ORDER_TOPOLOGICAL` or `ORT_EXECUTION_ORDER_BREADTH_FIRST` |
| `has_providers()` | bool | Check if providers configured via SessionOptions |

### Key Methods

```python
# Add configuration entries
opts.add_session_config_entry("session.disable_prepacking", "0")
opts.add_session_config_entry("session.graph_optimizations_loop_level", "1")

# Add registered operators
opts.register_ep_context()

# Add custom libraries
opts.register_ep_library("libcustom_ops.so")

# Provider configuration
opts.add_provider("CUDAExecutionProvider", {"device_id": "0"})
opts.set_provider_selection_policy(ort.OrtExecutionProviderDevicePolicy.PREFER_NPU)
```

## RunOptions

Per-run configuration.

```python
run_options = ort.RunOptions()
run_options.log_severity_level = 0
run_options.log_verbosity_level = 0
run_options.run_tag = "my_run"
run_options.terminate = False
```

## OrtValue

Zero-copy tensor container that can reside on any device.

### Creation

```python
# From numpy (zero-copy on CPU, copy on GPU)
ortvalue = ort.OrtValue.ortvalue_from_numpy(
    np_array, device_type="cuda", device_id=0
)

# From numpy with ONNX element type (e.g., BFLOAT16)
ortvalue = ort.OrtValue.ortvalue_from_numpy_with_onnx_type(
    np_array, onnx.TensorProto.BFLOAT16
)

# Pre-allocate with shape and type
ortvalue = ort.OrtValue.ortvalue_from_shape_and_type(
    shape=[1, 3, 224, 224],
    element_type=np.float32,
    device_type="cuda",
    device_id=0,
)

# With memory_info for zero-copy allocator selection
ortvalue = ort.OrtValue.ortvalue_from_shape_and_type(
    shape=[1, 3, 224, 224],
    element_type=np.float32,
    memory_info=ep_device.memory_info(ort.OrtDeviceMemoryType.HOST_ACCESSIBLE),
)

# From DLPack (PyTorch, JAX, numpy)
ortvalue = ort.OrtValue.from_dlpack(torch_tensor)

# From SparseTensor
ortvalue = ort.OrtValue.ort_value_from_sparse_tensor(sparse_tensor)
```

### Accessors

| Method | Returns | Description |
|---|---|---|
| `numpy()` | `np.ndarray` | Convert to numpy (copies from GPU) |
| `data_ptr()` | int | Raw pointer to data buffer |
| `device_name()` | str | Device name: `cpu`, `cuda`, `cann` |
| `shape()` | `Sequence[int]` | Tensor shape |
| `data_type()` | str | Type string, e.g. `tensor(float)` |
| `element_type()` | int | ONNX TensorProto DataType enum |
| `tensor_size_in_bytes()` | int | Total data size in bytes |
| `has_value()` | bool | True for optional types with data |
| `is_tensor()` | bool | True if contains a tensor |
| `is_sparse_tensor()` | bool | True if contains sparse tensor |
| `is_tensor_sequence()` | bool | True if contains tensor sequence |
| `update_inplace(data)` | None | Update data in-place (for CUDA graphs) |

### DLPack Protocol

OrtValue implements `__dlpack__`, `__dlpack_device__`, and `from_dlpack()` for zero-copy exchange with PyTorch, JAX, and NumPy.

```python
# OrtValue -> PyTorch
torch_tensor = torch.from_dlpack(ortvalue)

# PyTorch -> OrtValue
ortvalue = ort.OrtValue.from_dlpack(torch_tensor)
```

## IOBinding

Bind inputs/outputs to specific devices, avoiding CPU copies.

```python
binding = session.io_binding()

# Bind CPU numpy input (zero-copy)
binding.bind_cpu_input("input_name", np_array)

# Bind GPU input
binding.bind_input("input_name", "cuda", 0, np.float32, [1, 3, 224, 224], gpu_ptr)

# Bind OrtValue input
binding.bind_ortvalue_input("input_name", ortvalue)

# Bind output to GPU (ORT allocates)
binding.bind_output("output_name", device_type="cuda", device_id=0)

# Bind output with pre-allocated buffer
binding.bind_output("output_name", "cuda", 0, np.float32, [1, 1000], gpu_output_ptr)

# Synchronize inputs/outputs
binding.synchronize_inputs()
session.run_with_iobinding(binding)
binding.synchronize_outputs()

# Get outputs
outputs = binding.get_outputs()  # list of OrtValue
cpu_outputs = binding.copy_outputs_to_cpu()  # list of numpy arrays
```

## ModelCompiler

Ahead-of-time compilation to EPContext format.

```python
sess_options = ort.SessionOptions()
sess_options.add_provider("CUDAExecutionProvider", {"device_id": "0"})

compiler = ort.ModelCompiler(
    sess_options,
    "input_model.onnx",
    embed_compiled_data_into_model=False,
    external_initializers_file_path=None,
    external_initializers_size_threshold=1024,
    flags=ort.OrtCompileApiFlags.NONE,
    graph_optimization_level=ort.GraphOptimizationLevel.ORT_DISABLE_ALL,
)

# Compile to file
compiler.compile_to_file("output_model.onnx")

# Compile to bytes
compiled_bytes = compiler.compile_to_bytes()

# Compile to stream
compiler.compile_to_stream(lambda data: file.write(data))
```

## SparseTensor

Handle sparse model inputs/outputs.

```python
# COO format
sparse = ort.SparseTensor.sparse_coo_from_numpy(
    dense_shape=np.array([100, 100], dtype=np.int64),
    values=np.array([1.0, 2.0, 3.0], dtype=np.float32),
    coo_indices=np.array([[0, 50], [50, 0], [99, 99]], dtype=np.int64),
    ort_device=ort.OrtDevice.make("cpu", 0),
)

# CSR format
sparse = ort.SparseTensor.sparse_csr_from_numpy(
    dense_shape=np.array([100, 100], dtype=np.int64),
    values=np.array([1.0, 2.0], dtype=np.float32),
    inner_indices=np.array([0, 2], dtype=np.int64),
    outer_indices=np.array([0, 1], dtype=np.int64),
    ort_device=ort.OrtDevice.make("cpu", 0),
)
```

## OrtDevice

```python
device = ort.OrtDevice.make("cuda", 0)
device = ort.OrtDevice.make("gpu", 0, vendor_id=ort.OrtDeviceVendorId.NVIDIA)

device.device_id()       # 0
device.device_type()     # Ort memory device type enum
device.device_vendor_id()  # PCI vendor ID
device.device_mem_type()   # Memory type
```

## LoraAdapter

```python
adapter = ort.LoraAdapter("adapter.onnx")
```

## AdapterFormat

Read/write LoRA adapter files.

```python
# Read
adapter = ort.AdapterFormat.read_adapter("adapter.onnx")
params = adapter.get_parameters()  # dict[str, OrtValue] (zero-copy views)

# Write
adapter = ort.AdapterFormat()
adapter.set_adapter_version(1)
adapter.set_model_version(1)
adapter.set_parameters({"weight": ortvalue})
adapter.export_adapter("output_adapter.onnx")
```

## copy_tensors

Copy between OrtValues (supports GPU-to-GPU).

```python
ort.copy_tensors([src_ortvalue], [dst_ortvalue], stream=None)
```

## Global Functions

```python
ort.get_available_providers()          # List of available EPs
ort.get_all_providers()               # All compiled-in EPs
ort.get_build_info()                  # Build configuration dict
ort.get_device()                      # Current device info
ort.get_ep_devices()                  # EP device info
ort.get_version_string()              # ORT version string
ort.has_collective_ops()              # True if collective ops enabled

ort.set_default_logger_severity(2)    # 0-4
ort.set_seed(42)                      # Reproducibility

ort.disable_telemetry_events()
ort.enable_telemetry_events()

ort.set_global_thread_pool_sizes(intra=4, inter=2)

ort.register_execution_provider_library("lib.so")
ort.unregister_execution_provider_library("lib.so")

ort.create_and_register_allocator(memory_info, arena_config)
ort.create_and_register_allocator_v2(memory_info, arena_config, name)
```
