# TabFM 1.0.0 — Model Architecture

## Overview

TabFM processes tabular data through three stages: column attention for feature interactions, row compression into dense vectors, and an ICL Transformer for zero-shot prediction.

## Stage 1: Column Attention (Set Transformer)

Embeds each cell using Fourier features and a per-group linear projection, then aggregates across rows via induced self-attention.

- **Embedding dimension**: 256
- **Blocks**: 3
- **Attention heads**: 4
- **Induced points**: 256
- **Fourier features**: 32 frequencies

This stage captures complex feature interactions and dependencies — the equivalent of manual feature engineering in traditional ML.

## Stage 2: Row Compression

Each row's cross-attended representation is compressed into a single dense vector using row-level attention with Rotary Position Embedding (RoPE).

- **Blocks**: 3
- **Attention heads**: 8
- **CLS tokens**: 8 per row

The CLS tokens summarize each row into a compact embedding that preserves its relationship to all features.

## Stage 3: ICL Transformer

A causal Transformer operates over the sequence of compressed row vectors. Training rows serve as context (prefix), test rows are the targets (suffix).

- **Blocks**: 24
- **Attention heads**: 8
- **Embedding dim**: 256
- **Feed-forward factor**: 4
- **Activation**: SwiGLU
- **Positional encoding**: RoPE

This is where in-context learning happens — the model interprets the training rows as examples and generates predictions for the test rows in a single forward pass.

## Key Hyperparameters

| Parameter | Value |
| --- | --- |
| Embedding dim | 256 |
| Column attention blocks | 3 (4 heads, 256 induced points) |
| Row attention blocks | 3 (8 heads, 8 CLS tokens) |
| ICL transformer blocks | 24 (8 heads) |
| Feed-forward factor | 4 |
| Max classes | 10 |
| Activation | SwiGLU |
| Fourier features | 32 frequencies |

## Training Data

TabFM was trained on hundreds of millions of synthetic datasets generated using structural causal models (SCMs). The SCM prior encodes inductive biases about causal structure and feature relationships typical in tabular tasks. Synthetic data was chosen due to the scarcity of diverse, high-quality open-source tabular datasets and to avoid privacy/licensing concerns.

## Design Influences

TabFM synthesizes ideas from:
- **TabPFN** — alternating row/column attention for tabular data
- **TabICL** — efficient ICL over compressed row vectors instead of raw grids
