# GDP: Generalized Disjunctive Programming

GDP models logical conditions using disjunctions (OR) instead of big-M constraints. The `pyomo.gdp` module provides `Disjunct` and `Disjunction` components.

## Basic Disjunction

Model "A or B" where exactly one disjunct must hold. Disjuncts are Block-like components; add constraints to them directly or via rules.

```python
from pyomo.gdp import Disjunct, Disjunction

model = pyo.ConcreteModel(name='LOA example')
model.x = pyo.Var(bounds=(-1.2, 2))
model.y = pyo.Var(bounds=(-10, 10))
model.c = pyo.Constraint(expr=model.x + model.y == 1)

model.fix_x = Disjunct()
model.fix_x.c = pyo.Constraint(expr=model.x == 0)

model.fix_y = Disjunct()
model.fix_y.c = pyo.Constraint(expr=model.y == 0)

# Exactly one of the disjuncts is active
model.d = Disjunction(expr=[model.fix_x, model.fix_y])

model.objective = pyo.Objective(expr=model.x + 0.1*model.y, sense=pyo.minimize)
```

### Indexed and Multi-indexed Disjuncts

```python
# Indexed disjuncts: one per index
model.disjuncts = Disjunct([1, 2, 3])
model.disjuncts[1].c = pyo.Constraint(expr=model.x <= 1)

# Multi-indexed disjuncts (e.g., scenarios x alternatives)
model.disjuncts = Disjunct([1, 2, 3], [1, 2])
model.disjuncts[1, 1].c = pyo.Constraint(expr=model.x1**2 + 0.25*(model.x2 - 5)**2 <= 1)

# Disjunctions can be declared with a decorator
@model.Disjunction(model.disjunction_set, xor=True)
def disjunctions(model, i):
    return [model.disjuncts[i, 1], model.disjuncts[i, 2]]
```

## Semi-Continuous Variables

"x[k] == 0 OR L[k] <= x[k] <= U[k]" — variable is either zero or within a range.

```python
L = [1, 2, 3]
U = [2, 4, 6]
index = [0, 1, 2]

m = pyo.ConcreteModel()
m.x = pyo.Var(index, within=pyo.Reals, bounds=(0, 20))
m.x_nonzero = pyo.Var(index, bounds=(0, 1))

m.d_zero = Disjunct(index)
m.d_range = Disjunct(index)
for k in index:
    m.d_zero[k].c = pyo.Constraint(expr=m.x[k] == 0)
    m.d_range[k].c = pyo.Constraint(expr=pyo.inequality(L[k], m.x[k], U[k]))
    m.d_range[k].count = pyo.Constraint(expr=m.x_nonzero[k] == 1)

m.D = Disjunction(index)
for k in index:
    m.D[k] = [m.d_zero[k], m.d_range[k]]

# Minimize number of nonzero variables
m.obj = pyo.Objective(expr=sum(m.x_nonzero[k] for k in index))
m.demand = pyo.Constraint(expr=sum(m.x[k] for k in index) >= 7)
```

## Reformulations (MI(N)LP)

Disjunctions must be transformed to a standard model before sending to most solvers. The two classical strategies are registered transforms:

### Big-M Reformulation

```python
# apply_to() transforms in place; create_using() returns a new model
m_bigm = pyo.TransformationFactory('gdp.bigm').create_using(m_base)
# or: pyo.TransformationFactory('gdp.bigm').apply_to(m_base)
# or with an explicit M:
# m_bigm = pyo.TransformationFactory('gdp.bigm').create_using(m_base, bigM=100)
```

By default the Big-M transformation estimates reasonably tight M values when variables are bounded. Otherwise provide M values through the `bigM=` argument or a `BigM` suffix; a `GDP_Error` is raised for missing M values. The resulting model is smaller (no extra variables) but has a looser continuous relaxation.

### Hull (Convex Hull) Reformulation

```python
m_hull = pyo.TransformationFactory('gdp.hull').create_using(m_base)
# or: pyo.TransformationFactory('gdp.hull').apply_to(m_base)
```

Tighter formulation using the convex hull: better bounds at the cost of more variables. Prefer Hull when problem size allows; use Big-M for larger instances.

## GDPopt (Logic-Based Solvers)

GDPopt solves nonlinear GDP models directly with logic-based decomposition — no reformulation to a single MIP needed. Most effective for nonlinear GDP models.

```python
# Generic solver with an algorithm argument
results = pyo.SolverFactory('gdpopt').solve(model, algorithm='LOA', mip_solver='glpk')

# Or an algorithm-specific solver
results = pyo.SolverFactory('gdpopt.loa').solve(model, mip_solver='glpk', tee=True)
```

Available algorithms: **LOA** (logic-based outer approximation), **GLOA** (global LOA), **LBB** (logic-based branch-and-bound), **LD-SDA** (logic-based discrete steepest descent). `mip_solver` selects the MIP solver used for the subproblems; `tee=True` prints verbose output. For nonconvex problems, LOA may not report rigorous lower/upper bounds — use LBB or GLOA for rigor.

## Scheduling and Layout Problems

### Job Shop Scheduling

Operations on the same machine cannot overlap — model each pair with a 2-way disjunction (operation A before B, or B before A).

```python
# For each pair of operations (a, b) on the same machine:
d = Disjunct([0, 1])
d[0].c = pyo.Constraint(expr=m.end[a] <= m.start[b])
d[1].c = pyo.Constraint(expr=m.end[b] <= m.start[a])
m.machine_conflict = Disjunction(expr=[d[0], d[1]])

# Plus per-operation processing-time constraints:
# m.end[op] == m.start[op] + processing_time[op]
```

### Facility Layout

Facilities cannot overlap — for each pair, at least one separation must hold (i left of j OR i right of j OR i above j OR i below j).

```python
for i in facilities:
    for j in facilities:
        if i >= j:
            continue
        d = Disjunct([1, 2, 3, 4])
        d[1].c = pyo.Constraint(expr=m.x[i] + m.w[i] <= m.x[j])  # i left of j
        d[2].c = pyo.Constraint(expr=m.x[j] + m.w[j] <= m.x[i])  # i right of j
        d[3].c = pyo.Constraint(expr=m.y[i] + m.h[i] <= m.y[j])  # i above j
        d[4].c = pyo.Constraint(expr=m.y[j] + m.h[j] <= m.y[i])  # i below j
        m.sep[i, j] = Disjunction(expr=[d[1], d[2], d[3], d[4]])
```

### Batch Processing

A unit cannot process two batches simultaneously — for each pair of batches assigned to the same unit, a sequencing disjunction (A before B, or B before A).

## Gotchas

- **Disjunctions must be handled before solving** — raw GDP models cannot be sent to standard solvers. Apply `gdp.bigm` / `gdp.hull`, or use the `gdpopt` logic-based solvers directly on the GDP model.
- **`Disjunction(expr=[...])` takes the list of disjuncts** — or use the indexed form with a rule/decorator returning a list per index.
- **M values matter** — too-large M values produce weak relaxations. Big-M estimates tight M for bounded variables by default; pass `bigM=` or a `BigM` suffix when estimation is not possible.
- **Hull transformation is tighter but creates more variables** — prefer Hull when problem size allows.
- **GDPopt needs an MIP solver for its subproblems** — pass `mip_solver=` when instantiating/solving.
- **Use `create_using` for experiments** — it returns a transformed copy, leaving your base GDP model intact for comparing reformulations.
