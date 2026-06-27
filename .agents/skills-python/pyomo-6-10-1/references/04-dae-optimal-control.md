# DAE and Optimal Control: Differential Equations, Discretization, Path Constraints

## DAE Fundamentals

Pyomo's `pyomo.dae` module extends Pyomo with continuous-time modeling. Key components:

- **`ContinuousSet`** — Represents a continuous domain (time, space)
- **`DerivativeVar`** — Declares the derivative of a variable
- **Discretization transforms** — Convert DAE to algebraic system for solving

## Optimal Control Problem

```python
import pyomo.environ as pyo
from pyomo.dae import ContinuousSet, DerivativeVar

m = pyo.ConcreteModel()

# Continuous time set
m.t = ContinuousSet(bounds=(0, 1))

# State and control variables
m.x1 = pyo.Var(m.t, bounds=(0, 1))
m.x2 = pyo.Var(m.t, bounds=(0, 1))
m.u = pyo.Var(m.t, initialize=0)

# Derivatives
m.dx1 = DerivativeVar(m.x1)
m.dx2 = DerivativeVar(m.x2)

# Differential equations
def x1dot_rule(m, t):
    if t == 0:
        return pyo.Constraint.Skip
    return m.dx1[t] == m.u[t]

m.x1dot = pyo.Constraint(m.t, rule=x1dot_rule)

def x2dot_rule(m, t):
    if t == 0:
        return pyo.Constraint.Skip
    return m.dx2[t] == m.x1[t]**2 + m.u[t]**2

m.x2dot = pyo.Constraint(m.t, rule=x2dot_rule)

# Initial conditions
m.x1[0].fix(1)
m.x2[0].fix(0)

# Objective: minimize x2 at final time
m.obj = pyo.Objective(expr=m.x2[1])
```

## Discretization Methods

### Finite Difference

Simple discretization, suitable for quick prototyping.

```python
from pyomo.dae import FiniteDifference

# Apply finite difference with 20 intervals
dae.FiniteDifference.apply(
    m,
    nfe=20,                      # Number of finite elements
    nfp=1,                       # Points per element (1 = backward Euler)
    wrt=m.t,                     # Variable to discretize
    scheme='BACKWARD',           # or 'CENTERED'
)
```

After discretization, the `ContinuousSet` becomes a regular `RangeSet` and derivatives become algebraic expressions. Solve with any algebraic solver.

### Collocation

Higher-order accuracy using polynomial approximation within each element.

```python
from pyomo.dae import Collocation

dae.Collocation.apply(
    m,
    nfe=10,                      # Fewer elements needed vs finite difference
    ncp=3,                       # Collocation points per element
    wrt=m.t,
)
```

Collocation gives higher accuracy with fewer discretization points but produces larger algebraic systems.

## Path Constraints

Inequality constraints that must hold at all times.

```python
# State path constraint: x2(t) <= 8*(t-0.5)^2 - 0.5
def path_rule(m, t):
    return m.x2[t] - 8*(t - 0.5)**2 + 0.5 <= 0

m.path_con = pyo.Constraint(m.t, rule=path_rule)
```

## Parameter Estimation from DAE

Fit model parameters to observed trajectory data.

```python
m = pyo.ConcreteModel()
m.t = ContinuousSet(bounds=(0, 10))
m.x = pyo.Var(m.t)
m.dx = DerivativeVar(m.x)
m.k = pyo.Param(mutable=True)  # Parameter to estimate

# ODE: dx/dt = -k * x
def ode_rule(m, t):
    if t == 0:
        return pyo.Constraint.Skip
    return m.dx[t] == -m.k * m.x[t]
m.ode = pyo.Constraint(m.t, rule=ode_rule)

# Fit to observed data
observed = {0: 1.0, 2: 0.67, 4: 0.45, 6: 0.30, 8: 0.20, 10: 0.14}
def fit_rule(m, t):
    if t in observed:
        return (m.x[t] - observed[t])**2
    return pyo.Constraint.Skip
m.fit = pyo.Constraint(m.t, rule=fit_rule)

m.obj = pyo.Objective(expr=sum(m.fit[t] for t in m.t if t in observed))
```

## PDE Examples

Partial differential equations use multiple ContinuousSets.

```python
# Heat equation: du/dt = alpha * d2u/dx2
m = pyo.ConcreteModel()
m.t = ContinuousSet(bounds=(0, 1))
m.x = ContinuousSet(bounds=(0, 10))

m.u = pyo.Var(m.t, m.x)
m.ut = DerivativeVar(m.u, wrt=m.t)
m.uxx = DerivativeVar(m.u, wrt=m.x, order=2)

def heat_rule(m, t, x):
    if t == 0:
        return pyo.Constraint.Skip
    return m.ut[t,x] == 0.1 * m.uxx[t,x]

m.heat = pyo.Constraint(m.t, m.x, rule=heat_rule)
```

## Simulation vs Optimization

- **Simulation**: Fix all inputs/parameters, solve DAE forward in time. Use `pyomo.dae.initialization` helpers.
- **Optimization**: Optimize control variables or parameters subject to DAE constraints.

## Typical Workflow

1. Define model with `ContinuousSet`, `Var(continuous_set)`, `DerivativeVar`
2. Write differential equations as indexed constraints over the continuous set
3. Set initial conditions with `.fix()`
4. Add path constraints if needed
5. Apply discretization transform (`FiniteDifference` or `Collocation`)
6. Solve resulting algebraic model with appropriate solver

## Gotchas

- **Skip first time point in derivative constraints** — derivatives at t=0 are undefined; use `if t == 0: return pyo.Constraint.Skip`.
- **Discretization must be applied before solving** — the DAE is not solvable as-is. Apply transform, then solve the discretized model.
- **Initial conditions use `.fix()`**, not constraints. Fixed variables are treated as constants by solvers.
- **Collocation needs more memory** than finite difference for same accuracy. Start with finite difference, switch to collocation if accuracy is insufficient.
- **Use `wrt=` in `DerivativeVar`** when multiple continuous sets exist (e.g., PDEs with time and space).
