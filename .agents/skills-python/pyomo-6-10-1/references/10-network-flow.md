# Network Flow: Max Flow, Min Cost Flow, Shortest Path, Interdiction

## Max Flow

Find maximum flow from source to sink through a capacity-constrained network.

```python
m = pyo.AbstractModel()
m.N = pyo.Set()                    # Nodes
m.A = pyo.Set(within=m.N*m.N)      # Arcs (i,j) pairs
m.s = pyo.Param(within=m.N)        # Source node
m.t = pyo.Param(within=m.N)        # Sink node
m.c = pyo.Param(m.A)               # Arc capacities

m.f = pyo.Var(m.A, within=pyo.NonNegativeReals)

# Maximize flow into sink
def total_rule(model):
    return sum(model.f[i,j] for (i,j) in model.A if j == pyo.value(model.t))
m.total = pyo.Objective(rule=total_rule, sense=pyo.maximize)

# Capacity constraints
def limit_rule(model, i, j):
    return model.f[i,j] <= model.c[i,j]
m.limit = pyo.Constraint(m.A, rule=limit_rule)

# Flow conservation (except source and sink)
def flow_rule(model, k):
    if k == pyo.value(model.s) or k == pyo.value(model.t):
        return pyo.Constraint.Skip
    inflow = sum(model.f[i,k] for (i,j) in model.A if j == k)
    outflow = sum(model.f[k,j] for (i,j) in model.A if i == k)
    return inflow == outflow
m.flow = pyo.Constraint(m.N, rule=flow_rule)
```

## Min Cost Flow

Minimize cost of satisfying demands through a network.

```python
import pandas as pd
import pyomo.environ as pe

# Data from DataFrames
nodes_df = pd.read_csv('nodes.csv')
arcs_df = pd.read_csv('arcs.csv')

m = pe.ConcreteModel()
m.N = pe.Set(initialize=nodes_df['Node'].tolist())
m.A = pe.Set(
    initialize=[(r['From'], r['To']) for _, r in arcs_df.iterrows()],
    dimen=2,
)
m.cost = pe.Param(m.A, initialize=dict(zip(
    [(r['From'], r['To']) for _, r in arcs_df.iterrows()],
    arcs_df['Cost']
)))
m.cap = pe.Param(m.A, initialize=dict(zip(
    [(r['From'], r['To']) for _, r in arcs_df.iterrows()],
    arcs_df['Capacity']
)))
m.demand = pe.Param(m.N, initialize=dict(zip(nodes_df['Node'], nodes_df['Demand'])))

m.x = pe.Var(m.A, bounds=(0, None))

# Minimize total cost
m.obj = pe.Objective(expr=sum(m.cost[i,j]*m.x[i,j] for (i,j) in m.A))

# Capacity
m.cap_con = pe.Constraint(m.A, rule=lambda m, i, j: m.x[i,j] <= m.cap[i,j])

# Flow balance
def balance_rule(m, k):
    inflow = sum(m.x[i,k] for (i,j) in m.A if j == k)
    outflow = sum(m.x[k,j] for (i,j) in m.A if i == k)
    return inflow - outflow == m.demand[k]
m.balance = pe.Constraint(m.N, rule=balance_rule)
```

## Shortest Path

Find shortest path from source to destination.

```python
m = pyo.AbstractModel()
m.N = pyo.Set()
m.A = pyo.Set(within=m.N*m.N, dimen=2)
m.s = pyo.Param(within=m.N)
m.t = pyo.Param(within=m.N)
m.c = pyo.Param(m.A)  # Arc costs

# Binary: arc used or not
m.x = pyo.Var(m.A, within=pyo.Binary)

m.obj = pyo.Objective(expr=sum(m.c[i,j]*m.x[i,j] for (i,j) in m.A))

def path_rule(model, k):
    if k == pyo.value(model.s):
        return sum(model.x[k,j] for (i,j) in model.A if i == k) - \
               sum(model.x[i,k] for (i,j) in model.A if j == k) == 1
    if k == pyo.value(model.t):
        return sum(model.x[i,k] for (i,j) in model.A if j == k) - \
               sum(model.x[k,j] for (i,j) in model.A if i == k) == 1
    # Flow conservation for intermediate nodes
    return sum(model.x[i,k] for (i,j) in model.A if j == k) == \
           sum(model.x[k,j] for (i,j) in model.A if i == k)

m.path = pyo.Constraint(m.N, rule=path_rule)
```

## Multi-Commodity Flow

Multiple products flowing through shared network.

```python
m = pyo.ConcreteModel()
m.N = pyo.Set(initialize=nodes)
m.A = pyo.Set(initialize=arcs, dimen=2)
m.K = pyo.Set(initialize=commodities)  # Product types

m.cap = pyo.Param(m.A)
m.demand = pyo.Param(m.K, m.N)         # Demand per commodity per node
m.cost = pyo.Param(m.K, m.A)           # Cost per commodity per arc

m.x = pyo.Var(m.K, m.A, within=pyo.NonNegativeReals)

# Minimize total cost
m.obj = pyo.Objective(
    expr=sum(m.cost[k,i,j]*m.x[k,i,j] for k in m.K for (i,j) in m.A)
)

# Shared capacity
def shared_cap(m, i, j):
    return sum(m.x[k,i,j] for k in m.K) <= m.cap[i,j]
m.capacity = pyo.Constraint(m.A, rule=shared_cap)

# Flow balance per commodity
def balance(m, k, n):
    inflow = sum(m.x[k,i,n] for (i,j) in m.A if j == n)
    outflow = sum(m.x[k,n,j] for (i,j) in m.A if i == n)
    return inflow - outflow == m.demand[k,n]
m.flow_balance = pyo.Constraint(m.K, m.N, rule=balance)
```

## Network Interdiction

Adversarial problem: attacker removes arcs to minimize defender's max flow.

### Two-Stage Formulation

```python
# Stage 1 (attacker): choose arcs to interdict
# Stage 2 (defender): compute max flow after interdiction

m = pyo.ConcreteModel()
m.N = pyo.Set(initialize=nodes)
m.A = pyo.Set(initialize=arcs, dimen=2)
m.cap = pyo.Param(m.A)
m.attackable = pyo.Param(m.A, within=pyo.Binary)  # Can this arc be attacked?
m.budget = pyo.Param()                              # Number of attacks allowed

# Attacker variables: x[i,j] = 1 if arc (i,j) is interdicted
m.x = pyo.Var(m.A, within=pyo.Binary)

# Defender variables: y[i,j] = flow on arc (i,j)
m.y = pyo.Var(m.A, within=pyo.NonNegativeReals)
m.v = pyo.Var(within=pyo.NonNegativeReals)  # Total flow

# Minimize defender's max flow
m.obj = pyo.Objective(expr=m.v, sense=pyo.minimize)

# Attack budget
m.budget_con = pyo.Constraint(
    expr=sum(m.x[i,j]*m.attackable[i,j] for (i,j) in m.A) <= m.budget
)

# Defender flow constraints (using dual of max flow)
# rho[j] - rho[i] + pi[i,j] >= 0 - M*x[i,j]
m.rho = pyo.Var(m.N)
m.pi = pyo.Var(m.A, within=pyo.NonNegativeReals)

M = 1e6  # Big-M

def dual_edge_rule(m, i, j):
    attackable = int(m.attackable[i,j])
    return m.rho[j] - m.rho[i] + m.pi[(i,j)] >= 0 - M*m.x[(i,j)]*attackable
m.dual_edge = pyo.Constraint(m.A, rule=dual_edge_rule)

# Unit flow requirement
m.unit_flow = pyo.Constraint(
    expr=m.rho['source'] - m.rho['sink'] == 1
)

# Objective: minimize sum of capacity * pi
m.obj2 = pyo.Objective(
    expr=sum(m.cap[i,j]*m.pi[i,j] for (i,j) in m.A),
    sense=pyo.minimize,
)
```

## Transportation Problem

Classic supply-demand problem (see [02-lp-mip](references/02-lp-mip.md) for full example).

```python
# Plants -> Markets with capacity and demand constraints
m.x = pyo.Var(m.plants, m.markets, bounds=(0, None))

# Supply: sum over markets <= plant capacity
# Demand: sum over plants >= market demand
# Objective: minimize total transport cost
```

## Connector-Based Network Models

Use `pyo.Connector` and `pyo.Block` for modular network construction.

```python
def pipe_rule(model, i):
    pipe = pyo.Block()
    pipe.flow = pyo.Var()
    pipe.pIn = pyo.Var(within=pyo.NonNegativeReals)
    pipe.pOut = pyo.Var(within=pyo.NonNegativeReals)
    pipe.pDrop = pyo.Constraint(
        expr=pipe.pIn - pipe.pOut == model.friction * model.pipe_length[i] * pipe.flow
    )
    pipe.IN = pyo.Connector()
    pipe.IN.add(-pipe.flow, "flow")
    pipe.IN.add(pipe.pIn, "pressure")
    pipe.OUT = pyo.Connector()
    pipe.OUT.add(pipe.flow)
    pipe.OUT.add(pipe.pOut, "pressure")
    return pipe

m.pipes = pyo.Block(m.PIPES, rule=pipe_rule)
m.nodes = pyo.Block(m.NODES, rule=node_rule)

# Connect pipes to nodes
m.network_src = pyo.Constraint(
    m.PIPES, rule=lambda m, p: m.nodes[m.pipe_links[p,0]].port == m.pipes[p].IN
)
```

## Gotchas

- **Flow conservation must skip source/sink** — use `pyo.Constraint.Skip` for these nodes.
- **Multi-commodity flow is NP-hard** in general. Use strong solvers (Gurobi, CPLEX) for larger instances.
- **Network interdiction requires bilevel reformulation** — typically solved via dual substitution or cutting-plane methods.
- **Use `dimen=2` for arc sets** — tells Pyomo the set contains pairs, affecting indexing syntax.
- **Connector ports must match** — when connecting blocks, the port names and signs must be consistent (inflow negative, outflow positive).
