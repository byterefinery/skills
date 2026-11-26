# Piecewise Functions and Special Ordered Sets

## Piecewise Linear Functions

The `pyo.Piecewise` component adds piecewise-linear constraints of the form `y = f(x)` (or one-sided bounds) for a function defined by breakpoints.

### Using `pyo.Piecewise`

```python
def f(model, x):
    return abs(x - 1) + 1.0

m = pyo.ConcreteModel()
m.X = pyo.Var(bounds=(-5, 5))
m.Z = pyo.Var()

m.con = pyo.Piecewise(
    m.Z,                # range variable (output)
    m.X,                # domain variable (input)
    pw_pts=[-5, 1, 5],  # breakpoints (ALWAYS REQUIRED)
    pw_constr_type='LB',# Z >= f(X)
    f_rule=f,            # f(model, ..., x) -> value at domain point x
)

m.obj = pyo.Objective(expr=m.Z, sense=pyo.minimize)
```

`f_rule` is either a function `f(model, [indices...], x)` whose last argument is the domain value (a plain number, not a Var), or a list/dict of range values evaluated at `pw_pts`.

### Keyword Arguments

- **`pw_pts`** — breakpoints; must be non-decreasing. Duplicated points represent vertical segments (step functions).
- **`pw_constr_type`** — `'LB'` (Z >= f(X)), `'UB'` (Z <= f(X)), `'EQ'` (Z == f(X)).
- **`pw_repn`** — formulation: `'SOS2'` (default), `'BIGM_BIN'` (big-M with binaries), `'BIGM_SOS1'`, `'CC'`, `'DCC'`, `'DLOG'`, `'LOG'`, `'MC'`, `'INC'` (incremental delta). Some representations (BIGM_SOS1, BIGM_BIN, MC) do not support step functions; `'INC'` does.
- **`force_pw`** — by default, if the function is convex with `'LB'` bounds (or concave with `'UB'`), the piecewise constraints are automatically simplified to linear constraints; `force_pw=True` keeps the full piecewise structure.
- **`unbounded_domain_var`** — allow an unbounded domain Var (the breakpoints still bound it per index).
- **`warn_domain_coverage`** — warn when breakpoints do not cover the domain variable's bounds.

### Step Function

Duplicate domain points create vertical segments; choose a representation that supports steps (e.g., `'INC'`).

```python
DOMAIN_PTS = [0.0, 1.0, 1.0, 2.0, 2.0, 3.0]
RANGE_PTS  = [0.0, 0.0, 2.0, 2.0, 0.5, 0.5]

model = pyo.ConcreteModel()
model.X = pyo.Var(bounds=(0, 3))
model.Z = pyo.Var()

model.con = pyo.Piecewise(
    model.Z, model.X,
    pw_pts=DOMAIN_PTS,
    pw_constr_type='EQ',
    f_rule=RANGE_PTS,      # range values at the breakpoints
    pw_repn='INC',
)
model.obj = pyo.Objective(expr=model.Z + model.X, sense=pyo.maximize)
```

At duplicated domain points the range variable can take any value on the vertical segment — there is no discontinuous jump.

### Indexed Piecewise

```python
# Piecewise(index_1, ..., index_n, yvar, xvar, **Keywords)
m = pyo.ConcreteModel()
m.I = pyo.Set(initialize=[1, 2, 3])
m.X = pyo.Var(m.I, bounds=(0, 10))
m.Z = pyo.Var(m.I)

def f_rule(model, i, x):
    return x**2 + i

m.pw = pyo.Piecewise(
    m.I, m.Z, m.X,
    pw_pts=[0, 2, 5, 10],
    pw_constr_type='LB',
    f_rule=f_rule,
)
```

## Special Ordered Sets (SOS)

`pyo.SOSConstraint` declares special ordered sets of type 1, 2, ... over a Var component.

### SOS1

At most one variable in the set is nonzero — mutually exclusive selection.

```python
m = pyo.ConcreteModel()
m.I = pyo.Set(initialize=[1, 2, 3, 4, 5])
m.x = pyo.Var(m.I, within=pyo.NonNegativeReals)

# At most one x[i] is nonzero
m.sos1 = pyo.SOSConstraint(sos=1, var=m.x)
```

### SOS2

At most two *adjacent* variables are nonzero (adjacency determined by weights) — the standard representation for piecewise linear interpolation.

```python
m = pyo.ConcreteModel()
m.V = pyo.RangeSet(1, 5)
m.x = pyo.Var(m.V, within=pyo.NonNegativeReals)

# SOS2 with explicit weights (e.g., breakpoint positions)
m.x_sos = pyo.SOSConstraint(
    sos=2,
    var=m.x,
    weights={1: 0, 2: 1, 3: 3, 4: 5, 5: 10},
)
```

`SOSConstraint` accepts `sos=` (type), `var=` (the Var component), `index=` (optional subset), `weights=` (Param or dict; defaults derived from the var index set), or a `rule=` returning a variable list (2-tuple with weights) or `pyo.Constraint.Skip`.

### SOS2 Piecewise Example

Manual SOS2 formulation for piecewise linear cost.

```python
# Cost function with breakpoints at (0,0), (100,50), (300,120), (500,180)
m = pyo.ConcreteModel()
m.lamb = pyo.Var([0, 1, 2, 3], within=pyo.NonNegativeReals)  # lambda weights

m.sos2 = pyo.SOSConstraint(sos=2, var=m.lamb)
m.sum_lamb = pyo.Constraint(expr=sum(m.lamb[i] for i in [0, 1, 2, 3]) == 1)

breakpoints = [0, 100, 300, 500]
m.x_def = pyo.Constraint(
    expr=m.x == sum(m.lamb[i]*breakpoints[i] for i in [0, 1, 2, 3]))

costs = [0, 50, 120, 180]
m.cost_def = pyo.Constraint(
    expr=m.cost == sum(m.lamb[i]*costs[i] for i in [0, 1, 2, 3]))
```

The lambda weights interpolate between adjacent breakpoints; the sum-to-1 and SOS2 constraints keep the interpolation on a single segment.

## Nonconvex Piecewise

Nonconvex exact representations need integrality. Use a binary/SOS1-based representation:

```python
m.con = pyo.Piecewise(
    m.Z, m.X,
    pw_pts=[0, 2, 5],
    f_rule=f,
    pw_constr_type='EQ',   # exact representation
    pw_repn='BIGM_BIN',    # big-M with binary variables
)
```

## Piecewise via Manual Binary Formulation

Big-M segment selection (for learning or when the component does not fit).

```python
m = pyo.ConcreteModel()
m.X = pyo.Var(bounds=(-5, 5))
m.Z = pyo.Var()
m.y = pyo.Var([0, 1], within=pyo.Binary)   # segment selector

M = 100  # Big-M
m.seg0_lb = pyo.Constraint(expr=m.Z >= -m.X + 2 - M*(1-m.y[0]))
m.seg1_lb = pyo.Constraint(expr=m.Z >= m.X - M*(1-m.y[1]))
m.select = pyo.Constraint(expr=m.y[0] + m.y[1] == 1)

# Domain constraints per segment
m.dom0 = pyo.Constraint(expr=-5*m.y[0] <= m.X <= 1*m.y[0] + M*(1-m.y[0]))
m.dom1 = pyo.Constraint(expr=1*m.y[1] <= m.X <= 5*m.y[1] + M*(1-m.y[1]))
```

## Gotchas

- **Convex piecewise with `LB` auto-simplifies** — Pyomo detects convexity (or concavity for `UB`) and substitutes linear constraints, avoiding binaries/SOS. Use `force_pw=True` to keep the full piecewise structure.
- **`pw_constr_type` values are `'LB'`, `'UB'`, `'EQ'`** — not `'E'`.
- **There is no `fpts` keyword** — pass range values through `f_rule` as a list (or dict) aligned with `pw_pts`.
- **SOS2 requires solver support** — not all solvers handle SOS constraints (e.g., GLPK does not). Use CPLEX, Gurobi, or reformulate with binary variables (`pw_repn='BIGM_BIN'`).
- **Breakpoint order matters** — `pw_pts` must be non-decreasing; duplicates only for vertical segments.
- **SOS weights define adjacency** — for SOS2, the weight values determine which variables are "adjacent" for interpolation.
- **`SOSConstraint` kwarg is `weights=`** (dict or Param), not `weight=`.
