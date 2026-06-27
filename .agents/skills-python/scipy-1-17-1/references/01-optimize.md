# scipy.optimize Reference

Optimization, root-finding, curve fitting, and linear programming.

## Table of Contents

- [Local Optimization](#local-optimization)
- [Global Optimization](#global-optimization)
- [Scalar Root-Finding](#scalar-root-finding)
- [Multivariate Root-Finding](#multivariate-root-finding)
- [Least-Squares and Curve Fitting](#least-squares-and-curve-fitting)
- [Linear Programming / MILP](#linear-programming--milp)
- [Assignment Problems](#assignment-problems)
- [Constraint Classes](#constraint-classes)
- [Common Objects](#common-objects)

## Local Optimization

### `minimize(func, x0, method='Nelder-Mead', ...)`

Minimize a multivariate function. Returns `OptimizeResult`.

**Methods and their capabilities:**

| Method | Gradient | Hessian | Bounds | Constraints | Notes |
|---|---|---|---|---|---|
| `Nelder-Mead` | No | No | No | No | Simplex, derivative-free |
| `Powell` | No | No | No | No | Conjugate-direction |
| `CG` | Yes | No | No | No | Conjugate gradient |
| `BFGS` | No (approx) | No | No | No | Quasi-Newton |
| `L-BFGS-B` | No (approx) | No | Yes | No | Bounded, large-scale |
| `TNC` | No (approx) | No | Yes | No | Truncated Newton |
| `COBYLA` | No | No | Yes | Nonlinear | Derivative-free |
| `SLSQP` | No (approx) | No | Yes | Linear + nonlinear | Sequential quadratic |
| `trust-constr` | Optional | Optional | Yes | General | Most capable, slowest |
| `dogleg` | Yes | Yes | No | No | Trust-region |
| `trust-ncg` | Yes | Hessian×vector | No | Bounds | Large-scale trust-region |
| `trust-krylov` | Yes | No | No | No | Trust-region, no Hessian |
| `trust-exact` | Yes | Yes | No | No | Exact trust-region |

```python
from scipy.optimize import minimize, Bounds, NonlinearConstraint

# Unconstrained
res = minimize(lambda x: x[0]**2 + x[1]**2, x0=[1.0, 2.0], method='BFGS')
print(res.x, res.fun, res.success)

# Bounded
res = minimize(func, x0, method='L-BFGS-B', bounds=[(-1, 1), (0, None)])

# With nonlinear constraints
cons = NonlinearConstraint(lambda x: x[0] + x[1], 0, np.inf)
res = minimize(func, x0, method='trust-constr', constraints=cons)
```

### `minimize_scalar(func, bracket=None, bounds=None, method='brent')`

Minimize a univariate function. Methods: `brent`, `golden`, `bounded`.

```python
from scipy.optimize import minimize_scalar

res = minimize_scalar(lambda x: (x - 3)**2, bracket=[0, 5])
# res.x → 3.0
```

## Global Optimization

### `differential_evolution(func, bounds, ...)`

Stochastic global optimizer using differential evolution. Good for multimodal problems.

```python
from scipy.optimize import differential_evolution

bounds = [(-5, 5), (-5, 5)]
res = differential_evolution(lambda x: x[0]**2 + x[1]**2, bounds)
```

### Other global optimizers

| Function | Description |
|---|---|
| `basinhopping(func, x0)` | Stochastic basin-hopping optimizer |
| `brute(func, ranges)` | Brute-force grid search |
| `shgo(func, bounds)` | Simplicial homology global optimizer |
| `dual_annealing(func, bounds)` | Dual annealing (simulated annealing variant) |
| `direct(func, bounds)` | DIRECT (Dividing Rectangles) algorithm |

## Scalar Root-Finding

### `root_scalar(func, bracket=[a, b], method='brentq')`

Unified interface for scalar root-finding.

**Methods:**

| Method | Bracket Required | Derivatives | Convergence |
|---|---|---|---|
| `brentq` | Yes | No | Guaranteed, ~1.6 order |
| `brenth` | Yes | No | Guaranteed, faster than brentq |
| `bisect` | Yes | No | Guaranteed, linear (slowest) |
| `ridder` | Yes | No | Guaranteed, quadratic |
| `toms748` | Yes | No | Guaranteed, superlinear |
| `newton` | No | `fprime` optional | Quadratic if close |
| `secant` | No | No | ~1.62 order, not guaranteed |
| `halley` | No | `fprime`, `fprime2` | Cubic if close |

```python
from scipy.optimize import root_scalar

# Bracketing method (guaranteed convergence)
res = root_scalar(lambda x: x**3 - x - 1, bracket=[1, 2], method='brentq')
print(res.root)  # ≈ 1.3247

# Newton's method (faster but needs good initial guess)
res = root_scalar(
    lambda x: x**3 - x - 1,
    x0=1.5,
    fprime=lambda x: 3*x**2 - 1,
    method='newton'
)
```

### Direct function calls

`brentq(func, a, b)`, `bisect(func, a, b)`, `newton(func, x0, fprime=None)` — call directly without `root_scalar`.

## Multivariate Root-Finding

### `root(func, x0, method='hybr')`

Solve `func(x) = 0` for multivariate `x`.

**Methods:**

| Method | Description |
|---|---|
| `hybr` | Modified Powell hybrid (Jacobian via finite differences) |
| `lm` | Levenberg-Marquardt (good for least-squares form) |
| `broyden1`, `broyden2` | Quasi-Newton Broyden updates |
| `anderson` | Anderson mixing |
| `linearmixing` | Linear mixing |
| `diagbroyden` | Diagonal Broyden |
| `excitingmixing` | Exciting mixing |
| `krylov` | Krylov-based method |
| `dfsane` | Derivative-free, bound-constrained |

```python
from scipy.optimize import root

def equations(x):
    return [x[0]**2 + x[1] - 10, x[0] + x[1]**2 - 10]

res = root(equations, x0=[1, 1])
print(res.x)  # ≈ [2.39, 2.39] or [3.08, -0.08]
```

### `fixed_point(func, x0)`

Find fixed point where `func(x) = x`.

## Least-Squares and Curve Fitting

### `curve_fit(func, xdata, ydata, p0=None, sigma=None)`

Fit `func(x, *params)` to data. Returns `(optimal_params, covariance_matrix)`.

```python
from scipy.optimize import curve_fit
import numpy as np

def model(x, a, b, c):
    return a * np.exp(-b * x) + c

popt, pcov = curve_fit(model, xdata, ydata, p0=[1, 0.1, 0])
# popt → [a, b, c] optimal parameters
# pcov → covariance matrix (use sqrt(diag) for std errors)
```

### `least_squares(func, x0, method='trf', ...)`

Nonlinear least-squares with bounds support. Methods: `trf` (trust-region reflective), `lm` (Levenberg-Marquardt).

### Linear least-squares

| Function | Description |
|---|---|
| `nnls(A, b)` | Non-negative least squares |
| `lsq_linear(A, b, bounds)` | Bounded linear least squares |
| `isotonic_regression(y)` | Isotonic regression via PAVA |

## Linear Programming / MILP

### `linprog(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None, bounds=None, method='highs')`

Minimize `c^T x` subject to constraints.

**Methods:** `highs` (default, HiGHS solver), `highs-ipm`, `highs-ds`, `interior-point`, `simplex`, `revised_simplex`.

```python
from scipy.optimize import linprog

# Minimize: -x - y
# Subject to: x + 2y <= 14, 3x - y <= 12, x, y >= 0
res = linprog(
    c=[-1, -1],
    A_ub=[[1, 2], [3, -1]],
    b_ub=[14, 12],
    bounds=[(0, None), (0, None)],
    method='highs'
)
print(res.x)  # optimal x, y
```

### `milp(c, constraints, integrality=None, ...)`

Mixed-integer linear programming. Use `LinearConstraint` and `Bounds` objects.

```python
from scipy.optimize import milp, LinearConstraint, Bounds

# Minimize: x0 + x1
# Subject to: x0 + 2*x1 >= 10, x0 integer, x1 continuous >= 0
constraints = [
    LinearConstraint([[1, 2]], 10, np.inf),
]
bounds = Bounds(lb=[0, 0], ub=[np.inf, np.inf])
integrality = [1, 0]  # 1 = integer, 0 = continuous

res = milp(c=[1, 1], constraints=constraints, bounds=bounds, integrality=integrality)
```

## Assignment Problems

### `linear_sum_assignment(cost_matrix)`

Solve the linear-sum assignment problem (Hungarian algorithm). Returns `(row_indices, col_indices)`.

```python
from scipy.optimize import linear_sum_assignment

cost = np.array([[4, 1, 3], [2, 0, 5], [3, 2, 2]])
row_ind, col_ind = linear_sum_assignment(cost)
print(col_ind)      # optimal assignment per row
print(cost[row_ind, col_ind].sum())  # minimum total cost
```

## Constraint Classes

| Class | Description |
|---|---|
| `Bounds(lb, ub)` | Simple bound constraints per variable |
| `LinearConstraint(A, lb, ub)` | Linear constraints: `lb <= A @ x <= ub` |
| `NonlinearConstraint(fun, lb, ub, jac=None)` | Nonlinear: `lb <= fun(x) <= ub` |

## Common Objects

| Object | Description |
|---|---|
| `OptimizeResult` | Named tuple with `x`, `fun`, `success`, `message`, `nfev`, etc. |
| `RootResults` | Root-finding result with `root`, `function_values`, `success` |
| `show_options()` | Print available options for optimization solvers |
