# Moirai 2.0-R-Small API Reference

## Moirai2Module

Core transformer module. Load from HuggingFace Hub.

```python
from uni2ts.model.moirai2 import Moirai2Module

module = Moirai2Module.from_pretrained("Salesforce/moirai-2.0-R-small")
```

### Constructor

```python
Moirai2Module(
    d_model: int = 384,           # hidden dimension
    d_ff: int = 1024,             # feed-forward dimension
    num_layers: int = 6,          # transformer layers
    patch_size: int = 16,         # patch size (fixed for 2.0)
    max_seq_len: int = 512,       # max token sequence length
    attn_dropout_p: float = 0.0,  # attention dropout (forced to 0 in Forecast)
    dropout_p: float = 0.0,       # dropout (forced to 0 in Forecast)
    scaling: bool = True,         # auto-standardization
    num_predict_token: int = 4,   # multi-token prediction count
    quantile_levels: tuple = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9),
)
```

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `d_model` | `int` | Hidden dimension (384) |
| `num_layers` | `int` | Number of transformer layers (6) |
| `patch_size` | `int` | Patch size (16) |
| `num_predict_token` | `int` | Tokens predicted at once (4) |
| `max_seq_len` | `int` | Max sequence length (512) |
| `scaling` | `bool` | Whether auto-scaling is enabled |
| `quantile_levels` | `tuple[float]` | Quantile levels |
| `num_quantiles` | `int` | Number of quantile levels (9) |

### Forward

```python
module(
    target,               # Float[*batch, seq_len, patch]
    observed_mask,        # Bool[*batch, seq_len, patch]
    sample_id,            # Int[*batch, seq_len]
    time_id,              # Int[*batch, seq_len]
    variate_id,           # Int[*batch, seq_len]
    prediction_mask,      # Bool[*batch, seq_len]
    training_mode=True,   # bool
)
```

Returns raw predictions. Not called directly — use `Moirai2Forecast` instead.

---

## Moirai2Forecast

Wrapper that handles data transformation and produces GluonTS forecasts.

### Constructor

```python
Moirai2Forecast(
    module=Moirai2Module.from_pretrained("Salesforce/moirai-2.0-R-small"),
    prediction_length: int,              # forecast horizon
    context_length: int,                 # lookback window
    target_dim: int = 1,                 # number of target dimensions (1 for univariate)
    feat_dynamic_real_dim: int = 0,      # future covariates (always 0 for 2.0)
    past_feat_dynamic_real_dim: int = 0, # past covariates (always 0 for 2.0)
)
```

**Required parameters**: `prediction_length`, `context_length`.

**Not available** (vs Moirai 1.x):
- No `patch_size` parameter — fixed at 16
- No `num_samples` parameter — uses quantile loss, not sampling

### create_predictor

```python
predictor = model.create_predictor(
    batch_size: int = 32,    # inference batch size
    device: str = "auto",    # "auto", "cuda", "cpu"
)
```

Returns a `PyTorchPredictor` (GluonTS). Use `predictor.predict(dataset)` to forecast.

### predict

Direct prediction from numpy arrays, bypassing the GluonTS predictor:

```python
import numpy as np

forecasts = model.predict(
    past_target: List[np.ndarray],           # list of 1D arrays, shape (context_length,)
    feat_dynamic_real: None,                 # not supported
    past_feat_dynamic_real: None,            # not supported
)
# Returns: np.ndarray, shape (batch, num_quantiles, prediction_length)
```

Each element of `past_target` is a 1D numpy array. Shorter arrays are left-padded. Internal NaNs are imputed with causal mean. Return shape: `(batch_size, 9, prediction_length)` — index 4 is the median (0.5 quantile).

### hparams_context

Context manager for temporarily changing prediction parameters:

```python
with model.hparams_context(prediction_length=48, context_length=500):
    predictor = model.create_predictor(batch_size=32)
    forecasts = predictor.predict(dataset)
```

### Properties

| Property | Type | Description |
|---|---|---|
| `past_length` | `int` | Same as `context_length` |
| `prediction_input_names` | `list[str]` | Input keys expected by the predictor |
| `training_input_names` | `list[str]` | Input keys for training |

---

## GluonTS Forecast Object

Each forecast from `predictor.predict()` is a GluonTS `QuantileForecast`:

```python
forecast = next(iter(forecasts))

forecast.mean              # np.ndarray, shape (prediction_length,)
forecast.quantile(0.5)     # np.ndarray, shape (prediction_length,)
forecast.quantile(0.1)     # np.ndarray, shape (prediction_length,)
forecast.quantile(0.9)     # np.ndarray, shape (prediction_length,)
forecast.start_date        # pandas Timestamp
forecast.item_id           # str or None
```

Available quantiles: 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9.

---

## GluonTS Datasets

### PandasDataset (wide format)

```python
from gluonts.dataset.pandas import PandasDataset

df = pd.read_csv("data.csv", index_col=0, parse_dates=True)
ds = PandasDataset(dict(df))
```

Each column becomes a separate time series.

### PandasDataset (long format)

```python
df = pd.read_csv("data.csv", parse_dates=["timestamp"])
ds = PandasDataset.from_long_dataframe(
    df,
    target="value",
    item_id="series_id",
)
```

### ListDataset

```python
from gluonts.dataset.common import ListDataset

dataset = ListDataset(
    [{"target": np.array([1.0, 2.0, 3.0])}],
    freq="H",
)
```

---

## Dataset Splitting

```python
from gluonts.dataset.split import split

train, test_template = split(ds, offset=-100)  # last 100 steps as test

# Rolling window evaluation
test_data = test_template.generate_instances(
    prediction_length=24,
    windows=100 // 24,
    distance=24,  # non-overlapping
)
```

`test_data.input` and `test_data.label` are iterators over context and ground truth.

---

## Visualization

```python
from uni2ts.eval_util.plot import plot_single, plot_next_multi

# Single series
plot_single(
    inp,              # dict with "target", "start"
    label,            # dict with "target", "start"
    forecast,         # GluonTS forecast
    context_length=200,
    intervals=(0.5, 0.9),
    name="pred",
    show_label=True,
)

# Multiple series
plot_next_multi(
    axes,             # matplotlib axes array
    input_it,         # iterator over inputs
    label_it,         # iterator over labels
    forecast_it,      # iterator over forecasts
    context_length=200,
    intervals=(0.5, 0.9),
    dim=None,
    name="pred",
    show_label=True,
)
```
