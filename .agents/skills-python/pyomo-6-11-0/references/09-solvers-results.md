# Solvers and Results: Interfaces, Suffixes, Options, Persistent Solvers

## SolverFactory

Create solver instances with `pyo.SolverFactory(name)`. Common registered names:

```python
opt = pyo.SolverFactory('glpk')     # LP (open source)
opt = pyo.SolverFactory('cbc')      # MIP (open source)
opt = pyo.SolverFactory('scip')     # MIP/NLP (open source)
opt = pyo.SolverFactory('ipopt')    # NLP (open source)
opt = pyo.SolverFactory('gurobi')   # LP/MIP/MINLP (commercial)
opt = pyo.SolverFactory('cplex')    # LP/MIP/MILP (commercial)
opt = pyo.SolverFactory('baron')    # global MINLP
opt = pyo.SolverFactory('gams')     # GAMS bridge (select solver via options)
opt = pyo.SolverFactory('gdpopt')   # logic-based GDP solver
```

Direct/persistent variants also exist (`gurobi_direct`, `gurobi_persistent`, `cplex_persistent`, `mosek_persistent`, `xpress_persistent`, ...). Check availability before solving: `opt.available()`.

## Solving

```python
status = opt.solve(m)
status = opt.solve(m, tee=True)          # print solver log
```

### Solve Keyword Arguments

The `solve()` call accepts these keyword arguments:

- **`options`** (dict) — solver-specific options
- **`suffixes`** (list of str) — suffix names to import, e.g. `['dual', 'slack', 'rc']`
- **`warmstart`** (bool) — warm-start the solver with current variable values
- **`keepfiles`** (bool) — keep the solver input/log files
- **`logfile`** (str) — name for the solver log file
- **`load_solutions`** (bool) — load solutions into the model after solving
- **`report_timing`** (bool) — print timing information
- **`tee`** (bool) — print solver log output

### Options

Option names are solver-specific; set them on the solver object or pass via `solve()`:

```python
# Options on the solver object
opt.options['TimeLimit'] = 300

# Or through solve()
status = opt.solve(m, options={'TimeLimit': 300}, tee=True)

# GAMS bridge: select the underlying solver via options
gams = pyo.SolverFactory('gams')
gams.options['solver'] = 'baron'
```

## Inspecting Results

```python
status = opt.solve(m)

print(status.solver.status)                # ok, error, warning
print(status.solver.termination_condition) # optimal, infeasible, infeasibleOrUnbounded, maxTimeLimit, ...
print(status.solver.time)                  # solve time

# Assert optimal termination (raises otherwise)
pyo.assert_optimal_termination(status)

# Objective value
print(pyo.value(m.obj))
```

### Loading Solutions

Solutions are auto-loaded by default (`load_solutions=True`). To control this:

```python
results = opt.solve(m, load_solutions=False)
m.solutions.load_from(results)   # load manually later
```

## Suffixes (Duals, Slacks, etc.)

Suffixes collect additional solver information.

### Dual Values

```python
m.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
opt.solve(m)
print(m.dual[m.c1])              # Dual value for constraint c1
print(m.dual[m.supply[1]])       # Indexed constraint dual
```

### Slack and Reduced Costs

```python
m.slack = pyo.Suffix(direction=pyo.Suffix.IMPORT)
m.rc = pyo.Suffix(direction=pyo.Suffix.IMPORT)
opt.solve(m)
print(m.slack[m.c1])             # Slack for constraint c1
print(m.rc[m.x[1]])              # Reduced cost of variable x[1]
```

Alternatively request suffixes per solve via the `suffixes=` keyword: `opt.solve(m, suffixes=['dual', 'slack', 'rc'])`.

### Export Suffixes

Send data to the solver (e.g., warm-start values):

```python
m.mip_start = pyo.Suffix(direction=pyo.Suffix.EXPORT)
for v in m.x.values():
    m.mip_start[v] = 0.5
```

## Persistent Solvers

Persistent interfaces load the model once and support incremental mutation — ideal for Benders, column generation, and other iterative algorithms.

```python
opt = pyo.SolverFactory('gurobi_persistent')
opt.set_instance(m)      # load the model once
status = opt.solve()     # solve (same instance is remembered)
```

Incremental operations (methods on the persistent solver):

- `add_block(block)` / `remove_block(block)`
- `add_constraint(con)` / `remove_constraint(con)`
- `add_var(var)` / `remove_var(var)` / `update_var(var)`
- `set_objective(obj)`
- `add_sos_constraint(con)` / `remove_sos_constraint(con)`
- `add_column(model, var, obj_coef, constraints, coefficients)` — add a new variable with its objective coefficient and constraint coefficients at once (column generation)
- `has_instance()` — whether a model is currently loaded

```python
# Benders-style: add a cut each iteration without re-exporting
m_master.cuts = pyo.ConstraintList()
opt = pyo.SolverFactory('gurobi_persistent')
opt.set_instance(m_master)

for iteration in range(max_iter):
    status = opt.solve()
    y_vals = {w: pyo.value(m_master.y[w]) for w in W}
    cut = build_cut(y_vals)
    m_master.cuts.add(cut)          # model mutation
    opt.add_constraint(m_master.cuts.last())  # sync to solver
```

The `gurobi_persistent`, `cplex_persistent`, `mosek_persistent`, and `xpress_persistent` interfaces are available for solvers with persistent Python APIs.

## NEOS Server

Free remote access to commercial solvers via the NEOS server through the `_neos` interface and the `pyomo.neos.kestrel` client. The email address used for the NEOS account is read from the `NEOS_EMAIL` environment variable; `kestrel.solvers()` lists the remote solvers currently available.

```python
opt = pyo.SolverFactory('_neos')
# configure remote solver options on opt.options, then solve
status = opt.solve(m)
```

Expect queue times on the remote server; NEOS is best for occasional runs, not tight loops.

## Solver Selection Guide

| Problem Type | Open Source | Commercial |
|-------------|-------------|------------|
| LP | GLPK, CBC, HiGHS | Gurobi, CPLEX, XPRESS |
| MIP | CBC, SCIP | Gurobi, CPLEX, XPRESS |
| NLP | IPOPT | SNOPT, KNITRO |
| MINLP | SCIP | KNITRO, BARON |
| Global MINLP | — | BARON, ANTIGONE (via NEOS) |
| GDP | GDPopt (LOA/LBB) + MIP/NLP solver | via BARON after Big-M/Hull |
| MPEC | — | KNITRO |

## Warm-Starting

Provide initial solutions to speed up solving:

```python
# Set values, then solve with warmstart
for v in m.x.values():
    v.set_value(0.5)
status = opt.solve(m, warmstart=True)
```

## Gotchas

- **Check termination condition** before using solution values. An `infeasible` or error status means values may be unreliable. `pyo.assert_optimal_termination(status)` makes this explicit.
- **Suffix availability depends on solver** — not all solvers return duals, slacks, or reduced costs. Linear NLP/LP solvers typically return duals; MIP solvers often do not.
- **Persistent solvers require compatible solvers** — only interfaces with persistent Python APIs (`*_persistent` names) work this way.
- **NEOS has queue times** — expect waits depending on server load; set `NEOS_EMAIL` for the account.
- **`tee=True` prints solver log** to stdout. Useful for debugging but can produce large output.
- **Solver options are solver-specific** — option names vary by solver (e.g., `TimeLimit` vs `max_cpu_time`); check the solver's documentation.
