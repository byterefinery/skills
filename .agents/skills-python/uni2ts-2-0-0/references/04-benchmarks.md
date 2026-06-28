# Benchmarks

Uni2TS provides evaluation code for three major benchmark suites. The evaluation follows a standardized protocol using GluonTS's evaluation framework.

## Monash Forecasting Benchmark

The [Monash Forecasting Benchmark](https://forecastingdatabook.com/) covers 30+ datasets spanning daily, hourly, weekly, and other frequencies. It is the most widely-used benchmark for time series forecasting.

### Running Evaluation

```bash
python -m cli.eval \
  run_name=monash_eval \
  model=moirai_1.1_R_small \
  model.patch_size=32 \
  model.context_length=1000 \
  data=monash
```

The Monash config (`cli/conf/eval/data/monash.yaml`) handles all datasets automatically. Results are aggregated across datasets.

### Key Metrics

- **sMAPE** — primary metric for Monash
- **MASE** — scaled error metric
- **OWA** — Overall Weighted Average (combines sMAPE and MASE)

## Long Sequence Forecasting (LSF)

The [LSF benchmark](https://github.com/thuml/Time-Series-Library) focuses on long-horizon forecasting with datasets from electricity, traffic, weather, and energy domains.

### Setup

1. Clone TSLib and download datasets
2. Set environment variable:
```bash
echo "LSF_PATH=/path/to/tslib/dataset" >> .env
```

### Running Evaluation

```bash
python -m cli.eval \
  run_name=lsf_eval \
  model=moirai_1.1_R_small \
  model.patch_size=32 \
  model.context_length=1000 \
  data=lsf_test \
  data.dataset_name=ETTh1 \
  data.prediction_length=96
```

### Datasets

| Dataset | Domain | Frequency | Points |
|---|---|---|---|
| ETTh1 | Electricity | Hourly | ~6900 |
| ETTh2 | Electricity | Hourly | ~6900 |
| ETTm1 | Electricity | 15-min | ~27000 |
| ETTm2 | Electricity | 15-min | ~27000 |
| Electricity | Power | Hourly | ~26000 |
| Traffic | Traffic | Hourly | ~17000 |
| Weather | Weather | 10-min | ~70000 |
| ExchangeRate | Finance | Daily | ~7000 |

### Prediction Lengths

LSF uses four standard prediction lengths: 96, 192, 336, 720.

## Probabilistic Forecasting (PF)

The PF benchmark evaluates probabilistic (quantile) forecasting capabilities.

### Running Evaluation

Use the appropriate data config from `cli/conf/eval/data/`. PF datasets require the GluonTS test split format.

## GIFT-Eval

[GIFT-Eval](https://github.com/SalesforceAIResearch/gift-eval) is the General time series InForecasting and TRansformer Evaluation benchmark. It provides a standardized evaluation framework for foundation models.

- [Leaderboard](https://huggingface.co/spaces/Salesforce/GIFT-Eval)
- Covers multiple domains and forecasting tasks
- Designed specifically for evaluating universal time series models

## Evaluation Metrics

### Point Forecasting Metrics

| Metric | Formula | Interpretation |
|---|---|---|
| MSE | Mean of squared errors | Penalizes large errors |
| MAE | Mean of absolute errors | Robust to outliers |
| sMAPE | Symmetric MAPE | Scale-independent |
| MASE | Mean absolute scaled error | Compared to naive forecast |

### Probabilistic Metrics

| Metric | Description |
|---|---|
| CRPS | Continuous Ranked Probability Score — proper scoring rule for full distributions |
| Quantile loss | Pinball loss at specific quantile levels |
| Log likelihood | Negative log-likelihood under assumed distribution |

### Metric Configuration

Metrics are configured in `cli/conf/eval/default.yaml` using GluonTS's metric definitions:

```python
from uni2ts.eval_util.metrics import MedianMSE

# Custom metric definition
@dataclass
class MedianMSE(BaseMetricDefinition):
    forecast_type: str = "0.5"

    def __call__(self, axis=None):
        return DirectMetric(
            name=f"MSE[{self.forecast_type}]",
            stat=partial(squared_error, forecast_type=self.forecast_type),
            aggregate=Mean(axis=axis),
        )
```

## Comparison with Other Models

Uni2TS provides evaluation code for competing models:
- **TimesFM** — Google's time series foundation model
- **Chronos** — Amazon's tokenization-based model
- **VisionTS** — Vision transformer approach

Evaluation code is in `project/benchmarks/`. This allows fair comparison using identical data splits and metrics.

## Best Practices

- **Use consistent context/prediction lengths** across models for fair comparison
- **Run multiple seeds** and report mean ± std for robust results
- **Match patch size to context length** — larger contexts benefit from larger patches
- **Validate on held-out data** before benchmark evaluation
- **Use the same data preprocessing** (normalization, frequency handling) across all models
