# scipy.stats Reference

Probability distributions, hypothesis tests, summary statistics, and more.

## Table of Contents

- [Probability Distributions](#probability-distributions)
- [Continuous Distributions (Key)](#continuous-distributions-key)
- [Discrete Distributions (Key)](#discrete-distributions-key)
- [Multivariate Distributions](#multivariate-distributions)
- [Distribution Methods](#distribution-methods)
- [Summary Statistics](#summary-statistics)
- [Hypothesis Tests](#hypothesis-tests)
- [Correlation / Association Tests](#correlation--association-tests)
- [Resampling and Monte Carlo](#resampling-and-monte-carlo)
- [Multiple Hypothesis Testing](#multiple-hypothesis-testing)
- [Kernel Density Estimation](#kernel-density-estimation)
- [Transformations](#transformations)
- [Other Statistical Functionality](#other-statistical-functionality)

## Probability Distributions

Every distribution is an object instance of `rv_continuous` or `rv_discrete`. They share a common API.

```python
from scipy.stats import norm, t, chi2, expon, poisson

# All distributions support:
dist.pdf(x)        # probability density / mass
dist.cdf(x)        # cumulative distribution
dist.sf(x)         # survival function (1 - cdf), more accurate for tail
dist.ppf(q)        # percent point function (inverse CDF)
dist.isf(q)        # inverse survival function
dist.icdf(q)       # alias for ppf
dist.rvs(size=n)   # random variates
dist.mean()        # mean
dist.var()         # variance
dist.std()         # standard deviation
dist.stats(moments='mvsk')  # mean, variance, skewness, kurtosis
```

### Parameter convention

All distributions use `loc` (location/shift) and `scale` (scale/spread) as the last two keyword arguments. Shape parameters come before them.

```python
# Normal: N(mu=5, sigma=2)
norm.pdf(x, loc=5, scale=2)
# or positionally:
norm.pdf(x, 0, 5, 2)  # shape args (none for norm), loc=5, scale=2
```

## Continuous Distributions (Key)

| Name | Distribution | Shape Parameters |
|---|---|---|
| `norm` | Normal (Gaussian) | — |
| `lognorm` | Log-normal | `s` (sigma) |
| `expon` | Exponential | — |
| `gamma` | Gamma | `a` (shape) |
| `beta` | Beta | `a`, `b` |
| `chi2` | Chi-squared | `df` (degrees of freedom) |
| `t` | Student's t | `df` |
| `f` | F (Snedecor-F) | `df1`, `df2` |
| `uniform` | Uniform | — |
| `cauchy` | Cauchy | — |
| `laplace` | Laplace (double exponential) | — |
| `weibull_min` | Weibull | `c` (shape) |
| `pareto` | Pareto | `b` (shape) |
| `gumbel_r` | Gumbel (extreme value) | — |
| `vonmises` | Von Mises (circular normal) | `kappa` |
| `wishart` | Wishart (matrix-variate) | `df`, `scale` |
| `multivariate_normal` | Multivariate normal | `mean`, `cov` |

SciPy provides 126 continuous distributions total. Use `stats.__all__` to list all.

## Discrete Distributions (Key)

| Name | Distribution | Parameters |
|---|---|---|
| `binom` | Binomial | `n`, `p` |
| `poisson` | Poisson | `mu` |
| `geom` | Geometric | `p` |
| `hypergeom` | Hypergeometric | `M`, `n`, `k` |
| `negbinom` | Negative binomial | `n`, `p` |
| `bernoulli` | Bernoulli | `p` |
| `binom` | Binomial | `n`, `p` |
| `randint` | Discrete uniform | `low`, `high` |

## Multivariate Distributions

| Name | Description |
|---|---|
| `multivariate_normal` | Multivariate Gaussian |
| `dirichlet` | Dirichlet distribution |
| `wishart` | Wishart distribution |
| `matrix_variate_normal` | Matrix normal |

```python
from scipy.stats import multivariate_normal

mean = [0, 0]
cov = [[1, 0.5], [0.5, 1]]
mvn = multivariate_normal(mean=mean, cov=cov)
x = np.array([[0, 0], [1, 1]])
mvn.pdf(x)  # evaluate at multiple points
```

## Distribution Methods

### Fitting data to a distribution

```python
from scipy.stats import norm

data = np.random.normal(5, 2, size=1000)
params = norm.fit(data)  # returns (loc, scale) for norm
# params ≈ (5.0, 2.0)

# With fixed shape parameters:
gamma.fit(data, floc=0)  # fix loc=0, estimate shape and scale
```

### Freezing a distribution

```python
# Freeze parameters for repeated calls
frozen = norm(loc=5, scale=2)
frozen.pdf(5)   # same as norm.pdf(5, loc=5, scale=2)
frozen.rvs(100)  # draw samples
```

## Summary Statistics

| Function | Description |
|---|---|
| `describe(data)` | Full descriptive stats (nobs, minmax, mean, variance, skewness, kurtosis) |
| `gmean(a)` | Geometric mean |
| `hmean(a)` | Harmonic mean |
| `skew(a)` | Skewness |
| `kurtosis(a)` | Kurtosis (Fisher/Pearson) |
| `moment(a, n)` | n-th central moment |
| `sem(a)` | Standard error of the mean |
| `iqr(a)` | Interquartile range |
| `mode(a, keepdims=False)` | Modal value(s) |
| `entropy(pk, qk=None)` | Shannon entropy (or KL divergence if qk given) |
| `variation(a)` | Coefficient of variation |
| `rankdata(a)` | Rank data (handles ties) |
| `trim_mean(a, proportiontocut)` | Truncated mean |
| `median_abs_deviation(a)` | Median absolute deviation |

## Hypothesis Tests

Tests return `(statistic, pvalue)`. Some also return confidence intervals.

### One-sample / paired tests

| Function | Test |
|---|---|
| `ttest_1samp(a, popmean)` | One-sample t-test |
| `ttest_rel(a, b)` | Paired t-test |
| `shapiro(a)` | Shapiro-Wilk normality test |
| `anderson(a, dist='norm')` | Anderson-Darling test |
| `ks_1samp(a, cdf)` | Kolmogorov-Smirnov one-sample |
| `chisquare(f_obs, f_exp=None)` | Chi-square goodness-of-fit |
| `binomtest(k, n, p=0.5)` | Exact binomial test |
| `skewtest(a)` | Test for skewness |
| `kurtosistest(a)` | Test for kurtosis |
| `normaltest(a)` | Combined skewness + kurtosis test |
| `jarque_bera(a)` | Jarque-Bera normality test |

### Two-sample / independent tests

| Function | Test |
|---|---|
| `ttest_ind(a, b, equal_var=True)` | Independent t-test (Student's if equal_var, Welch's if not) |
| `mannwhitneyu(x, y)` | Mann-Whitney U test (nonparametric) |
| `ranksums(x, y)` | Anderson-Darling rank-sums |
| `ks_2samp(data1, data2)` | Kolmogorov-Smirnov two-sample |
| `welch_ttest(a, b)` | Welch's t-test (unequal variance) |

### Multiple-sample tests

| Function | Test |
|---|---|
| `f_oneway(*arrays)` | One-way ANOVA F-test |
| `kruskal(*arrays)` | Kruskal-Wallis H-test (nonparametric ANOVA) |
| `friedmanchisquare(*arrays)` | Friedman test (repeated measures) |
| `bartlett(*arrays)` | Bartlett's test for equal variances |
| `levene(*arrays)` | Levene's test for equal variances |
| `tukey_hsd(*arrays)` | Tukey's HSD post-hoc test |

## Correlation / Association Tests

| Function | Description |
|---|---|
| `pearsonr(x, y)` | Pearson correlation + p-value |
| `spearmanr(x, y)` | Spearman rank correlation |
| `kendalltau(x, y)` | Kendall's tau |
| `pointbiserialr(x, y)` | Point-biserial correlation |
| `linregress(x, y)` | Simple linear regression (slope, intercept, rvalue, pvalue, stderr) |
| `theilslopes(x, y)` | Theil-Sen robust linear regression |
| `siegelslopes(x, y)` | Siegel robust regression |
| `chatterjeexi(x, y)` | Chatterjee's correlation |

## Resampling and Monte Carlo

| Function | Description |
|---|---|
| `bootstrap((a, b), statistic, n_resamples=9999)` | Nonparametric bootstrap CI |
| `permutation_test(data, func, alternative='two-sided')` | Permutation test |
| `monte_carlo_test(data, null_result, func, ...)` | Monte Carlo hypothesis test |
| `power(statistic, alternative, p_value)` | Post-hoc power analysis |

```python
from scipy.stats import bootstrap

data = (group1, group2)
result = bootstrap(data, lambda x: x[0].mean() - x[1].mean(), confidence_interval=0.95)
print(result.confidence_interval)  # (low, high)
```

## Multiple Hypothesis Testing

| Function | Description |
|---|---|
| `false_discovery_control(pvalues, method='bs')` | FDR correction (Benjamini-Hochberg or Benjamini-Yekutieli) |
| `combine_pvalues(pvalues, method='fisher')` | Combine p-values (Fisher, Stouffer, etc.) |

## Kernel Density Estimation

### `gaussian_kde(data, bw_method=None)`

Univariate/multivariate kernel density estimation.

```python
from scipy.stats import gaussian_kde

data = np.random.normal(0, 1, size=1000)
kde = gaussian_kde(data)
x_eval = np.linspace(-3, 3, 200)
pdf_est = kde(x_eval)  # estimated PDF at evaluation points
```

## Transformations

| Function | Description |
|---|---|
| `boxcox(a, lmbda=None)` | Box-Cox power transformation |
| `yeojohnson(a, lmbda=None)` | Yeo-Johnson transformation |
| `power()` | Power transform for distributions |

## Other Statistical Functionality

### Contingency tables (`scipy.stats.contingency`)

- `contingency.margins()`, `contingency.odd_ratio()`, `contingency.cramers_v()`

### Masked statistics (`scipy.stats.mstats`)

Statistics that handle masked arrays (missing data):
- `mstats.describe()`, `mstats.gmean()`, `mstats.kurtosis()`, `mstats.skew()`

### Quasi-Monte Carlo (`scipy.stats.qmc`)

- `qmc.Sobol(d)`, `qmc.Halton(d)`, `qmc.MLPQ(d)` — QMC samplers
- `qmc.scale(points, xmin, xmax)` — scale to hyperrectangle
- `qmc.discrepancy()`, `qmc.centred_discrepancy()` — quality metrics
