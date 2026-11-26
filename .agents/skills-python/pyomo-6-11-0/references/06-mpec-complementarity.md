# MPEC: Mathematical Programs with Equilibrium Constraints

MPECs model problems where constraints include complementarity conditions — typically arising from equilibrium, bilevel optimization, or variational inequalities. `pyomo.mpec` provides `Complementarity` and `complements()`.

## Complementarity Basics

The notation `x ⟂ y` (read "x is complementary to y") means:
- `x >= 0`
- `y >= 0`
- `x * y = 0`

```python
from pyomo.environ import *
from pyomo.mpec import *

a = 100

model = ConcreteModel()
model.x1 = Var(bounds=(-2, 2))
model.x2 = Var(bounds=(-1, 1))

model.f = Objective(expr=-model.x1 - 2*model.x2)

# x1 >= 0 is complementary to x2 >= 0
model.c = Complementarity(expr=complements(model.x1 >= 0, model.x2 >= 0))
```

`complements(expr1, expr2)` accepts inequality expressions in `>= 0` / `<= 0` form; the constraint component is `Complementarity(expr=...)`.

## Indexed Complementarity

Multiple complementarity conditions over a set.

```python
n = 5
m = pyo.ConcreteModel()
m.x = pyo.Var(range(1, n+1))
m.f = pyo.Objective(
    expr=sum(i * (m.x[i] - 1)**2 for i in range(1, n+1))
)

def compl_rule(model, i):
    return complements(m.x[i] >= 0, m.x[i+1] >= 0)

m.compl = Complementarity(range(1, n), rule=compl_rule)
```

## LPEC Example

Linear programs with equilibrium constraints. Adapted from the classic LPEC example (S. Scholtes): minimize a linear objective over a polyhedron plus a complementarity condition.

```python
from pyomo.environ import *
from pyomo.mpec import *

model = ConcreteModel()

model.z = Var([1, 2], within=NonNegativeReals, initialize={1: 0, 2: 1})
model.z3 = Var(initialize=0)

model.objf = Objective(expr=model.z[1] + model.z[2] - model.z3)

model.lin1 = Constraint(expr=-4*model.z[1] + model.z3 <= 0)
model.lin2 = Constraint(expr=-4*model.z[2] + model.z3 <= 0)

# Complementarity between z[1] and z[2]
model.compl = Complementarity(expr=complements(0 <= model.z[1], model.z[2] >= 0))
```

## KKT-Based MPEC from Bilevel Optimization

Reformulate a bilevel problem by replacing the lower-level problem with its KKT conditions.

### Original Bilevel Problem

```
min    F(x, y)
s.t.   G(x, y) <= 0
       y solves:  min f(x, y)
                  s.t. g(x, y) <= 0
```

### MPEC Reformulation

Replace the lower-level with KKT conditions: stationarity, primal feasibility, dual feasibility, and complementarity for each lower-level constraint.

```python
from pyomo.mpec import Complementarity, complements

m = pyo.ConcreteModel()

# Upper-level variables
m.x = pyo.Var(within=pyo.NonNegativeReals)
m.y = pyo.Var(within=pyo.NonNegativeReals)

# Lower-level Lagrange multipliers (must be declared explicitly)
m.l = pyo.Var([1, 2, 3])

# Upper-level objective
m.f = pyo.Objective(expr=(m.x - 5)**2 + (2*m.y + 1)**2)

# KKT stationarity from the lower level (derive from your problem)
m.stationarity = pyo.Constraint(expr=...)

# Primal feasibility of the lower level
m.primal_1 = pyo.Constraint(expr=3*m.x - m.y - 3 >= 0)
m.primal_2 = pyo.Constraint(expr=-m.x + 0.5*m.y + 4 >= 0)
m.primal_3 = pyo.Constraint(expr=-m.x - m.y + 7 >= 0)

# Dual feasibility
m.dual_1 = pyo.Constraint(expr=m.l[1] >= 0)
m.dual_2 = pyo.Constraint(expr=m.l[2] >= 0)
m.dual_3 = pyo.Constraint(expr=m.l[3] >= 0)

# Complementarity: constraint activity * multiplier = 0
m.comp_1 = Complementarity(expr=complements(0 <= 3*m.x - m.y - 3, m.l[1] >= 0))
m.comp_2 = Complementarity(expr=complements(0 <= -m.x + 0.5*m.y + 4, m.l[2] >= 0))
m.comp_3 = Complementarity(expr=complements(0 <= -m.x - m.y + 7, m.l[3] >= 0))
```

## Linear Complementarity Problems (LCP)

Find `z >= 0` such that `w = M*z + q >= 0` and `z' * w = 0`.

```python
import numpy as np
from pyomo.mpec import Complementarity, complements

M = [[2, -1], [-1, 1]]
q = [-1, -2]
n = 2

m = pyo.ConcreteModel()
m.z = pyo.Var(range(n), within=pyo.NonNegativeReals)
m.w = pyo.Var(range(n), within=pyo.NonNegativeReals)

def w_rule(model, i):
    return m.w[i] == sum(M[i][j]*m.z[j] for j in range(n)) + q[i]
m.w_def = pyo.Constraint(range(n), rule=w_rule)

def compl_rule(model, i):
    return complements(m.z[i] >= 0, m.w[i] >= 0)
m.compl = Complementarity(range(n), rule=compl_rule)
```

## Common Applications

1. **Nash Equilibrium** — game theory, each player's strategy is a best response to others
2. **Market Equilibrium** — supply equals demand at equilibrium price
3. **Contact Mechanics** — normal force and gap cannot be simultaneously positive
4. **Bilevel Optimization** — leader-follower problems in supply chains, energy markets
5. **Variational Inequalities** — fixed-point problems, traffic assignment

## Solvers for MPEC

| Solver | Approach | Notes |
|--------|----------|-------|
| KNITRO | Slack-based reformulation | Handles complementarity natively |
| PATH | Lemke's algorithm | Specialized for LCP |
| SNOPT + reformulation | Perturbed/slack formulation | Requires manual reformulation |
| IPOPT | With MPEC-specific constraints | Needs careful formulation |

## Gotchas

- **MPECs are not standard MIPs** — standard MIP solvers cannot solve them directly. Use specialized solvers or reformulations (slack-based, Scholtes, KKT).
- **KKT reformulation assumes the lower-level problem is convex** (and that appropriate constraint qualifications hold). Nonconvex lower levels require global optimization approaches.
- **Complementarity is nonconvex** — `x*y = 0` defines a nonconvex feasible set. Standard NLP solvers may find only local solutions.
- **Use `complements(lower_expr, upper_expr)`** — both arguments must be inequality expressions (in `>= 0` / `<= 0` form).
- **Multipliers must be declared as explicit variables** — they are not automatically created by Pyomo.
