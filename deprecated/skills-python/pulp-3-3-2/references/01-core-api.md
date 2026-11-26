# 01 — Core API

## LpProblem

The top-level container for an optimization model.

```python
from pulp import LpProblem, LpMinimize, LpMaximize

prob = LpProblem("MyModel", LpMinimize)   # or LpMaximize
# Sense defaults to LpMinimize if omitted
```

### Adding Expressions and Constraints

Use `+=` on the problem:

```python
# Objective (first expression added without <=/>=/== becomes the objective)
prob += x + 2*y, "Objective name"

# Constraints
prob += x + y <= 10, "Constraint name"
prob += x - y >= 3, "Another constraint"
prob += 2*x + y == 5, "Equality"

# Use setObjective to replace existing objective
from pulp import LpConstraintVar
obj = LpConstraintVar("obj")
prob.setObjective(obj)
```

### Problem Methods

| Method | Description |
|---|---|
| `prob.solve(solver=None)` | Solve with default or specified solver; returns status int |
| `prob.writeLP("file.lp")` | Write model to LP format file |
| `prob.writeMPS("file.mps")` | Write model to MPS format file |
| `prob.variables()` | Iterate over all variables in the problem |
| `prob.constraints()` | Iterate over `(name, constraint)` pairs |
| `prob.get_constraint_by_name(name)` | Retrieve a constraint object by name |
| `prob.roundSolution(epsInt=1e-5, eps=1e-7)` | Round near-integer values to integers |
| `prob.sensitivityAnalysis()` | Run sensitivity analysis (solver-dependent) |
| `prob.clone()` | Deep copy of the model |
| `prob.resolve(solver=None)` | Re-solve with modified constraints/objective |

### Status Codes

```python
from pulp import LpStatus, LpStatusOptimal, LpStatusInfeasible

status = prob.solve()
print(LpStatus[status])   # "Optimal", "Infeasible", "Unbounded", etc.

# Check status
if status == LpStatusOptimal:
    print("Found optimal solution")
```

| Constant | Value | Meaning |
|---|---|---|
| `LpStatusNotSolved` | 0 | Problem not yet solved |
| `LpStatusOptimal` | 1 | Optimal solution found |
| `LpStatusInfeasible` | -1 | No feasible solution exists |
| `LpStatusUnbounded` | -2 | Objective is unbounded |
| `LpStatusUndefined` | -3 | Solution status undefined |

## LpVariable

Variables represent decision variables. Always create via `prob.add_variable()`.

### Properties After Solving

| Property | Description |
|---|---|
| `v.varValue` | Optimal value (None if not solved) |
| `v.dj` | Reduced cost (for LP, indicates how much objective changes per unit increase) |
| `v.lowBound` / `v.upBound` | Variable bounds |
| `v.cat` | Category: "Continuous", "Integer", "Binary" |

### Variable Methods

```python
# Check variable properties
v.isBinary()     # True if binary (0/1)
v.isInteger()    # True if integer category
v.isFree()       # True if no bounds
v.isPositive()   # True if lower bound is 0, no upper bound

# Modify bounds
v.bounds(0, 10)  # Set new bounds

# Round value
v.roundedValue(eps=1e-5)  # Returns rounded value for integer vars
```

## LpAffineExpression

Represents a linear combination of variables: `a1*x1 + a2*x2 + ... + constant`.

### Creation

```python
from pulp import LpAffineExpression, lpSum, lpDot

# From a variable
expr = LpAffineExpression(x)          # 1*x + 0

# From dict of {variable: coefficient}
expr = LpAffineExpression({x: 3, y: -2})  # 3*x + -2*y + 0

# From list of (var, coeff) tuples
expr = LpAffineExpression([(x, 3), (y, -2)])

# Using helpers
expr = lpSum([3*x, -2*y])
expr = lpDot([3, -2], [x, y])
```

### Operators

All standard arithmetic operators work:

```python
expr1 = 3*x + 2*y
expr2 = expr1 * 2           # 6*x + 4*y
expr3 = expr1 + 5            # adds constant
expr4 = -expr1               # negates all coefficients

# Comparison creates constraints
constraint = expr1 <= 10     # LpConstraint object
```

## LpConstraint

Constraints are created automatically when using comparison operators.

### Properties

| Property | Description |
|---|---|
| `c.name` | Constraint name |
| `c.sense` | -1 (≤), 0 (=), 1 (≥) |
| `c.constant` | RHS value (stored as LHS constant, negated for ≥) |
| `c.pi` | Dual value / shadow price |
| `c.slack` | Slack = RHS - LHS at solution |

### Modifying Constraints for Resolve

```python
# Store constraint reference
constraint = x + y <= 10
prob += constraint, "my_constraint"

# Later, modify the RHS (constant is stored as negated value on LHS)
constraint.constant = -15   # changes to x + y <= 15

# Re-solve
prob.resolve()
```

## Utility Functions

### `value(x)`

Returns the numeric value of a variable or expression. Returns the number itself if `x` is already numeric. Safe to call on unsolved variables (returns None for single vars, evaluates expressions with available values).

```python
from pulp import value

print(value(x))              # Variable value after solving
print(value(3*x + 2*y))      # Evaluates expression using solved values
print(value(42))             # Returns 42
```

### `lpSum(iterable)`

Sums a list of variables or affine expressions. More efficient than Python's `sum()` for PuLP expressions.

```python
# Sum all x[i]
total = lpSum([x[i] for i in indices])

# Weighted sum
cost = lpSum([costs[i] * x[i] for i in indices])
```

### `lpDot(coeffs, vars)`

Computes dot product of two lists. Equivalent to `lpSum([c*v for c,v in zip(coeffs, vars)])`.

```python
# For matrix-style indexing
total = lpDot(cost_row, var_column)
```

### `makeDict(headers, array, default=None)`

Converts a nested list into a nested dictionary using header lists. Useful for 2D data tables.

```python
from pulp import makeDict

Warehouses = ["A", "B"]
Bars = ["1", "2", "3"]
costs = [[2, 4, 5], [3, 1, 3]]
cost_dict = makeDict([Warehouses, Bars], costs)
# cost_dict["A"]["1"] == 2
```

### `splitDict(data)`

Splits a dictionary with list values into separate dictionaries.

```python
from pulp import splitDict

nodeData = {"A": [100, 50], "B": [200, 30]}
supply, fixed_cost = splitDict(nodeData)
# supply == {"A": 100, "B": 200}
# fixed_cost == {"A": 50, "B": 30}
```

### `allcombinations(orgset, k)` / `allpermutations(orgset, k)`

Generate all combinations or permutations of size up to `k`. Useful for set partitioning models.

```python
from pulp import allcombinations

guests = ["A", "B", "C", "D"]
for combo in allcombinations(guests, 3):
    print(combo)
# (A,), (B,), ..., (A, B), (A, C), ..., (A, B, C), ...
```

### `read_table(data, coerce_type, transpose=False)`

Parse a whitespace-delimited text table into a dictionary keyed by `(row_label, col_label)`.

```python
from pulp import read_table

table_str = """
        L1      L2
C1      6736    42658
C2      217266  227190
"""
table = read_table(table_str, int)
# table[("C1", "L1")] == 6736
```
