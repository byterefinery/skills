# Solvers and Results: Interfaces, Suffixes, Options, NEOS

## SolverFactory

Create solver instances with `SolverFactory()`.

```python
opt = pyo.SolverFactory('glpk')     # LP
opt = pyo.SolverFactory('cbc')      # MIP
opt = pyo.SolverFactory('gurobi')   # LP/MIP/MILP
opt = pyo.SolverFactory('cplex')    # LP/MIP
opt = pyo.SolverFactory('ipopt')    # NLP/MINLP
opt = pyo.SolverFactory('neos.gurobi')  # Free remote solver
```

## Solving

```python
results = opt.solve(m)
results = opt.solve(m, tee=True)         # Print solver output
results = opt.solve(m, timelimit=300)    # Time limit in seconds
results = opt.solve(m, logfile='log.txt')
```

### Common Solve Options

```python
# Solver-specific options
opt = pyo.SolverFactory('gurobi')
results = opt.solve(m, options_string='MIPGap=0.01 Threads=4')

opt = pyo.SolverFactory('ipopt')
results = opt.solve(m, options_string='max_iter 1000 tol 1e-8')

# Using solve() kwargs
results = opt.solve(m,
    timelimit=600,
    keepfiles=True,      # Keep solver input/output files
    load_solutions=False, # Don't auto-load results
)
```

## Inspecting Results

### Solver Status

```python
print(results.solver.status)              # ok, error, warning
print(results.solver.termination_condition)  # optimal, infeasible, etc.
print(results.solver.time)                 # Solve time in seconds
```

Common termination conditions: `optimal`, `infeasible`, `unbounded`, `iterationLimit`, `error`.

### Loading Solutions

```python
# Auto-loaded by default
print(pyo.value(m.x[1]))

# Manual loading
results = opt.solve(m, load_solutions=False)
m.solutions.load_from(results)
```

### Objective Value

```python
print(pyo.value(m.obj))
print(results.problem.objective)
```

## Suffixes (Duals, Slacks, etc.)

Suffixes collect additional solver information.

### Dual Values

```python
m.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
opt.solve(m)
print(m.dual[m.c1])    # Dual value for constraint c1
print(m.dual[m.supply[1]])  # Indexed constraint dual
```

### Slack Values

```python
m.slack = pyo.Suffix(direction=pyo.Suffix.IMPORT)
opt.solve(m)
print(m.slack[m.c1])    # Slack for constraint c1
```

### Reduced Costs

```python
m.rc = pyo.Suffix(direction=pyo.Suffix.IMPORT)
opt.solve(m)
print(m.rc[m.x[1]])    # Reduced cost of variable x[1]
```

### Basis Status (for warm-starting)

```python
m.urbas = pyo.Suffix(direction=pyo.Suffix.IMPORT)   # Upper bound status
m.lbbas = pyo.Suffix(direction=pyo.Suffix.IMPORT)   # Lower bound status
```

### Export Suffixes

Send data to the solver:

```python
m.mip_start = pyo.Suffix(direction=pyo.Suffix.EXPORT)
for v in m.component_objects(pyo.Var):
    for idx in v:
        m.mip_start[v[idx]] = 0.5  # Initial guess
```

## Persistent Solvers

For iterative algorithms, persistent interfaces avoid re-exporting the model.

```python
opt = pyo.SolverFactory('gurobi_persistent')
opt.load(m)

# Modify and resolve without re-export
m.new_con = pyo.Constraint(expr=m.x[1] <= 5)
opt.add_constraint(m.new_con)
results = opt.solve()

# Remove constraint
opt.remove_constraint(m.new_con)
```

### Persistent Solver Operations

```python
opt = pyo.SolverFactory('cplex_persistent')
opt.load(m)

# Add/remove variables and constraints dynamically
new_var = pyo.Var(within=pyo.Binary)
m.x_new = new_var
opt.add_variable(new_var)

# Update objective
m.obj.expr = new_expression
opt.update_objective(m.obj)

# Add cuts
cut = pyo.Constraint(expr=sum(m.x[i] for i in subset) <= limit)
opt.add_constraint(cut)
```

## NEOS Server

Free access to commercial solvers via the NEOS server.

```python
opt = pyo.SolverFactory('neos')
opt.options['solver'] = 'gurobi'     # or cplex, knitr, etc.
opt.options['email'] = 'user@example.com'
results = opt.solve(m)
```

Available NEOS solvers: gurobi, cplex, ipopt, knitro, scip, baron, antigone, and more. Check `https://www.neos-server.org`.

## Solver Selection Guide

| Problem Type | Open Source | Commercial |
|-------------|-------------|------------|
| LP | GLPK | Gurobi, CPLEX, XPRESS |
| MIP | CBC, SCIP | Gurobi, CPLEX, XPRESS |
| NLP | IPOPT | SNOPT, KNITRO |
| MINLP | IPOPT (barrier) | KNITRO, BARON |
| Global MINLP | — | BARON, ANTIGONE |
| MPEC | — | KNITRO |

## Warm-Starting

Provide initial solutions to speed up solving.

```python
# Fix variables to known good values
for v in m.component_objects(pyo.Var):
    for idx in v:
        if pyo.value(v[idx]) > 0:
            v[idx].fix(pyo.value(v[idx]))

results = opt.solve(m)

# Unfix after solve
for v in m.component_objects(pyo.Var):
    for idx in v:
        v[idx].unfix()
```

## Gotchas

- **Check termination condition** before using solution values. An `infeasible` or `error` status means values may be unreliable.
- **Suffix availability depends on solver** — not all solvers return duals, slacks, or reduced costs. Linear solvers typically return duals; MIP solvers may not.
- **Persistent solvers require compatible solver** — only Gurobi, CPLEX, MOSEK, and XPRESS have persistent interfaces.
- **NEOS has queue times** — expect 1-30 minutes wait depending on server load.
- **`tee=True` prints solver log** to stdout. Useful for debugging but can produce large output.
- **Solver options are solver-specific** — `options_string` syntax varies by solver. Check solver documentation for correct option names.
