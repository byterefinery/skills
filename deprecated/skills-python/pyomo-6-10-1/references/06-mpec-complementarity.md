# MPEC: Mathematical Programs with Equilibrium Constraints

MPECs model problems where constraints include complementarity conditions — typically arising from equilibrium, bilevel optimization, or variational inequalities.

## Complementarity Basics

The notation `x ⟂ y` (read "x is complementary to y") means:
- `x >= 0`
- `y >= 0`
- `x * y = 0`

In Pyomo:

```python
from pyomo.mpec import Complementarity, complements

m = pyo.ConcreteModel()
m.x = pyo.Var()
m.y = pyo.Var()

# x >= 0 ⟂ y >= 0
m.compl = Complementarity(
    expr=complements(m.x >= 0, m.y >= 0)
)
```

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

Replace lower-level with KKT conditions:

```python
from pyomo.mpec import Complementarity, complements

m = pyo.ConcreteModel()

# Upper-level variables
m.x = pyo.Var(within=pyo.NonNegativeReals)
m.y = pyo.Var(within=pyo.NonNegativeReals)

# Lower-level Lagrange multipliers
m.l = pyo.Var([1, 2, 3])

# Upper-level objective
m.f = pyo.Objective(expr=(m.x - 5)**2 + (2*m.y + 1)**2)

# KKT stationarity from lower-level
m.stationarity = pyo.Constraint(
    expr=grad_f_y - sum(m.l[k] * grad_gk_y for k in [1,2,3]) == 0
)

# Primal feasibility of lower-level
m.primal_1 = pyo.Constraint(expr=3*m.x - m.y - 3 >= 0)
m.primal_2 = pyo.Constraint(expr=-m.x + 0.5*m.y + 4 >= 0)
m.primal_3 = pyo.Constraint(expr=-m.x - m.y + 7 >= 0)

# Dual feasibility
m.dual_1 = pyo.Constraint(expr=m.l[1] >= 0)
m.dual_2 = pyo.Constraint(expr=m.l[2] >= 0)
m.dual_3 = pyo.Constraint(expr=m.l[3] >= 0)

# Complementarity: primal * dual = 0
m.comp_1 = Complementarity(
    expr=complements(0 <= 3*m.x - m.y - 3, m.l[1] >= 0)
)
m.comp_2 = Complementarity(
    expr=complements(0 <= -m.x + 0.5*m.y + 4, m.l[2] >= 0)
)
m.comp_3 = Complementarity(
    expr=complements(0 <= -m.x - m.y + 7, m.l[3] >= 0)
)
```

## Scholtes C-Regularity

For numerical solution, MPECs often need reformulation to satisfy constraint qualifications. The Scholtes reformulation replaces complementarity with perturbed constraints.

```python
# Scholtes reformulation: x*y = 0 becomes x + y >= ε, x - y >= -ε
# Or use specialized MPEC solvers that handle complementarity natively
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

1. **Nash Equilibrium** — Game theory, each player's strategy is best response to others
2. **Market Equilibrium** — Supply equals demand at equilibrium price
3. **Contact Mechanics** — Normal force and gap cannot be simultaneously positive
4. **Bilevel Optimization** — Leader-follower problems in supply chain, energy markets
5. **Variational Inequalities** — Fixed-point problems, traffic assignment

## Solvers for MPEC

| Solver | Approach | Notes |
|--------|----------|-------|
| KNITRO | Slack-based reformulation | Handles complementarity natively |
| PATH | Lemke's algorithm | Specialized for LCP |
| SNOPT + Scholtes | Perturbed formulation | Requires manual reformulation |
| Interior-point (IPOPT) | With MPEC-specific constraints | Needs careful formulation |

## Gotchas

- **MPECs are non-MIQP** — standard MIP solvers cannot solve them directly. Use specialized solvers or reformulations.
- **KKT reformulation assumes convexity** of the lower-level problem. Nonconvex lower levels require global optimization approaches.
- **Complementarity is nonconvex** — `x*y = 0` defines a nonconvex feasible set. Standard NLP solvers may find only local solutions.
- **Use `complements(lower_expr, upper_expr)`** — both arguments must be inequality expressions (>= 0 form).
- **Multipliers must be declared as explicit variables** — they are not automatically created by Pyomo.
