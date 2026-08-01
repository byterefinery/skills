---
name: onnxruntime-1-28-0
description: Use ONNX Runtime 1.28.0 for high-performance inference of ONNX models across CPU, GPU, NPU, and other accelerators. Covers Python/C/C++ APIs, InferenceSession, Execution Providers (CUDA, TensorRT, OpenVINO, CoreML, DML, DirectML, WebGPU, CANN, MIGraphX, QNN, SNPE, ACL, XNNPACK, NNAPI, WebNN, VitisAI, RKNPU, Azure, VSINPU), SessionOptions tuning, IOBinding/OrtValue zero-copy patterns, ModelCompiler (EPContext), LoRA adapters, quantization, graph optimizations, profiling, building from source, and minimal/reduced builds. Use when the user asks about ONNX Runtime inference, model optimization, execution provider selection, zero-copy inference, cross-platform deployment, or building ONNX Runtime.
license: MIT
metadata:
  tags:
    - ai-ml
    - inference
    - onnx
    - deep-learning
    - acceleration
    - quantization
    - lora
---

# onnxruntime 1.28.0

## Overview

**ONNX Runtime 1.28.0** is a cross-platform inference and training ML accelerator. It executes ONNX models with optimal performance via hardware accelerators, graph optimizations, and memory-efficient execution patterns.

Key capabilities:
- **Multi-EP support** — CPU, CUDA, TensorRT, OpenVINO, CoreML, DirectML, WebGPU, CANN, MIGraphX, QNN, SNPE, ACL, XNNPACK, NNAPI, WebNN, VitisAI, RKNPU, Azure, VSINPU
- **Python/C/C++/C#/Java/Node.js/Objective-C APIs** — full language coverage
- **Zero-copy inference** — IOBinding and OrtValue for GPU-resident data
- **ModelCompiler** — ahead-of-time compilation to EPContext format
- **LoRA adapters** — native support for loading LoRA fine-tuned parameters at inference time
- **Quantization** — QDQ fusion, INT8/FP8/FP4, dynamic and static quantization
- **Graph optimizations** — constant folding, node fusion, memory optimization, operator reduction
- **ORT format** — optimized model format with faster loading and memory mapping
- **Minimal builds** — reduced binary size for edge/on-device

## Usage

### Installation

```bash
# CPU-only
pip install onnxruntime==1.28.0

# CUDA (match your CUDA version)
pip install onnxruntime-gpu==1.28.0
```

### Basic Inference (Python)

```python
import onnxruntime as ort
import numpy as np

# Create session with preferred execution providers
session = ort.InferenceSession(
    "model.onnx",
    providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
)

# Inspect model I/O
print("Inputs:", [(i.name, i.shape, i.type) for i in session.get_inputs()])
print("Outputs:", [(o.name, o.shape, o.type) for o in session.get_outputs()])

# Run inference
inputs = {session.get_inputs()[0].name: np.random.randn(1, 3, 224, 224).astype(np.float32)}
outputs = session.run(None, inputs)
```

### Session Options Tuning

```python
import onnxruntime as ort

opts = ort.SessionOptions()
opts.inter_op_num_threads = 2       # parallelism across independent ops
opts.intra_op_num_threads = 4       # threads within a single op
opts.execution_mode = ort.ExecutionMode.ORT_PARALLEL
opts.optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
opts.enable_profiling = True
opts.add_session_config_entry("session.disable_prepacking", "0")

session = ort.InferenceSession("model.onnx", sess_options=opts)
# ... run inference ...
session.end_profiling()  # writes profile to file
```

### Zero-Copy GPU Inference with IOBinding

```python
import onnxruntime as ort
import numpy as np

session = ort.InferenceSession("model.onnx", providers=["CUDAExecutionProvider"])

binding = session.io_binding()

# Bind input on GPU (no CPU copy)
input_ortvalue = ort.OrtValue.ortvalue_from_numpy(
    input_data, device_type="cuda", device_id=0
)
binding.bind_ortvalue_input("input", input_ortvalue)

# Bind output to GPU
binding.bind_output("output", device_type="cuda", device_id=0)

# Execute
session.run_with_iobinding(binding)

# Retrieve output
output = binding.get_outputs()[0]
output_np = output.numpy()  # copies from GPU to CPU
```

### Loading LoRA Adapters

```python
import onnxruntime as ort

opts = ort.SessionOptions()
session = ort.InferenceSession("base_model.onnx", sess_options=opts, providers=["CPUExecutionProvider"])

# Load LoRA adapter
adapter = ort.LoraAdapter("lora_adapter.onnx")
session.add_session_config_entry("session.load_model_format", "ONNX")

# Run with adapter applied
outputs = session.run(None, inputs, run_options=None)
```

### ModelCompiler — Ahead-of-Time Compilation

```python
import onnxruntime as ort

sess_options = ort.SessionOptions()
sess_options.add_provider("CUDAExecutionProvider", {"device_id": "0"})

compiler = ort.ModelCompiler(sess_options, "input_model.onnx")
compiler.compile_to_file("output_model.onnx")  # EPContext model
```

## Gotchas

- **Provider order is precedence** — `["CUDAExecutionProvider", "CPUExecutionProvider"]` means CUDA first, CPU fallback. If a provider is listed but not available, ORT skips it silently unless `session.log_severity_level` is verbose.
- **`InferenceSession` is not thread-safe** — create one session per thread or use explicit synchronization. Multiple threads can call `session.run()` concurrently only if the session was created with `execution_mode = ORT_SEQUENTIAL`.
- **GPU memory leaks** — when using `OrtValue` with CPU numpy arrays, keep the numpy reference alive for the duration of any IOBinding or session run that uses it. ORT holds a zero-copy view, not a copy.
- **`providers` in `InferenceSession()` override `SessionOptions` providers** — if both are set, `InferenceSession` providers take precedence with a warning.
- **CUDA version mismatch** — `onnxruntime-gpu` wheels are built against specific CUDA versions. A CUDA 12.x wheel will warn if PyTorch uses CUDA 11.x. Match versions or install compatible wheels.
- **ORT format models** — `.ort` files load faster and support memory mapping (`session.use_memory_mapped_ort_model = "1"`), but the model file must remain accessible and immutable during session lifetime.
- **Quantized models** — ORT fuses QDQ (QuantizeLinear/DequantizeLinear) pairs by default. Set `session.disable_quant_qdq = "1"` to disable fusion (needed for some EPs like DirectML).
- **Minimal builds** — `--minimal_build` disables RTTI and limits operator support. Use `--include_ops_by_config` to specify exactly which operators are needed.
- **`session.run()` returns list in output order** — not dict. Use named `output_names` parameter to control order, or iterate with `session.get_outputs()`.
- **DLPack interoperability** — `OrtValue` supports `__dlpack__`/`from_dlpack` for zero-copy exchange with PyTorch, JAX, and NumPy. Bool tensors encoded as uint8 by older DLPack versions are not distinguishable from true uint8.
- **TensorRT and TensorRT RTX are mutually exclusive** — cannot enable both `TensorrtExecutionProvider` and `NvTensorRTRTXExecutionProvider` in the same session.
- **`--use_openmp` vs ORT threadpool** — OpenMP controls intra-op parallelism; ORT threadpool always handles inter-op. For single-threaded execution, set both `OMP_NUM_THREADS=1` and `intra_op_num_threads=1`.

## References

- [01-python-api](references/01-python-api.md) — Python API reference: InferenceSession, SessionOptions, RunOptions, OrtValue, IOBinding, ModelCompiler, SparseTensor
- [02-execution-providers](references/02-execution-providers.md) — Execution providers: CUDA, TensorRT, OpenVINO, CoreML, DirectML, WebGPU, CANN, MIGraphX, QNN, and more
- [03-build-from-source](references/03-build-from-source.md) — Building from source: CMake, build.sh/build.py, platform targets, minimal builds, size reduction
- [04-session-options](references/04-session-options.md) — Session options, config keys, graph optimizations, threading, memory tuning
- [05-advanced-features](references/05-advanced-features.md) — LoRA adapters, quantization, EPContext/ModelCompiler, custom ops, profiling, ORT format
