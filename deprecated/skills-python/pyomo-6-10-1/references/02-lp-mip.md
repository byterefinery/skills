# LP and MIP: Diet, Transport, Knapsack, Facility Location, Lot Sizing

## Linear Programming (LP)

### Diet Problem

Minimize food cost subject to nutritional requirements.

```python
m = pyo.AbstractModel()
m.F = pyo.Set()                    # Foods
m.N = pyo.Set()                    # Nutrients
m.cost = pyo.Param(m.F, within=pyo.PositiveReals)
m.nutrient = pyo.Param(m.F, m.N, within=pyo.NonNegativeReals)
m.min_nut = pyo.Param(m.N, default=0.0)
m.max_nut = pyo.Param(m.N, default=float('inf'))

m.x = pyo.Var(m.F, within=pyo.NonNegativeReals)

m.obj = pyo.Objective(expr=sum(m.cost[i]*m.x[i] for i in m.F))

def nutrient_rule(model, j):
    val = sum(m.nutrient[i,j]*m.x[i] for i in m.F)
    return pyo.inequality(m.min_nut[j], val, m.max_nut[j])
m.nut_limit = pyo.Constraint(m.N, rule=nutrient_rule)
```

### Transportation Problem

Minimize shipping cost from plants to markets.

```python
m = pyo.ConcreteModel()
m.i = pyo.Set(initialize=['seattle', 'san-diego'])
m.j = pyo.Set(initialize=['new-york', 'chicago', 'topeka'])
m.a = pyo.Param(m.i, initialize={'seattle': 350, 'san-diego': 600})
m.b = pyo.Param(m.j, initialize={'new-york': 325, 'chicago': 300, 'topeka': 275})
dtab = {('seattle','new-york'): 2.5, ('seattle','chicago'): 1.7, ...}
m.d = pyo.Param(m.i, m.j, initialize=dtab)
m.f = pyo.Param(initialize=90)

def c_init(model, i, j):
    return model.f * model.d[i,j] / 1000
m.c = pyo.Param(m.i, m.j, initialize=c_init)

m.x = pyo.Var(m.i, m.j, bounds=(0, None))

def supply_rule(model, i):
    return sum(model.x[i,j] for j in model.j) <= model.a[i]
m.supply = pyo.Constraint(m.i, rule=supply_rule)

def demand_rule(model, j):
    return sum(model.x[i,j] for i in model.i) >= model.b[j]
m.demand = pyo.Constraint(m.j, rule=demand_rule)

m.obj = pyo.Objective(expr=sum(m.c[i,j]*m.x[i,j] for i in m.i for j in m.j))
```

## Mixed Integer Programming (MIP)

### Knapsack Problem

Maximize value of selected items within weight limit.

```python
A = ['hammer', 'wrench', 'screwdriver', 'towel']
b = {'hammer': 8, 'wrench': 3, 'screwdriver': 6, 'towel': 11}
w = {'hammer': 5, 'wrench': 7, 'screwdriver': 4, 'towel': 3}
W_max = 14

m = pyo.ConcreteModel()
m.x = pyo.Var(A, within=pyo.Binary)

m.obj = pyo.Objective(expr=sum(b[i]*m.x[i] for i in A), sense=pyo.maximize)
m.weight = pyo.Constraint(expr=sum(w[i]*m.x[i] for i in A) <= W_max)
```

### Warehouse Location (p-median / Uncapacitated Facility Location)

Choose P warehouses to minimize distance-weighted assignment cost.

```python
W = ['Harlingen', 'Memphis', 'Ashland']   # Candidate warehouses
C = ['NYC', 'LA', 'Chicago', 'Houston']    # Customers
d = {('Harlingen','NYC'): 1956, ...}        # Distance matrix
P = 2                                       # Number of warehouses to open

m = pyo.ConcreteModel()
m.x = pyo.Var(W, C, bounds=(0, 1))          # Assignment fraction
m.y = pyo.Var(W, within=pyo.Binary)         # Open warehouse?

m.obj = pyo.Objective(expr=sum(d[w,c]*m.x[w,c] for w in W for c in C))

def one_per_cust(m, c):
    return sum(m.x[w,c] for w in W) == 1
m.one_per_cust = pyo.Constraint(C, rule=one_per_cust)

def warehouse_active(m, w, c):
    return m.x[w,c] <= m.y[w]               # Can only assign if open
m.warehouse_active = pyo.Constraint(W, C, rule=warehouse_active)

def num_warehouses(m):
    return sum(m.y[w] for w in W) <= P
m.num_warehouses = pyo.Constraint(rule=num_warehouses)
```

### Lot Sizing

Production planning with setup costs over multiple periods.

```python
m = pyo.ConcreteModel()
m.T = pyo.RangeSet(5)    # Time periods

i0 = 5.0                 # Initial inventory
c_setup = 4.6            # Setup cost per period
h_pos = 0.7              # Holding cost (positive inventory)
h_neg = 1.2              # Shortage cost (negative inventory)
P_max = 5.0              # Max production per period
d = {1: 5.0, 2: 7.0, 3: 6.2, 4: 3.1, 5: 1.7}  # Demand

m.y = pyo.Var(m.T, within=pyo.Binary)           # Setup indicator
m.x = pyo.Var(m.T, within=pyo.NonNegativeReals) # Production amount
m.i = pyo.Var(m.T)                               # Inventory level
m.i_pos = pyo.Var(m.T, within=pyo.NonNegativeReals)
m.i_neg = pyo.Var(m.T, within=pyo.NonNegativeReals)

def inventory_rule(m, t):
    if t == m.T.first():
        return m.i[t] == i0 + m.x[t] - d[t]
    return m.i[t] == m.i[t-1] + m.x[t] - d[t]
m.inventory = pyo.Constraint(m.T, rule=inventory_rule)

m.pos_neg = pyo.Constraint(m.T, rule=lambda m, t: m.i[t] == m.i_pos[t] - m.i_neg[t])
m.prod_indicator = pyo.Constraint(m.T, rule=lambda m, t: m.x[t] <= P_max * m.y[t])

m.obj = pyo.Objective(
    expr=sum(c_setup*m.y[t] + h_pos*m.i_pos[t] + h_neg*m.i_neg[t] for t in m.T)
)
```

### Sodacan (Geometry Optimization — LP relaxation of NLP)

Minimize surface area of cylinder with fixed volume.

```python
from math import pi
m = pyo.ConcreteModel()
m.r = pyo.Var(bounds=(0, None))
m.h = pyo.Var(bounds=(0, None))
m.obj = pyo.Objective(expr=2*pi*m.r*(m.r + m.h))
m.c = pyo.Constraint(expr=pi*m.h*m.r**2 == 355)
```

## Big-M Patterns

Common in MIP formulations. Use the smallest valid M for tighter formulations.

```python
# If-then: if y[i] == 1 then x[w,c] can be positive
m.x[w,c] <= M * m.y[w]

# Logical OR: at least one of two conditions must hold
m.z = pyo.Var(within=pyo.Binary)
m.c1 = pyo.Constraint(expr=m.x >= L1 - M*(1-m.z))
m.c2 = pyo.Constraint(expr=m.x <= U2 + M*m.z)
```

## Common Solvers for LP/MIP

| Solver | Type | License | Notes |
|--------|------|---------|-------|
| GLPK | LP | Open source | No MIP, no NLP |
| CBC | MIP | Open source | Via COIN-OR |
| Gurobi | LP/MIP/MILP | Commercial | Fastest for MIP |
| CPLEX | LP/MIP/MILP | Commercial | Full feature set |
| SCIP | MIP/NLP | Academic/Commercial | Strong presolve |
