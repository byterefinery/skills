# Model Sizes

## Family Overview

All five Toto 2.0 checkpoints share the same training recipe, architecture, and API. They differ only in width/depth scaling via u-μP. Pick a size based on accuracy/latency budget.

| Model | Params | d_model | Layers | Heads | Weights (fp32) | Latency (A100, bs=8) |
|---|---|---|---|---|---|---|
| Toto-2.0-4m | 4.1M | 256 | 4 | 4 | 16 MB | ~3.8 ms |
| Toto-2.0-22m | 21.9M | 512 | 6 | 8 | 84 MB | ~5.0 ms |
| Toto-2.0-313m | 312.7M | 1024 | 24 | 16 | 1.2 GB | ~15.4 ms |
| Toto-2.0-1B | 1.04B | 1536 | 36 | 24 | 3.9 GB | ~20.9 ms |
| Toto-2.0-2.5B | 2.45B | 2048 | 48 | 32 | 9.1 GB | ~36.2 ms |

Latency is forward-pass time for a 1,024-step single-pass forecast at batch size 8 on a single A100.

## Benchmark Comparison

### BOOM (Observability)

| Model | CRPS | MASE |
|---|---|---|
| 4m | 0.377 | 0.624 |
| 22m | 0.363 | 0.601 |
| 313m | 0.351 | 0.585 |
| 1B | 0.349 | 0.582 |
| **2.5B** | **0.349** | **0.581** |

### GIFT-Eval (General-Purpose)

| Model | CRPS | MASE |
|---|---|---|
| 4m | 0.524 | 0.757 |
| 22m | 0.496 | 0.719 |
| 313m | 0.481 | 0.703 |
| 1B | 0.478 | 0.699 |
| **2.5B** | **0.476** | **0.696** |

### TIME (Contamination-Resistant)

| Model | CRPS | MASE |
|---|---|---|
| 4m | 0.574 | 0.689 |
| 22m | 0.556 | 0.668 |
| 313m | 0.535 | 0.642 |
| 1B | 0.537 | 0.643 |
| **2.5B** | **0.532** | **0.640** |

## Selection Guide

### Use 4m (16 MB) when:
- Edge deployment with tight memory constraints
- CPU-only inference
- Latency-critical applications (< 5 ms)
- Prototyping and quick experiments

### Use 22m (84 MB) when:
- Efficient default choice
- Matches or beats Toto 1.0 quality with ~7× fewer parameters
- Moderate accuracy needs with low resource usage
- Batch processing on CPU

### Use 313m (1.2 GB) when:
- Strong general-purpose accuracy needed
- Top-3 foundation model on GIFT-Eval
- Good accuracy/latency tradeoff
- Available on consumer GPUs (RTX 3060+)

### Use 1B (3.9 GB) when:
- Best quality/cost tradeoff for production
- Available on datacenter GPUs (A10G, T4)
- Need near-state-of-the-art accuracy with reasonable latency
- Production workloads with moderate throughput

### Use 2.5B (9.1 GB) when:
- Highest accuracy is the priority
- #1 foundation model on every benchmark
- Available on high-end GPUs (A100, H100)
- Batch processing where latency is secondary to accuracy
- Research and benchmarking

## Architecture Differences

All models share identical structural design:
- Same patch size (32)
- Same alternating time/variate attention pattern
- Same quantile output head (9 levels)
- Same causal scaler with arcsinh
- Same `layer_group_size` = `num_layers` (1 variate layer per group)

Differences are purely in width/depth:

| Model | d_model | d_ff | num_layers | num_heads | num_groups | layer_group_size |
|---|---|---|---|---|---|---|
| 4m | 256 | 688 | 4 | 4 | 4 | 4 |
| 22m | 512 | 1368 | 6 | 8 | 8 | 6 |
| 313m | 1024 | 2736 | 24 | 16 | 16 | 24 |
| 1B | 1536 | 4096 | 36 | 24 | 24 | 36 |
| 2.5B | 2048 | 5464 | 48 | 32 | 32 | 48 |

Smaller models (4m, 22m) have `norm_eps=0.0001` and `qk_norm=False`. Larger models (1B, 2.5B) use `norm_eps=0.0005`. All use `use_xpos=True` and `per_dim_scale=True`.

## Loading Any Size

```python
from toto2 import Toto2Model

# Swap size by changing checkpoint
SIZE = "2.5B"  # "4m" | "22m" | "313m" | "1B" | "2.5B"
model = Toto2Model.from_pretrained(f"Datadog/Toto-2.0-{SIZE}")
```

The API is identical across all sizes.
