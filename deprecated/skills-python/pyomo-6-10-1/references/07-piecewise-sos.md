# Piecewise Functions and Special Ordered Sets

## Piecewise Linear Functions

Represent nonlinear functions as piecewise linear approximations.

### Using `pyo.Piecewise`

```python
def f(model, x):
    return abs(x - 1) + 1.0

m = pyo.ConcreteModel()
m.X = pyo.Var(bounds=(-5, 5))
m.Z = pyo.Var()

m.con = pyo.Piecewise(
    m.Z,           # Range variable (output)
    m.X,           # Domain variable (input)
    pw_pts=[-5, 1, 5],       # Break points
    pw_constr_type='LB',     # Lower bound: Z >= f(X)
    f_rule=f,                # Function definition
)

m.obj = pyo.Objective(expr=m.Z, sense=pyo.minimize)
```

Options for `pw_constr_type`:
- `'LB'` — `Z >= f(X)` (lower bounding convex function)
- `'UB'` — `Z <= f(X)` (upper bounding concave function)
- `'E'`  — `Z == f(X)` (exact representation, needs binary vars for nonconvex)

### Indexed Piecewise

```python
m = pyo.ConcreteModel()
m.I = pyo.Set(initialize=[1, 2, 3])
m.X = pyo.Var(m.I, bounds=(0, 10))
m.Z = pyo.Var(m.I)

def f_rule(model, x):
    return x**2

m.pw = pyo.Piecewise(
    m.I, m.Z, m.X,
    pw_pts=[0, 2, 5, 10],
    pw_constr_type='LB',
    f_rule=f_rule,
)
```

### Piecewise with Explicit Points

```python
# Define breakpoints and function values explicitly
m.pw = pyo.Piecewise(
    m.Z, m.X,
    pw_pts=[0, 1, 2, 3],
    fpts=[0, 1, 4, 9],       # Function values at breakpoints
    pw_constr_type='LB',
)
```

## Special Ordered Sets (SOS)

### SOS1

At most one variable in the set is nonzero.

```python
# Mutually exclusive selection: only one option chosen
m = pyo.ConcreteModel()
m.I = pyo.Set(initialize=[1, 2, 3, 4, 5])
m.x = pyo.Var(m.I, within=pyo.NonNegativeReals)

# At most one x[i] is nonzero
m.sos1 = pyo.SOSConstraint(var=m.x, sos=1)
```

### SOS2

At most two adjacent variables are nonzero (used for piecewise linear interpolation).

```python
m = pyo.AbstractModel()
m.V = pyo.RangeSet(1, 5)
m.x = pyo.Var(m.V, within=pyo.PositiveReals)

# SOS2: at most 2 consecutive x values are nonzero
m.x_sos = pyo.SOSConstraint(var=m.x, sos=2)
```

SOS2 is the standard representation for piecewise linear functions. The variables correspond to breakpoints, and the nonzero weights interpolate between adjacent breakpoints.

### SOS with Weights

```python
m.sos = pyo.SOSConstraint(
    var=m.x,
    weight={1: 0, 2: 1, 3: 3, 4: 5, 5: 10},   # Breakpoint values
    sos=2,
)
```

## SOS2 Piecewise Example

Manual SOS2 formulation for piecewise linear cost.

```python
# Cost function with breakpoints at (0,0), (100,50), (300,120), (500,180)
m = pyo.ConcreteModel()
m.lamb = pyo.Var([0, 1, 2, 3], within=pyo.NonNegativeReals)  # Lambda weights

# SOS2 constraint
m.sos2 = pyo.SOSConstraint(var=m.lamb, sos=2)

# Convex combination
m.sum_lamb = pyo.Constraint(expr=sum(m.lamb[i] for i in [0,1,2,3]) == 1)

# x = sum(lambda_i * breakpoint_i)
breakpoints = [0, 100, 300, 500]
m.x_def = pyo.Constraint(
    expr=m.x == sum(m.lamb[i] * breakpoints[i] for i in [0,1,2,3])
)

# cost = sum(lambda_i * cost_i)
costs = [0, 50, 120, 180]
m.cost_def = pyo.Constraint(
    expr=m.cost == sum(m.lamb[i] * costs[i] for i in [0,1,2,3])
)
```

## Nonconvex Piecewise

Nonconvex piecewise functions require binary variables.

```python
# Nonconvex: use force_pw=True to prevent automatic simplification
m.con = pyo.Piecewise(
    m.Z, m.X,
    pw_pts=[0, 2, 5],
    f_rule=f,
    pw_constr_type='E',      # Exact representation
    force_pw=True,            # Force piecewise even if convex
)
# Generates binary variables internally
```

## Piecewise via Binary Formulation

Manual big-M formulation for nonconvex piecewise.

```python
m = pyo.ConcreteModel()
m.X = pyo.Var(bounds=(-5, 5))
m.Z = pyo.Var()
m.y = pyo.Var([0, 1], within=pyo.Binary)  # Segment selector

# Segment 0: Z >= -X + 2 for X in [-5, 1]
# Segment 1: Z >= X for X in [1, 5]
M = 100  # Big-M

m.seg0_lb = pyo.Constraint(expr=m.Z >= -m.X + 2 - M*(1-m.y[0]))
m.seg1_lb = pyo.Constraint(expr=m.Z >= m.X - M*(1-m.y[1]))
m.select = pyo.Constraint(expr=m.y[0] + m.y[1] == 1)

# Domain constraints
m.dom0 = pyo.Constraint(expr=-5*m.y[0] <= m.X <= 1*m.y[0] + M*(1-m.y[0]))
m.dom1 = pyo.Constraint(expr=1*m.y[1] <= m.X <= 5*m.y[1] + M*(1-m.y[1]))
```

## Depot Siting with SOS2

Classic example: choose depot locations using SOS2 for piecewise cost.

```python
# Distance to nearest depot is piecewise linear function
# Use SOS2 to represent the distance-cost relationship
m = pyo.AbstractModel()
m.DEPOTS = pyo.Set()
m.CLIENTS = pyo.Set()

m.x = pyo.Var(m.CLIENTS, m.DEPOTS, within=pyo.Binary)  # Assignment
m.y = pyo.Var(m.DEPOTS, within=pyo.Binary)              # Open depot

# For each client, distance to assigned depot is piecewise linear
# Use SOS2 variables for cost approximation
```

## Gotchas

- **Convex piecewise with `LB` constraint auto-simplifies** — Pyomo detects convexity and avoids binary variables. Add `force_pw=True` to keep the full piecewise structure.
- **SOS2 requires solver support** — GLPK does not support SOS constraints. Use CPLEX, Gurobi, or reformulate with binary variables.
- **Breakpoint order matters** — `pw_pts` must be sorted in ascending order.
- **SOS weights define adjacency** — for SOS2, the weight values determine which variables are "adjacent" for interpolation purposes.
- **Piecewise exact representation (`E`) creates binaries** — even for convex functions, `pw_constr_type='E'` generates binary variables unless auto-simplification applies.
