# scipy.interpolate Reference (1.18.1)

Interpolation and spline fitting.

## Table of Contents

- [Choosing the Right Interpolator](#choosing-the-right-interpolator)
- [Univariate Interpolation](#univariate-interpolation)
- [Low-Level Spline Classes](#low-level-spline-classes)
- [Multivariate Interpolation (Unstructured)](#multivariate-interpolation-unstructured)
- [Multivariate Interpolation (Grid Data)](#multivariate-interpolation-grid-data)
- [1-D Spline Smoothing and Approximation](#1-d-spline-smoothing-and-approximation)
- [Rational Approximation](#rational-approximation)
- [FITPACK Interfaces (Legacy)](#fitpack-interfaces-legacy)

## Choosing the Right Interpolator

From the user guide:

| Data | Kind | Routine | Continuity | Notes |
|---|---|---|---|---|
| 1D | linear | `numpy.interp` or `make_interp_spline(..., k=1)` | piecewise continuous | |
| 1D | cubic spline | `CubicSpline` | 2nd derivative | |
| 1D | monotone cubic spline | `PchipInterpolator` | 1st derivative | non-overshooting |
| 1D | non-cubic spline | `make_interp_spline` | (k-1)th derivative | `k=3` ≡ `CubicSpline` |
| N-D regular (rectilinear) grid | linear | `RegularGridInterpolator` method='linear' | | |
| N-D regular grid | splines | `RegularGridInterpolator` method='cubic'/'quintic' | 2nd derivatives | |
| N-D regular grid | monotone splines | `RegularGridInterpolator` method='pchip' | 1st derivatives | |
| N-D scattered | nearest | `NearestNDInterpolator` | | |
| N-D scattered | linear | `LinearNDInterpolator` (alias `griddata`) | | |
| N-D scattered | cubic (2D only) | `CloughTocher2DInterpolator` | 1st derivatives | |
| N-D scattered | radial basis function | `RBFInterpolator` | | |

Smoothing/approximation: `make_smoothing_spline` (classic, GCV penalty), `make_splrep` (automated knot selection), `make_lsq_spline` (unconstrained least-squares spline fit), `RectBivariateSpline` (gridded 2-D surfaces), `bisplrep` (scattered 2-D), `RBFInterpolator` (N-D).

## Univariate Interpolation

### `make_interp_spline(x, y, k=3, bc_type=None)`

Construct an interpolating B-spline (returns a `BSpline`). `k=3` is the cubic case.

### `CubicSpline(x, y, bc_type='natural', axis=-1)`

Cubic spline with customizable boundary conditions.

**`bc_type`:** `'natural'` (2nd derivative zero at boundaries, default), `'clamped'` (pass first-derivative values as a tuple), `'not-a-knot'`, `periodic` (or a 2-tuple of conditions).

```python
from scipy.interpolate import CubicSpline

cs = CubicSpline(x, y, bc_type='natural')
y_new = cs(x_new)
dy_new = cs(x_new, 1)   # first derivative
d2y_new = cs(x_new, 2)  # second derivative
```

### `PchipInterpolator(x, y, axis=-1)`

Piecewise cubic Hermite interpolating polynomial — monotonicity-preserving, no overshoot. Good when data has sharp changes or shape preservation matters.

### Other univariate interpolators

| Class | Description |
|---|---|
| `Akima1DInterpolator(x, y)` | Akima interpolation (robust to outliers) |
| `FloaterHormannInterpolator(x, y, d=None)` | Floater-Hormann rational interpolation (stable, oscillation-free) |
| `BarycentricInterpolator(x, y)` | Barycentric rational interpolation |
| `KroghInterpolator(x, y)` | Krogh's algorithm with divided differences |
| `CubicHermiteSpline(x, y, slope=None)` | Cubic Hermite with optional slope specification |
| `interp1d(x, y, kind='linear', ...)` | Legacy convenience wrapper (`kind='linear'/'nearest'/'previous'/'next'/'zero'/'slinear'/'quadratic'/'cubic'/'pchip'/'cubicspline'`); prefer the explicit classes for new code |

## Low-Level Spline Classes

| Class | Description |
|---|---|
| `PPoly(c, x)` | Piecewise polynomial: coefficients `c` (shape `(k+1, M)`), breakpoints `x`; call with derivative order |
| `BPoly(t, c, k, xc, axis=-1)` | B-spline with knots `t`, coefficients `c`, order `k` |
| `BSpline(t, c, k, extrapolate=None)` | Evaluate a B-spline (t: knot vector, c: coefficients, k: degree) |
| `NdPPoly(c, x)` / `NdBSpline(t, c, k)` | Tensor-product polynomial / B-spline (N-D) |

```python
from scipy.interpolate import BSpline
bs = BSpline(t, c, k)
y = bs(x_new)
```

## Multivariate Interpolation (Unstructured)

For scattered data points not on a regular grid.

| Class | Description |
|---|---|
| `LinearNDInterpolator(points, values)` | Linear interpolation on the Delaunay triangulation (the routine behind `griddata(method='linear')`) |
| `NearestNDInterpolator(points, values)` | Nearest-neighbor interpolation |
| `CloughTocher2DInterpolator(points, values)` | C¹ smooth interpolation in 2-D (Clough-Tocher scheme) |
| `RBFInterpolator(points, values, smoothing=0.0, kernel='cubic', ...)` | Radial basis function interpolation, any dimension |

**`RBFInterpolator` kernels:** `'multiquadric'`, `'inverse_multiquadric'`, `'gaussian'`, `'linear'`, `'quadratic'`, `'cubic'`, `'quintic'`, `'thin_plate_spline'`.

```python
from scipy.interpolate import RBFInterpolator
interp = RBFInterpolator(points, values, kernel='cubic')  # points: (N, d), values: (N,)
values_new = interp(points_new)
```

**1.18.0:** `LinearNDInterpolator.__call__` and `CloughTocher2DInterpolator.__call__` gained a `simplex_tolerance` argument — increasing it can avoid holes in certain interpolation problems.

## Multivariate Interpolation (Grid Data)

### `RegularGridInterpolator(points, values, method='linear', bounds_error=True, fill_value=np.nan)`

Interpolate on a regular grid; `points` is a tuple of 1-D arrays defining the grid axes.

**Methods:** `'linear'`, `'nearest'`, `'slinear'` (cubic in 1-D), `'cubic'`, `'quintic'`, `'pchip'` (1-D only).

```python
from scipy.interpolate import RegularGridInterpolator
import numpy as np

x = np.linspace(0, 1, 10)
y = np.linspace(0, 1, 10)
z = np.sin(x[:, None]) * np.cos(y[None, :])

interp = RegularGridInterpolator((x, y), z, method='linear')
values_query = interp(np.random.uniform(0, 1, size=(100, 2)))
```

### `interpn(points, xi, values, method='linear', ...)` / `griddata(points, values, xi, method='linear', ...)`

Function-style interfaces for N-D gridded (`interpn`) and scattered (`griddata`) interpolation.

## 1-D Spline Smoothing and Approximation

| Function | Description |
|---|---|
| `make_smoothing_spline(x, y, lam=None)` | Smoothing spline (roughness penalty, GCV) |
| `make_lsq_spline(x, y, t=None, weights=None, ...)` | Least-squares spline approximation given data and interior knots |
| `make_splrep(x, y, w=None, s=None, k=3)` | Wrapper for FITPACK `splrep`; returns `(t, c, k)` |
| `make_splprep(u, x, ...)` | Wrapper for parametric `splprep` |
| `generate_knots(x, k, ...)` | Generate knot sequences from data points |

## Rational Approximation

### `AAA(f, domain=(-1, 1), n=20, ...)`

AAA algorithm for rational approximation of a function — a **class** (subclass of the barycentric-rational interpolator). Instantiate with a function `f`, the approximation domain, and a budget `n`; the instance is callable to evaluate the rational approximation.

```python
from scipy.interpolate import AAA
import numpy as np

f = lambda z: np.exp(z)
r = AAA(f, domain=(-1, 1), n=20)
vals = r(np.array([0.0, 0.5]))  # evaluate the approximation
```

## FITPACK Interfaces (Legacy)

Lower-level wrappers around FITPACK (ported from Fortran to C in 1.18.0). Prefer the higher-level classes above.

### 1-D

| Function | Description |
|---|---|
| `splrep(x, y, w=None, s=None, k=3)` | B-spline representation of data |
| `splprep(u, x, ...)` | Parametric spline representation |
| `splev(x, tck, der=0)` | Evaluate spline and derivatives |
| `splint(a, b, tck)` | Integrate a spline |
| `sproot(tck)` | Find roots of a spline |
| `splder(tck, n=1)` | Derivative of a spline |

### 2-D

| Function | Description |
|---|---|
| `bisplrep(x, y, z, ...)` | Bivariate spline representation (scattered data) |
| `bisplev(x, y, tck, ...)` | Evaluate bivariate spline |
| `RectBivariateSpline(x, y, z, ...)` | Rectangular bivariate spline (gridded data) |
| `SmoothBivariateSpline(x, y, z, w=None, ...)` | Smooth rectangular bivariate spline |

**Deprecated in 1.18.0:** `pade`, `lagrange`, `approximate_taylor_polynomial` (deemed not practically useful).
