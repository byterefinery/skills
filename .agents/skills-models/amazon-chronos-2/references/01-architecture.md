# 01 — Architecture

## Model Architecture

Chronos-2 is an encoder-only transformer inspired by the T5 encoder:

- **Parameters**: 120M
- **Layers**: 6
- **Attention heads**: 8
- **Hidden dimension (d_model)**: 512
- **Max context length**: 8192 tokens
- **Max prediction length**: 1024 tokens (autoregressive beyond)

The model uses a patch-based approach to encode time series into token sequences, similar to how vision transformers process images. Each patch represents a fixed window of the time series.

## Group Attention Mechanism

Chronos-2 introduces a group attention mechanism that enables efficient in-context learning across related series within a batch. Instead of attending to each series independently, the model jointly attends to groups of series, allowing it to:

- Share statistical strength across similar time series
- Learn cross-series dependencies automatically
- Improve accuracy when individual series have limited history

The group size during pretraining determines the optimal batch size for cross-learning inference. Deviating from this size may reduce effectiveness.

## Cross-Learning

Cross-learning is the inference-time application of the group attention mechanism. When `cross_learning=True` in `predict_df()`, the model processes multiple series together and uses cross-attention to share information.

**When it helps**:
- Series with short history (limited context)
- Related series from the same domain (e.g., multiple product SKUs)
- Sparse or noisy individual series

**When it may not help**:
- Series with abundant, clean history
- Very dissimilar series in the same batch
- Large batch sizes that deviate from pretraining group sizes

## Training Data

Chronos-2 was trained on:

1. **Chronos Datasets** — subset of `autogluon/chronos_datasets` (excluding test portions overlapping with GIFT-Eval). Contains 32 datasets covering hourly, daily, weekly, and monthly frequencies.

2. **GIFT-Eval Pretrain** — subset of `Salesforce/GiftEvalPretrain`. Provides diverse real-world time series.

3. **Synthetic data** — large-scale synthetic univariate and multivariate time series to improve generalization.

The combination of real-world and synthetic data enables strong zero-shot performance across diverse domains.

## Quantile Training

The model is trained to predict 9 quantiles directly: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]. Other quantile levels are interpolated at inference time. This direct quantile prediction avoids the sampling overhead of the original Chronos models.

## Comparison with Other Chronos Families

| Feature | Chronos-2 | Chronos-Bolt | Chronos (T5) |
|---|---|---|---|
| Architecture | Encoder-only transformer | Patch-based direct forecasting | T5 decoder |
| Parameters | 120M | 9M–205M | 8M–710M |
| Max context | 8192 | 2048 | 512 |
| Max prediction | 1024 | 64 | 64 |
| Multivariate | Yes | No | No |
| Covariates | Yes | No | No |
| Cross-learning | Yes | No | No |
| Forecast type | Quantiles | Quantiles | Samples |
| Speed | 300+/sec (A10G) | 250x faster than Chronos | Baseline |
