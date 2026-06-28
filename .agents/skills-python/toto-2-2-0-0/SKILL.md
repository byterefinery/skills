---
name: toto-2-2-0-0
description: >
  DataDog Toto 2.0 — a foundation model for multivariate time series forecasting
  with a focus on observability metrics. Use when working with zero-shot time
  series forecasting, probabilistic predictions (quantile-based), multi-variate
  time series, or observability metric prediction. Covers the full Toto 2.0
  model family (4m to 2.5B parameters), the Toto2Model API, forecast(),
  decode strategies (single-pass and block decode), GluonTS integration via
  Toto2GluonTSModel, BOOM and GIFT-Eval benchmarks, and missing-value handling.
  Default model: Datadog/Toto-2.0-22m. Trigger on: toto, toto-2, time-series
  forecasting, observability metrics, zero-shot forecasting, quantile
  forecasting, multivariate time series, BOOM benchmark, GluonTS integration.
metadata:
  tags:
    - ml
    - time-series
    - deep-learning
    - python
    - observability
---

# toto 2.2.0.0

## Overview

Toto 2.0 is DataDog's foundation model for multivariate time series forecasting, optimized for observability metrics. It uses a u-μP-scaled decoder-only transformer with alternating time/variate attention and a quantile-based probabilistic forecasting head. The model supports zero-shot forecasting without fine-tuning on domain-specific data.

**Key capabilities:**
- **Zero-shot forecasting** — forecast without fine-tuning on your specific time series
- **Probabilistic predictions** — outputs 9 quantile levels `[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]` for uncertainty estimates
- **Multi-variate support** — alternating time/variate attention efficiently processes many variables
- **High-dimensional support** — handles time series with large numbers of variables
- **Variable horizons and context lengths** — decoder-only architecture supports flexible prediction windows
- **Flash Attention** — enabled via `has_missing_values=False` for meaningful speedups on gap-free data

**Model family (all on Hugging Face under `Datadog/`):**

| Model | Parameters | Best for |
|---|---|---|
| `Datadog/Toto-2.0-4m` | 4m | Edge / constrained environments |
| `Datadog/Toto-2.0-22m` | 22m | Default — balanced speed and accuracy |
| `Datadog/Toto-2.0-313m` | 313m | Higher accuracy, moderate compute |
| `Datadog/Toto-2.0-1B` | 1B | High-accuracy forecasting |
| `Datadog/Toto-2.0-2.5B` | 2.5B | Maximum accuracy, large compute budget |

**Dependencies:** Python 3.10+, PyTorch 2.5+, CUDA-capable device (Ampere+ recommended).

**Not yet available:** Fine-tuning and exogenous variable (EV) support are planned for a future 2.0 release. Use [Toto 1.0](https://github.com/DataDog/toto) if you need those features today.

## Usage

### Installation

```bash
pip install "toto-2 @ git+https://github.com/DataDog/toto.git#subdirectory=toto2"
```

### Quick Start

```python
import torch
from toto2 import Toto2Model

model = Toto2Model.from_pretrained("Datadog/Toto-2.0-22m")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device).eval()

# Input shape: (batch, n_variates, time_steps)
target = torch.randn(1, 1, 512, device=device)
target_mask = torch.ones_like(target, dtype=torch.bool)
series_ids = torch.zeros(1, 1, dtype=torch.long, device=device)

# Returns quantiles of shape (9, batch, n_variates, horizon)
# Quantile levels: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
quantiles = model.forecast(
    {"target": target, "target_mask": target_mask, "series_ids": series_ids},
    horizon=96,
    decode_block_size=768,
    has_missing_values=False,
)

# Point forecast (median = 0.5 quantile, index 4)
median = quantiles[4]  # (batch, n_variates, horizon)

# Confidence interval (10th to 90th percentile)
lower = quantiles[0]   # (batch, n_variates, horizon)
upper = quantiles[8]   # (batch, n_variates, horizon)
```

### Multi-Variate Forecasting

```python
# 5 variables, 1024 context steps
target = torch.randn(1, 5, 1024, device=device)
target_mask = torch.ones_like(target, dtype=torch.bool)
series_ids = torch.zeros(1, 5, dtype=torch.long, device=device)

quantiles = model.forecast(
    {"target": target, "target_mask": target_mask, "series_ids": series_ids},
    horizon=336,
    decode_block_size=768,
    has_missing_values=False,
)
```

### Handling Missing Values

```python
# Mark missing timesteps with False in target_mask
target = torch.randn(1, 3, 512, device=device)
target_mask = torch.ones_like(target, dtype=torch.bool)
target_mask[:, :, 100:150] = False  # gap in timesteps 100-149

# Set has_missing_values=True (disables Flash Attention but handles gaps correctly)
quantiles = model.forecast(
    {"target": target, "target_mask": target_mask, "series_ids": series_ids},
    horizon=96,
    has_missing_values=True,
)
```

### Decode Strategy Selection

```python
# Single forward pass (no block decode) — faster, better short-term accuracy
# Used for all leaderboard/benchmark results
quantiles = model.forecast(inputs, horizon=96, decode_block_size=None)

# Block decode — better long-term stability for horizons ≳1000
quantiles = model.forecast(inputs, horizon=2000, decode_block_size=768)
```

### GluonTS Integration

```python
from toto2 import Toto2GluonTSModel

# Wrap Toto 2.0 for use with GluonTS evaluation pipelines
toto_gluonts = Toto2GluonTSModel.from_pretrained("Datadog/Toto-2.0-22m")

# Use with GluonTS evaluators, datasets, and metrics
# See the GluonTS integration notebook for full examples
```

### Evaluating on Benchmarks

- **GIFT-Eval**: Use the [official notebook](https://github.com/SalesforceAIResearch/gift-eval/blob/main/notebooks/toto_2_0.ipynb) from the GIFT-Eval repository.
- **BOOM**: Use the [BOOM evaluation notebook](https://github.com/DataDog/toto/tree/v2.0.0/boom/notebooks/toto.ipynb) and [BOOM README](https://github.com/DataDog/toto/tree/v2.0.0/boom/README.md) for observability-focused benchmarking.

## Gotchas

- **Fine-tuning is not available in 2.0** — it is planned for a future release. Use Toto 1.0 (`pip install toto-ts`) if you need fine-tuning or exogenous variable support.
- **`has_missing_values` controls Flash Attention** — set to `False` when your context has no gaps for a meaningful speedup. Leave as `True` (default) if `target_mask` contains any `False` entries; the model will handle gaps correctly but fall back to standard attention.
- **`decode_block_size=None` vs block decode** — `None` means a single forward pass (used for all leaderboard results, better for short horizons). Use a value like `768` for block decoding when horizons are ≳1000 for better long-term stability.
- **Output shape is `(9, batch, n_variates, horizon)`, not `(batch, ...)`** — the first dimension is the quantile index. The median (0.5 quantile) is at index 4.
- **`series_ids` must be provided** — even for a single series, pass `torch.zeros(1, n_variates, dtype=torch.long)`. It distinguishes different time series in a batch.
- **`target_mask` is required** — pass `torch.ones_like(target, dtype=torch.bool)` for fully observed data. Set entries to `False` for missing timesteps.
- **Context length flexibility** — the decoder-only architecture accepts variable context lengths, but very short contexts may produce unreliable forecasts. Typical contexts range from 256 to 4096+ timesteps.
- **CUDA device required for large models** — the 1B and 2.5B models need substantial GPU memory. Use the 4m or 22m variants for CPU or constrained environments.
- **Installation is from git, not PyPI** — use `pip install "toto-2 @ git+https://..."` with the `#subdirectory=toto2` fragment. The 1.0 package is separate (`pip install toto-ts`).
- **Quantiles are fixed at 9 levels** — the model always outputs `[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]`. There is no 0.0 or 1.0 quantile.

## References

- [01-api-reference](references/01-api-reference.md) — Toto2Model, forecast(), Toto2GluonTSModel API details
- [02-benchmarks](references/02-benchmarks.md) — BOOM and GIFT-Eval benchmark setup, evaluation scripts, expected results
- [03-toto-1-comparison](references/03-toto-1-comparison.md) — Differences between Toto 1.0 and 2.0, migration notes, when to use 1.0
