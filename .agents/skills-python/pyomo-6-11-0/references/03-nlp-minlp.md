# NLP and MINLP: Reactor Design, Parameter Estimation, Multimodal Optimization

## Nonlinear Programming (NLP)

### Rosenbrock Function

Classic nonlinear test problem with a narrow curved valley.

```python
m = pyo.ConcreteModel()
m.x = pyo.Var([1, 2], initialize=(0, 0))
m.obj = pyo.Objective(
    expr=100*(m.x[2] - m.x[1]**2)**2 + (1 - m.x[1])**2
)
```

Solve with IPOPT or another NLP solver. The initial point matters for non-convex problems.

### Reactor Design (CSTRs in Series)

Series of continuous stirred-tank reactors; choose space velocity and concentrations to maximize the intermediate product `cb`.

```python
def create_model(k1, k2, k3, caf):
    model = pyo.ConcreteModel()

    model.sv = pyo.Var(initialize=1.0, within=pyo.PositiveReals)
    model.ca = pyo.Var(initialize=5000.0, within=pyo.PositiveReals)
    model.cb = pyo.Var(initialize=2000.0, within=pyo.PositiveReals)
    model.cc = pyo.Var(initialize=2000.0, within=pyo.PositiveReals)
    model.cd = pyo.Var(initialize=1000.0, within=pyo.PositiveReals)

    model.obj = pyo.Objective(expr=model.cb, sense=pyo.maximize)

    # Steady-state balances
    model.ca_bal = pyo.Constraint(
        expr=(0 == model.sv * caf - model.sv * model.ca
              - k1 * model.ca - 2.0 * k3 * model.ca**2.0))
    model.cb_bal = pyo.Constraint(
        expr=(0 == -model.sv * model.cb + k1 * model.ca - k2 * model.cb))
    model.cc_bal = pyo.Constraint(
        expr=(0 == -model.sv * model.cc + k2 * model.cb))
    model.cd_bal = pyo.Constraint(
        expr=(0 == -model.sv * model.cd + k3 * model.ca**2.0))

    return model

m = create_model(k1=5.0/6.0, k2=5.0/3.0, k3=1.0/6000.0, caf=10000.0)
status = pyo.SolverFactory('ipopt').solve(m)
pyo.assert_optimal_termination(status)
```

Key habits shown here: give every `Var` a sensible `initialize=` value, and assert optimal termination on the returned status object.

### Parameter Estimation

Fit model parameters to observed data. The disease-estimation example uses an `AbstractModel` with an error variable `eps_I` per observation; the objective minimizes the sum of squared errors.

```python
model = pyo.AbstractModel()

model.S_SI = pyo.Set(ordered=True)
model.P_REP_CASES = pyo.Param(model.S_SI)   # observed data (from .dat)
model.P_POP = pyo.Param()

model.I = pyo.Var(model.S_SI, bounds=(0, model.P_POP), initialize=1)
model.S = pyo.Var(model.S_SI, bounds=(0, model.P_POP), initialize=300)
model.beta = pyo.Var(bounds=(0.05, 70))     # parameters to estimate
model.alpha = pyo.Var(bounds=(0.5, 1.5))
model.eps_I = pyo.Var(model.S_SI, initialize=0.0)  # error variables

def _objective(model):
    return sum((model.eps_I[i]) ** 2 for i in model.S_SI)

model.objective = pyo.Objective(rule=_objective, sense=pyo.minimize)

def _InfDynamics(model, i):
    if i != 1:
        return (model.I[i]
                == (model.beta * model.S[i - 1] * model.I[i - 1] ** model.alpha)
                / model.P_POP)
    return pyo.Constraint.Skip

model.InfDynamics = pyo.Constraint(model.S_SI, rule=_InfDynamics)
```

The pattern: declare one error/eps variable per data point, tie it to the observation in a constraint or the objective, and minimize the squared sum.

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
| IPOPT | NLP | Open source | Interior-point, handles large problems |
| SNOPT | NLP | Commercial | Active-set, robust |
| KNITRO | NLP/MINLP | Commercial | Multiple algorithms |
| BARON | Global MINLP | Academic/Commercial | Guaranteed global optimum |
| ANTIGONE | Global MINLP | Open source | Available via NEOS |

## Gotchas

- **IPOPT needs a feasible or near-feasible starting point** for non-convex problems. Use `initialize=` on variables.
- **Nonlinear constraints require NLP-capable solvers**. GLPK and CBC cannot handle nonlinear constraints.
- **Check termination with `pyo.assert_optimal_termination(status)`** — it raises if the solve did not terminate optimally, which is cleaner than inspecting status codes by hand.
- **Piecewise convexity matters**. Convex piecewise functions can be represented without binary variables; nonconvex ones need SOS2 or binary formulations.
