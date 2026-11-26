# Model patterns (PuLP 4.3.1)

Formulations grounded in the PuLP 4.3.1 `examples/` directory and the `CaseStudies` documentation.

## On this page

- [Transportation (Beer Distribution)](#transportation-beer-distribution)
- [Blending (Whiskas)](#blending-whiskas)
- [Sudoku as a 0-1 program](#sudoku-as-a-0-1-program)
- [Set partitioning (wedding seating)](#set-partitioning-wedding-seating)
- [Two-stage stochastic production planning](#two-stage-stochastic-production-planning)
- [Cutting stock (column generation)](#cutting-stock-column-generation)
- [examples/ catalog](#examples-catalog)

## Transportation (Beer Distribution)

Minimize transport cost moving product from warehouses to bars, subject to supply and demand. `examples/BeerDistributionProblem.py`:

```python
from pulp import *

Warehouses = ["A", "B"]
supply = {"A": 1000, "B": 4000}
Bars = ["1", "2", "3", "4", "5"]
demand = {"1": 500, "2": 900, "3": 1800, "4": 200, "5": 700}

costs = [  # indexed [warehouse][bar]
    [2, 4, 5, 2, 1],  # A
    [3, 1, 3, 2, 3],  # B
]
costs_dict = makeDict([Warehouses, Bars], costs, 0)

prob = LpProblem("Beer Distribution Problem", LpMinimize)
Routes = [(w, b) for w in Warehouses for b in Bars]

# One variable per (warehouse, bar) route
vars = prob.add_variable_dict("Route", (Warehouses, Bars), 0, None, LpInteger)

prob += (lpSum([vars[w, b] * costs_dict[w][b] for (w, b) in Routes]),
         "Sum_of_Transporting_Costs")

# Supply: what leaves a warehouse is bounded by its stock
for w in Warehouses:
    prob += (lpSum([vars[w, b] for b in Bars]) <= supply[w],
             f"Sum_of_Products_out_of_Warehouse_{w}")

# Demand: what enters a bar meets its demand
for b in Bars:
    prob += (lpSum([vars[w, b] for w in Warehouses]) >= demand[b],
             f"Sum_of_Products_into_Bar{b}")

prob.writeLP("BeerDistributionProblem.lp")
stats = prob.solve()
```

Variants in `examples/`: `BeerDistributionProblemWarehouseExtension.py` (open/close warehouses with fixed costs), `BeerDistributionProblemCompetitorExtension.py`, `BeerDistributionProblem_resolve.py` (change one demand RHS and re-solve in a loop — see [02-editing-and-column-wise](02-editing-and-column-wise.md)).

## Blending (Whiskas)

Minimize ingredient cost to meet nutritional requirements. `examples/WhiskasModel1.py`:

```python
prob = LpProblem("The Whiskas Problem", LpMinimize)

x1 = prob.add_variable("ChickenPercent", 0, None, LpInteger)
x2 = prob.add_variable("BeefPercent", 0, None, LpContinuous)

prob += 0.013 * x1 + 0.008 * x2, "Total Cost of Ingredients per can"
prob += x1 + x2 == 100, "PercentagesSum"
prob += 0.100 * x1 + 0.200 * x2 >= 8.0, "ProteinRequirement"
prob += 0.080 * x1 + 0.100 * x2 >= 6.0, "FatRequirement"
prob += 0.001 * x1 + 0.005 * x2 <= 2.0, "FibreRequirement"
prob += 0.002 * x1 + 0.005 * x2 <= 0.4, "SaltRequirement"

stats = prob.solve()
```

## Sudoku as a 0-1 program

The elegant formulation uses 729 binary variables `Choice_(v, r, c)` — one per (value, row, column) — instead of 81 value variables (LPs have no "not equal" operator). `examples/Sudoku1.py`:

```python
VALS = ROWS = COLS = range(1, 10)
Boxes = [
    [(3 * i + k + 1, 3 * j + m + 1) for k in range(3) for m in range(3)]
    for i in range(3)
    for j in range(3)
]

prob = LpProblem("Sudoku Problem")
choices = prob.add_variable_dict("Choice", (VALS, ROWS, COLS), 0, 1, LpBinary)

# No objective needed — feasibility only
for r in ROWS:
    for c in COLS:
        prob += lpSum([choices[v, r, c] for v in VALS]) == 1   # one value per square

for v in VALS:
    for r in ROWS:
        prob += lpSum([choices[v, r, c] for c in COLS]) == 1   # each value once per row
    for c in COLS:
        prob += lpSum([choices[v, r, c] for r in ROWS]) == 1   # once per column
    for b in Boxes:
        prob += lpSum([choices[v, r, c] for (r, c) in b]) == 1  # once per 3x3 box

# Givens are fixed by equality constraints, e.g.:
# prob += choices[5, 1, 1] == 1
```

`examples/Sudoku2.py` is a larger/alternative version.

## Set partitioning (wedding seating)

Choose tables (combinations of guests) so every guest is seated exactly once, at most `max_tables` tables are used, and "happiness" (distance between the alphabetically first and last guest at a table) is minimized. From the set-partitioning case study (`examples/wedding.py`):

```python
max_tables = 5
max_table_size = 4
guests = 'A B C D E F G I J K L M N O P Q R'.split()

def happiness(table):
    return abs(ord(table[0]) - ord(table[-1]))

possible_tables = [tuple(c) for c in pulp.allcombinations(guests, max_table_size)]

model = LpProblem("Wedding_Seating_Model", LpMinimize)
x = model.add_variable_dict('table', possible_tables, 0, 1, LpInteger)

model += pulp.lpSum([happiness(t) * x[t] for t in possible_tables])
model += pulp.lpSum([x[t] for t in possible_tables]) <= max_tables, "Maximum_number_of_tables"

for guest in guests:
    model += pulp.lpSum([x[t] for t in possible_tables if guest in t]) == 1, f"Must_seat_{guest}"
```

`examples/wedding_initial.py` is the warm-started version (see [03-export-and-warm-start](03-export-and-warm-start.md)).

## Two-stage stochastic production planning

`examples/Two_stage_Stochastic_GemstoneTools.py` (case study: "a_two_stage_production_planning_problem"): GTC buys steel (stage 1), then produces wrenches and pliers (stage 2) once assembly capacity and revenues are known, under four equally likely scenarios. Stage-2 variables are created with `add_variable_dict` indexed over products × scenarios; expected profit = stage-1 cost + average of scenario profits.

## Cutting stock (column generation)

`examples/SpongeRollProblem1.py`–`5.py` and `examples/CG.py`: rolls of fixed length are cut into patterns (`Pattern` class with length counts); the master problem minimizes production cost subject to demand, and new patterns are generated/priced iteratively. The modern 4.x formulation using `prob.add_column` + `prob.resolve()` is in [02-editing-and-column-wise](02-editing-and-column-wise.md).

Other catalog examples: `AmericanSteelProblem.py` (production mix), `ComputerPlantProblem.py`, `furniture.py`, `test1.py`–`test5.py`, `test7.py` (basic tutorial models).

## examples/ catalog

| File | Pattern |
|---|---|
| `BeerDistributionProblem.py` + extensions | Transportation, supply/demand, `resolve` variant |
| `WhiskasModel1.py`, `WhiskasModel2.py` | Blending / diet |
| `Sudoku1.py`, `Sudoku2.py` | 0-1 combinatorial constraint modelling |
| `wedding.py`, `wedding_initial.py` | Set partitioning, `allcombinations`, warm start |
| `Two_stage_Stochastic_GemstoneTools.py` | Two-stage stochastic programming |
| `SpongeRollProblem1-5.py`, `CG.py` | Cutting stock, column generation |
| `AmericanSteelProblem.py`, `ComputerPlantProblem.py`, `furniture.py` | Production/mix problems |
| `test1.py`–`test5.py`, `test7.py` | Small tutorial models |
