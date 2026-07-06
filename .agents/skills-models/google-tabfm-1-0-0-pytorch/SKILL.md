---
name: google-tabfm-1-0-0-pytorch
description: Run Google's TabFM 1.0.0 (PyTorch) for zero-shot tabular classification and regression. Use when the user asks to classify or regress on tabular/structured data, mentions TabFM, or needs predictions from mixed numerical and categorical columns without training or hyperparameter tuning. Supports binary and multiclass classification (up to 10 classes) and regression via in-context learning.
metadata:
  tags:
    - ai-ml
    - tabular
    - classification
    - regression
    - zero-shot
    - google
    - pytorch
---

# google-tabfm-1-0-0-pytorch

## Overview

Google's **TabFM 1.0.0 (PyTorch)** is a pretrained foundation model for zero-shot tabular classification and regression. Feed it a table with mixed numerical and categorical columns — training rows as context, test rows to predict — and it returns predictions in a single forward pass with no fine-tuning or hyperparameter search.

Key capabilities:
- Zero-shot classification (binary or multiclass, up to 10 classes) and regression
- In-context learning: training examples passed as context, predictions in one forward pass
- Mixed numerical and categorical columns, no manual feature engineering required
- Works with pandas DataFrames or numpy arrays
- `TabFMClassifier.ensemble()` preset for boosted performance (feature crosses, SVD, NNLS blending)
- ~256-d embedding, 24-block ICL Transformer backbone
- Trained on hundreds of millions of synthetic datasets via structural causal models

## Usage

### Installation

```bash
pip install tabfm[pytorch]
pip install torch>=2.0.0
```

### Classification

```python
from tabfm import TabFMClassifier, tabfm_v1_0_0_pytorch as tabfm_v1_0_0

model = tabfm_v1_0_0.load(model_type="classification")
clf = TabFMClassifier(model=model)

# X_train, y_train: training context (pandas DataFrame / numpy array)
# X_test: rows to predict
clf.fit(X_train, y_train)
probs = clf.predict_proba(X_test)
```

### Regression

```python
from tabfm import TabFMRegressor, tabfm_v1_0_0_pytorch as tabfm_v1_0_0

model = tabfm_v1_0_0.load(model_type="regression")
reg = TabFMRegressor(model=model)

reg.fit(X_train, y_train)
preds = reg.predict(X_test)
```

### Direct Hub Loading

```python
from tabfm.src.pytorch.tabfm_v1_0_0 import TabFM_HF

clf_model = TabFM_HF.from_pretrained("google/tabfm-1.0.0-pytorch", subfolder="classification")
reg_model = TabFM_HF.from_pretrained("google/tabfm-1.0.0-pytorch", subfolder="regression")
```

### Ensemble (Classification)

```python
from tabfm import TabFMClassifier, tabfm_v1_0_0_pytorch as tabfm_v1_0_0

model = tabfm_v1_0_0.load(model_type="classification")
clf = TabFMClassifier.ensemble(model=model)
clf.fit(X_train, y_train)
probs = clf.predict_proba(X_test)
```

The ensemble adds feature crosses, SVD features, and non-negative least squares blending. It yields better accuracy at the cost of higher compute.

### From CSV

```python
import pandas as pd

df = pd.read_csv("data.csv")
X_train = df.drop(columns=["target"])
y_train = df["target"]
X_test = test_df.drop(columns=["target"])

clf.fit(X_train, y_train)
probs = clf.predict_proba(X_test)
```

## Gotchas

- **Max 10 classes** — hard architectural limit for classification. For more classes, use a different model or reduce the label space.
- **`fit()` does no training** — it stores training rows as context for in-context learning. No weights are updated.
- **Memory scales with training rows** — all training rows are passed as context. For very large datasets, consider subsetting or using a smaller context.
- **Optimized for ≤ 500 features** — behavior on very wide tables may degrade. Consider dimensionality reduction first.
- **Non-commercial license** — model weights are TabFM Non-Commercial License v1.0. Source code is Apache 2.0. Do not use for commercial products without checking license terms.
- **Categorical columns** — pass them as strings or categoricals in the DataFrame. TabFM handles encoding internally via Fourier features and per-group linear projections.
- **`predict_proba` returns class probabilities** — use `np.argmax(probs, axis=1)` for class predictions.
- **Not an officially supported Google product** — this is a research release. No SLA or backward compatibility guarantees.
- **JAX/Flax variant** — a separate checkpoint exists at `google/tabfm-1.0.0-jax`. Do not mix PyTorch and JAX weights.

## References

- [01-api-reference](references/01-api-reference.md) — `TabFMClassifier`, `TabFMRegressor`, `TabFM_HF` API details and parameters
- [02-model-architecture](references/02-model-architecture.md) — Column attention, row compression, ICL Transformer, hyperparameters
- [03-data-preparation](references/03-data-preparation.md) — Input formats, categorical handling, CSV/Excel/Parquet loading tips
- [04-ensemble](references/04-ensemble.md) — Ensemble preset, feature crosses, SVD features, NNLS blending
