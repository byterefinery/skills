# 03 — Solvers

## Installation

Install PuLP with the `[cbc]` extra to bundle the CBC solver:

```bash
pip install "pulp[cbc]==3.3.2"
```

This ensures `COIN_CMD` (CBC) is available as the default solver. Without the `[cbc]` extra, `prob.solve()` may fail if no solver is found on your system.

For better performance, also install HiGHS:

```bash
pip install highspy
```

## Default Solver

PuLP selects a default solver at import time: `COIN_CMD` (CBC) → `PULP_CBC_CMD` (deprecated) → `GLPK_CMD`. When calling `prob.solve()` without arguments, the first available solver is used.

```python
# Uses default solver
status = prob.solve()

# Check which solver is default
from pulp import LpSolverDefault
print(LpSolverDefault.name)
```

## Specifying a Solver

```python
# By solver class
prob.solve(COIN_CMD())
prob.solve(HiGHS())
prob.solve(GLPK_CMD())

# By name string
solver = getSolver("HiGHS")
prob.solve(solver)
```

## Available Solvers

### Free / Open Source

| Solver | Class | Notes |
|---|---|---|
| **CBC** (bundled) | `COIN_CMD()` | Default, included with PuLP. Supports LP and MILP. |
| **HiGHS** | `HiGHS()` or `HiGHS_CMD()` | Fast modern solver. Install via `pip install highspy`. Recommended for most use cases. |
| **GLPK** | `GLPK_CMD()` or `GLPK()` | Requires `glpsol` in PATH. LP and MILP support. |
| **CHOCO** | `CHOCO_CMD()` | Constraint programming solver. Requires Java. |

### Commercial (Require License)

| Solver | Class | Notes |
|---|---|---|
| **Gurobi** | `GUROBI()` or `GUROBI_CMD()` | Industry standard. Install `gurobipy`. |
| **CPLEX** | `CPLEX()`, `CPLEX_CMD()`, `CPLEX_PY` | IBM solver. Install `cplex`. |
| **MOSEK** | `MOSEK()` | Specialized for conic optimization. |
| **XPRESS** | `XPRESS()`, `XPRESS_CMD()`, `XPRESS_PY` | FICO Xpress. |
| **SCIP** | `SCIP()`, `SCIP_CMD()`, `SCIP_PY` | Academic/free for research, commercial otherwise. |
| **COPT** | `COPT()`, `COPT_DLL()`, `COPT_CMD()` | Gurobi alternative by Shanghai Shangle. |
| **SAS** | `SAS94()`, `SASCAS()` | SAS optimization. |
| **MIPCL** | `MIPCL_CMD()` | MIPCL solver. |
| **CUOPT** | `CUOPT()` | NVIDIA GPU-accelerated solver. |

## Solver Parameters

Most solvers accept common parameters:

```python
# Suppress solver output
solver = COIN_CMD(msg=False)
prob.solve(solver)

# Set time limit (seconds)
solver = COIN_CMD(msg=False, timeLimit=300)
prob.solve(solver)

# HiGHS with options
solver = HiGHS(msg=False, timeLimit=60)
prob.solve(solver)

# Gurobi with parameters
solver = GUROBI(msg=False, timeLimit=120, threads=4)
prob.solve(solver)
```

### Common Parameters

| Parameter | Description |
|---|---|
| `msg` | Boolean. If `True`, solver prints output. Default: `True`. |
| `timeLimit` | Maximum solve time in seconds. |
| `threads` | Number of parallel threads (solver-dependent). |
| `gap` | MIP gap tolerance (e.g., 0.01 for 1%). |

## Checking Solver Availability

```python
# Check if a specific solver is available
print(COIN_CMD().available())
print(HiGHS().available())
print(GUROBI().available())

# List all available solvers
from pulp import listSolvers
print(listSolvers(onlyAvailable=True))   # Only installed
print(listSolvers())                      # All known solvers
```

## Solver Selection Strategy

1. **Small problems (< 1000 vars/constraints)**: Default CBC (bundled with `pulp[cbc]`) is fine
2. **Medium problems**: Install HiGHS (`pip install highspy`) — faster than CBC
3. **Large MILP problems**: Use Gurobi or CPLEX if licensed
4. **Pure LP problems**: HiGHS or GLPK are excellent
5. **Constraint satisfaction (no objective)**: CHOCO

## Installing Recommended Solvers

```bash
# PuLP with bundled CBC solver (default, always use this)
pip install "pulp[cbc]==3.3.2"

# HiGHS (recommended for better performance over CBC)
pip install highspy

# Gurobi (commercial, free academic license available)
pip install gurobipy

# CPLEX (commercial)
pip install cplex

# GLPK (if not in PATH)
# Ubuntu: sudo apt install glpk-utils
# macOS: brew install glpk
```

## Solver-Specific Gotchas

- **CBC** may be slow on large MILP problems. Use `timeLimit` to prevent indefinite solving.
- **HiGHS** requires `highspy` package. The C extension must load before PuLP's Rust extension — PuLP handles this automatically at import.
- **Dual values (`pi`) are solver-dependent**. CBC returns duals for LP; MILP duals may be unavailable or approximate.
- **Gurobi** and **CPLEX** have their own parameter systems. Pass parameters as keyword arguments to the solver constructor.
- **`PULP_CBC_CMD` is deprecated** in 3.3.2. Use `COIN_CMD()` instead.

## Warm Starting

Some solvers support warm starts via initial variable values:

```python
# Set initial values before solving
for v in prob.variables():
    v.setInitialValue(estimate[v.name])

prob.solve()
```

This can speed up resolve scenarios where the solution is expected to be similar.

## Exporting Solver Configuration

```python
from pulp import getSolverFromDict, getSolverFromJson

# From dict
config = {"solver": "HiGHS", "msg": False, "timeLimit": 60}
solver = getSolverFromDict(config)

# From JSON file
solver = getSolverFromJson("solver_config.json")
```
