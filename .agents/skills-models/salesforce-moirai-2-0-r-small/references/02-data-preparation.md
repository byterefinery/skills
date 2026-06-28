# Data Preparation

## Input Formats

Moirai 2.0 works through GluonTS datasets. All data must be wrapped in one of GluonTS's dataset types before passing to the predictor.

### Wide DataFrame (multiple columns = multiple series)

```python
import pandas as pd
from gluonts.dataset.pandas import PandasDataset

df = pd.read_csv("data.csv", index_col=0, parse_dates=True)
# Columns: col_a, col_b, col_c
ds = PandasDataset(dict(df))
```

Each column is treated as a separate univariate series.

### Long DataFrame (item_id + value column)

```python
df = pd.read_csv("data.csv", parse_dates=["timestamp"])
# Columns: timestamp, item_id, value

ds = PandasDataset.from_long_dataframe(
    df,
    target="value",
    item_id="item_id",
)
```

### ListDataset (manual)

```python
from gluonts.dataset.common import ListDataset
import numpy as np

dataset = ListDataset(
    [
        {"target": np.array([1.0, 2.0, 3.0, 4.0]), "start": pd.Timestamp("2024-01-01", freq="H")},
        {"target": np.array([5.0, 6.0, 7.0, 8.0]), "start": pd.Timestamp("2024-01-01", freq="H")},
    ],
    freq="H",
)
```

### NumPy Array (direct prediction)

For quick inference without GluonTS datasets, use `model.predict()`:

```python
import numpy as np

past_target = [np.array([1.0, 2.0, 3.0, ...]).astype(np.float32)]
forecasts = model.predict(past_target)
# Shape: (batch, num_quantiles, prediction_length)
```

## NaN Handling

Moirai 2.0 handles missing values internally:

- **Trailing NaNs** — dropped automatically via `past_observed_target` mask
- **Internal NaNs** — imputed with causal mean (forward-filling with mean of observed values)
- **Leading NaNs** — context is left-padded with the first valid value; `past_is_pad` marks padded regions

The model's patch token embedding encodes missing value information, so it is aware of which values are observed vs. imputed.

## Frequency Handling

Moirai 2.0 is frequency-agnostic — it does not require specifying a frequency. The model handles any regular time series regardless of granularity (seconds, minutes, hours, days, etc.).

For GluonTS datasets, set `freq` appropriately:

```python
# Common frequencies
freq = "H"   # hourly
freq = "D"   # daily
freq = "W"   # weekly
freq = "MS"  # month start
freq = "T"   # minutely
```

## Context Length Selection

The `context_length` parameter controls how many historical points the model sees. Any positive integer is valid.

| Use case | Recommended context |
|---|---|
| Short-term (hours) | 200–500 |
| Daily seasonality | 200–500 (covers ~1–3 weeks of hourly data) |
| Weekly seasonality | 500–1680 (covers ~2–4 weeks of hourly data) |
| Monthly seasonality | 1680–5000 |
| Long-term trends | 1000–5000 |

The model's max token sequence length is 512 tokens. With a patch size of 16, this means the theoretical max context is ~8192 points (512 × 16). In practice, use 200–2000 for most applications.

## Prediction Length Selection

`prediction_length` is the forecast horizon. Any positive integer is valid.

- Short horizons (1–24) are generally more accurate
- Longer horizons (>100) use autoregressive unrolling internally
- The model predicts 4 tokens at a time, so horizons that are multiples of 4 are slightly more efficient

## Rolling Window Evaluation

For proper evaluation, use rolling windows rather than a single split:

```python
from gluonts.dataset.split import split

# Use last N steps as evaluation window
train, test_template = split(ds, offset=-500)

# Non-overlapping windows
test_data = test_template.generate_instances(
    prediction_length=24,
    windows=500 // 24,
    distance=24,  # step between windows
)

# Overlapping windows (more evaluations, more correlated)
test_data = test_template.generate_instances(
    prediction_length=24,
    windows=500 // 12,
    distance=12,  # half the prediction length = 50% overlap
)
```

## Batch Size Tuning

| Hardware | Recommended batch size |
|---|---|
| CPU only | 16–32 |
| Consumer GPU (4–8 GB) | 32–64 |
| Datacenter GPU (16–24 GB) | 64–128 |
| Multiple GPUs | 128+ (scales with devices) |

Larger batch sizes improve throughput but increase memory usage.

## Data Normalization

Moirai 2.0 applies internal auto-standardization (scaling). Do not pre-normalize your data — the model handles it.

## Saving and Loading Models

```python
# Save
module.save_pretrained("./moirai-2.0-saved")

# Load from local
from uni2ts.model.moirai2 import Moirai2Module

module = Moirai2Module.from_pretrained("./moirai-2.0-saved")
```
