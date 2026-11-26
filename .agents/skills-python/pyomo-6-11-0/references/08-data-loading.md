# Data Loading: .dat, .yaml, .json, CSV, Excel, SQL Files, Dicts

Pyomo's dataportal reads model data from several file formats — the classic AMPL `.dat` plus `.yaml`, `.json`, `.csv`, Excel (`.xls`/`.xlsx`), and SQL/SQLite files. Abstract models load data via `create_instance()`.

## AbstractModel.create_instance

```python
instance = m.create_instance(filename, data=None, name=None,
                             namespace=None, namespaces=None, ...)
```

- `filename` — a Pyomo data file (any supported format)
- `data` — a dict containing initialization data, used when there is no filename
- `namespace` / `namespaces` — select data from (a) namespace(s) in namespaced data files

```python
m = pyo.AbstractModel()
# ... define model structure ...
instance = m.create_instance('data.dat')
opt.solve(instance)
```

## AMPL .dat Format

The standard data file format for AbstractModel.

### Basic .dat File

```ampl
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

Rules of thumb: `set` commands list elements (space- or newline-separated), `param` commands assign scalars (`:= value;`) or tables (rows and columns with headers). The tutorials `set.py`, `param.py`, and `data.py` in `examples/pyomo/tutorials` show these formats in detail.

### ContinuousSet in .dat

A `ContinuousSet` is initialized with the `set` command (not `continuousset`):

```ampl
set t := 0 0.5 2.25 3.75 5;
```

## Python Dicts

Pass data directly as nested dicts; keys use `None` for the scenario key.

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

Dict patterns:

- **Scalar param**: `{'param_name': {None: value}}`
- **Indexed param**: `{'param_name': {index1: val1, index2: val2}}`
- **Multi-indexed param**: `{'param_name': {(i1, j1): val1, (i2, j2): val2}}`
- **Set**: `{'SET_NAME': {None: [elem1, elem2, ...]}}`

## Other Data Formats

The same `create_instance` call works with other file types; the dataportal detects the format.

```python
instance = m.create_instance('data.yaml')   # YAML
instance = m.create_instance('data.json')   # JSON
instance = m.create_instance('data.csv')    # CSV
instance = m.create_instance('data.xls')    # Excel (also .xlsx)
instance = m.create_instance('data.sqlite') # SQLite database
```

YAML/JSON dataportal support ships in the `optional` install extra (`pip install 'pyomo[optional]'`), as does Excel support (`openpyxl`).

## Writing Data Out

`pyo.instance2dat` writes a concrete model's data to a `.dat` file — useful for round-tripping a concrete model to the abstract workflow.

```python
pyo.instance2dat('out.dat', concrete_model)
```

## Concrete Models: Building Data from External Sources

For `ConcreteModel`, read external data with plain Python and pass it through `initialize=`:

```python
import json

with open('warehouse_data.json') as fd:
    data = json.load(fd)
# Build the model from the parsed dict, e.g. via initialize= on Sets/Params

# CSV with the csv module or pandas (installed separately)
import csv
with open('nodes.csv') as f:
    nodes = [row['Node'] for row in csv.DictReader(f)]
m.N = pyo.Set(initialize=nodes)
```

```python
# Pandas (install separately): DataFrame -> dicts for initialize=
import pandas as pd
df = pd.read_csv('data.csv')   # columns: item, value, weight
m.ITEMS = pyo.Set(initialize=df['item'].tolist())
m.v = pyo.Param(m.ITEMS, initialize=dict(zip(df['item'], df['value'])))
m.w = pyo.Param(m.ITEMS, initialize=dict(zip(df['item'], df['weight'])))

# 2D parameter from a pivot table
pivot = df.pivot(index='plant', columns='market', values='distance')
m.d = pyo.Param(m.plants, m.markets, initialize=pivot.to_dict())
```

## Parameter Initialization Patterns

### Lambda / Function Initialization

```python
# Compute parameter values on the fly
m.c = pyo.Param(m.I, m.J, initialize=lambda m, i, j: m.f * m.d[i,j] / 1000)

# Or a named function
def c_init(model, i, j):
    return model.f * model.d[i,j] / 1000
m.c = pyo.Param(m.I, m.J, initialize=c_init)
```

### Dictionary Comprehensions

```python
pairs = [('a','b', 1.5), ('a','c', 2.0), ('b','c', 1.0)]
dtab = {(i, j): v for i, j, v in pairs}
m.d = pyo.Param(m.I, m.J, initialize=dtab)
```

## Updating Parameters After Construction

### Mutable Parameters

```python
m.p = pyo.Param(initialize=5, mutable=True)
m.p.value = 10  # Change value after construction
```

### Reconstructing Components

For non-mutable params, change the value and re-construct dependent components:

```python
m.d[i,j].value = new_value
m.constraint.construct()  # Rebuild with the new data
```

## The pyomo Command-Line Tool

The `pyomo` executable solves a model file (and optional data file) from the command line:

```bash
pyomo model.py model.dat        # solve and summarize results
pyomo -l -s model.py model.dat  # -l prints solver log, -s summarizes solution
```

The `.py` file must create a `model` object that is a Pyomo Model instance.

## Gotchas

- **AbstractModel requires `create_instance()`** before any computation. You cannot access parameter values on the AbstractModel itself.
- **`.dat` files use AMPL syntax** — sets are space-separated, tables use row/column headers.
- **Pandas DataFrames need explicit conversion** to dicts for Pyomo parameters. Use `.to_dict()`, `dict(zip(...))`, or list comprehensions.
- **Missing data raises errors** — ensure all indices in a Set have corresponding Param values, or use `default=` on the Param.
- **Tuple keys must be tuples**, not lists: `{(1,2): val}` works, `[{1,2}: val]` does not.
