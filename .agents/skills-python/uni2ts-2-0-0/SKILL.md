---
name: uni2ts-2-0-0
description: >
  Uni2TS 2.0.0 — Salesforce's PyTorch library for unified training and inference of
  Universal Time Series Transformers. Provides the Moirai family of pretrained
  foundation models (Moirai 1.0/1.1, Moirai-MoE, Moirai-2.0) for zero-shot and
  fine-tuned probabilistic time series forecasting. Patch-based transformer
  architecture with quantile predictions, GluonTS-backed data pipeline, Hydra CLI
  for training/evaluation, and HuggingFace Hub integration. Use when the user needs
  pretrained time series foundation models, masked-forecasting pre-training,
  fine-tuning Moirai models on custom datasets, or running benchmark evaluations
  (Monash, LSF, PF) with standardized metrics.
metadata:
  tags:
    - ml
    - deep-learning
    - time-series
    - forecasting
    - foundation-model
    - probabilistic
    - transformer
---

# uni2ts 2.0.0

## Overview

Uni2TS is a PyTorch library for research and applications in time series forecasting, built on a unified framework for pre-training, fine-tuning, inference, and evaluation of Universal Time Series Transformers. Install with `pip install uni2ts` (requires Python 3.10+, PyTorch 2.1–2.4).

The library provides three model families under the Moirai brand:

- **Moirai 1.0/1.1** (`MoiraiForecast`/`MoiraiModule`) — original universal time series transformer with masked-forecasting pre-training objective. Sizes: small (36M), base (94M), large (305M). Supports automatic and fixed patch sizes, configurable context/prediction lengths, and multivariate forecasting via dimension masking.
- **Moirai-MoE** (`MoiraiMoEForecast`/`MoiraiMoEModule`) — sparse mixture-of-experts variant. Sizes: small, base. Uses fixed patch size 16.
- **Moirai-2.0** (`Moirai2Forecast`/`Moirai2Module`) — latest generation. Fixed `prediction_length=100`, `context_length=1680`. Quantile-based (no sampling). Only univariate forecasting currently supported.

All models produce quantile forecasts (levels: 0.1–0.9) and load from HuggingFace Hub via `from_pretrained()`.

### Architecture

All Moirai models share a common design:
- **Patch-based encoding** — time series are split into patches, each projected to d_model via a ResidualBlock
- **Transformer encoder** — multi-head self-attention with rotary positional embeddings (time) and binary attention bias (variate)
- **Masked forecasting** — during pre-training, random patches are masked and the model predicts them autoregressively
- **Standardization** — per-series standardization via `PackedStdScaler` (configurable)
- **Quantile output** — the decoder outputs quantile predictions directly (Moirai-2.0) or via distribution parameters (Moirai 1.x)

### Pre-trained Models on HuggingFace Hub

| Model | Family | Size | Patch | Notes |
|---|---|---|---|---|
| `Salesforce/moirai-1.0-R-small` | Moirai 1.0 | 36M | auto/8/16/32/64/128 | Original release |
| `Salesforce/moirai-1.0-R-base` | Moirai 1.0 | 94M | auto/8/16/32/64/128 | Original release |
| `Salesforce/moirai-1.0-R-large` | Moirai 1.0 | 305M | auto/8/16/32/64/128 | Original release |
| `Salesforce/moirai-1.1-R-small` | Moirai 1.1 | 36M | auto/8/16/32/64/128 | Improved weights |
| `Salesforce/moirai-1.1-R-base` | Moirai 1.1 | 94M | auto/8/16/32/64/128 | Improved weights |
| `Salesforce/moirai-1.1-R-large` | Moirai 1.1 | 305M | auto/8/16/32/64/128 | Improved weights |
| `Salesforce/moirai-moe-1.0-R-small` | Moirai-MoE | — | 16 (fixed) | Mixture of experts |
| `Salesforce/moirai-moe-1.0-R-base` | Moirai-MoE | — | 16 (fixed) | Mixture of experts |
| `Salesforce/moirai-2.0-R-small` | Moirai-2.0 | — | — | Latest, fixed 100-step horizon |

## Usage

### Zero-Shot Forecasting

The standard pattern: load data as a GluonTS dataset, construct the model, create a predictor, and generate forecasts.

```python
import torch
import pandas as pd
from gluonts.dataset.pandas import PandasDataset
from gluonts.dataset.split import split
from uni2ts.model.moirai import MoiraiForecast, MoiraiModule

PDT = 20   # prediction length
CTX = 200  # context length
PSZ = "auto"  # patch size: "auto" or int {8, 16, 32, 64, 128}

# Load data — wide DataFrame (columns = series, index = timestamps)
url = "https://gist.githubusercontent.com/rsnirwan/c8c8654a98350fadd229b00167174ec4/raw/a42101c7786d4bc7695228a0f2c8cea41340e18f/ts_wide.csv"
df = pd.read_csv(url, index_col=0, parse_dates=True)
ds = PandasDataset(dict(df))

# Split into train/test
train, test_template = split(ds, offset=-100)
test_data = test_template.generate_instances(
    prediction_length=PDT,
    windows=5,
    distance=PDT,
)

# Load pretrained model
model = MoiraiForecast(
    module=MoiraiModule.from_pretrained("Salesforce/moirai-1.1-R-small"),
    prediction_length=PDT,
    context_length=CTX,
    patch_size=PSZ,
    num_samples=100,
    target_dim=1,
    feat_dynamic_real_dim=ds.num_feat_dynamic_real,
    past_feat_dynamic_real_dim=ds.num_past_feat_dynamic_real,
)

# Create predictor and forecast
predictor = model.create_predictor(batch_size=32)
forecasts = predictor.predict(test_data.input)
```

### Moirai-2.0 Forecasting

Moirai-2.0 uses fixed context (1680) and prediction (100) lengths. It does not use patch size or sampling — it outputs quantiles directly.

```python
from uni2ts.model.moirai2 import Moirai2Forecast, Moirai2Module

model = Moirai2Forecast(
    module=Moirai2Module.from_pretrained("Salesforce/moirai-2.0-R-small"),
    prediction_length=100,
    context_length=1680,
    target_dim=1,
    feat_dynamic_real_dim=0,
    past_feat_dynamic_real_dim=0,
)

predictor = model.create_predictor(batch_size=32)
forecasts = predictor.predict(test_data.input)
```

### Moirai-MoE Forecasting

Moirai-MoE uses a fixed patch size of 16.

```python
from uni2ts.model.moirai_moe import MoiraiMoEForecast, MoiraiMoEModule

model = MoiraiMoEForecast(
    module=MoiraiMoEModule.from_pretrained("Salesforce/moirai-moe-1.0-R-small"),
    prediction_length=PDT,
    context_length=CTX,
    patch_size=16,
    num_samples=100,
    target_dim=1,
    feat_dynamic_real_dim=ds.num_feat_dynamic_real,
    past_feat_dynamic_real_dim=ds.num_past_feat_dynamic_real,
)

predictor = model.create_predictor(batch_size=32)
forecasts = predictor.predict(test_data.input)
```

### Plotting Forecasts

```python
import matplotlib.pyplot as plt
from uni2ts.eval_util.plot import plot_single

inp = next(iter(test_data.input))
label = next(iter(test_data.label))
forecast = next(iter(forecasts))

plot_single(inp, label, forecast, context_length=CTX, name="pred", show_label=True)
plt.show()
```

### Data Preparation

Convert a CSV to the Uni2TS dataset format (HuggingFace datasets library):

```bash
# Set output directory
echo "CUSTOM_DATA_PATH=/path/to/save" >> .env

# Wide format (each column = one series)
python -m uni2ts.data.builder.simple ETTh1 dataset/ETT-small/ETTh1.csv --dataset_type wide

# With train/val split by date
python -m uni2ts.data.builder.simple ETTh1 dataset/ETT-small/ETTh1.csv \
    --date_offset '2017-10-23 23:00:00'

# With normalization (mean/std from training set)
python -m uni2ts.data.builder.simple ETTh1 dataset/ETT-small/ETTh1.csv \
    --date_offset '2017-10-23 23:00:00' --normalize
```

Dataset types: `wide` (each column = series), `long` (item_id column), `wide_multivariate` (all columns as multivariate). The validation split is saved as `DATASET_NAME_eval`.

### Fine-Tuning

Fine-tune a pretrained model using the Hydra CLI:

```bash
python -m cli.train \
  -cp conf/finetune \
  exp_name=example_lsf \
  run_name=example_run \
  model=moirai_1.1_R_small \
  model.patch_size=32 \
  model.context_length=1000 \
  model.prediction_length=96 \
  data=etth1 \
  data.patch_size=32 \
  data.context_length=1000 \
  data.prediction_length=96 \
  data.mode=S \
  val_data=etth1 \
  val_data.patch_size=32 \
  val_data.context_length=1000 \
  val_data.prediction_length=96 \
  val_data.mode=S
```

The `data.mode` controls the forecasting setup: `S` for univariate (sample-level), `I` for instance-level (multivariate). Config files live in `cli/conf/finetune/` and `cli/conf/finetune/data/`.

### Evaluation

Run evaluation with metrics (MSE, MASE, CRPS, etc.):

```bash
# Evaluate on a custom test dataset
python -m cli.eval \
  run_name=example_eval \
  model=moirai_1.1_R_small \
  model.patch_size=32 \
  model.context_length=1000 \
  data=etth1_test

# Evaluate on LSF benchmark (requires TSLib dataset)
echo "LSF_PATH=/path/to/tslib/dataset" >> .env

python -m cli.eval \
  run_name=example_eval \
  model=moirai_1.1_R_small \
  model.patch_size=32 \
  model.context_length=1000 \
  data=lsf_test \
  data.dataset_name=ETTh1 \
  data.prediction_length=96
```

Config files in `cli/conf/eval/` and `cli/conf/eval/data/`. Supported benchmark datasets: Monash, LSF (Long Sequence Forecasting), PF (Probabilistic Forecasting), GluonTS.

### Pre-Training

Pre-train a model from scratch using LOTSA data:

```bash
# Download LOTSA data
huggingface-cli download Salesforce/lotsa_data --repo-type=dataset --local-dir /path/to/lotsa

echo "LOTSA_V1_PATH=/path/to/lotsa" >> .env

# Start pre-training
python -m cli.train \
  -cp conf/pretrain \
  run_name=first_run \
  model=moirai_small \
  data=lotsa_v1_unweighted
```

Config files in `cli/conf/pretrain/`. The pre-training objective is masked forecasting — the model learns to predict masked patches of the input sequence.

### Direct Prediction (No GluonTS)

For quick inference on raw arrays without the GluonTS pipeline, use the `predict()` method directly:

```python
import numpy as np
from uni2ts.model.moirai2 import Moirai2Forecast, Moirai2Module

model = Moirai2Forecast(
    module=Moirai2Module.from_pretrained("Salesforce/moirai-2.0-R-small"),
    prediction_length=100,
    context_length=1680,
    target_dim=1,
    feat_dynamic_real_dim=0,
    past_feat_dynamic_real_dim=0,
)

# Predict from a list of numpy arrays
series = [np.random.randn(500), np.random.randn(800)]
predictions = model.predict(past_target=series)
# Shape: (batch, num_quantiles, prediction_length)
```

The `predict()` method handles NaN imputation (causal mean), padding/slicing to context length, and returns quantile predictions.

## Gotchas

- **Moirai-2.0 has fixed lengths** — `prediction_length=100` and `context_length=1680` are hardcoded. Unlike Moirai 1.x, you cannot change these. The model also only supports univariate forecasting (`target_dim=1`, `feat_dynamic_real_dim=0`).
- **Moirai-MoE uses fixed patch size 16** — do not pass other patch sizes. The MoE variant does not support the `patch_size` parameter variation that Moirai 1.x does.
- **`patch_size="auto"` is Moirai 1.x only** — Moirai 1.x accepts `"auto"` or integers `{8, 16, 32, 64, 128}`. Moirai-MoE is always 16. Moirai-2.0 does not expose patch size.
- **`num_samples` applies to Moirai 1.x and MoE only** — Moirai 1.x uses distribution-based sampling for probabilistic forecasts. Moirai-2.0 outputs quantiles directly with no sampling step.
- **GluonTS dataset required for `create_predictor()`** — the predictor wraps GluonTS's `PyTorchPredictor` and expects GluonTS dataset inputs. For raw array inference, use `model.predict()` directly.
- **`.env` file required for CLI** — the CLI reads environment variables from `.env` (e.g., `CUSTOM_DATA_PATH`, `LOTSA_V1_PATH`, `LSF_PATH`). Create it with `touch .env` before running CLI commands.
- **`data.mode` must match dataset type** — use `S` (sample/univariate) for wide-format data where each column is a separate series. Use `I` (instance/multivariate) when treating all columns as one multivariate series.
- **CLI runs from repo root** — `python -m cli.train` and `python -m cli.eval` must be run from the uni2ts repository root directory where `cli/` and `conf/` are accessible.
- **Auto-batch-size reduction on OOM** — the evaluation CLI automatically halves batch size on CUDA OOM errors down to `min_batch_size`. Fine-tuning does not have this safety net — set batch size conservatively.
- **Moirai-2.0 `predict()` only supports univariate** — passing multivariate data or covariates (`feat_dynamic_real`, `past_feat_dynamic_real`) will not work correctly. The implementation explicitly notes "only support univariate forecast now".
- **Patch size affects token length** — larger patch sizes reduce sequence length (more tokens → more memory). The auto mode selects patch size based on context length to keep token count reasonable.
- **`from_pretrained()` downloads on first use** — model weights are cached in the HuggingFace hub cache directory. Subsequent loads are fast. Ensure `huggingface_hub` is installed.

## References

- [01-model-architecture](references/01-model-architecture.md) — Patch-based transformer design, masked forecasting objective, MoE routing, quantile output head
- [02-data-pipeline](references/02-data-pipeline.md) — GluonTS dataset formats, Uni2TS transforms, data builders, indexers, and loaders
- [03-cli-reference](references/03-cli-reference.md) — Full CLI reference for training, fine-tuning, evaluation, and pre-training with Hydra configs
- [04-benchmarks](references/04-benchmarks.md) — Monash, LSF, PF benchmark setups, evaluation metrics, and comparison protocols
