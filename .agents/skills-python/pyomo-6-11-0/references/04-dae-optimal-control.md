# DAE and Optimal Control: Differential Equations, Discretization, Path Constraints

## DAE Fundamentals

The `pyomo.dae` module extends Pyomo with continuous-time modeling. Key components (import from `pyomo.dae`):

- **`ContinuousSet`** — a bounded continuous domain (time, space); declared with `bounds=(lo, hi)` or `initialize=[points]`
- **`DerivativeVar`** — declares the derivative of a variable; `wrt=` selects the continuous set (a tuple of sets gives mixed/multiple derivatives)
- **`Integral`** — integral of a variable over a continuous set
- **Discretization transforms** — convert the DAE to an algebraic system so it can be solved

```python
import pyomo.environ as pyo
import pyomo.dae as dae

m = pyo.ConcreteModel()
m.tf = pyo.Param(initialize=1)
m.t = dae.ContinuousSet(bounds=(0, m.tf))
m.x1 = pyo.Var(m.t)
m.dx1 = dae.DerivativeVar(m.x1, wrt=m.t)
```

A `ContinuousSet` cannot be solved until every continuous set in the model has been discretized. `first()` and `last()` give the lower/upper boundary points.

## Optimal Control Problem

Classic example (minimize the final state, subject to ODEs and a path constraint).

```python
m = pyo.ConcreteModel()
m.tf = pyo.Param(initialize=1)
m.t = dae.ContinuousSet(bounds=(0, m.tf))

# State and control variables
m.u = pyo.Var(m.t, initialize=0)
m.x1 = pyo.Var(m.t)
m.x2 = pyo.Var(m.t)
m.x3 = pyo.Var(m.t)

# Derivatives
m.dx1 = dae.DerivativeVar(m.x1, wrt=m.t)
m.dx2 = dae.DerivativeVar(m.x2, wrt=m.t)
m.dx3 = dae.DerivativeVar(m.x3)   # wrt inferred for a single continuous set

# Differential equations (indexed constraints over the continuous set)
def _x1dot(m, t):
    return m.dx1[t] == m.x2[t]
m.x1dotcon = pyo.Constraint(m.t, rule=_x1dot)

def _x2dot(m, t):
    return m.dx2[t] == -m.x2[t] + m.u[t]
m.x2dotcon = pyo.Constraint(m.t, rule=_x2dot)

def _x3dot(m, t):
    return m.dx3[t] == m.x1[t]**2 + m.x2[t]**2 + 0.005*m.u[t]**2
m.x3dotcon = pyo.Constraint(m.t, rule=_x3dot)

# Objective: minimize x3 at final time
m.obj = pyo.Objective(expr=m.x3[m.tf])

# Path constraint: must hold at all times
def _con(m, t):
    return m.x2[t] - 8*(t - 0.5)**2 + 0.5 <= 0
m.con = pyo.Constraint(m.t, rule=_con)

# ODEs are not enforced at the first time point — deactivate them there
m.x1dotcon[m.t.first()].deactivate()
m.x2dotcon[m.t.first()].deactivate()
m.x3dotcon[m.t.first()].deactivate()

# Initial conditions: fix the state variables at the start
m.x1[0].fix(0)
m.x2[m.t.first()].fix(-1)
m.x3[m.t.first()].fix(0)
```

## Discretization Methods

Discretization uses registered transforms, applied with `apply_to` (in place) or `create_using` (new model).

### Finite Difference

```python
discretizer = pyo.TransformationFactory('dae.finite_difference')
discretizer.apply_to(m, nfe=20, wrt=m.t, scheme='BACKWARD')
# scheme: 'FORWARD', 'BACKWARD', or 'CENTERED'
# nfp: points per finite element (default 1)
```

### Collocation

Higher-order accuracy using polynomial approximation within each element.

```python
discretizer = pyo.TransformationFactory('dae.collocation')
discretizer.apply_to(m, nfe=10, ncp=3, wrt=m.t)
# scheme: 'LAGRANGE-LEGENDRE' or 'LAGRANGE-RADAU'
```

After discretization, the `ContinuousSet` is replaced by a finite set of points and the derivative variables become algebraic expressions. Solve the result with any algebraic/NLP solver. You can apply multiple discretizations (e.g., different `wrt` sets or schemes) to the same model in sequence.

## PDE Examples

Partial differential equations use multiple `ContinuousSet`s and mixed derivatives.

```python
m.t1 = dae.ContinuousSet(bounds=(0, 1))
m.t2 = dae.ContinuousSet(bounds=(0, 1))

m.x = pyo.Var(m.t1, m.t2)
# Second derivative with respect to (t1, t1)
m.dx2 = dae.DerivativeVar(m.x, wrt=(m.t1, m.t1))
# Mixed partial
m.dxy = dae.DerivativeVar(m.x, wrt=(m.t1, m.t2))

# Discretize each continuous set separately
fd = pyo.TransformationFactory('dae.finite_difference')
fd.apply_to(m, wrt=m.t1, nfe=10, scheme='BACKWARD')
fd.apply_to(m, wrt=m.t2, nfe=100, scheme='FORWARD')
```

## Consistent Initialization

`pyomo.dae.initialization` provides helpers to find state values consistent with the DAE at the initial time point (useful when initial conditions are not fully specified): `get_inconsistent_initial_conditions(...)` and `solve_consistent_initial_conditions(...)`.

## Typical Workflow

1. Define model with `ContinuousSet`, `Var(continuous_set)`, `DerivativeVar`
2. Write differential equations as indexed constraints over the continuous set
3. Fix initial conditions with `.fix()` at the first time point
4. Deactivate (or skip) derivative constraints at the first point
5. Add path constraints if needed
6. Apply a discretization transform (`dae.finite_difference` or `dae.collocation`)
7. Solve the resulting algebraic model with an appropriate solver (IPOPT for nonlinear)

## Gotchas

- **Discretization must be applied before solving** — a model with an undiscretized `ContinuousSet` cannot be sent to a solver.
- **Initial conditions use `.fix()`**, not constraints. Fixed variables are treated as constants by solvers.
- **Deactivate derivative constraints at the first time point** — the official pattern is `m.con[m.t.first()].deactivate()` after construction (alternatively return `pyo.Constraint.Skip` in the rule).
- **There is no `pyomo.dae.FiniteDifference` class** — discretizers are obtained by name: `pyo.TransformationFactory('dae.finite_difference')` / `'dae.collocation'`.
- **Use `wrt=` in `DerivativeVar`** when multiple continuous sets exist (e.g., PDEs with time and space); a tuple like `wrt=(m.t, m.t)` gives higher-order derivatives.
- **Collocation gives higher accuracy with fewer elements** but produces a larger algebraic system; finite difference is simpler and cheaper to prototype with.
- **Implicit summation over a `ContinuousSet`** in an expression is fixed at construction time and is not updated when discretization adds points — build expressions after discretization if they must reference the discretized points.
