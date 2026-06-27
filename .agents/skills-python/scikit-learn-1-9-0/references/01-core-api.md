# Core API Reference

## Base Classes and Mixins

### `BaseEstimator` (`sklearn.base`)
Parent class for all estimators. Provides:
- `get_params(deep=True)` / `set_params(**params)` — introspection for GridSearchCV
- `__repr__` / HTML repr — readable representation in notebooks
- `__sklearn_clone__()` — cloning protocol (delegated by `clone()`)
- Parameter validation via `_validate_params`
- Feature names tracking (`feature_names_in_`, `n_features_in_`)

**Rule:** All `__init__` parameters must be explicit keyword arguments. No `*args` or `**kwargs`.

### Mixins
| Mixin | Purpose | Methods |
|-------|---------|---------|
| `ClassifierMixin` | Classification | `predict()`, `score()` (accuracy) |
| `RegressorMixin` | Regression | `predict()`, `score()` (R²) |
| `TransformerMixin` | Transformation | `fit_transform()`, `inverse_transform()` |
| `ClustererMixin` | Clustering | `fit_predict()` |

## Pipeline

### `Pipeline(steps, *, memory=None, transform_input=None)`
Chain transformers → final estimator. All steps except last must implement `transform()`.

```python
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# Explicit naming
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", SVC())
])

# Auto-naming (class name + index)
pipe = make_pipeline(StandardScaler(), SVC())
```

**Parameter access:** `pipe.set_params(clf__C=0.1, scaler__with_mean=False)`

**Step replacement:** `pipe.named_steps["scaler"] = "passthrough"` removes a step.

**`transform_input` (new in 1.6):** List of metadata parameter names to transform through the pipeline before reaching the consuming step. Requires `enable_metadata_routing=True`.

### `FeatureUnion(transformers, *, n_jobs=None, transformer_params=None)`
Apply multiple transformers in parallel, concatenate outputs horizontally.

```python
from sklearn.pipeline import FeatureUnion, make_union
union = make_union(StandardScaler(), PCA(n_components=5))
```

## ColumnTransformer

### `ColumnTransformer(transformers, *, remainder="drop", sparse_threshold=0.3)`
Apply different transformers to different columns. Essential for mixed-type data.

```python
from sklearn.compose import ColumnTransformer, make_column_transformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), ["age", "income"]),
    ("cat", OneHotEncoder(handle_unknown="infrequent_if_exist"), ["city", "category"]),
], remainder="drop")

# Auto-detection with make_column_transformer
from sklearn.compose import make_column_selector as selector
preprocessor = make_column_transformer(
    (StandardScaler(), selector("numeric")),
    (OneHotEncoder(), selector("categorical")),
)
```

**`remainder`:** `"drop"` (default), `"passthrough"`, or a transformer.

### `TransformedTargetRegressor(regressor, transformer, *, check_inverse=True)`
Transform the target variable before fitting, inverse-transform predictions.

```python
from sklearn.compose import TransformedTargetRegressor
from sklearn.preprocessing import PowerTransformer
from sklearn.ensemble import RandomForestRegressor

model = TransformedTargetRegressor(
    regressor=RandomForestRegressor(),
    transformer=PowerTransformer()
)
```

## Clone and Inspection

### `clone(estimator, *, safe=True)` (`sklearn.base`)
Create an unfitted copy with identical hyperparameters. Used internally by CV splitters.

```python
from sklearn.base import clone
fitted = model.fit(X, y)
fresh = clone(fitted)  # Unfitted, same params
```

### `config_context(**changes)` / `set_config(**changes)` / `get_config()`
Thread-local global configuration.

| Key | Default | Description |
|-----|---------|-------------|
| `assume_finite` | `False` | Skip NaN/inf checks for speed |
| `working_memory` | `1024` | Min MB to keep arrays in memory |
| `enable_metadata_routing` | `False` | Enable metadata routing API |
| `transform_output` | `"default"` | Default output container (`"pandas"`, `"polars"`) |
| `array_api_dispatch` | `False` | Dispatch to Array API compliant backends |
| `skip_parameter_validation` | `False` | Skip parameter validation (dev use) |
| `sparse_interface` | `"spmatrix"` | Return sparse matrices or arrays (`"sparray"`) |
| `display` | `"diagram"` | Pipeline repr style (`"text"`, `"diagram"`) |
| `print_changed_only` | `True` | Only print changed params in repr |

```python
import sklearn
sklearn.set_config(transform_output="pandas", enable_metadata_routing=True)

# Context manager (temporary)
with sklearn.config_context(enable_metadata_routing=True):
    model.fit(X, y, sample_weight=w)
```

## Metadata Routing

Enable with `sklearn.set_config(enable_metadata_routing=True)`. Allows passing extra arguments (`sample_weight`, `groups`) through pipelines and meta-estimators.

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

pipe = Pipeline([("scaler", StandardScaler()), ("clf", SVC())])

# Route sample_weight to all steps that support it
from sklearn.utils.metadata_routing import MethodMapping
pipe.set_fit_request(scaler__sample_weight=True, clf__sample_weight=True)

# Or use the convenience method
pipe = pipe.set_fit_request(sample_weight=True)

pipe.fit(X, y, sample_weight=w)
```

## `set_output` API

Configure transformer output format globally or per-estimator.

```python
# Per-estimator
scaler = StandardScaler().set_output(transform="pandas")
X_scaled = scaler.fit_transform(X_df)  # Returns DataFrame

# Global
import sklearn
sklearn.set_config(transform_output="polars")
```

Supported outputs: `"default"` (numpy/sparse), `"pandas"`, `"polars"`.
