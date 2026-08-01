# Inference Engines — RapidOCR 3.9.2

RapidOCR supports six inference backends. Each stage (det, cls, rec) can use a different engine. Default is ONNX Runtime.

## ONNX Runtime (Default)

```python
from rapidocr import EngineType, RapidOCR

engine = RapidOCR(params={
    "Det.engine_type": EngineType.ONNXRUNTIME,
    "Cls.engine_type": EngineType.ONNXRUNTIME,
    "Rec.engine_type": EngineType.ONNXRUNTIME,
})
```

**Package:** `pip install onnxruntime` (CPU) or `pip install onnxruntime-gpu` (CUDA)

**Device support:** CPU, CUDA, DML (DirectML), CoreML, CANN (Ascend NPU)

### CPU Configuration

```yaml
EngineConfig:
  onnxruntime:
    intra_op_num_threads: -1     # -1 = auto (CPU count)
    inter_op_num_threads: -1
    enable_cpu_mem_arena: false
    cpu_ep_cfg:
      arena_extend_strategy: "kSameAsRequested"
```

### CUDA Configuration

```yaml
EngineConfig:
  onnxruntime:
    use_cuda: true
    cuda_ep_cfg:
      device_id: 0
      arena_extend_strategy: "kNextPowerOfTwo"
      cudnn_conv_algo_search: "EXHAUSTIVE"
      do_copy_in_default_stream: true
```

### DirectML (Windows GPU)

```yaml
EngineConfig:
  onnxruntime:
    use_dml: true
    dml_ep_cfg: null
```

### CoreML (macOS)

```yaml
EngineConfig:
  onnxruntime:
    use_coreml: true
    coreml_ep_cfg:
      ModelFormat: "MLProgram"
      MLComputeUnits: "ALL"
      RequireStaticInputShapes: 0
      EnableOnSubgraphs: 0
      SpecializationStrategy: "FastPrediction"
      ProfileComputePlan: 0
      AllowLowPrecisionAccumulationOnGPU: 0
      ModelCacheDirectory: "/tmp/RapidOCR"
```

### CANN (Ascend NPU)

```yaml
EngineConfig:
  onnxruntime:
    use_cann: true
    cann_ep_cfg:
      device_id: 0
      arena_extend_strategy: "kNextPowerOfTwo"
      npu_mem_limit: 21474836480
      op_select_impl_mode: "high_performance"
      optypelist_for_implmode: "Gelu"
      enable_cann_graph: true
```

**Key behavior:** ONNX models embed character dictionaries in metadata, so no separate dict file download is needed. Models auto-download from ModelScope on first use with SHA256 verification.

## TensorRT

```python
engine = RapidOCR(params={
    "Det.engine_type": EngineType.TENSORRT,
    "Cls.engine_type": EngineType.TENSORRT,
    "Rec.engine_type": EngineType.TENSORRT,
})
```

**Package:** `pip install tensorrt` (requires NVIDIA GPU + CUDA toolkit)

### Configuration

```yaml
EngineConfig:
  tensorrt:
    device_id: 0
    use_fp16: true
    use_int8: false
    workspace_size: 1073741824  # 1GB

    cache_dir: null       # null = use default models dir
    force_rebuild: false

    det_profile:
      min_shape: [1, 3, 32, 32]
      opt_shape: [1, 3, 736, 736]
      max_shape: [1, 3, 2048, 2048]

    rec_profile:
      min_shape: [1, 3, 48, 32]
      opt_shape: [6, 3, 48, 320]
      max_shape: [6, 3, 48, 2048]

    cls_profile:
      min_shape: [1, 3, 48, 32]
      opt_shape: [6, 3, 48, 192]
      max_shape: [6, 3, 48, 192]
```

**Key behavior:** On first use, TensorRT builds engines from ONNX models using the dynamic shape profiles. Built engines are cached to disk. Subsequent runs load cached engines directly. Set `force_rebuild: true` to force rebuild.

## OpenVINO

```python
engine = RapidOCR(params={
    "Det.engine_type": EngineType.OPENVINO,
    "Cls.engine_type": EngineType.OPENVINO,
    "Rec.engine_type": EngineType.OPENVINO,
})
```

**Package:** `pip install openvino`

**Device support:** CPU, GPU (Intel), VPU (Myriad), NPU (Intel Core), OpenVINO GPU

### Configuration

```yaml
EngineConfig:
  openvino:
    inference_num_threads: -1
    performance_hint: null
    performance_num_requests: -1
    enable_cpu_pinning: null
    num_streams: -1
    enable_hyper_threading: null
    scheduling_core_type: null
```

## PaddlePaddle

```python
engine = RapidOCR(params={
    "Det.engine_type": EngineType.PADDLE,
    "Cls.engine_type": EngineType.PADDLE,
    "Rec.engine_type": EngineType.PADDLE,
})
```

**Package:** `pip install paddlepaddle` (CPU) or `pip install paddlepaddle-gpu` (CUDA)

### Configuration

```yaml
EngineConfig:
  paddle:
    cpu_math_library_num_threads: -1

    use_cuda: false
    cuda_ep_cfg:
      device_id: 0
      gpu_mem: 500

    use_npu: false
    npu_ep_cfg:
      device_id: 0
      envs:
        FLAGS_npu_jit_compile: 0
        FLAGS_use_stride_kernel: 0
        FLAGS_allocator_strategy: "auto_growth"
```

**Key behavior:** PaddlePaddle uses its own model format (not ONNX). Models are downloaded as bundles (multiple files per model) rather than single files. Character dictionaries are separate files.

## PyTorch

```python
engine = RapidOCR(params={
    "Det.engine_type": EngineType.TORCH,
    "Cls.engine_type": EngineType.TORCH,
    "Rec.engine_type": EngineType.TORCH,
})
```

**Package:** `pip install torch`

### Configuration

```yaml
EngineConfig:
  torch:
    use_cuda: false
    cuda_ep_cfg:
      device_id: 0

    use_npu: false
    npu_ep_cfg:
      device_id: 0

    use_mps: false    # Apple Metal
```

**Key behavior:** Uses PyTorch network definitions from `inference_engine/pytorch/networks/`. Supports backbones: MobileNetV3, HGNet, LCNetV3/V4, PPLCNet, PPHGNetV2, SVTRNet, DONUT-Swin. Heads: DB (detection), CTC (recognition), classification head. Transforms: TPS, TBSRN, TSRN, STN.

## MNN

```python
engine = RapidOCR(params={
    "Det.engine_type": EngineType.MNN,
    "Cls.engine_type": EngineType.MNN,
    "Rec.engine_type": EngineType.MNN,
})
```

**Package:** `pip install MNN`

**Configuration:** No engine-specific config needed (empty `mnn: {}` section).

## Engine Selection Guide

| Use case | Recommended engine |
|---|---|
| General CPU inference | ONNX Runtime |
| NVIDIA GPU (max speed) | TensorRT > ONNX Runtime CUDA |
| Intel CPU/GPU | OpenVINO |
| Apple Silicon (MPS) | PyTorch (use_mps) or ONNX Runtime CoreML |
| Windows GPU (non-NVIDIA) | ONNX Runtime DML |
| Ascend NPU | ONNX Runtime CANN or PaddlePaddle NPU |
| Mobile (Android/iOS) | MNN |
| Development/debugging | PyTorch |

## Custom Session

ONNX Runtime supports passing a pre-built `InferenceSession`:

```python
from onnxruntime import InferenceSession

custom_session = InferenceSession("my_model.onnx")
engine = RapidOCR(params={
    "Det.engine_type": EngineType.ONNXRUNTIME,
    "Det.session": custom_session,
})
```
