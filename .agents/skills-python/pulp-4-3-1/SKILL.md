---
name: pulp-4-3-1
description: >
  PuLP 4.3.1 — Python LP/MILP modeler with a Rust-backed core for linear,
  mixed-integer, and binary programming. Use when the user mentions optimization,
  linear programming (LP), mixed-integer programming (MIP), MILP, integer
  programming, solver selection (CBC, HiGHS, GLPK, Gurobi, CPLEX, COPT, MOSEK,
  XPRESS, SCIP, CP-SAT, GLOP, Clarabel, cuOpt), transportation problems,
  assignment, blending, set partitioning, Sudoku via MIP, column generation,
  cutting stock, dual values and shadow prices, warm starts, or migrating PuLP
  3.x code to 4.x. Covers the 4.3.1 API — `prob.add_variable()`,
  `add_variable_dicts()`, `add_variable_dict()`, `add_variable_matrix()`,
  `add_column()`, `LpSolveStats` returned by `prob.solve()`, `LpSolveStatus`
  enum, editable constraints, `prob.resolve()` in-place solves, `lpSum`,
  `lpDot`, `value`, LP/MPS/JSON export, and solver extras. Requires Python 3.12+;
  install with `pip install "pulp[cbc]"` to bundle the CBC solver.
---

# pulp 4.3.1

## Overview

PuLP is a Python modeler for linear programming (LP), mixed-integer linear programming (MILP), and binary problems. In the 4.x line the model core is Rust-backed and the API is problem-centred: variables are created **by the problem** (`prob.add_variable(...)`) and belong to it, and `prob.solve()` returns an `LpSolveStats` object instead of an integer status code.

PuLP 4 requires **Python 3.12 or newer** and installs as a platform wheel. CBC is no longer bundled (`PULP_CBC_CMD` is removed): `pip install "pulp[cbc]"` (the `cbcbox` wheel) or a `cbc` executable on `PATH`, used through `COIN_CMD`, is the default open-source path. Other solvers come from optional extras (`pulp[highs]`, `pulp[glpk]`, `pulp[gurobi]`, `pulp[cplex]`, `pulp[xpress]`, `pulp[scip]`, `pulp[ortools]`, `pulp[clarabel]`, `pulp[cylp]`, `pulp[copt]`, `pulp[mosek]`).

## Usage

### Quick start

```python
from pulp import LpProblem, LpMinimize, LpBinary, value

prob = LpProblem("example", LpMinimize)

# Variables are created by the problem and belong to it
x = prob.add_variable("x", lowBound=0, upBound=4)
y = prob.add_variable("y", lowBound=-1, upBound=1)
z = prob.add_variable("z", cat=LpBinary)

# Adding a bare expression sets the objective
prob += x + 4 * y + 9 * z, "Objective"

# Named constraints
prob += x + y <= 5, "C1"
prob += x + z >= 10, "C2"
prob += -y + z == 7, "C3"

# solve() returns an LpSolveStats, not a status code
stats = prob.solve()          # default solver (COIN_CMD when CBC is available)
print(stats.status_str)       # e.g. "Optimal"
for v in prob.variables():
    print(v.name, "=", v.varValue)
print("Objective =", value(prob.objective))
```

### Variable creation

| Call | Returns |
|---|---|
| `prob.add_variable(name, lowBound=None, upBound=None, cat=LpContinuous)` | one `LpVariable` |
| `prob.add_variable_dicts(prefix, indices, ...)` | flat dict (one index) or nested dicts (tuple of indices) |
| `prob.add_variable_dict(prefix, (idx1, idx2), ...)` | one flat dict keyed by tuples |
| `prob.add_variable_matrix(prefix, (idx1, idx2), ...)` | nested lists, indexed by position |
| `prob.add_column(name, ..., obj=..., coefficients={c: a})` | a `LpVariable` with coefficients in existing constraints |

- `lowBound`/`upBound` default to `None` (unbounded); pass `None`, not `float("inf")`.
- `cat` is `LpContinuous` (default), `LpInteger`, or `LpBinary`. A binary variable is stored as an integer with bounds 0 and 1, so `z.cat` reads `"Integer"` — check binaries with `z.isBinary()`.
- `add_variable_dicts` with a tuple of indices builds nested dicts; variable names join the prefix and indices with `_` (a `%s` placeholder per index works in the prefix).
- The problem must exist before its variables; pass the problem into helper functions that build variables.

### Solving and reading results

```python
from pulp import LpSolveStatus, COIN_CMD

stats = prob.solve(COIN_CMD(msg=False, timeLimit=60))

if stats.status == LpSolveStatus.Optimal:
    ...
if stats.has_solution:          # any feasible solution the solver returned
    ...
print(stats.objective, stats.time, stats.best_bound, stats.gap_rel)
```

- `stats.status` is the `LpSolveStatus` IntEnum (`Optimal=1`, `Infeasible=-1`, `Unbounded=-2`, `Undefined=-3`, plus `TimeLimit`, `MemoryLimit`, `NodeLimit`, `GapLimit`, `IterationLimit`, `SolutionLimit`, `Interrupted`, `Stopped`, `NumericalError`). `stats.status_str` is the member name.
- `LpSolveStats` also has `solver`, `cpu_time`, `best_bound`, `gap_abs`, `num_variables`, `num_constraints`, `is_mip`, `solver_options`, and (for log-parsing solvers) `logs` plus `solver_version`, `nodes`, `root_time`, `presolve`, `cut_info`, `first_solution`.
- The problem no longer carries `status`, `sol_status`, `solutionTime`, `solutionCpuTime`, or `bestBound`.
- Duals, slacks, reduced costs: `c.pi`, `c.slack` on constraints, `v.dj` on variables.

### Constraints and objective

- `prob += expr, "name"` adds a constraint (a bare expression becomes the objective) and returns the **problem**; use `prob.addConstraint(expr, "name")` when you want to keep the returned `LpConstraint`.
- `prob.constraints()` returns all constraints **as a list**, in the order added; `prob.get_constraint_by_name(name)` looks one up by name (`None` if absent).
- Constraint editing (`c[x] = 2`, `c.changeRHS(8)`, `c.sense = ...`) and column-wise modelling (`add_column`, `remove_variables`, `prob.resolve()`) are documented in [02-editing-and-column-wise](references/02-editing-and-column-wise.md).

### Common helpers

- `lpSum([...])` — sum of expressions, or a list of `(var, coeff)` pairs
- `lpDot(coeffs, vars)` — dot product of two lists
- `lpSum_vars(vars)` — batch sum of variables with coefficient 1 (fast Rust path; all must belong to the same model)
- `value(expr)` / `valueOrDefault(expr)` — evaluate with solved values
- `allpermutations(items, k)` / `allcombinations(items, k)` — index-set combinatorics
- `makeDict(...)` / `splitDict(...)` — reshape nested data for dict-indexed variables

## Gotchas

- **`prob.solve()` returns `LpSolveStats`, not a status code** — the `LpStatus*` constants and the `LpStatus` dict are removed. Use `stats.status == LpSolveStatus.Optimal` and `stats.has_solution`.
- **"Optimal" now means optimal** — a solver stopped at a time limit reports `LpSolveStatus.TimeLimit` (with `has_solution=True` when it found a solution). 3.x-style `if prob.status == LpStatusOptimal` checks now silently reject time-limited solutions; decide explicitly between `has_solution` and `Optimal`.
- **Create variables with `prob.add_variable(...)`** — calling `LpVariable(...)` directly raises `TypeError`. `LpVariable.dicts/dict/matrix`, `prob.addVariable(s)`, `LpConstraintVar`, and `LpVariable(..., e=...)` are all removed.
- **A variable cannot be used in another problem** — adding an expression containing a foreign variable raises `PulpError`. Build the variables inside each problem.
- **`prob.constraints` is a method returning a list** — `prob.constraints["c"]` raises `TypeError`; use `prob.get_constraint_by_name("c")`.
- **Editing the expression you added does not edit the problem** — the problem keeps its own copy and PuLP raises a `UserWarning` when you edit a sense-bearing expression. Edit the `LpConstraint` instead (`c[x] = 2`, `c.changeRHS(8)`).
- **`PULP_CBC_CMD` is gone** — CBC comes from `pulp[cbc]` (the `cbcbox` wheel) or a `cbc` executable on PATH, used via `COIN_CMD` (same arguments as before). With no solver available, `prob.solve()` raises `PulpError: No solver available`.
- **Solver module imports dropped the `_api` suffix** — `from pulp.apis.coin import COIN_CMD`, not `pulp.apis.coin_api`.
- **Problems cannot be pickled** — use `prob.toDict()` / `prob.toJson(path)` and `LpProblem.fromDict(data)` / `fromJson(path)`, which return `(variables_dict, problem)`.
- **Elastic constraints are removed** — model the penalty explicitly: non-negative slack variables plus a penalty term in the objective.
- **Constructor-style modelling is gone** — build expressions with operators (`x + y <= 5`) or `LpAffineExpression.from_dict(...)` / `from_list(...)`; `LpAffineExpression({...})` and `LpConstraint(e, sense, name, rhs)` are not callable constructors anymore.
- **Unknown solver keyword arguments are passed through to the solver library** — a parameter the solver does not accept raises the solver's own error (or `PulpSolverError` for `HiGHS`), not a silent ignore.

## References

- [01-solvers](references/01-solvers.md) — Solver catalog and PyPI extras, `COIN_CMD`/`HiGHS`/`CPSAT`/`GLOP`/`CLARABEL`/`CYLP`/`CUOPT` details, paths and env vars, `LpSolver_API` three-step, solver export
- [02-editing-and-column-wise](references/02-editing-and-column-wise.md) — Editing constraints in place, `add_column` / `remove_variables`, `prob.resolve()` in-place solves, cutting-stock column generation
- [03-export-and-warm-start](references/03-export-and-warm-start.md) — LP/MPS/JSON export and import, caveats, MIP start values and `warmStart`
- [04-model-patterns](references/04-model-patterns.md) — Transportation, blending, Sudoku, set partitioning, two-stage stochastic, cutting stock; examples/ catalog
- [05-migrate-from-3-x](references/05-migrate-from-3-x.md) — Complete 3.x → 4.x breaking-change mapping, status enum values, removed names
