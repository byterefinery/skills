# Preprocessing Reference

## Scaling

### `StandardScaler(*, with_mean=True, with_std=True)`
Zero mean, unit variance. Most common preprocessing step.

```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)  # Never fit_transform on test!
```

### `MinMaxScaler(*, feature_range=(0, 1))`
Scales to a fixed range (default [0, 1]). Sensitive to outliers.

### `MaxAbsScaler()`
Scales by maximum absolute value. Preserves sparsity. Good for sparse data.

### `RobustScaler(*, with_centering=True, with_scaling=True)`
Uses median and IQR — robust to outliers.

### `Normalizer(norm="l2")`
Normalizes samples (rows) to unit norm. Used in text classification.

## Encoding Categorical Variables

### `OneHotEncoder(*, categories=None, handle_unknown="infrequent_if_exist", drop=None)`
Converts categorical features to binary indicator columns.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `handle_unknown` | `"infrequent_if_exist"` | `"ignore"` (zero vector), `"error"` — new in 1.2: infrequent category grouping |
| `drop` | `None` | `"first"` or `"if_binary"` to avoid multicollinearity |
| `sparse_output` | `True` | Set `False` for dense output |

```python
from sklearn.preprocessing import OneHotEncoder
enc = OneHotEncoder(handle_unknown="infrequent_if_exist", drop="first")
X_encoded = enc.fit_transform([["a"], ["b"], ["c"]])
enc.get_feature_names_out(["color"])  # ['color_b', 'color_c']
```

### `OrdinalEncoder(*, categories=None, handle_unknown="use_encoded_value", unknown_value=-1)`
Encodes categoricals as integers. Use when there is natural ordering.

### `TargetEncoder(*, cv=5, smooth=1.0)`
Encodes categoricals using target variable statistics (mean encoding with cross-validation).

**1.9 deprecation:** `shuffle` and `random_state` deprecated — pass a CV generator via `cv` instead.

```python
from sklearn.preprocessing import TargetEncoder
encoder = TargetEncoder(cv=5)
X_encoded = encoder.fit_transform(X_cat, y)
```

## Imputation

### `SimpleImputer(*, strategy="mean", fill_value=None)`
Replace missing values with mean, median, most_frequent, or constant.

| Strategy | Use Case |
|----------|----------|
| `"mean"` | Numerical features (default) |
| `"median"` | Numerical with outliers |
| `"most_frequent"` | Categorical features |
| `"constant"` | Custom fill value via `fill_value` |

### `KNNImputer(*, n_neighbors=5, weights="uniform")`
Impute using k-nearest neighbors. Captures feature correlations.

### `MissingIndicator(*, sparse_threshold=0.10)`
Binary indicator for missing values. Often combined with SimpleImputer in ColumnTransformer.

### `IterativeImputer` (experimental)
Iteratively imputes each feature using other features as predictors. Enable with:
```python
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
```

## Polynomial and Nonlinear

### `PolynomialFeatures(*, degree=2, include_bias=True, interaction_only=False)`
Generate polynomial and interaction features.

```python
# x1, x2 → x1, x2, x1², x1*x2, x2²
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2, include_bias=False)
```

### `SplineTransformer(*, n_knots=5, degree=3, extrapolation="constant")`
B-spline basis transformation. Good for nonlinear relationships.

### `KBinsDiscretizer(*, n_bins=5, strategy="quantile", encode="onehot-dummy")`
Bin continuous features into discrete intervals.

## Transformations

### `FunctionTransformer(func=None, inverse_func=None, validate=True)`
Apply arbitrary function to data. Useful for custom transforms in pipelines.

```python
from sklearn.preprocessing import FunctionTransformer
import numpy as np
log_transform = FunctionTransformer(np.log1p, inverse_func=np.expm1)
```

### `PowerTransformer(method="yeo-johnson", *, standardize=True)`
Apply power transformation toward normality. `"yeo-johnson"` handles negative values.

### `QuantileTransformer(n_quantiles=1000, output_distribution="uniform")`
Transform features to uniform or normal distribution using quantiles. Robust to outliers.

## Label Encoding

### `LabelEncoder()`
Encode string labels as integers (0 to n_classes-1). For targets only — not for features.

### `LabelBinarizer()`
Binary indicator matrix from labels. Useful for one-vs-rest multiclass.

### `MultiLabelBinarizer()`
Transform iterables of iterables into binary indicator matrix. For multi-label classification.

## Binarization

### `Binarizer(threshold=0.0)`
Threshold features to 0/1.

## Utility Functions

| Function | Purpose |
|----------|---------|
| `scale(X)` | In-place StandardScaler equivalent |
| `normalize(X, norm="l2")` | Row-wise normalization |
| `minmax_scale(X, feature_range=(0, 1))` | In-place MinMaxScaler |
| `robust_scale(X)` | In-place RobustScaler |
| `add_dummy_feature(X, value=1.0)` | Add bias/intercept column |
| `binarize(X, threshold=0.0)` | In-place binarization |
| `label_binarize(y, classes=None)` | Label binarization function |

## Common Pipeline Patterns

```python
# Numerical + categorical preprocessing
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

preprocessor = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]), numeric_cols),
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="infrequent_if_exist")),
    ]), categorical_cols),
])

# Full pipeline
pipe = Pipeline([
    ("preprocess", preprocessor),
    ("model", RandomForestClassifier(random_state=42)),
])
```
