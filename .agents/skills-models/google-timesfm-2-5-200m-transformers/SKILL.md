---
name: google-timesfm-2-5-200m-transformers
description: >
  Forecast time series with Google's TimesFM-2.5 200M decoder-only transformer via
  HuggingFace transformers (TimesFm2_5ModelForPrediction). Patch-based input encoding,
  point and quantile forecasts, context length 1024, max horizon 512. Zero-shot
  univariate forecasting on arbitrary time series. Use when the user needs pretrained
  time series forecasting with the TimesFM model family through the transformers library,
  or when they reference google/timesfm-2.5-200m-transformers.
metadata:
  tags:
    - ml
    - deep-learning
    - time-series
    - forecasting
    - foundation-model
    - transformers
---

# google-timesfm-2-5-200m-transformers

## Overview

TimesFM-2.5 is a pretrained decoder-only transformer for time series forecasting from Google Research. The `google/timesfm-2.5-200m-transformers` checkpoint is the HuggingFace transformers-compatible port of the official PyTorch release. Load with `TimesFm2_5ModelForPrediction` from the `transformers` library.

Requires `torch` and `transformers` (4.x). Install with `pip install torch transformers`.

### Model Details

- **Architecture**: Decoder-only transformer, 200M parameters, patch-based input encoding
- **Context length**: 1024 (max `forecast_context_len`)
- **Horizon**: up to 512 steps (controlled by `forecast_horizon`)
- **Outputs**: Point forecasts (mean predictions) and full quantile forecasts
- **Training data**: GIFT-Eval Pretrain, Wikimedia Pageviews (cutoff Nov 2023), Google Trends (cutoff EoY 2022), synthetic and augmented data
- **License**: Apache-2.0
- **Paper**: [A decoder-only foundation model for time-series forecasting](https://arxiv.org/abs/2310.10688) (ICML 2024)

Related checkpoints:
- `google/timesfm-2.5-200m-pytorch` — original PyTorch checkpoint (use with `timesfm` package)
- `google/timesfm-1-0-200m-transformers` — previous TimesFM 1.0 release

## Usage

### Loading the Model

```python
import torch
from transformers import TimesFm2_5ModelForPrediction

model = TimesFm2_5ModelForPrediction.from_pretrained(
    "google/timesfm-2.5-200m-transformers",
)
model = model.to(torch.float32).eval()
```

Always cast to `torch.float32` — the model expects float32 inputs and may produce NaNs with lower precision.

### Forecasting

Pass a list of 1-D tensors as `past_values`. Each tensor is one time series. Variable-length inputs are supported:

```python
past_values = [
    torch.linspace(0, 1, 100),       # series 1: 100 steps
    torch.sin(torch.linspace(0, 20, 67)),  # series 2: 67 steps
]

with torch.no_grad():
    outputs = model(
        past_values=past_values,
        forecast_context_len=1024,
        forecast_horizon=12,
    )

# Point forecasts: (batch_size, forecast_horizon)
print(outputs.mean_predictions.shape)  # (2, 12)

# Full quantile forecasts: (batch_size, forecast_horizon, n_quantiles)
print(outputs.full_predictions.shape)  # (2, 12, 11)
```

The quantile output contains the mean plus quantile levels (typically 10th through 90th percentiles in 10% increments, giving 11 values total).

### Key Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `past_values` | `List[torch.Tensor]` | required | List of 1-D tensors, one per series |
| `forecast_context_len` | `int` | 512 | Context window length (max 1024) |
| `forecast_horizon` | `int` | 128 | Prediction horizon (max 512) |

Use `forecast_context_len=1024` to leverage the full context capacity. The model pads shorter series internally.

### GPU Inference

```python
model = TimesFm2_5ModelForPrediction.from_pretrained(
    "google/timesfm-2.5-200m-transformers",
).to("cuda")
model = model.to(torch.float32).eval()
```

Move the model to CUDA before casting dtype to avoid unnecessary memory copies.

### Batch Forecasting

```python
# Generate synthetic batch
batch = [torch.randn(200) for _ in range(32)]

with torch.no_grad():
    outputs = model(
        past_values=batch,
        forecast_context_len=1024,
        forecast_horizon=24,
    )

mean_forecasts = outputs.mean_predictions    # (32, 24)
quantile_forecasts = outputs.full_predictions  # (32, 24, 11)
```

### Using with pandas

```python
import pandas as pd

df = pd.read_csv("data.csv")  # columns: timestamp, value, item_id

# Group by item_id and forecast each series
results = []
for item_id, group in df.groupby("item_id"):
    series = torch.tensor(group["value"].values, dtype=torch.float32)
    with torch.no_grad():
        out = model(past_values=[series], forecast_context_len=1024, forecast_horizon=24)
    results.append({
        "item_id": item_id,
        "mean_forecast": out.mean_predictions[0].tolist(),
        "quantile_forecast": out.full_predictions[0].tolist(),
    })
```

### Comparison with Original PyTorch Checkpoint

The transformers port (`google/timesfm-2.5-200m-transformers`) and the original PyTorch checkpoint (`google/timesfm-2.5-200m-pytorch`) produce equivalent forecasts. Weight conversion parity is verified against the official implementation.

Use the transformers port when:
- You already depend on `transformers` and want to avoid the separate `timesfm` package
- You need integration with the HuggingFace ecosystem (tokenizers, pipelines, model cards)
- You want a simpler API without the `ForecastConfig` boilerplate

Use the original PyTorch checkpoint when:
- You need `torch.compile` optimization (the original supports `model.compile()`)
- You need the `timesfm` package's higher-level utilities (normalization, quantile head config)

## Gotchas

- **Always use float32** — the model expects `torch.float32`. Using `float16` or `bfloat16` produces NaN outputs silently. Cast with `model.to(torch.float32)`.
- **`past_values` must be a list of 1-D tensors** — not a single 2-D tensor. Each element is one series. Variable lengths are fine.
- **`forecast_context_len` controls padding** — if a series is shorter than `forecast_context_len`, it is left-padded. If longer, it is truncated from the start. Set this to 1024 to use the full context window.
- **No built-in normalization** — unlike the original `timesfm` package which has `normalize_inputs=True`, the transformers port does not auto-normalize. Normalize your data before passing to the model if needed.
- **No `torch.compile` support** — the transformers port does not expose the `model.compile()` method available in the original PyTorch implementation. Use the original checkpoint if compile-time optimization is needed.
- **Quantile output shape** — `full_predictions` has shape `(batch, horizon, n_quantiles)` where `n_quantiles` includes the mean. The first column is the mean; remaining columns are quantile levels from 10th to 90th percentile.
- **Model downloads on first use** — the checkpoint is ~400MB (float32 safetensors). First load triggers download; consider caching explicitly in production.
- **Single univariate series per input** — the model forecasts one series at a time. For multivariate forecasting, run separate predictions per variable or use a model designed for multivariate inputs (e.g., Chronos-2).

## References

- [01-model-architecture](references/01-model-architecture.md) — Decoder-only transformer design, patch-based encoding, quantile head
- [02-api-reference](references/02-api-reference.md) — Full parameter reference, output types, device placement patterns
- [03-original-pytorch-api](references/03-original-pytorch-api.md) — Comparison with the original timesfm package API, migration guide
