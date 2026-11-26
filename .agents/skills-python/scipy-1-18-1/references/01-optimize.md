# scipy.optimize Reference (1.18.1)

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
- [Utilities](#utilities)
- [Common Objects](#common-objects)

## Local Optimization

### `minimize(func, x0, method='Nelder-Mead', bounds=None, constraints=(), ...)`

Minimize a multivariate function. The objective must have signature `f(x, *args)` where `x` is a numpy array and the return is a float; extra parameters go through `args=(...)` or by wrapping the function. Returns `OptimizeResult` with `.x` (solution), `.fun` (value), `.success`, `.message`, `.nfev`, `.nit`.

**Solver comparison (from the user guide):**

| Method | Bounds | Nonlinear constraints | Uses gradient | Uses Hessian | Utilizes sparsity |
|---|---|---|---|---|---|
| `CG` | | | ✓ | | |
| `BFGS` | | | ✓ | | |
| `dogleg` | | | ✓ | ✓ | |
| `trust-ncg` | | | ✓ | ✓ | |
| `trust-krylov` | | | ✓ | ✓ | |
| `trust-exact` | | | ✓ | ✓ | |
| `Newton-CG` | | | ✓ | ✓ | ✓ |
| `Nelder-Mead` | ✓ | | | | |
| `Powell` | ✓ | | | | |
| `L-BFGS-B` | ✓ | | ✓ | | |
| `TNC` | ✓ | | ✓ | | |
| `COBYLA` | ✓ | ✓ | | | |
| `COBYQA` | ✓ | ✓ | | | |
| `SLSQP` | ✓ | ✓ | ✓ | | |
| `trust-constr` | ✓ | ✓ | ✓ | ✓ | ✓ |

Gradient-based methods converge faster when `jac` (and `hess`/`hessp` where supported) are supplied. `trust-constr` is the only method utilizing sparsity. If multiple candidates fit, try several and compare execution time and objective value.

**Constraint formats differ per method:**

- `trust-constr`, `COBYLA`, `COBYQA`: constraints are sequences of `LinearConstraint(A, lb, ub)` and `NonlinearConstraint(fun, lb, ub, jac=..., hess=...)`; bounds via a `Bounds(lb, ub)` object.
- `SLSQP`: constraints are dictionaries `{'type': 'eq' | 'ineq', 'fun': ..., 'jac': ...}` (for `'ineq'`, `fun(x) >= 0`).
- `bounds` may be a `Bounds` object or an array of `(min, max)` pairs.

```python
from scipy.optimize import minimize, Bounds, LinearConstraint, NonlinearConstraint
import numpy as np

# Unconstrained
res = minimize(lambda x: x[0]**2 + x[1]**2, x0=[1.0, 2.0], method='BFGS')
print(res.x, res.fun, res.success)

# Bounded
res = minimize(func, x0, method='L-BFGS-B', bounds=[(-1, 1), (0, None)])

# trust-constr with constraint objects
bounds = Bounds([0, -0.5], [1.0, 2.0])
lc = LinearConstraint([[1, 2], [2, 1]], [-np.inf, 1], [1, 1])  # lb <= A@x <= ub
nc = NonlinearConstraint(lambda x: x[0]**2 + x[1], 0, 1,
                         jac=lambda x: 2*x[0])
res = minimize(func, x0, method='trust-constr', bounds=bounds, constraints=[lc, nc])
```

### `minimize_scalar(func, bracket=None, bounds=None, method='brent')`

Minimize a univariate function. Methods: `brent` (unconstrained), `bounded` (with bounds), `golden`. Result: `.x`, `.fun`, `.success`.

```python
from scipy.optimize import minimize_scalar
res = minimize_scalar(lambda x: (x - 3)**2, bracket=[0, 5])
# res.x → 3.0
```

## Global Optimization

All return `OptimizeResult` with `.x` and `.fun`.

| Function | Description |
|---|---|
| `differential_evolution(func, bounds, ...)` | Population-based; bounds required; good default for bounded black-box problems |
| `basinhopping(func, x0, ...)` | Stochastic escape from local minima; pairs with a local minimizer |
| `brute(func, ranges, ...)` | Brute-force grid search |
| `shgo(func, bounds, ...)` | Simplicial homology global optimizer |
| `dual_annealing(func, bounds, ...)` | Dual annealing (simulated annealing variant) |
| `direct(func, bounds, ...)` | DIRECT (Dividing Rectangles) |

## Scalar Root-Finding

### `root_scalar(func, bracket=[a, b], method='brentq')`

Unified interface for scalar root-finding. Result: `RootResults` with `.root`, `.converged`, `.function_calls`, `.iterations`.

| Method | Bracket Required | Notes |
|---|---|---|
| `brentq` (default) | Yes | Recommended bracketing method |
| `brenth` | Yes | Brent modified with hyperbolic extrapolation |
| `bisect` | Yes | Bisection, guaranteed, slowest |
| `ridder` | Yes | Ridder's method |
| `toms748` | Yes | Alefeld, Potra & Shi Algorithm 748 |
| `newton` | No | Needs `x0` (or `x1`); `fprime` improves convergence |
| `secant` | No | Needs two initial points |
| `halley` | No | Needs `fprime` and `fprime2` |

Each method also has a direct function (`brentq`, `brenth`, `bisect`, `newton`, `toms748`) callable without `root_scalar`.

```python
from scipy.optimize import root_scalar

# Bracketing (needs a sign change on [a, b])
res = root_scalar(lambda x: x**3 - x - 1, bracket=[1, 2], method='brentq')
print(res.root)  # ≈ 1.3247

# Newton (faster, needs a good initial guess)
res = root_scalar(lambda x: x**3 - x - 1, x0=1.5,
                  fprime=lambda x: 3*x**2 - 1, method='newton')
```

Fixed-point form: `fixed_point(g, x0)` solves `x = g(x)`.

## Multivariate Root-Finding

### `root(func, x0, method='hybr', jac=None, tol=1e-05, ...)`

Solve `func(x) = 0` for multivariate `x`; `func` must return an array of residuals. Methods (`ROOT_METHODS`): `hybr` (default, modified Powell hybrid), `lm` (Levenberg-Marquardt, good for least-squares form), `broyden1`, `broyden2`, `anderson`, `linearmixing`, `diagbroyden`, `excitingmixing`, `krylov`, `df-sane` (derivative-free, bound-constrained). Defaults: `rtol=1e-3`, `atol=1e-6`. For large problems, Krylov-style methods and preconditioning are the recommendation.

```python
from scipy.optimize import root

def equations(x):
    return [x[0]**2 + x[1] - 10, x[0] + x[1]**2 - 10]

res = root(equations, x0=[1, 1])
print(res.x)  # ≈ [2.39, 2.39] or [3.08, -0.08]
```

## Least-Squares and Curve Fitting

### `curve_fit(func, xdata, ydata, p0=None, sigma=None, absolute_sigma=False, ...)`

Fit `func(x, *params)` to data (wrapper around `least_squares`). Returns `(optimal_params, covariance_matrix)`; `sqrt(diag(pcov))` gives standard errors.

```python
from scipy.optimize import curve_fit
import numpy as np

def model(x, a, b, c):
    return a * np.exp(-b * x) + c

popt, pcov = curve_fit(model, xdata, ydata, p0=[1, 0.1, 0])
```

### `least_squares(func, x0, bounds=(-np.inf, np.inf), method='trf', ...)`

Nonlinear least-squares; `func` returns the residual array. Methods: `trf` (trust-region reflective, default), `dogbox`. Bounds supported; `diff` controls finite-difference Jacobian.

### Linear least-squares

| Function | Description |
|---|---|
| `nnls(A, b)` | Non-negative least squares (the `atol` argument was removed in 1.18.0) |
| `lsq_linear(A, b, bounds)` | Bounded linear least squares |
| `isotonic_regression(y)` | Isotonic regression via PAVA |

## Linear Programming / MILP

### `linprog(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None, bounds=None, method='highs', ...)`

Minimize `c @ x` s.t. `A_ub @ x <= b_ub`, `A_eq @ x == b_eq`, `l <= x <= u`. Methods: `highs` (default, HiGHS solver), `highs-ds` (dual simplex), `highs-ipm` (interior point), `simplex`, `revised simplex`, `interior-point`. To maximize, negate `c`; "greater-than" constraints must be flipped (multiply by -1). `linprog_verbose_callback` is provided for callback-style progress reporting.

```python
from scipy.optimize import linprog

# Minimize: -x - y
# Subject to: x + 2y <= 14, 3x - y <= 12, x, y >= 0
res = linprog(c=[-1, -1],
              A_ub=[[1, 2], [3, -1]],
              b_ub=[14, 12],
              bounds=[(0, None), (0, None)])
print(res.x)
```

### `milp(c, constraints, integrality=None, bounds=None, ...)`

Mixed-integer linear programming. Constraints are `LinearConstraint` objects; `integrality` is per-variable 0 (continuous) / 1 (integer); solved by HiGHS (MILP support requires `method='highs'`, the default).

```python
from scipy.optimize import milp, LinearConstraint, Bounds
import numpy as np

constraints = [LinearConstraint([[1, 2]], 10, np.inf)]   # x0 + 2*x1 >= 10
res = milp(c=[1, 1], constraints=constraints,
           bounds=Bounds([0, 0], [np.inf, np.inf]),
           integrality=[1, 0])
```

## Assignment Problems

### `linear_sum_assignment(cost_matrix)`

Solve the linear-sum assignment problem. Returns `(row_indices, col_indices)`.

```python
import numpy as np
from scipy.optimize import linear_sum_assignment

cost = np.array([[4, 1, 3], [2, 0, 5], [3, 2, 2]])
row_ind, col_ind = linear_sum_assignment(cost)
print(cost[row_ind, col_ind].sum())  # minimum total cost
```

## Constraint Classes

| Class | Description |
|---|---|
| `Bounds(lb, ub)` | Simple bound constraints per variable |
| `LinearConstraint(A, lb, ub)` | Linear constraints: `lb <= A @ x <= ub` |
| `NonlinearConstraint(fun, lb, ub, jac=None, hess=None, hessp=None)` | Nonlinear: `lb <= fun(x) <= ub` |
| `BFGS`, `SR1` | Hessian update strategies for `trust-constr` |

## Utilities

| Function | Description |
|---|---|
| `show_options(solver=None, method=None, disp=True)` | Print the method-specific `options` documentation for a solver — use it instead of guessing option names |
| `approx_fprime(f, x0, epsilon=None, ...)` | Approximate the gradient of a scalar function |
| `check_grad(f, x0, fprime=None, epsilon=1e-8, ...)` | Check a supplied derivative against finite differences |
| `bracket(f, x1, x2, ...)` | Bracket a minimum given two starting points |
| `line_search` | Return a step satisfying the strong Wolfe conditions |
| `rosen(x, ...)`, `rosen_der(x, ...)` | Rosenbrock function and its derivative (benchmarks) |

## Common Objects

| Object | Description |
|---|---|
| `OptimizeResult` | Result from `minimize`, `minimize_scalar`, global optimizers: `x`, `fun`, `success`, `message`, `nfev`, ... |
| `RootResults` | Root-finding result: `root`, `function_calls`, `converged`, `iterations` |
| `OptimizeWarning` | Raised when an optimizer encounters problems |
