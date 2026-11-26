# Network Flow: Max Flow, Min Cost Flow, Shortest Path, Interdiction

## Max Flow

Find maximum flow from source to sink through a capacity-constrained network.

```python
m = pyo.AbstractModel()
m.N = pyo.Set()                    # Nodes
m.A = pyo.Set(within=m.N*m.N, dimen=2)   # Arcs (i,j) pairs
m.s = pyo.Param(within=m.N)        # Source node
m.t = pyo.Param(within=m.N)        # Sink node
m.c = pyo.Param(m.A)               # Arc capacities

m.f = pyo.Var(m.A, within=pyo.NonNegativeReals)

# Maximize flow into sink
def total_rule(model):
    return sum(model.f[i,j] for (i,j) in model.A if j == model.t.value)
m.total = pyo.Objective(rule=total_rule, sense=pyo.maximize)

# Capacity constraints
def limit_rule(model, i, j):
    return model.f[i,j] <= model.c[i,j]
m.limit = pyo.Constraint(m.A, rule=limit_rule)

# Flow conservation (except source and sink)
def flow_rule(model, k):
    if k == model.s.value or k == model.t.value:
        return pyo.Constraint.Skip
    inflow = sum(model.f[i,k] for (i,j) in model.A if j == k)
    outflow = sum(model.f[k,j] for (i,j) in model.A if i == k)
    return inflow == outflow
m.flow = pyo.Constraint(m.N, rule=flow_rule)
```

## Min Cost Flow

Minimize cost of satisfying demands through a network.

```python
m = pyo.ConcreteModel()
m.N = pyo.Set(initialize=nodes)
m.A = pyo.Set(initialize=arcs, dimen=2)          # list of (from, to) pairs
m.cost = pyo.Param(m.A, initialize=cost)
m.cap = pyo.Param(m.A, initialize=cap)
m.demand = pyo.Param(m.N, initialize=demand)     # + supply / - demand per node

m.x = pyo.Var(m.A, bounds=(0, None))

# Minimize total cost
m.obj = pyo.Objective(expr=sum(m.cost[i,j]*m.x[i,j] for (i,j) in m.A))

# Capacity
m.cap_con = pyo.Constraint(m.A, rule=lambda m, i, j: m.x[i,j] <= m.cap[i,j])

# Flow balance (inflow - outflow == net demand)
def balance_rule(m, k):
    inflow = sum(m.x[i,k] for (i,j) in m.A if j == k)
    outflow = sum(m.x[k,j] for (i,j) in m.A if i == k)
    return inflow - outflow == m.demand[k]
m.balance = pyo.Constraint(m.N, rule=balance_rule)
```

Build `arcs`, `cost`, `cap`, `demand` from CSV/DataFrames as plain Python dicts before constructing the model (see [08-data-loading](references/08-data-loading.md)).

## Shortest Path

Find the shortest path from source to destination (arc variables binary or continuous — costs are nonnegative, so LP relaxation suffices).

```python
m = pyo.AbstractModel()
m.N = pyo.Set()
m.A = pyo.Set(within=m.N*m.N, dimen=2)
m.s = pyo.Param(within=m.N)
m.t = pyo.Param(within=m.N)
m.c = pyo.Param(m.A)  # Arc costs

m.x = pyo.Var(m.A, within=pyo.Binary)

m.obj = pyo.Objective(expr=sum(m.c[i,j]*m.x[i,j] for (i,j) in m.A))

def path_rule(model, k):
    if k == model.s.value:
        return sum(model.x[k,j] for (i,j) in model.A if i == k) - \
               sum(model.x[i,k] for (i,j) in model.A if j == k) == 1
    if k == model.t.value:
        return sum(model.x[i,k] for (i,j) in model.A if j == k) - \
               sum(model.x[k,j] for (i,j) in model.A if i == k) == 1
    # Flow conservation for intermediate nodes
    return sum(model.x[i,k] for (i,j) in model.A if j == k) == \
           sum(model.x[k,j] for (i,j) in model.A if i == k)

m.path = pyo.Constraint(m.N, rule=path_rule)
```

## Multi-Commodity Flow

Multiple products flowing through a shared network.

```python
m = pyo.ConcreteModel()
m.N = pyo.Set(initialize=nodes)
m.A = pyo.Set(initialize=arcs, dimen=2)
m.K = pyo.Set(initialize=commodities)   # product types

m.cap = pyo.Param(m.A)
m.demand = pyo.Param(m.K, m.N)          # net demand per commodity per node
m.cost = pyo.Param(m.K, m.A)            # cost per commodity per arc

m.x = pyo.Var(m.K, m.A, within=pyo.NonNegativeReals)

m.obj = pyo.Objective(
    expr=sum(m.cost[k,i,j]*m.x[k,i,j] for k in m.K for (i,j) in m.A))

# Shared capacity across commodities
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

Adversarial problem: an attacker removes arcs (budget-limited) to minimize the defender's maximum flow. Solved as a single-level MIP by substituting the defender's max-flow problem with its dual (the dual variables are added to the attacker model).

```python
m = pyo.ConcreteModel()
m.N = pyo.Set(initialize=nodes)
m.A = pyo.Set(initialize=arcs, dimen=2)
m.cap = pyo.Param(m.A)
m.attackable = pyo.Param(m.A, initialize=attackable)   # 1 if arc can be cut
m.budget = pyo.Param(initialize=B)

# Attacker variables: x[i,j] = 1 if arc (i,j) is interdicted
m.x = pyo.Var(m.A, within=pyo.Binary)

# Defender's max-flow dual variables
m.rho = pyo.Var(m.N)                      # node potentials
m.pi = pyo.Var(m.A, within=pyo.NonNegativeReals)  # arc capacity duals

# Minimize the defender's max flow (dual objective)
m.obj = pyo.Objective(
    expr=sum(m.cap[i,j]*m.pi[i,j] for (i,j) in m.A), sense=pyo.minimize)

# Attack budget
m.budget_con = pyo.Constraint(
    expr=sum(m.x[i,j] for (i,j) in m.A if m.attackable[i,j]) <= m.budget)

# Dual feasibility, relaxed where the attacker cuts the arc:
# rho[j] - rho[i] + pi[i,j] >= 0  (if arc survives),  rho[j] - rho[i] >= -M*x[i,j]
def dual_edge_rule(m, i, j):
    return m.rho[j] - m.rho[i] + m.pi[i,j] >= 0 - M * m.x[i,j] * m.attackable[i,j]
m.dual_edge = pyo.Constraint(m.A, rule=dual_edge_rule)

# Unit source-sink potential
m.unit_flow = pyo.Constraint(expr=m.rho[s] - m.rho[t] == 1)
```

## Transportation Problem

Classic supply-demand problem (full example in [02-lp-mip](references/02-lp-mip.md)).

```python
m.x = pyo.Var(m.plants, m.markets, bounds=(0, None))
# Supply: sum over markets <= plant capacity
# Demand: sum over plants >= market demand
# Objective: minimize total transport cost
```

## Connector-Based Network Models

`pyo.Connector` groups expressions with named ports for modular network assembly (pipes, nodes):

```python
def pipe_rule(model, i):
    pipe = pyo.Block()
    pipe.flow = pyo.Var()
    pipe.pIn = pyo.Var(within=pyo.NonNegativeReals)
    pipe.pOut = pyo.Var(within=pyo.NonNegativeReals)
    pipe.pDrop = pyo.Constraint(
        expr=pipe.pIn - pipe.pOut == model.friction * model.pipe_length[i] * pipe.flow)
    pipe.IN = pyo.Connector()
    pipe.IN.add(pipe.flow, "flow")
    pipe.IN.add(pipe.pIn, "pressure")
    pipe.OUT = pyo.Connector()
    pipe.OUT.add(pipe.flow, "flow")
    pipe.OUT.add(pipe.pOut, "pressure")
    return pipe

m.pipes = pyo.Block(m.PIPES, rule=pipe_rule)
```

`ConnectorData.add(var, name=None, aggregate=None)` appends an expression (optionally with a port name) to the connector.

## Gotchas

- **Flow conservation must skip source/sink** — use `pyo.Constraint.Skip` for these nodes (or use a net-demand formulation where source/sink have nonzero demand).
- **Multi-commodity flow is NP-hard** in general. Use strong solvers (Gurobi, CPLEX) for larger instances.
- **Network interdiction requires the dual substitution** (or cutting-plane/Benders methods) — you cannot nest two optimization problems in one model.
- **Use `dimen=2` for arc sets** — tells Pyomo the set contains pairs, affecting indexing and `.dat` parsing.
- **Connector ports must match** — when connecting blocks, the port names and signs must be consistent (e.g., inflow and outflow of the same quantity use opposite signs).
