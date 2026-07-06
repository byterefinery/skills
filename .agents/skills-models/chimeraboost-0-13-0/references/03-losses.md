# Loss Functions

Each loss provides three methods:
- `init(y, sample_weight)` — initial raw score (starting prediction)
- `grad_hess(y, raw)` — gradient and hessian of loss w.r.t. raw score
- `eval(y, raw, sample_weight)` — scalar loss value for early stopping/logging

Raw scores are the additive model output before any link function.

## RMSE (Squared Error)

```python
reg = ChimeraBoostRegressor(loss="RMSE")  # default
```

- **init**: weighted mean of y
- **grad**: `raw - y`
- **hess**: `1` (constant)
- **eval**: weighted RMSE
- **transform**: identity (raw score = prediction)
- Supports `linear_leaves` and `leaf_estimation_iterations`

## MAE (Mean Absolute Error)

```python
reg = ChimeraBoostRegressor(loss="MAE")
```

- **init**: weighted median of y
- **grad**: `sign(raw - y)` (sign gradient picks tree structure only)
- **hess**: `1` (constant)
- **eval**: weighted MAE
- **transform**: identity
- **Leaf values**: set to weighted median of residuals (minimizer of absolute error)
- Does NOT support `linear_leaves` (leaf values are residual median, not Newton step)

## Quantile (Pinball Loss)

```python
reg = ChimeraBoostRegressor(loss="Quantile", alpha=0.9)
```

- **init**: weighted quantile of y at level alpha
- **grad**: `-alpha` where `y >= raw`, `1 - alpha` otherwise
- **hess**: `1` (constant)
- **eval**: weighted pinball loss
- **transform**: identity
- **Leaf values**: weighted quantile of residuals at level alpha
- Default `depth=4` (shallower to avoid overfitting tail quantiles)
- Does NOT support `linear_leaves`

## Logloss (Binary Cross-Entropy)

Used internally by `ChimeraBoostClassifier` for binary classification.

- **init**: log-odds of weighted mean probability
- **grad**: `sigmoid(raw) - y`
- **hess**: `max(p * (1 - p), 1e-6)` where `p = sigmoid(raw)`
- **eval**: weighted cross-entropy
- **transform**: numerically stable sigmoid

## MultiSoftmax (Multinomial Logistic)

Used internally by `ChimeraBoostClassifier` for multiclass (3+ classes).

- **init**: log of class proportions (shape `(K,)`)
- **grad**: `softmax(F) - Y_onehot`
- **hess**: `max(P * (1 - P), 1e-6)`
- **eval**: weighted softmax cross-entropy
- **transform**: softmax (numerically stable via max subtraction)

## Loss Selection Summary

| Task | Loss | Configurable? |
|---|---|---|
| Regression (default) | RMSE | No (fixed) |
| Regression (median) | MAE | Set `loss="MAE"` |
| Regression (quantile) | Quantile | Set `loss="Quantile"`, `alpha=...` |
| Binary classification | Logloss | Auto-detected |
| Multiclass classification | MultiSoftmax | Auto-detected |

## Numerical Stability

- Sigmoid uses branch-on-sign to avoid overflow: `exp(-|z|)` is always in `[0, 1]`
- Softmax subtracts max before exponentiation
- Hessian values are floored at `1e-6` to prevent division by zero
- Probability values are clipped to `[1e-9, 1 - 1e-9]` in eval to prevent log(0)
