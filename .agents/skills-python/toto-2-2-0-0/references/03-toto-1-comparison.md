# Toto 1.0 vs 2.0 — Comparison and Migration

## Key Differences

| Feature | Toto 1.0 | Toto 2.0 |
|---|---|---|
| **Architecture** | Proportional Factorized Space-Time Attention | Alternating time/variate attention |
| **Scaling** | Single 151M model | u-μP-scaled family (4m → 2.5B) |
| **Probabilistic output** | Student-T mixture (sample-based) | Quantile head (direct 9 quantiles) |
| **Fine-tuning** | ✅ Supported with EV support | ❌ Not yet available |
| **Exogenous variables** | ✅ Supported | ❌ Not yet available |
| **Installation** | `pip install toto-ts` | `pip install "toto-2 @ git+..."` |
| **Package** | `toto` | `toto2` |
| **API** | `TotoForecaster` + `MaskedTimeseries` | `Toto2Model.forecast()` |

## When to Use Toto 1.0

Use Toto 1.0 (`pip install toto-ts`) if you need:
- **Fine-tuning** on domain-specific datasets
- **Exogenous variable (EV) support** — known future covariates
- **Sample-based probabilistic forecasting** via Student-T mixture

## When to Use Toto 2.0

Use Toto 2.0 if you need:
- **Zero-shot forecasting** — no fine-tuning required
- **Multiple model sizes** — choose compute/accuracy tradeoff
- **Direct quantile outputs** — no sampling overhead
- **State-of-the-art benchmark scores** — top on GIFT-Eval and BOOM
- **Flash Attention support** — faster inference on gap-free data

## API Migration (1.0 → 2.0)

### Loading

```python
# Toto 1.0
from toto.model.toto import Toto
from toto.inference.forecaster import TotoForecaster
toto = Toto.from_pretrained('Datadog/Toto-Open-Base-1.0')
forecaster = TotoForecaster(toto.model)

# Toto 2.0
from toto2 import Toto2Model
model = Toto2Model.from_pretrained("Datadog/Toto-2.0-22m")
model = model.to("cuda").eval()
```

### Forecasting

```python
# Toto 1.0
from toto.data.util.dataset import MaskedTimeseries
inputs = MaskedTimeseries(
    series=input_series,
    padding_mask=torch.full_like(input_series, True, dtype=torch.bool),
    id_mask=torch.zeros_like(input_series),
    timestamp_seconds=timestamp_seconds,
    time_interval_seconds=time_interval_seconds,
)
forecast = forecaster.forecast(inputs, prediction_length=336, num_samples=256)
median = forecast.median

# Toto 2.0
target = torch.randn(1, n_variates, context_len, device=device)
target_mask = torch.ones_like(target, dtype=torch.bool)
series_ids = torch.zeros(1, n_variates, dtype=torch.long, device=device)
quantiles = model.forecast(
    {"target": target, "target_mask": target_mask, "series_ids": series_ids},
    horizon=336,
    decode_block_size=768,
    has_missing_values=False,
)
median = quantiles[4]  # 0.5 quantile at index 4
```

### Output Differences

- **Toto 1.0**: Returns `Forecast` object with `.median`, `.samples`, `.quantile(p)` methods
- **Toto 2.0**: Returns raw tensor of shape `(9, batch, n_variates, horizon)` with fixed quantile levels

## Toto 1.0 Model

| Checkpoint | Parameters |
|---|---|
| `Datadog/Toto-Open-Base-1.0` | 151M |
