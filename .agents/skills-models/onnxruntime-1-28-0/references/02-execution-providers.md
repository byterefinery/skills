# Execution Providers — ONNX Runtime 1.28.0

## Overview

Execution Providers (EPs) are hardware-specific backends that ORT uses to execute model operations. Multiple EPs can be registered with a precedence order — ORT falls through the list when an operator is not supported by a higher-priority EP.

## Provider Selection

```python
# Simple list (precedence order)
session = ort.InferenceSession(
    "model.onnx",
    providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
)

# With options
session = ort.InferenceSession(
    "model.onnx",
    providers=[
        ("CUDAExecutionProvider", {"device_id": "0", "arena_extend_strategy": "kSameAsRequested"}),
        "CPUExecutionProvider",
    ],
)

# Via SessionOptions
opts = ort.SessionOptions()
opts.add_provider("CUDAExecutionProvider", {"device_id": "0"})
```

## CPU Execution Provider

Always available. Supports SIMD (SSE4.2, AVX2, AVX512, NEON, SVE, RVV).

### Build Flags

```bash
--use_dnnl           # Enable DNNL (oneDNN) for optimized CPU ops
--use_xnnpack        # Enable XNNPACK for mobile/embedded CPU
--enable_arm_neon_nchwc  # NCHWc ARM kernels (higher thread counts)
--enable_rvv         # RISC-V Vector extension
--no_sve             # Disable SVE (ARM)
```

### Key Options

| Option | Description |
|---|---|
| `arena_extend_strategy` | `kSameAsRequested`, `kNextPowerOfTwo`, `kLARGE_ALLOC_ARENA` |
| `cudnn_conv_algo_search` | N/A for CPU |
| `gpu_mem_limit` | N/A for CPU |

## CUDA Execution Provider

NVIDIA GPU acceleration via CUDA/cuDNN.

### Build Flags

```bash
--use_cuda
--cuda_version 12.4
--cuda_home /usr/local/cuda
--cudnn_home /usr/local/cuda
--enable_nvtx_profile       # NVTX markers for profiling
--enable_cuda_profiling     # CUPTI kernel profiling
--enable_cuda_minimal_build # Reduced CUDA build
--nvcc_threads 4            # Parallel NVCC compilation
```

### Key Options

| Option | Values | Description |
|---|---|---|
| `device_id` | `"0"`, `"1"`, ... | GPU device index |
| `arena_extend_strategy` | `kSameAsRequested`, `kNextPowerOfTwo` | Memory arena growth |
| `cudnn_conv_algo_search` | `EXHAUSTIVE`, `HEURISTIC`, `DEFAULT` | cuDNN convolution algo search |
| `gpu_mem_limit` | bytes | GPU memory limit |
| `cudnn_conv_use_max_workspace` | `"1"`, `"0"` | Allow max workspace for cuDNN |
| `do_copy_in_default_stream` | `"1"`, `"0"` | Copy on default stream |
| `user_compute_stream` | stream ptr | Use existing CUDA stream |
| `enable_cuda_graph` | `"1"`, `"0"` | Enable CUDA graph capture |
| `enable_tensor_cores` | `"1"`, `"0"` | Use Tensor Cores |
| `conv_algo_search` | `EXHAUSTIVE`, `HEURISTIC`, `DEFAULT`, `DISABLED` | Convolution algo search |

### CUDA Graph

```python
opts = ort.SessionOptions()
opts.add_session_config_entry("ep.cuda.enable_cuda_graph", "1")
session = ort.InferenceSession("model.onnx", sess_options=opts, providers=["CUDAExecutionProvider"])
```

## TensorRT Execution Provider

NVIDIA TensorRT for optimized inference on GPUs.

### Build Flags

```bash
--use_tensorrt
--tensorrt_home /usr
--use_tensorrt_oss_parser   # Use OSS parser instead of built-in
```

### Key Options

| Option | Values | Description |
|---|---|---|
| `device_id` | `"0"`, ... | GPU device |
| `trt_max_workspace_size` | bytes | Max TensorRT workspace |
| `trt_builder_optimization_level` | int | Optimization level (-1 to 9) |
| `trt_sparsity` | `"1"`, `"0"` | Enable sparsity |
| `trt_int8_enable` | `"1"`, `"0"` | Enable INT8 |
| `trt_fp16_enable` | `"1"`, `"0"` | Enable FP16 |
| `trt_engine_cache_enable` | `"1"`, `"0"` | Enable engine caching |
| `trt_engine_cache_path` | path | Engine cache directory |
| `trt_engine_decryption_enable` | `"1"`, `"0"` | Enable engine decryption |
| `trt_max_partition_iterations` | int | Max partitioning iterations |
| `trt_tactic_sources` | int | Tactic source bitmask |

### Gotchas

- TensorRT and TensorRT RTX are mutually exclusive in the same session
- TensorRT falls back to CUDA if both are in the provider list
- Engine caching requires write access to the cache path

## NvTensorRTRTX Execution Provider

TensorRT RTX variant for RTX-specific features.

```bash
--use_nv_tensorrt_rtx
--tensorrt_rtx_home /path/to/trt-rtx
```

## OpenVINO Execution Provider

Intel CPU/iGPU/NPU acceleration via OpenVINO.

### Build Flags

```bash
--use_openvin CPU           # CPU device
--use_openvin GPU           # iGPU device
--use_openvin NPU           # NPU device
--use_openvin HETERO:GPU,CPU  # Heterogeneous
--use_openvin MULTI:GPU,CPU   # Multi-device
--use_openvin AUTO:GPU,CPU    # Auto-selection
```

### Key Options

| Option | Values | Description |
|---|---|---|
| `device_id` | `"0"`, ... | Device index |
| `cache_dir` | path | Model cache directory |
| `enable_openvino_ep_slicing` | `"1"`, `"0"` | Enable graph slicing |
| `openvino_threading_model` | `WORKERS`, `INTRA_OWN` | Threading model |

## CoreML Execution Provider

Apple Silicon/Intel Mac acceleration.

### Build Flags

```bash
--use_coreml
```

### Key Options

| Option | Values | Description |
|---|---|---|
| `enable_on_subgraph` | `"1"`, `"0"` | Run on subgraph (fallback to CPU) |
| `only_run_on_condensed_graph` | `"1"`, `"0"` | Run only fully-supported models |
| `hide_metadata` | `"1"`, `"0"` | Hide CoreML metadata |

## DirectML Execution Provider

Windows GPU acceleration via Direct3D 12.

### Build Flags

```bash
--use_dml
--dml_path /path/to/dml/sdk
--dml_external_project
```

### Key Options

| Option | Values | Description |
|---|---|---|
| `device_id` | `"0"`, ... | GPU device |
| `enable_tensor_storage_float16_cb` | `"1"`, `"0"` | FP16 tensor storage |
| `enable_dml_memory_arena` | `"1"`, `"0"` | Enable memory arena |

## WebGPU Execution Provider

Web GPU via Dawn (web and desktop).

### Build Flags

```bash
--use_webgpu static_lib     # Static linkage (default)
--use_webgpu shared_lib     # Dynamic linkage
--use_external_dawn          # External Dawn dependency
```

## CANN Execution Provider

Huawei Ascend NPU acceleration.

### Build Flags

```bash
--use_cann
--cann_home /path/to/cann
```

### Key Options

| Option | Values | Description |
|---|---|---|
| `device_id` | `"0"`, ... | Ascend device |
| `enable_tiling` | `"1"`, `"0"` | Enable tiling |
| `enable_shape_sync` | `"1"`, `"0"` | Enable shape sync |
| `dump_intermediate_tensor` | `"1"`, `"0"` | Dump tensors for debugging |

## MIGraphX Execution Provider

AMD GPU acceleration via ROCm/MIGraphX.

### Build Flags

```bash
--use_migraphx
--migraphx_home /opt/rocm
```

## QNN Execution Provider

Qualcomm NPU acceleration.

### Build Flags

```bash
--use_qnn shared_lib        # Dynamic (default)
--use_qnn static_lib        # Static
--qnn_home /path/to/qnn/sdk
```

## SNPE Execution Provider

Qualcomm SNPE (legacy).

```bash
--use_snpe
--snpe_root /path/to/snpe
```

## ACL Execution Provider

ARM Compute Library for ARM CPUs/NPUs.

### Build Flags

```bash
--use_acl
--acl_home /path/to/acl
--acl_libs /path/to/acl/libs
--no_kleidiai               # Disable KleidiAI
```

## XNNPACK Execution Provider

XNNPACK for mobile/embedded CPU.

```bash
--use_xnnpack
```

## NNAPI Execution Provider

Android Neural Networks API.

### Build Flags

```bash
--use_nnapi
--nnapi_min_api 27
```

## WebNN Execution Provider

Web Neural Network API (browser).

```bash
--use_webnn
```

## Vitis-AI Execution Provider

Xilinx FPGA/ACAP acceleration.

```bash
--use_vitisai
```

## RKNPU Execution Provider

Rockchip NPU.

```bash
--use_rknpu
```

## VSINPU Execution Provider

VeriSilicon NPU.

```bash
--use_vsinpu
```

## Azure Execution Provider

Azure cloud inference.

```bash
--use_azure
```

## JSEP (JavaScript Execution Provider)

JavaScript backend for WebAssembly.

```bash
--use_jsep
```

## QMX Kernel Library

Qualcomm QMX kernels alongside Arm KleidiAI.

```bash
--use_qmx
```

## Plugin EPs

Plugin EPs are loaded at runtime as shared libraries.

```python
ort.register_execution_provider_library("libplugin_ep.so")
```

### Available Plugin EPs

- **QNN Plugin EP** — [onnxruntime/onnxruntime-qnn](https://github.com/onnxruntime/onnxruntime-qnn)

## Checking Available Providers

```python
import onnxruntime as ort

print(ort.get_available_providers())   # EPs available in current build
print(ort.get_all_providers())         # All compiled-in EPs
print(session.get_providers())         # EPs actually used after partitioning
```

## EP Auto-Tuning

```python
# Get tuning results
results = session.get_tuning_results()

# Apply tuning results
session.set_tuning_results(results)
session.set_tuning_results(results, error_on_invalid=True)
```

## EP Dynamic Options

```python
session.set_ep_dynamic_options({
    "ep.cuda.enable_cuda_graph": "1",
    "ep.cuda.conv_algo_search": "HEURISTIC",
})
```
