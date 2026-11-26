---
name: scipy-1-18-1
description: SciPy (scientific Python) library reference for mathematics, science, and engineering. Covers optimization, integration, linear algebra, statistics, signal processing, FFT, interpolation, sparse arrays, spatial algorithms, special functions, image processing, clustering, I/O, and physical constants. Use when the user needs scientific computing in Python, numerical methods, data analysis with scipy, solving equations, statistical tests, Fourier transforms, ODE systems, matrix operations, or any math-heavy computation. Also triggers on mentions of scipy, SciPy, scientific Python, numerical Python, or packages like numpy/scipy together.
license: BSD-3-Clause
compatibility: Python 3.12+, NumPy >= 2.0 (tested < 2.8). Install via pip.
metadata:
  tags:
    - python
    - scientific-computing
    - numerics
    - statistics
    - signal-processing
---

# scipy 1.18.1

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
| `scipy.interpolate` | Interpolation and spline fitting | `CubicSpline`, `PchipInterpolator`, `RegularGridInterpolator`, `RBFInterpolator`, `griddata` |
| `scipy.sparse` | Sparse array storage and operations | `csr_array`, `coo_array`, `diags_array`, `eye_array` |
| `scipy.sparse.linalg` | Sparse linear algebra (iterative solvers, partial eig) | `spsolve`, `gmres`, `eigs`, `svds`, `LinearOperator` |
| `scipy.spatial` | Spatial data structures, distance metrics, geometry | `KDTree`, `ConvexHull`, `Delaunay`, `distance.pdist` |
| `scipy.special` | Special mathematical functions (Bessel, gamma, erf, etc.) | `gamma`, `erf`, `jv`, `eval_legendre`, `lambertw` |
| `scipy.ndimage` | N-dimensional image processing (filters, morphology, measurements) | `gaussian_filter`, `label`, `binary_erosion`, `center_of_mass` |
| `scipy.io` | File I/O (MATLAB, Matrix Market, NetCDF, Fortran, WAV) | `loadmat`, `savemat`, `mmread`, `FortranFile` |
| `scipy.cluster` | Clustering algorithms (k-means, hierarchical) | `vq.kmeans`, `hierarchy.linkage`, `hierarchy.dendrogram` |
| `scipy.constants` | Physical and mathematical constants, units, CODATA database | `pi`, `c`, `h`, `physical_constants`, `value()` |
| `scipy.differentiate` | Finite-difference numerical differentiation | `derivative`, `jacobian`, `hessian` |
| `scipy.datasets` | Sample datasets for examples | `ascent()`, `face()`, `electrocardiogram()` |

### Deprecated / Legacy Modules

- **`scipy.fftpack`** — legacy FFT; use `scipy.fft` instead
- **`scipy.misc`** — deprecated utility namespace, removed in 2.0.0
- **`scipy.odr`** — deprecated as of 1.17.0, removed in SciPy 1.19.0; use the `odrpack` package on PyPI instead
- **`odeint`** — old ODE API; prefer `solve_ivp` for new code
- **`scipy.sparse` spmatrix interface** — deprecated; the sparse *array* (`sparray`) interface is the future

## Usage

### Import Patterns

```python
# Submodule-level import (recommended)
from scipy import optimize, integrate, stats, linalg, signal, fft, sparse, spatial, special, ndimage, cluster, constants, differentiate, interpolate

# Function-level import for frequently used functions
from scipy.optimize import minimize, curve_fit, differential_evolution
from scipy.integrate import quad, solve_ivp
from scipy.stats import norm, ttest_ind, pearsonr
from scipy.linalg import eig, svd, cholesky, expm
from scipy.signal import find_peaks, welch, firwin, lfilter
from scipy.fft import fft, ifft, rfft, next_fast_len
from scipy.interpolate import CubicSpline, RegularGridInterpolator
from scipy.sparse import csr_array, diags_array, eye_array
from scipy.sparse.linalg import spsolve, gmres, eigs
from scipy.spatial import KDTree, ConvexHull, distance
from scipy.special import gamma, erf, jv, lambertw
from scipy.ndimage import gaussian_filter, label, binary_erosion
from scipy.cluster.vq import kmeans
from scipy.cluster.hierarchy import linkage, dendrogram

# For scipy.io prefer "import scipy" (io collides with the stdlib module)
import scipy
scipy.io.loadmat(...)
```

### Quick Reference by Task

**Optimization**: `minimize(func, x0, method='L-BFGS-B', bounds=...)` for bounded; `method='Nelder-Mead'` derivative-free; `method='trust-constr'` for general nonlinear constraints (with `LinearConstraint`/`NonlinearConstraint` objects). `differential_evolution(func, bounds)` for global. `curve_fit(model, xdata, ydata)` for fitting data to a model.

**Root-finding**: `root_scalar(func, bracket=[a, b], method='brentq')` for scalar; `root(func, x0)` for multivariate. Bracketing methods (`brentq`, `bisect`) are guaranteed to converge.

**Integration**: `quad(func, a, b)` for definite integrals — returns `(value, abs_error)`, not a scalar. `solve_ivp(fun, t_span, y0, method='RK45')` for ODEs. `trapezoid(y, x)` or `simpson(y, x)` for integration from samples.

**Linear Algebra**: Prefer `scipy.linalg` over `numpy.linalg` — it is always compiled with BLAS/LAPACK and offers more methods. Use `solve(A, b)` instead of `inv(A) @ b`. Use `eig()`, `eigh()` (Hermitian), `svd()`, `cholesky()`.

**Statistics**: Distributions are objects: `norm.pdf(x, loc=0, scale=1)`, `norm.cdf(x)`, `norm.rvs(size=1000)`. Hypothesis tests return a result with `statistic` and `pvalue`: `stat, p = ttest_ind(a, b)`.

**Signal Processing**: `find_peaks(signal, height=threshold, distance=min_distance)` (returns indices). `welch(x, fs=sampling_rate)` for power spectral density. `firwin(numtaps, cutoff, fs=fs)` for FIR design. `lfilter(b, a, x)` to apply a filter.

**FFT**: `fft(x)` and `ifft(X)`. Use `rfft(x)` for real-valued input (faster, half-size output). `next_fast_len(n)` finds optimal zero-pad length. Prefer `scipy.fft` over `numpy.fft` for multi-threading and backend control.

**Sparse Arrays**: Use `_array` classes (`csr_array`, not `csr_matrix`) for new code — the `spmatrix` interface is deprecated. Multiplication uses `@`; `*` is element-wise. Use `spsolve(A, b)` for direct solve, `gmres(A, b)` for iterative.

**Spatial**: `KDTree(points).query(query_points, k=5)` for nearest neighbors. `distance.pdist(X, metric='euclidean')` for pairwise distances. `ConvexHull(points)` and `Delaunay(points)` for geometry.

**Special Functions**: Vectorized over NumPy arrays. `gamma(x)`, `erf(x)`, `jv(n, x)` (Bessel J), `lambertw(x)`. Error handling via `seterr()` / `errstate()`.

### Version Compatibility

SciPy 1.18.1 requires Python 3.12+ (1.18.0 targets 3.12–3.14; 1.18.1 adds Python 3.15 binaries) and NumPy >= 2.0.0. A `UserWarning` is emitted if the installed NumPy version is outside `[2.0.0, 2.8.0)`. 1.18.1 is a bug-fix release with no new features compared to 1.18.0.

## Gotchas

- **`quad` returns `(value, abs_error)`** — not a scalar. Unpack both or index `[0]`. Extra integrand parameters go through `args=(...)`, not direct callables.
- **`solve_ivp` tolerances** — `rtol`/`atol` default to `1e-3`/`1e-6`; the user guide shows visible deviation from analytic solutions at defaults. Pass tighter `rtol`/`atol` (e.g. `1e-8`) when accuracy matters. `sol.y` columns are solution states at each time point (initial condition is the first column).
- **`func` argument order differs** — `solve_ivp` takes `fun(t, y)`, legacy `odeint` takes `func(y, t)`. Mixing them up gives wrong results or shape errors.
- **`scipy.sparse` arrays use `@` for matrix multiplication** — the `*` operator is element-wise. Always use `_array` classes, not the deprecated `_matrix` classes. Operations may silently return a different format (e.g. COO `@` COO → CSR).
- **`scipy.odr` is deprecated** (since 1.17.0, removed in 1.19.0) — use the `odrpack` package on PyPI for orthogonal distance regression.
- **`scipy.fftpack` is legacy** — use `scipy.fft` (multi-threading, backends, `rfft`, DCT/DST).
- **Distribution parameters use `loc` and `scale`** — not `mu`/`sigma`. E.g. `norm.pdf(x, loc=5, scale=2)` for N(5, 4).
- **Hypothesis tests return `(statistic, pvalue)`** — not just p-values. Unpack both: `stat, p = ttest_ind(a, b)`.
- **`find_peaks` returns indices, not values** — use `signal[peaks]` for peak values.
- **`minimize` methods have different capabilities** — Nelder-Mead/Powell are derivative-free (bounds OK); L-BFGS-B supports bounds; trust-constr/COBYLA/COBYQA/SLSQP handle nonlinear constraints — and **the constraint format differs**: trust-constr/COBYLA/COBYQA take `LinearConstraint`/`NonlinearConstraint` objects while SLSQP takes dictionaries.
- **1.18.0 dtype strictness in `scipy.linalg`** — non-LAPACK dtypes are deprecated: integers upcast to float; single/double precision float/complex are the supported families.
- **1.18.0 sparse migration** — `spmatrix` interface deprecated; `kron`/`kronsum`/`block_diag` returning `spmatrix` for all-dense inputs is deprecated (will become `sparray`); `scipy.io` readers' `spmatrix=True` is deprecated.
- **1.18.0 stats behavior changes** — `multinomial` returns NaNs (and `multinomial.rvs` raises) when `p` rows do not sum to unity; `rankdata` always returns float dtype; `contingency.crosstab(sparse=True)` returns a sparse *array*.
- **1.18.0 linalg.lstsq residual semantics** — with `lapack_driver='gesld'/'gelss'` on an overdetermined system a non-empty residual is always returned; rank-deficient slices get `NaN` residuals.
- **Thread safety is per-object** — SciPy functions generally release the GIL and are safe on shared immutable arrays, but sparse arrays are mutable and **not** thread-safe under concurrent mutation; `scipy.integrate.ode` may raise `IntegratorConcurrencyError` for non-parallel-safe methods.

## References

Detailed function listings and usage patterns for each submodule:

- [01-optimize.md](references/01-optimize.md) — Optimization, root-finding, curve fitting, LP/MILP
- [02-integrate.md](references/02-integrate.md) — Numerical integration, ODE/BVP solvers
- [03-stats.md](references/03-stats.md) — Probability distributions, hypothesis tests, summary statistics
- [04-linalg.md](references/04-linalg.md) — Dense linear algebra (decompositions, eigenvalues, matrix functions)
- [05-signal.md](references/05-signal.md) — Signal processing, filter design, spectral analysis, LTI systems
- [06-fft.md](references/06-fft.md) — Discrete Fourier transforms, DCT/DST, Hankel transforms
- [07-interpolate.md](references/07-interpolate.md) — Interpolation and spline fitting
- [08-sparse.md](references/08-sparse.md) — Sparse arrays, sparse linear algebra, csgraph
- [09-spatial.md](references/09-spatial.md) — Spatial algorithms, distance metrics, geometry, transforms
- [10-special.md](references/10-special.md) — Special mathematical functions (Bessel, gamma, erf, orthogonal polynomials)
- [11-ndimage.md](references/11-ndimage.md) — N-dimensional image processing (filters, morphology, measurements)
- [12-io.md](references/12-io.md) — File I/O (MATLAB, Matrix Market, NetCDF, Fortran, WAV)
- [13-cluster.md](references/13-cluster.md) — Clustering algorithms (k-means, hierarchical)
- [14-constants.md](references/14-constants.md) — Physical/mathematical constants, units, CODATA database
