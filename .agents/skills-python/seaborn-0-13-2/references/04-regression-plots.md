# Regression Plots

Plots showing relationships with fitted regression models.

## regplot

Scatter plot with linear regression fit.

```python
sns.regplot(data=df, x="total_bill", y="tip", ci=95, order=1, scatter=True)
```

**Parameters:**
- `x`, `y` — column names or array-like
- `x_estimator` — callable to aggregate x values (e.g., `np.mean`)
- `x_bins` — number of bins for binning x before aggregation
- `x_ci` — confidence interval for x bins (`"ci"`, `"sd"`, or int percentage)
- `scatter` — `True` (default, show scatter points), `False` (regression line only)
- `fit_reg` — `True` (default, draw regression line), `False` (scatter only)
- `ci` — confidence interval width (default 95), or `None` to omit error band
- `n_boot` — bootstrap iterations (default 1000)
- `units` — column name for repeated measures
- `seed` — random seed
- `order` — polynomial order (default 1)
- `logistic` — `True` for logistic regression (requires statsmodels)
- `lowess` — `True` for LOWESS smooth (non-parametric, no confidence interval)
- `robust` — `True` for robust regression (less sensitive to outliers)
- `logx` — `True` if the relationship has log-x (linear regression on log(x))
- `x_partial`, `y_partial` — column names to partial out (regress out confounders)
- `truncate` — `True` (default, truncate to data range), `False` (extend to plot limits)
- `dropna` — `True` (default, drop rows with NaN in x, y, or hue)
- `x_jitter`, `y_jitter` — add jitter to scatter points (float amount)
- `label` — label for legend
- `color` — single color
- `marker` — scatter marker (default `"o"`)
- `scatter_kws` — dict passed to scatter plotting
- `line_kws` — dict passed to line plotting
- `ax` — target Axes

## lmplot

Figure-level regression plot with faceting.

```python
g = sns.lmplot(
    data=df,
    x="total_bill", y="tip",
    hue="time", col="day", row="smoker",
    height=4, aspect=1.2,
    order=1, ci=95, scatter=True
)
```

**Parameters:**
- All `regplot` parameters for regression fitting
- `col`, `row` — faceting columns
- `col_wrap` — max columns before wrapping
- `height`, `aspect` — subplot dimensions
- `sharex`, `sharey` — axis sharing across facets
- `legend` — `True` (default), `False`
- `legend_out` — `True` (default, legend outside plot), `False`
- `markers` — marker style (default `"o"`)
- `palette` — color palette
- `hue_order`, `col_order`, `row_order` — ordering control

**Return value:** `FacetGrid` object.

## residplot

Residual plot — scatter of residuals from regression fit.

```python
sns.residplot(data=df, x="total_bill", y="tip", order=1, lowess=False)
```

**Parameters:**
- `x`, `y` — column names or array-like
- `x_partial`, `y_partial` — columns to partial out
- `lowess` — `True` for non-parametric LOWESS fit
- `order` — polynomial order (default 1)
- `robust` — `True` for robust regression
- `dropna` — `True` (default)
- `label`, `color` — styling
- `scatter_kws`, `line_kws` — dicts passed to underlying plotting
- `ax` — target Axes

**Use case:** Diagnostic plot for checking regression assumptions. Points should be randomly scattered around y=0 if the model fits well. Systematic patterns indicate model misspecification.

## Partial Regression

Both `regplot` and `residplot` support `x_partial` and `y_partial` to control for confounding variables:

```python
# Regress out 'size' from both x and y before plotting
sns.residplot(data=df, x="total_bill", y="tip", x_partial=["size"], y_partial=["size"])
```

This shows the relationship between x and y after removing the linear effect of the partial variables.

## Objects API: Regression

```python
import seaborn.objects as so

# Scatter with regression line
(so.Plot(df, x="total_bill", y="tip", color="time")
    .add(so.Dot)
    .add(so.Line, so.PolyFit(degree=1))
    .configure(xlabel="Total Bill", ylabel="Tip"))

# Residual plot
(so.Plot(residuals_df, x="fitted", y="residual")
    .add(so.Dot)
    .add(so.Line, y=0, linewidth=1, color="red")
    .configure(xlabel="Fitted", ylabel="Residual"))
```
