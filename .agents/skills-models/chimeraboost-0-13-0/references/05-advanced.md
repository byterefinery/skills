# Advanced Topics

## Callbacks

Per-round fit hooks for live monitoring and custom stopping:

```python
def callback(iteration, train_loss, val_loss, model):
    print(f"Round {iteration}: train={train_loss:.4f} val={val_loss:.4f}")
    # Return True to request early stop
    return val_loss > 0.5

m = ChimeraBoostClassifier(n_estimators=200, random_state=0)
m.fit(Xtr, ytr, eval_set=(Xte, yte), callbacks=callback)
```

- Callback signature: `cb(iteration, train_loss, val_loss, model)`
- `iteration` is 0-indexed
- Return `True` to stop early; return `False` or `None` to continue
- Can be a single callable or a list of callables
- **Not supported with `n_ensembles > 1`** (members fit in parallel processes)

## staged_predict()

Yield prediction after each successive tree:

```python
r = ChimeraBoostRegressor(n_estimators=50, random_state=0).fit(Xtr, ytr)
for stage_pred in r.staged_predict(Xte):
    # stage_pred shape: (n_samples,)
    pass

# Final stage equals predict()
stages = list(r.staged_predict(Xte))
assert np.allclose(stages[-1], r.predict(Xte))
assert len(stages) == r.best_iteration_
```

- Not available with `n_ensembles > 1` (raises `NotImplementedError`)
- Useful for plotting learning curves from a single fit

## validation_history_

Per-round validation loss recorded during fit:

```python
m = ChimeraBoostClassifier(n_estimators=1000, early_stopping_rounds=20, random_state=0)
m.fit(Xtr, ytr, eval_set=(Xte, yte))

hist = m.validation_history_
best = int(np.argmin(hist)) + 1  # == m.best_iteration_
print(f"Best iteration: {best}, rounds run: {len(hist)}")
```

- Length equals rounds actually run (best + patience) when early stopping is active
- Length equals `n_estimators` when `early_stopping=False` with `eval_set`
- Empty when no validation split is available
- For bagged models: list of members' histories
- For classifiers: log loss values; for regressors: RMSE-space loss values

## Hyperparameter Tuning

### Key Parameters to Tune

| Priority | Parameter | Range | Effect |
|---|---|---|---|
| High | `depth` | 4–10 | Model capacity. Default 6 is conservative. |
| High | `n_ensembles` | 1–20 | Variance reduction via bagging. |
| Medium | `l2_leaf_reg` | 0.1–10 | Leaf smoothing. Default 1.0. |
| Medium | `learning_rate` | 0.01–0.3 | Shrinkage. Default 0.1 (auto). |
| Medium | `subsample` | 0.5–1.0 | Row sampling. Below 1.0 uses MVS. |
| Medium | `colsample` | 0.3–1.0 | Feature sampling. |
| Low | `max_bins` | 64–256 | Histogram resolution. |
| Low | `cat_smoothing` | 0.1–10 | Categorical encoding strength. |
| Low | `cat_n_permutations` | 2–8 | Ordered encoding permutations. |

### GridSearchCV

```python
from sklearn.model_selection import GridSearchCV

search = GridSearchCV(
    ChimeraBoostRegressor(cat_features=[0, 3], random_state=0),
    {
        "depth": [6, 8, 10],
        "l2_leaf_reg": [1.0, 3.0, 10.0],
        "subsample": [0.8, 1.0],
        "colsample": [0.7, 1.0],
    },
    cv=5,
    scoring="neg_root_mean_squared_error",
)
search.fit(X, y)
print(search.best_params_)
```

Set `cat_features` on the constructor so `GridSearchCV` carries it (a fit-only kwarg can't be grid-searched).

### Random Search

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

search = RandomizedSearchCV(
    ChimeraBoostRegressor(random_state=0),
    {
        "depth": randint(4, 11),
        "l2_leaf_reg": uniform(0.1, 10.0),
        "subsample": uniform(0.5, 0.5),
        "n_ensembles": randint(1, 11),
    },
    n_iter=30,
    cv=5,
)
search.fit(X, y)
```

## Reproducibility

```python
m = ChimeraBoostRegressor(
    random_state=0,        # seed
    thread_count=4,        # fixed threads for deterministic reductions
).fit(Xtr, ytr)
```

- `random_state` alone is not enough for full determinism
- Floating-point reductions across numba threads can vary
- Pin `thread_count` to a specific value for exact reproducibility
- `thread_count=None` or `-1` uses all detected cores

## Performance Tips

### Thread Count

```python
# All cores (default)
m = ChimeraBoostRegressor(thread_count=None).fit(Xtr, ytr)

# Specific count
m = ChimeraBoostRegressor(thread_count=4).fit(Xtr, ytr)

# Thread count does not change predictions (histogram sums are deterministic)
```

### Bagging with Parallel Jobs

```python
reg = ChimeraBoostRegressor(
    n_ensembles=10,
    ensemble_n_jobs=-1,   # parallel processes
    random_state=0,
).fit(Xtr, ytr)
```

### Large Interaction-Heavy Data

```python
reg = ChimeraBoostRegressor(
    depth=10,
    linear_leaves=True,
    n_estimators=3000,
    early_stopping_rounds=100,
    random_state=0,
).fit(Xtr, ytr)
```

### Wide Categorical Data

```python
# Force cat_combinations on wide all-categorical data
clf = ChimeraBoostClassifier(cat_combinations=True, random_state=0)
clf.fit(Xtr, ytr, cat_features=list(range(Xtr.shape[1])))
```

Auto mode caps at 1000 pairs and 50M cells as resource guards.

## Cross-Validation

```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(
    ChimeraBoostRegressor(random_state=0),
    X, y, cv=5,
    scoring="neg_root_mean_squared_error",
)
print(f"CV RMSE: {-scores.mean():.4f} (+/- {scores.std():.4f})")
```

## Save and Load

```python
import joblib

joblib.dump(model, "model.joblib")
model = joblib.load("model.joblib")
```

Standard scikit-learn pickling. No ChimeraBoost-specific serialization.

## Input Data Formats

- **NumPy arrays** — `dtype=float64` for numeric-only, `dtype=object` when mixing with categoricals
- **pandas DataFrames** — column names captured as `feature_names_in_`; names enforced at predict time
- **PyArrow tables** — `.column_names` used (not `.columns` which is column data)
- **Not supported**: scipy sparse matrices, masked arrays, complex data, infinity values

## Feature Name Enforcement

At predict time, if the model was fit with a DataFrame (capturing column names), passing a DataFrame with different column names or order raises `ValueError`. This prevents silently wrong predictions from reordered columns.

```python
# Warns if one side has names and the other doesn't
# Raises if names disagree
model.predict(X_test_different_columns)  # ValueError
```

For maximum inference throughput, skip the finiteness scan via sklearn's config:

```python
import sklearn
sklearn.set_config(assume_finite=True)
```
