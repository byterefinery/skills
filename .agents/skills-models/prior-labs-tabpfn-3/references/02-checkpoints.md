# TabPFN-3 — Checkpoints

## Default Checkpoints

The default classifier and regressor checkpoints are used automatically when no `model_path` is specified.

| Checkpoint | Task | Download |
| --- | --- | --- |
| `tabpfn-v3-classifier-v3_default.ckpt` | Classification (default) | Auto-downloaded on first use |
| `tabpfn-v3-regressor-v3_default.ckpt` | Regression (default) | Auto-downloaded on first use |

## Specialized Checkpoints

Experimental variants optimized for specific regimes. Start with the defaults; use these for ensembling or when the default underperforms.

| Checkpoint | Task | Specialization |
| --- | --- | --- |
| `tabpfn-v3-classifier-v3_20260417_binary.ckpt` | Classification | Binary classification, datasets < 200k rows |
| `tabpfn-v3-classifier-v3_20260417_multiclass.ckpt` | Classification | Multiclass classification, datasets < 200k rows |
| `tabpfn-v3-regressor-v3_20260417_mediumdata.ckpt` | Regression | Alternative preprocessing, datasets < 100k rows |
| `tabpfn-v3-classifier-v3_20260506_ood.ckpt` | Classification | OOD-robust — test inputs outside training distribution. Uses `squashing_scaler_max10 + none` preprocessors. |
| `tabpfn-v3-regressor-v3_20260506_ood.ckpt` | Regression | OOD-robust — test inputs outside training distribution. Uses `quantile_uni_extrapolate + squashing_scaler_max10` preprocessors. |
| `tabpfn-v3-regressor-v3_20260506_timeseries.ckpt` | Regression / Time-series | Fine-tuned on synthetic time-series data. Used by default in TabPFN-TS-3. |

### Using Specialized Checkpoints

```python
from tabpfn import TabPFNClassifier, TabPFNRegressor

# Binary classification
clf = TabPFNClassifier(model_path="tabpfn-v3-classifier-v3_20260417_binary.ckpt")

# OOD-robust regression
reg = TabPFNRegressor(model_path="tabpfn-v3-regressor-v3_20260506_ood.ckpt")

# Time-series
reg = TabPFNRegressor(model_path="tabpfn-v3-regressor-v3_20260506_timeseries.ckpt")
```

## Checkpoint Selection Guide

| Scenario | Recommended Checkpoint |
| --- | --- |
| General classification | Default (`TabPFNClassifier()`) |
| Binary classification, < 200k rows | `binary.ckpt` or default |
| Multiclass classification, < 200k rows | `multiclass.ckpt` or default |
| General regression | Default (`TabPFNRegressor()`) |
| Regression, < 100k rows, alternative preprocessing | `mediumdata.ckpt` |
| Test data may differ from training distribution | `ood.ckpt` |
| Time-series forecasting | `timeseries.ckpt` |

## Ensembling

Combine multiple checkpoints for improved accuracy:

```python
from tabpfn import TabPFNClassifier
from sklearn.ensemble import VotingClassifier

clf_default = TabPFNClassifier()
clf_binary = TabPFNClassifier(model_path="tabpfn-v3-classifier-v3_20260417_binary.ckpt")
clf_ood = TabPFNClassifier(model_path="tabpfn-v3-classifier-v3_20260506_ood.ckpt")

ensemble = VotingClassifier(
    estimators=[
        ("default", clf_default),
        ("binary", clf_binary),
        ("ood", clf_ood),
    ],
    voting="soft",
)

ensemble.fit(X_train, y_train)
predictions = ensemble.predict(X_test)
```

For regression, average predictions across multiple checkpoints:

```python
from tabpfn import TabPFNRegressor

models = [
    TabPFNRegressor(),
    TabPFNRegressor(model_path="tabpfn-v3-regressor-v3_20260417_mediumdata.ckpt"),
    TabPFNRegressor(model_path="tabpfn-v3-regressor-v3_20260506_ood.ckpt"),
]

preds = [m.predict(X_test) for m in models]
ensemble_pred = sum(preds) / len(preds)
```

## Downloading Checkpoints

For offline usage, download all models:

```bash
python scripts/download_all_models.py
```

Or download manually from HuggingFace:
- [Classifier](https://huggingface.co/Prior-Labs/tabpfn_3/blob/main/tabpfn-v3-classifier-v3_default.ckpt)
- [Regressor](https://huggingface.co/Prior-Labs/tabpfn_3/blob/main/tabpfn-v3-regressor-v3_default.ckpt)

Place in the cache directory or specify via `model_path`.
