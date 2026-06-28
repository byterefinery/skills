# Toto 1.0 vs 2.0 Comparison

## When to Use Each

| Feature | Toto 1.0 | Toto 2.0 |
|---|---|---|
| Zero-shot forecasting | ✅ | ✅ |
| Multivariate support | ✅ | ✅ |
| Fine-tuning | ✅ | ❌ (planned) |
| Exogenous variables | ✅ | ❌ (planned) |
| Probabilistic outputs | Student-T mixture | Quantile head (0.1–0.9) |
| Attention mechanism | Proportional Factorized Space-Time | Alternating time/variate |
| Parallel decoding | ❌ | ✅ (CPM) |
| Model sizes | 151M only | 4m, 22m, 313m, 1B, 2.5B |
| Package | `toto-ts` | `toto-models` |
| Python | 3.10+ | 3.12+ |

**Use Toto 1.0 if you need fine-tuning or exogenous covariate support.**

**Use Toto 2.0 for zero-shot forecasting** — it achieves higher accuracy across all benchmarks.

## Architecture Differences

### Toto 1.0
- 151M parameters, single checkpoint
- Proportional Factorized Space-Time Attention (PFSTA)
- Student-T mixture output for probabilistic forecasting
- Uses `TotoForecaster` wrapper with `MaskedTimeseries` inputs
- Supports `num_samples` for probabilistic sampling
- Input shape: `(channels, time_steps)` — variate-first

### Toto 2.0
- 4m to 2.5B parameters, five checkpoints
- Alternating time-axis (causal) and variate-axis (full) attention
- Quantile output head with 9 fixed levels (0.1–0.9)
- Direct `model.forecast()` call with dict inputs
- No sampling — deterministic quantile predictions
- Input shape: `(batch, n_var, time)` — batch-first

## API Comparison

### Toto 1.0 Inference

```python
from toto.data.util.dataset import MaskedTimeseries
from toto.inference.forecaster import TotoForecaster
from toto.model.toto import Toto

toto = Toto.from_pretrained('Datadog/Toto-Open-Base-1.0')
toto.to('cuda')
toto.compile()  # Optional JIT compilation

forecaster = TotoForecaster(toto.model)

# Input shape: (channels, time_steps)
input_series = torch.randn(7, 4096).to('cuda')

inputs = MaskedTimeseries(
    series=input_series,
    padding_mask=torch.full_like(input_series, True, dtype=torch.bool),
    id_mask=torch.zeros_like(input_series),
    timestamp_seconds=torch.zeros(7, 4096).to('cuda'),
    time_interval_seconds=torch.full((7,), 60*15).to('cuda'),
)

forecast = forecaster.forecast(
    inputs,
    prediction_length=336,
    num_samples=256,
    samples_per_batch=256,
)

median = forecast.median
samples = forecast.samples
q10 = forecast.quantile(0.1)
q90 = forecast.quantile(0.9)
```

### Toto 2.0 Inference

```python
from toto2 import Toto2Model

model = Toto2Model.from_pretrained("Datadog/Toto-2.0-2.5B")
model = model.to("cuda").eval()

# Input shape: (batch, n_var, time)
target = torch.randn(1, 7, 512, device="cuda")
target_mask = torch.ones_like(target, dtype=torch.bool)
series_ids = torch.zeros(1, 7, dtype=torch.long, device="cuda")

quantiles = model.forecast(
    {"target": target, "target_mask": target_mask, "series_ids": series_ids},
    horizon=336,
)

# Shape: (9, batch, n_var, horizon)
median = quantiles[4]  # 0.5 quantile
q10 = quantiles[0]     # 0.1 quantile
q90 = quantiles[8]     # 0.9 quantile
```

## Key Migration Points

### Input Shape
- **1.0**: `(channels, time_steps)` — variate-first, no batch dimension
- **2.0**: `(batch, n_var, time)` — batch-first, explicit batch dimension

### Probabilistic Outputs
- **1.0**: Student-T mixture with configurable `num_samples`. Access via `forecast.quantile(q)` or `forecast.samples`.
- **2.0**: Fixed 9 quantile levels. Access via index: `quantiles[4]` for median, `quantiles[0]` for q10.

### Missing Values
- **1.0**: `padding_mask` in `MaskedTimeseries`
- **2.0**: `target_mask` in the inputs dict

### Covariates
- **1.0**: Supported via `MaskedTimeseries` fields (`timestamp_seconds`, `time_interval_seconds`) and exogenous variable support in fine-tuning
- **2.0**: Not supported in current release. Code paths exist for `known_dynamic` but are not functional.

### Fine-Tuning
- **1.0**: Full fine-tuning pipeline with exogenous variable support. Use `TotoForecaster` and LightningDataModule.
- **2.0**: Not available yet. Planned for future release.

## Package and Dependencies

| | Toto 1.0 | Toto 2.0 |
|---|---|---|
| Package | `pip install toto-ts` | `pip install toto-models` |
| Python | 3.10+ | 3.12+ |
| PyTorch | 2.5+ | 2.5+ |
| Import | `from toto.model.toto import Toto` | `from toto2 import Toto2Model` |
| Optional deps | `xformers`, `flash-attention` | Auto-installed via `toto-models` |

## Benchmark Comparison

Toto 2.0 dominates Toto 1.0 on all benchmarks:

| Benchmark | Toto 1.0 (CRPS) | Toto 2.0-2.5B (CRPS) | Improvement |
|---|---|---|---|
| BOOM | ~0.370 | 0.349 | -5.7% |
| GIFT-Eval | ~0.500 | 0.476 | -4.8% |
| TIME | N/A | 0.532 | New benchmark |

Even Toto 2.0-22m (84 MB) matches or beats Toto 1.0 (151M) while using ~7× fewer parameters.
