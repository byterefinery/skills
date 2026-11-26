# Core Modeling: Sets, Params, Vars, Objectives, Constraints

## Two Paradigms

### ConcreteModel

Define structure and data together. Best for prototyping, inline data, or when data comes from Python computations. Components are constructed immediately at model creation.

```python
import pyomo.environ as pyo

m = pyo.ConcreteModel()
m.I = pyo.Set(initialize=[1, 2, 3])
m.a = pyo.Param(m.I, initialize={1: 10, 2: 20, 3: 30})
m.x = pyo.Var(m.I, within=pyo.NonNegativeReals)
```

### AbstractModel

Define structure first, load data later from Pyomo data files or a Python dict via `create_instance()`. Mirrors the AMPL workflow. You cannot solve an AbstractModel directly.

```python
m = pyo.AbstractModel()
m.I = pyo.Set()
m.a = pyo.Param(m.I)
m.x = pyo.Var(m.I)

instance = m.create_instance('data.dat')
# Or from a dict (see 08-data-loading):
instance = m.create_instance(data={None: {'I': {None: [1, 2, 3]},
                                         'a': {1: 10, 2: 20, 3: 30}}})
```

`create_instance` also accepts `namespace=` / `namespaces=` to select data from namespaced data files.

## Sets

```python
# Simple set
m.I = pyo.Set(initialize=[1, 2, 3])

# Range
m.T = pyo.RangeSet(1, 5)      # {1, 2, 3, 4, 5}
m.T = pyo.RangeSet(5)         # {1, 2, 3, 4, 5}

# Cross product
m.IJ = m.I * m.J
# or constrain membership explicitly:
m.D = pyo.Set(within=m.I * m.J)

# Set with domain restriction
m.I = pyo.Set(within=pyo.Integers, initialize=range(10))

# Indexed set (one set per group)
m.S = pyo.Set(m.GROUPS)

# Declare the dimension of multi-index elements
m.A = pyo.Set(initialize=[(1, 2), (2, 3)], dimen=2)
```

`SetOf` builds a set from all combinations of given sets.

## Parameters

```python
# Scalar parameter
m.f = pyo.Param(initialize=90)

# Indexed parameter
m.a = pyo.Param(m.I, initialize={1: 10, 2: 20})

# Multi-indexed
m.d = pyo.Param(m.I, m.J, initialize=dtab)

# With domain restriction
m.c = pyo.Param(m.I, within=pyo.PositiveReals)

# With default value
m.b = pyo.Param(m.J, default=0.0)

# Mutable parameters (values can change after construction)
m.p = pyo.Param(initialize=5, mutable=True)

# With a validation function: validate(model, value, *index) -> bool
def prob_validator(model, value, s):
    return (value >= 0) and (value <= 1.0)
m.prob = pyo.Param(m.SCEN, validate=prob_validator)
```

Common domains: `Reals`, `NonNegativeReals`, `PositiveReals`, `Integers`, `NonNegativeIntegers`, `PositiveIntegers`, `Binary`, `Boolean`, `Any`.

## Variables

```python
# Scalar
m.x = pyo.Var(within=pyo.NonNegativeReals)
m.y = pyo.Var(within=pyo.Binary)

# Indexed
m.x = pyo.Var(m.I, within=pyo.Reals)
m.f = pyo.Var(m.I, m.J, within=pyo.NonNegativeReals)

# With bounds
m.x = pyo.Var(bounds=(0, 10))
m.x = pyo.Var(m.I, bounds=(0, None))      # None = unbounded
m.x = pyo.Var(m.I, bounds=lambda m, i: (0, m.a[i]))  # data-dependent bounds

# Initialize and fix
m.x = pyo.Var(initialize=1.0)
m.x.fix(5.0)        # Fix to value
m.x.unfix()         # Unfix
m.x.is_fixed()      # Check if fixed

# VarList (unordered collection of variables, useful for column generation)
m.v = pyo.VarList(within=pyo.NonNegativeReals)
v_new = m.v.add()   # add a new variable
m.v.add()
```

## Objectives

```python
# Direct expression
m.obj = pyo.Objective(expr=sum(c[i]*m.x[i] for i in m.I))

# With sense
m.obj = pyo.Objective(expr=..., sense=pyo.minimize)
m.obj = pyo.Objective(expr=..., sense=pyo.maximize)

# Rule-based
def obj_rule(model):
    return sum(model.c[i,j]*model.x[i,j] for i in model.I for j in model.J)
m.obj = pyo.Objective(rule=obj_rule)
```

Default sense is minimize. Only one active objective per model.

## Constraints

```python
# Single constraint
m.c1 = pyo.Constraint(expr=m.x + m.y >= 5)
m.c2 = pyo.Constraint(expr=m.x == 10)

# Inequality shorthand
m.c = pyo.Constraint(expr=pyo.inequality(0, m.x, 10))  # 0 <= x <= 10

# Indexed constraint (one per set element)
def supply_rule(model, i):
    return sum(model.x[i,j] for j in model.J) <= model.a[i]
m.supply = pyo.Constraint(m.I, rule=supply_rule)

# Multi-indexed
def flow_rule(model, i, j):
    return model.x[i,j] <= model.y[i]
m.flow = pyo.Constraint(m.I, m.J, rule=flow_rule)

# ConstraintList (dynamic collection)
m.cons = pyo.ConstraintList()
m.cons.add(m.x >= 0)
m.cons.add(m.y <= 10)

# Skipping constraints
def rule(model, i):
    if i == 1:
        return pyo.Constraint.Skip
    return model.x[i] >= 0
m.c = pyo.Constraint(m.I, rule=rule)

# Deactivate a constructed constraint (instead of skipping during build)
m.c1.deactivate()
```

### Logical Expressions

Build logical propositions from `Var`/`BooleanVar` and comparison expressions; attach them with `LogicalConstraint` instead of `Constraint`.

```python
m.b = pyo.BooleanVar()
m.b1 = pyo.BooleanVar([1, 2, 3])

# Logical operators
m.lc = pyo.LogicalConstraint(expr=pyo.lor(m.x >= 5, m.y <= 3))
m.lc2 = pyo.LogicalConstraint(expr=pyo.atmost(1, [m.b1[1], m.b1[2], m.b1[3]]))
m.lc3 = pyo.LogicalConstraint(expr=pyo.exactly(2, [m.b1[1], m.b1[2]]))
m.lc4 = pyo.LogicalConstraint(expr=pyo.implies(m.b, m.x >= 0))

# Convert logical constraints to algebraic form before solving
pyo.TransformationFactory('core.logical_to_linear').apply_to(m)
# Faster alternative (larger model):
# pyo.TransformationFactory('contrib.logical_to_disjunctive').apply_to(m)
```

Operators: `pyo.land`, `pyo.lor`, `pyo.lnot`, `pyo.xor`, `pyo.equivalent`, `pyo.implies`, `pyo.atleast`, `pyo.atmost`, `pyo.exactly`, `pyo.all_different`, `pyo.count_if`.

## Blocks

Group related components. Useful for modular model construction.

```python
def pipe_rule(model, i):
    pipe = pyo.Block()
    pipe.flow = pyo.Var()
    pipe.pressure = pyo.Var()
    pipe.con = pyo.Constraint(expr=pipe.flow <= 100)
    return pipe

m.pipes = pyo.Block(m.PIPES, rule=pipe_rule)
# Access: m.pipes[i].flow
```

## Expression Building

```python
# Summation patterns
sum(m.x[i] for i in m.I)
sum(m.x[i,j] for i in m.I for j in m.J)
pyo.quicksum(m.x[i] for i in m.I)   # faster for very large sums

# Product of sums
(sum(m.a[i] for i in m.I)) * (sum(m.b[j] for j in m.J))

# Conditional summation
sum(m.x[i] for i in m.I if i > 3)

# abs, min, max (nonlinear)
pyo.abs(m.x)
pyo.min(m.x, m.y)
pyo.max(m.x, m.y)

# Math functions
pyo.log(m.x), pyo.exp(m.x), pyo.sqrt(m.x), pyo.sin(m.x), ...

# Conditional expression
pyo.Expr_if(m.x > 0, m.x, 0)
```

## Model Inspection

```python
m.pprint()                     # Full model structure
m.x.display()                  # Variable values
list(m.component_objects(pyo.Var))        # All variables
list(m.component_objects(pyo.Constraint)) # All constraints

# Iterate over constraint data
for con in m.supply.values():
    print(con, pyo.value(con.body))

# Check results of a solve
status = opt.solve(m)
pyo.assert_optimal_termination(status)
```

## Common Pitfalls

- **Use `pyo.value()` to extract numeric values** from Pyomo objects for comparisons or Python arithmetic.
- **Generator expressions are preferred** over list comprehensions in summation — `sum(x[i] for i in I)` not `sum([x[i] for i in I])`.
- **`Constraint.Skip` is the correct way to skip** a constraint index. Returning `None` raises an error.
- **AbstractModel requires `create_instance()`** before solving. You cannot solve an AbstractModel directly.
- **ConcreteModel is constructed immediately** — all components are built at creation time.
- **Mutable params behave like Python variables** — their values can change after construction; expressions are re-evaluated from current values.
