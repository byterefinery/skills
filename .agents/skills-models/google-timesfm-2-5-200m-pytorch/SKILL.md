---
name: google-timesfm-2-5-200m-pytorch
description: Run Google's TimesFM 2.5 (200M, PyTorch) for zero-shot time-series forecasting. Use when the user asks to forecast time series, predict future values from historical data, or specifically mentions TimesFM 2.5. Returns point forecasts with calibrated quantile prediction intervals. Supports batched inference, covariates via XReg, and contexts up to 16,384 points.
metadata:
  tags:
    - ai-ml
    - time-series
    - forecasting
    - google
    - pytorch
---

# google-timesfm-2-5-200m-pytorch

## Overview

Google's **TimesFM 2.5 (200M, PyTorch)** is a pretrained decoder-only foundation model for zero-shot time-series forecasting. Feed it any univariate series — sales, sensor readings, weather, vitals, prices — and it returns point forecasts with calibrated quantile prediction intervals, no training required.

Key capabilities:
- Zero-shot forecasting on any univariate time series
- Context lengths up to 16,384 points
- Batched inference across many series
- Probabilistic forecasts (mean + 10 quantile slices: q10–q90)
- Covariate support via XReg (`pip install timesfm[xreg]`)
- ~800 MB model, ~1.5 GB RAM on CPU, ~1 GB VRAM on GPU

## Usage

### Installation

```bash
# PyTorch backend (CPU/GPU)
pip install timesfm[torch]

# For covariate forecasting (XReg)
pip install timesfm[xreg]

# Install PyTorch for your hardware
pip install torch>=2.0.0
```

### Minimal Example

```python
import torch, numpy as np, timesfm

torch.set_float32_matmul_precision("high")

model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
    "google/timesfm-2.5-200m-pytorch"
)
model.compile(timesfm.ForecastConfig(
    max_context=1024,
    max_horizon=256,
    normalize_inputs=True,
    use_continuous_quantile_head=True,
    force_flip_invariance=True,
    infer_is_positive=True,
    fix_quantile_crossing=True,
))

point, quantiles = model.forecast(
    horizon=24,
    inputs=[np.sin(np.linspace(0, 20, 200))],
)
# point.shape     == (1, 24)      — median forecast
# quantiles.shape == (1, 24, 10)  — [mean, q10, q20, ..., q90]
```

### From CSV

```python
import pandas as pd, numpy as np

df = pd.read_csv("data.csv", parse_dates=["date"])
values = df["value"].values.astype(np.float32)

point, quantiles = model.forecast(horizon=30, inputs=[values])
```

### Batch Forecasting

```python
# Multiple series (variable lengths OK)
inputs = [
    df["store_a"].dropna().values.astype(np.float32),
    df["store_b"].dropna().values.astype(np.float32),
]

point, quantiles = model.forecast(horizon=30, inputs=inputs)
# point.shape == (2, 30)
```

### Covariate Forecasting (XReg)

Requires `pip install timesfm[xreg]`.

```python
point, quantiles = model.forecast_with_covariates(
    inputs=inputs,
    dynamic_numerical_covariates={"price": price_arrays},
    dynamic_categorical_covariates={"holiday": holiday_arrays},
    static_categorical_covariates={"region": region_labels},
    xreg_mode="xreg + timesfm",
)
```

Dynamic covariates must span both the context window and the forecast horizon.

### Understanding Output

`model.forecast()` returns `(point_forecast, quantile_forecast)`:

| Index | Quantile | Use |
| ----- | -------- | --- |
| 0 | Mean | Average prediction |
| 1 | 0.10 | Lower bound of 80% PI |
| 5 | 0.50 | Median (= `point_forecast`) |
| 9 | 0.90 | Upper bound of 80% PI |

```python
lower_80 = quantiles[:, :, 1]  # 10th percentile
upper_80 = quantiles[:, :, 9]  # 90th percentile
```

### ForecastConfig Reference

```python
timesfm.ForecastConfig(
    max_context=1024,                    # Max context window (up to 16,384)
    max_horizon=256,                     # Max forecast horizon
    normalize_inputs=True,               # Always True — prevents scale instability
    per_core_batch_size=32,              # Tune for memory/speed
    use_continuous_quantile_head=True,   # Better quantile accuracy for long horizons
    force_flip_invariance=True,          # Ensures f(-x) = -f(x)
    infer_is_positive=True,              # Clamp ≥ 0 when all inputs > 0
    fix_quantile_crossing=True,          # Ensure q10 ≤ q20 ≤ ... ≤ q90
    return_backcast=False,               # Return backcast (for covariate workflows)
)
```

Set `infer_is_positive=False` for data that can be negative (temperature, financial returns).

## Gotchas

- **`compile()` is mandatory** — call `model.compile(ForecastConfig(...))` before `forecast()`, or `forecast()` raises `RuntimeError`.
- **Quantile index 0 is the mean, not q0** — q10 is at index 1, q90 at index 9. Common off-by-one bug.
- **No frequency flag in 2.5** — TimesFM 2.5 removed the `freq` parameter entirely. Do not pass it.
- **Context length is configurable** — set `max_context` in `ForecastConfig` to match your data. Default supports up to 16,384 points, but use smaller values (512–1024) for memory-constrained environments.
- **Trailing NaNs are not handled** — drop them before passing to `forecast()`. Leading NaNs are stripped automatically; internal NaNs are linearly interpolated.
- **`torch.set_float32_matmul_precision("high")`** — always set this on Ampere+ GPUs (A100, RTX 3090+) for speed.
- **`matplotlib.use("Agg")`** — set before any pyplot import when running headless.
- **Covariates need full-span arrays** — dynamic covariates must cover both the context window and the forecast horizon, not just the horizon.
- **Minimum series length** — context must be at least 32 data points.
- **`infer_is_positive`** — leave True for counts/demand; set False for temperature, returns, or any series that can be negative.
- **Memory formula** — `RAM ≈ 0.8 GB (model) + 0.5 GB (overhead) + (0.2 MB × num_series × context_length / 1000)`. Process in chunks for large batches.
- **`forecast_with_covariates()` is 2.5 only** — not available in TimesFM 1.0/2.0.

## References

- [01-api-reference](references/01-api-reference.md) — Full `TimesFM_2p5_200M_torch` API, `ForecastConfig` parameters, and output shapes
- [02-data-preparation](references/02-data-preparation.md) — Input formats, NaN handling, CSV/Excel/Parquet loading, covariate setup
- [03-system-requirements](references/03-system-requirements.md) — Hardware tiers, GPU/CPU selection, batch size tuning, memory estimation
- [04-examples](references/04-examples.md) — Worked examples: single series, batch, evaluation, anomaly detection, covariates
