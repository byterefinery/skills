# Model Selection Reference

## Train/Test Split

### `train_test_split(*arrays, test_size=0.25, random_state=None, stratify=None)`
Split data into training and test sets.

```python
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

**`stratify`:** Maintain class distribution in splits. Essential for imbalanced data.

## Cross-Validation Splitters

### `KFold(n_splits=5, shuffle=False, random_state=None)`
Split into k consecutive folds. Set `shuffle=True` for randomized order.

### `StratifiedKFold(n_splits=5, shuffle=False)`
Stratified version of KFold — preserves class proportions in each fold. Use for classification.

### `RepeatedKFold(n_splits=5, n_repeats=10)` / `RepeatedStratifiedKFold()`
Repeat CV multiple times with different shuffles. More robust estimates.

### `ShuffleSplit(n_splits=100, test_size=0.2, train_size=None)`
Random permuted splits. More control than KFold.

### `StratifiedShuffleSplit(n_splits=100, test_size=0.2)`
Stratified random splits.

### `TimeSeriesSplit(n_splits=5)`
For time series — each fold uses earlier data as train, later as test. No shuffling.

```python
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
for train_idx, test_idx in tscv.split(X):
    print(f"Train: {len(train_idx)}, Test: {len(test_idx)}")
```

### `GroupKFold(n_splits=5)` / `GroupShuffleSplit()`
Split by groups — ensures same group never appears in both train and test.

**1.9:** `GroupKFold` now uses stable sorting for consistent splits across runs.

### `LeaveOneOut()` / `LeavePOut(p)`
Leave one/p samples out. Expensive but exhaustive.

### `LeaveOneGroupOut()` / `LeavePGroupsOut()`
Leave group(s) out. For grouped data with known structure.

### `PredefinedSplit(test_fold)`
Use pre-defined train/test splits (e.g., from external source).

### `check_cv(cv, y, classifier=None)`
Validate and return a CV splitter. Returns appropriate default based on data.

## Cross-Validation Functions

### `cross_val_score(estimator, X, y, cv=5, scoring=None)`
Quick single-metric evaluation. Returns array of scores (one per fold).

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5, scoring="f1")
print(f"Mean: {scores.mean():.3f} ± {scores.std():.3f}")
```

### `cross_validate(estimator, X, y, cv=5, scoring=None, return_train_score=False)`
Multi-metric evaluation with detailed output dict.

```python
from sklearn.model_selection import cross_validate
results = cross_validate(
    model, X, y, cv=5,
    scoring=["accuracy", "f1", "precision", "recall"],
    return_train_score=True
)
# results["test_f1"], results["fit_time"], etc.
```

### `cross_val_predict(estimator, X, y, cv=5)`
Get predictions for each sample using CV (sample predicted by model trained without it). Useful for model-agnostic evaluation.

## Hyperparameter Search

### `GridSearchCV(estimator, param_grid, cv=5, scoring=None, n_jobs=None)`
Exhaustive search over parameter grid.

```python
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier

param_grid = {
    "n_estimators": [50, 100, 200],
    "max_depth": [None, 10, 20],
    "min_samples_split": [2, 5, 10],
}

search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid, cv=5, scoring="f1", n_jobs=-1
)
search.fit(X_train, y_train)
print(search.best_params_)
print(search.best_score_)
```

**Pipeline parameter grid:** Use `stepname__param` syntax.

```python
param_grid = {
    "preprocessor__num__scaler__with_mean": [True, False],
    "clf__n_estimators": [50, 100],
}
```

### `RandomizedSearchCV(estimator, param_distributions, n_iter=10, cv=5)`
Random sampling from parameter distributions. More efficient than GridSearch for large spaces.

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

param_dist = {
    "n_estimators": randint(50, 300),
    "max_depth": [None, 10, 20, 30, 50],
    "min_samples_leaf": randint(1, 20),
}

search = RandomizedSearchCV(
    model, param_dist, n_iter=50, cv=5, random_state=42
)
```

### `HalvingGridSearchCV` / `HalvingRandomSearchCV` (experimental)
Successive halving — eliminates poor configurations early. Enable with:
```python
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingGridSearchCV
```

## Learning and Validation Curves

### `learning_curve(estimator, X, y, cv=None, train_sizes=None)`
Plot model performance vs training set size. Diagnoses bias-variance tradeoff.

```python
from sklearn.model_selection import learning_curve
train_sizes, train_scores, val_scores = learning_curve(
    model, X, y, cv=5,
    train_sizes=np.linspace(0.1, 1.0, 10)
)
```

### `validation_curve(estimator, X, y, param_name, param_range, cv=None)`
Plot performance vs a single hyperparameter value.

### `LearningCurveDisplay` / `ValidationCurveDisplay`
Built-in display classes for plotting curves.

## Permutation Importance (model-agnostic)

```python
from sklearn.inspection import permutation_importance
result = permutation_importance(model, X_test, y_test, n_repeats=30, random_state=42)
# result.importances_mean — feature importance ranking
```

## Parameter Utilities

### `ParameterGrid(param_grid)`
Expand parameter grid into list of dicts.

### `ParameterSampler(param_distribution, n_iter, random_state=None)`
Sample from parameter distributions.
