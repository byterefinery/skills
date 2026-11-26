---
name: scipy-1-17-1
description: SciPy (scientific Python) library reference for mathematics, science, and engineering. Covers optimization, integration, linear algebra, statistics, signal processing, FFT, interpolation, sparse matrices, spatial algorithms, special functions, image processing, clustering, I/O, and physical constants. Use when the user needs scientific computing in Python, numerical methods, data analysis with scipy, solving equations, statistical tests, Fourier transforms, ODE systems, matrix operations, or any math-heavy computation. Also triggers on mentions of scipy, SciPy, scientific Python, numerical Python, or packages like numpy/scipy together.
---

# scipy 1.17.1

SciPy is the core scientific computing library for Python, built on NumPy arrays. It provides efficient numerical routines across mathematics, science, and engineering domains.

## Overview

SciPy organizes its functionality into submodules, each accessible as `scipy.<module>`. The main namespace exports submodule names (lazy-loaded), plus `__version__`, `LowLevelCallable`, `show_config`, and `test`.

### Submodule Map

| Submodule | Domain | Key Functions |
|---|---|---|
| `scipy.optimize` | Optimization, root-finding, curve fitting, LP/MILP | `minimize`, `root`, `curve_fit`, `linprog`, `differential_evolution` |
| `scipy.integrate` | Numerical integration, ODE/BVP solvers | `quad`, `solve_ivp`, `solve_bvp`, `trapezoid`, `simpson` |
| `scipy.linalg` | Dense linear algebra (extends `numpy.linalg`) | `solve`, `eig`, `svd`, `cholesky`, `expm`, `null_space` |
| `scipy.stats` | Probability distributions, hypothesis tests, summary stats | `norm`, `ttest_ind`, `pearsonr`, `gaussian_kde`, `bootstrap` |
| `scipy.signal` | Signal processing, filter design, spectral analysis, LTI systems | `find_peaks`, `welch`, `firwin`, `lfilter`, `StateSpace` |
| `scipy.fft` | Discrete Fourier transforms (modern, replaces `scipy.fftpack`) | `fft`, `ifft`, `rfft`, `dct`, `next_fast_len` |
| `scipy.interpolate` | Interpolation and spline fitting | `interp1d`, `CubicSpline`, `RegularGridInterpolator`, `RBFInterpolator` |
| `scipy.sparse` | Sparse matrix/array storage and operations | `csr_array`, `coo_array`, `diags_array`, `eye_array` |
| `scipy.sparse.linalg` | Sparse linear algebra (iterative solvers, partial eig) | `spsolve`, `gmres`, `eigs`, `svds`, `LinearOperator` |
| `scipy.spatial` | Spatial data structures, distance metrics, geometry | `KDTree`, `ConvexHull`, `Delaunay`, `distance.pdist` |
| `scipy.special` | Special mathematical functions (Bessel, gamma, erf, etc.) | `gamma`, `erf`, `jv`, `eval_legendre`, `lambertw` |
| `scipy.ndimage` | N-dimensional image processing (filters, morphology, measurements) | `gaussian_filter`, `label`, `binary_erosion`, `center_of_mass` |
| `scipy.io` | File I/O (MATLAB, Matrix Market, NetCDF, Fortran, WAV) | `loadmat`, `savemat`, `mmread`, `FortranFile` |
| `scipy.cluster` | Clustering algorithms (k-means, hierarchical) | `vq.kmeans`, `hierarchy.linkage`, `hierarchy.dendrogram` |
| `scipy.constants` | Physical and mathematical constants, units, SI prefixes | `pi`, `c`, `h`, `physical_constants`, `value()` |
| `scipy.differentiate` | Finite-difference numerical differentiation | `derivative`, `jacobian`, `hessian` |
| `scipy.datasets` | Sample datasets for testing and examples | `fetch()` functions |

### Deprecated / Legacy Modules

- **`scipy.fftpack`** — legacy FFT; use `scipy.fft` instead
- **`scipy.misc`** — deprecated, removed in 2.0.0
- **`scipy.odr`** — deprecated since 1.17.0, removed in 1.19.0; migrate to `odrpack` on PyPI
- **`odeint`** — old ODE API; prefer `solve_ivp` for new code

## Usage

### Import Patterns

```python
# Submodule-level import (recommended)
from scipy import optimize, integrate, stats, linalg, signal, fft, sparse, spatial, special, ndimage, io, cluster, constants, differentiate, interpolate

# Function-level import for frequently used functions
from scipy.optimize import minimize, curve_fit, differential_evolution
from scipy.integrate import quad, solve_ivp
from scipy.stats import norm, ttest_ind, pearsonr
from scipy.linalg import eig, svd, cholesky, expm
from scipy.signal import find_peaks, welch, firwin, lfilter
from scipy.fft import fft, ifft, rfft, next_fast_len
from scipy.interpolate import interp1d, CubicSpline, RegularGridInterpolator
from scipy.sparse import csr_array, diags_array, eye_array
from scipy.sparse.linalg import spsolve, gmres, eigs
from scipy.spatial import KDTree, ConvexHull, distance
from scipy.special import gamma, erf, jv, lambertw
from scipy.ndimage import gaussian_filter, label, binary_erosion
from scipy.io import loadmat, savemat
from scipy.cluster.vq import kmeans
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.constants import pi, c, h, value
```

### Quick Reference by Task

**Optimization**: `minimize(func, x0, method='LBFGS')` for unconstrained; add `bounds` or `constraints` for constrained. Use `differential_evolution()` for global optimization. Use `curve_fit(model, xdata, ydata)` for fitting data to a model.

**Root-finding**: `root_scalar(func, bracket=[a, b], method='brentq')` for scalar; `root(func, x0)` for multivariate. Bracketing methods (`brentq`, `bisect`) are guaranteed to converge.

**Integration**: `quad(func, a, b)` for definite integrals. `solve_ivp(fun, t_span, y0, method='RK45')` for ODEs. `trapezoid(y, x)` or `simpson(y, x)` for numerical integration from samples.

**Linear Algebra**: Prefer `scipy.linalg` over `numpy.linalg` — it offers more methods and consistent behavior. Use `solve(A, b)` instead of `inv(A) @ b`. Use `eig()`, `eigh()` (Hermitian), `svd()`, `cholesky()`.

**Statistics**: Distributions are objects: `norm.pdf(x, loc=0, scale=1)`, `norm.cdf(x)`, `norm.rvs(size=1000)`. Hypothesis tests return `(statistic, pvalue)`: `ttest_ind(a, b)`, `pearsonr(x, y)`.

**Signal Processing**: `find_peaks(signal, height=threshold, distance=min_distance)`. `welch(x, fs=sampling_rate)` for power spectral density. `firwin(numtaps, cutoff, fs=fs)` for FIR filter design. `lfilter(b, a, x)` to apply a filter.

**FFT**: `fft(x)` and `ifft(X)`. Use `rfft(x)` for real-valued input (faster, half-size output). `next_fast_len(n)` finds optimal zero-pad length. Prefer `scipy.fft` over `numpy.fft` for multi-threading and backend control.

**Sparse Matrices**: Use `_array` classes (`csr_array`, not `csr_matrix`) for new code. Matrix multiplication uses `@` operator, not `*`. Use `spsolve(A, b)` for direct solve, `gmres(A, b)` for iterative.

**Spatial**: `KDTree(points).query(query_points, k=5)` for nearest neighbors. `distance.pdist(X, metric='euclidean')` for pairwise distances. `ConvexHull(points)` and `Delaunay(points)` for geometry.

**Special Functions**: Vectorized over NumPy arrays. `gamma(x)`, `erf(x)`, `jv(n, x)` (Bessel J), `lambertw(x)`. Error handling via `seterr()`, `errstate()`.

### Version Compatibility

SciPy 1.17.1 requires NumPy ≥ 1.26.4 and < 2.7.0. A warning is emitted if the installed NumPy version is outside this range.

## Gotchas

- **`scipy.sparse` arrays use `@` for matrix multiplication** — the `*` operator does element-wise multiplication (like NumPy). This differs from the old `_matrix` classes where `*` was matrix multiply. Always use `_array` classes, not `_matrix`.
- **`scipy.odr` is deprecated** since 1.17.0 and will be removed in 1.19.0. Migrate to the standalone `odrpack` package on PyPI.
- **`scipy.fftpack` is legacy** — use `scipy.fft` which supports multi-threading, backends, and real-valued optimizations (`rfft`).
- **`odeint` vs `solve_ivp`** — `odeint` is the old Fortran-based API. `solve_ivp` is the modern Python API with event detection, dense output, and multiple solver methods. Prefer `solve_ivp`.
- **Distribution parameters use `loc` and `scale`** — not `mu`/`sigma`. E.g., `norm.pdf(x, loc=5, scale=2)` for N(5, 4). The `*args` positional form still works but keyword form is clearer.
- **Hypothesis tests return `(statistic, pvalue)` tuples** — not just p-values. Unpack both: `stat, p = ttest_ind(a, b)`.
- **`scipy.linalg` extends `numpy.linalg`** — same function names but with more methods and consistent behavior across dtypes. Prefer `scipy.linalg` when you need features beyond what NumPy provides.
- **`find_peaks` returns indices, not values** — use `signal[peaks]` to get peak values. Parameters like `height`, `distance`, `prominence`, and `width` control filtering.
- **Sparse solver choice matters** — `spsolve` uses SuperLU (direct, good for small/medium). Iterative solvers (`gmres`, `cg`) scale better for large systems but need preconditioners. Use `LinearOperator` when A is implicit (e.g., defined by a function).
- **`quad` expects a callable** — for data-driven integration, use `trapezoid()` or `simpson()` instead. `quad` adapts its sampling internally.
- **`minimize` methods have different capabilities** — `Nelder-Mead` needs no gradient but is slow. `L-BFGS-B` supports bounds. `trust-constr` supports general constraints. Choose method based on problem structure.

## References

Detailed function listings and usage patterns for each submodule:

- [01-optimize.md](references/01-optimize.md) — Optimization, root-finding, curve fitting, LP/MILP
- [02-integrate.md](references/02-integrate.md) — Numerical integration, ODE/BVP solvers
- [03-stats.md](references/03-stats.md) — Probability distributions, hypothesis tests, summary statistics
- [04-linalg.md](references/04-linalg.md) — Dense linear algebra (decompositions, eigenvalues, matrix functions)
- [05-signal.md](references/05-signal.md) — Signal processing, filter design, spectral analysis, LTI systems
- [06-fft.md](references/06-fft.md) — Discrete Fourier transforms, DCT/DST, Hankel transforms
- [07-interpolate.md](references/07-interpolate.md) — Interpolation and spline fitting
- [08-sparse.md](references/08-sparse.md) — Sparse matrices and sparse linear algebra
- [09-spatial.md](references/09-spatial.md) — Spatial algorithms, distance metrics, geometry, transforms
- [10-special.md](references/10-special.md) — Special mathematical functions (Bessel, gamma, erf, orthogonal polynomials)
- [11-ndimage.md](references/11-ndimage.md) — N-dimensional image processing (filters, morphology, measurements)
- [12-io.md](references/12-io.md) — File I/O (MATLAB, Matrix Market, NetCDF, Fortran, WAV)
- [13-cluster.md](references/13-cluster.md) — Clustering algorithms (k-means, hierarchical)
- [14-constants.md](references/14-constants.md) — Physical/mathematical constants, units, SI prefixes
