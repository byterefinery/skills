# TimesFM-2.5 Model Architecture

## Decoder-Only Transformer

TimesFM is a decoder-only transformer architecture designed specifically for time series forecasting. Unlike encoder-decoder models (e.g., T5-based Chronos), it uses only the decoder stack, which simplifies the architecture and reduces compute during inference.

### Key Design Choices

- **Decoder-only**: No encoder component. The past values are processed directly by the decoder stack with causal masking.
- **Patch-based input encoding**: Input series are split into patches (contiguous segments) before being embedded. This reduces sequence length and captures local structure.
- **Continuous quantile head**: The output head predicts quantiles directly using a continuous quantile loss, rather than tokenizing the output space.

## Patch-Based Encoding

The input time series is divided into non-overlapping patches of fixed size. Each patch is embedded into a vector, reducing the effective sequence length by the patch size factor. This is analogous to patching in vision transformers (ViT).

Benefits:
- **Reduced sequence length** — fewer tokens to process, lower memory and compute
- **Local structure preservation** — each patch captures a local segment of the series
- **Positional encoding** — standard sinusoidal or learned positional encodings applied to patch embeddings

The patch size is fixed at model construction time and is not a user-configurable parameter.

## Quantile Head

The model outputs both point forecasts (mean) and quantile forecasts simultaneously. The quantile head uses a continuous quantile loss:

- **Training objective**: Pinball loss (quantile loss) over continuous output values
- **Output shape**: `(batch, horizon, n_quantiles)` where the first column is the mean and remaining columns are quantile levels
- **Quantile levels**: 10th, 20th, 30th, 40th, 50th, 60th, 70th, 80th, 90th percentiles (9 quantiles + 1 mean = 11 total)

The `use_continuous_quantile_head` flag in the original PyTorch implementation controls whether the quantile head uses continuous output or discretized tokenization. The transformers port always uses the continuous head.

## Training Data

TimesFM-2.5 was pretrained on a diverse mix of data sources:

1. **GIFT-Eval Pretrain** — a large collection of real-world time series datasets
2. **Wikimedia Pageviews** — web traffic data, cutoff November 2023
3. **Google Trends** — search query popularity, cutoff end of 2022
4. **Synthetic data** — procedurally generated time series with known patterns
5. **Augmented data** — transformations of existing series (scaling, shifting, noise injection)

This diverse training mix enables zero-shot generalization across domains.

## Position in the TimesFM Family

| Checkpoint | Release | Context | Horizon | Notes |
|---|---|---|---|---|
| `google/timesfm-1-0-200m` | 2023 | 512 | 128 | Original release |
| `google/timesfm-1-0-200m-transformers` | 2024 | 512 | 128 | Transformers port of v1.0 |
| `google/timesfm-2.5-200m-pytorch` | 2025 | 1024 | 256 | Updated PyTorch checkpoint |
| `google/timesfm-2.5-200m-transformers` | 2025 | 1024 | 512 | Transformers port of v2.5 |

The 2.5 release doubled the context length (512 → 1024) and increased the max horizon. The QKV matrices were fused for speed optimization in October 2025.

## Citation

```bibtex
@inproceedings{das2024a,
  title={A decoder-only foundation model for time-series forecasting},
  author={Abhimanyu Das and Weihao Kong and Rajat Sen and Yichen Zhou},
  booktitle={Forty-first International Conference on Machine Learning},
  year={2024},
  url={https://openreview.net/forum?id=jn2iTJas6h}
}
```
