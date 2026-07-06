# Scikit-Learn API Reference

## Estimators

### XGBClassifier

Binary and multi-class classification.

```python
from xgboost import XGBClassifier

clf = XGBClassifier(
    n_estimators=200,          # Number of boosting rounds
    max_depth=6,               # Max tree depth (0 = unlimited)
    learning_rate=0.1,         # Step shrinkage (alias: eta)
    subsample=0.8,             # Row subsample ratio per iteration
    colsample_bytree=0.8,      # Column subsample ratio per tree
    objective="binary:logistic",  # Auto-set for binary; "multi:softprob" for multi-class
    eval_metric="logloss",     # "auc", "error", "mlogloss" for multi-class
    early_stopping_rounds=10,  # Stop if no improvement for N rounds
    random_state=42,           # Reproducibility
    n_jobs=-1,                 # Parallel threads (-1 = all)
    tree_method="hist",        # Default; "hist", "approx", "exact"
    device=None,               # "cuda", "cuda:0", "gpu", None (CPU)
    enable_categorical=True,   # Native categorical support
    use_label_encoder=False,   # Required: do not set to True
)

clf.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=10)
```

**Key methods:**
- `predict(X)` — class labels
- `predict_proba(X)` — class probabilities
- `predict_log_proba(X)` — log probabilities
- `get_booster()` — underlying `Booster` object
- `get_booster().get_score(importance_type="gain")` — feature importance dict
- `save_model("model.json")` / `load_model("model.json")`
- `evals_result_` — dict of evaluation history after fit

**Multi-class:**
```python
clf = XGBClassifier(
    objective="multi:softprob",
    num_class=10,
    eval_metric="mlogloss",
)
```

### XGBRegressor

Regression with configurable objective.

```python
from xgboost import XGBRegressor

reg = XGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    objective="reg:squarederror",  # Default; see objectives for alternatives
    eval_metric="rmse",            # "mae", "rmsle", "mape"
    early_stopping_rounds=10,
    random_state=42,
)
reg.fit(X_train, y_train, eval_set=[(X_val, y_val)])
```

Supports multi-output regression (`y` with shape `(n, k)`).

**Special objectives:**
- `reg:squarederror` — squared loss (default)
- `reg:squaredlogerror` — squared log loss (labels > -1)
- `reg:pseudohubererror` — differentiable absolute loss
- `reg:absoluteerror` — L1 loss
- `reg:quantileerror` — quantile regression (set `quantile_alpha`)
- `reg:expectileerror` — expectile regression (set `expectile_alpha`, new in 3.3.0)
- `reg:gamma` — gamma regression
- `reg:tweedie` — Tweedie regression (set `tweedie_variance_power`)
- `count:poisson` — Poisson regression for count data
- `survival:cox` — Cox proportional hazards
- `survival:aft` — Accelerated failure time

### XGBRanker

Learning to rank.

```python
from xgboost import XGBRanker

ranker = XGBRanker(
    objective="rank:ndcg",       # Default; also "rank:map", "rank:pairwise"
    eval_metric=["ndcg@3", "map@5"],
    n_estimators=200,
    learning_rate=0.1,
    lambdarank_pair_method="topk",
    lambdarank_num_pair_per_sample=10,
)

# group = array of group sizes; data must be sorted by query
ranker.fit(X_train, y_train, group=[10, 20, 15, ...])

# Or use qid column
ranker.fit(X_train, y_train, qid=[1,1,1,2,2,2,...])
```

### XGBRFClassifier / XGBRFRegressor

XGBoost's random forest implementation.

```python
from xgboost import XGBRFClassifier, XGBRFRegressor

rf = XGBRFClassifier(
    n_estimators=100,
    max_depth=6,
    subsample=0.8,
    colsample_bynode=0.8,
    reg_lambda=1e-5,
    random_state=42,
)
rf.fit(X_train, y_train)
```

Note: `early_stopping_rounds` and `callbacks` are not supported for RF estimators.

## Common Parameters

| Parameter | Default | Description |
|---|---|---|
| `n_estimators` | 100 | Number of boosting rounds |
| `max_depth` | 6 | Maximum tree depth (0 = unlimited) |
| `learning_rate` | 0.3 | Step shrinkage |
| `subsample` | 1.0 | Row subsample ratio |
| `sampling_method` | "uniform" | "uniform" or "gradient_based" |
| `colsample_bytree` | 1.0 | Column subsample per tree |
| `colsample_bylevel` | 1.0 | Column subsample per level |
| `colsample_bynode` | 1.0 | Column subsample per split |
| `reg_alpha` | 0 | L1 regularization |
| `reg_lambda` | 1 | L2 regularization |
| `gamma` | 0 | Minimum loss reduction to split |
| `min_child_weight` | 1 | Minimum hessian sum in child |
| `max_delta_step` | 0 | Max leaf output change |
| `tree_method` | "hist" | "hist", "approx", "exact", "auto" |
| `grow_policy` | "depthwise" | "depthwise" or "lossguide" |
| `max_leaves` | 0 | Max leaves per tree (with lossguide) |
| `max_bin` | 256 | Max bins for hist/approx |
| `booster` | "gbtree" | "gbtree", "dart" (gblinear deprecated) |
| `device` | None | "cuda", "cuda:0", "gpu", None |
| `n_jobs` | 1 | Parallel threads (-1 = all) |
| `random_state` | None | Random seed |
| `missing` | NaN | Value to treat as missing |
| `enable_categorical` | True | Native categorical support |
| `monotone_constraints` | None | Dict or string of constraints |
| `interaction_constraints` | None | Feature interaction groups |
| `scale_pos_weight` | 1 | Positive/negative weight balance |
| `base_score` | auto | Initial prediction score |
| `eval_metric` | auto | Evaluation metric(s) |
| `early_stopping_rounds` | None | Early stopping patience |
| `callbacks` | None | List of TrainingCallback |

## fit() Method

```python
model.fit(
    X,                          # Features
    y,                          # Labels
    sample_weight=None,         # Instance weights
    base_margin=None,           # Base margin per instance
    eval_set=None,              # [(X_val, y_val), ...]
    verbose=True,               # Print eval metrics (True/False/int)
    xgb_model=None,             # Continue training from existing model
    sample_weight_eval_set=None,# Weights for each eval set
    base_margin_eval_set=None,  # Base margins for each eval set
)
```

### Continue Training

```python
# Resume from existing model
model.fit(X_train, y_train, xgb_model=existing_model)

# Resume from file
model.fit(X_train, y_train, xgb_model="checkpoint.json")
```

## predict() Method

```python
# Standard prediction
preds = model.predict(X)

# With iteration range (use best n trees)
preds = model.predict(X, iteration_range=(0, 50))

# Raw margin output (before transformation)
margins = model.predict(X, output_margin=True)

# Feature contributions (SHAP-like)
contribs = model.predict(X, pred_contribs=True)
# Shape: (n_samples, n_features + 1), last column is bias

# Both predictions and contributions
preds, contribs = model.predict(X, pred_contribs=True, approx_contribs=False)
```

## Model Persistence

```python
# Save
model.save_model("model.json")    # JSON (recommended)
model.save_model("model.raw")     # Binary

# Load
model.load_model("model.json")

# Serialize to bytes
import io
buf = io.BytesIO()
model.get_booster().save_raw(buf)
raw_bytes = buf.getvalue()

# Load from bytes
booster = xgb.Booster()
booster.load_model(raw_bytes)
```

## Integration with scikit-learn

XGBoost estimators are full scikit-learn compatible:

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, cross_val_score

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("xgb", XGBRegressor(n_estimators=100, random_state=42)),
])

# Grid search
param_grid = {
    "xgb__max_depth": [3, 6, 9],
    "xgb__learning_rate": [0.01, 0.1, 0.3],
    "xgb__subsample": [0.6, 0.8, 1.0],
}

search = GridSearchCV(pipe, param_grid, cv=5, scoring="neg_mean_squared_error")
search.fit(X, y)
print(search.best_params_)

# Cross-validation
scores = cross_val_score(pipe, X, y, cv=5, scoring="neg_mean_squared_error")
```

## evals_result_

After `fit()`, access evaluation history:

```python
model.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_val, y_val)])

# Access results
results = model.evals_result_
# {
#   "validation_0": {"rmse": [0.5, 0.4, ...]},
#   "validation_1": {"rmse": [0.6, 0.55, ...]},
# }

# Best iteration (if early stopping was used)
best_iter = model.best_iteration
```
