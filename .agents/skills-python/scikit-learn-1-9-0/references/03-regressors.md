# Regressors Reference

## Linear Models

### `LinearRegression(*, fit_intercept=True, positive=False)`
Ordinary least squares. No regularization — can overfit with many features.

```python
from sklearn.linear_model import LinearRegression
model = LinearRegression().fit(X, y)
model.coef_  # Weights
model.intercept_  # Bias
```

### `Ridge(alpha=1.0, *, fit_intercept=True, solver="auto")`
Linear regression with L2 regularization.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `alpha` | `1.0` | Regularization strength (larger = more shrinkage) |
| `solver` | `"auto"` | `"svd"`, `"cholesky"`, `"lsqr"`, `"saga"` — saga for sparse/large data |
| `positive` | `False` | Constrain coefficients to be positive |

### `RidgeCV(alphas=(0.1, 1.0, 10.0), *, cv=5, gcv_mode=None)`
Cross-validated Ridge. Selects best `alpha`.

**1.9:** `gcv_mode="auto"` now equivalent to `"eigen"`, picks cheaper option based on n_features vs n_samples.

### `Lasso(alpha=1.0, *, max_iter=1000, solver="auto")`
Linear regression with L1 regularization — produces sparse coefficients (feature selection).

| Parameter | Default | Notes |
|-----------|---------|-------|
| `alpha` | `1.0` | Regularization strength |
| `solver` | `"auto"` | `"coord_descent"` (default), `"lsqr"`, `"saga"` — saga supports `positive` |
| `max_iter` | `1000` | Increase if convergence warning |
| `positive` | `False` | Constrain coefficients positive |

### `LassoCV(*, alphas=None, cv=5, max_iter=1000)`
Cross-validated Lasso. Selects best `alpha`.

**1.9:** Now accounts for `positive` parameter when computing max alpha.

### `ElasticNet(alpha=1.0, l1_ratio=0.5)`
Combines L1 and L2 regularization. `l1_ratio=0` → Ridge, `l1_ratio=1` → Lasso.

### `ElasticNetCV(*, alphas=None, l1_ratio=0.5, cv=5)`
Cross-validated ElasticNet.

**1.9:** Can now fit pure Ridge (`l1_ratio=0`) without dual gap warnings.

### `MultiTaskLasso` / `MultiTaskElasticNet`
Lasso/ElasticNet for multi-output regression (multiple target variables).

**1.9:** Now support sparse `X` and `sample_weight`.

### `BayesianRidge(*, alpha_1=1e-6, lambda_1=1e-6)`
Bayesian linear regression with automatic relevance determination.

### `ARDRegression(*, alpha_1=1e-6, lambda_1=1e-6)`
Automatic Relevance Detection. More aggressive feature selection than BayesianRidge.

**1.9:** Now correctly centers test features during `predict()` for variance computation.

### `HuberRegressor(*, epsilon=1.35, alpha=1.0)`
Robust linear regression — less sensitive to outliers than OLS.

### `TheilSenRegressor(*, max_subpopulation=200_000, random_state=None)`
Robust regression using Theil-Sen estimator. Exact for small data, subsampled for large.

### `RANSACRegressor(estimator=LinearRegression(), *, residual_threshold=None)`
RANdom SAmple Consensus — fits model to inliers, ignores outliers.

### `PassiveAggressiveRegressor()` / `SGDRegressor()`
Online learning regressors with `partial_fit()`.

### `QuantileRegressor(*, quantile=0.5, solver="highs")`
Linear regression targeting a specific quantile of the target distribution.

### `OrthogonalMatchingPursuit(*, n_nonzero_coefs=10)`
Greedy algorithm for sparse approximation.

## GLM (Generalized Linear Models)

### `PoissonRegressor(*, alpha=0.0, solver="lbfgs")`
Poisson regression for count data (non-negative integer targets).

### `GammaRegressor(*, alpha=0.0, solver="lbfgs")`
Gamma regression for positive continuous targets.

### `TweedieRegressor(*, power=1.0, alpha=0.0)`
Tweedie regression — `power=0` → Gaussian, `1` → Poisson, `2` → Gamma.

## Tree-Based

### `DecisionTreeRegressor(*, criterion="squared_error", max_depth=None)`
Single decision tree for regression.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `criterion` | `"squared_error"` | `"absolute_error"`, `"poisson"`, `"friedman_mse"` (deprecated) |
| `max_depth` | `None` | Limit depth to prevent overfitting |
| `min_samples_leaf` | `1` | Min samples in a leaf |

**1.9:** All criteria now support missing values (NaN) in dense data. `criterion="friedman_mse"` deprecated — use `"squared_error"`.

### `ExtraTreeRegressor(*, criterion="squared_error")`
Extremely randomized tree for regression.

## Ensemble Methods

### `RandomForestRegressor(*, n_estimators=100, max_features="sqrt")`
Bagged decision trees for regression. Same parameters as classifier variant.

**1.9:** `max_samples` behavior updated — float as fraction of `sample_weight.sum()`, integer `> n_samples` allowed.

### `ExtraTreesRegressor(*, n_estimators=100)`
Extremely randomized trees ensemble for regression.

### `GradientBoostingRegressor(*, n_estimators=100, learning_rate=0.1)`
Sequentially built trees for regression.

**1.9:** `criterion` parameter deprecated — use `"squared_error"`.

### `HistGradientBoostingRegressor(*, max_iter=100, learning_rate=0.1)`
Histogram-based gradient boosting for regression. Fast on large data, handles NaN natively.

### `AdaBoostRegressor(*, n_estimators=50, loss="linear")`
Adaptive boosting for regression. `loss` can be `"linear"`, `"square"`, `"exponential"`.

### `BaggingRegressor(*, n_estimators=10)` / `VotingRegressor()` / `StackingRegressor()`
Same patterns as classification variants.

## Other Regressors

### `KNeighborsRegressor(*, n_neighbors=5, weights="uniform")`
k-Nearest Neighbors regression. Predicts by averaging neighbors' targets.

### `RadiusNeighborsRegressor(*, radius=1.0)`
Fixed-radius nearest neighbors regression.

### `MLPRegressor(*, hidden_layer_sizes=(100,), max_iter=200)`
Multi-layer perceptron for regression. Same parameters as `MLPClassifier`.

### `GaussianProcessRegressor(*, kernel=None, alpha=1e-10, optimizer="fmin_l_bfgs_b")`
Gaussian process regression. Provides uncertainty estimates via `predict(X, return_std=True)`.

**1.9:** Default kernel `ConstantKernel() * RBF()` hyperparameters now optimized by default when `optimizer` is not `None`.

### `KernelRidge(alpha=1.0, kernel="linear")`
Kernel ridge regression — equivalent to SVM regression with dual formulation.

### `NuSVR(*, nu=0.4, kernel="rbf")`
Support Vector Regression with `nu` parameter.

**1.9:** Raises informative error when fitted with all-zero sample weights.

### `SVR(*, kernel="rbf", C=1.0, epsilon=0.1)`
Support Vector Regression. `epsilon` controls the insensitive loss band.

### `TransformedTargetRegressor(regressor, transformer)`
Transform target before fitting, inverse-transform predictions. Useful for log-transforming skewed targets.

```python
from sklearn.compose import TransformedTargetRegressor
from sklearn.preprocessing import PowerTransformer
from sklearn.ensemble import RandomForestRegressor

model = TransformedTargetRegressor(
    regressor=RandomForestRegressor(),
    transformer=PowerTransformer()
)
```
