# Migrating PuLP 3.x code to 4.x

Source: PuLP 4.3.1 docs (`guides/how_to_migrate_to_v4.rst`). PuLP 4.0 moves the model into a Rust core. Most modelling code keeps working: `prob += ...`, `lpSum`, `lpDot`, `value`, constraint names, `writeLP`, `writeMPS` and the solver classes are the same. The breaking changes are in four places: variables are created **by the problem**, `prob.constraints` is a method returning a list, `solve()` returns an `LpSolveStats` object, and CBC is no longer bundled.

## On this page

- [Before you upgrade](#before-you-upgrade)
- [Quick reference](#quick-reference)
- [Status enum](#status-enum)
- [`LpSolveStats` fields](#lpsolvestats-fields)
- [Removed top-level names](#removed-top-level-names)
- [Custom solver classes](#custom-solver-classes)

## Before you upgrade

PuLP 3.3.1 and 3.3.2 emit a `DeprecationWarning` for most calls 4.0 removes, and already include the new methods (`add_variable`, `constraints()`, ...). Smooth path:

1. Run your code on `pulp==3.3.2` with `python -W error::DeprecationWarning my_model.py`.
2. Fix every warning using the mapping below — the code then runs on both 3.3.2 and 4.x.
3. Upgrade to 4.x and update the code that reads the solve result (`LpSolveStats`), which cannot be written for both versions.

Remove any `set_v4_migration_warnings(...)` call when upgrading — the function does not exist in 4.0.

## Quick reference

| PuLP 3.x | PuLP 4.x |
|---|---|
| `x = LpVariable("x", 0, 10)` | `x = prob.add_variable("x", 0, 10)` |
| `LpVariable.dicts("x", idx, 0)` | `prob.add_variable_dicts("x", idx, 0)` |
| `LpVariable.dict("x", idx, 0)` | `prob.add_variable_dict("x", idx, 0)` |
| `LpVariable.matrix("x", idx, 0)` | `prob.add_variable_matrix("x", idx, 0)` |
| `prob.addVariable(x)` / `addVariables(xs)` | not needed — variables belong to the problem that created them |
| `LpAffineExpression({x: 1, y: 2}, constant=3)` | `LpAffineExpression.from_dict({x: 1, y: 2}, constant=3)` |
| `LpConstraint(e, LpConstraintLE, "c", 5)` | `prob += e <= 5, "c"` |
| `prob.constraints["c"]` | `prob.get_constraint_by_name("c")` |
| `prob.constraints.values()` | `prob.constraints()` |
| `c = e <= 5; prob += c; c[x] = 2` | `c = prob.addConstraint(e <= 5); c[x] = 2` |
| `LpConstraintVar` / `LpVariable(..., e=...)` | `prob.add_column(name, ..., obj=..., coefficients={c: a})` |
| `status = prob.solve()` | `stats = prob.solve()` |
| `prob.status` | `stats.status` |
| `LpStatus[prob.status]` | `stats.status_str` |
| `LpStatusOptimal`, ... | `LpSolveStatus.Optimal`, ... |
| `prob.sol_status`, `LpSolution*` | `stats.has_solution` |
| `prob.solutionTime` / `solutionCpuTime` | `stats.time` / `stats.cpu_time` |
| `prob.bestBound` | `stats.best_bound` |
| `PULP_CBC_CMD(...)` | `COIN_CMD(...)` (with `pip install pulp[cbc]`) |
| `from pulp.apis.coin_api import COIN_CMD` | `from pulp.apis.coin import COIN_CMD` (or `from pulp import COIN_CMD`) |
| `pickle.dumps(prob)` | `prob.toDict()` / `prob.toJson(path)` |

Notes:

- The problem must exist before its variables — reorder code that created variables first, and pass the problem into helper functions.
- `LpVariable.fromDict` / `fromDataclass` take the problem as first argument: `LpVariable.fromDict(prob, data)`.
- `prob.copy()` / `deepcopy()` now copy the whole model, variables included — use the copy's own variables (`other.variablesDict()["x"]`).
- Solver imports from modules dropped the `_api` suffix (`pulp.apis.coin`, `pulp.apis.gurobi`).
- JSON written by 3.x loads in 4.0; 4.0 files are not readable by 3.x (no `status`/`sol_status`).

## Status enum

The `LpStatus*` constants and the `LpStatus` dict are replaced by the `LpSolveStatus` IntEnum, which keeps the old numbers (so `stats.status == 1` still works):

| PuLP 3.x | PuLP 4.x | Value |
|---|---|---|
| `LpStatusNotSolved` | `LpSolveStatus.NotSolved` | 0 |
| `LpStatusOptimal` | `LpSolveStatus.Optimal` | 1 |
| `LpStatusInfeasible` | `LpSolveStatus.Infeasible` | -1 |
| `LpStatusUnbounded` | `LpSolveStatus.Unbounded` | -2 |
| `LpStatusUndefined` | `LpSolveStatus.Undefined` | -3 |
| (new) | `LpSolveStatus.TimeLimit` | -4 |
| (new) | `LpSolveStatus.MemoryLimit` | -5 |
| (new) | `LpSolveStatus.NodeLimit` | -6 |
| (new) | `LpSolveStatus.GapLimit` | -7 |
| (new) | `LpSolveStatus.IterationLimit` | -8 |
| (new) | `LpSolveStatus.SolutionLimit` | -9 |
| (new) | `LpSolveStatus.Interrupted` | -10 |
| (new) | `LpSolveStatus.Stopped` | -11 |
| (new) | `LpSolveStatus.NumericalError` | -12 |

`stats.status_str` is the member's name — text changes slightly (`"Not Solved"` → `"NotSolved"`). To turn a stored integer into a name: `LpSolveStatus(code).name`.

**"Optimal" now means optimal.** In 3.x a solver stopped at a time limit with a feasible solution usually reported `LpStatusOptimal`; only `prob.sol_status` said it was not proven optimal. In 4.x the status says why the solver stopped and whether it returned a solution is `stats.has_solution`. Mapping of the removed `LpSolution*` constants:

| PuLP 3.x `prob.sol_status` | PuLP 4.x |
|---|---|
| `LpSolutionOptimal` | `stats.has_solution and stats.status == LpSolveStatus.Optimal` |
| `LpSolutionIntegerFeasible` | `stats.has_solution and stats.status != LpSolveStatus.Optimal` |
| `LpSolutionNoSolutionFound`, `LpSolutionInfeasible`, `LpSolutionUnbounded` | `not stats.has_solution` (and `stats.status` for the reason) |

`LpSolution*` constants and `LpStatusToSolution` are removed.

## `LpSolveStats` fields

Always filled: `solver`, `status`, `has_solution`, `time`, `cpu_time`, `objective`, `best_bound`, `num_variables`, `num_constraints`, `is_mip`, `solver_options`.

For solvers whose log PuLP can read (`COIN_CMD`, `CPLEX_CMD`, `CPLEX_PY`, `GUROBI`, `GUROBI_CMD`, `CPSAT`): `solver_version`, `nodes`, `root_time`, `presolve`, `matrix`, `cut_info`, `first_solution`, and the full parsed log in `logs` (`None` for other solvers). `print(stats)` shows a short summary; `stats.toDict()` / `stats.toJson(path)` export it.

## Removed top-level names

No longer importable from `pulp`:

- `PULP_CBC_CMD` — use `COIN_CMD`.
- `LpStatus`, `LpStatusNotSolved`, `LpStatusOptimal`, `LpStatusInfeasible`, `LpStatusUnbounded`, `LpStatusUndefined` — use `LpSolveStatus`.
- `LpSolution`, `LpSolutionNoSolutionFound`, `LpSolutionOptimal`, `LpSolutionIntegerFeasible`, `LpSolutionInfeasible`, `LpSolutionUnbounded`, `LpStatusToSolution` — use `LpSolveStats.has_solution`.
- `LpConstraintVar`, `LpElement`, `LpFractionConstraint`, `FixedElasticSubProblem`, `FractionElasticSubProblem`.
- `set_v4_migration_warnings`, `pulpTestAll`, `configSolvers`, `clock`, `VERSION` — use `pulp.__version__` for the version.

Also removed, without a direct equivalent: elastic constraints (`LpConstraint.makeElasticSubProblem`, `LpProblem.extend` — model the penalty explicitly with slack variables), `LpProblem.normalisedNames`, `unusedConstraintName`, `startClock`/`stopClock`, `assignStatus`.

## Custom solver classes

If you subclass `LpSolver` / `LpSolver_CMD`:

- `actualSolve(lp)` must return an `LpSolveStats` — build it with `self.buildStats(lp, status, has_solution, start=start)`, where `start` is `clocks()` (from `pulp.apis.core`) taken at the beginning of `actualSolve`. Do not call `lp.assignStatus` (removed).
- The API solvers' `findSolutionValues(lp)` returns a `(status, has_solution)` tuple instead of a status.
- Register the class with `pulp.apis.addSolver(MySolver)` so `getSolver("MY_SOLVER")` and `listSolvers()` can find it.

Since 4.3, solvers using an official Python interface inherit `LpSolver_API` and share the signatures `buildSolverModel(lp)`, `callSolver(lp, **kwargs)` and `findSolutionValues(lp, result=None)` (`result` is what `callSolver` returned); the old `setParams` / `_set_params` / `_setControls` methods are now `configureSolver(lp)`. A solver parameter the solver does not accept raises the solver library's own error (`PulpSolverError` for `HiGHS`).
