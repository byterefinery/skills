# Fine-Tuning

## Overview

Fine-tune Moirai 2.0-R-Small on custom datasets using the uni2ts CLI with Hydra configuration. The process involves:

1. Prepare data into HuggingFace dataset format
2. Configure fine-tuning with Hydra
3. Run training via CLI
4. Evaluate the fine-tuned checkpoint

## Dataset Preparation

### Using the Simple Builder

```bash
# Add save path to .env
echo "CUSTOM_DATA_PATH=./datasets" >> .env

# Wide format (single series per column)
python -m uni2ts.data.builder.simple my_dataset ./data/my_data.csv --dataset_type wide

# With train/val split by date
python -m uni2ts.data.builder.simple my_dataset ./data/my_data.csv \
    --dataset_type wide \
    --date_offset '2023-01-01 00:00:00'

# With train/val split by offset (last N rows as validation)
python -m uni2ts.data.builder.simple my_dataset ./data/my_data.csv \
    --dataset_type wide \
    --offset 1000

# With normalization (using training statistics)
python -m uni2ts.data.builder.simple my_dataset ./data/my_data.csv \
    --dataset_type wide \
    --normalize \
    --date_offset '2023-01-01 00:00:00'
```

Dataset types:
- `wide` — each column is a separate univariate series
- `long` — item_id + value columns
- `wide_multivariate` — all columns treated as one multivariate series

### LSF Dataset Builder

For Long Sequence Forecasting benchmarks, use the provided script:

```bash
bash project/moirai-1/finetune_lsf/build_lsf_ft_datasets.sh
```

This creates sliding-window datasets with fixed-length samples. Key points:
- Uses `distance=1` (every possible window) by default
- For large datasets, increase `distance` to reduce samples per epoch
- LSF setup requires normalization with training statistics

## Hydra Configuration

Fine-tuning uses Hydra config files under `cli/conf/finetune/`.

### Default Config

```yaml
# cli/conf/finetune/default.yaml
exp_name: moirai2_ft
run_name: run1
seed: 0
tf32: true
compile: false

trainer:
  max_epochs: 200
  precision: 32
  gradient_clip_val: 1.0
  gradient_clip_algorithm: norm
  callbacks:
    - ModelCheckpoint (monitors val/PackedNLLLoss, save_top_k=1)
    - EarlyStopping (patience=3)

train_dataloader:
  batch_size: 512
  cycle: false       # loop over all samples per epoch
  shuffle: true
  num_workers: 11

val_dataloader:
  batch_size: 128
  shuffle: false
```

### Model Config

Create `cli/conf/finetune/model/moirai2_small.yaml`:

```yaml
_target_: uni2ts.model.moirai2.Moirai2Forecast
_partial_: true
_prediction_length_: ???
_context_length_: ???
_target_dim_: 1
_feat_dynamic_real_dim_: 0
_past_feat_dynamic_real_dim_: 0
module_kwargs:
  _target_: uni2ts.model.moirai2.Moirai2Module.from_pretrained
  pretrained_name: Salesforce/moirai-2.0-R-small
finetune_pattern: full    # full, head_only, freeze_ffn
lr: 5.0e-7
```

Fine-tuning patterns:
- `full` — update all parameters (lr ~5e-7)
- `head_only` — linear probing, only output head (lr ~1e-4 to 1e-3)
- `freeze_ffn` — freeze feed-forward layers, update attention only

### Data Config

Create `cli/conf/finetune/data/my_dataset.yaml`:

```yaml
_target_: uni2ts.data.indexer.HuggingFaceDatasetIndexer
dataset_path: ./datasets/my_dataset
mode: S          # S=univariate, M=multivariate
context_length: 1000
prediction_length: 24
```

## Running Fine-Tuning

```bash
python -m cli.finetune \
    exp_name=moirai2_ft \
    run_name=exp1 \
    model=moirai2_small \
    data=my_dataset \
    val_data=my_dataset \
    trainer.max_epochs=50 \
    train_dataloader.batch_size=256
```

Outputs go to `outputs/finetune/<exp_name>/<model>/<finetune_pattern>/<data>/<run_name>/`.

## Key Hyperparameters

| Parameter | Default | Notes |
|---|---|---|
| Learning rate | 5e-7 | Use 1e-4–1e-3 for head_only |
| Batch size | 512 | Larger for univariate (mode=S) |
| Max epochs | 200 | With early stopping (patience=3) |
| Gradient clip | 1.0 | Norm-based clipping |
| Precision | 32 | Use 16-mixed for faster training on Ampere+ GPUs |

## Evaluation After Fine-Tuning

```bash
# Update checkpoint path in eval config
python -m cli.eval \
    model=moirai2_small \
    data=lsf_test \
    ckpt_path=outputs/finetune/.../checkpoints/...\.ckpt
```

## Tips

- Use small learning rates (5e-7) for full fine-tuning to avoid catastrophic forgetting
- Head-only fine-tuning (linear probing) is faster and works well when data distribution is similar
- Sequence packing is disabled during fine-tuning — all samples have identical shapes
- Each epoch processes all training samples (not `num_batches_per_epoch`)
- Validate on held-out data to tune hyperparameters and apply early stopping
- For LSF benchmarks, follow the dataset split in `src/uni2ts/eval_util/_lsf_dataset.py`
