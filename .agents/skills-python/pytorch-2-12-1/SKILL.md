---
name: pytorch-2-12-1
description: >
  PyTorch 2.12.1 — the Python deep learning framework. Use when working with
  tensors, neural networks, autograd, model training, GPU acceleration,
  TorchScript, torch.compile, distributed training (DDP, FSDP), DataLoader,
  or any ML/DL task using PyTorch. Covers torch, torch.nn, torch.optim,
  torch.utils.data, torch.jit, torch.distributed, torch.cuda, and the full
  2.12 API. Trigger on: pytorch, torch, tensor, nn.Module, DataLoader,
  autograd, GPU, CUDA, torch.compile, TorchScript, DDP, FSDP, distributed,
  optimizer, loss, tensor operations, linear algebra, FFT, sparse tensors.
metadata:
  tags:
    - ml
    - deep-learning
    - python
    - gpu
---

# pytorch 2.12.1

## Overview

PyTorch 2.12.1 (May 2026) is the Python deep learning framework providing tensor computation with GPU acceleration and a tape-based autograd system. It is the foundation for most modern ML/DL workloads in Python.

**Core modules:**
- **`torch`** — Tensor class and operations (math, linear algebra, reductions, FFT, random)
- **`torch.nn`** — Neural network layers, losses, containers (Module, Sequential, DataParallel)
- **`torch.nn.functional`** — Functional forms of layers and losses (no state)
- **`torch.optim`** — Optimizers (SGD, Adam, AdamW, Lion, etc.) and lr schedulers
- **`torch.autograd`** — Automatic differentiation engine
- **`torch.utils.data`** — `Dataset`, `DataLoader`, samplers, data loading utilities
- **`torch.jit`** — TorchScript for serialization and optimization
- **`torch.distributed`** — DDP, FSDP, RPC, collective communications
- **`torch.cuda`** — CUDA device management, streams, memory management
- **`torch.compile`** — PyTorch 2.x compilation stack (Inductor backend)

**PyTorch 2.12 specifics:**
- Python >= 3.10, <= 3.14 (3.14t experimental)
- CUDA 12.6, 12.8 (stable), CUDA 13.0 (experimental in 2.11+)
- ROCm 7.2
- C++17
- Triton 3.7.1
- Blackwell GPU support (CUDA 12.8+ architectures 10.0, 12.0)

**Dependencies:** `numpy`, `jinja2`, `fsspec`, `sympy`, `networkx`, `filelock`, `setuptools`. Optional: `triton`, `mkl`, `mkldnn`, `cuda-toolkit`, `nccl`.

## Installation

PyTorch distributes separate wheels per platform and accelerator (CPU, CUDA, ROCm, XPU). Choose the right index for the target environment.

### pip

```bash
# CPU-only (all platforms)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# CUDA 12.6
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# CUDA 12.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# CUDA 13.0
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

# ROCm 7.2 (Linux only)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.2

# XPU / Intel GPU (Linux, Windows)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/xpu
```

**Rule:** `--index-url` replaces the default PyPI index. Without it, pip installs from PyPI which ships CPU-only wheels for Windows/macOS and CUDA wheels for Linux. Use the PyTorch index explicitly for the desired accelerator.

### uv (project mode)

```bash
# Initialize project and add PyTorch
uv init --python 3.12
uv add torch torchvision

# This generates pyproject.toml with torch in dependencies.
# By default, uv resolves from PyPI (CPU on Windows/macOS, CUDA on Linux).
```

For explicit accelerator selection, configure `[[tool.uv.index]]` and `[tool.uv.sources]` in `pyproject.toml`:

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "torch>=2.11.0",
  "torchvision>=0.26.0",
]

# Define PyTorch indexes
[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true

[[tool.uv.index]]
name = "pytorch-cu126"
url = "https://download.pytorch.org/whl/cu126"
explicit = true

[[tool.uv.index]]
name = "pytorch-cu128"
url = "https://download.pytorch.org/whl/cu128"
explicit = true

[[tool.uv.index]]
name = "pytorch-cu130"
url = "https://download.pytorch.org/whl/cu130"
explicit = true

# Route packages to indexes (CUDA 12.8 on Linux/Windows, PyPI fallback on macOS)
[tool.uv.sources]
torch = [
  { index = "pytorch-cu128", marker = "sys_platform == 'linux' or sys_platform == 'win32'" },
]
torchvision = [
  { index = "pytorch-cu128", marker = "sys_platform == 'linux' or sys_platform == 'win32'" },
]
```

**Rule:** PyTorch does not publish CUDA builds for macOS. Always gate CUDA/ROCm/XPU indexes with `sys_platform` markers and fall back to PyPI for macOS (`sys_platform != 'linux'`).

### uv (pip interface)

```bash
# CPU-only
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# CUDA 12.8
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### Automatic Backend Selection (uv pip)

uv can auto-detect the available GPU and select the matching PyTorch index:

```bash
# Auto-detect CUDA/ROCm/XPU and install the compatible build
uv pip install torch --torch-backend=auto

# Or via environment variable
UV_TORCH_BACKEND=auto uv pip install torch

# Explicit backend selection
uv pip install torch --torch-backend=cu128
UV_TORCH_BACKEND=cu130 uv pip install torch torchvision
```

**Rule:** `--torch-backend` is only available in the `uv pip` interface, not in project mode. For project mode, use explicit index configuration in `pyproject.toml`.

## Usage

See the reference files for complete code examples:

- **Tensors** — creation, dtypes, shapes, indexing, broadcasting: [01-tensors](references/01-tensors.md)
- **Operations** — math, linear algebra, reductions, FFT, random: [02-operations](references/02-operations.md)
- **Neural networks** — `nn.Module`, layers, containers, hooks, initialization: [03-nn-module](references/03-nn-module.md)
- **Functional API** — stateless activations, convolutions, pooling, losses: [04-nn-functional](references/04-nn-functional.md)
- **Autograd** — automatic differentiation, custom functions, hooks: [05-autograd](references/05-autograd.md)
- **Optimization** — optimizers, lr schedulers, gradient clipping, mixed precision: [06-optimization](references/06-optimization.md)
- **Data loading** — `Dataset`, `DataLoader`, samplers, collate functions: [07-data](references/07-data.md)
- **Compilation** — `torch.compile`, Inductor, dynamo, backends: [08-compile](references/08-compile.md)
- **TorchScript** — scripting, tracing, serialization: [09-torchscript](references/09-torchscript.md)
- **Distributed** — DDP, FSDP, collective ops, RPC: [10-distributed](references/10-distributed.md)
- **CUDA** — device management, streams, memory, custom kernels: [11-cuda](references/11-cuda.md)
- **Specialized** — sparse tensors, quantization, vmap, profiling: [12-specialized](references/12-specialized.md)
- **Training workflow** — model definition, training loop, gradient accumulation, AMP, saving/loading: [13-training-workflow](references/13-training-workflow.md)

## Gotchas

- **`torch.load()` defaults to `pickle`** — use `weights_only=True` when loading state dicts to avoid arbitrary code execution. Only omit when loading full models with custom objects.
- **`.cuda()` vs `.to(device)`** — `.to(device)` is device-agnostic and works for CPU/GPU/other. Prefer `.to(device)` for portable code. `.cuda()` is CUDA-only.
- **`model.train()` vs `model.eval()`** — must call `model.eval()` before inference. Forgets to toggle causes dropout/batch norm to behave incorrectly.
- **`optimizer.zero_grad()` is required** — PyTorch accumulates gradients. Forgetting `zero_grad()` causes gradient explosion. Alternatively use `optimizer.zero_grad(set_to_none=True)` to free memory.
- **`keepdim=True` in reductions** — `x.sum(dim=1)` changes shape from `(N, C)` to `(N,)`. Use `keepdim=True` to keep `(N, 1)` for broadcasting.
- **`view()` vs `reshape()`** — `view()` requires contiguous tensor; `reshape()` handles non-contiguous by copying. Use `view()` when you know tensor is contiguous (faster), `reshape()` for safety.
- **`inplace=True` breaks autograd** — operations like `x.add_(y)` or `F.relu(x, inplace=True)` can break gradient computation for operations that share the tensor. Avoid in `nn.Sequential` with shared weights.
- **`DataLoader` workers are separate processes** — variables from the main process are not available in worker functions. Pass data through `__getitem__`, not closures.
- **`pin_memory=True` requires enough CPU memory** — it allocates pinned (page-locked) memory. Can cause OOM on CPU with large batches. Only use when transferring to GPU.
- **`torch.compile` is not a drop-in replacement** — some dynamic patterns (variable control flow, dynamic shapes) may fall back to eager mode. Use `torch._dynamo.explain(model)` to debug.
- **`strict=False` in `load_state_dict`** — silently ignores missing keys. Use `strict=True` (default) and check return values: `missing, unexpected = model.load_state_dict(sd, strict=False)`.
- **`nn.CrossEntropyLoss` already includes softmax** — do not apply `F.softmax()` before passing to `CrossEntropyLoss`. Pass raw logits.
- **`batch_size` in DataLoader must be int** — passing `None` or a tensor causes errors. For variable batch sizes, use `batch_size=None` only with custom collate functions.
- **`torch.no_grad()` vs `inference_mode()`** — `torch.no_grad()` disables gradient tracking but still builds the graph (memory cost). `torch.inference_mode()` skips graph construction entirely (less memory, faster). Use `inference_mode()` for pure inference.
- **`device` attribute only on tensors** — `model.device` does not exist. Use `next(model.parameters()).device` to get the device.
- **`torch.Size` is a tuple** — `x.size()` returns `torch.Size([3, 4])` which is a subclass of `tuple`. Use `x.size(0)` for dim 0 length, or `x.shape[0]`.
- **`num_workers > 0` on Windows** — uses `spawn` method, not `fork`. Module-level code runs in each worker. Guard with `if __name__ == "__main__"`.
- **`torch.save` with `pickle` protocol** — default protocol is 2. Use `pickle_protocol=4` or `5` for better performance with large tensors.
- **`GradientAccumulation` requires loss scaling** — divide loss by accumulation steps before `backward()`, otherwise effective learning rate is multiplied.
- **`torch.compile` with `fullgraph=True`** — fails if any operation falls back to eager. Use without `fullgraph=True` first, then enable for strict checking.
- **`torch.cuda.empty_cache()` is rarely needed** — it frees unused cached memory back to OS. PyTorch manages its own cache efficiently. Only call when doing dynamic model switching or explicit memory management.
- **`pin_memory` with `num_workers=0`** — has no effect. Pin memory only works with multi-worker DataLoader or manual `cuda.Stream` transfers.
- **`nn.Module.children()` vs `nn.Module.modules()`** — `children()` returns immediate children; `modules()` returns all nested modules including self. Use `children()` for one-level iteration, `modules()` for global search.
- **`torch.manual_seed()` only seeds CPU** — also call `torch.cuda.manual_seed_all(seed)` for GPU reproducibility. For full reproducibility, also set `torch.backends.cudnn.deterministic = True`.
- **`torch.vmap` for batched operations** — use `torch.vmap` (not `torch.func.vmap` in 2.12) to vectorize over a batch dimension. Available since 2.0.
- **`torch.linalg` vs `torch.*`** — use `torch.linalg.solve()` instead of `torch.solve()`. The `torch.linalg` namespace is the modern API.
- **`autocast` dtype depends on device** — on CUDA defaults to `float16`, on CPU defaults to `bfloat16`. Use `torch.amp.autocast("cuda", dtype=torch.bfloat16)` to override.
- **`GradScaler` not needed for bfloat16** — `GradScaler` is for float16 to prevent underflow. bfloat16 has same exponent range as float32, so scaling is unnecessary.
- **`torch.compile` re-compiles on shape change** — each unique input shape triggers a new compilation. Use `dynamic=True` (default in 2.12) for dynamic shapes, or `dynamic=False` for static.

## References

- [01-tensors](references/01-tensors.md) — Tensor creation, dtypes, shapes, indexing, broadcasting, memory layout
- [02-operations](references/02-operations.md) — Math, linear algebra, reductions, FFT, random, special functions
- [03-nn-module](references/03-nn-module.md) — nn.Module, layers (Linear, Conv, LSTM, Transformer), containers, hooks
- [04-nn-functional](references/04-nn-functional.md) — Functional API: activations, convolutions, pooling, normalization, losses
- [05-autograd](references/05-autograd.md) — Automatic differentiation, grad computation, custom functions, hooks
- [06-optimization](references/06-optimization.md) — Optimizers, lr schedulers, gradient clipping, mixed precision
- [07-data](references/07-data.md) — Dataset, DataLoader, samplers, transforms, collate functions
- [08-compile](references/08-compile.md) — torch.compile, Inductor, dynamo, backends, debugging
- [09-torchscript](references/09-torchscript.md) — Scripting, tracing, serialization, mobile deployment
- [10-distributed](references/10-distributed.md) — DDP, FSDP, collective ops, RPC, launch utilities
- [11-cuda](references/11-cuda.md) — CUDA device management, streams, memory, custom kernels, cuDNN
- [12-specialized](references/12-specialized.md) — Sparse tensors, quantization, vmap, functional API, profiling
- [13-training-workflow](references/13-training-workflow.md) — Model definition, training loop, gradient accumulation, AMP, saving/loading
