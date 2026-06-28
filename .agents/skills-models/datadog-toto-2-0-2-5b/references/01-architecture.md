# Architecture

## Overview

Toto 2.0 2.5B is a decoder-only patched transformer with 48 layers, 32 attention heads, and d_model=2048. The architecture alternates between time-axis (causal) and variate-axis (full) attention layers, enabling efficient multivariate forecasting.

## Core Components

### Patched Input Encoding

Raw time series values are split into non-overlapping patches of size 32. Each patch is concatenated with its corresponding mask values (0 for observed, 1 for missing) and projected through a residual MLP (`InputResidualMLP`) to produce the initial embedding. The input is transformed through arcsinh after causal standardization.

### Causal Standard Deviation Scaler

The `PatchedCausalStdScaler` normalizes each variate independently using causally-computed mean and standard deviation. The scaler is patch-aware — statistics respect the causal ordering and mask. After scaling, values pass through arcsinh for robustness to extreme values.

### Alternating Time/Variate Attention

The transformer decoder alternates between two attention modes:

- **Time-axis layers** (causal): attend across time positions within each variate. Standard causal masking ensures no future information leaks.
- **Variate-axis layers** (full): attend across variates at each time position. Full attention enables cross-variable information sharing.

The alternation pattern is controlled by `layer_group_size` (48 for 2.5B) and `num_variate_layers_per_group` (1). With `variate_layer_first=False`, each group has 47 time layers followed by 1 variate layer.

### Contiguous Patch Masking (CPM)

CPM is the key innovation enabling single-pass parallel decoding. During training, contiguous blocks at the end of the context are masked, forcing the model to predict multiple future patches simultaneously. At inference, this allows the model to forecast a block of `decode_block_size` steps in a single forward pass.

For horizons exceeding `decode_block_size`, the model uses block decoding with median feedback: predict a block, feed the median back as context, predict the next block, and so on.

### Quantile Output Head

The `QuantileKnotsOutputHead` produces 9 quantile predictions (0.1 through 0.9) using a fused patched parameter projection (`FusedPatchedParamProjection`) with residual MLP projections. The head is trained with pinball loss.

Output quantiles are in latent space; they are converted back to real space via `sinh() * scale + loc`. The quantile crossing fix is applied by sorting the real-space quantiles.

### KV Cache for Block Decoding

When `decode_block_size` is set and the horizon requires multiple blocks, the model uses a KV cache to avoid re-computing attention for previously processed patches. The cache is reused across `forecast()` calls if shapes match.

## u-μP Scaling

Toto 2.0 uses unit-scaled μP (u-μP) hyperparameter transfer to train all five model sizes (4m → 2.5B) from a single recipe. The `dd-unit-scaling` library (a compile-friendly extension of graphcore-research/unit-scaling) handles the scaling factors for weights, gradients, and residuals.

Key scaling properties:
- `residual_mult=0.75` — residual connection scaling factor
- `residual_attn_ratio=5.136` — computed as `sqrt(S / log(S))` where S = context_length / patch_size
- `per_dim_scale=True` — per-dimension scaling for attention

## Architecture Parameters (2.5B)

| Parameter | Value |
|---|---|
| d_model | 2048 |
| d_ff | 5464 |
| num_layers | 48 |
| num_heads | 32 |
| num_groups | 32 |
| qk_dim | 64 |
| v_dim | 64 |
| patch_size | 32 |
| layer_group_size | 48 |
| num_variate_layers_per_group | 1 |
| variate_layer_first | False |
| num_output_patches | 1 |
| pre_norm | True |
| norm_eps | 0.0005 |
| attn_bias | True |
| mlp_bias | False |
| dropout_p | 0.0 |
| qk_norm | False |
| use_xpos | True |
| residual_mult | 0.75 |
| residual_attn_ratio | 5.1362 |
| per_dim_scale | True |

## Training Data

Toto 2.0 was trained on a diverse mixture of time series data:
- **Observability data** — real-world metrics from Datadog's internal monitoring (infrastructure, networking, databases, security, application performance)
- **Public datasets** — GIFT-Eval Pretrain, Chronos pretraining data (subset to avoid leakage), and others
- **Synthetic data** — approximately 1/3 of the pretraining mix for robustness

## Pretraining Details

- Trained with NorMuon optimizer
- Pinball loss for quantile predictions
- No dropout (dropout_p=0.0) — non-zero dropout causes long-term training instability
- All five sizes trained from the same recipe via u-μP
