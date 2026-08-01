---
name: timesfm-2-0-1
description: >
  TimesFM 2.0.1 — pretrained decoder-only foundation model for zero-shot time series
  forecasting from Google Research. Provides the TimesFM 2.5 model (200M parameters,
  16,384 context length) with PyTorch and JAX/Flax backends. Returns point forecasts
  with calibrated quantile prediction intervals. Supports covariate-aware forecasting
  via XReg (dynamic/static numerical and categorical features). Batch inference with
  automatic NaN handling, input normalization, and quantile crossing repair. Use when
  the user needs zero-shot probabilistic time series forecasting, quantile prediction
  intervals, covariate-aware forecasts, or fast batch inference on arbitrary univariate
  time series without training.
metadata:
  tags:
    - ml
    - deep-learning
    - time-series
    - forecasting
    - foundation-model
    - probabilistic
---

# timesfm 2.0.1

## Overview

TimesFM (Time Series Foundation Model) is a pretrained decoder-only transformer for zero-shot time series forecasting. The 2.0.1 package ships the TimesFM 2.5 model (200M parameters). Install with `pip install timesfm[torch]` (requires Python 3.10+).

### Model Architecture

- **Architecture**: Decoder-only transformer with 20 layers, 16 attention heads, d_model=1280
- **Parameters**: 200M (main model) + 30M (optional continuous quantile head)
- **Context length**: Up to 16,384 time points
- **Forecast horizon**: Up to 1,024 steps via continuous quantile head
- **Input patch size**: 32 time steps per token
- **Output patch size**: 128 time steps per generation step
- **Quantiles**: Trained on [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]; output has 10 channels (mean + 9 quantiles)
- **Normalization**: Uses ReVIN (Reversible Instance Normalization) for per-series normalization
- **License**: Apache-2.0

### Backends

| Backend | Install | Class | Notes |
|---------|---------|-------|-------|
| PyTorch | `pip install timesfm[torch]` | `TimesFM_2p5_200M_torch` | Default; CPU + CUDA + MPS |
| JAX/Flax | `pip install timesfm[flax]` | `TimesFM_2p5_200M_flax` | Faster on TPU/GPU |

### Available Checkpoints

| Model ID | Backend | Context |
|----------|---------|---------|
| `google/timesfm-2.5-200m-pytorch` | PyTorch | 16,384 |
| `google/timesfm-2.5-200m-flax` | JAX/Flax | 16,384 |
| `google/timesfm-2.5-200m-transformers` | Transformers | 16,384 |

Archived models (TimesFM 1.0/2.0, use `pip install timesfm==1.3.0`):

| Model ID | Params | Context |
|----------|--------|---------|
| `google/timesfm-2.0-500m-pytorch` | 500M | 2,048 |
| `google/timesfm-1.0-200m-pytorch` | 200M | 2,048 |

## Usage

### Loading and Compiling

The model must be loaded via `from_pretrained()` and compiled with a `ForecastConfig` before calling `forecast()`. Weights download from HuggingFace on first use and cache in `~/.cache/huggingface/`.

```python
import torch
import numpy as np
import timesfm

# Set precision on Ampere+ GPUs (A100, RTX 3090+)
torch.set_float32_matmul_precision("high")

# Load from HuggingFace
model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
    "google/timesfm-2.5-200m-pytorch"
)

# Compile with forecast configuration (required before forecast())
model.compile(
    timesfm.ForecastConfig(
        max_context=1024,
        max_horizon=256,
        normalize_inputs=True,
        use_continuous_quantile_head=True,
        force_flip_invariance=True,
        infer_is_positive=True,
        fix_quantile_crossing=True,
    )
)
```

### ForecastConfig Parameters

`ForecastConfig` controls all inference behavior:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_context` | 0 | Max historical points; 0 = model max (16,384). Must be multiple of patch size (32) |
| `max_horizon` | 0 | Max forecast steps; 0 = model max. Must be multiple of output patch size (128) |
| `normalize_inputs` | False | Z-normalize each series before inference. **Set True** for numerical stability |
| `per_core_batch_size` | 1 | Series per device per batch. Tune for memory/throughput tradeoff |
| `use_continuous_quantile_head` | False | Use 30M quantile head for better interval calibration. **Set True** for long horizons |
| `force_flip_invariance` | True | Ensures f(-x) = -f(x). **Keep True** for consistency |
| `infer_is_positive` | True | Clamp forecasts ≥ 0 when all inputs are positive. Set False for temperatures, returns |
| `fix_quantile_crossing` | False | Post-process to ensure q10 ≤ q20 ≤ ... ≤ q90. **Set True** for well-ordered quantiles |
| `return_backcast` | False | Include model's reconstruction of input. Required for XReg covariate workflows |

### Single Series Forecast

```python
# Forecast 24 steps ahead
point_forecast, quantile_forecast = model.forecast(
    horizon=24,
    inputs=[np.sin(np.linspace(0, 20, 200))],  # list of 1-D arrays
)

# point_forecast.shape  → (1, 24)    — median forecast
# quantile_forecast.shape → (1, 24, 10) — [mean, q10, q20, ..., q90]
```

### Batch Forecasting

```python
series = [
    np.random.randn(500),
    np.sin(np.linspace(0, 40, 300)),
    np.linspace(0, 1, 150) + np.random.randn(150) * 0.1,
]

point, quantiles = model.forecast(horizon=48, inputs=series)
# point.shape → (3, 48)
# quantiles.shape → (3, 48, 10)
```

### Extracting Prediction Intervals

```python
point, quantiles = model.forecast(horizon=24, inputs=[data])

# 80% prediction interval
lower_80 = quantiles[0, :, 1]  # 10th percentile
upper_80 = quantiles[0, :, 9]  # 90th percentile

# 60% prediction interval
lower_60 = quantiles[0, :, 2]  # 20th percentile
upper_60 = quantiles[0, :, 8]  # 80th percentile

# Median
median = quantiles[0, :, 5]  # same as point[0]
```

### Covariate-Aware Forecasting (XReg)

Requires `pip install timesfm[xreg]` (adds JAX + scikit-learn).

```python
# Dynamic numerical covariates: values for context + horizon
price_context_plus_horizon = np.concatenate([historical_prices, future_prices])

# Dynamic categorical covariates: e.g., day-of-week
dow_context_plus_horizon = np.array([0, 1, 2, 3, 4, 5, 6] * 100)

point, quantiles = model.forecast_with_covariates(
    inputs=[data],
    dynamic_numerical_covariates={"price": [price_context_plus_horizon]},
    dynamic_categorical_covariates={"dow": [dow_context_plus_horizon]},
    static_categorical_covariates={"region": ["east"]},
    xreg_mode="xreg + timesfm",  # or "timesfm + xreg"
)
```

Two XReg modes:
- **`"xreg + timesfm"`**: Fit linear model on targets first, then forecast residuals with TimesFM
- **`"timesfm + xreg"`**: Forecast with TimesFM first, then fit linear model on residuals

For XReg, set `return_backcast=True` in `ForecastConfig` and recompile.

### Evaluation

```python
H = 24
train, actual = data[:-H], data[-H:]
point, quantiles = model.forecast(horizon=H, inputs=[train])

mae  = np.mean(np.abs(actual - point[0]))
rmse = np.sqrt(np.mean((actual - point[0]) ** 2))
mape = np.mean(np.abs((actual - point[0]) / actual)) * 100
# 80% PI coverage
coverage = np.mean(
    (actual >= quantiles[0, :, 1]) & (actual <= quantiles[0, :, 9])
) * 100
```

## Gotchas

- **`compile()` is mandatory** — calling `forecast()` without `compile()` raises `RuntimeError`. The model must be compiled with a `ForecastConfig` before any inference.
- **`inputs` must be a list** — pass `[array]` not `array`. The `forecast()` method expects `list[np.ndarray]`, even for a single series.
- **Quantile index 0 is the mean, not q0** — `quantiles[..., 0]` is the mean prediction. Quantiles start at index 1: `quantiles[..., 1]` = q10, `quantiles[..., 9]` = q90. The median (q50) is at index 5 and equals `point_forecast`.
- **`max_context` and `max_horizon` alignment** — `max_context` must be a multiple of 32 (input patch size). `max_horizon` must be a multiple of 128 (output patch size). The compiler rounds up automatically but logs a warning.
- **`max_context + max_horizon` limit** — their sum must not exceed 16,384 (the model's context limit). For `max_context=1024`, max horizon is 15,360.
- **`infer_is_positive` behavior** — when True, if all input values are ≥ 0, forecasts are clamped to ≥ 0. Set False for data that can be negative (temperatures, financial returns, anomalies).
- **NaN handling is automatic** — leading NaNs are stripped, internal NaNs are linearly interpolated. No pre-processing needed.
- **Series longer than `max_context` are truncated** — only the last `max_context` points are used. Series shorter than `max_context` are zero-padded at the front.
- **Dynamic covariates span context + horizon** — for XReg, dynamic covariate arrays must have length `len(context) + horizon`, covering both the historical window and the forecast period.
- **`use_continuous_quantile_head` has horizon limit** — continuous quantile head only works for horizons ≤ 1,024 (the `output_quantile_len`). Longer horizons require disabling it.
- **Batch size tuning** — `per_core_batch_size` controls memory vs throughput. GPU 8 GB: use 64. GPU 16 GB: use 128. CPU 8 GB: use 8. CPU 16 GB: use 32.
- **`torch.set_float32_matmul_precision("high")` on Ampere+** — enables TF32 on A100/RTX 3090+ for faster inference without meaningful accuracy loss.
- **XReg requires `return_backcast=True`** — the `forecast_with_covariates()` method needs the backcast output. Recompile with `return_backcast=True` before calling it.
- **Archived models use different API** — TimesFM 1.0/2.0 (via `pip install timesfm==1.3.0`) use the `v1/` API with `freq` parameter. TimesFM 2.5 (2.0.1 package) does not use frequency indicators.

## References

- [01-architecture](references/01-architecture.md) — Transformer architecture, ReVIN normalization, patch-based decoding
- [02-api-reference](references/02-api-reference.md) — Full API reference for ForecastConfig, model methods, and output shapes
- [03-covariates-xreg](references/03-covariates-xreg.md) — XReg covariate forecasting, mode selection, and covariate formatting
- [04-performance-tuning](references/04-performance-tuning.md) — Batch size, memory estimation, GPU/CPU optimization, chunked inference
