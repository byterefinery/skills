# 05 — Statistics and Random Sampling

## Descriptive Statistics

### Averages and variances

```python
np.mean(a)                   # arithmetic mean
np.average(a, weights=w)     # weighted average
np.median(a)                 # median
np.sum(a)                    # sum of elements
np.prod(a)                   # product of elements
np.std(a)                    # standard deviation (ddof=0, population)
np.var(a)                    # variance (ddof=0)
np.std(a, ddof=1)            # sample std (Bessel correction)
np.var(a, ddof=1)            # sample variance
```

NaN-safe variants: `np.nanmean()`, `np.nanstd()`, `np.nanvar()`, `np.nanmedian()`, `np.nansum()`, `np.nanprod()`.

### Cumulative operations

```python
np.cumsum(a)                 # cumulative sum
np.cumprod(a)                # cumulative product
np.nancumsum(a)              # NaN-aware cumulative sum
np.diff(a)                   # discrete differences
np.gradient(a)               # numerical gradient
```

### Order statistics

```python
np.percentile(a, 50)         # 50th percentile (median)
np.percentile(a, [25, 50, 75])  # multiple percentiles
np.quantile(a, 0.5)          # quantile (same as percentile but 0–1 scale)
np.ptp(a)                    # peak-to-peak (max - min)
```

The `method=` parameter controls interpolation: `'inverted_cdf'`, `'nearest'`, `'lower'`, `'higher'`, `'midpoint'`, `'linear'` (default). The old `interpolation=` parameter was removed in 2.4.

### Correlation and covariance

```python
np.corrcoef(a, b)            # correlation matrix
np.cov(a, b)                 # covariance matrix
np.correlate(a, v)           # cross-correlation of two signals
```

## Histograms

```python
counts, edges = np.histogram(a, bins=10)
counts, edges = np.histogram(a, bins='auto')   # automatic bin selection
counts, edges = np.histogram(a, bins=20, range=(0, 100))
```

Automatic bin methods: `'auto'` (max of Sturges/Freedman-Diaconis), `'sturges'`, `'fd'` (Freedman-Diaconis), `'doane'`, `'sqrt'`.

### Multi-dimensional histograms

```python
H, xedges, yedges = np.histogram2d(x, y, bins=20)
H, edges = np.histogramdd(points, bins=10)     # N-dimensional
```

### Binning utilities

```python
np.bincount(a)               # count occurrences (non-negative integers only)
np.digitize(x, bins)         # find which bin each element belongs to
```

## Sorting and Searching

### Sorting

```python
np.sort(a)                   # sorted copy
a.sort()                     # in-place sort
np.sort(a, axis=0)           # sort along specific axis
np.argsort(a)                # indices that would sort
np.lexsort((key2, key1))     # stable sort by multiple keys (last key primary)
```

Sort algorithms: `'quicksort'` (default), `'mergesort'` (stable), `'heapsort'`.

### Partial sorting

```python
np.partition(a, k)           # partition so a[k] is in sorted position
np.argpartition(a, k)        # indices of partition
np.partition(a, (3, 7))      # multiple partition points
```

`partition` is O(n) vs O(n log n) for full sort. Use when you only need the top-k elements.

### Searching

```python
np.searchsorted(a, v)        # indices to insert v into sorted a
np.searchsorted(a, v, side='right')  # right-side insertion
np.argmax(a)                 # index of maximum
np.argmin(a)                 # index of minimum
np.nonzero(a)                # indices where a != 0
np.where(condition)          # indices where condition is True
np.extract(condition, a)     # elements where condition is True (alias of a[condition])
```

## Set Operations

```python
np.unique(a)                 # sorted unique values
np.unique(a, return_counts=True)       # with counts
np.unique(a, return_inverse=True)      # with reconstruction indices
np.unique_values(a)          # unique values only (faster, no sorting guarantee in future)
np.isin(a, test_elements)    # boolean array: is each element of a in test_elements?
np.intersect1d(a, b)         # sorted intersection
np.union1d(a, b)             # sorted union
np.setdiff1d(a, b)           # set difference
np.setxor1d(a, b)            # symmetric difference
```

Note: `np.in1d` was removed in 2.4 — use `np.isin()` instead.

## Random Number Generation

### The modern API (recommended)

```python
rng = np.random.default_rng()           # seeded from OS entropy
rng = np.random.default_rng(42)         # reproducible seed
rng = np.random.default_rng(np.random.SeedSequence(42))  # spawnable
```

### Basic distributions

```python
rng.random()                    # uniform [0, 1)
rng.random((3, 4))              # array of uniform randoms
rng.integers(low, high, size)   # uniform integers in [low, high)
rng.standard_normal(size)       # standard normal (mean=0, std=1)
```

### Common distributions

```python
# Continuous
rng.normal(loc=0, scale=1, size=100)      # normal/Gaussian
rng.uniform(low, high, size)              # uniform
rng.exponential(scale, size)              # exponential
rng.pareto(a, size)                       # Pareto
rng.lognormal(mean, sigma, size)          # log-normal
rng.beta(a, b, size)                      # beta
rng.gamma(shape, scale, size)             # gamma
rng.chisquare(df, size)                   # chi-squared

# Discrete
rng.binomial(n, p, size)                  # binomial
rng.poisson(lam, size)                    # Poisson
rng.geometric(p, size)                    # geometric
rng.negative_binomial(n, p, size)         # negative binomial

# Special
rng.standard_cauchy(size)                 # standard Cauchy
rng.standard_t(df, size)                  # Student's t
rng.weibull(a, size)                      # Weibull
```

### Sampling and shuffling

```python
rng.choice(a, size=5, replace=False)      # sample without replacement
rng.choice(10, size=3, p=weights)         # weighted sampling
rng.permutation(a)                         # shuffled copy
rng.shuffle(a)                             # in-place shuffle
```

### Reproducibility and seeding

```python
# Use large seeds for statistical independence
import secrets
seed = secrets.randbits(128)
rng = np.random.default_rng(seed)

# Spawn child generators from a parent
parent = np.random.default_rng(42)
child1, child2 = parent.spawn(2)
```

### Legacy API (avoid in new code)

```python
np.random.seed(42)            # global seed (affects all processes)
np.random.rand(3, 4)          # uniform [0, 1)
np.random.randn(3, 4)         # standard normal
np.random.randint(0, 10, 5)   # integers in [0, 10)
np.random.RandomState(42)     # isolated legacy generator
```

The legacy `RandomState` and module-level functions use the MT19937 algorithm. The modern `Generator` uses PCG64 which is faster and has better statistical properties.
