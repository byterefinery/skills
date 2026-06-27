---
name: scikit-learn-1-9-0
description: >
  Comprehensive guide to scikit-learn 1.9.0 — the Python machine learning library.
  Use when working with ML models, pipelines, preprocessing, model selection, metrics,
  or any data science task using scikit-learn. Covers classification, regression,
  clustering, dimensionality reduction, ensemble methods, hyperparameter tuning,
  cross-validation, feature engineering, and more. Trigger on: sklearn, scikit-learn,
  machine learning, ML pipeline, model training, cross-validation, GridSearchCV,
  Random Forest, SVM, logistic regression, PCA, KMeans, train_test_split, metrics.
metadata:
  tags:
    - ml
    - data-science
    - python
---

# scikit-learn 1.9.0

## Overview

Scikit-learn 1.9.0 (June 2026) is the Python machine learning library built on NumPy, SciPy, and joblib. All estimators follow a unified API: `fit()`, `predict()` (predictors), `transform()` (transformers). The library ships with ~130+ estimators across classification, regression, clustering, dimensionality reduction, preprocessing, model selection, and metrics.

**Key 1.9 additions:**
- **Callback API** (`sklearn.callback`) — progress bars and scoring monitors during fitting
- **FrozenEstimator** (`sklearn.frozen`) — wrap fitted estimators to prevent re-fitting in pipelines
- **sparse_interface config** — control sparse matrix vs array output
- **narwhals dependency** — improved pandas/Polars dataframe support
- `metric_at_thresholds()` for computing metrics across all thresholds
- Tree models now handle missing values (NaN) natively in dense data

**Dependencies:** Python 3.11+, NumPy >= 1.24.1, SciPy >= 1.10.0, joblib >= 1.4.0, narwhals >= 2.0.1, threadpoolctl >= 3.5.0.

## Usage

### Estimator Pattern (all models)

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)          # Train
y_pred = model.predict(X_test)       # Predict
y_proba = model.predict_proba(X_test)  # Probabilities (classifiers)
score = model.score(X_test, y_test)    # Default metric
```

### Pipeline Pattern (recommended for production)

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", RandomForestClassifier(random_state=42)),
])
pipe.fit(X_train, y_train)
pipe.predict(X_test)
```

### Model Selection Pattern

```python
from sklearn.model_selection import cross_validate, GridSearchCV

# Quick evaluation
cv_results = cross_validate(pipe, X, y, cv=5,
                            scoring=["accuracy", "f1"])

# Hyperparameter tuning
search = GridSearchCV(
    pipe,
    param_grid={"clf__n_estimators": [50, 100, 200]},
    cv=5, scoring="f1"
)
search.fit(X_train, y_train)
search.best_params_
```

### Column-Wise Preprocessing (mixed feature types)

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numeric_cols),
    ("cat", OneHotEncoder(handle_unknown="infrequent_if_exist"), categorical_cols),
])
```

### Callbacks (new in 1.9)

```python
from sklearn.callback import ProgressBar, ScoringMonitor

# During fitting of supported estimators
model.fit(X, y, callbacks=[ProgressBar()])
```

## Gotchas

- **`load_boston` removed since 1.2** — use `fetch_california_housing` or `fetch_openml(name="house_prices")` instead. The Boston dataset had ethical issues (racially biased variable).
- **`SVC(probability=True)` deprecated in 1.9** — not thread-safe. Use `CalibratedClassifierCV(svc, ensemble=False)` for probability estimates instead.
- **`criterion="friedman_mse"` deprecated** in tree regressors — it was buggy and identical to `"squared_error"`. Use `"squared_error"` instead.
- **`TargetEncoder(shuffle=...)` deprecated** — pass a CV generator via `cv` argument instead.
- **`LogisticRegressionCV(scoring)` default changing** — will switch from `None` (accuracy) to `"neg_log_loss"` in v1.11. Explicitly set `scoring` now.
- **`n_alphas` deprecated** in `lasso_path`/`enet_path` — pass `alphas` directly as int or array-like.
- **`sample_weight` with all zeros raises ValueError** — validate weights before passing.
- **Pipeline parameter access uses double underscore** — `pipe.set_params(clf__C=0.1)` not `pipe.clf.C = 0.1`.
- **`clone()` resets fitted state** — use `sklearn.base.clone()` to get a fresh unfitted copy with same hyperparameters.
- **RandomForest/ExtraTrees `max_samples` behavior changed** — when float, interpreted as fraction of `sample_weight.sum()`, not `X.shape[0]`. Integer `max_samples > n_samples` now allowed.
- **`FrozenEstimator.__sklearn_clone__` returns self** — cloning a frozen estimator doesn't clone the inner estimator. This is intentional (prevents re-fitting).
- **Sparse interface config defaults to `"spmatrix"`** — will change to `"sparray"` in future releases. Set explicitly if you need sparse arrays now.

## References

- [01-core-api](references/01-core-api.md) — BaseEstimator, mixins, Pipeline, ColumnTransformer, clone, config
- [02-classifiers](references/02-classifiers.md) — All classification estimators and their key parameters
- [03-regressors](references/03-regressors.md) — All regression estimators and their key parameters
- [04-clustering](references/04-clustering.md) — Clustering algorithms: KMeans, DBSCAN, Agglomerative, etc.
- [05-preprocessing](references/05-preprocessing.md) — Scalers, encoders, imputers, transformers
- [06-model-selection](references/06-model-selection.md) — CV splitters, GridSearchCV, cross_validate, learning curves
- [07-metrics](references/07-metrics.md) — Classification/regression metrics, scorers, display classes
- [08-feature-selection](references/08-feature-selection.md) — RFE, SelectKBest, VarianceThreshold, mutual info
- [09-dimensionality-reduction](references/09-dimensionality-reduction.md) — PCA, SVD, NMF, manifold methods
- [10-data-io](references/10-data-io.md) — Built-in datasets, fetch_openml, synthetic data generators
- [11-advanced-topics](references/11-advanced-topics.md) — Callbacks, metadata routing, FrozenEstimator, experimental features
