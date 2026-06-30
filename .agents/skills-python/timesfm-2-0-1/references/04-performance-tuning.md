# Performance Tuning

## Batch Size Guidelines

`per_core_batch_size` controls the number of series processed per device per batch. Tune based on available memory:

| Hardware | Recommended `per_core_batch_size` | Notes |
|----------|-----------------------------------|-------|
| GPU 4 GB VRAM | 8–16 | Small batches, chunk large datasets |
| GPU 8 GB VRAM | 32–64 | Good balance |
| GPU 16 GB VRAM | 64–128 | High throughput |
| GPU 24+ GB VRAM | 128–256 | Max throughput |
| CPU 4 GB RAM | 1–4 | Very small batches |
| CPU 8 GB RAM | 4–8 | Moderate |
| CPU 16 GB RAM | 16–32 | Good |
| CPU 32+ GB RAM | 32–64 | High |

Global batch size = `per_core_batch_size × num_devices`.

## Memory Estimation

### Model Memory

| Component | Size |
|-----------|------|
| Model weights (200M params) | ~800 MB (fp32) / ~400 MB (fp16) |
| Quantile head (30M params) | ~120 MB (fp32) / ~60 MB (fp16) |
| Decode caches (per series) | ~2 MB per 1024 context |
| Activations (per series) | ~1 MB per 1024 context |

### Total Memory Formula

```
RAM (GB) ≈ 0.8 (model) + 0.5 (overhead) + (0.0002 × num_series × context_length)
```

| Dataset Size | Context=512 | Context=1024 | Context=2048 |
|--------------|-------------|--------------|--------------|
| 100 series | ~1.4 GB | ~1.5 GB | ~1.7 GB |
| 1,000 series | ~1.9 GB | ~2.3 GB | ~3.1 GB |
| 10,000 series | ~9.0 GB | ~17.0 GB | ~33.0 GB |

### Reducing Memory

1. **Reduce context**: `max_context=512` instead of 2048 (50% reduction in per-series memory)
2. **Chunk processing**: Split large batches into smaller groups
3. **Reduce batch size**: Lower `per_core_batch_size`
4. **Use fp16/bf16**: `torch.set_float32_matmul_precision("high")` on Ampere+ GPUs

## Chunked Inference

For datasets that don't fit in memory:

```python
CHUNK_SIZE = 100
all_points = []
all_quantiles = []

for i in range(0, len(inputs), CHUNK_SIZE):
    chunk = inputs[i:i + CHUNK_SIZE]
    point, quantiles = model.forecast(horizon=H, inputs=chunk)
    all_points.append(point)
    all_quantiles.append(quantiles)

point_forecast = np.concatenate(all_points, axis=0)
quantile_forecast = np.concatenate(all_quantiles, axis=0)
```

## GPU Optimization

### Ampere+ GPUs (A100, RTX 3090/4090)

```python
import torch

# Enable TF32 for faster matmul
torch.set_float32_matmul_precision("high")

# Or explicitly use bf16
torch.autocast(device_type="cuda", dtype=torch.bfloat16)
```

### CUDA Memory Management

```python
import torch

# Clear cache between large batches
torch.cuda.empty_cache()

# Check available memory
print(f"GPU memory: {torch.cuda.memory_allocated() / 1e9:.1f} GB")
```

## CPU Optimization

```python
# Use all available CPU threads
import os
os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())

# Or limit threads to avoid oversubscription
os.environ["OMP_NUM_THREADS"] = "4"
```

## Context Length Tradeoffs

| Context | Accuracy | Speed | Memory |
|---------|----------|-------|--------|
| 256 | Lower (limited history) | Fastest | Lowest |
| 512 | Good balance | Fast | Low |
| 1024 | High accuracy | Moderate | Moderate |
| 2048 | Higher accuracy | Slower | Higher |
| 4096+ | Diminishing returns | Slow | High |

**Recommendation**: Start with `max_context=1024` and increase only if accuracy on your data improves.

## Horizon Tradeoffs

| Horizon | Decode Steps | Notes |
|---------|-------------|-------|
| 1–128 | 0 (prefill only) | Fastest — no autoregressive steps |
| 129–256 | 1 decode step | One feedback loop |
| 257–384 | 2 decode steps | Two feedback loops |
| 385–512 | 3 decode steps | Three feedback loops |
| 513+ | 4+ decode steps | Each step adds latency |

Number of decode steps: `(horizon - 1) // 128`

## Compilation Overhead

- **First call**: `compile()` sets up the decode function (fast, no torch.compile)
- **First inference**: Model weights are loaded and device is set
- **Subsequent calls**: Cached decode function is reused

## Benchmarking

```python
import time

# Warmup
model.forecast(horizon=H, inputs=[np.random.randn(512)])

# Benchmark
N_ITERATIONS = 10
start = time.perf_counter()
for _ in range(N_ITERATIONS):
    model.forecast(horizon=H, inputs=batch)
elapsed = time.perf_counter() - start

throughput = len(batch) * N_ITERATIONS / elapsed
print(f"Throughput: {throughput:.1f} series/sec")
print(f"Latency: {elapsed / N_ITERATIONS * 1000:.1f} ms/batch")
```

## JAX/Flax Backend

The Flax backend (`timesfm[flax]`) can be faster on TPU and some GPU setups:

```python
import timesfm

model = timesfm.TimesFM_2p5_200M_flax.from_pretrained(
    "google/timesfm-2.5-200m-flax"
)
model.compile(timesfm.ForecastConfig(max_context=1024, max_horizon=256))
```

JAX compiles kernels on first call (tracing overhead), then runs at high speed.
