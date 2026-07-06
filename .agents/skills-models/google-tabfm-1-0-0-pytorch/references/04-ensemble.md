# TabFM 1.0.0 — Ensemble

## Overview

`TabFMClassifier.ensemble()` builds a 32-way ensemble that boosts classification accuracy beyond the base model. It combines three techniques:

1. **Feature crosses** — interaction features between column pairs
2. **SVD features** — Singular Value Decomposition to extract latent structure
3. **NNLS blending** — Non-negative least squares to compute optimal ensemble weights

For classification, the ensemble also applies **Platt scaling** for probability calibration.

## Usage

```python
from tabfm import TabFMClassifier, tabfm_v1_0_0_pytorch as tabfm_v1_0_0

model = tabfm_v1_0_0.load(model_type="classification")
clf = TabFMClassifier.ensemble(model=model)

clf.fit(X_train, y_train)
probs = clf.predict_proba(X_test)
```

## How It Works

### Feature Crosses

Creates interaction features by multiplying pairs of columns. This captures non-linear relationships that the base model's column attention might miss.

### SVD Features

Applies Singular Value Decomposition to the input matrix, extracting the top singular vectors as additional features. This reveals latent structure in the data.

### NNLS Blending

Solves a non-negative least squares problem to find optimal weights for combining the 32 ensemble members. The non-negativity constraint ensures interpretable blending.

### Platt Scaling

For classification, applies Platt scaling (logistic regression calibration) to the ensemble's raw scores, producing better-calibrated probability estimates.

## Trade-offs

| Aspect | Base Model | Ensemble |
| --- | --- | --- |
| Accuracy | Strong baseline | Higher (TabArena leader) |
| Speed | Single forward pass | 32× compute + blending |
| Memory | Context rows only | Context rows + feature expansions |
| Use case | Quick prototyping, large datasets | Final models, smaller datasets |

## When to Use Ensemble

- **Use ensemble** when accuracy matters more than speed and the dataset fits comfortably in memory
- **Use base model** for quick prototyping, very large datasets, or when inference speed is critical
- Ensemble is only available for classification, not regression

## Performance

On TabArena benchmarks, the ensemble configuration outperforms the base model and heavily-tuned supervised baselines including gradient-boosted trees. See the [TabArena leaderboard](https://tabarena.ai) for detailed per-dataset results.
