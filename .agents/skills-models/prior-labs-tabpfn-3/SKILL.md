---
name: prior-labs-tabpfn-3
description: Run Prior Labs' TabPFN-3 for zero-shot tabular classification and regression. Use when the user asks to classify or regress on tabular/structured data, mentions TabPFN, or needs predictions from mixed numerical and categorical columns without training or hyperparameter tuning. Supports binary and multiclass classification and regression via in-context learning. Handles missing values natively. Requires PriorLabs authentication. Non-commercial license.
metadata:
  tags:
    - ai-ml
    - tabular
    - classification
    - regression
    - zero-shot
    - prior-labs
    - pytorch
---

# prior-labs-tabpfn-3

## Overview

Prior Labs' **TabPFN-3** is a transformer-based foundation model that solves tabular prediction problems in a single forward pass using in-context learning. Feed it training rows as context and test rows to predict — no weight updates, no hyperparameter search.

Key capabilities:
- Zero-shot classification (binary and multiclass) and regression
- In-context learning: training examples passed as context, predictions in one forward pass
- Mixed numerical and categorical columns, no manual feature engineering required
- Native missing value handling
- Handles up to 1M × 200, 100k × 2,000, or 1,000 × 20,000 (rows × features)
- 24-layer transformer with row-wise and cross-row attention
- Trained purely on synthetic tabular tasks — no dataset leakage
- Specialized checkpoints for binary, multiclass, time-series, and OOD-robust scenarios

## Usage

### Installation

```bash
pip install tabpfn
```

Requires Python 3.10+. A compatible PyTorch build is installed automatically. For CPU-only or specific CUDA versions, install PyTorch first via the [PyTorch installer](https://pytorch.org/get-started/locally/).

### Authentication

On first use, TabPFN opens a browser to log in via PriorLabs and accept the license. For headless/CI environments, obtain a token from [priorlabs.ai](https://ux.priorlabs.ai) and set:

```bash
export TABPFN_TOKEN="your_token_here"
```

### Classification

```python
from tabpfn import TabPFNClassifier

clf = TabPFNClassifier()
clf.fit(X_train, y_train)          # downloads checkpoint on first use
predictions = clf.predict(X_test)
probabilities = clf.predict_proba(X_test)
```

### Regression

```python
from tabpfn import TabPFNRegressor

reg = TabPFNRegressor()
reg.fit(X_train, y_train)          # downloads checkpoint on first use
predictions = reg.predict(X_test)
```

### GPU (Recommended)

```python
clf = TabPFNClassifier(device="cuda")
clf.fit(X_train, y_train)
predictions = clf.predict(X_test)
```

GPU is strongly recommended. CPU is only feasible for small datasets (≲1,000 samples).

### Specialized Checkpoints

Use `model_path` to select a specialized checkpoint:

```python
# Binary classification (datasets < 200k rows)
clf = TabPFNClassifier(model_path="tabpfn-v3-classifier-v3_20260417_binary.ckpt")

# Multiclass classification (datasets < 200k rows)
clf = TabPFNClassifier(model_path="tabpfn-v3-classifier-v3_20260417_multiclass.ckpt")

# Regression with alternative preprocessing (datasets < 100k rows)
reg = TabPFNRegressor(model_path="tabpfn-v3-regressor-v3_20260417_mediumdata.ckpt")

# OOD-robust classification (test inputs outside training distribution)
clf = TabPFNClassifier(model_path="tabpfn-v3-classifier-v3_20260506_ood.ckpt")

# OOD-robust regression
reg = TabPFNRegressor(model_path="tabpfn-v3-regressor-v3_20260506_ood.ckpt")

# Time-series forecasting (used by TabPFN-TS-3)
reg = TabPFNRegressor(model_path="tabpfn-v3-regressor-v3_20260506_timeseries.ckpt")
```

### From CSV

```python
import pandas as pd
from tabpfn import TabPFNClassifier

df = pd.read_csv("data.csv")
X_train = df.drop(columns=["target"])
y_train = df["target"]

clf = TabPFNClassifier()
clf.fit(X_train, y_train)
predictions = clf.predict(X_test)
```

### Save and Load Fitted Model

```python
from tabpfn import TabPFNRegressor
from tabpfn.model_loading import save_fitted_tabpfn_model, load_fitted_tabpfn_model

reg = TabPFNRegressor(device="cuda")
reg.fit(X_train, y_train)
save_fitted_tabpfn_model(reg, "my_model.tabpfn_fit")

# Reload later, even on CPU
reg_cpu = load_fitted_tabpfn_model("my_model.tabpfn_fit", device="cpu")
```

### Batch Prediction

Each `predict` call recomputes the training set. Batch test rows together — calling `predict` on 100 samples separately is ~100× slower than a single call. For large test sets, split into chunks of ~1,000 samples.

### Offline Usage

Download models ahead of time:

```bash
python scripts/download_all_models.py
```

Or set a custom cache directory:

```bash
export TABPFN_MODEL_CACHE_DIR="/path/to/models"
```

Default cache locations: `~/.cache/tabpfn/` (Linux), `~/Library/Caches/tabpfn/` (macOS), `%APPDATA%\tabpfn\` (Windows).

### Previous Versions

```python
from tabpfn import TabPFNClassifier
from tabpfn.constants import ModelVersion

# TabPFN-2.6
clf = TabPFNClassifier.create_default_for_version(ModelVersion.V2_6)

# TabPFN-2
clf = TabPFNClassifier.create_default_for_version(ModelVersion.V2)
```

## Gotchas

- **Non-commercial license** — TabPFN-3 weights are under `tabpfn-3-license-v1.0`. Research, testing, and internal benchmarking are allowed. Production, revenue-generating products, client deliverables, and internal commercial decision-making are prohibited. Contact `sales@priorlabs.ai` for commercial licensing.
- **Authentication required** — first use opens a browser for PriorLabs login. In headless environments, set `TABPFN_TOKEN` manually.
- **No preprocessing** — do not apply scaling, normalization, or one-hot encoding. Feed raw data directly. The model handles categorical encoding internally.
- **GPU recommended** — CPU inference is only practical for ≲1,000 samples. Even older GPUs with ~8GB VRAM work well.
- **Batch predictions** — each `predict()` call recomputes the full training context. Never call `predict()` in a loop over individual samples.
- **Size limits** — TabPFN-3 supports up to 1M × 200, 100k × 2,000, or 1k × 20,000 (rows × features). For larger datasets, subsample or set `ignore_pretraining_limits=True` (performance not guaranteed).
- **Missing values supported** — TabPFN handles NaN/None natively. No imputation needed.
- **Feature engineering helps** — adding domain-specific features improves performance. But avoid standard preprocessing (scaling, one-hot encoding).
- **`fit()` does no training** — it stores training rows as in-context learning context. No weights are updated.
- **Memory scales with training rows** — all training rows are kept in context. Very large training sets consume significant GPU memory.
- **Python 3.10+ required** — not compatible with Python 3.9 or earlier.
- **Apple Silicon/MPS** — for best performance, use PyTorch nightly after `2.13.0.dev20260510` for flash attention support. Set `TABPFN_MPS_MEMORY_FRACTION` (default `0.7`) to prevent system crashes.
- **Not suitable for unstructured data** — text and images are not supported. Use the API version for textual features.

## References

- [01-api-reference](references/01-api-reference.md) — `TabPFNClassifier`, `TabPFNRegressor` API, parameters, and methods
- [02-checkpoints](references/02-checkpoints.md) — Specialized checkpoints, selection guide, and ensembling
- [03-environment-variables](references/03-environment-variables.md) — Configuration via environment variables and `.env`
- [04-performance-tips](references/04-performance-tips.md) — GPU setup, batch prediction, memory optimization, and troubleshooting
