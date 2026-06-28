# System Requirements for TimesFM 2.5

## Hardware Overview

TimesFM 2.5 (200M parameters) is lightweight compared to earlier versions:

| Resource | TimesFM 2.5 | TimesFM 2.0 (archived) |
| -------- | ----------- | ---------------------- |
| Parameters | 200M | 500M |
| Disk (weights) | ~800 MB | ~2 GB |
| RAM (CPU) | ~1.5 GB | ~32 GB |
| VRAM (GPU) | ~1 GB | ~8 GB |
| Max context | 16,384 | 2,048 |

## Hardware Tiers

### Tier 1: Minimal (CPU-Only, 4–8 GB RAM)

- **Use case**: Light exploration, single-series forecasting, prototyping
- **Batch size**: `per_core_batch_size=4`
- **Context**: `max_context=512`
- **Expected speed**: ~2–5 seconds per 100-point series

```python
model.compile(timesfm.ForecastConfig(
    max_context=512,
    max_horizon=128,
    per_core_batch_size=4,
    normalize_inputs=True,
    use_continuous_quantile_head=True,
    fix_quantile_crossing=True,
))
```

### Tier 2: Standard (CPU 16 GB or GPU 4–8 GB VRAM)

- **Use case**: Batch forecasting (dozens of series), evaluation, production prototypes
- **Batch size**: `per_core_batch_size=32` (CPU) or `64` (GPU)
- **Context**: `max_context=1024`
- **Expected speed**: ~0.5–1 second per 100-point series (GPU)

```python
model.compile(timesfm.ForecastConfig(
    max_context=1024,
    max_horizon=256,
    per_core_batch_size=64,
    normalize_inputs=True,
    use_continuous_quantile_head=True,
    fix_quantile_crossing=True,
))
```

### Tier 3: Production (GPU 16+ GB VRAM or Apple Silicon 32+ GB)

- **Use case**: Large-scale batch forecasting (thousands of series), long context
- **Batch size**: `per_core_batch_size=128–256`
- **Context**: `max_context=4096` or higher
- **Expected speed**: ~0.1–0.3 seconds per 100-point series

```python
model.compile(timesfm.ForecastConfig(
    max_context=4096,
    max_horizon=256,
    per_core_batch_size=128,
    normalize_inputs=True,
    use_continuous_quantile_head=True,
    fix_quantile_crossing=True,
))
```

## Memory Estimation

**Formula**: `RAM ≈ 0.8 GB (model) + 0.5 GB (overhead) + (0.2 MB × num_series × context_length / 1000)`

| Scenario | Series | Context | Est. RAM |
| -------- | ------ | ------- | -------- |
| Single series | 1 | 512 | ~1.3 GB |
| Small batch | 10 | 512 | ~1.5 GB |
| Medium batch | 100 | 1024 | ~2.5 GB |
| Large batch | 1000 | 1024 | ~200 GB |

For large batches, process in chunks:

```python
CHUNK = 50
results = []
for i in range(0, len(inputs), CHUNK):
    p, q = model.forecast(horizon=H, inputs=inputs[i:i+CHUNK])
    results.append((p, q))
```

## GPU Setup

### NVIDIA CUDA

```bash
pip install torch>=2.0.0 --index-url https://download.pytorch.org/whl/cu121
```

Always set precision for Ampere+ GPUs:
```python
torch.set_float32_matmul_precision("high")
```

### Apple Silicon (MPS)

```bash
pip install torch>=2.0.0  # MPS support is built-in
```

PyTorch automatically uses MPS on Apple Silicon. No extra configuration needed.

### CPU

```bash
pip install torch>=2.0.0 --index-url https://download.pytorch.org/whl/cpu
```

## Batch Size Guidelines

| Hardware | Recommended `per_core_batch_size` |
| -------- | --------------------------------- |
| GPU 8 GB VRAM | 64 |
| GPU 16 GB VRAM | 128 |
| CPU 8 GB RAM | 8 |
| CPU 16 GB RAM | 32 |
| CPU 32+ GB RAM | 64 |

## Disk Space

- Model weights: ~800 MB (downloaded on first use from Hugging Face Hub)
- Cache location: `~/.cache/huggingface/hub/`
- Specify custom cache: `model = TimesFM_2p5_200M_torch.from_pretrained(..., cache_dir="/path/to/cache")`
