---
name: datadog-toto-2-0-2-5b
description: >
  Datadog Toto 2.0 2.5B — 2.45B-parameter decoder-only transformer for zero-shot
  multivariate time series forecasting. Trained with u-μP scaling, alternating
  time/variate attention, contiguous patch masking (CPM) for single-pass parallel
  decoding, and a quantile output head (0.1–0.9). Highest-accuracy checkpoint in the
  Toto 2.0 family (4m → 2.5B). #1 foundation model on BOOM, GIFT-Eval, and TIME
  benchmarks. Supports variable context/horizon, missing values via target_mask,
  and GluonTS integration. Requires `toto-models` (Python 3.12+, PyTorch 2.5+).
  Use when the user needs high-accuracy zero-shot multivariate time series forecasting,
  observability metric forecasting, or specifically mentions Datadog Toto 2.0.
metadata:
  tags:
    - ml
    - deep-learning
    - time-series
    - forecasting
    - foundation-model
    - multivariate
    - probabilistic
    - datadog
    - observability
---

# datadog-toto-2-0-2-5b

## Overview

Toto 2.0 2.5B is the largest checkpoint in Datadog's Toto 2.0 family — a decoder-only patched transformer for zero-shot multivariate time series forecasting. It uses alternating time-axis (causal) and variate-axis (full) attention layers, contiguous patch masking (CPM) for parallel decoding, and a quantile output head trained with pinball loss.

Key capabilities:
- **Zero-shot multivariate forecasting** — no fine-tuning needed, works on any multivariate time series
- **Alternating time/variate attention** — efficiently models cross-variable dependencies
- **Probabilistic outputs** — 9 quantile levels (0.1 through 0.9) for uncertainty estimates
- **Contiguous Patch Masking (CPM)** — enables single-pass parallel decoding for horizons up to `decode_block_size`
- **Variable context and horizon** — flexible input lengths, flexible prediction horizons
- **Missing value handling** — `target_mask` controls which positions are observed
- **GluonTS integration** — `Toto2GluonTSModel` wraps the model as a standard GluonTS predictor
- **u-μP scaled** — single training recipe transfers cleanly from 4m to 2.5B parameters

Install with `pip install toto-models` (Python 3.12+, PyTorch 2.5+). Load with `Toto2Model.from_pretrained("Datadog/Toto-2.0-2.5B")`.

### Model Details

| Property | Value |
|---|---|
| Parameters | 2,454,281,792 (~2.5B) |
| Architecture | Decoder-only patched transformer, 48 layers, 32 heads, d_model=2048 |
| Patch size | 32 |
| Quantile levels | [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9] |
| Scaler | Causal std-dev scaler with arcsinh transform |
| Weights (fp32) | ~9.1 GB |
| Latency (A100, bs=8, ctx=1024) | ~36.2 ms |
| License | Apache-2.0 |
| Paper | [Toto 2.0: Time Series Forecasting Enters the Scaling Era](https://arxiv.org/abs/2605.20119) |

### Benchmark Results

| Benchmark | CRPS | MASE | Rank |
|---|---|---|---|
| BOOM | 0.349 | 0.581 | #1 |
| GIFT-Eval | 0.476 | 0.696 | #1 |
| TIME | 0.532 | 0.640 | #1 |

Other Toto 2.0 sizes: 4m (16 MB), 22m (84 MB), 313m (1.2 GB), 1B (3.9 GB). All share the same API and training recipe.

## Usage

### Installation

```bash
pip install toto-models
```

Requires Python 3.12+ and PyTorch 2.5+. CUDA-capable GPU (Ampere+) recommended for optimal performance.

### Loading the Model

```python
import torch
from toto2 import Toto2Model

model = Toto2Model.from_pretrained("Datadog/Toto-2.0-2.5B")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device).eval()
```

### Univariate Forecasting

```python
import torch

context_length = 512
t = torch.arange(context_length, dtype=torch.float32)
series = 100 + 0.05 * t + 10 * torch.sin(2 * torch.pi * t / 24) + torch.randn(context_length)

# Shape: (batch=1, n_var=1, time)
target = series.unsqueeze(0).unsqueeze(0).to(device)
target_mask = torch.ones_like(target, dtype=torch.bool)
series_ids = torch.zeros(1, 1, dtype=torch.long, device=device)

horizon = 96
quantiles = model.forecast(
    {"target": target, "target_mask": target_mask, "series_ids": series_ids},
    horizon=horizon,
)

# Output shape: (9, batch, n_var, horizon)
# Quantile levels: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
print(quantiles.shape)  # (9, 1, 1, 96)

# Access median (0.5 quantile)
median = quantiles[4, 0, 0]  # index 4 = 0.5
q10 = quantiles[0, 0, 0]     # index 0 = 0.1
q90 = quantiles[8, 0, 0]     # index 8 = 0.9
```

### Multivariate Forecasting

Pass multiple variates along the `n_var` dimension. The model's alternating time/variate attention layers model cross-variable dependencies:

```python
n_var = 5
target_mv = torch.randn(1, n_var, 512, device=device)
mask_mv = torch.ones(1, n_var, 512, dtype=torch.bool, device=device)
ids_mv = torch.zeros(1, n_var, dtype=torch.long, device=device)

quantiles_mv = model.forecast(
    {"target": target_mv, "target_mask": mask_mv, "series_ids": ids_mv},
    horizon=48,
)
# Output shape: (9, 1, 5, 48)
```

### Handling Missing Values

Set `target_mask` to `False` where observations are missing. The model masks these positions in both the scaler and attention:

```python
target_missing = series.unsqueeze(0).unsqueeze(0).to(device)
mask_missing = torch.ones_like(target_missing, dtype=torch.bool)
# Mask 20% of positions
mask_missing[0, 0, torch.randperm(context_length)[:context_length // 5]] = False

quantiles = model.forecast(
    {"target": target_missing, "target_mask": mask_missing, "series_ids": series_ids},
    horizon=96,
)
```

### Decoding Strategies

`decode_block_size` controls the decoding strategy:

```python
# Single forward pass — faster, better short-term accuracy (used for leaderboard results)
quantiles = model.forecast(inputs, horizon=96, decode_block_size=None)

# Block decode — better long-term stability for horizons ≳1000
quantiles = model.forecast(inputs, horizon=2000, decode_block_size=768)
```

With block decoding, the model uses a KV cache and median feedback between blocks. The causal scaler re-runs each iteration so loc/scale update as predicted medians fill in.

### Performance Optimization

```python
# When context has no missing values, enable Flash Attention
quantiles = model.forecast(
    inputs, horizon=96, has_missing_values=False,
)

# Cap quantile range to prevent extreme outliers
quantiles = model.forecast(
    inputs, horizon=96, quantile_real_cap_k=10.0,
)

# Backfill loc/scale on short-observation leading patches
quantiles = model.forecast(
    inputs, horizon=96, scaler_fallback_min_obs=8,
)
```

### GluonTS Integration

Wrap the model with `Toto2GluonTSModel` for standard GluonTS evaluation pipelines:

```python
from toto2 import Toto2Model, Toto2GluonTSModel, Toto2GluonTSModelConfig

model = Toto2Model.from_pretrained("Datadog/Toto-2.0-2.5B").to(device).eval()

gts_config = Toto2GluonTSModelConfig(
    prediction_length=96,
    context_length=512,
    target_dim=1,  # or 2 for multivariate
    imputation_internal="ffill",  # "none", "ffill", "linear"
)

gts_model = Toto2GluonTSModel(model, gts_config).to(device).eval()
predictor = gts_model.create_predictor(batch_size=64, device=device)

# Predict on GluonTS datasets
from gluonts.dataset.repository import get_dataset
dataset = get_dataset("airpassengers")
from gluonts.dataset.split import split

_, test_template = split(dataset.test, offset=-dataset.metadata.prediction_length)
test_data = test_template.generate_instances(
    prediction_length=dataset.metadata.prediction_length, windows=1,
)
forecasts = list(predictor.predict(test_data.input))

# Evaluate
from gluonts.model import evaluate_model
from gluonts.ev.metrics import MAE, MASE, MSE, MeanWeightedSumQuantileLoss

results = evaluate_model(
    predictor, test_data=test_data,
    metrics=[MASE(), MAE(), MeanWeightedSumQuantileLoss()],
)
```

### Batch Forecasting

```python
# Batch of independent univariate series
batch_size = 32
target_batch = torch.randn(batch_size, 1, 512, device=device)
mask_batch = torch.ones_like(target_batch, dtype=torch.bool)
ids_batch = torch.zeros(batch_size, 1, dtype=torch.long, device=device)

quantiles = model.forecast(
    {"target": target_batch, "target_mask": mask_batch, "series_ids": ids_batch},
    horizon=48,
)
# Output: (9, 32, 1, 48)
```

## Gotchas

- **`target_mask` is required** — every call to `forecast()` needs `target`, `target_mask`, and `series_ids` in the inputs dict. All three are mandatory.
- **Output shape is `(Q, batch, n_var, horizon)`** — quantile dimension is first, not last. Index `[4]` is the median (0.5 quantile), `[0]` is 0.1, `[8]` is 0.9.
- **`decode_block_size` must be divisible by patch size (32)** — passing a non-multiple raises an assertion error. Valid values: 32, 64, 96, …, 768, etc.
- **`has_missing_values=False` requires a fully observed mask** — only set this when `target_mask` is all `True`. If any position is masked, leave it as `True` (default).
- **No fine-tuning support yet** — fine-tuning and exogenous variable support are planned for a future 2.0 release. Use Toto 1.0 if you need fine-tuning today.
- **No exogenous covariates** — Toto 2.0 does not accept known-future or past-only covariates. For covariate-aware forecasting, use Toto 1.0.
- **`series_ids` controls cross-series attention** — series with the same `series_id` share attention; different IDs isolate attention. Use `torch.zeros` for independent series, or assign matching IDs for related series.
- **Model downloads on first use** — the 2.5B checkpoint is ~9.1 GB (fp32 safetensors). First load triggers download; consider explicit caching in production.
- **`forecast()` runs under `torch.no_grad()`** — gradients are disabled automatically. No need to wrap manually.
- **Causal scaler is autoregressive** — the `PatchedCausalStdScaler` computes loc/scale causally. In block decoding mode, it re-runs each iteration as medians fill in.
- **`quantile_real_cap_k` prevents extreme outliers** — default is 0 (disabled). Set to a positive value (e.g., 10.0) to clip quantiles to `[ctx_min - K*scale, ctx_max + K*scale]`. Useful for production stability.
- **`scaler_fallback_min_obs` backfills short patches** — default 0 (disabled). Set to a positive value (e.g., 8) to backfill loc/scale on leading patches with few observations. Helps with sparse data.
- **Python 3.12+ required** — `toto-models` requires Python 3.12+. It will not install on older versions.
- **`toto2` not `toto`** — import from `toto2` (the 2.0 package), not `toto` (the 1.0 package). The packages are separate: `toto-models` for 2.0, `toto-ts` for 1.0.

## References

- [01-architecture](references/01-architecture.md) — Decoder-only patched transformer, alternating time/variate attention, CPM, quantile head, u-μP scaling
- [02-api-reference](references/02-api-reference.md) — Full API: Toto2Model, Toto2GluonTSModel, forecast(), create_predictor(), configuration details
- [03-gluonts-integration](references/03-gluonts-integration.md) — GluonTS predictor setup, evaluation pipelines, dataset loading, metrics
- [04-model-sizes](references/04-model-sizes.md) — Family comparison: 4m, 22m, 313m, 1B, 2.5B architectures, benchmarks, selection guide
- [05-toto-1-0-comparison](references/05-toto-1-0-comparison.md) — Differences between Toto 1.0 and 2.0, migration guide, when to use each
