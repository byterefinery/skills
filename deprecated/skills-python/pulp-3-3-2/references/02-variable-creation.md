# 02 — Variable Creation

## `prob.add_variable()`

Create a single variable attached to the problem. This is the preferred API in PuLP 3.x.

```python
from pulp import LpProblem, LpMinimize, LpInteger, LpBinary

prob = LpProblem("Example", LpMinimize)

# Continuous variable with bounds
x = prob.add_variable("x", lowBound=0, upBound=10)

# Unbounded above (use None for infinity)
y = prob.add_variable("y", lowBound=0)

# Free variable (no bounds)
z = prob.add_variable("z")

# Integer variable
i = prob.add_variable("count", lowBound=0, cat="Integer")

# Binary variable
b = prob.add_variable("switch", cat="Binary")
# Equivalent: b = prob.add_variable("switch", lowBound=0, upBound=1, cat="Integer")
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `name` | str | Variable name (alphanumeric + underscores; `-+[] ->/` replaced with `_`) |
| `lowBound` | float or None | Lower bound. `None` = -∞. Must be finite if specified. |
| `upBound` | float or None | Upper bound. `None` = +∞. Must be finite if specified. |
| `cat` | str | Category: `"Continuous"` (default), `"Integer"`, `"Binary"` |

## `prob.add_variable_dicts()`

Create a dictionary of variables indexed by one or more keys. Returns nested dicts for multi-dimensional indices.

```python
# Single index
ingredients = ["CHICKEN", "BEEF", "MUTTON"]
x = prob.add_variable_dicts("Ingr", ingredients, lowBound=0)
# x["CHICKEN"], x["BEEF"], x["MUTTON"]

# Two indices (returns nested dict)
warehouses = ["A", "B"]
bars = ["1", "2", "3"]
route = prob.add_variable_dicts("Route", (warehouses, bars), lowBound=0, cat="Integer")
# route["A"]["1"], route["A"]["2"], ..., route["B"]["3"]

# Three indices
vals = rows = cols = range(1, 10)
choices = prob.add_variable_dicts("Choice", (vals, rows, cols), cat="Binary")
# choices[v][r][c] for each value, row, column

# With bounds
x = prob.add_variable_dicts("x", indices, lowBound=0, upBound=100)
```

### Accessing Multi-Dimensional Dicts

```python
# Nested dict access
route["A"]["1"]           # warehouse A, bar 1

# Iterate over all
for w in warehouses:
    for b in bars:
        prob += route[w][b] >= 0
```

## `prob.add_variable_matrix()`

Create a list-of-lists (matrix) of variables. Indexed by integer positions.

```python
# 1D
x = prob.add_variable_matrix("x", range(5), lowBound=0)
# x[0], x[1], ..., x[4]

# 2D
time_steps = list(range(9))
units = list(range(5))
p = prob.add_variable_matrix("p", (time_steps, units), lowBound=0)
# p[t][i] for each time step and unit

# Set individual bounds after creation
for t in time_steps:
    for i in units:
        p[t][i].upBound = max_output[i]
```

### When to Use Which

| Scenario | Method |
|---|---|
| Single variable | `prob.add_variable()` |
| Variables keyed by named items (strings, tuples) | `prob.add_variable_dicts()` |
| Variables indexed by integer positions (matrices, grids) | `prob.add_variable_matrix()` |
| Cartesian product of two index sets as dict keys | `prob.add_variable_dict()` (flat dict with tuple keys) |

## `prob.add_variable_dict()`

Creates a flat dictionary with tuple keys for the Cartesian product of index lists.

```python
# Creates {(w, b): variable} for all warehouse-bar pairs
arc = prob.add_variable_dict("Arc", (warehouses, bars), lowBound=0)
# arc[("A", "1")], arc[("A", "2")], etc.
```

Use this when you want flat tuple-keyed access instead of nested dict access.

## Legacy API (Deprecated)

The following still work in 3.3.2 but emit deprecation warnings and will be removed in PuLP 4.0:

```python
# DEPRECATED — use prob.add_variable() instead
x = LpVariable("x", lowBound=0, upBound=10)

# DEPRECATED — use prob.add_variable_dicts() instead
x = LpVariable.dicts("x", indices, lowBound=0)

# DEPRECATED — use prob.add_variable_matrix() instead
x = LpVariable.matrix("x", indices, lowBound=0)
```

## Variable Modification After Creation

```python
# Change bounds
x.bounds(0, 20)

# Set initial value (for warm starting)
x.setInitialValue(5.0)

# Fix variable to current value
x.fixValue()     # Sets both bounds to varValue
x.unfixValue()   # Restores original bounds

# Check properties
x.isBinary()
x.isInteger()
x.isFree()
x.isPositive()
```

## Naming Conventions for Multi-Index Variables

When creating indexed variables, PuLP generates names automatically:

```python
x = prob.add_variable_dicts("Route", (Warehouses, Bars))
# Names: Route_A_1, Route_A_2, ..., Route_B_3

p = prob.add_variable_matrix("p", (time_steps, units))
# Names: p_0_0, p_0_1, ..., p_8_4
```

For clarity in LP files and debugging, use descriptive prefix names.
