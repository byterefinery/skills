---
name: pyomo-6-10-1
description: >
  Pyomo 6.10.1 — Python optimization modeling for LP, MIP, NLP, MINLP, DAE/optimal control,
  GDP (disjunctive programming), MPEC (equilibrium/complementarity), piecewise functions,
  network flow, stochastic programming, and more. Use this skill whenever the user mentions
  Pyomo, optimization modeling, mathematical programming, linear/nonlinear/mixed-integer
  programming, optimal control, differential equations optimization, disjunctive constraints,
  complementarity conditions, solver interfaces (Gurobi, CPLEX, IPOPT, GLPK, CBC, etc.),
  AMPL-style modeling in Python, or building optimization models with Python. Also use when
  the user asks about formulating LP/MIP/NLP models, network flow problems, facility location,
  lot sizing, transportation problems, diet/nutrition problems, parameter estimation, reactor
  design, job shop scheduling, or any mathematical optimization task in Python.
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

# pyomo 6.10.1

Pyomo is a Python-based, open-source optimization modeling language that supports LP, MIP, NLP, MINLP, DAE, GDP, and MPEC formulations. It works with many solvers (Gurobi, CPLEX, GLPK, CBC, IPOPT, etc.) via `SolverFactory`.

## Overview

Pyomo provides two modeling paradigms:

- **`ConcreteModel`** — Define model structure and data together in Python. Best for prototyping and small-to-medium models where data is available at construction time.
- **`AbstractModel`** — Define model structure first, then load data from `.dat` files or Python dicts. Best for larger models with external data sources or AMPL-style workflows.

Core components: `Set`, `Param`, `Var`, `Objective`, `Constraint`, `Block`. Indexed variants accept sets as arguments (e.g., `Var(I, J)` creates variables indexed by `(i, j)`).

## Usage

### Quick Start

```python
import pyomo.environ as pyo

# Concrete model — inline data
m = pyo.ConcreteModel()
m.x = pyo.Var(bounds=(0, None))
m.y = pyo.Var(within=pyo.Binary)
m.obj = pyo.Objective(expr=2*m.x + 3*m.y, sense=pyo.minimize)
m.c1 = pyo.Constraint(expr=m.x + m.y >= 5)
m.c2 = pyo.Constraint(expr=m.x <= 10)

# Solve
opt = pyo.SolverFactory('glpk')
results = opt.solve(m)

# Inspect
print(pyo.value(m.x), pyo.value(m.y))
```

### Abstract Model with Data

```python
m = pyo.AbstractModel()
m.I = pyo.Set()
m.J = pyo.Set()
m.a = pyo.Param(m.I)
m.b = pyo.Param(m.J)
m.x = pyo.Var(m.I, m.J, within=pyo.NonNegativeReals)

def supply_rule(model, i):
    return sum(model.x[i, j] for j in model.J) <= model.a[i]

m.supply = pyo.Constraint(m.I, rule=supply_rule)

# Load data from .dat file or dict
instance = m.create_instance('data.dat')
# Or: instance = m.create_instance(data={None: {'I': {None: [1,2]}, ...}})
```

### Common Patterns

- **Summation**: `sum(model.x[i] for i in model.I)` — use generator expressions, not `pyo.summation()` (deprecated).
- **Indexed constraints**: `pyo.Constraint(I, rule=rule_func)` creates one constraint per index.
- **Skip rules**: Return `pyo.Constraint.Skip` to skip constructing a constraint for certain indices.
- **Inequality shorthand**: `pyo.inequality(lower, expr, upper)` produces `lower <= expr <= upper`.
- **Fixing variables**: `m.x[1].fix(5.0)` sets value and marks as fixed; `m.x[1].unfix()` restores.

### Solver Selection

```python
# Common solvers by problem type:
opt = pyo.SolverFactory('glpk')    # LP (open source)
opt = pyo.SolverFactory('cbc')     # MIP (open source)
opt = pyo.SolverFactory('gurobi')  # LP/MIP/MINLP (commercial, fast)
opt = pyo.SolverFactory('cplex')   # LP/MIP/MILP (commercial)
opt = pyo.SolverFactory('ipopt')   # NLP/MINLP (open source)
opt = pyo.SolverFactory('neos.gurobi')  # Free remote solver via NEOS server

results = opt.solve(m, tee=True)   # tee=True prints solver output
```

### Data Loading Options

- **`.dat` files** — AMPL data format, load with `create_instance('file.dat')`
- **Python dicts** — Pass directly to `create_instance(data={None: {...}})`
- **CSV/Excel** — Read with pandas or csv module, construct Params from DataFrames
- **JSON** — Parse with `json` module, convert to Pyomo data structures

### Inspecting Models and Solutions

```python
m.pprint()                    # Print full model structure
m.x.display()                 # Display variable values
results.write()               # Print solver results summary
print(results.solver.status)  # ok, error, etc.
print(results.solver.termination_condition)  # optimal, infeasible, etc.

# Collect duals/slacks from solver
m.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
m.slack = pyo.Suffix(direction=pyo.Suffix.IMPORT)
opt.solve(m)
print(m.dual[m.c1])           # Dual value for constraint c1
```

## Gotchas

- **`ConcreteModel` vs `AbstractModel`**: Use `ConcreteModel` when all data is available in Python. Use `AbstractModel` only when loading from external `.dat` files or large data sources. Abstract models require `create_instance()` before solving.
- **`pyo.value()` is essential**: Always wrap Pyomo expressions with `pyo.value()` when you need a numeric value for comparison, printing, or Python arithmetic. `m.x[1]` returns a Pyomo object; `pyo.value(m.x[1])` returns the float.
- **Rule functions must accept `model` as first arg**: For indexed components, the rule signature is `rule(model, index)`. Non-indexed rules use `rule(model)`.
- **Generator expressions vs lists**: Use generator expressions (`sum(x[i] for i in I)`) not list comprehensions (`sum([x[i] for i in I])`) — generators are faster and use less memory.
- **`Constraint.Skip` vs returning `None`**: Return `pyo.Constraint.Skip` to omit a constraint for an index. Returning `None` will cause an error.
- **Variable domains**: `within=pyo.Binary` is different from `bounds=(0,1)`. Binary variables are integer; bounded continuous variables can take any value in [0,1]. Use `pyo.Binary` for true binary variables.
- **Nonlinear expressions**: Pyomo automatically detects nonlinear constraints and routes them to NLP-capable solvers. But open-source LP solvers (GLPK) cannot handle nonlinear constraints — use IPOPT or a commercial solver.
- **SOS2 constraints**: Only supported by some solvers (CPLEX, Gurobi). GLPK does not support SOS2 natively.
- **GDP transformations**: Disjunctive models must be transformed before solving. Common transforms: `BigM`, `Hull`, `GDPopt`. Not all solvers support all transforms.
- **DAE discretization**: DAE models require a discretization transform (e.g., finite differences or collocation) before solving. Use `pyomo.dae.FiniteDifference` or `pyomo.dae.Collocation`.
- **Suffix direction**: Use `IMPORT` to collect solver results (duals, slacks). Use `EXPORT` to send data to the solver. Some solvers don't support all suffix types.
- **Persistent solvers**: For iterative algorithms (Benders, column generation), use persistent solver interfaces (`gurobi_persistent`, `cplex_persistent`) to avoid re-exporting the model each iteration.

## References

- [01-core-modeling](references/01-core-modeling.md) — Sets, Params, Vars, Objectives, Constraints, Abstract vs Concrete
- [02-lp-mip](references/02-lp-mip.md) — Linear and mixed-integer programming: diet, transport, knapsack, facility location, lot sizing
- [03-nlp-minlp](references/03-nlp-minlp.md) — Nonlinear programming: reactor design, parameter estimation, multimodal optimization
- [04-dae-optimal-control](references/04-dae-optimal-control.md) — DAE modeling, optimal control, discretization (finite difference, collocation), path constraints
- [05-gdp-disjunctive](references/05-gdp-disjunctive.md) — Generalized disjunctive programming: disjunctions, transformations (BigM, Hull), job shop scheduling, facility layout
- [06-mpec-complementarity](references/06-mpec-complementarity.md) — Mathematical programs with equilibrium constraints: complementarity conditions, KKT-based formulations
- [07-piecewise-sos](references/07-piecewise-sos.md) — Piecewise linear functions, SOS1/SOS2 constraints, special ordered sets
- [08-data-loading](references/08-data-loading.md) — Data loading: .dat files, dicts, pandas/CSV/Excel, JSON, parameter initialization patterns
- [09-solvers-results](references/09-solvers-results.md) — Solver interfaces, result inspection, suffixes (duals/slacks), solver options, NEOS server
- [10-network-flow](references/10-network-flow.md) — Network flow: max flow, min cost flow, shortest path, transportation, network interdiction
- [11-advanced-patterns](references/11-advanced-patterns.md) — Benders decomposition, column generation, callbacks, transforms, kernel API, performance tips
