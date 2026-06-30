# Covariate Forecasting with XReg

## Overview

XReg (Exogenous Regression) extends TimesFM with covariate-aware forecasting. It combines the foundation model's zero-shot forecasting with in-context linear regression on exogenous variables. Requires `pip install timesfm[xreg]` (adds JAX + scikit-learn).

## XReg Modes

### `"xreg + timesfm"`

1. Fit a linear model on the target time series using covariates
2. Compute residuals (target − xreg prediction)
3. Forecast residuals with TimesFM
4. Add xreg forecast back to TimesFM forecast

**Best when**: Covariates have a strong linear relationship with the target. The linear model captures the covariate effect, and TimesFM forecasts the remaining pattern.

### `"timesfm + xreg"`

1. Run TimesFM forecast on the raw target
2. Compute residuals (target − TimesFM forecast on context)
3. Fit a linear model on the residuals using covariates
4. Add xreg forecast to TimesFM forecast

**Best when**: TimesFM captures the base pattern well, and covariates explain systematic deviations from that pattern.

## Required Configuration

XReg requires `return_backcast=True` in `ForecastConfig`:

```python
model.compile(
    timesfm.ForecastConfig(
        max_context=1024,
        max_horizon=256,
        normalize_inputs=True,
        return_backcast=True,  # Required for XReg
    )
)
```

## Covariate Types

### Dynamic Numerical Covariates

Time-varying numeric features with values for both context and horizon:

```python
dynamic_numerical_covariates = {
    "price": [
        np.concatenate([historical_prices, future_prices]),  # series 1
        np.concatenate([historical_prices_2, future_prices_2]),  # series 2
    ],
    "temperature": [
        np.concatenate([temp_history, temp_forecast]),
    ],
}
```

Each array must have length `len(context) + horizon`.

### Dynamic Categorical Covariates

Time-varying categorical features (integers or strings):

```python
dynamic_categorical_covariates = {
    "day_of_week": [
        np.array([0, 1, 2, 3, 4, 5, 6] * 100),  # repeats for context + horizon
    ],
    "holiday": [
        np.array(["no", "no", "yes", "no", ...]),  # string values OK
    ],
}
```

### Static Numerical Covariates

Fixed numeric features, one value per series:

```python
static_numerical_covariates = {
    "store_capacity": [100.0, 200.0, 150.0],
    "latitude": [40.7, 34.0, 51.5],
}
```

### Static Categorical Covariates

Fixed categorical features, one value per series:

```python
static_categorical_covariates = {
    "region": ["east", "west", "central"],
    "store_type": ["supermarket", "convenience", "supermarket"],
}
```

## Full Example

```python
import numpy as np
import timesfm

model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
    "google/timesfm-2.5-200m-pytorch"
)
model.compile(
    timesfm.ForecastConfig(
        max_context=512,
        max_horizon=128,
        normalize_inputs=True,
        return_backcast=True,
        fix_quantile_crossing=True,
    )
)

# Historical data
sales = [np.random.randn(200).cumsum() + 100 for _ in range(3)]

# Covariates spanning context + horizon
horizon = 24
prices = [np.random.uniform(5, 15, 200 + horizon) for _ in range(3)]
dow = [np.array([i % 7 for i in range(200 + horizon)]) for _ in range(3)]

point, quantiles = model.forecast_with_covariates(
    inputs=sales,
    dynamic_numerical_covariates={"price": prices},
    dynamic_categorical_covariates={"dow": dow},
    static_categorical_covariates={"region": ["north", "south", "east"]},
    xreg_mode="xreg + timesfm",
    ridge=0.0,
)
```

## Internal Mechanics

### `BatchedInContextXRegLinear`

The XReg module uses `BatchedInContextXRegLinear` from `timesfm.utils.xreg_lib`:

1. **Covariate matrix construction**:
   - Dynamic numerical covariates are normalized (zero mean, unit variance)
   - Categorical covariates are one-hot encoded (with first category dropped)
   - Static covariates are broadcast to match dynamic lengths
   - An intercept column is added

2. **Linear fit via pseudoinverse**:
   ```
   β = pinv(X_train^T × X_train + ridge × I) × X_train^T × y
   ŷ = X_test × β
   ```

3. **JAX acceleration**: The pseudoinverse computation runs on GPU/TPU via JAX with automatic padding to power-of-2 dimensions.

### Normalization

Per-series normalization is applied to the XReg target:

```python
def normalize(batch):
    stats = [(mean(x), std(x)) for x in batch]
    return [(x - m) / s for x, (m, s) in zip(batch, stats)], stats

def renormalize(batch, stats):
    return [x * s + m for x, (m, s) in zip(batch, stats)]
```

## Performance Considerations

- **JAX first-call overhead**: The first call to `forecast_with_covariates()` triggers JAX compilation. Subsequent calls are faster.
- **`force_on_cpu=True`**: Use when GPU memory is tight; avoids moving data to accelerator memory and prevents precision loss.
- **`max_rows_per_col`**: Subsample training rows for faster fitting when context is very long. Set to `0` for no subsampling.
- **Ridge penalty**: Small ridge values (e.g., 0.01) can stabilize the fit when covariates are collinear.
- **Categorical encoding**: String-valued categoricals are supported but slower than integer codes. Use integer codes when possible.

## Common Patterns

### Price Elasticity Forecasting

```python
point, quantiles = model.forecast_with_covariates(
    inputs=[demand_history],
    dynamic_numerical_covariates={
        "price": [np.concatenate([past_prices, future_prices])],
        "competitor_price": [np.concatenate([past_comp, future_comp])],
    },
    xreg_mode="xreg + timesfm",
)
```

### Promotional Impact

```python
point, quantiles = model.forecast_with_covariates(
    inputs=[sales],
    dynamic_categorical_covariates={
        "promotion": [np.array(["none", "sale", "none", ...])],
    },
    dynamic_numerical_covariates={
        "discount_pct": [np.array([0, 0.2, 0, ...])],
    },
    xreg_mode="timesfm + xreg",
)
```

### Multi-Store with Region Effects

```python
point, quantiles = model.forecast_with_covariates(
    inputs=[store1, store2, store3],
    dynamic_numerical_covariates={
        "temperature": [temp1, temp2, temp3],
    },
    static_categorical_covariates={
        "region": ["north", "south", "east"],
        "store_class": ["A", "B", "A"],
    },
    xreg_mode="xreg + timesfm",
)
```

## Validation

```python
# Verify covariate lengths match context + horizon
for name, values in dynamic_numerical_covariates.items():
    for i, (inp, cov) in enumerate(zip(inputs, values)):
        assert len(cov) == len(inp) + horizon, \
            f"Covariate {name}[{i}] length {len(cov)} != {len(inp) + horizon}"
```
