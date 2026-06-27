# Advanced Topics Reference

## Callback API (New in 1.9)

Invoke callbacks during fitting of supported estimators. Currently experimental.

### Built-In Callbacks

#### `ProgressBar()`
Display a progress bar during fitting.

```python
from sklearn.callback import ProgressBar
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(solver="lbfgs", max_iter=1000)
model.fit(X, y, callbacks=[ProgressBar()])
```

#### `ScoringMonitor(scoring, X_val, y_val)`
Compute and log a scoring metric at each iteration.

```python
from sklearn.callback import ScoringMonitor
from sklearn.linear_model import LogisticRegression

monitor = ScoringMonitor("roc_auc", X_val, y_val)
model = LogisticRegression(solver="lbfgs", max_iter=1000)
model.fit(X, y, callbacks=[monitor])
```

### Supported Estimators

- `LogisticRegression` (only with `solver="lbfgs"`)
- `GridSearchCV`, `RandomizedSearchCV`
- `HalvingGridSearchCV`, `HalvingRandomSearchCV`
- `Pipeline`
- `StandardScaler`

### Custom Callbacks

```python
from sklearn.callback import FitCallback

class MyCallback(FitCallback):
    def on_iter_end(self, event):
        print(f"Iteration {event.iteration}: loss={event.loss:.4f}")
```

### Developer Guide

To add callback support to a custom estimator:

```python
from sklearn.callback import CallbackSupportMixin, with_callbacks, CallbackContext

class MyEstimator(CallbackSupportMixin):
    @with_callbacks
    def fit(self, X, y):
        ctx = CallbackContext()
        for i in range(100):
            # ... training logic ...
            ctx.on_iter_end(iteration=i, loss=current_loss)
        return self
```

## FrozenEstimator (New in 1.9)

Wrap a fitted estimator to prevent re-fitting. Useful when using pre-trained models as pipeline steps.

```python
from sklearn.frozen import FrozenEstimator
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Pre-train a model
pretrained = LogisticRegression().fit(X_pretrain, y_pretrain)

# Freeze it — fit() becomes a no-op
frozen = FrozenEstimator(pretrained)

# Use in a pipeline without re-fitting
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("model", frozen),
])
pipe.fit(X, y)  # Only scaler is fitted; model predictions use pretrained weights
```

**Behavior:**
- `fit()` is a no-op (returns self)
- `fit_predict()` and `fit_transform()` raise `AttributeError`
- `__sklearn_clone__()` returns self (doesn't clone inner estimator)
- All other methods delegated to wrapped estimator

## Metadata Routing

Enable with `sklearn.set_config(enable_metadata_routing=True)`. Passes extra arguments through pipelines and meta-estimators.

### Requesting Metadata

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", SVC())
])

# Route sample_weight to specific steps
pipe = pipe.set_fit_request(clf__sample_weight=True)

# Or route to all supporting steps
pipe = pipe.set_fit_request(sample_weight=True)

# Now pass it during fit
pipe.fit(X, y, sample_weight=w)
```

### Custom Metadata

```python
from sklearn.utils.metadata_routing import MetadataRequest

class MyEstimator:
    _metadata_request_fit = MetadataRequest(sample_weight=None, custom_meta=None)

    def fit(self, X, y, *, sample_weight=None, custom_meta=None):
        # Use metadata...
        return self

    def set_fit_request(self, **kwargs):
        self._metadata_request_fit.update_requests(**kwargs)
        return self
```

## Experimental Features

### IterativeImputer
```python
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

imputer = IterativeImputer(max_iter=10, random_state=42)
X_complete = imputer.fit_transform(X_with_missing)
```

### Successive Halving Search
```python
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingGridSearchCV

search = HalvingGridSearchCV(
    estimator, param_grid,
    max_iter=100, factor=3, cv=5
)
```

## Model Persistence

### Joblib (Recommended for sklearn models)

```python
from joblib import dump, load

# Save
dump(model, "model.joblib")

# Load
model = load("model.joblib")
```

### Pickle (Use with caution)

```python
import pickle
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)
```

**Security note:** Never unpickle untrusted data. Use `InconsistentVersionWarning` to detect version mismatches.

## Parallel Computing

Most estimators and meta-estimators support `n_jobs`:

```python
# Use all cores
model = RandomForestClassifier(n_jobs=-1)

# Use specific number
search = GridSearchCV(model, param_grid, n_jobs=4, cv=5)
```

**Note:** `n_jobs=-1` uses all available CPUs. Set `LOKY_MAX_CPU_COUNT` env var to limit.

## Configuration and Environment

### Global Config

```python
import sklearn

# Thread-local configuration
sklearn.set_config(
    transform_output="pandas",
    enable_metadata_routing=True,
    sparse_interface="sparray",  # Return sparse arrays instead of matrices
    working_memory=2048,  # Min MB to keep in memory
)

# Temporary context
with sklearn.config_context(transform_output="polars"):
    X_transformed = transformer.fit_transform(X)
```

### Sparse Interface (New in 1.9)

```python
# Default: sparse matrices
sklearn.set_config(sparse_interface="spmatrix")

# Use sparse arrays (SciPy sparse array API)
sklearn.set_config(sparse_interface="sparray")
```

**Note:** Default will change to `"sparray"` in future releases. Set explicitly if you need consistency.

### Array API Dispatch

```python
# Enable dispatching to Array API compliant backends
sklearn.set_config(array_api_dispatch=True)

# Works with PyTorch tensors, JAX arrays, etc.
import torch
X_torch = torch.tensor(X, dtype=torch.float32)
model.fit(X_torch, y_torch)
```

## Exceptions and Warnings

| Exception/Warning | When Raised |
|-------------------|-------------|
| `NotFittedError` | Using estimator before `fit()` |
| `ConvergenceWarning` | Algorithm didn't converge (increase `max_iter`) |
| `DataConversionWarning` | Implicit data type conversion |
| `EfficiencyWarning` | Suboptimal computation detected |
| `FitFailedWarning` | Estimator failed during CV fitting |
| `UndefinedMetricWarning` | Metric is undefined (e.g., no positive samples) |
| `PositiveSpectrumWarning` | PSD matrix has negative eigenvalues |
| `InconsistentVersionWarning` | Loading model from different sklearn version |

## Narwhals Dependency (New in 1.9)

Scikit-learn now uses `narwhals` for dataframe interoperability. This simplifies pandas/Polars support and replaces the deprecated dataframe interchange protocol.

```python
# Works with both pandas and polars
import pandas as pd
import polars as pl

df_pandas = pd.DataFrame(X)
df_polars = pl.DataFrame(X)

scaler.fit_transform(df_pandas)  # Returns same type
scaler.fit_transform(df_polars)   # Returns Polars DataFrame
```
