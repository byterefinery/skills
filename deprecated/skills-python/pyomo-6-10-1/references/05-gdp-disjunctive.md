# GDP: Generalized Disjunctive Programming

GDP models logical conditions using disjunctions (OR) instead of big-M constraints. Pyomo's `pyomo.gdp` module provides `Disjunct` and `Disjunction` components.

## Basic Disjunction

Model "A or B" where exactly one must hold.

```python
from pyomo.gdp import Disjunct, Disjunction

m = pyo.ConcreteModel()
m.x = pyo.Var(bounds=(0, None))
m.y = pyo.Var(bounds=(0, None))

# x == 0 OR y == 0
def d_rule(disjunct, flag):
    if flag:
        disjunct.c = pyo.Constraint(expr=m.x == 0)
    else:
        disjunct.c = pyo.Constraint(expr=m.y == 0)

m.d = Disjunct([0, 1], rule=d_rule)

def D_rule(model):
    return [m.d[0], m.d[1]]
m.D = Disjunction(rule=D_rule)

m.C = pyo.Constraint(expr=m.x + m.y <= 1)
m.obj = pyo.Objective(expr=2*m.x + 3*m.y, sense=pyo.maximize)
```

## Semi-Continuous Variables

"x[k] == 0 OR L[k] <= x[k] <= U[k]" — variable is either zero or within a range.

```python
from pyomo.gdp import Disjunct, Disjunction

L = [1, 2, 3]
U = [2, 4, 6]
index = [0, 1, 2]

m = pyo.ConcreteModel()
m.x = pyo.Var(index, within=pyo.Reals, bounds=(0, 20))
m.x_nonzero = pyo.Var(index, bounds=(0, 1))

def d_zero_rule(d, k):
    m = d.model()
    d.c = pyo.Constraint(expr=m.x[k] == 0)
m.d_zero = Disjunct(index, rule=d_zero_rule)

def d_range_rule(d, k):
    m = d.model()
    d.c = pyo.Constraint(expr=pyo.inequality(L[k], m.x[k], U[k]))
    d.count = pyo.Constraint(expr=m.x_nonzero[k] == 1)
m.d_range = Disjunct(index, rule=d_range_rule)

def D_rule(m, k):
    return [m.d_zero[k], m.d_range[k]]
m.D = Disjunction(index, rule=D_rule)

# Minimize number of nonzero variables
m.obj = pyo.Objective(expr=sum(m.x_nonzero[k] for k in index))
m.demand = pyo.Constraint(expr=sum(m.x[k] for k in index) >= 7)
```

## Transforms

Disjunctions must be transformed to MILP before solving. Three main transforms:

### BigM Transformation

Replaces disjunctions with big-M constraints. Simple but loose formulation.

```python
from pyomo.gdp import BigM

BigM.apply(m, compute_big_M=False)  # Use user-provided or auto-compute
# Then solve with MIP solver
```

### Hull Transformation

Tighter formulation using convex hull. Better bounds, more variables.

```python
from pyomo.gdp import Hull

Hull.apply(m)
# Solve with MIP solver
```

### GDPopt

Two-phase algorithm: restriction (continuous relaxation) → projection (MILP).

```python
from pyomo.contrib.gdpopt import GDPopt

solver = GDPopt(
    solver='gurobi',
    rule=GDPopt.LGO,          # Logical Inference Based Global Optimization
    max_iter=10,
    gap=0.01,
)
results = solver.solve(m)
```

Available rules: `LGO` (logical inference), `RIF` (restricted incidence), `HIF` (hull-based incidence).

## Job Shop Scheduling

Classic scheduling problem with disjunctive constraints for machine conflicts.

```python
from pyomo.gdp import Disjunct, Disjunction

# Operations: (job, operation) pairs
# Each operation has processing time and assigned machine
# Two operations on same machine cannot overlap

m = pyo.ConcreteModel()
m.start = pyo.Var(operations, within=pyo.NonNegativeReals)
m.end = pyo.Var(operations, within=pyo.NonNegativeReals)

# Processing time constraint
for op in operations:
    m.processing.add(m.end[op] == m.start[op] + processing_time[op])

# Disjunctive constraints for machine conflicts
for machine in machines:
    ops_on_machine = [op for op in operations if assigned_machine[op] == machine]
    for i in range(len(ops_on_machine)):
        for j in range(i+1, len(ops_on_machine)):
            oi, oj = ops_on_machine[i], ops_on_machine[j]

            def d_rule(d, first=oi, second=oj):
                if d.index == 0:
                    d.c = pyo.Constraint(expr=m.end[first] <= m.start[second])
                else:
                    d.c = pyo.Constraint(expr=m.end[second] <= m.start[first])

            d = Disjunct([0, 1], rule=d_rule)
            Disjunction(rule=lambda mdl: [d[0], d[1]])
```

## Facility Layout

Place facilities in a facility with minimum material handling cost.

```python
# Each pair of facilities cannot overlap
# Use disjunctions to enforce ordering in x and y dimensions
from pyomo.gdp import Disjunct, Disjunction

m = pyo.ConcreteModel()
m.x = pyo.Var(facilities)    # x-coordinate
m.y = pyo.Var(facilities)    # y-coordinate
m.w = pyo.Param(facilities)  # width
m.h = pyo.Param(facilities)  # height

# For each pair (i, j), at least one separation must hold:
# i left of j, OR i right of j, OR i above j, OR i below j
for i in facilities:
    for j in facilities:
        if i >= j:
            continue

        def sep_rule(d, idx):
            if idx == 1:   # i left of j
                d.c = pyo.Constraint(expr=m.x[i] + m.w[i] <= m.x[j])
            elif idx == 2: # i right of j
                d.c = pyo.Constraint(expr=m.x[j] + m.w[j] <= m.x[i])
            elif idx == 3: # i above j
                d.c = pyo.Constraint(expr=m.y[i] + m.h[i] <= m.y[j])
            else:          # i below j
                d.c = pyo.Constraint(expr=m.y[j] + m.h[j] <= m.y[i])

        d = Disjunct([1, 2, 3, 4], rule=sep_rule)
        Disjunction(rule=lambda mdl: [d[1], d[2], d[3], d[4]])
```

## Batch Processing

Scheduling batch processes with sequencing constraints.

```python
# Unit cannot process two batches simultaneously
# Use disjunctions for sequencing: batch A before B, or B before A
from pyomo.gdp import Disjunct, Disjunction

m = pyo.ConcreteModel()
m.start = pyo.Var(batches, within=pyo.NonNegativeReals)
m.duration = pyo.Param(batches)

# For each pair of batches assigned to same unit
for unit in units:
    batches_on_unit = [b for b in batches if assigned_unit[b] == unit]
    for i in range(len(batches_on_unit)):
        for j in range(i+1, len(batches_on_unit)):
            bi, bj = batches_on_unit[i], batches_on_unit[j]

            def seq_rule(d, idx):
                if idx == 0:
                    d.c = pyo.Constraint(
                        expr=m.start[bi] + m.duration[bi] <= m.start[bj])
                else:
                    d.c = pyo.Constraint(
                        expr=m.start[bj] + m.duration[bj] <= m.start[bi])

            d = Disjunct([0, 1], rule=seq_rule)
            Disjunction(rule=lambda mdl: [d[0], d[1]])
```

## Gotchas

- **Disjunctions must be transformed before solving** — raw GDP models cannot be sent to solvers. Apply `BigM`, `Hull`, or use `GDPopt`.
- **`Disjunct.rule` receives the parent model via `disjunct.model()`** — access shared variables through this method.
- **Big-M values matter** — too-large M values produce weak relaxations. Use `compute_big_M=True` for automatic computation when bounds are available.
- **Hull transformation is tighter but creates more variables** — prefer Hull when problem size allows; use BigM for larger instances.
- **GDPopt requires a MIP solver** — the projection phase solves MILP subproblems.
