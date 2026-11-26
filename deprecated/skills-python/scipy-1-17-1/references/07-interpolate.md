# scipy.interpolate Reference

Interpolation and spline fitting.

## Table of Contents

- [Univariate Interpolation](#univariate-interpolation)
- [Low-Level Spline Classes](#low-level-spline-classes)
- [Multivariate Interpolation (Unstructured)](#multivariate-interpolation-unstructured)
- [Multivariate Interpolation (Grid Data)](#multivariate-interpolation-grid-data)
- [1-D Spline Smoothing and Approximation](#1-d-spline-smoothing-and-approximation)
- [Rational Approximation](#rational-approximation)
- [FITPACK Interfaces (Legacy)](#fitpack-interfaces-legacy)
- [Choosing the Right Interpolator](#choosing-the-right-interpolator)

## Univariate Interpolation

### `make_interp_spline(x, y, k=3, bc_type=None)`

Construct an interpolating B-spline. Returns `BSpline` object.

```python
from scipy.interpolate import make_interp_spline

spl = make_interp_spline(x, y, k=3)  # cubic spline
y_new = spl(x_new)
```

### `CubicSpline(x, y, bc_type='natural', axis=-1)`

Cubic spline interpolation with customizable boundary conditions.

**Boundary conditions (`bc_type`):**
- `'natural'` — second derivative zero at boundaries
- `'clamped'` — first derivative specified (pass as tuple)
- `'not-a-knot'` — not-a-knot condition
- `periodic` — periodic boundary

```python
from scipy.interpolate import CubicSpline

cs = CubicSpline(x, y, bc_type='natural')
y_new = cs(x_new)
dy_new = cs(x_new, 1)  # first derivative
d2y_new = cs(x_new, 2)  # second derivative
```

### `PchipInterpolator(x, y, axis=-1)`

Piecewise cubic Hermite interpolating polynomial. Monotonicity-preserving. Good when data has sharp changes or you need shape preservation.

```python
from scipy.interpolate import PchipInterpolator

pchip = PchipInterpolator(x, y)
y_new = pchip(x_new)
```

### Other univariate interpolators

| Class | Description |
|---|---|
| `Akima1DInterpolator(x, y)` | Akima interpolation (robust to outliers) |
| `FloaterHormannInterpolator(x, y, d=None)` | Floater-Hormann rational interpolation (stable, oscillation-free) |
| `BarycentricInterpolator(x, y)` | Barycentric rational interpolation |
| `KroghInterpolator(x, y)` | Krogh's algorithm with divided differences |
| `CubicHermiteSpline(x, y, slope=None)` | Cubic Hermite with optional slope specification |

### `interp1d(x, y, kind='linear', ...)` — legacy

Convenience function wrapping various interpolators. Prefer the explicit classes above for new code.

**Kind options:** `'linear'`, `'nearest'`, `'zero'`, `'slinear'`, `'quadratic'`, `'cubic'`, `'pchip'`, `'cubicspline'`.

## Low-Level Spline Classes

### `PPoly(c, x)` — Piecewise Polynomial

General piecewise polynomial representation.

```python
from scipy.interpolate import PPoly

# c: coefficients array of shape (k+1, M) where k is order, M is number of intervals
# x: breakpoints
pp = PPoly(c, x)
y = pp(x_new)
dy = pp(x_new, 1)  # derivative
```

### `BPoline(t, c, k, xc, axis=-1)` — B-Spline

B-spline representation with knots `t`, coefficients `c`, and order `k`.

### `BSpline(t, c, k, extrapolate=None)`

Evaluate B-spline at given points.

```python
from scipy.interpolate import BSpline

# t: knot vector, c: coefficients, k: degree
bs = BSpline(t, c, k)
y = bs(x_new)
```

## Multivariate Interpolation (Unstructured)

For scattered data points not on a regular grid.

### `LinearNDInterpolator(points, values)`

Linear interpolation on the Delaunay triangulation of the points.

### `NearestNDInterpolator(points, values)`

Nearest-neighbor interpolation.

### `CloughTocher2DInterpolator(points, values)`

C¹ smooth interpolation in 2-D using Clough-Tocher scheme. Only for 2-D data.

### `RBFInterpolator(points, values, smoothing=0.0, kernel='cubic')`

Radial basis function interpolation. Works in any dimension.

**Kernel options:** `'multiquadric'`, `'inverse_multiquadric'`, `'gaussian'`, `'linear'`, `'quadratic'`, `'cubic'`, ` 'quintic'`, `'thin_plate_spline'`.

```python
from scipy.interpolate import RBFInterpolator

# points: (N, d) array of N points in d dimensions
# values: (N,) array of values at those points
interp = RBFInterpolator(points, values, kernel='cubic')
values_new = interp(points_new)
```

## Multivariate Interpolation (Grid Data)

### `RegularGridInterpolator(points, values, method='linear', bounds_error=True, fill_value=None)`

Interpolate on a regular grid. `points` is a tuple of 1-D arrays defining the grid axes.

```python
from scipy.interpolate import RegularGridInterpolator
import numpy as np

# Define grid
x = np.linspace(0, 1, 10)
y = np.linspace(0, 1, 10)
z = np.sin(x[:, None]) * np.cos(y[None, :])  # values on grid

interp = RegularGridInterpolator((x, y), z, method='linear')
# Query at arbitrary points
points_query = np.random.uniform(0, 1, size=(100, 2))
values_query = interp(points_query)
```

**Method options:** `'linear'`, `'nearest'`, `'slinear'` (cubic in 1-D), `'cubic'`, `'quintic'`.

## 1-D Spline Smoothing and Approximation

### `make_smoothing_spline(x, y, lam=None)`

Smoothing spline (minimizes roughness penalty). Returns `LSQSubspaceSpline`.

### `make_lsq_spline(x, y, t=None, weights=None)`

Least-squares spline approximation. Given data and interior knots, finds best-fit spline.

```python
from scipy.interpolate import make_lsq_spline

# Interior knots
knots = np.linspace(x.min(), x.max(), 10)
spl = make_lsq_spline(x, y, t=knots, k=3)
y_smooth = spl(x_fine)
```

### `make_splrep(x, y, w=None, s=None, k=3)`

Wrapper for FITPACK `splrep`. Returns `(t, c, k)` triple.

### `generate_knots(x, k, extrapolation=None)`

Generate knot sequences from data points.

## Rational Approximation

### `AAA(f, domain=(-1, 1), ...)`

AAA algorithm for rational approximation of a function. Returns `(r, h)` where `r` is the rational function and `h` is the error bound.

```python
from scipy.interpolate import AAA

f = lambda z: np.exp(z)
r, h = AAA(f, domain=(-1, 1), n=20)
# r(z) approximates f(z) with error bounded by h
```

## FITPACK Interfaces (Legacy)

These are lower-level wrappers around the FITPACK Fortran library. Prefer the higher-level classes above.

### 1-D FITPACK

| Function | Description |
|---|---|
| `splrep(x, y, w=None, s=None, k=3)` | B-spline representation of data |
| `splprep(u, x, u0=None, ub=None, s=None, k=3)` | Parametric spline |
| `splev(x, tck, der=0)` | Evaluate spline and derivatives |
| `spalde(tck, x)` | Evaluate spline with all derivatives |
| `splint(a, b, tck)` | Integrate a spline |
| `sproot(tck)` | Find roots of a spline |
| `splder(tck, n=1)` | Derivative of spline |
| `splev_deriv(tck, x, der=0)` | Evaluate with derivatives |

### 2-D FITPACK

| Function | Description |
|---|---|
| `bisplrep(x, y, z, ...)` | Bivariate spline representation |
| `bisplev(x, y, tck, ...)` | Evaluate bivariate spline |
| `rect_bispl(x, y, z, ...)` | Rectangular bivariate spline |
| `splftree(x, y, z, ...)` | Spline fitting tree |

### Object-oriented FITPACK

| Class | Description |
|---|---|
| `InterpolatedUnivariateSpliner` | 1-D interpolating spline (FITPACK) |
| `SmoothB_Spliner` | 1-D smoothing spline (FITPACK) |
| `BivariateSpliner` | 2-D spline (FITPACK) |
| `RectBivariateSpline(x, y, z, ...)` | Rectangular bivariate spline |
| `splmake(x, y, z, kx=3, ky=3)` | Spline from rectangular grid data |

## Choosing the Right Interpolator

| Use case | Recommended |
|---|---|
| Smooth curve through points (1-D) | `CubicSpline` or `make_interp_spline` |
| Monotonicity/shape preservation | `PchipInterpolator` |
| Robust to outliers | `Akima1DInterpolator` |
| Scattered 1-D data, fast queries | `BarycentricInterpolator` |
| Grid data (2-D+) | `RegularGridInterpolator` |
| Scattered data (2-D+) | `RBFInterpolator` |
| C¹ smooth 2-D scattered | `CloughTocher2DInterpolator` |
| Smoothing noisy data | `make_smoothing_spline` or `savgol_filter` (from scipy.signal) |
| Parametric curves | `splprep` / `splev` |
