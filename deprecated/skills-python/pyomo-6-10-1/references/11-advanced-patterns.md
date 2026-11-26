# Advanced Patterns: Benders, Column Generation, Callbacks, Transforms, Kernel API

## Benders Decomposition

Decompose large MIP into master problem and subproblems.

### Master Problem

```python
m_master = pyo.ConcreteModel()
m_master.y = pyo.Var(W, within=pyo.Binary)     # First-stage variables
m_master.z = pyo.Var(within=pyo.Reals)          # Epigraph variable

# Master objective
m_master.obj = pyo.Objective(
    expr=sum(fixed_cost[w]*m_master.y[w] for w in W) + m_master.z
)

# Stored cuts will be added here
m_master.cuts = pyo.ConstraintList()
```

### Subproblem (Dual)

```python
def solve_subproblem(y_values):
    m_sub = pyo.ConcreteModel()
    # Dual of the second-stage problem
    m_sub.pi = pyo.Var(master_constraints, within=pyo.Reals)
    m_sub.mu = pyo.Var(nonneg_constraints, within=pyo.NonNegativeReals)

    # Dual objective gives Benders cut
    def obj_rule(m):
        return sum(b[j]*m.pi[j] for j in demands) - \
               sum(y_values[w]*sum(a[w,j]*m.mu[w,j] for j in demands) for w in W)
    m_sub.obj = pyo.Objective(rule=obj_rule, sense=pyo.maximize)

    # Dual constraints
    def dual_con_rule(m, j):
        return sum(a[w,j]*m.mu[w,j] for w in W) - m.pi[j] <= 0
    m_sub.dual_con = pyo.Constraint(demands, rule=dual_con_rule)

    opt.solve(m_sub)
    dual_obj = pyo.value(m_sub.obj)

    if dual_obj > 1e6:
        return 'infeasible', None   # Feasibility cut
    else:
        # Optimality cut: z >= dual_obj
        cut_coeffs = {w: sum(a[w,j]*pyo.value(m_sub.mu[w,j]) for j in demands)
                      for w in W}
        return 'optimal', (dual_obj, cut_coeffs)
```

### Iteration Loop

```python
for iteration in range(max_iter):
    opt_master.solve(m_master)
    y_vals = {w: pyo.value(m_master.y[w]) for w in W}

    status, cut_data = solve_subproblem(y_vals)
    if status == 'infeasible':
        # Add feasibility cut
        m_master.cuts.add(m_master.z >= -M * (1 - sum(y[w] for w in infeasible_set)))
    else:
        dual_obj, coeffs = cut_data
        # Add optimality cut
        rhs = dual_obj - sum(coeffs[w]*y_vals[w] for w in W)
        m_master.cuts.add(
            m_master.z >= sum(coeffs[w]*m_master.y[w] for w in W) + rhs
        )

    gap = abs(pyo.value(m_master.z) - dual_obj) / max(abs(dual_obj), 1)
    if gap < tolerance:
        break
```

## Column Generation (Dantzig-Wolfe)

Decompose by variables instead of constraints. Useful for cutting stock, vehicle routing.

### Restricted Master Problem (RMP)

```python
m_rmp = pyo.ConcreteModel()
# Start with initial columns (patterns)
initial_patterns = generate_initial_patterns()
m_rmp.patterns = pyo.Set(initialize=range(len(initial_patterns)))
m_rmp.x = pyo.Var(m_rmp.patterns, within=pyo.NonNegativeReals)
m_rmp.cost = pyo.Param(m_rmp.patterns, initialize={i: cost(p) for i, p in enumerate(initial_patterns)})

def obj_rule(m):
    return sum(m.cost[p]*m.x[p] for p in m.patterns)
m_rmp.obj = pyo.Objective(rule=obj_rule)

# Covering constraints
def cover_rule(m, i):
    return sum(usage[p][i]*m.x[p] for p in m.patterns) >= demand[i]
m_rmp.cover = pyo.Constraint(items, rule=cover_rule)
```

### Pricing Subproblem

```python
def solve_pricing(dual_values):
    """Find column with negative reduced cost."""
    m_price = pyo.ConcreteModel()
    m_price.y = pyo.Var(items, within=pyo.Binary)

    def pricing_obj(m):
        return 1 - sum(dual_values[i]*m.y[i] for i in items)
    m_price.obj = pyo.Objective(rule=pricing_obj)

    # Pattern feasibility constraints
    m_price.feas = pyo.Constraint(expr=sum(m_price.y[i] for i in items) <= capacity)

    opt.solve(m_price)
    reduced_cost = pyo.value(m_price.obj)

    if reduced_cost < -1e-6:
        new_pattern = {i: int(pyo.value(m_price.y[i])) for i in items}
        return reduced_cost, new_pattern
    else:
        return 0, None
```

### Column Generation Loop

```python
for iteration in range(max_iter):
    opt.solve(m_rmp)
    # Extract dual values
    duals = {i: m_rmp.dual[m_rmp.cover[i]] for i in items}

    rc, new_pattern = solve_pricing(duals)
    if new_pattern is None:
        break  # Optimal

    # Add new column
    new_idx = len(initial_patterns)
    m_rmp.patterns.add(new_idx)
    m_rmp.cost[new_idx] = pattern_cost(new_pattern)
    m_rmp.x.add(new_idx)
    initial_patterns.append(new_pattern)
```

## Callbacks

Inject custom logic during solver execution.

```python
from sc import pyomo_callback

@pyomo_callback('solve-callback')
def solve_callback(solver, model):
    print("CB-Solve")

@pyomo_callback('cut-callback')
def cut_callback(solver, model):
    # Add lazy constraints during branch-and-bound
    pass

@pyomo_callback('node-callback')
def node_callback(solver, model):
    # Called at each node of the search tree
    pass
```

### Persistent Solver with Callbacks

```python
opt = pyo.SolverFactory('gurobi_persistent')
# Gurobi supports callbacks via the Gurobi Python API directly
# Pyomo callback decorators work with script-based solving
```

## Transforms

Pyomo transforms modify model structure before solving.

### Discretization (DAE)

```python
from pyomo.dae import FiniteDifference, Collocation

FiniteDifference.apply(m, nfe=20, wrt=m.t, scheme='BACKWARD')
# Or:
Collocation.apply(m, nfe=10, ncp=3, wrt=m.t)
```

### GDP Transforms

```python
from pyomo.gdp import BigM, Hull

BigM.apply(m, compute_big_M=True)
# Or:
Hull.apply(m)
```

### Index Pushdown

Flatten multi-indexed components for solver compatibility.

```python
from pyomo.core.transform import index_pushdown
index_pushdown.TransformationFactory('core.index_pushdown').apply_to(m)
```

### Symbolic Representation

Generate human-readable algebraic representation.

```python
from pyomo.repn import generate_symbolic_repn
repn = generate_symbolic_repn(m.obj, compute_values=True)
print(repn)
```

## Kernel API

Low-level modeling interface for advanced use cases.

```python
import pyomo.kernel as pmo

# Variables
v = pmo.variable(value=2, bounds=(0, 10))

# Expressions
e = pmo.expression(expr=v**2 + 1)
print(pmo.value(e))  # 5

# Sub-expressions (mutable)
esub = pmo.expression(expr=v + 1)
e2 = pmo.expression(expr=esub + 1)
esub.expr = v - 1    # Changing esub updates e2

# Constraints
c = pmo.constraint()
c.body = e + 1
c.lb = 0

# Data expressions (for bounds)
de = pmo.data_expression()
c.lb = de + 1
de.expr = -1
```

### Kernel Blocks

```python
block = pmo.block()
block.x = pmo.variable()
block.y = pmo.variable()
block.con = pmo.constraint(expr=block.x + block.y >= 1)
block.obj = pmo.objective(expr=block.x + 2*block.y)
```

## Performance Tips

### Expression Building

- **Use generator expressions** for summation: `sum(x[i] for i in I)` not `sum([x[i] for i in I])`
- **Avoid nested Python loops** in constraint rules — precompute data structures
- **Use `pyo.quicksum()`** for very large sums (slightly faster than `sum()`)

### Model Construction

- **Pre-allocate Sets and Params** before building constraints
- **Use `initialize=` on Params** instead of setting values after construction
- **Batch constraint creation** with `ConstraintList` for dynamic constraints

### Solver Configuration

- **Set reasonable time limits**: `timelimit=300`
- **Use MIP starts** for warm-starting: fix variables to known good values
- **Tighten tolerances** only when needed: default tolerances are usually sufficient
- **Use persistent solvers** for iterative algorithms (Benders, column generation)

### Large Models

- **Decompose** using Benders or Dantzig-Wolfe for very large instances
- **Use abstract models with .dat files** for data-heavy problems
- **Profile model construction** time — Python overhead can dominate for models with millions of constraints

## Gotchas

- **Benders convergence depends on cut quality** — poor cuts lead to slow convergence. Use Pareto-optimal cuts when possible.
- **Column generation needs good initial columns** — start with heuristic patterns before pricing.
- **Callbacks require solver-specific support** — not all solvers support lazy constraints or user cuts.
- **Transforms modify the model in place** — the original structure is lost after transformation.
- **Kernel API is lower-level** — use `pyomo.environ` for standard modeling; kernel is for advanced customization.
- **Symbolic representation helps debug** — use `generate_symbolic_repn()` to see what the solver actually receives.
