# scipy.stats Reference (1.18.1)

Probability distributions, hypothesis tests, summary statistics, and more.

## Table of Contents

- [Probability Distributions](#probability-distributions)
- [Continuous Distributions (Key)](#continuous-distributions-key)
- [Discrete Distributions (Key)](#discrete-distributions-key)
- [Multivariate Distributions](#multivariate-distributions)
- [Summary Statistics](#summary-statistics)
- [Hypothesis Tests](#hypothesis-tests)
- [Correlation / Association Tests](#correlation--association-tests)
- [Resampling and Monte Carlo](#resampling-and-monte-carlo)
- [Multiple Hypothesis Testing](#multiple-hypothesis-testing)
- [Kernel Density Estimation](#kernel-density-estimation)
- [Transformations](#transformations)
- [Submodules](#submodules)

## Probability Distributions

Every distribution is an object (`rv_continuous`, `rv_discrete`, or `rv_histogram`). They share a common method family:

```python
from scipy import stats

dist.pdf(x)   / dist.pmf(x)      # density / mass
dist.logpdf(x) / dist.logpmf(x)  # log density / mass
dist.cdf(x)                 # cumulative distribution
dist.sf(x)                  # survival function (1 - cdf), more accurate in the tail
dist.ppf(q)                 # quantile (inverse CDF); dist.icdf is an alias
dist.isf(q)                 # inverse survival function
dist.rvs(size=n)            # random variates
dist.mean() / dist.var() / dist.std()
dist.skew() / dist.kurt()   # skewness / kurtosis
dist.interval(alpha)         # central interval containing (1-alpha) probability
dist.fit(data)               # parameter estimation (floc/fscale fix parameters)
```

**Parameter convention:** shape parameters first, then `loc` (location) and `scale` (spread) as the last two keyword arguments — not `mu`/`sigma`.

```python
# Normal N(mu=5, sigma=2)
stats.norm.pdf(x, loc=5, scale=2)
```

**1.18.0 behavior change:** `multinomial` returns NaNs when the category probability rows/arrays (`p`) do not sum to unity, and `multinomial.rvs` raises — the old implicit adjustment of the last element is gone. Also `rankdata` always returns a floating-point dtype now.

## Continuous Distributions (Key)

| Name | Distribution | Shape Parameters |
|---|---|---|
| `norm` | Normal (Gaussian) | — |
| `lognorm` | Log-normal | `s` |
| `expon` | Exponential | — |
| `gamma` | Gamma | `a` |
| `beta` | Beta | `a`, `b` |
| `chi2` | Chi-squared | `df` |
| `t` | Student's t | `df` |
| `f` | F (Snedecor) | `df1`, `df2` |
| `uniform` | Uniform | — |
| `cauchy` | Cauchy | — |
| `laplace` | Laplace | — |
| `weibull_min` | Weibull | `c` |
| `pareto` | Pareto | `b` |
| `gumbel_r` | Gumbel (extreme value) | — |
| `vonmises` | Von Mises (circular) | `kappa` |

Also available: `levy`, `levy_l`, `levy_stable`, `wrapcauchy`, `vonmises_line`, `tukeylambda`, `wald`, `weibull_max`, `rice`, `ncf`, `nct`, `ncx2`, and many more (each has a dedicated reference page in the user guide).

## Discrete Distributions (Key)

| Name | Distribution | Parameters |
|---|---|---|
| `binom` | Binomial | `n`, `p` |
| `poisson` | Poisson | `mu` |
| `geom` | Geometric | `p` |
| `hypergeom` | Hypergeometric | `M`, `n`, `k` |
| `nbinom` | Negative binomial | `n`, `p` |
| `bernoulli` | Bernoulli | `p` |
| `randint` | Discrete uniform | `low`, `high` |

Also: `nchypergeom_fisher`, `nchypergeom_wallenius`, `betanbinom`, `betabinom`, `logser`, `dlaplace`, `boltzmann`, `planck`, `zipf`, `zipfian`, `yulesimon`.

## Multivariate Distributions

| Name | Description |
|---|---|
| `multivariate_normal` | Multivariate Gaussian |
| `dirichlet` | Dirichlet distribution |
| `wishart` | Wishart distribution |

```python
from scipy.stats import multivariate_normal

mvn = multivariate_normal(mean=[0, 0], cov=[[1, 0.5], [0.5, 1]])
mvn.pdf([[0, 0], [1, 1]])  # evaluate at multiple points
```

Freezing and fitting:

```python
frozen = stats.norm(loc=5, scale=2)
frozen.pdf(5)      # same as stats.norm.pdf(5, loc=5, scale=2)
frozen.rvs(100)    # draw samples

params = stats.norm.fit(data)   # → (loc, scale) for norm
```

## Summary Statistics

| Function | Description |
|---|---|
| `describe(data)` | Full descriptive stats (nobs, min/max, mean, variance, skewness, kurtosis) |
| `gmean(a)` / `hmean(a)` | Geometric / harmonic mean |
| `skew(a)` / `kurtosis(a)` | Skewness / Fisher kurtosis |
| `moment(a, order=1)` | Central moment |
| `lmoment(x, orders)` | Lower partial moments |
| `sem(a)` | Standard error of the mean |
| `iqr(a)` | Interquartile range |
| `mode(a, keepdims=False)` | Modal value(s) |
| `median_abs_deviation(a)` | Median absolute deviation |
| `entropy(pk, qk=None)` | Shannon entropy (KL divergence if `qk` given) |
| `differential_entropy(x)` | Differential entropy |
| `variation(a)` | Coefficient of variation |
| `gstd(a, axis=0, ddof=1)` | Generalized standard deviation |
| `rankdata(a)` | Rank data (handles ties) — always float dtype since 1.18.0 |
| `trim_mean(a, proportiontocut)` | Truncated mean |
| `bayes_mvs(x, alpha)` / `mvsdist(x, alpha)` | Bayesian mean/variance estimates (multivariate) |

### Frequency statistics

`quantile(x, p, *, method='linear', axis=0, nan_policy='propagate', ...)` (several interpolation `method`s), `estimated_cdf`, `cumfreq`, `relfreq`, `percentileofscore`, `scoreatpercentile`, `tiecorrect`.

## Hypothesis Tests

Tests return a result object with `statistic` and `pvalue` attributes (tuple-unpacking also works): `stat, p = ttest_ind(a, b)`.

### One-sample / paired tests

| Function | Test |
|---|---|
| `ttest_1samp(a, popmean)` | One-sample t-test |
| `ttest_rel(a, b)` | Paired t-test |
| `binomtest(count, n=None, p=0.5, alternative='two-sided')` | Exact binomial test |
| `wilcoxon(x, y=None, correction=...)` | Paired sign-rank |
| `median_test` | Fligner-Policello |
| `shapiro(a)` | Shapiro-Wilk normality |
| `anderson(a, dist='norm')` | Anderson-Darling |
| `normaltest(a)` | D'Agostino-Pearson (skew + kurtosis) |
| `jarque_bera(a)` | Jarque-Bera normality |
| `skewtest(a)` / `kurtosistest(a)` | Skewness / kurtosis tests |
| `ks_1samp(a, cdf)` | Kolmogorov-Smirnov one-sample |
| `chisquare(f_obs, f_exp=None)` | Chi-square goodness-of-fit |
| `power_divergence`, `quantile_test`, `goodness_of_fit` | Related GOF tools |

### Two-sample / independent tests

| Function | Test |
|---|---|
| `ttest_ind(a, b, equal_var=True)` | Independent t-test (Welch's when `equal_var=False`) |
| `ttest_ind_from_stats(mean1, std1, nobs1, mean2, std2, nobs2)` | From summary statistics |
| `mannwhitneyu(x, y)` | Mann-Whitney U (nonparametric) |
| `ranksums(x, y)` | Rank-sums |
| `brunnermunzel(x, y)`, `bws_test(x, y)` | Brunner-Münzel / Breslow-Wolz-Stehlik |
| `ks_2samp(data1, data2)` | Two-sample Kolmogorov-Smirnov |
| `poisson_means_test` | Two-sample Poisson means |
| `friedmanchisquare(*arrays)` | Friedman (repeated measures) |

### Multiple-sample tests

| Function | Test |
|---|---|
| `f_oneway(*arrays)` | One-way ANOVA F-test |
| `kruskal(*arrays)` | Kruskal-Wallis |
| `alexandergovern(*arrays)` | Alexander-Govern |
| `bartlett(*arrays)` | Bartlett (equal variances) |
| `levene(*arrays)` | Levene (equal variances, robust) |
| `fligner(*arrays)`, `mood(*arrays)`, `ansari(a, b)` | Variance-homogeneity variants |
| `tukey_hsd(*arrays)` | Tukey's HSD post-hoc |
| `dunnett(*arrays)` | Dunnett's test |
| `anderson_ksamp(*arrays)`, `cramervonmises_2samp`, `epps_singleton_2samp` | Higher-order CDF tests |

## Correlation / Association Tests

| Function | Description |
|---|---|
| `pearsonr(x, y)` | Pearson correlation + p-value |
| `spearmanr(x, y)` | Spearman rank correlation |
| `kendalltau(x, y)` | Kendall's tau |
| `pointbiserialr(x, y)` | Point-biserial correlation |
| `linregress(x, y)` | Simple linear regression (slope, intercept, rvalue, pvalue, stderr) |
| `theilslopes(x, y)` | Theil-Sen robust regression |
| `siegelslopes(x, y)` | Siegel robust regression |
| `chatterjeexi(x, y)` | Chatterjee's xi |
| `weightedtau(x, y)` | Weighted Kendall tau |
| `somersd(x, y)` | Somers' D |
| `page_trend_test`, `multiscale_graphcorr` | Trend / multiscale correlation |

### Contingency tables

`chi2_contingency`, `fisher_exact`, `barnard_exact`, `boschloo_exact` (see also the `scipy.stats.contingency` submodule).

## Resampling and Monte Carlo

```python
from scipy.stats import bootstrap, permutation_test, monte_carlo_test, power
```

| Function | Signature highlights |
|---|---|
| `bootstrap(data, statistic, *, n_resamples=9999, batch=None, vectorized=None, paired=False, axis=0, confidence_level=0.95, alternative='two-sided', method='BCa', bootstrap_result=None)` | Nonparametric bootstrap CI (methods: `BCa`, `B`, `Studentized`) |
| `permutation_test(data_1, data_2, statistic, ...)` | Permutation test for two samples |
| `monte_carlo_test(data_obs, data_1, data_2, statistic, ...)` | Monte Carlo hypothesis test |
| `power(family='F', power=None, nobs1=..., ...)` | Statistical power analysis |

```python
data = (group1, group2)
result = bootstrap(data, lambda x: x[0].mean() - x[1].mean(),
                   confidence_level=0.95)
print(result.confidence_interval)  # (low, high)
```

## Multiple Hypothesis Testing

| Function | Description |
|---|---|
| `false_discovery_control(ps, *, axis=0, method='bh')` | FDR correction (`'bh'` Benjamini-Hochberg, `'by'` Benjamini-Yekutieli, adjusted variants) |
| `combine_pvalues(pvals, method='fisher', ...)` | Combine p-values (Fisher, Stouffer, ...) |

## Kernel Density Estimation

### `gaussian_kde(dataset, bw_method=None)`

Kernel density estimation (1-D and low-dimensional).

```python
from scipy.stats import gaussian_kde
import numpy as np

data = np.random.normal(0, 1, size=1000)
kde = gaussian_kde(data)
x_eval = np.linspace(-3, 3, 200)
pdf_est = kde(x_eval)
```

## Transformations

| Function | Description |
|---|---|
| `boxcox(x, lmbda=None)` | Box-Cox power transformation |
| `boxcox_normmax(x, ...)` | Optimal lambda for Box-Cox |
| `boxcox_llf(x, lmbda)` | Log-likelihood of Box-Cox transform |
| `truncate(dist, a, b)` | Truncated distribution |
| `order_statistic(dist, n)` | Distribution of the n-th order statistic |
| `make_distribution(pdf, ppf)` | Build a distribution from pdf/ppf functions |
| `Mixture` | Mixture distribution |
| `CensoredData` | Censored data support for `fit` |

## Submodules

- **`scipy.stats.contingency`** — contingency-table helpers: `crosstab` (the sparse output became a sparse *array* in 1.18.0), `chi2_contingency`, `margins`, `odd_ratio`, `cramers_v`
- **`scipy.stats.qmc`** — quasi-Monte Carlo: `Halton`, `Sobol`, `LatinHypercube`, `MLPQ`, `scale`, `discrepancy`, `centred_discrepancy`
- **`scipy.stats.sampling`** — discrete samplers (e.g. Poisson, Binomial, Dirichlet samplers)
- **`scipy.stats.mstats`** — masked-array statistics (`describe`, `gmean`, `kurtosis`, `skew`, ...)

**1.18.0 note:** many `scipy.stats` functions gained lazy-array / JAX-JIT support (Array API), and 16 functions gained masked-array (`MArray`) input support.
