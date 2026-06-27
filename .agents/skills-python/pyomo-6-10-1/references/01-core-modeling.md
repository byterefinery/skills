# Core Modeling: Sets, Params, Vars, Objectives, Constraints

## Two Paradigms

### ConcreteModel

Define structure and data together. Best for prototyping, inline data, or when data comes from Python computations.

```python
import pyomo.environ as pyo

m = pyo.ConcreteModel()
m.I = pyo.Set(initialize=[1, 2, 3])
m.a = pyo.Param(m.I, initialize={1: 10, 2: 20, 3: 30})
m.x = pyo.Var(m.I, within=pyo.NonNegativeReals)
```

### AbstractModel

Define structure first, load data later from `.dat` files or Python dicts. Mirrors AMPL workflow.

```python
m = pyo.AbstractModel()
m.I = pyo.Set()
m.a = pyo.Param(m.I)
m.x = pyo.Var(m.I)

# Load data
instance = m.create_instance('data.dat')
# Or from dict:
instance = m.create_instance(data={None: {'I': {None: [1,2,3]}, 'a': {1: 10, 2: 20, 3: 30}}})
```

## Sets

```python
# Simple set
m.I = pyo.Set(initialize=[1, 2, 3])

# Range
m.T = pyo.RangeSet(1, 5)        # {1, 2, 3, 4, 5}
m.T = pyo.RangeSet(5)            # {1, 2, 3, 4, 5}

# Cartesian product
m.IJ = pyo.Set(initialize=[(i,j) for i in I for j in J])
# Or: m.IJ = m.I * m.J

# Set with domain restriction
m.I = pyo.Set(within=pyo.Integers, initialize=range(10))

# Indexed set
m.S = pyo.Set(m.GROUPS)  # One set per group
```

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

# Mutable parameters (can be changed after construction)
m.p = pyo.Param(initialize=5, mutable=True)
```

Common domains: `Reals`, `NonNegativeReals`, `PositiveReals`, `Integers`, `NonNegativeIntegers`, `PositiveIntegers`, `Binary`.

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
m.x = pyo.Var(m.I, bounds=(0, None))   # None = unbounded

# Initialize and fix
m.x = pyo.Var(initialize=1.0)
m.x.fix(5.0)        # Fix to value
m.x.unfix()         # Unfix
m.x.is_fixed()      # Check if fixed

# VarList (unordered collection of variables)
m.v = pyo.VarList()
m.v.add(pyo.Var())
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
```

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

# Product of sums
(sum(m.a[i] for i in m.I)) * (sum(m.b[j] for j in m.J))

# Conditional summation
sum(m.x[i] for i in m.I if i > 3)

# abs, min, max (nonlinear)
pyo.abs(m.x)
pyo.min(m.x, m.y)
pyo.max(m.x, m.y)

# Logical operators (create binary indicator variables)
pyo.or_([m.x >= 5, m.y <= 3])
pyo.and_([m.x >= 0, m.x <= 10])
```

## Model Inspection

```python
m.pprint()                    # Full model structure
m.x.display()                 # Variable values
list(m.component_objects(pyo.Var))   # All variables
list(m.component_objects(pyo.Constraint))  # All constraints

# Check construction status
m.x.constructed

# Iterate over constraint data
for con in m.supply.values():
    print(con, pyo.value(con.body))
```

## Common Pitfalls

- **Use `pyo.value()` to extract numeric values** from Pyomo objects for comparisons or Python arithmetic.
- **Generator expressions are preferred** over list comprehensions in summation — `sum(x[i] for i in I)` not `sum([x[i] for i in I])`.
- **`Constraint.Skip` is the correct way to skip** a constraint index. Returning `None` raises an error.
- **AbstractModel requires `create_instance()`** before solving. You cannot solve an AbstractModel directly.
- **ConcreteModel is constructed immediately** — all components are built at creation time.
- **Mutable params behave like Python variables** — their values can change after construction, but they cannot appear in nonlinear expressions.
