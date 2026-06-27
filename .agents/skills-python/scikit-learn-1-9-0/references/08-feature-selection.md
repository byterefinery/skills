# Feature Selection Reference

## Univariate Selection

### `SelectKBest(score_func=f_classif, k=10)`
Select top-k features by univariate statistical test.

| Score Function | Task |
|----------------|------|
| `f_classif` | ANOVA F-value (classification) |
| `mutual_info_classif` | Mutual information (classification) |
| `chi2` | Chi-squared (classification, non-negative features) |
| `f_regression` | F-value (regression) |
| `mutual_info_regression` | Mutual information (regression) |

```python
from sklearn.feature_selection import SelectKBest, f_classif
selector = SelectKBest(score_func=f_classif, k=50)
X_selected = selector.fit_transform(X, y)
selector.scores_  # Test scores per feature
selector.pvalues_  # P-values
```

### `SelectPercentile(score_func=f_classif, percentile=10)`
Select features by percentile threshold instead of fixed count.

### `GenericUnivariateSelect(score_func=f_classif, mode="percentile", param=10)`
Unified interface — `mode` can be `"percentile"`, `"k_best"`, or `"fpr"`/`"fdr"`/`"fwe"`.

### `SelectFpr` / `SelectFdr` / `SelectFwe`
Select by false discovery/positive error rate thresholds.

## Model-Based Selection

### `SelectFromModel(estimator, threshold=None, max_features=None)`
Select features based on model weights/importances.

```python
from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import RandomForestClassifier

# Uses mean_decrease_impurity by default
selector = SelectFromModel(RandomForestClassifier(random_state=42))
X_selected = selector.fit_transform(X, y)
selector.get_support()  # Boolean mask of selected features

# Custom threshold
selector = SelectFromModel(
    model, threshold="mean", max_features=50
)

# With importance getter (for models without feature_importances_)
selector = SelectFromModel(
    model, importance_getter=lambda est: est.coef_
)
```

**1.9:** Now supports sparse feature importance matrices/arrays.

## Recursive Feature Elimination

### `RFE(estimator, n_features_to_select=1, step=1)`
Recursively removes least important features.

```python
from sklearn.feature_selection import RFE
rfe = RFE(RandomForestClassifier(), n_features_to_select=10)
X_selected = rfe.fit_transform(X, y)
rfe.ranking_  # Feature ranking (1 = best)
```

**1.9:** Now uses stable sorting for deterministic results when importances are tied.

### `RFECV(estimator, step=1, cv=5, scoring=None)`
RFE with cross-validation to find optimal number of features.

## Variance Threshold

### `VarianceThreshold(threshold=0.0)`
Remove features with variance below threshold. Removes constant/near-constant features.

```python
from sklearn.feature_selection import VarianceThreshold
# Remove features that are the same for >99% of samples
selector = VarianceThreshold(threshold=0.01)
```

## Sequential Feature Selection

### `SequentialFeatureSelector(estimator, n_features_to_select=10, direction="forward")`
Iteratively add/remove features based on CV score.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `direction` | `"forward"` | `"backward"` — start with all, remove worst |
| `n_features_to_select` | `10` | Number of features to select (or int for final count) |
| `cv` | `None` | CV splitter for scoring |

```python
from sklearn.feature_selection import SequentialFeatureSelector
sfs = SequentialFeatureSelector(
    RandomForestClassifier(),
    n_features_to_select=10,
    direction="forward",
    cv=5
)
X_selected = sfs.fit_transform(X, y)
sfs.get_support()  # Selected features
```

## Mutual Information Functions

### `mutual_info_classif(X, y, *, discrete_features=False, n_neighbors=3)`
Estimate mutual information between features and target (classification).

### `mutual_info_regression(X, y, *, discrete_features=False, n_neighbors=3)`
Same for regression.

**Tip:** Set `discrete_features=True` (or array of booleans) for categorical features to get better estimates.

## SelectorMixin API

All selectors implement:
- `get_support(indices=False)` — Boolean mask or indices of selected features
- `transform(X)` — Reduce X to selected features
- `inverse_transform(X)` — Expand X back to original dimensionality (zeros in unselected columns)
- `get_feature_names_out(input_features)` — Names of selected features

## Common Patterns

```python
# Feature selection in a pipeline
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.ensemble import RandomForestClassifier

pipe = Pipeline([
    ("select", SelectKBest(f_classif, k=50)),
    ("clf", RandomForestClassifier(random_state=42)),
])

# Grid search over feature selection
param_grid = {
    "select__k": [10, 25, 50, 100],
    "clf__n_estimators": [50, 100],
}

# SelectFromModel with L1-penalized model (automatic feature selection)
from sklearn.linear_model import LogisticRegression
selector = SelectFromModel(LogisticRegression(penalty="l1", solver="saga"))
```
