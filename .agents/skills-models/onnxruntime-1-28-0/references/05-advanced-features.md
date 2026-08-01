# Advanced Features — ONNX Runtime 1.28.0

## LoRA Adapters

ONNX Runtime supports loading LoRA (Low-Rank Adaptation) fine-tuned parameters at inference time without modifying the base model.

### Loading Adapters

```python
import onnxruntime as ort

session = ort.InferenceSession("base_model.onnx", providers=["CPUExecutionProvider"])

# Load adapter from file
adapter = ort.LoraAdapter("lora_adapter.onnx")

# Run inference with adapter
# Adapter is applied via session configuration
```

### AdapterFormat — Read/Write

```python
# Read adapter
adapter = ort.AdapterFormat.read_adapter("adapter.onnx")
print(adapter.get_format_version())
print(adapter.get_adapter_version())
print(adapter.get_model_version())

# Get parameters (zero-copy views)
params = adapter.get_parameters()  # dict[str, OrtValue]

# Create and write adapter
adapter = ort.AdapterFormat()
adapter.set_adapter_version(1)
adapter.set_model_version(1)
adapter.set_parameters({
    "q_proj.lora_A": ortvalue_a,
    "q_proj.lora_B": ortvalue_b,
})
adapter.export_adapter("output_adapter.onnx")
```

### Adapter Format Details

- Single-source architecture: `parameters` dict is the authoritative source
- Read path: OrtValues are zero-copy views backed by `LoraAdapter` buffer
- Memory ownership via `py::capsule` pinned as patient on each OrtValue

## Quantization

### Supported Formats

- **INT8** — symmetric and asymmetric quantization
- **FP8** — E4M3 and E5M2 formats
- **FP4** — via contrib operators (MatMulBnb4, MatMulFpQ4, MatMulNBits)

### QDQ Fusion

ORT automatically fuses QuantizeLinear → (ops) → DequantizeLinear patterns into quantized operators.

```python
# Disable QDQ fusion (needed for some EPs)
opts = ort.SessionOptions()
opts.add_session_config_entry("session.disable_quant_qdq", "1")
```

### Quantization Config Keys

| Key | Description |
|---|---|
| `session.disable_quant_qdq` | Disable QDQ fusion |
| `session.disable_qdq_constant_folding` | Prevent DequantizeLinear constant folding |
| `session.disable_double_qdq_remover` | Disable Double QDQ removal |
| `session.enable_quant_qdq_cleanup` | Remove QDQ pairs after handling |
| `session.qdqisint8allowed` | Allow INT8 for QDQ on ARM |

### Quantization Utilities (C++)

```cpp
#include "core/quantization/quantization.h"

using namespace onnxruntime::quantization;

// Quantize float buffer to int8
Params<int8_t> params = QuantizeLinear<int8_t>(float_data, int8_output, size);

// Quantize with forced symmetric
Params<int8_t> sym_params = QuantizeLinear<int8_t>(data, output, size, true);

// Dequantize
float dequantized = Dequantize<int8_t>(quant_value, params);
```

## EPContext and ModelCompiler

EPContext enables ahead-of-time compilation of subgraphs to specific execution providers, producing a compiled model with embedded EP-specific execution contexts.

### Compilation

```python
import onnxruntime as ort

sess_options = ort.SessionOptions()
sess_options.add_provider("CUDAExecutionProvider", {"device_id": "0"})

compiler = ort.ModelCompiler(
    sess_options,
    "input_model.onnx",
    embed_compiled_data_into_model=False,  # External initializers
    external_initializers_file_path="init.bin",
    external_initializers_size_threshold=1024,
    flags=ort.OrtCompileApiFlags.NONE,
    graph_optimization_level=ort.GraphOptimizationLevel.ORT_DISABLE_ALL,
)

compiler.compile_to_file("output_model.onnx")
```

### Custom Initializer Location

```python
def get_initializer_location(
    initializer_name: str,
    initializer_value: ort.OrtValue,
    external_info: ort.OrtExternalInitializerInfo | None,
) -> ort.OrtExternalInitializerInfo | None:
    byte_size = initializer_value.tensor_size_in_bytes()

    if byte_size < 64:
        return None  # Store inline

    # Store externally
    file_offset = ext_file.tell()
    ext_file.write(initializer_value.numpy().tobytes())
    return ort.OrtExternalInitializerInfo("init.bin", file_offset, byte_size)

compiler = ort.ModelCompiler(
    sess_options,
    "input_model.onnx",
    get_initializer_location_func=get_initializer_location,
)
```

### Loading Compiled Models

```python
# EPContext model loads like any ONNX model
session = ort.InferenceSession("output_model.onnx", providers=["CUDAExecutionProvider"])
```

## Custom Operators

### Registration

```python
opts = ort.SessionOptions()
opts.register_custom_ops_library("libcustom_ops.so")

session = ort.InferenceSession("model.onnx", sess_options=opts)
```

### Contrib Operators

ORT includes Microsoft contrib operators (`com.microsoft` domain):

- **Transformer ops**: Attention, DecoderAttention, GroupQueryAttention, LinearAttention, LongformerAttention
- **Fused ops**: FusedMatMul, FusedMatMulActivation, FusedConv, FusedGemm, BiasGelu, BiasSoftmax, BiasDropout
- **Quantization**: GatherBlockQuantized, MatMulIntegerToFloat, MatMulInteger16
- **Low-bit**: MatMulBnb4, MatMulFpQ4, MatMulNBits, MatMulNBitsMlp, GemmFloat8
- **Search**: BeamSearch, GreedySearch, Sampling, WhisperBeamSearch
- **Specialized**: DynamicTimeWarping, GridSample, CropAndResize, ComplexMul, GroupNorm

Enable/disable:

```bash
./build.sh --disable_contrib_ops    # Disable all contrib ops
./build.sh --disable_generation_ops  # Disable search/generation ops
```

## CUDA Graph

Capture and replay CUDA kernels for reduced launch overhead.

```python
opts = ort.SessionOptions()
opts.add_session_config_entry("ep.cuda.enable_cuda_graph", "1")

session = ort.InferenceSession("model.onnx", sess_options=opts,
                                providers=["CUDAExecutionProvider"])

# First run captures the graph
outputs = session.run(None, inputs)

# Subsequent runs replay the graph (faster)
outputs = session.run(None, inputs)
```

### Updating Inputs with CUDA Graph

Use `OrtValue.update_inplace()` to update input data without changing memory addresses:

```python
binding = session.io_binding()
input_ortvalue = ort.OrtValue.ortvalue_from_numpy(data, device_type="cuda", device_id=0)
binding.bind_ortvalue_input("input", input_ortvalue)
binding.bind_output("output", device_type="cuda", device_id=0)

# First run (captures graph)
session.run_with_iobinding(binding)

# Update input in place
input_ortvalue.update_inplace(new_data)
session.run_with_iobinding(binding)
```

## Async Inference

```python
def callback(results, user_data, err):
    if err:
        print(f"Error: {err}")
    else:
        user_data.save_results(results)

class MyData:
    def __init__(self):
        self.results = None
    def save_results(self, results):
        self.results = results

user_data = MyData()
session.run_async(None, inputs, callback, user_data)
```

## Profiling

### Session Profiling

```python
opts = ort.SessionOptions()
opts.enable_profiling = True
opts.profiling_file_name = "profile.json"

session = ort.InferenceSession("model.onnx", sess_options=opts)
# ... run inference ...
session.end_profiling()
```

### CUDA Profiling

```bash
# Build with profiling support
./build.sh --use_cuda --enable_nvtx_profile --enable_cuda_profiling

# Run with Nsight Systems or nvprof
nsys profile --stats=true python inference.py
```

## ORT Format

ORT format is an optimized model representation with faster loading.

### Converting

```python
opts = ort.SessionOptions()
opts.optimized_model_path = "model.ort"
opts.add_session_config_entry("session.save_model_format", "ORT")

session = ort.InferenceSession("model.onnx", sess_options=opts)
```

### Loading

```python
# Auto-detected from .ort extension
session = ort.InferenceSession("model.ort")

# Or force format
opts = ort.SessionOptions()
opts.add_session_config_entry("session.load_model_format", "ORT")
```

### Memory-Mapped Loading

```python
opts = ort.SessionOptions()
opts.add_session_config_entry("session.use_memory_mapped_ort_model", "1")
opts.add_session_config_entry("session.use_ort_model_bytes_for_initializers", "1")
```

## Run with OrtValueVector

Minimal overhead execution with pre-allocated OrtValues:

```python
# Pre-allocate input/output OrtValues
input_ov = ort.OrtValue.ortvalue_from_numpy(input_data, device_type="cuda", device_id=0)
output_ov = ort.OrtValue.ortvalue_from_shape_and_type(
    [1, 1000], np.float32, device_type="cuda", device_id=0
)

# Execute with minimal conversion overhead
session.run_with_ortvaluevector(
    run_options,
    ["input"], [input_ov],
    ["output"], [output_ov],
    ["cuda:0"],
)
```

## Copy Tensors

```python
# Copy between OrtValues (supports GPU-to-GPU)
ort.copy_tensors([src_ortvalue], [dst_ortvalue], stream=cuda_stream)
```

## DLPack Interoperability

Zero-copy exchange with PyTorch, JAX, NumPy:

```python
# OrtValue -> PyTorch
torch_tensor = torch.from_dlpack(ortvalue)

# PyTorch -> OrtValue
ortvalue = ort.OrtValue.from_dlpack(torch_tensor)

# OrtValue -> JAX
jax_array = jax.dlpack.from_dlpack(ortvalue)

# OrtValue -> NumPy
np_array = np.from_dlpack(ortvalue)
```

### Bool Tensor Gotcha

DLPack encodes bool as uint8. When the source object exposes `dtype`, ORT auto-detects bool tensors. For raw DLPack capsules, bool is not distinguishable from uint8.

## Multi-Input/Multi-Output

```python
# Get all inputs/outputs
inputs_meta = session.get_inputs()
outputs_meta = session.get_outputs()

# Run with specific inputs
input_feed = {
    "input1": data1,
    "input2": data2,
}

# Get specific outputs by name
outputs = session.run(["output1", "output2"], input_feed)
```

## Overridable Initializers

```python
# Get initializers that can be overridden
overridable = session.get_overridable_initializers()

# Override at runtime
input_feed = {session.get_inputs()[0].name: input_data}
for init in overridable:
    input_feed[init.name] = new_value

outputs = session.run(None, input_feed)
```

## EP Dynamic Options

Set EP options at runtime (after session creation):

```python
session.set_ep_dynamic_options({
    "ep.cuda.enable_cuda_graph": "1",
    "ep.cuda.conv_algo_search": "HEURISTIC",
})
```

## Tuning Results

```python
# Get auto-tuning results
results = session.get_tuning_results()

# Apply tuning results to new sessions
new_session.set_tuning_results(results)
new_session.set_tuning_results(results, error_on_invalid=True)
```

## Memory Info and EP Devices

```python
# Get memory info for inputs/outputs
input_meminfos = session.get_input_memory_infos()
output_meminfos = session.get_output_memory_infos()

# Get EP device info for inputs
input_epdevices = session.get_input_epdevices()

# Get EP device info
ep_devices = ort.get_ep_devices()
```

## Gotchas

- **LoRA adapters** — the adapter file format is ORT-specific; convert from other formats before loading
- **QDQ fusion** — may affect accuracy on some models; test with `session.disable_quant_qdq = "1"`
- **CUDA graph** — requires fixed input shapes; dynamic shapes need separate graph captures
- **EPContext** — compiled models are EP-specific; a CUDA-compiled model won't run on CPU alone
- **Memory-mapped ORT** — the model file must remain accessible and immutable; don't delete or modify it
- **`update_inplace()`** — only works when memory address must stay fixed (CUDA graph, pre-allocated buffers)
- **`run_with_ortvaluevector()`** — fetches must be pre-allocated OrtValues; ORT does not allocate outputs
- **Bool DLPack** — raw PyCapsules cannot distinguish bool from uint8; use objects with `dtype` attribute
- **TensorRT + TensorRT RTX** — mutually exclusive in the same session
