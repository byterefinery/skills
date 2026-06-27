# Classifiers Reference

## Linear Models

### `LogisticRegression(*, penalty="l2", C=1.0, solver="lbfgs", max_iter=100)`
Binary and multiclass logistic regression. The workhorse classifier.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `penalty` | `"l2"` | `"l1"`, `"elasticnet"`, `"none"` — use `l1_ratio` with elasticnet |
| `C` | `1.0` | Inverse regularization strength (smaller = stronger) |
| `solver` | `"lbfgs"` | `"liblinear"` (small data), `"saga"` (l1, multiclass), `"newton-cg"`, `"sag"` |
| `multi_class` | `"auto"` | `"ovr"`, `"multinomial"` — multinomial is more accurate |
| `class_weight` | `None` | `"balanced"` for imbalanced data |
| `max_iter` | `100` | Increase if convergence warning appears |

```python
from sklearn.linear_model import LogisticRegression

# Imbalanced data
clf = LogisticRegression(class_weight="balanced", max_iter=1000)

# L1 regularization (feature selection)
clf = LogisticRegression(penalty="l1", solver="saga", C=0.1)
```

### `LogisticRegressionCV(*, Cs=10, cv=5, scoring=None)`
Cross-validated logistic regression. Selects best `C` automatically.

**1.9 note:** Default `scoring` changing from `None` (accuracy) to `"neg_log_loss"` in v1.11. Set explicitly now.

### `LinearSVC(*, penalty="l2", loss="hinge", dual="auto", C=1.0)`
Linear SVM for classification. Faster than `SVC(kernel="linear")` on large datasets.

- Does not support `predict_proba()` — wrap with `CalibratedClassifierCV`
- Use `dual=False` when `n_samples > n_features`

### `RidgeClassifier(alpha=1.0)` / `RidgeClassifierCV(alphas=None, cv=5)`
Linear classification with L2 regularization.

### `PassiveAggressiveClassifier(C=1.0, warm_start=False)`
Online learning classifier. Supports `partial_fit()`. Good for streaming data.

### `Perceptron(max_iter=1000, tol=0.001)`
Simple online learning algorithm. No regularization by default.

### `SGDClassifier(loss="hinge", *, penalty=None, random_state=None)`
Stochastic gradient descent classifier. Supports many loss functions and `partial_fit()`.

| Loss | Use Case |
|------|----------|
| `"hinge"` | Linear SVM (default) |
| `"log_loss"` | Logistic regression |
| `"modified_huber"` | Probabilities + hinge |
| `"squared_hinge"` | Smooth SVM |
| `"perceptron"` | Perceptron algorithm |

## Tree-Based

### `DecisionTreeClassifier(*, criterion="gini", max_depth=None, random_state=None)`
Single decision tree. Prone to overfitting — use ensembles instead.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `criterion` | `"gini"` | `"entropy"`, `"log_loss"` |
| `max_depth` | `None` | Limit depth to prevent overfitting |
| `min_samples_split` | `2` | Min samples to split a node |
| `min_samples_leaf` | `1` | Min samples in a leaf |
| `class_weight` | `None` | `"balanced"` for imbalanced data |

**1.9:** Tree classifiers now support missing values (NaN) in dense data.

### `ExtraTreeClassifier(*, criterion="gini", random_state=None)`
Extremely randomized tree — random split thresholds instead of optimal search. Used in ExtraTrees ensemble.

## SVM

### `SVC(*, kernel="rbf", C=1.0, gamma="scale")`
Support Vector Classification. Powerful but scales poorly (O(n²) to O(n³)).

| Parameter | Default | Notes |
|-----------|---------|-------|
| `kernel` | `"rbf"` | `"linear"`, `"poly"`, `"sigmoid"`, callable |
| `C` | `1.0` | Regularization (smaller = wider margin) |
| `gamma` | `"scale"` | `"auto"` (1/n_features), float — kernel coefficient |
| `decision_function_shape` | `"ovr"` | `"ovo"` for multiclass |

**1.9 deprecation:** `probability=True` is deprecated (not thread-safe). Use `CalibratedClassifierCV(SVC(), ensemble=False)` instead.

### `NuSVC(*, kernel="rbf", nu=0.5)`
Variant of SVC with `nu` parameter controlling error/outlier tradeoff.

### `LinearSVC` / `LinearSVR`
Linear SVM — use for large datasets where `SVC(kernel="linear")` is too slow.

## Ensemble Methods

### `RandomForestClassifier(*, n_estimators=100, max_features="sqrt", random_state=None)`
Bagged decision trees with feature subsampling. Robust default classifier.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `n_estimators` | `100` | More trees = better (diminishing returns) |
| `max_features` | `"sqrt"` | `"log2"`, float, int — features per split |
| `max_depth` | `None` | Limit tree depth |
| `min_samples_split` | `2` | Min samples to split |
| `class_weight` | `None` | `"balanced"`, dict |
| `n_jobs` | `None` | `-1` for all cores |

**1.9:** `max_samples` as float now interpreted as fraction of `sample_weight.sum()`. Integer `max_samples > n_samples` allowed.

### `ExtraTreesClassifier(*, n_estimators=100, max_features="sqrt")`
Extremely randomized trees ensemble. Faster training, slightly lower accuracy than RandomForest.

### `GradientBoostingClassifier(*, n_estimators=100, learning_rate=0.1)`
Sequentially built trees correcting previous errors.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `n_estimators` | `100` | Number of boosting stages |
| `learning_rate` | `0.1` | Shrinkage (smaller = more trees needed) |
| `max_depth` | `3` | Tree depth (keep shallow for GB) |
| `subsample` | `1.0` | Fraction of samples per tree |

**1.9:** `criterion` parameter deprecated — `"friedman_mse"` was buggy, use `"squared_error"`.

### `HistGradientBoostingClassifier(*, max_iter=100, learning_rate=0.1)`
Histogram-based gradient boosting. Much faster on large datasets, handles missing values natively.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `max_iter` | `100` | Number of trees |
| `learning_rate` | `0.1` | Shrinkage |
| `max_depth` | `None` | `None` = unlimited, typically 3-8 |
| `l2_regularization` | `0.0` | L2 regularization |
| `max_bins` | `255` | Binning granularity |

### `AdaBoostClassifier(*, n_estimators=50, algorithm="SAMME.R")`
Adaptive boosting with weak learners (default: decision stumps).

### `BaggingClassifier(*, n_estimators=10, max_samples=1.0)`
Generic bagging ensemble — wrap any estimator.

### `VotingClassifier(estimators, *, voting="hard")`
Combine multiple classifiers. `voting="soft"` uses averaged probabilities.

```python
from sklearn.ensemble import VotingClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

vc = VotingClassifier([
    ("rf", RandomForestClassifier()),
    ("svm", SVC(probability=True)),  # needed for soft voting
    ("lr", LogisticRegression()),
], voting="soft")
```

### `StackingClassifier(estimators, final_estimator=None, cv=5)`
Stack predictions of base estimators as features for a final estimator.

## Other Classifiers

### `KNeighborsClassifier(*, n_neighbors=5, weights="uniform", algorithm="auto")`
k-Nearest Neighbors. No training phase — stores all data. Scales poorly with n_samples.

### `MLPClassifier(*, hidden_layer_sizes=(100,), max_iter=200)`
Multi-layer perceptron (neural network).

| Parameter | Default | Notes |
|-----------|---------|-------|
| `hidden_layer_sizes` | `(100,)` | Tuple of layer sizes, e.g., `(128, 64, 32)` |
| `activation` | `"relu"` | `"tanh"`, `"logistic"` |
| `solver` | `"adam"` | `"sgd"`, `"lbfgs"` |
| `early_stopping` | `False` | Validate on training split |
| `max_iter` | `200` | Max iterations |

### `GaussianProcessClassifier(*, kernel=None, optimizer="fmin_l_bfgs_b")`
Gaussian process classification (Laplace approximation). Good for small datasets.

### `GaussianNB(*, var_smoothing=1e-9)`
Naive Bayes with Gaussian features. Fast, works well as baseline.

### `MultinomialNB(*, alpha=1.0)` / `BernoulliNB(*, alpha=1.0)`
Naive Bayes for count/binary features respectively. Common in text classification.

### `QDA()` / `LinearDiscriminantAnalysis()`
Quadratic/Linear Discriminant Analysis. LDA also works as dimensionality reduction (`transform()`).

### `CalibratedClassifierCV(estimator, cv=5, method="sigmoid")`
Calibrate probability estimates of any classifier. Use Platt scaling (`"sigmoid"`) or isotonic regression (`"isotonic"`).

**1.9:** Recommended replacement for `SVC(probability=True)`.
