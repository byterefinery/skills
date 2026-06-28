---
name: salesforce-moirai-2-0-r-small
description: >
  Salesforce Moirai 2.0-R-Small — ~12M-parameter decoder-only universal time series
  forecasting transformer. Zero-shot probabilistic forecasts with quantile outputs
  on any univariate series. Uses quantile loss, multi-token prediction, and patch-level
  masking for improved accuracy and robustness over Moirai 1.x. ~46 MB model, runs on
  CPU or GPU. Requires the uni2ts library (from source or PyPI). Use when the user needs
  lightweight zero-shot time series forecasting, quantile-based probabilistic predictions,
  or a compact model that fits in under 1 GB RAM.
metadata:
  tags:
    - ml
    - deep-learning
    - time-series
    - forecasting
    - foundation-model
    - probabilistic
    - salesforce
---

# salesforce-moirai-2-0-r-small

## Overview

Moirai 2.0-R-Small is a ~12M-parameter decoder-only transformer for zero-shot time series forecasting. It produces multi-step-ahead quantile forecasts (0.1–0.9) on any univariate series — sales, sensor data, weather, vitals, prices — without fine-tuning.

Key capabilities:
- **Zero-shot forecasting** — works on any univariate time series, no training needed
- **Probabilistic outputs** — 9 quantile levels (0.1, 0.2, …, 0.9) for uncertainty estimates
- **Multi-token prediction** — predicts 4 tokens at once, improving efficiency and stability
- **Patch-level masking** — random mask during inference improves robustness
- **Missing value aware** — patch token embeddings encode NaN information
- **Compact** — ~46 MB model, ~1 GB RAM on CPU, ~0.5 GB VRAM on GPU
- **Flexible context** — any context length, any prediction horizon

Key improvements over Moirai 1.x:
- Quantile loss instead of distributional loss
- Multi-token prediction instead of single-token
- Data filtering to remove non-forecastable series during pretraining
- Missing value information in patch embeddings
- Patch-level random mask for inference robustness

Install via `pip install uni2ts` or build from the [uni2ts GitHub repo](https://github.com/SalesforceAIResearch/uni2ts). Load with `Moirai2Module.from_pretrained("Salesforce/moirai-2.0-R-small")`.

### Model Details

| Property | Value |
|---|---|
| Parameters | ~12M |
| Architecture | Decoder-only transformer, 6 layers, d_model=384, d_ff=1024 |
| Max sequence length | 512 tokens |
| Patch size | 16 |
| Prediction tokens | 4 (multi-token) |
| Quantile levels | [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9] |
| Scaling | Yes (auto-normalization) |
| License | CC BY-NC 4.0 (non-commercial only) |
| Model size | 45.6 MB |
| Paper | [Moirai 2.0: When Less Is More](https://arxiv.org/abs/2511.11698) |

Moirai 2.0 family has only the `small` variant. For larger models, use Moirai 1.1 (small/base/large) or Moirai-MoE.

## Usage

### Installation

```bash
# PyPI (recommended)
pip install uni2ts

# Or from source (for latest features)
git clone https://github.com/SalesforceAIResearch/uni2ts.git
cd uni2ts
pip install -e '.[notebook]'
touch .env
```

### Minimal Example

```python
import torch
import pandas as pd
from gluonts.dataset.pandas import PandasDataset
from gluonts.dataset.split import split

from uni2ts.model.moirai2 import Moirai2Forecast, Moirai2Module

PDT = 24   # prediction length
CTX = 200  # context length
BSZ = 32   # batch size

# Load data
df = pd.read_csv("data.csv", index_col=0, parse_dates=True)
ds = PandasDataset(dict(df))

# Split
train, test_template = split(ds, offset=-PDT)
test_data = test_template.generate_instances(
    prediction_length=PDT,
    windows=1,
    distance=PDT,
)

# Load model
model = Moirai2Forecast(
    module=Moirai2Module.from_pretrained("Salesforce/moirai-2.0-R-small"),
    prediction_length=PDT,
    context_length=CTX,
    target_dim=1,
    feat_dynamic_real_dim=0,
    past_feat_dynamic_real_dim=0,
)

predictor = model.create_predictor(batch_size=BSZ)
forecasts = predictor.predict(test_data.input)

# Get forecast
forecast = next(iter(forecasts))
print(forecast.mean)  # point forecast (array)
```

### From a NumPy Array

```python
import numpy as np
from gluonts.dataset.common import ListDataset

from uni2ts.model.moirai2 import Moirai2Forecast, Moirai2Module

model = Moirai2Forecast(
    module=Moirai2Module.from_pretrained("Salesforce/moirai-2.0-R-small"),
    prediction_length=24,
    context_length=200,
    target_dim=1,
    feat_dynamic_real_dim=0,
    past_feat_dynamic_real_dim=0,
)
predictor = model.create_predictor(batch_size=32)

# Single series
series = np.random.randn(500).astype(np.float32)
dataset = ListDataset([{"target": series}], freq="H")
forecasts = list(predictor.predict(dataset))
print(forecasts[0].mean)
```

### Batch Forecasting

```python
from gluonts.dataset.common import ListDataset

# Multiple series
series_list = [
    np.random.randn(300).astype(np.float32),
    np.random.randn(500).astype(np.float32),
    np.random.randn(400).astype(np.float32),
]

dataset = ListDataset(
    [{"target": s} for s in series_list],
    freq="H",
)

forecasts = list(predictor.predict(dataset))
for i, fc in enumerate(forecasts):
    print(f"Series {i}: mean={fc.mean[:5]}")
```

### Quantile Forecasts

```python
forecast = next(iter(forecasts))

# Mean (point forecast)
print(forecast.mean)

# Quantile access
print(forecast.quantile(0.5))  # median
print(forecast.quantile(0.1))  # 10th percentile
print(forecast.quantile(0.9))  # 90th percentile

# All quantiles
for q in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    print(f"q{q}: {forecast.quantile(q)[:5]}")
```

### Rolling Window Evaluation

```python
from gluonts.dataset.split import split

# Use last 200 steps as evaluation window
train, test_template = split(ds, offset=-200)

# Generate rolling windows (non-overlapping)
test_data = test_template.generate_instances(
    prediction_length=24,
    windows=200 // 24,
    distance=24,
)

forecasts = list(predictor.predict(test_data.input))
```

### Visualization

```python
import matplotlib.pyplot as plt
from uni2ts.eval_util.plot import plot_single

input_it = iter(test_data.input)
label_it = iter(test_data.label)
forecast_it = iter(forecasts)

inp = next(input_it)
label = next(label_it)
forecast = next(forecast_it)

plot_single(
    inp,
    label,
    forecast,
    context_length=200,
    intervals=(0.5, 0.9),
    name="pred",
    show_label=True,
)
plt.show()
```

### GPU Inference

```python
predictor = model.create_predictor(
    batch_size=32,
    device=torch.device("cuda"),
)
```

## Gotchas

- **CC BY-NC 4.0 license** — this model is non-commercial only. Do not use in production commercial products. For commercial use, contact Salesforce or use the proprietary version.
- **No covariate support** — Moirai 2.0-R-Small does not accept dynamic or past covariates. Set `feat_dynamic_real_dim=0` and `past_feat_dynamic_real_dim=0`. For covariate-aware forecasting, use Moirai 1.1 instead.
- **`Moirai2Forecast` not `MoiraiForecast`** — Moirai 2.0 uses `Moirai2Forecast`/`Moirai2Module`, not the `MoiraiForecast`/`MoiraiModule` classes from 1.x. Using the wrong class will fail.
- **No `num_samples` parameter** — Moirai 2.0 uses quantile loss, not distributional sampling. Do not pass `num_samples` to `Moirai2Forecast` (it has no such parameter).
- **No `patch_size` parameter** — Moirai 2.0 uses a fixed patch size of 16. Do not pass `patch_size` to `Moirai2Forecast` (it has no such parameter).
- **`forecast.mean` returns an array** — not a scalar. It is the mean forecast over the prediction horizon.
- **GluonTS dataset required** — Moirai 2.0 inference goes through GluonTS's predictor interface. Data must be wrapped in a GluonTS dataset (`PandasDataset`, `ListDataset`, etc.).
- **`target_dim=1` only** — this is a univariate model. Set `target_dim=1` even if your DataFrame has multiple columns (forecast one at a time).
- **`uni2ts` from source requires `.env`** — when installing from source, create an empty `.env` file or the library may fail on import.
- **Only small variant exists** — Moirai 2.0 only has the `small` size. There is no `base` or `large` variant in the 2.0 family.
- **Context length flexibility** — unlike some models with fixed context, Moirai 2.0 accepts any positive integer for `context_length`. Use 200–1000 for most use cases.

## References

- [01-api-reference](references/01-api-reference.md) — Full API: Moirai2Forecast, Moirai2Module, predictor, GluonTS dataset formats
- [02-data-preparation](references/02-data-preparation.md) — Input formats, PandasDataset, ListDataset, rolling window evaluation, frequency handling
- [03-fine-tuning](references/03-fine-tuning.md) — Fine-tuning on custom datasets, data preparation, Hydra config, LSF benchmark examples
- [04-evaluation](references/04-evaluation.md) — GIFT-Eval benchmark, Monash/LSF/PF benchmarks, evaluation metrics, leaderboard
