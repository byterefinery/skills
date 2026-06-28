# TimesFM 2.5 Examples

## Single Series Forecast with Visualization

```python
import torch, numpy as np, pandas as pd, timesfm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

torch.set_float32_matmul_precision("high")

model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
    "google/timesfm-2.5-200m-pytorch"
)
model.compile(timesfm.ForecastConfig(
    max_context=512, max_horizon=52, normalize_inputs=True,
    use_continuous_quantile_head=True, fix_quantile_crossing=True,
))

# Load data
df = pd.read_csv("weekly_demand.csv", parse_dates=["week"])
values = df["demand"].values.astype(np.float32)

# Forecast
H = 52
point, quantiles = model.forecast(horizon=H, inputs=[values])

# Visualize
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(values[-104:], label="Historical")
x_fc = range(len(values[-104:]), len(values[-104:]) + H)
ax.plot(x_fc, point[0], label="Forecast", color="tab:orange")
ax.fill_between(x_fc, quantiles[0, :, 1], quantiles[0, :, 9],
                alpha=0.2, color="tab:orange", label="80% PI")
ax.legend()
ax.set_title("52-Week Demand Forecast")
plt.tight_layout()
plt.savefig("forecast.png", dpi=150)
```

## Batch Forecasting (Many Series)

```python
df = pd.read_csv("all_stores.csv", parse_dates=["date"], index_col="date")
inputs = [df[col].dropna().values.astype(np.float32) for col in df.columns]

point, quantiles = model.forecast(horizon=30, inputs=inputs)

import json
results = {col: {"forecast": point[i].tolist(),
                 "lower_80": quantiles[i, :, 1].tolist(),
                 "upper_80": quantiles[i, :, 9].tolist()}
           for i, col in enumerate(df.columns)}
with open("batch_forecasts.json", "w") as f:
    json.dump(results, f, indent=2)
```

## Evaluate Forecast Accuracy

```python
H = 24
train, actual = values[:-H], values[-H:]
point, quantiles = model.forecast(horizon=H, inputs=[train])
pred = point[0]

mae  = np.mean(np.abs(actual - pred))
rmse = np.sqrt(np.mean((actual - pred) ** 2))
mape = np.mean(np.abs((actual - pred) / actual)) * 100
coverage = np.mean((actual >= quantiles[0, :, 1]) & (actual <= quantiles[0, :, 9])) * 100

print(f"MAE: {mae:.2f} | RMSE: {rmse:.2f} | MAPE: {mape:.1f}% | 80% PI Coverage: {coverage:.1f}%")
```

## Anomaly Detection via Quantile Intervals

Use quantile forecasts as prediction intervals — values outside the interval are statistically unusual.

```python
# Phase 1: Forecast from training data
H = len(test_values)
point, q = model.forecast(horizon=H, inputs=[train_values])

lower_90 = q[0, :, 1]   # 10th percentile
upper_90 = q[0, :, 9]   # 90th percentile

# Phase 2: Compare actuals against intervals
anomalies_80 = (test_values < q[0, :, 2]) | (test_values > q[0, :, 8])  # outside 60%
anomalies_90 = (test_values < lower_90) | (test_values > upper_90)       # outside 80%

for i, (actual, is_anomaly_80, is_anomaly_90) in enumerate(zip(test_values, anomalies_80, anomalies_90)):
    if is_anomaly_90:
        severity = "CRITICAL"
    elif is_anomaly_80:
        severity = "WARNING"
    else:
        severity = "NORMAL"
    print(f"  Step {i}: {actual:.2f} — {severity}")
```

| Severity | Condition | Interpretation |
| -------- | --------- | -------------- |
| Normal | Inside 80% CI | Expected behavior |
| Warning | Outside 80% CI | Unusual but possible |
| Critical | Outside 90% CI | Statistically rare (< 10% probability) |

> For trending data, detrend first (e.g., rolling mean subtraction) before computing residuals.

## Covariate Forecasting

```python
import timesfm

point, quantiles = model.forecast_with_covariates(
    inputs=[demand_values],
    dynamic_numerical_covariates={
        "price": [price_context + price_future],
        "temperature": [temp_context + temp_future],
    },
    dynamic_categorical_covariates={
        "day_of_week": [dow_context + dow_future],
    },
    static_categorical_covariates={
        "region": ["north"],
    },
    xreg_mode="xreg + timesfm",
)
```

### XReg Modes

| Mode | Description |
| ---- | ----------- |
| `"xreg + timesfm"` | XReg first, then TimesFM on residuals (default) |
| `"timesfm + xreg"` | TimesFM first, then XReg on residuals |

## Chunked Processing for Large Batches

```python
CHUNK = 50
all_points, all_quantiles = [], []

for i in range(0, len(inputs), CHUNK):
    chunk = inputs[i:i+CHUNK]
    p, q = model.forecast(horizon=H, inputs=chunk)
    all_points.append(p)
    all_quantiles.append(q)

point = np.concatenate(all_points, axis=0)
quantiles = np.concatenate(all_quantiles, axis=0)
```

## Quality Checklist

Run after every TimesFM task:

- [ ] Output shapes: `point_fc` is `(n_series, horizon)`, `quant_fc` is `(n_series, horizon, 10)`
- [ ] Quantile indices: index 0 = mean, 1 = q10, 9 = q90
- [ ] No NaN in output: `np.isnan(point_fc).any()` must be False
- [ ] `matplotlib.use("Agg")` before pyplot import (headless)
- [ ] `infer_is_positive=False` for temperature, financial returns, or any negative data
