# TabPFN-3 — API Reference

## TabPFNClassifier

```python
from tabpfn import TabPFNClassifier
```

### Constructor Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `device` | `str` | `"auto"` | `"cuda"`, `"cpu"`, `"mps"`, or `"auto"` |
| `model_path` | `str` | `None` | Path to a specialized checkpoint file |
| `ignore_pretraining_limits` | `bool` | `False` | Allow datasets exceeding recommended size limits |
| `seed` | `int` | `0` | Random seed for reproducibility |

### Methods

| Method | Description | Return |
| --- | --- | --- |
| `fit(X_train, y_train)` | Store training rows as ICL context. No weight update. | `self` |
| `predict(X_test)` | Return predicted class labels. | `np.ndarray` shape `(n_test,)` |
| `predict_proba(X_test)` | Return class probabilities for each row. | `np.ndarray` shape `(n_test, n_classes)` |
| `create_default_for_version(version)` | Class method. Create classifier for a specific model version. | `TabPFNClassifier` |

### Usage

```python
clf = TabPFNClassifier(device="cuda")
clf.fit(X_train, y_train)
predictions = clf.predict(X_test)
probabilities = clf.predict_proba(X_test)
classes = np.argmax(probabilities, axis=1)
confidence = np.max(probabilities, axis=1)
```

## TabPFNRegressor

```python
from tabpfn import TabPFNRegressor
```

### Constructor Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `device` | `str` | `"auto"` | `"cuda"`, `"cpu"`, `"mps"`, or `"auto"` |
| `model_path` | `str` | `None` | Path to a specialized checkpoint file |
| `ignore_pretraining_limits` | `bool` | `False` | Allow datasets exceeding recommended size limits |
| `seed` | `int` | `0` | Random seed for reproducibility |

### Methods

| Method | Description | Return |
| --- | --- | --- |
| `fit(X_train, y_train)` | Store training rows as ICL context. No weight update. | `self` |
| `predict(X_test)` | Return predicted continuous values. | `np.ndarray` shape `(n_test,)` |
| `create_default_for_version(version)` | Class method. Create regressor for a specific model version. | `TabPFNRegressor` |

### Usage

```python
reg = TabPFNRegressor(device="cuda")
reg.fit(X_train, y_train)
predictions = reg.predict(X_test)
```

## Model Loading Utilities

```python
from tabpfn.model_loading import (
    save_fitted_tabpfn_model,
    load_fitted_tabpfn_model,
    save_tabpfn_model,
    load_model_criterion_config,
)
```

| Function | Description |
| --- | --- |
| `save_fitted_tabpfn_model(estimator, path)` | Save a fitted estimator (with training context) to disk |
| `load_fitted_tabpfn_model(path, device)` | Reload a fitted estimator, optionally on a different device |
| `save_tabpfn_model(estimator, path)` | Save only the pre-trained weights (no training context) |
| `load_model_criterion_config(path)` | Reload a checkpoint of pre-trained weights |

### Save/Load Example

```python
# Train on GPU
reg = TabPFNRegressor(device="cuda")
reg.fit(X_train, y_train)
save_fitted_tabpfn_model(reg, "model.tabpfn_fit")

# Reload on CPU
reg_cpu = load_fitted_tabpfn_model("model.tabpfn_fit", device="cpu")
predictions = reg_cpu.predict(X_test)
```

## Model Versions

```python
from tabpfn.constants import ModelVersion

# Available versions
ModelVersion.V3      # TabPFN-3 (default)
ModelVersion.V2_6    # TabPFN-2.6
ModelVersion.V2_5    # TabPFN-2.5
ModelVersion.V2      # TabPFN-2
```

```python
from tabpfn import TabPFNClassifier

clf_v26 = TabPFNClassifier.create_default_for_version(ModelVersion.V2_6)
clf_v2 = TabPFNClassifier.create_default_for_version(ModelVersion.V2)
```

## Input Formats

Accepts the following input types for `X` and `y`:
- `pandas.DataFrame` / `pandas.Series`
- `numpy.ndarray`
- Scikit-learn compatible sparse matrices

Categorical columns are handled internally — pass them as strings, categoricals, or integers without one-hot encoding.

## Ecosystem Packages

| Package | Description | Install |
| --- | --- | --- |
| `tabpfn` | Core library for local inference | `pip install tabpfn` |
| `tabpfn-client` | API client for cloud-based inference | `pip install tabpfn-client` |
| `tabpfn-extensions` | SHAP explanations, outlier detection, embeddings, many-class | `pip install tabpfn-extensions` |
