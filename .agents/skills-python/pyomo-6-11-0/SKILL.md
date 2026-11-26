---
name: pyomo-6-11-0
description: >
  Pyomo 6.11.0 — Python optimization modeling for LP, MIP, NLP, MINLP,
  DAE/optimal control, GDP (disjunctive programming), MPEC (equilibrium/
  complementarity), piecewise functions, network flow, and decomposition
  algorithms (Benders, column generation). Use this skill whenever the user
  mentions Pyomo, optimization modeling, mathematical programming,
  linear/nonlinear/mixed-integer programming, optimal control, differential
  equations optimization, disjunctive constraints, complementarity
  conditions, solver interfaces (Gurobi, CPLEX, IPOPT, GLPK, CBC, etc.),
  AMPL-style modeling in Python, or building optimization models with
  Python. Also use when the user asks about formulating LP/MIP/NLP models,
  network flow problems, facility location, lot sizing, transportation
  problems, diet/nutrition problems, parameter estimation, reactor design,
  job shop scheduling, or any mathematical optimization task in Python.
metadata:
  tags:
    - optimization
    - modeling
    - lp
    - mip
    - nlp
    - dae
    - gdp
    - mpec
---

# pyomo 6.11.0

Pyomo is a Python-based, open-source optimization modeling framework (BSD-3-Clause) that supports LP, MIP, NLP, MINLP, DAE, GDP, and MPEC formulations. It works with many solvers (Gurobi, CPLEX, GLPK, CBC, IPOPT, BARON, SCIP, GAMS, MOSEK, etc.) via `SolverFactory`. This is the last release to support Python 3.10 and the first tested against Python 3.15.

## Overview

Pyomo provides two modeling paradigms:

- **`ConcreteModel`** — Define model structure and data together in Python. Best for prototyping and small-to-medium models where data is available at construction time.
- **`AbstractModel`** — Define model structure first, then load data from Pyomo data files (`.dat`, `.yaml`, `.json`, Excel, SQL/SQLite) or a Python dict via `create_instance()`. Best for larger models with external data or AMPL-style workflows.

Core components: `Set`, `Param`, `Var`, `Objective`, `Constraint`, `Block`. Indexed variants accept sets as arguments (e.g., `Var(I, J)` creates variables indexed by `(i, j)`).

## Installation

```bash
pip install 'pyomo==6.11.0'
# or with optional dependencies (yaml/json dataportals, Excel, viewer, ...):
pip install 'pyomo[optional]==6.11.0'
```

Solvers install separately (e.g., `gurobipy`, `cplex`, or system packages for GLPK/CBC/IPOPT).

## Usage

### Quick Start (Concrete Model)

```python
import pyomo.environ as pyo

m = pyo.ConcreteModel()
m.x = pyo.Var(bounds=(0, None))
m.y = pyo.Var(within=pyo.Binary)
m.obj = pyo.Objective(expr=2*m.x + 3*m.y, sense=pyo.minimize)
m.c1 = pyo.Constraint(expr=m.x + m.y >= 5)
m.c2 = pyo.Constraint(expr=m.x <= 10)

status = pyo.SolverFactory('glpk').solve(m, tee=True)
pyo.assert_optimal_termination(status)
print(pyo.value(m.x), pyo.value(m.y))
```

### Abstract Model with Data

```python
m = pyo.AbstractModel()
m.I = pyo.Set()
m.a = pyo.Param(m.I)
m.x = pyo.Var(m.I)

def supply_rule(model, i):
    return model.x[i] <= model.a[i]

m.supply = pyo.Constraint(m.I, rule=supply_rule)

# Load data from a Pyomo data file, or from a Python dict
instance = m.create_instance('data.dat')
# Or: instance = m.create_instance(data={None: {'I': {None: [1, 2, 3]},
#                                               'a': {1: 10, 2: 20, 3: 30}}})
```

### Common Patterns

- **Summation** — use generator expressions, `sum(model.x[i] for i in model.I)`; `pyo.quicksum(...)` for very large sums.
- **Indexed constraints** — `pyo.Constraint(I, rule=rule_func)` creates one constraint per index.
- **Skip rules** — return `pyo.Constraint.Skip` to omit a constraint for certain indices.
- **Inequality shorthand** — `pyo.inequality(lower, expr, upper)` produces `lower <= expr <= upper`.
- **Logical expressions** — `pyo.lor(...)`, `pyo.land(...)`, `pyo.atmost(...)`, `pyo.exactly(...)`, `pyo.implies(...)` build logical expressions for `pyo.LogicalConstraint`; transforms like `core.logical_to_linear` convert them to algebraic form.
- **Fixing variables** — `m.x[1].fix(5.0)` sets the value and marks it fixed; `m.x[1].unfix()` restores.

### Solver Selection and Options

```python
opt = pyo.SolverFactory('glpk')     # LP (open source)
opt = pyo.SolverFactory('cbc')      # MIP (open source)
opt = pyo.SolverFactory('ipopt')    # NLP (open source)
opt = pyo.SolverFactory('gurobi')   # LP/MIP/MINLP (commercial)
opt = pyo.SolverFactory('cplex')    # LP/MIP/MILP (commercial)
opt = pyo.SolverFactory('gdpopt')   # logic-based GDP solver (LOA, GLOA, LBB, LD-SDA)

# Solver options go in an options dict (names are solver-specific)
opt.options['TimeLimit'] = 300
status = opt.solve(m, options={'TimeLimit': 300}, tee=True)
```

The `pyomo` command-line executable also solves models: `pyomo -l -s model.py model.dat`.

### Data Loading Options

- **`.dat` files** — AMPL data format, the classic Pyomo format
- **Other formats** — `.yaml`, `.json`, `.csv`, Excel (`.xls`/`.xlsx`), SQL/SQLite data files
- **Python dicts** — pass directly to `create_instance(data=...)`
- **CSV/Excel** — read with pandas (installed separately) or the csv module, build `initialize=` dicts

### Inspecting Models and Solutions

```python
m.pprint()                    # Print full model structure
m.x.display()                 # Display variable values
print(status.solver.status)            # ok, error, etc.
print(status.solver.termination_condition)  # optimal, infeasible, ...
print(pyo.value(m.obj))                 # Objective value

# Collect duals/slacks from solver
m.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
opt.solve(m)
print(m.dual[m.c1])           # Dual value for constraint c1
```

## Gotchas

- **`ConcreteModel` vs `AbstractModel`** — use `ConcreteModel` when all data is available in Python. Use `AbstractModel` only when loading from external data files or large data sources. Abstract models require `create_instance()` before solving.
- **`pyo.value()` is essential** — always wrap Pyomo expressions with `pyo.value()` when you need a numeric value for comparison, printing, or Python arithmetic. `m.x[1]` returns a Pyomo object; `pyo.value(m.x[1])` returns the float.
- **Rule functions must accept `model` as first arg** — for indexed components the rule signature is `rule(model, index)`; non-indexed rules use `rule(model)`.
- **DAE models are discretized with named transforms** — `pyo.TransformationFactory('dae.finite_difference').apply_to(m, nfe=20, wrt=m.t)` or `pyo.TransformationFactory('dae.collocation').apply_to(m, nfe=10, ncp=3, wrt=m.t)`. There is no `pyomo.dae.FiniteDifference` class to import; the transforms are registered under these names.
- **GDP models must be transformed before solving** — `pyo.TransformationFactory('gdp.bigm').apply_to(m)` (Big-M, M estimated for bounded variables or provided via `bigM=`/`BigM` suffix) or `pyo.TransformationFactory('gdp.hull').apply_to(m)` (convex hull), or solve logic-based with `pyo.SolverFactory('gdpopt').solve(m, algorithm='LOA')`.
- **`Constraint.Skip` vs returning `None`** — return `pyo.Constraint.Skip` to omit a constraint for an index. Returning `None` will cause an error.
- **Binary vs bounded continuous** — `within=pyo.Binary` is integer; `bounds=(0, 1)` alone leaves the variable continuous. Use `pyo.Binary` for true binary variables.
- **Time limits are solver-specific options** — `solve()` takes an `options` dict (or set `opt.options[...]`); there is no generic `timelimit=` keyword.
- **Suffix direction** — use `IMPORT` to collect solver results (duals, slacks); use `EXPORT` to send data to the solver. Some solvers do not return all suffix types.
- **Persistent solvers use `set_instance`** — `opt.set_instance(m)` loads the model once, then mutate incrementally (`add_constraint`, `remove_constraint`, `add_var`, `update_var`, `set_objective`, `add_column`) and call `opt.solve()` without re-exporting the model each iteration.
- **Only one active objective per model** — if you need multiple objectives, fix all but one or transform the problem.

## References

- [01-core-modeling](references/01-core-modeling.md) — Sets, Params, Vars, Objectives, Constraints, logical expressions, Abstract vs Concrete
- [02-lp-mip](references/02-lp-mip.md) — Linear and mixed-integer programming: diet, transport, knapsack, facility location, lot sizing, Big-M patterns
- [03-nlp-minlp](references/03-nlp-minlp.md) — Nonlinear programming: reactor design, parameter estimation, multimodal optimization
- [04-dae-optimal-control](references/04-dae-optimal-control.md) — DAE modeling, optimal control, discretization (finite difference, collocation), path constraints
- [05-gdp-disjunctive](references/05-gdp-disjunctive.md) — Generalized disjunctive programming: disjunctions, BigM/Hull transforms, GDPopt, scheduling and layout problems
- [06-mpec-complementarity](references/06-mpec-complementarity.md) — Mathematical programs with equilibrium constraints: complementarity conditions, KKT-based formulations, LCP
- [07-piecewise-sos](references/07-piecewise-sos.md) — Piecewise linear functions, SOS1/SOS2 constraints, special ordered sets
- [08-data-loading](references/08-data-loading.md) — Data loading: .dat/.yaml/.json/CSV/Excel/SQL files, dicts, parameter initialization patterns
- [09-solvers-results](references/09-solvers-results.md) — Solver interfaces, result inspection, suffixes (duals/slacks), solver options, persistent solvers, NEOS
- [10-network-flow](references/10-network-flow.md) — Network flow: max flow, min cost flow, shortest path, multi-commodity, network interdiction
- [11-advanced-patterns](references/11-advanced-patterns.md) — Benders decomposition, column generation, callbacks, transforms, kernel API, performance tips
