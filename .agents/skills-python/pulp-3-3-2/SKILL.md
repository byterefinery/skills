---
name: pulp-3-3-2
description: >
  PuLP 3.3.2 — Python LP/MILP modeler for linear, mixed-integer, and binary programming.
  Use this skill whenever the user mentions optimization, linear programming (LP),
  mixed-integer programming (MIP), MILP, integer programming, solver selection,
  transportation problems, assignment problems, blending, scheduling, cutting stock,
  Sudoku solving via MIP, column generation, stochastic programming, sensitivity analysis,
  or any problem that can be expressed as minimizing/maximizing a linear objective
  subject to linear constraints. Covers PuLP 3.3.2 API including `prob.add_variable()`,
  `prob.add_variable_dicts()`, `prob.add_variable_matrix()`, `lpSum`, `lpDot`, solver
  configuration (CBC, HiGHS, GLPK, Gurobi, CPLEX, etc.), file I/O (LP/MPS), dual values,
  resolve workflows, and common modeling patterns. Install via `pip install "pulp[cbc]==3.3.2"` (the `[cbc]` extra bundles the CBC solver).
---

# pulp 3.3.2

## Overview

PuLP is a Python library for formulating and solving linear programming (LP), mixed-integer linear programming (MILP), and binary programming problems. It provides a clean, declarative API for building optimization models and dispatches to any installed solver (CBC included by default; supports HiGHS, GLPK, Gurobi, CPLEX, MOSEK, XPRESS, SCIP, COPT, SAS, CHOCO, MIPCL, and more).

Install with `pip install "pulp[cbc]==3.3.2"` — the `[cbc]` extra bundles the CBC solver so `prob.solve()` works out of the box without separate solver setup.

PuLP 3.3.2 introduces `prob.add_variable()` / `add_variable_dicts()` / `add_variable_matrix()` as the preferred API. The legacy `LpVariable()` constructor still works but emits deprecation warnings (removed in PuLP 4.0).

## Usage

### Quick Start

```python
from pulp import LpProblem, LpMinimize, value

prob = LpProblem("MyProblem", LpMinimize)

# Create variables attached to the problem
x = prob.add_variable("x", lowBound=0, upBound=4)
y = prob.add_variable("y", lowBound=-1, upBound=1)
z = prob.add_variable("z", lowBound=0)          # upper bound is +∞

# Objective
prob += x + 4*y + 9*z, "Objective"

# Constraints
prob += x + y <= 5, "C1"
prob += x + z >= 10, "C2"
prob += -y + z == 7, "C3"

# Solve (uses default CBC solver)
status = prob.solve()

print(f"Status: {LpStatus[status]}")
for v in prob.variables():
    print(f"{v.name} = {v.varValue}")
print(f"Objective = {value(prob.objective)}")
```

### Variable Categories

| Category | Constant | Usage |
|---|---|---|
| Continuous | `LpContinuous` (default) | Real-valued variables |
| Integer | `LpInteger` | Integer-valued variables |
| Binary | `LpBinary` | 0 or 1 only |

```python
b = prob.add_variable("binary_var", cat="Binary")        # 0 or 1
i = prob.add_variable("int_var", lowBound=0, cat="Integer")
c = prob.add_variable("cont_var", lowBound=0)            # continuous (default)
```

### Named Constraints and Variables

Always name constraints for debugging, sensitivity analysis, and resolve workflows:

```python
prob += x + y <= 5, "capacity"       # named constraint
c = prob.get_constraint_by_name("capacity")  # retrieve later
print(c.pi)   # dual value (shadow price)
print(c.slack)
```

### Common Expression Helpers

- `lpSum([x1, x2, ...])` — sum of variables or expressions
- `lpDot(coeffs, vars)` — dot product of two lists
- `value(expr)` — evaluate expression with solved variable values

```python
from pulp import lpSum, lpDot, value

# Sum: 3*x + 4*y
prob += lpSum([3*x, 4*y]) <= 100

# Dot product
costs = [2, 5, 3]
vars_list = [x1, x2, x3]
prob += lpDot(costs, vars_list)          # 2*x1 + 5*x2 + 3*x3

# Retrieve value after solving
print(value(x))                          # safe even if not solved yet
```

## Gotchas

- **Use `prob.add_variable()`, not `LpVariable()`** — The legacy constructor emits deprecation warnings and variables are not automatically attached to the model. In PuLP 4.0, `LpVariable()` standalone will be removed.
- **Use `prob.add_variable_dicts()` / `add_variable_matrix()`, not `LpVariable.dicts()` / `matrix()`** — Same deprecation applies.
- **`PULP_CBC_CMD` is deprecated** — Use `COIN_CMD()` or install HiGHS (`pip install highspy`) for better performance.
- **Constraint constant is stored as LHS, not RHS** — When modifying constraints for resolve, the constant on the left-hand side is negated relative to the right-hand side. E.g., `x + y <= 10` stores constant `-10`.
- **`prob.solve()` returns status code, not bool** — Check with `LpStatus[status] == "Optimal"` rather than truthiness.
- **Dual values (`pi`) require LP relaxation** — Solvers typically only return duals for continuous LP problems, not MILP. Solve the LP relaxation first if you need shadow prices.
- **`prob.roundSolution()` rounds integer variables** — Useful after solving a relaxed LP to get near-integer solutions before re-solving with integer constraints.
- **Variable names cannot contain `-+[] ->/`** — These characters are replaced with `_`. Use alphanumeric names with underscores.

## References

- [01-core-api](references/01-core-api.md) — LpProblem, LpVariable, LpAffineExpression, LpConstraint classes and operators
- [02-variable-creation](references/02-variable-creation.md) — add_variable, add_variable_dicts, add_variable_matrix with examples
- [03-solvers](references/03-solvers.md) — Solver selection, configuration, availability checks, time limits
- [04-model-patterns](references/04-model-patterns.md) — Transportation, assignment, blending, facility location, Sudoku, cutting stock
- [05-advanced-topics](references/05-advanced-topics.md) — Sensitivity analysis, resolve, column generation, stochastic programming, warm starts
