# Data Loading: .dat Files, Dicts, Pandas, CSV/Excel

## AMPL .dat Format

Standard data file format for AbstractModel.

### Basic .dat File

```
param I := 1 2 3;
param a :=
    1  10
    2  20
    3  30;
param d :=
        new-york   chicago   topeka
seattle     2.5       1.7       1.8
san-diego   2.5       1.8       1.4;
```

### Loading .dat Files

```python
m = pyo.AbstractModel()
# ... define model structure ...
instance = m.create_instance('data.dat')
opt.solve(instance)
```

Multiple data files can be merged:
```python
instance = m.create_instance(['base.dat', 'scenario1.dat'])
```

## Python Dicts

Pass data directly as nested dicts. Keys use `None` for the scenario key.

```python
data = {
    None: {
        'ITEMS': {None: ('hammer', 'wrench', 'screwdriver', 'towel')},
        'v': {'hammer': 8, 'wrench': 3, 'screwdriver': 6, 'towel': 11},
        'w': {'hammer': 5, 'wrench': 7, 'screwdriver': 4, 'towel': 3},
        'limit': {None: 14},
    }
}

instance = model.create_instance(data=data)
```

### Dict Patterns

- **Scalar param**: `{'param_name': {None: value}}`
- **Indexed param**: `{'param_name': {index1: val1, index2: val2}}`
- **Multi-indexed param**: `{'param_name': {(i1,j1): val1, (i2,j2): val2}}`
- **Set**: `{'SET_NAME': {None: [elem1, elem2, ...]}}`

## Pandas Integration

### CSV to Model

```python
import pandas as pd
import pyomo.environ as pyo

# Read CSV data
df = pd.read_csv('data.csv')
# Columns: item, value, weight

m = pyo.ConcreteModel()
m.ITEMS = pyo.Set(initialize=df['item'].tolist())
m.v = pyo.Param(m.ITEMS, initialize=dict(zip(df['item'], df['value'])))
m.w = pyo.Param(m.ITEMS, initialize=dict(zip(df['item'], df['weight'])))
```

### Excel to Model

```python
df = pd.read_excel('knapsack_data.xlsx')

m = pyo.ConcreteModel()
m.ITEMS = pyo.Set(initialize=df['Item'].tolist())
m.value = pyo.Param(m.ITEMS, initialize=dict(zip(df['Item'], df['Value'])))
m.weight = pyo.Param(m.ITEMS, initialize=dict(zip(df['Item'], df['Weight'])))
```

### DataFrame as Parameter Source

```python
# 2D parameter from pivot table
pivot = df.pivot(index='plant', columns='market', values='distance')
dtab = pivot.to_dict()

m.d = pyo.Param(m.plants, m.markets, initialize=dtab)
```

## JSON Data

```python
import json

with open('data.json') as f:
    data = json.load(f)

# Convert to Pyomo data format
pyomo_data = {
    None: {
        'I': {None: list(data['items'].keys())},
        'a': {k: v['capacity'] for k, v in data['items'].items()},
    }
}
instance = m.create_instance(data=pyomo_data)
```

## Parameter Initialization Patterns

### Lambda Functions

```python
# Compute parameter values on the fly
m.c = pyo.Param(m.I, m.J, initialize=lambda m, i, j: m.f * m.d[i,j] / 1000)

# Random initialization
import random
m.cost = pyo.Param(m.M, m.N,
    initialize=lambda m, i, j: random.uniform(1.0, 2.0))
```

### Function-Based Initialization

```python
def c_init(model, i, j):
    return model.f * model.d[i,j] / 1000

m.c = pyo.Param(m.I, m.J, initialize=c_init)
```

### Dictionary Comprehensions

```python
# From list of tuples
pairs = [('a','b', 1.5), ('a','c', 2.0), ('b','c', 1.0)]
dtab = {(i,j): v for i, j, v in pairs}
m.d = pyo.Param(m.I, m.J, initialize=dtab)
```

## Network Data from CSV

Common pattern for network flow problems.

```python
import pandas as pd

nodes_df = pd.read_csv('nodes.csv')      # Column: Node
arcs_df = pd.read_csv('arcs.csv')        # Columns: StartNode, EndNode, Capacity

m = pyo.ConcreteModel()
m.N = pyo.Set(initialize=nodes_df['Node'].tolist())
m.A = pyo.Set(
    initialize=[(r['StartNode'], r['EndNode']) for _, r in arcs_df.iterrows()],
    dimen=2,
)
m.c = pyo.Param(m.A, initialize=dict(zip(
    [(r['StartNode'], r['EndNode']) for _, r in arcs_df.iterrows()],
    arcs_df['Capacity']
)))
```

## Updating Parameters After Construction

### Mutable Parameters

```python
m.p = pyo.Param(initialize=5, mutable=True)
m.p.value = 10  # Change value after construction
```

### Reconstructing Components

For non-mutable params, reconstruct dependent components:

```python
# Change param and rebuild constraints
m.d[i,j].value = new_value
m.constraint.construct()  # Rebuild constraint with new data
```

## Gotchas

- **AbstractModel requires `create_instance()`** before any computation. You cannot access parameter values on the AbstractModel itself.
- **`.dat` files use AMPL syntax** — sets are space-separated, tables use row/column headers.
- **Pandas DataFrames need explicit conversion** to dicts for Pyomo parameters. Use `.to_dict()`, `dict(zip(...))`, or list comprehensions.
- **Missing data raises errors** — ensure all indices in a Set have corresponding Param values, or use `default=` on the Param.
- **Tuple keys must be tuples**, not lists: `{(1,2): val}` works, `{{1,2}: val}` does not.
