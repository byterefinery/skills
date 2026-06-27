# Metrics Reference

## Classification Metrics

### Accuracy and Confusion

| Function | Purpose |
|----------|---------|
| `accuracy_score(y_true, y_pred)` | Fraction of correct predictions |
| `confusion_matrix(y_true, y_pred)` | TP/FP/TN/FN matrix |
| `classification_report(y_true, y_pred)` | Text report: precision, recall, f1 per class |

```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
cm = confusion_matrix(y_true, y_pred)
ConfusionMatrixDisplay(confusion_matrix=cm).plot()
```

### Precision, Recall, F-Score

| Function | Notes |
|----------|-------|
| `precision_score(y_true, y_pred, average="binary")` | TP / (TP + FP) |
| `recall_score(y_true, y_pred, average="binary")` | TP / (TP + FN) |
| `f1_score(y_true, y_pred, average="binary")` | Harmonic mean of precision and recall |
| `fbeta_score(y_true, y_pred, beta=1)` | Weighted F-score (beta > 1 favors recall) |

**`average` options:** `"binary"` (default), `"macro"`, `"weighted"`, `"micro"`, `"samples"`.

- **Macro:** Equal weight per class — good when all classes matter equally
- **Weighted:** Weight by class support — good for imbalanced data
- **Micro:** Global counts — equals accuracy for multiclass

### Probability-Based

| Function | Purpose |
|----------|---------|
| `log_loss(y_true, y_proba)` | Cross-entropy loss (negative log likelihood) |
| `brier_score_loss(y_true, y_prob)` | Mean squared error of probabilities |
| `roc_auc_score(y_true, y_score)` | Area under ROC curve |
| `average_precision_score(y_true, y_score)` | Area under precision-recall curve |
| `hinge_loss(y_true, y_score)` | SVM hinge loss |

### Curve Functions

| Function | Returns |
|----------|---------|
| `roc_curve(y_true, y_score)` | fpr, tpr, thresholds |
| `precision_recall_curve(y_true, y_scores)` | precision, recall, thresholds |
| `det_curve(y_true, y_scores)` | fpr, fnr, thresholds |

**1.9:** `metric_at_thresholds(metric, y_true, y_score)` — compute metric values across all possible thresholds.

### Display Classes

```python
from sklearn.metrics import RocCurveDisplay, PrecisionRecallDisplay, ConfusionMatrixDisplay

# From estimator
RocCurveDisplay.from_estimator(model, X_test, y_test)

# From predictions
PrecisionRecallDisplay.from_predictions(y_true, y_proba[:, 1])

# From CV results (1.9)
PrecisionRecallDisplay.from_cv_results(cv_results, param_name="C")
```

## Regression Metrics

| Function | Formula | Notes |
|----------|---------|-------|
| `mean_squared_error(y_true, y_pred)` | MSE | Default for `RegressorMixin.score()` is R² |
| `root_mean_squared_error(y_true, y_pred)` | RMSE | Same units as target |
| `mean_absolute_error(y_true, y_pred)` | MAE | Robust to outliers |
| `median_absolute_error(y_true, y_pred)` | Median AE | Very robust |
| `r2_score(y_true, y_pred)` | R² | 1 = perfect, 0 = mean predictor |
| `explained_variance_score(y_true, y_pred)` | EVS | Similar to R² but allows shift |
| `max_error(y_true, y_pred)` | Max error | Worst case |

### Quantile/Deviance Metrics

| Function | Use Case |
|----------|----------|
| `mean_pinball_loss(y_true, y_pred, quantile=0.5)` | Quantile regression |
| `mean_squared_log_error(y_true, y_pred)` | Penalizes relative errors |
| `mean_absolute_percentage_error(y_true, y_pred)` | Percentage error |
| `d2_tweedie_score()` / `d2_pinball_score()` / `d2_absolute_error_score()` | Generalized R² variants |

## Clustering Metrics

### With Ground Truth

| Function | Range | Notes |
|----------|-------|-------|
| `adjusted_rand_score(labels_true, labels_pred)` | [-1, 1] | 1 = perfect match |
| `normalized_mutual_info_score()` | [0, 1] | Information-theoretic |
| `homogeneity_completeness_v_measure()` | — | Three complementary scores |

### Without Ground Truth

| Function | Notes |
|----------|-------|
| `silhouette_score(X, labels)` | [-1, 1], higher = better separated clusters |
| `calinski_harabasz_score(X, labels)` | Higher = better (variance ratio) |
| `davies_bouldin_score(X, labels)` | Lower = better (similarity index) |

## Pairwise Metrics

| Function | Purpose |
|----------|---------|
| `pairwise_distances(X, Y=None, metric="euclidean")` | Distance matrix |
| `pairwise_kernels(X, Y=None, kernel="linear")` | Kernel matrix |
| `euclidean_distances(X, Y)` | Euclidean distance matrix |
| `nan_euclidean_distances(X, Y)` | Handles NaN values |

## Scorers

Scorers are callable objects wrapping metric functions for use in model selection.

```python
from sklearn.metrics import make_scorer, get_scorer, get_scorer_names

# Built-in scorers
get_scorer("f1_weighted")
get_scorer_names()  # List all available

# Custom scorer
from sklearn.metrics import mean_absolute_error
mae_scorer = make_scorer(mean_absolute_error, greater_is_better=False)

# With custom parameters
custom_scorer = make_scorer(
    fbeta_score, beta=2, greater_is_better=True
)
```

**Scorer naming convention:** `{metric_name}` or `neg_{metric_name}` for loss functions. E.g., `"neg_mean_squared_error"`.

## 1.9 Changes

- `cohen_kappa_score` now has `replace_undefined_by` parameter for division-by-zero handling
- `confusion_matrix_at_thresholds` — `pos_label` and `sample_weight` as positional args deprecated
- `log_loss` / `d2_log_loss_score`: `y_pred` parameter renamed to `y_proba`
- `metric_at_thresholds()` added for computing metrics across all thresholds
