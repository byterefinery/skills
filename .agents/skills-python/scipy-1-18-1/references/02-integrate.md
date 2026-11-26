# scipy.integrate Reference (1.18.1)

Numerical integration and ODE/BVP solvers.

## Table of Contents

- [Definite Integration (Function Object)](#definite-integration-function-object)
- [Integration from Samples](#integration-from-samples)
- [ODE Initial Value Problems](#ode-initial-value-problems)
- [ODE Boundary Value Problems](#ode-boundary-value-problems)
- [Legacy ODE API](#legacy-ode-api)
- [Summation](#summation)

## Definite Integration (Function Object)

### `quad(func, a, b, args=(), full_output=0, epsabs=1.49e-8, epsrel=1.49e-8, ...)`

General-purpose 1-D integration (QUADPACK). Returns a **tuple** `(result, abs_error_estimate)` — not a scalar.

```python
from scipy.integrate import quad
import numpy as np

result, error = quad(lambda x: x**2, 0, 1)
# result ≈ 0.33333333333333337, error ≈ 3.7e-15
```

**Key parameters:**
- `args` — extra arguments passed to `func` (e.g. `quad(integrand, 0, 1, args=(a, b))`)
- `epsabs`, `epsrel` — absolute/relative error tolerances (default `1.49e-8` each)
- `limit` — max number of subintervals
- `points` — points of discontinuity within `[a, b]`
- `weight`, `wvar` — weighted integration (Chebyshev, Fourier, ...)
- Infinity is allowed: `quad(func, 0, np.inf)` or `quad(func, -np.inf, np.inf)`
- The integrand may itself call `quad` (nested integration), though the error bound may underestimate

```python
# Extra parameters via args=
def integrand(x, a, b):
    return a * x**2 + b
I, err = quad(integrand, 0, 1, args=(2, 1))  # ≈ 1.6667
```

### Other multi-dimensional integrators

| Function | Description |
|---|---|
| `quad_vec(func, a, b)` | Vector-valued function integration |
| `cubature(func, bounds, ...)` | Multi-dimensional array-valued integration |
| `dblquad(func, a, b, gfun, hfun)` | Double integration ∫∫ over `x∈[a,b]`, `y∈[gfun(x), hfun(x)]` |
| `tplquad(func, a, b, gfun, hfun, qfun, rfun)` | Triple integration |
| `nquad(func, ranges, ...)` | N-dimensional integration |
| `tanhsinh(func, a, b)` | tanh-sinh quadrature (good for endpoint singularities) |
| `qmc_quad(func, a, b, ...)` | Quasi-Monte Carlo quadrature |

### Gaussian quadrature

| Function | Description |
|---|---|
| `fixed_quad(func, a, b, args=(), n=5)` | Gauss-Legendre quadrature with a fixed number `n` of points (fast, no adaptivity) |
| `newton_cotes(rn, equal=0)` | Returns a Newton-Cotes rule (closed form when `equal=1`); call it as `rule(func, a, b)` |
| `lebedev_rule(...)` | Gauss-Lebedev quadrature rules (3-D spherical) |

## Integration from Samples

Integrate when you have discrete data points rather than a callable function.

### `trapezoid(y, x=None, dx=1.0, axis=-1)`

Composite trapezoidal rule.

```python
from scipy.integrate import trapezoid
import numpy as np

x = np.linspace(0, 1, 100)
y = np.sin(np.pi * x)
result = trapezoid(y, x)  # ≈ 2/π ≈ 0.6366
```

### `simpson(y, x=None, *, dx=1.0, axis=-1)`

Simpson's rule (more accurate than trapezoidal for smooth data). Note `dx` is keyword-only.

### Other sample-based integrators

| Function | Description |
|---|---|
| `cumulative_trapezoid(y, x=None, dx=1.0, axis=-1, initial=None)` | Cumulative trapezoidal integration |
| `cumulative_simpson(y, *, x=None, dx=1.0, axis=-1, initial=None)` | Cumulative Simpson's rule |
| `romb(y, dx=1.0, axis=-1, show=False)` | Composite Romberg integration (note: takes `dx`, not `x`) |

Rule of thumb: `trapezoid`/`simpson`/`romb` for sampled data; `quad`/`fixed_quad` when you have the function.

## ODE Initial Value Problems

### `solve_ivp(fun, t_span, y0, method='RK45', t_eval=None, dense_output=False, events=None, vectorized=False, args=None, **options)`

Solve `dy/dt = fun(t, y)` with `y(t0) = y0`. Note `fun` takes `t` **first**, then `y`. Higher-order ODEs are reduced to first-order systems by appending intermediate derivatives to `y`. Returns an `OdeSolution` object:

- `sol.t` — time grid actually used (auto-chosen if `t_eval` is not given)
- `sol.y` — shape `(len(y0), len(sol.t))`; **columns are solution states at each time point** (initial condition is the first column)
- `sol.sol` — dense interpolant when `dense_output=True`
- `sol.success`, `sol.message`

**Methods:** `RK45` (default, explicit), `RK23`, `DOP853` (high-order explicit), `Radau`, `BDF` (implicit, stiff), `LSODA` (auto stiff/non-stiff switching). `Radau`/`BDF`/`LSODA` need the Jacobian (`jac` argument or finite differences).

**Tolerances** go through `options`: `rtol` and `atol` default to `1e-3` and `1e-6` respectively — the user guide shows visible deviation from analytic solutions at defaults; pass tighter values (e.g. `rtol=1e-8, atol=1e-8`) when accuracy matters.

```python
from scipy.integrate import solve_ivp
import numpy as np

def lotka_volterra(t, y):
    x, yv = y
    return [1.0*x - 1.0*x*yv, 0.75*x*yv - 1.5*yv]

sol = solve_ivp(lotka_volterra, t_span=[0, 10], y0=[10, 5],
                t_eval=np.linspace(0, 10, 1000),
                dense_output=True,      # enables sol.sol(t)
                rtol=1e-8, atol=1e-8)
```

**Key parameters:**
- `t_span` — `(t0, tf)` tuple
- `y0` — initial state vector
- `t_eval` — array of times for output
- `events` — callable or list of callables; a zero crossing is an event
- `max_step` — maximum step size
- `vectorized=True` — if `fun` accepts arrays of `t` values

## ODE Boundary Value Problems

### `solve_bvp(fun, bc, x, y, p=None, S=None, fun_jac=None, bc_jac=None, ...)`

Solve boundary value problem `y' = fun(x, y)` with boundary conditions `bc(ya, yb) = 0` (values at `x[0]` and `x[-1]`). `x` is the mesh and `y` the initial guess. Returns a solution object with `.x`, `.y`, `.success`, `.message`.

```python
from scipy.integrate import solve_bvp
import numpy as np

def fun(x, y):
    return -x * y          # example system

def bc(ya, yb):
    return [ya[0] - 1, yb[0]]   # y(0) = 1, y(end) = 0

x = np.linspace(0, 10, 100)
y_guess = np.zeros((1, x.size))
sol = solve_bvp(fun, bc, x, y_guess)
```

## Legacy ODE API

### `odeint(func, y0, t, args=(), ...)`

Legacy Fortran-based ODE solver (ODEPACK/VODE). Note the function signature is `func(y, t, *args)` — `y` **first** (the reverse of `solve_ivp`). Returns a `(len(t), len(y0))` array. Still fast for simple problems; prefer `solve_ivp` for new code.

```python
from scipy.integrate import odeint
sol = odeint(func, y0, t)  # (len(t), len(y0)) array
```

### Other legacy/low-level solvers

| Function | Description |
|---|---|
| `ode(fun)` | Low-level integrator factory (VODE/ZVODE style); may raise `IntegratorConcurrencyError` for methods that do not support parallel execution |
| `complex_ode(fun)` | Complex-valued counterpart of `ode` |

## Summation

### `nsum(func, ranges, ...)`

N-dimensional numerical summation of a series.

```python
from scipy.integrate import nsum
import numpy as np

result = nsum(lambda n: 1/n**2, [(1, np.inf)])  # ≈ π²/6 ≈ 1.644934
```
