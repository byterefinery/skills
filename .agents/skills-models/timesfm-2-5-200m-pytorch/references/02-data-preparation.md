# Data Preparation for TimesFM

## Input Format

TimesFM accepts a **list of 1-D numpy arrays**. Each array represents one univariate time series.

```python
inputs = [
    np.array([1.0, 2.0, 3.0, 4.0, 5.0]),       # Series 1
    np.array([10.0, 20.0, 15.0, 25.0]),          # Series 2 (different length OK)
    np.array([100.0, 110.0, 105.0, 115.0, 120.0, 130.0]),  # Series 3
]
```

### Key Properties

- **Variable lengths**: Series in the same batch can have different lengths
- **Float values**: Use `np.float32` or `np.float64`
- **1-D only**: Each array must be 1-dimensional
- **Minimum length**: At least 32 data points required

## Loading from Common Formats

### CSV — Single Series (Long Format)

```python
import pandas as pd, numpy as np

df = pd.read_csv("data.csv", parse_dates=["date"])
values = df["value"].values.astype(np.float32)
inputs = [values]
```

### CSV — Multiple Series (Wide Format)

```python
df = pd.read_csv("data.csv", parse_dates=["date"], index_col="date")
inputs = [df[col].dropna().values.astype(np.float32) for col in df.columns]
```

### CSV — Long Format with ID Column

```python
df = pd.read_csv("data.csv", parse_dates=["date"])
inputs = []
for series_id, group in df.groupby("series_id"):
    values = group.sort_values("date")["value"].values.astype(np.float32)
    inputs.append(values)
```

### Pandas DataFrame

```python
# Single column
inputs = [df["temperature"].values.astype(np.float32)]

# Multiple columns
inputs = [df[col].dropna().values.astype(np.float32) for col in numeric_cols]
```

### Numpy Arrays

```python
# 2-D array (rows = series, cols = time steps)
data = np.load("timeseries.npy")  # shape (N, T)
inputs = [data[i] for i in range(data.shape[0])]
```

### Excel

```python
df = pd.read_excel("data.xlsx", sheet_name="Sheet1")
inputs = [df[col].dropna().values.astype(np.float32)
          for col in df.select_dtypes(include=[np.number]).columns]
```

### Parquet

```python
df = pd.read_parquet("data.parquet")
inputs = [df[col].dropna().values.astype(np.float32)
          for col in df.select_dtypes(include=[np.number]).columns]
```

### JSON

```python
import json

with open("data.json") as f:
    data = json.load(f)

# Assumes {"series_name": [values...], ...}
inputs = [np.array(values, dtype=np.float32) for values in data.values()]
```

## NaN Handling

TimesFM handles NaN values automatically with these rules:

### Leading NaNs — Stripped

```python
# Input:  [NaN, NaN, 1.0, 2.0, 3.0]
# Actual: [1.0, 2.0, 3.0]
```

### Internal NaNs — Linearly Interpolated

```python
# Input:  [1.0, NaN, 3.0, NaN, NaN, 6.0]
# Actual: [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
```

### Trailing NaNs — Not Handled

Drop them before passing to the model:

```python
values = df["value"].values.astype(np.float32)
# Remove trailing NaNs
while len(values) > 0 and np.isnan(values[-1]):
    values = values[:-1]
inputs = [values]
```

## Context Length Selection

Choose `max_context` based on your data frequency and available history:

| Data Frequency | Recommended Context | Covers |
| -------------- | ------------------- | ------ |
| Hourly | 512–1024 | ~3–7 days |
| Daily | 256–512 | ~10–20 months |
| Weekly | 128–256 | ~2–5 years |
| Monthly | 64–128 | ~5–10 years |
| Yearly | 32–64 | ~3–5 decades |

Larger context gives the model more history but uses more memory. The model supports up to 16,384 context points.

## Covariate Data Preparation

### Dynamic Numerical Covariates

Must span both context and forecast periods:

```python
# If context = 100 points and horizon = 24:
# covariate must have 124 values
covariate = np.concatenate([
    historical_covariate[-100:],   # context window
    future_covariate[:24],          # forecast window
])
```

### Dynamic Categorical Covariates

Encode as integers or strings:

```python
day_of_week = [d.weekday() for d in context_dates + forecast_dates]
```

### Static Categorical Covariates

One value per series:

```python
static_covariates = {
    "region": ["east", "west", "central"],
    "store_type": ["mall", "standalone", "mall"],
}
```

## Normalization

`normalize_inputs=True` in `ForecastConfig` handles normalization internally. Do not pre-normalize your data — the model expects raw values and applies its own normalization.
