# Export/import models and warm starts (PuLP 4.3.1)

Source: PuLP 4.3.1 docs (`guides/how_to_export_models.rst`, `guides/how_to_mip_start.rst`).

## On this page

- [Two export formats](#two-export-formats)
- [JSON / dict round-trip](#json--dict-round-trip)
- [MPS round-trip](#mps-round-trip)
- [Caveats](#caveats)
- [Warm starts (MIP start)](#warm-starts-mip-start)

## Two export formats

- **MPS** — industry standard, but not very flexible: stores only variables and constraints, not variable values.
- **Dict / JSON** — made to fit how PuLP stores information, so nothing is lost: it saves enough data to restore a complete PuLP model. Variable values, shadow prices and reduced costs are exported too, so a solved model can be read back to see those values. The solve outcome itself (status, timings) lives on the `LpSolveStats` each solve returns, not on the exported model.

## JSON / dict round-trip

```python
prob = LpProblem("test", LpMinimize)
x = prob.add_variable("x", 0, 4)
y = prob.add_variable("y", -1, 1)
z = prob.add_variable("z", 0, None, LpInteger)
prob += x + 4 * y + 9 * z, "obj"
prob += x + y <= 5, "c1"

data = prob.toDict()                      # or prob.toJson("model.json")
vars_dict, prob1 = LpProblem.fromDict(data)   # or LpProblem.fromJson("model.json")

vars_dict   # {'x': x, 'y': y, 'z': z}
prob1.solve()
vars_dict["x"].value()
```

Both `fromDict` and `fromJson` return a **tuple**: `(variables_dict, problem)`. The `to_dict` / `from_dict` / `to_json` / `from_json` spellings still work but are deprecated in 4.x.

JSON files written by 3.x load in 4.0; files written by 4.0 no longer contain `status` / `sol_status`, so PuLP 3.x cannot read them.

## MPS round-trip

```python
prob.writeMPS("model.mps")
vars_dict, prob1 = LpProblem.fromMPS("model.mps")
```

Same `(variables_dict, problem)` tuple. `prob.writeLP("model.lp")` writes a human-readable LP file (for inspection — no import counterpart). Since 4.1.0 the MPS reader reads BV, LI and UI bounds as integer variables.

## Caveats

- **Variable names must be unique.** PuLP permits duplicate internal names, but exports identify variables by name only.
- **Grouping is not restored.** Several dicts of variables come back as one flat dictionary keyed by name. With a strict naming convention you can reconstruct the structure by parsing names.
- **JSON and numpy/pandas types**: the standard `json` module cannot serialize `np.integer` / `np.floating` / `np.ndarray`. Pass a custom encoder (`to_json(path, cls=NpEncoder)` that maps `np.integer → int`, `np.floating → float`, `np.ndarray → list`), or cast values with `int()` / `float()` before modelling.

## Warm starts (MIP start)

Supported solver APIs: `CPLEX_CMD`, `GUROBI_CMD`, `COIN_CMD`, `CPLEX_PY`, `GUROBI`, `XPRESS`, `XPRESS_PY`.

**Filling values.** After a previous solve, each variable already has a value (`v.value()` / `v.varValue`). To seed a model that has not been solved, assign values directly:

```python
x[("O", "P", "Q", "R")].setInitialValue(1)
x[("K", "N", "O", "R")].setInitialValue(0)
```

(Since 4.3.0 `LpVariable.varValue` can also be set — including back to `None`.)

**Activating it.** Pass `warmStart=True` to the solver:

```python
prob.solve(pl.COIN_CMD(msg=True, warmStart=True))   # msg=True shows the solver confirming it loaded the start
```

**Fixing a variable.** Setting an initial value plus `fixValue()` pins it (bounds set to that value):

```python
v = x[("O", "P", "Q", "R")]
v.setInitialValue(1)
v.fixValue()
```

Complete script: `examples/wedding_initial.py` (warm-started wedding seating model). Note that for solvers that keep the model in memory (see `prob.resolve()` in [02-editing-and-column-wise](02-editing-and-column-wise.md)), `warmStart` only applies when the model is built; on a resolve the previous basis is the warm start.
