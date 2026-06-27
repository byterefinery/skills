# NLP and MINLP: Reactor Design, Parameter Estimation, Multimodal Optimization

## Nonlinear Programming (NLP)

### Rosenbrock Function

Classic nonlinear test problem.

```python
m = pyo.ConcreteModel()
m.x = pyo.Var([1, 2], initialize=(0, 0))
m.obj = pyo.Objective(
    expr=100*(m.x[2] - m.x[1]**2)**2 + (1 - m.x[1])**2
)
```

Solve with IPOPT or another NLP solver. Initial point matters for non-convex problems.

### Reactor Design

Optimize reactor dimensions for maximum conversion.

```python
m = pyo.ConcreteModel()
m.V = pyo.Var(bounds=(0, 10))           # Reactor volume
m.T = pyo.Var(bounds=(300, 500))         # Temperature
m.obj = pyo.Objective(
    expr=-(1 - exp(-0.1*m.V*m.T/8.314)),  # Negative for maximization
)
m.cost = pyo.Constraint(
    expr=100*m.V + 5*(m.T - 300) <= 2000
)
```

### Parameter Estimation

Fit model parameters to observed data.

```python
# Fit exponential decay: y = a * exp(-b*t) + c
observed = [(0, 10), (1, 6.7), (2, 4.5), (3, 3.0), (4, 2.1)]

m = pyo.ConcreteModel()
m.a = pyo.Var(bounds=(0, None))
m.b = pyo.Var(bounds=(0, None))
m.c = pyo.Var()

def residuals(model, t, y_obs):
    y_pred = m.a * pyo.exp(-m.b * t) + m.c
    return (y_pred - y_obs)**2

m.obj = pyo.Objective(
    expr=sum(residuals(m, t, y) for t, y in observed)
)
```

## Mathematical Programming with Equilibrium Constraints (MPEC)

### Complementarity Conditions

Model `x >= 0 ⟂ y >= 0` meaning `x >= 0, y >= 0, x*y = 0`.

```python
from pyomo.mpec import Complementarity, complements

m = pyo.ConcreteModel()
m.x = pyo.Var(within=pyo.NonNegativeReals)
m.y = pyo.Var(within=pyo.NonNegativeReals)

m.compl = Complementarity(
    expr=complements(m.x >= 0, m.y >= 0)
)
```

### KKT-Based MPEC

Two-level optimization reformulated via KKT conditions.

```python
from pyomo.mpec import Complementarity, complements

m = pyo.ConcreteModel()
m.x = pyo.Var(within=pyo.NonNegativeReals)
m.y = pyo.Var(within=pyo.NonNegativeReals)
m.l = pyo.Var([1, 2, 3])  # Lagrange multipliers

m.f = pyo.Objective(expr=(m.x - 5)**2 + (2*m.y + 1)**2)

# KKT stationarity
m.KKT = pyo.Constraint(
    expr=2*(m.y - 1) - 1.5*m.x + m.l[1] - m.l[2]*0.5 + m.l[3] == 0
)

# Complementarity for each constraint
m.lin_1 = Complementarity(
    expr=complements(0 <= 3*m.x - m.y - 3, m.l[1] >= 0)
)
m.lin_2 = Complementarity(
    expr=complements(0 <= -m.x + 0.5*m.y + 4, m.l[2] >= 0)
)
m.lin_3 = Complementarity(
    expr=complements(0 <= -m.x - m.y + 7, m.l[3] >= 0)
)
```

## Multimodal Optimization

For problems with multiple local optima, try different initial points.

```python
def solve_with_init(init_x, init_y):
    m = pyo.ConcreteModel()
    m.x = pyo.Var(initialize=init_x)
    m.y = pyo.Var(initialize=init_y)
    # ... define objective and constraints ...
    opt = pyo.SolverFactory('ipopt')
    return opt.solve(m)

# Try multiple starting points
for init in [(0, 0), (1, 1), (-1, -1), (2, 0.5)]:
    solve_with_init(*init)
```

## Piecewise Linear Approximation

Approximate nonlinear functions with piecewise linear segments.

```python
def f(model, x):
    return abs(x - 1) + 1.0

m = pyo.ConcreteModel()
m.X = pyo.Var(bounds=(-5, 5))
m.Z = pyo.Var()

m.con = pyo.Piecewise(
    m.Z, m.X,
    pw_pts=[-5, 1, 5],
    pw_constr_type='LB',
    f_rule=f,
)
m.obj = pyo.Objective(expr=m.Z, sense=pyo.minimize)
```

See [07-piecewise-sos](references/07-piecewise-sos.md) for detailed piecewise and SOS coverage.

## NLP Solvers

| Solver | Type | License | Notes |
|--------|------|---------|-------|
| IPOPT | NLP/MINLP | Open source | Interior-point, handles large problems |
| SNOPT | NLP | Commercial | Active-set, robust |
| KNITRO | NLP/MINLP | Commercial | Multiple algorithms |
| BARON | Global MINLP | Academic/Commercial | Guaranteed global optimum |
| ANTIGONE | Global MINLP | Open source | Via NEOS |

## Gotchas

- **IPOPT needs a feasible or near-feasible starting point** for non-convex problems. Use `initialize=` on variables.
- **Nonlinear constraints require NLP-capable solvers**. GLPK and CBC cannot handle nonlinear constraints.
- **MPEC reformulations are problem-specific**. The KKT-based approach requires manually deriving stationarity conditions.
- **Piecewise convexity matters**. Convex piecewise functions can be represented without binary variables; nonconvex ones need SOS2 or binary formulations.
