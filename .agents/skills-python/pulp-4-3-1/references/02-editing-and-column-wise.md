# Editing constraints and column-wise modelling (PuLP 4.3.1)

Source: PuLP 4.3.1 docs (`guides/how_to_edit_constraints.rst`, `guides/how_to_model_column_wise.rst`).

## On this page

- [Getting the `LpConstraint`](#getting-the-lpconstraint)
- [What you can change](#what-you-can-change)
- [What does not work](#what-does-not-work)
- [`add_column`](#add_column)
- [`remove_variables`](#remove_variables)
- [`prob.resolve()` — re-solving without rebuilding](#probresolvenbsp--re-solving-without-rebuilding)
- [Changing a variable's category](#changing-a-variables-category)
- [Example: cutting stock by column generation](#example-cutting-stock-by-column-generation)

## Getting the `LpConstraint`

Once a constraint is added to a problem, the problem keeps its own copy of it. You change that copy through its `LpConstraint`:

```python
# 1. keep the one returned by addConstraint
cap = prob.addConstraint(x + y <= 5, "cap")

# 2. look it up by name (None if there is no such constraint)
cap = prob.get_constraint_by_name("cap")

# 3. take it from the list of all constraints, in the order they were added
cap = prob.constraints()[0]
```

`prob += x + y <= 5, "cap"` also adds the constraint, but returns the problem, not the constraint. All three ways give an object for the same row: an edit made through one is visible through the others.

## What you can change

```python
cap = prob.addConstraint(x + y <= 5, "cap")   # x + y <= 5

cap[x] = 2              # 2*x + y <= 5      set a coefficient (same as cap.set_coefficient(x, 2))
del cap[y]              # 2*x <= 5          remove a term
cap[y] = 0              # same as del: coefficient 0 removes the term
cap.changeRHS(8)        # 2*x <= 8          set the right-hand side
cap += 3 * y            # 2*x + 3*y <= 8    add terms to the left-hand side
cap -= 1                # 2*x + 3*y <= 9    numbers go to the LHS (RHS moves the other way)
cap.sense = LpConstraintGE   # 2*x + 3*y >= 9
cap.name = "new_name"
```

- `cap.constant` is the constant on the **left-hand side**: `cap.constant = -8` is the same as `cap.changeRHS(8)`.
- `+=` / `-=` accept a variable, an expression, a number, or a list/dict of them.
- The sense is `LpConstraintLE`, `LpConstraintGE`, or `LpConstraintEQ` (importable from `pulp`).
- Each change is checked before it is applied: an infinite/NaN coefficient, a variable from another problem, or `cap.sense = None` raises `PulpError` and leaves the constraint unchanged.
- The dual (`cap.pi`) and slack (`cap.slack`) of the last solve are kept after an edit; the next solve replaces them.

### Re-solving with new data

```python
demand = prob.addConstraint(lpSum(flow[w]["bar_1"] for w in warehouses) >= 500, "demand_bar_1")

for value in range(500, 601, 10):
    demand.changeRHS(value)
    stats = prob.solve()
    print(value, stats.objective)
```

See `examples/BeerDistributionProblem_resolve.py` for the complete script.

## What does not work

`addConstraint` (and `prob += ...`) **copies** the expression into the problem. Changing the original expression afterwards changes only the expression:

```python
c = x + y <= 5
prob += c, "c"

c[x] = 3               # UserWarning; the problem still has x + y <= 5
c.changeRHS(8)         # UserWarning; same
```

PuLP raises a `UserWarning` whenever you edit an expression that has a sense (one created with `<=`, `>=`, `==`) — the message tells you to edit the `LpConstraint` instead. The warning also appears when you edit a sense-bearing expression **before** adding it (the expression does not know whether it was added). Build the whole expression before turning it into a constraint, or edit the `LpConstraint` after adding it. Expressions without a sense (objectives, `x + 2 * y`) never warn.

## `add_column`

Creates a variable together with its objective coefficient and its coefficients in **existing** constraints — the column-wise counterpart of row-wise modelling (typical for column generation):

```python
y = prob.add_column("y", lowBound=0, upBound=1, obj=2, coefficients={c1: 1, c2: 1})
```

- `name`, `lowBound`, `upBound`, `cat` are the same as `add_variable`.
- `obj` (default 0): the coefficient in the objective. If the problem has no objective yet and `obj` is not 0, one is created.
- `coefficients`: a dict from each `LpConstraint` of this problem to the coefficient of the new variable. Constraints not in the dict do not get the variable; a coefficient of 0 is skipped.
- Everything is checked before the variable is created: an infinite/NaN coefficient raises `ValueError` and leaves the problem unchanged.
- New terms go at the end of each constraint, so a column-wise model writes the same LP/MPS files as a row-wise one.

`LpConstraintVar` and `LpVariable(..., e=...)` (the 3.x way) are removed in 4.0; `add_column` replaces them. To set a single coefficient of an existing variable in a constraint, use `c1[z] = 0.5` or `del c1[x]`.

## `remove_variables`

`prob.remove_variables([z])` takes the variables out of every constraint, the objective, and every SOS group. The variables stay valid — you can still read them and put them back with `c[z] = value`. A variable no constraint and no objective uses is left out of the LP/MPS files and not sent to most solvers (the `resolve`-updating solvers send every variable, an unused one as an empty column, so new ones can be appended).

## `prob.resolve()` — re-solving without rebuilding

`prob.solve` loads the whole problem into the solver every time. `prob.resolve` does that too, except with the solvers that keep the model in memory and can edit it: **HiGHS**, **GUROBI**, **CPLEX_PY**, **XPRESS_PY**, **COPT**, **CYLP**, **PYGLPK** (since 4.3.0). After a first solve they record every edit, and `resolve` sends only those edits to the model held in `prob.solverModel`:

- new variables (`add_column` or `add_variable`) and new constraints;
- changed coefficients, right-hand sides and senses of existing constraints;
- changed bounds and categories of variables, and removed variables;
- a changed objective or objective sense.

The solver keeps its basis, so after adding a few columns or a cut it usually needs only a few simplex iterations (none if the old solution is still optimal). Duals, reduced costs and values are read back as after `solve`.

```python
prob.solve(getSolver("HiGHS", msg=False))   # builds the model
model = prob.solverModel
prob.add_column("y", 0, 1, obj=2, coefficients={c1: 1})
prob += x + y <= 1, "cut"
prob.resolve()                               # updates it in place
assert prob.solverModel is model
```

`resolve` builds the model from scratch, like `solve`, when it cannot update it:

- on the first solve, or when the last solve used another solver (or another instance);
- on a copy of the problem (`prob.copy()`): copies are not tracked;
- after adding or removing SOS groups;
- with CYLP, after changing a coefficient of an existing variable in an existing constraint (`remove_variables` included), since Clp cannot change a matrix entry — and for a MIP, which Cbc solves;
- with any other solver, which always rebuilds.

The solver's options (time limit, gaps, `msg`, log file) are applied again on every `resolve`. `warmStart` only applies when the model is built: on a resolve the previous basis is the warm start. A degenerate LP has several optimal bases, so a resolve can return other (equally valid) duals than a solve from scratch.

## Changing a variable's category

Bounds and category of a variable can be changed after creation — useful to solve the relaxation and then make it integer:

```python
x.lowBound = 2
x.upBound = None        # no upper bound
x.cat = LpInteger
x.cat = "Continuous"    # relax it
x.cat = LpBinary        # integer with bounds 0 and 1 (also sets the bounds)
```

Notes:

- The coefficients of `add_column` are given per `LpConstraint`, so keep the constraints when you create them (`addConstraint` returns them) or look them up with `prob.get_constraint_by_name(name)`.
- Duals and slacks are only available from solvers that return them, and only for linear problems: solve the relaxation while generating columns, then set `x.cat = LpInteger`.
- Editing a constraint, adding a column, or changing a category keeps the values (`varValue`, `pi`, `slack`) of the last solve until the next one.

## Example: cutting stock by column generation

Rolls of width 100 are cut to meet demands for four widths. Each variable is a *pattern*. The master problem starts with one simple pattern per width; new patterns are priced from the duals until none improves:

```python
from pulp import LpInteger, LpMaximize, LpMinimize, LpProblem, getSolver, lpSum

roll_width = 100
orders = {"w45": (45, 97), "w36": (36, 610), "w31": (31, 395), "w14": (14, 211)}
solver = getSolver("HiGHS", msg=False)   # any solver that returns duals

master = LpProblem("cutting_stock", LpMinimize)
patterns = []
demand = {}
for item, (width, quantity) in orders.items():
    x = master.add_variable(f"pattern_{len(patterns)}", lowBound=0)
    patterns.append(x)
    demand[item] = master.addConstraint(
        (roll_width // width) * x >= quantity, f"demand_{item}"
    )
master += lpSum(patterns)

master.solve(solver)
while True:
    duals = {item: c.pi for item, c in demand.items()}

    # Pricing: the pattern with the largest total dual value that fits a roll
    pricing = LpProblem("pricing", LpMaximize)
    n = pricing.add_variable_dicts("n", orders, lowBound=0, cat=LpInteger)
    pricing += lpSum(duals[i] * n[i] for i in orders)
    pricing += lpSum(width * n[i] for i, (width, _) in orders.items()) <= roll_width
    pricing.solve(solver)
    if 1 - pricing.objective.value() >= -1e-9:
        break   # no pattern improves the master problem

    pattern = {i: round(n[i].varValue) for i in orders}
    new = master.add_column(
        f"pattern_{len(patterns)}",
        lowBound=0,
        obj=1,
        coefficients={demand[i]: k for i, k in pattern.items() if k},
    )
    patterns.append(new)
    master.resolve()   # only the new column is sent to the solver

print("LP bound:", master.objective.value())   # 452.25

# Make the patterns integer and solve the final problem
for x in patterns:
    x.cat = LpInteger
stats = master.solve(solver)
print("rolls:", stats.objective)               # 453.0
```

The loop adds two patterns before no further improvement is possible. The same `master` problem is solved each time — never rebuilt. `master.resolve()` hands HiGHS only the new column and lets it start from the previous optimal basis; the final `master.solve(solver)` builds the model again, which is what you want once the categories changed.

Older style: `examples/CG.py` + `examples/SpongeRollProblem1.py`–`5.py` show the same idea with the `Pattern` class and explicit `resolve` loops.
