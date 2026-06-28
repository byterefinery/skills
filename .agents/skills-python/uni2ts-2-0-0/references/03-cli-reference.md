# CLI Reference

Uni2TS provides a Hydra-based CLI for training, fine-tuning, and evaluation. All commands run from the repository root.

## Command Structure

```
python -m cli.<command> [options]
```

Commands:
- `cli.train` — training (fine-tuning or pre-training)
- `cli.eval` — evaluation with metrics

Hydra manages configuration through YAML files in `cli/conf/`. Use `-cp <config_path>` to select the config group.

## Fine-Tuning

```bash
python -m cli.train \
  -cp conf/finetune \
  exp_name=<experiment_name> \
  run_name=<run_name> \
  model=<model_config> \
  data=<data_config> \
  val_data=<val_data_config>
```

### Model Configs (`cli/conf/finetune/model/`)

| Config | Model |
|---|---|
| `moirai_1.0_R_small` | Moirai 1.0 Small |
| `moirai_1.0_R_base` | Moirai 1.0 Base |
| `moirai_1.0_R_large` | Moirai 1.0 Large |
| `moirai_1.1_R_small` | Moirai 1.1 Small |
| `moirai_1.1_R_base` | Moirai 1.1 Base |
| `moirai_1.1_R_large` | Moirai 1.1 Large |

Override individual parameters:
```bash
model.patch_size=32 \
model.context_length=1000 \
model.prediction_length=96
```

### Data Configs (`cli/conf/finetune/data/`)

Predefined configs for LSF datasets: `etth1`, `etth2`, `ettm1`, `ettm2`.

Override parameters:
```bash
data.patch_size=32 \
data.context_length=1000 \
data.prediction_length=96 \
data.mode=S
```

`data.mode`: `S` for sample-level (univariate), `I` for instance-level (multivariate).

### Validation Data (`cli/conf/finetune/val_data/`)

Same structure as training data configs. Used for validation during fine-tuning.

### Full Fine-Tuning Example

```bash
python -m cli.train \
  -cp conf/finetune \
  exp_name=lsf_finetune \
  run_name=etth1_moirai_small \
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

## Evaluation

```bash
python -m cli.eval \
  run_name=<run_name> \
  model=<model_config> \
  data=<data_config>
```

### Model Configs (`cli/conf/eval/model/`)

Same as fine-tuning, plus:
- `moirai_moe_1.0_R_small` — Moirai-MoE Small
- `moirai_moe_1.0_R_base` — Moirai-MoE Base
- `moirai_lightning_ckpt` — Load from Lightning checkpoint

### Data Configs (`cli/conf/eval/data/`)

| Config | Dataset | Description |
|---|---|---|
| `etth1_test` | ETTh1 test | Custom test split |
| `etth1_val` | ETTh1 val | Custom val split |
| `gluonts_test` | GluonTS test | GluonTS benchmark |
| `gluonts_val` | GluonTS val | GluonTS benchmark |
| `lsf_test` | LSF test | Long Sequence Forecasting |
| `lsf_val` | LSF val | Long Sequence Forecasting |
| `monash` | Monash | Monash forecasting benchmark |

### LSF Evaluation

Requires the [TSLib](https://github.com/thuml/Time-Series-Library) dataset:

```bash
echo "LSF_PATH=/path/to/tslib/dataset" >> .env

python -m cli.eval \
  run_name=lsf_etth1 \
  model=moirai_1.1_R_small \
  model.patch_size=32 \
  model.context_length=1000 \
  data=lsf_test \
  data.dataset_name=ETTh1 \
  data.prediction_length=96
```

### Evaluation Metrics

Configured in `cli/conf/eval/default.yaml`. Default metrics include:
- `MSE` — Mean Squared Error (median quantile)
- `MASE` — Mean Absolute Scaled Error
- `CRPS` — Continuous Ranked Probability Score
- `sMAPE` — Symmetric Mean Absolute Percentage Error

Results are printed as a DataFrame and logged to TensorBoard.

### Auto OOM Handling

The evaluation CLI automatically reduces batch size on CUDA OOM:
```
OutOfMemoryError at batch_size 32, reducing to 16
```
It continues halving until `min_batch_size` is reached.

## Pre-Training

```bash
python -m cli.train \
  -cp conf/pretrain \
  run_name=<run_name> \
  model=<model_config> \
  data=<data_config>
```

### Model Configs (`cli/conf/pretrain/model/`)

| Config | Model |
|---|---|
| `moirai_small` | Small (36M) |
| `moirai_base` | Base (94M) |
| `moirai_large` | Large (305M) |

### Data Configs (`cli/conf/pretrain/data/`)

| Config | Dataset |
|---|---|
| `lotsa_v1_unweighted` | LOTSA v1 (uniform weights) |
| `lotsa_v1_weighted` | LOTSA v1 (length-proportional weights) |
| `buildings_900k` | Buildings 900K |
| `buildings_bench` | Buildings Benchmark |
| `cmip6` | Climate model data |
| `era5` | ERA5 weather data |
| `gluonts` | GluonTS datasets |
| `largest` | Largest dataset |
| `lib_city` | LibCity traffic data |
| `subseasonal` | Subseasonal forecasting |
| `cloudops_tsf` | CloudOps time series |
| `proenfo` | ProEnFo energy data |
| `others` | Miscellaneous datasets |

### Pre-Training Example

```bash
echo "LOTSA_V1_PATH=/path/to/lotsa" >> .env

python -m cli.train \
  -cp conf/pretrain \
  run_name=moirai_pretrain \
  model=moirai_small \
  data=lotsa_v1_unweighted
```

## Hydra Configuration

Uni2TS uses Hydra 1.3 for configuration management. Key concepts:

- **Config groups** — `-cp conf/finetune` sets the config path
- **Overrides** — `key=value` on command line overrides YAML defaults
- **Composition** — multiple config files are merged (e.g., `model=moirai_1.1_R_small` merges the model config)
- **Output** — logs and checkpoints saved to `outputs/<exp_name>/<run_name>/`

### Common Overrides

```bash
# Training
trainer.gpus=4 \
trainer.max_epochs=100 \
trainer.gradient_clip_val=1.0 \
optimizer.lr=1e-4 \
trainer.batch_size=32

# Model
model.patch_size=16 \
model.context_length=512 \
model.prediction_length=48

# Data
data.context_length=512 \
data.prediction_length=48 \
data.patch_size=16 \
data.mode=S
```

## Data Preparation CLI

```bash
python -m uni2ts.data.builder.simple <dataset_name> <csv_path> [options]
```

Options:
- `--dataset_type wide|long|wide_multivariate` — input format
- `--date_offset 'YYYY-MM-DD HH:MM:SS'` — train split end date
- `--offset <int>` — train split end row
- `--normalize` — standardize with training statistics
- `--freq <str>` — explicit frequency (e.g., `H`, `D`)

Output saved to `CUSTOM_DATA_PATH` (from `.env`).
