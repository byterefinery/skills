# GluonTS Integration

## Overview

`Toto2GluonTSModel` wraps `Toto2Model` as a standard GluonTS predictor. This provides automatic data transforms, instance splitting, batched inference, and forecast formatting.

## Basic Setup

```python
import torch
from toto2 import Toto2Model, Toto2GluonTSModel, Toto2GluonTSModelConfig

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load base model
model = Toto2Model.from_pretrained("Datadog/Toto-2.0-2.5B")
model = model.to(device).eval()

# Wrap for GluonTS
gts_config = Toto2GluonTSModelConfig(
    prediction_length=96,
    context_length=512,
    target_dim=1,
    imputation_internal="ffill",
)

gts_model = Toto2GluonTSModel(model, gts_config).to(device).eval()
predictor = gts_model.create_predictor(batch_size=64, device=device)
```

## Predicting on Built-in Datasets

```python
from gluonts.dataset.repository import get_dataset
from gluonts.dataset.split import split

# Load dataset
dataset = get_dataset("airpassengers")
pred_len = dataset.metadata.prediction_length

# Split
_, test_template = split(dataset.test, offset=-pred_len)
test_data = test_template.generate_instances(prediction_length=pred_len, windows=1)

# Predict
forecasts = list(predictor.predict(test_data.input))

# Access results
fc = forecasts[0]
print(fc.mean)          # Point forecast (array)
print(fc.quantile(0.5)) # Median
print(fc.quantile(0.1)) # 10th percentile
print(fc.quantile(0.9)) # 90th percentile
```

## Evaluating with GluonTS Metrics

```python
from gluonts.model import evaluate_model
from gluonts.ev.metrics import (
    MAE, MASE, MSE, RMSE, SMAPE,
    MeanWeightedSumQuantileLoss,
)
from gluonts.time_feature import get_seasonality

metrics = [
    MSE(forecast_type="mean"),
    MAE(),
    MASE(),
    SMAPE(),
    RMSE(forecast_type="mean"),
    MeanWeightedSumQuantileLoss(
        quantile_levels=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
    ),
]

results = evaluate_model(
    predictor,
    test_data=test_data,
    metrics=metrics,
    axis=None,
    mask_invalid_label=True,
    allow_nan_forecast=False,
    seasonality=get_seasonality(dataset.metadata.freq),
)

for key, val in results.items():
    print(f"{key}: {val.iloc[0]:.4f}")
```

## Multivariate Setup

For multivariate forecasting, set `target_dim=2`:

```python
gts_config = Toto2GluonTSModelConfig(
    prediction_length=96,
    context_length=512,
    target_dim=2,  # Multivariate
    imputation_internal="ffill",
)
```

## Imputation Methods

Three internal imputation strategies:

| Method | Description |
|---|---|
| `"ffill"` | Forward-fill NaN gaps (default). Leading NaNs left as 0 (masked). |
| `"linear"` | Linear interpolation. Trailing NaNs forward-filled, leading left as 0. |
| `"none"` | Replace NaN with 0. No interpolation. |

## Rolling Window Evaluation

```python
from gluonts.dataset.split import split

# Generate multiple non-overlapping windows
train, test_template = split(dataset.test, offset=-200)
test_data = test_template.generate_instances(
    prediction_length=24,
    windows=200 // 24,
    distance=24,
)

forecasts = list(predictor.predict(test_data.input))
```

## Visualization

```python
import matplotlib.pyplot as plt
from gluonts.dataset.split import split

# Get test data
_, test_template = split(dataset.test, offset=-pred_len)
test_data = test_template.generate_instances(prediction_length=pred_len, windows=1)

forecasts = list(predictor.predict(test_data.input))

# Plot
entry = list(dataset.test)[0]
full_target = entry["target"]
fc = forecasts[0]

fig, ax = plt.subplots(figsize=(12, 4))
ctx_len = min(4 * pred_len, len(full_target) - pred_len)
ctx = full_target[-(ctx_len + pred_len):-pred_len]
ax.plot(range(len(ctx)), ctx, color="black", label="Context")
ax.plot(range(len(ctx), len(ctx) + pred_len), full_target[-pred_len:],
        color="gray", ls="--", label="Ground truth")
x = range(len(ctx), len(ctx) + pred_len)
ax.plot(x, fc.quantile(0.5), color="tab:blue", label="Median")
ax.fill_between(x, fc.quantile(0.1), fc.quantile(0.9),
                 alpha=0.2, color="tab:blue", label="80% interval")
ax.legend()
plt.tight_layout()
plt.show()
```

## Multiple Series Datasets

For datasets with many series (e.g., electricity with 321 series):

```python
dataset = get_dataset("electricity")
pred_len = dataset.metadata.prediction_length

gts_config = Toto2GluonTSModelConfig(
    prediction_length=pred_len,
    context_length=512,
    target_dim=1,
)

gts_model = Toto2GluonTSModel(model, gts_config).to(device).eval()
predictor = gts_model.create_predictor(batch_size=32, device=device)

_, test_template = split(dataset.test, offset=-pred_len)
test_data = test_template.generate_instances(prediction_length=pred_len, windows=1)

forecasts = list(predictor.predict(test_data.input))
```

## Configuration Tuning

| Parameter | Effect |
|---|---|
| `batch_size` | Larger = faster throughput, more memory. Tune per hardware. |
| `context_length` | Longer context = more historical information. Default 512. |
| `prediction_length` | Must match the dataset's expected horizon. |
| `decode_block_size` | Set for long horizons (≳1000). `None` for single pass. |
| `has_missing_values` | Set `False` if data is fully observed for Flash Attention speedup. |
| `imputation_internal` | Choose based on data characteristics. `"ffill"` works well for most. |
| `scaler_fallback_min_obs` | Set to 8+ for sparse data with many leading missing values. |
| `quantile_real_cap_k` | Set to 10.0+ for production stability against extreme outliers. |
