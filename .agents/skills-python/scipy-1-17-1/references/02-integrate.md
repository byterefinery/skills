# scipy.integrate Reference

Numerical integration and ODE/BVP solvers.

## Table of Contents

- [Definite Integration (Function Object)](#definite-integration-function-object)
- [Integration from Samples](#integration-from-samples)
- [ODE Initial Value Problems](#ode-initial-value-problems)
- [ODE Boundary Value Problems](#ode-boundary-value-problems)
- [Legacy ODE API](#legacy-ode-api)
- [Summation](#summation)

## Definite Integration (Function Object)

### `quad(func, a, b, args=(), epsabs=1e-8, epsrel=1e-8, ...)`

General-purpose 1D integration using QUADPACK. Returns `(result, error_estimate)`.

```python
from scipy.integrate import quad

result, error = quad(lambda x: x**2, 0, 1)
# result ≈ 0.33333333333333337, error ≈ 3.7e-15
```

**Key parameters:**
- `args` — extra arguments passed to `func`
- `epsabs`, `epsrel` — absolute/relative error tolerance
- `limit` — max number of sub-intervals (default 50)
- `weight`, `wvar` — weighted integration (e.g., Chebyshev, Fourier)
- `points` — points of discontinuity within `[a, b]`
- Infinity is allowed: `quad(func, 0, np.inf)`

### Other multi-dimensional integrators

| Function | Description |
|---|---|
| `quad_vec(func, a, b)` | Vector-valued function integration |
| `cubature(func, bounds, ...)` | Multi-dimensional array-valued integration |
| `dblquad(func, a, b, gfun, hfun)` | Double integration ∫∫ f(x,y) dy dx |
| `tplquad(func, a, b, gfun, hfun, qfun, rfun)` | Triple integration |
| `nquad(func, ranges, ...)` | N-dimensional integration |
| `tanhsinh(func, a, b)` | Elementwise tanh-sinh quadrature |
| `qmc_quad(func, bounds, ...)` | Quasi-Monte Carlo N-D integration |

### Gaussian quadrature

| Function | Description |
|---|---|
| `fixed_quad(func, n, a=-1, b=1)` | Gaussian quadrature of order `n` |
| `newton_cotes(func, a, b, order=1)` | Newton-Cotes formula weights and error |
| `lebedev_rule(n)` | Lebedev quadrature rule on sphere |

## Integration from Samples

Integrate when you have discrete data points rather than a callable function.

### `trapezoid(y, x=None, dx=1.0, axis=-1)`

Trapezoidal rule integration (replaces deprecated `trapz`).

```python
from scipy.integrate import trapezoid
import numpy as np

x = np.linspace(0, 1, 100)
y = np.sin(np.pi * x)
result = trapezoid(y, x)  # ≈ 2/π ≈ 0.6366
```

### `simpson(y, x=None, dx=1.0, axis=-1)`

Simpson's rule (replaces deprecated `simps`). More accurate than trapezoidal for smooth functions.

```python
from scipy.integrate import simpson

result = simpson(y, x)  # more accurate than trapezoid for smooth data
```

### Other sample-based integrators

| Function | Description |
|---|---|
| `cumulative_trapezoid(y, x=None)` | Cumulative trapezoidal integration |
| `cumulative_simpson(y, x=None)` | Cumulative Simpson's rule |
| `romb(y, x=None, dx=1.0)` | Romberg integration (needs 2^k + 1 evenly-spaced samples) |

## ODE Initial Value Problems

### `solve_ivp(fun, t_span, y0, method='RK45', ...)`

Solve initial value problem `dy/dt = fun(t, y)`, `y(t0) = y0`. Returns `OdeSolution`.

**Methods:**

| Method | Type | Order | Stiff? | Notes |
|---|---|---|---|---|
| `RK45` | Explicit Runge-Kutta | 5(4) | No | Default, good for non-stiff |
| `RK23` | Explicit Runge-Kutta | 3(2) | No | Lower order, cheaper steps |
| `DOP853` | Explicit Runge-Kutta | 8 | No | High accuracy, expensive steps |
| `Radau` | Implicit Runge-Kutta | 5 | Yes | Stiff problems |
| `BDF` | Implicit multi-step | 1–5 | Yes | Stiff, variable order |
| `LSODA` | Automatic switching | — | Both | Auto-switches between Adams/BDF |

```python
from scipy.integrate import solve_ivp
import numpy as np

def lotka_volterra(t, y):
    x, y_pred = y
    alpha, beta, delta, gamma = 1.0, 1.0, 0.75, 1.5
    return [alpha * x - beta * x * y_pred,
            delta * x * y_pred - gamma * y_pred]

sol = solve_ivp(
    lotka_volterra,
    t_span=[0, 10],
    y0=[10, 5],
    method='RK45',
    t_eval=np.linspace(0, 10, 1000),  # evaluation points
    dense_output=True,                 # enable interpolation
    events=lambda t, y: y[0] - 10     # event: x crosses 10
)

# sol.t, sol.y — solution at evaluation points
# sol.sol(t) — interpolated solution (when dense_output=True)
```

**Key parameters:**
- `t_span` — `(t0, tf)` tuple
- `y0` — initial state vector
- `t_eval` — array of times for output
- `dense_output=True` — enables continuous interpolation via `sol.sol(t)`
- `events` — callable or list of callables; returns 0 at event
- `rtol`, `atol` — relative/absolute tolerances (default 1e-3, 1e-6)
- `max_step` — maximum step size
- `vectorized=True` — if `fun` accepts array of t values

### Direct solver class usage

```python
from scipy.integrate import RK45, BDF

solver = RK45(fun, t0, y0, tf)
solver.step()  # take one step
# solver.t, solver.y — current state
```

## ODE Boundary Value Problems

### `solve_bvp(fun, bc, x, y, ...)`

Solve boundary value problem `y' = fun(x, y)` with boundary conditions `bc(ya, yb) = 0`.

```python
from scipy.integrate import solve_bvp
import numpy as np

def fun(x, y):
    return [[y[0, :]], [-x * y[0, :] / (2 * x + 1)]]

def bc(ya, yb):
    return [ya[0] - 1, yb[0]]  # y(0) = 1, y(∞) → 0

x = np.linspace(0, 10, 100)
y = np.zeros((1, x.size))

sol = solve_bvp(fun, bc, x, y)
# sol.x — mesh points, sol.y — solution
```

## Legacy ODE API

### `odeint(func, y0, t, args=(), ...)`

Legacy Fortran-based ODE solver (ODEPACK/VODE). Still fast for simple problems. Prefer `solve_ivp` for new code.

```python
from scipy.integrate import odeint

sol = odeint(func, y0, t)  # returns (len(t), len(y0)) array
```

### Other legacy solvers

| Function | Description |
|---|---|
| `ode()` | Integrate using VODE/ZVODE with callbacks |
| `complex_ode()` | Convert complex ODE to real-valued and integrate |

## Summation

### `nsum(func, ranges, ...)`

N-dimensional summation of a series.

```python
from scipy.integrate import nsum
import numpy as np

# Compute ζ(2) = Σ 1/n²
result = nsum(lambda n: 1/n**2, [(1, np.inf)])
# ≈ π²/6 ≈ 1.644934
```
