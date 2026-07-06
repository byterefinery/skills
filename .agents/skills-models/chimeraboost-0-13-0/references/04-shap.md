# Exact TreeSHAP

## Overview

`model.shap_values(X)` returns exact interventional TreeSHAP feature attributions — an additive decomposition of each prediction into per-feature contributions.

```python
phi = model.shap_values(X)        # (n_samples, n_features)
base = model.expected_value_      # baseline, set by the call
```

## Exact, Not Sampled

Most SHAP tooling approximates by sampling feature coalitions. ChimeraBoost computes it exactly because oblivious trees split on the same feature at every node of a level. A depth-D tree involves at most D distinct features, so the coalition game has at most D players and all `2**D` coalitions are enumerated directly in a numba kernel (64 evaluations per tree at depth 6).

This is the interventional formulation of TreeSHAP, integrated over a background distribution.

## Efficiency Property

Contributions plus baseline reconstruct the prediction to floating-point tolerance:

```python
recon = phi[i].sum() + base
assert abs(recon - model.predict(X)[i]) < 1e-6  # holds to ~1e-14
```

This is the Shapley efficiency property. `feature_importances_` has no such guarantee — it measures split structure only and ignores per-leaf linear models.

## What the Numbers Mean

`phi[i, j]` is feature `j`'s signed contribution to the raw score of row `i`, measured against `expected_value_` (mean raw score over the background):

- **Regressor**: contributions to the predicted target value
- **Binary classifier**: contributions to the pre-temperature log-odds of the positive class (margin space)

Per-leaf linear models are included exactly. A leaf predicting `intercept + slope * (x - center)` folds its slope into the attribution.

## Global Importance

Average absolute contributions for a prediction-faithful global ranking:

```python
global_importance = np.abs(phi).mean(axis=0)
for j in np.argsort(global_importance)[::-1][:10]:
    print(f"feature {j}: {global_importance[j]:.4f}")
```

## Explaining One Prediction

```python
i = 0
print(f"baseline: {base:.3f}")
for j in np.argsort(np.abs(phi[i]))[::-1][:5]:
    direction = "up" if phi[i, j] > 0 else "down"
    print(f"  feature {j}: {phi[i, j]:+.3f} ({direction})")
print(f"  prediction: {phi[i].sum() + base:.3f}")
```

## Background Distribution

SHAP is defined against a reference. The background defaults to a sample of the training data captured at fit time. Override it:

```python
phi = model.shap_values(X_test, X_background=X_reference)
```

`expected_value_` is the mean prediction over whichever background is used. Cost scales linearly with background size; the default sample keeps it around 3 ms per row at depth 6 with 200 background rows.

## Bagged Models

When `n_ensembles > 1`, attributions are averaged across members:
- **Regression**: exact (bag prediction is members' mean, Shapley values are linear)
- **Classification**: additive surrogate for the soft-voted probability

## Categorical Features

SHAP maps back to the original feature space. If the model was fit with `cat_features=[1]` on a 2-column input, `shap_values` returns shape `(n, 2)` — not the wider internal (target-encoded / combo) matrix. Efficiency still holds.

## Limits

- **Binary classification and regression only** — multiclass raises `NotImplementedError`
- **Log-odds space for classifiers** — not probability space
- **Explains model behavior** — not causal effects

## SHAP vs Feature Importance

| | `feature_importances_` | `shap_values` |
|---|---|---|
| Measures | total split gain | contribution to each prediction |
| Granularity | global only | per-prediction and global |
| Includes linear leaves | no | yes |
| Reconstructs output | no | yes |
| Cost | free (tracked at fit) | milliseconds per row |

Use gain for a free global glance; use SHAP for faithful or per-prediction explanation.
