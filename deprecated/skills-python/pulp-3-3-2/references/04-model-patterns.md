# 04 — Model Patterns

Common optimization problem formulations with complete PuLP code.

## Transportation Problem

Minimize shipping cost from supply nodes to demand nodes.

```python
from pulp import *

Warehouses = ["A", "B"]
supply = {"A": 1000, "B": 4000}
Bars = ["1", "2", "3", "4", "5"]
demand = {"1": 500, "2": 900, "3": 1800, "4": 200, "5": 700}

# Cost matrix: cost[warehouse][bar]
costs = [  # Bars:  1  2  3  4  5
    [2, 4, 5, 2, 1],   # A
    [3, 1, 3, 2, 3],   # B
]
cost_dict = makeDict([Warehouses, Bars], costs)

prob = LpProblem("Transportation", LpMinimize)
x = prob.add_variable_dicts("Ship", (Warehouses, Bars), lowBound=0, cat="Integer")

# Minimize total shipping cost
prob += lpSum([x[w][b] * cost_dict[w][b] for w in Warehouses for b in Bars])

# Supply constraints
for w in Warehouses:
    prob += lpSum([x[w][b] for b in Bars]) <= supply[w], f"Supply_{w}"

# Demand constraints
for b in Bars:
    prob += lpSum([x[w][b] for w in Warehouses]) >= demand[b], f"Demand_{b}"

prob.solve()
```

## Assignment Problem

Assign each task to exactly one agent, minimizing cost.

```python
from pulp import *

Workers = ["Alice", "Bob", "Charlie"]
Tasks = ["T1", "T2", "T3"]
cost = {
    ("Alice", "T1"): 5, ("Alice", "T2"): 9, ("Alice", "T3"): 1,
    ("Bob", "T1"): 7, ("Bob", "T2"): 2, ("Bob", "T3"): 6,
    ("Charlie", "T1"): 3, ("Charlie", "T2"): 4, ("Charlie", "T3"): 8,
}

prob = LpProblem("Assignment", LpMinimize)
x = prob.add_variable_dicts("Assign", ((w, t) for w in Workers for t in Tasks), cat="Binary")

# Minimize total cost
prob += lpSum([cost[(w, t)] * x[(w, t)] for w in Workers for t in Tasks])

# Each worker does exactly one task
for w in Workers:
    prob += lpSum([x[(w, t)] for t in Tasks]) == 1, f"One_task_{w}"

# Each task assigned to exactly one worker
for t in Tasks:
    prob += lpSum([x[(w, t)] for w in Workers]) == 1, f"One_worker_{t}"

prob.solve()
```

## Blending Problem (Whiskas Cat Food)

Minimize ingredient cost while meeting nutritional requirements.

```python
from pulp import *

Ingredients = ["CHICKEN", "BEEF", "MUTTON", "RICE", "WHEAT", "GEL"]
costs = {"CHICKEN": 0.013, "BEEF": 0.008, "MUTTON": 0.010,
         "RICE": 0.002, "WHEAT": 0.005, "GEL": 0.001}
protein = {"CHICKEN": 0.100, "BEEF": 0.200, "MUTTON": 0.150,
           "RICE": 0.000, "WHEAT": 0.040, "GEL": 0.000}
fat = {"CHICKEN": 0.080, "BEEF": 0.100, "MUTTON": 0.110,
       "RICE": 0.010, "WHEAT": 0.010, "GEL": 0.000}

prob = LpProblem("Blending", LpMinimize)
x = prob.add_variable_dicts("Ingr", Ingredients, lowBound=0)

# Minimize cost
prob += lpSum([costs[i] * x[i] for i in Ingredients])

# Total must be 100%
prob += lpSum([x[i] for i in Ingredients]) == 100, "Total"

# Nutritional requirements
prob += lpSum([protein[i] * x[i] for i in Ingredients]) >= 8.0, "Protein"
prob += lpSum([fat[i] * x[i] for i in Ingredients]) >= 6.0, "Fat"

prob.solve()
```

## Facility Location (Fixed-Charge Network)

Decide which facilities to open (binary) and how much to ship (continuous), minimizing fixed + shipping costs.

```python
from pulp import *

Plants = ["SF", "LA", "Phoenix", "Denver"]
supply_data = {"SF": [1700, 70000], "LA": [2000, 70000],
               "Phoenix": [1700, 65000], "Denver": [2000, 70000]}
Stores = ["SD", "Barstow", "Tucson", "Dallas"]
demand = {"SD": 1700, "Barstow": 1000, "Tucson": 1500, "Dallas": 1200}

costs = [  # SD  Bar TU  Dal
    [5, 3, 2, 6],   # SF
    [4, 7, 8, 10],  # LA
    [6, 5, 3, 8],   # Phoenix
    [9, 8, 6, 5],   # Denver
]
cost_dict = makeDict([Plants, Stores], costs)
cap, fixed = splitDict(supply_data)

prob = LpProblem("FacilityLocation", LpMinimize)

# Flow variables (how much shipped on each route)
flow = prob.add_variable_dicts("Flow", (Plants, Stores), lowBound=0, cat="Integer")

# Binary: build or not
build = prob.add_variable_dicts("Build", Plants, cat="Binary")

# Minimize transport + fixed costs
prob += (lpSum([flow[p][s] * cost_dict[p][s] for p in Plants for s in Stores])
         + lpSum([fixed[p] * build[p] for p in Plants]))

# Supply only if plant is built
for p in Plants:
    prob += lpSum([flow[p][s] for s in Stores]) <= cap[p] * build[p], f"Cap_{p}"

# Meet demand
for s in Stores:
    prob += lpSum([flow[p][s] for p in Plants]) >= demand[s], f"Demand_{s}"

prob.solve()
```

## Sudoku Solver

Classic constraint satisfaction problem modeled as MIP.

```python
from pulp import *

VALS = ROWS = COLS = range(1, 10)

# Define 3x3 boxes
Boxes = [
    [(3*i+k+1, 3*j+l+1) for k in range(3) for l in range(3)]
    for i in range(3) for j in range(3)
]

prob = LpProblem("Sudoku")

# choices[v][r][c] = 1 if value v is placed at row r, column c
choices = prob.add_variable_dicts("Choice", (VALS, ROWS, COLS), cat="Binary")

# Exactly one value per cell
for r in ROWS:
    for c in COLS:
        prob += lpSum([choices[v][r][c] for v in VALS]) == 1

# Each value appears once per row, column, and box
for v in VALS:
    for r in ROWS:
        prob += lpSum([choices[v][r][c] for c in COLS]) == 1
    for c in COLS:
        prob += lpSum([choices[v][r][c] for r in ROWS]) == 1
    for b in Boxes:
        prob += lpSum([choices[v][r][c] for (r, c) in b]) == 1

# Given clues
clues = [(5, 1, 1), (6, 2, 1), (8, 4, 1)]
for v, r, c in clues:
    prob += choices[v][r][c] == 1

prob.solve()
```

## Cutting Stock Problem

Minimize raw material used to cut items of various lengths.

```python
from pulp import *

Lengths = ["5", "7", "9"]
demand = {"5": 150, "7": 200, "9": 300}
Patterns = ["A", "B", "C"]
# Each pattern: [num_5cm, num_7cm, num_9cm] from a 20cm roll
pattern_data = [[0, 2, 2], [1, 1, 0], [1, 0, 1]]
pattern_dict = makeDict([Lengths, Patterns], pattern_data)

prob = LpProblem("CuttingStock", LpMinimize)
x = prob.add_variable_dicts("Pattern", Patterns, lowBound=0, cat="Integer")

# Minimize total rolls used
prob += lpSum([x[p] for p in Patterns])

# Meet demand for each length
for l in Lengths:
    prob += lpSum([x[p] * pattern_dict[l][p] for p in Patterns]) >= demand[l], f"Demand_{l}"

prob.solve()
```

## Generation Planning (Unit Commitment)

Minimize generation cost with startup costs and binary on/off decisions.

```python
from pulp import *
import math

tmax = 9       # Time steps
units = 5      # Thermal units
time = list(range(tmax))
unit = list(range(units))

demand = [100 + 50 * math.sin(4 * t * 2 * 3.1415 / tmax) for t in time]
pmax = [30] * units
costs = [i + 1 for i in unit]
startup_costs = [100 * (i + 1) for i in unit]

prob = LpProblem("Generation", LpMinimize)

# Production variables
p = prob.add_variable_matrix("prod", (time, unit), lowBound=0)
for t in time:
    for i in unit:
        p[t][i].upBound = pmax[i]

# Binary on/off state
d = prob.add_variable_matrix("state", (list(range(tmax + 1)), unit), 0, 1, cat="Integer")

# Startup indicator
u = prob.add_variable_matrix("startup", (time, unit), lowBound=0, cat="Integer")

# Link production to state
for t in time:
    for i in unit:
        prob += p[t][i] <= pmax[i] * d[t][i], f"Prod_{t}_{i}"
        prob += u[t][i] >= d[t+1][i] - d[t][i], f"Startup_{t}_{i}"

# Meet demand
for t in time:
    prob += lpSum([p[t][i] for i in unit]) >= demand[t], f"Demand_{t}"

# Objective: production cost + startup cost
prob += (lpSum([lpSum([p[t][i] for t in time]) * costs[i] for i in unit])
         + lpSum([lpSum([u[t][i] for t in time]) * startup_costs[i] for i in unit]))

prob.solve()
```

## Wedding Seating (Set Partitioning)

Assign guests to tables, optimizing a happiness metric.

```python
from pulp import *

guests = "A B C D E F G I J K L M N O P Q R".split()
max_tables = 5
max_size = 4

# All possible table configurations
possible_tables = list(allcombinations(guests, max_size))

def happiness(table):
    return abs(ord(table[0]) - ord(table[-1]))

prob = LpProblem("WeddingSeating", LpMinimize)
x = prob.add_variable_dicts("Table", possible_tables, cat="Binary")

# Minimize total unhappiness
prob += lpSum([happiness(t) * x[t] for t in possible_tables])

# Limit number of tables
prob += lpSum([x[t] for t in possible_tables]) <= max_tables

# Each guest seated exactly once
for g in guests:
    prob += lpSum([x[t] for t in possible_tables if g in t]) == 1, f"Seat_{g}"

prob.solve()
```

## Network Flow (American Steel)

Minimize cost of shipping through a network with arc capacity constraints.

```python
from pulp import *

Nodes = ["Youngstown", "Pittsburgh", "Cincinnati", "KansasCity",
         "Chicago", "Albany", "Houston", "Tempe", "Gary"]

node_data = {
    "Youngstown": [10000, 0], "Pittsburgh": [15000, 0],
    "Cincinnati": [0, 0], "KansasCity": [0, 0],
    "Chicago": [0, 0], "Albany": [0, 3000],
    "Houston": [0, 7000], "Tempe": [0, 4000], "Gary": [0, 6000],
}
supply, demand = splitDict(node_data)

Arcs = [("Youngstown", "Albany"), ("Youngstown", "Chicago"), ...]
arc_data = {
    ("Youngstown", "Albany"): [0.5, 0, 1000],
    ("Youngstown", "Chicago"): [0.375, 0, 5000],
    # ... cost, min_flow, max_flow
}
costs, mins, maxs = splitDict(arc_data)

prob = LpProblem("NetworkFlow", LpMinimize)
x = prob.add_variable_dicts("Flow", Arcs, cat="Integer")

# Set arc bounds
for a in Arcs:
    x[a].bounds(mins[a], maxs[a])

# Minimize cost
prob += lpSum([x[a] * costs[a] for a in Arcs])

# Flow conservation at each node
for n in Nodes:
    inflow = lpSum([x[(i, j)] for (i, j) in Arcs if j == n])
    outflow = lpSum([x[(i, j)] for (i, j) in Arcs if i == n])
    prob += supply[n] + inflow >= demand[n] + outflow, f"Flow_{n}"

prob.solve()
```

## Two-Stage Stochastic Programming

First-stage decisions before uncertainty is revealed; second-stage adaptive decisions per scenario.

```python
from pulp import *

scenarios = [0, 1, 2, 3]
products = ["W", "P"]
p_scenario = [0.25, 0.25, 0.25, 0.25]
earnings = [[160, 100], [160, 100], [90, 100], [90, 100]]
cap_assembly = [8, 10, 8, 10]
steel_price = 58

prob = LpProblem("Stochastic", LpMaximize)

# First-stage: steel purchase
steel = prob.add_variable("SteelPurchase", lowBound=0)

# Second-stage: production per scenario
prod = prob.add_variable_dicts("Prod", (scenarios, products), lowBound=0)

# Maximize expected profit
prob += lpSum([p_scenario[s] * earnings[s][i] * prod[s][products.index(p)]
               for s in scenarios for i, p in enumerate(products)]) - steel * steel_price

# Steel constraint per scenario
for s in scenarios:
    prob += 1.5 * prod[s]["W"] + 1.0 * prod[s]["P"] <= steel, f"Steel_{s}"
    prob += 0.3 * prod[s]["W"] + 0.5 * prod[s]["P"] <= cap_assembly[s], f"Asm_{s}"

prob.solve()
```
