# Advanced Patterns: Benders, Column Generation, Callbacks, Transforms, Kernel API

## Benders Decomposition

Decompose a large (two-stage) problem into a master problem and subproblems. The classic AMPL-book Benders example in `examples/pyomo/benders` models this as an AbstractModel with scenarios: first-stage variables (`Make1`, `Inv1`, `Sell1`) plus an epigraph variable (`Min_Stage2_Profit`) that bounds the second-stage cost.

### Master Problem Pattern

```python
m_master = pyo.ConcreteModel()
m_master.y = pyo.Var(W, within=pyo.Binary)      # first-stage (here: binary) variables
m_master.z = pyo.Var(within=pyo.Reals)          # epigraph variable for stage-2 cost

m_master.obj = pyo.Objective(
    expr=sum(fixed_cost[w]*m_master.y[w] for w in W) + m_master.z)

# Benders cuts are accumulated here
m_master.cuts = pyo.ConstraintList()
```

### Subproblem (Dual)

For a fixed first-stage solution, the second-stage LP's dual gives a Benders cut.

```python
def solve_subproblem(y_values):
    m_sub = pyo.ConcreteModel()
    # Dual variables of the second-stage constraints
    m_sub.pi = pyo.Var(master_constraints)
    m_sub.mu = pyo.Var(nonneg_constraints, within=pyo.NonNegativeReals)

    # Dual objective (maximize) yields the cut value
    m_sub.obj = pyo.Objective(
        expr=sum(b[j]*m_sub.pi[j] for j in J)
             - sum(y_values[w]*a[w,j]*m_sub.mu[w,j] for w in W for j in J),
        sense=pyo.maximize)

    def dual_con_rule(m, j):
        return sum(a[w,j]*m_sub.mu[w,j] for w in W) - m_sub.pi[j] <= 0
    m_sub.dual_con = pyo.Constraint(J, rule=dual_con_rule)

    status = opt.solve(m_sub)
    if status.solver.termination_condition == TerminationCondition.infeasible:
        return 'infeasible', None          # -> feasibility cut
    dual_obj = pyo.value(m_sub.obj)
    coeffs = {w: sum(a[w,j]*pyo.value(m_sub.mu[w,j]) for j in J) for w in W}
    return 'optimal', (dual_obj, coeffs)   # -> optimality cut
```

### Iteration Loop

```python
opt_master = pyo.SolverFactory('glpk')
opt_master.set_instance(m_master)

for iteration in range(max_iter):
    status = opt_master.solve()
    y_vals = {w: pyo.value(m_master.y[w]) for w in W}

    status_, cut = solve_subproblem(y_vals)
    if cut[0] == 'infeasible':
        new_cut = m_master.cuts.add(m_master.z >= feasibility_rhs(y_vals))
    else:
        dual_obj, coeffs = cut
        rhs = dual_obj - sum(coeffs[w]*y_vals[w] for w in W)
        new_cut = m_master.cuts.add(
            m_master.z >= sum(coeffs[w]*m_master.y[w] for w in W) + rhs)
    opt_master.add_constraint(new_cut)   # add() returns the new constraint
    if converged(m_master, dual_obj):
        break
```

Use a persistent solver for the master so cuts are added incrementally without re-exporting the model.

## Column Generation (Dantzig-Wolfe)

Decompose by variables. The cutting-stock example in `examples/pyomo/columngeneration` shows the full pattern: columns are pattern variables in a `VarList`, the pricing subproblem is a knapsack, and new columns are added with `add_column`.

```python
cs = pyo.ConcreteModel()
cs.pattern = pyo.VarList(within=pyo.NonNegativeReals)   # one column per pattern

# Add initial (heuristic) columns, one per demanded item
for i, width in enumerate(demand):
    cs.pattern.add()

# Demand constraints, initially covered by the identity columns
cs.demand = pyo.Constraint(demand.keys())
for i, (width, quantity) in enumerate(demand.items()):
    cs.demand[width] = initial_count[width] * cs.pattern[i+1] >= quantity

cs.obj = pyo.Objective(expr=pyo.quicksum(cs.pattern.values()), sense=pyo.minimize)

# Import dual values of the demand constraints for pricing
cs.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)

# Pricing subproblem (knapsack)
ks = pyo.ConcreteModel()
ks.widths = pyo.Var(demand.keys(), within=pyo.NonNegativeIntegers)
ks.knapsack = pyo.Constraint(
    expr=pyo.quicksum(width*ks.widths[width] for width in demand) <= W)
ks.obj = pyo.Objective(expr=0, sense=pyo.maximize)

# Persistent solvers for both master and pricing (any *_persistent interface)
cs_s = pyo.SolverFactory(solver_name)   # e.g. 'gurobi_persistent'
ks_s = pyo.SolverFactory(solver_name)
cs_s.set_instance(cs)
ks_s.set_instance(ks)

for _ in range(max_iters):
    cs_s.solve()
    duals = {width: cs.dual[cs.demand[width]] for width in demand}

    # Reduced cost of a pattern = 1 - sum(dual * usage); price it via knapsack
    ks.obj.expr = sum(duals[width]*ks.widths[width] for width in demand)
    ks_s.set_objective(ks.obj)
    ks_s.solve()

    if pyo.value(ks.obj) <= 1:     # no column with positive reduced cost
        break

    new_var = cs.pattern.add()
    constraints, coeffs = [], []
    for width, var in ks.widths.items():
        n = int(round(pyo.value(var)))
        if n == 0:
            continue
        constraints.append(cs.demand[width])
        coeffs.append(n)
    cs_s.add_column(cs, new_var, 1.0, constraints, coeffs)
```

## Callbacks

Pyomo's script framework supports callbacks (`solve-callback`, `cut-callback`, `node-callback`, ...) registered with `pyomo_callback` from `pyomo.scripting.interface`. Callbacks are used when running through the `pyomo` executable (or a Pyomo script): the model file defines the callbacks, and the solver interface (e.g., `_cplex_direct`) invokes them during the solve.

```python
# In the model file, e.g. sc_callback.py
from pyomo.scripting.interface import pyomo_callback

@pyomo_callback('solve-callback')
def solve_callback(solver, model):
    print("CB-Solve")

@pyomo_callback('cut-callback')
def cut_callback(solver, model):
    # add lazy constraints / user cuts during branch-and-bound
    ...

@pyomo_callback('node-callback')
def node_callback(solver, model):
    # called at each node of the search tree
    ...
```

```bash
pyomo --solver=_cplex_direct sc_callback.py
```

The `examples/pyomo/callbacks` directory contains a working set-cover implementation (`sc.py`, `sc_script.py`, `sc_callback.py`, `tsp.py`). Callback support depends on the solver interface; direct interfaces (e.g., `_cplex_direct`) are the typical vehicle.

## Transforms

Registered transforms modify model structure before solving (use `apply_to` in place or `create_using` for a copy):

```python
# DAE discretization
pyo.TransformationFactory('dae.finite_difference').apply_to(m, nfe=20, wrt=m.t)
pyo.TransformationFactory('dae.collocation').apply_to(m, nfe=10, ncp=3, wrt=m.t)

# GDP reformulations
pyo.TransformationFactory('gdp.bigm').apply_to(m)      # Big-M
pyo.TransformationFactory('gdp.hull').apply_to(m)      # convex hull

# Logical -> algebraic
pyo.TransformationFactory('core.logical_to_linear').apply_to(m)
pyo.TransformationFactory('contrib.logical_to_disjunctive').apply_to(m)

# GDP basic-step preprocessing (bound improvement)
from pyomo.gdp.basic_step import apply_basic_step
apply_basic_step([m.disjunctions[i] for i in m.disjunction_set])
```

## Kernel API

`pyomo.kernel` (or `pyomo.core.kernel`) is the low-level homogeneous modeling interface: flat containers instead of named model components.

```python
import pyomo.kernel as pmo

v = pmo.variable(value=2, bounds=(0, 10))
e = pmo.expression(expr=v**2 + 1)        # immutable expression
print(pmo.value(e))

# Mutable data expression: updating it updates all expressions that use it
de = pmo.data_expression()
c = pmo.constraint(expr=v + de)
c.lb = 0
de.expr = -1     # c's body changes accordingly

o = pmo.objective(expr=v)

block = pmo.block()
block.x = pmo.variable()
block.con = pmo.constraint(expr=block.x >= 1)
block.obj = pmo.objective(expr=block.x)
```

Also available: `parameter`, `suffix`, `conic`, `sos`/`sos1`/`sos2`, `piecewise` (and `piecewise_nd`), plus `_tuple`/`_list`/`_dict` container variants of each.

## Performance Tips

The `examples/pyomobook/performance-ch` directory contains benchmarks (`lin_expr.py`, `persistent.py`, `SparseSets.py`) comparing construction approaches.

### Expression Building

- **Use generator expressions** for summation: `sum(x[i] for i in I)` not `sum([x[i] for i in I])`
- **Use `pyo.quicksum()`** for very large sums
- **Avoid building expressions in nested Python loops** when data allows precomputation

### Model Construction

- **Use `initialize=` on Sets/Params** instead of setting values after construction
- **Use `VarList` for dynamically growing collections** of variables (column generation)
- **Keep rules fast** — precompute index lists and coefficient dicts outside rules

### Solving

- **Set time limits via solver options** (names are solver-specific)
- **Use persistent solvers** for iterative algorithms (Benders, column generation)
- **Warm-start** (`solve(m, warmstart=True)`) when re-solving perturbed models
- **Decompose** very large instances with Benders or Dantzig-Wolfe

## Gotchas

- **Benders convergence depends on cut quality** — poor cuts lead to slow convergence; feasibility cuts for infeasible subproblems are mandatory.
- **Column generation needs good initial columns** — start with heuristic patterns before pricing.
- **Callbacks require solver-specific support** — not all solver interfaces invoke callbacks; direct interfaces are the common case.
- **Transforms modify the model** — `apply_to` changes the model in place (original structure is transformed away); use `create_using` when you need the base model intact.
- **Kernel API is lower-level** — use `pyomo.environ` for standard modeling; kernel is for performance-critical or advanced customization.
- **`add_column` needs the constraint objects** — pass the actual `Constraint` data objects (e.g., `cs.demand[width]`) and matching coefficient values.
