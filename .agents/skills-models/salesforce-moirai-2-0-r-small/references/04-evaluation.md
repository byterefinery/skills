# Evaluation

## Benchmarks

Moirai 2.0-R-Small is evaluated on three benchmark suites:

### GIFT-Eval

The **General Informative Time-series Forecasting Evaluation** benchmark from Salesforce. Tests across diverse domains and frequencies.

- Dataset: [Salesforce/GiftEval](https://huggingface.co/datasets/Salesforce/GiftEval)
- Leaderboard: [HuggingFace Space](https://huggingface.co/spaces/Salesforce/GIFT-Eval)
- Covers: energy, traffic, weather, healthcare, finance, and more

### Monash Forecasting Repository

The standard time series forecasting benchmark collection.

- 30+ datasets covering hourly, daily, weekly, and monthly frequencies
- Metrics: sMAPE, MASE, OWA

### Long Sequence Forecasting (LSF)

Multivariate forecasting on electricity, weather, and traffic data.

- Datasets: ETTh1, ETTh2, ETTm1, ETTm2, Electricity, Traffic, Weather
- Settings: univariate and multivariate
- Prediction horizons: 96, 192, 336, 720

### Probabilistic Forecasting (PF)

Evaluates uncertainty quantification.

- Metrics: CRPS (Continuous Ranked Probability Score), PINAW (Prediction Interval Normalized Average Width)

## Metrics

### Point Forecast Metrics

| Metric | Formula | Lower is better |
|---|---|---|
| sMAPE | Symmetric MAPE | Yes |
| MASE | Scaled MAE | Yes |
| OWA | Overall Weighted Average | Yes |
| MSE | Mean Squared Error | Yes |
| MAE | Mean Absolute Error | Yes |

### Probabilistic Metrics

| Metric | Description |
|---|---|
| CRPS | Continuous Ranked Probability Score — measures full distribution accuracy |
| PINAW | Prediction Interval Normalized Average Width — measures interval width |
| MPIW | Mean Prediction Interval Width |
| Pinball loss | Quantile-specific loss for each quantile level |

## Running Evaluation

### Via CLI

```bash
# LSF test evaluation
python -m cli.eval \
    model=moirai2_small \
    data=lsf_test \
    prediction_length=96 \
    context_length=1000

# LSF validation evaluation
python -m cli.eval \
    model=moirai2_small \
    data=lsf_val \
    prediction_length=96 \
    context_length=1000
```

### Via Python

```python
from uni2ts.eval_util.data import get_gluonts_test_dataset
from uni2ts.model.moirai2 import Moirai2Forecast, Moirai2Module

# Load dataset
test_data, metadata = get_gluonts_test_dataset(
    "electricity",
    prediction_length=None,
    regenerate=False,
)

# Load model
model = Moirai2Forecast(
    module=Moirai2Module.from_pretrained("Salesforce/moirai-2.0-R-small"),
    prediction_length=metadata.prediction_length,
    context_length=1680,
    target_dim=1,
    feat_dynamic_real_dim=0,
    past_feat_dynamic_real_dim=0,
)

predictor = model.create_predictor(batch_size=32)
forecasts = predictor.predict(test_data.input)

# Compute metrics
from gluonts.evaluation import backtest_metrics

agg_metrics, item_metrics = backtest_metrics(
    itertuple=test_data.label,
    iterator_forecasts=forecasts,
)
```

## Performance Notes

- Moirai 2.0-R-Small is the smallest variant in the Moirai 2.0 family
- For higher accuracy, consider Moirai 1.1-R-large (300M params) or Moirai-MoE
- The small model trades accuracy for efficiency: ~46 MB, fast inference on CPU
- Multi-token prediction (4 tokens at once) makes Moirai 2.0 more efficient than Moirai 1.x despite similar parameter counts
