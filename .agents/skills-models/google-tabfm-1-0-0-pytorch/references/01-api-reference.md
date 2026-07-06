# TabFM 1.0.0 — API Reference

## TabFMClassifier

```python
from tabfm import TabFMClassifier, tabfm_v1_0_0_pytorch as tabfm_v1_0_0

model = tabfm_v1_0_0.load(model_type="classification")
clf = TabFMClassifier(model=model)
```

### Methods

| Method | Description | Return |
| --- | --- | --- |
| `fit(X_train, y_train)` | Store training rows as ICL context. No weight update. | `self` |
| `predict_proba(X_test)` | Return class probabilities for each row. | `np.ndarray` shape `(n_test, n_classes)` |
| `ensemble(model, ...)` | Class method. Build ensemble with feature crosses, SVD, NNLS blending. | `TabFMClassifier` |

### Usage

```python
clf.fit(X_train, y_train)
probs = clf.predict_proba(X_test)
predictions = np.argmax(probs, axis=1)
confidence = np.max(probs, axis=1)
```

## TabFMRegressor

```python
from tabfm import TabFMRegressor, tabfm_v1_0_0_pytorch as tabfm_v1_0_0

model = tabfm_v1_0_0.load(model_type="regression")
reg = TabFMRegressor(model=model)
```

### Methods

| Method | Description | Return |
| --- | --- | --- |
| `fit(X_train, y_train)` | Store training rows as ICL context. No weight update. | `self` |
| `predict(X_test)` | Return point predictions for each row. | `np.ndarray` shape `(n_test,)` |

### Usage

```python
reg.fit(X_train, y_train)
preds = reg.predict(X_test)
```

## TabFM_HF (Direct Hub Loading)

```python
from tabfm.src.pytorch.tabfm_v1_0_0 import TabFM_HF

model = TabFM_HF.from_pretrained(
    "google/tabfm-1.0.0-pytorch",
    subfolder="classification"  # or "regression"
)
```

### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `pretrained_path` | str | — | Hugging Face repo or local path |
| `subfolder` | str | — | `"classification"` or `"regression"` |

### Properties

| Property | Type | Description |
| --- | --- | --- |
| `is_classifier` | bool | `True` for classification checkpoint, `False` for regression |

## Checkpoint Subfolders

| Subfolder | Task | `is_classifier` |
| --- | --- | --- |
| `classification/` | Classification (up to 10 classes) | `True` |
| `regression/` | Regression | `False` |

## Input Formats

Both `TabFMClassifier` and `TabFMRegressor` accept:

- `pandas.DataFrame` — columns can be mixed numerical and categorical
- `numpy.ndarray` — all columns must be numerical
- Categorical columns in DataFrames are handled internally via Fourier features

## Output Shapes

| Method | Shape | Description |
| --- | --- | --- |
| `predict_proba(X)` | `(n_test, n_classes)` | One probability per class per row |
| `predict(X)` | `(n_test,)` | One point prediction per row |
