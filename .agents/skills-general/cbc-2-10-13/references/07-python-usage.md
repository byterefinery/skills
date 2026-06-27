# Python Usage

Cbc is accessed from Python through modeling libraries or direct subprocess calls. There is no official standalone Python binding — use one of the wrappers below.

## PuLP (Most Common)

PuLP ships with a bundled Cbc binary. No separate installation needed.

### Basic MIP

```python
import pulp

prob = pulp.LpProblem("MyMIP", pulp.LpMinimize)

# Integer variables
x = pulp.LpVariable.dicts("x", range(5), lowBound=0, cat=pulp.LpInteger)

# Binary variables
y = pulp.LpVariable.dicts("y", range(3), cat=pulp.LpBinary)

# Continuous variable
z = pulp.LpVariable("z", lowBound=0, upBound=100)

# Objective
prob += pulp.lpSum([2*x[i] for i in range(5)]) + z

# Constraints
prob += x[0] + 2*x[1] <= 10
prob += pulp.lpSum(y) >= 1

# Solve with Cbc
solver = pulp.PULP_CBC_CMD(msg=1, timeLimit=300, threads=4)
status = prob.solve(solver)

# Check status
print(pulp.LpStatus[status])  # "Optimal", "Infeasible", etc.
print(f"Objective: {pulp.value(prob.objective)}")
```

### PuLP Solver Options

```python
solver = pulp.PULP_CBC_CMD(
    msg=1,              # 0=silent, 1=verbose
    timeLimit=300,      # seconds
    threads=4,          # parallel threads
    gapRel=0.01,        # relative gap (1%)
    gapAbs=1.0,         # absolute gap
    cuts="on",          # enable cuts
    maxNodes=1000000,   # node limit
    logFile="cbc.log",  # redirect Cbc output
)
```

### Multiple Solutions (Solution Pool)

PuLP doesn't directly expose the solution pool. Use `CbcCmd` to write solutions:

```python
solver = pulp.PULP_CBC_CMD(
    msg=0,
    timeLimit=300,
)
# Access underlying Cbc parameters via options string
solver.options = ["-maximumSavedSolutions", "10"]
prob.solve(solver)
```

### Writing/Reading MPS from PuLP

```python
prob.writeMPS("model.mps")

# Re-read and solve with different settings
prob2 = pulp.LpProblem()
prob2.read("model.mps")
prob2.solve(pulp.PULP_CBC_CMD(timeLimit=600))
```

## cvxpy

Install: `pip install cvxpy`

### Basic MIP

```python
import cvxpy as cp

# Variables
x = cp.Variable(5, integer=True)
y = cp.Variable(3, boolean=True)
z = cp.Variable()

# Problem
prob = cp.Problem(
    cp.Minimize(cp.sum(2*x) + z),
    [
        x[0] + 2*x[1] <= 10,
        cp.sum(y) >= 1,
        x >= 0,
        0 <= z <= 100,
    ]
)

# Solve with Cbc
prob.solve(solver=cp.CBC, verbose=True)

print(f"Status: {prob.status}")      # "optimal", "infeasible", etc.
print(f"Objective: {prob.optimal_value}")
print(f"x = {x.value}")
```

### cvxpy Solver Parameters

```python
prob.solve(
    solver=cp.CBC,
    verbose=True,
    timeLimit=300,
    threads=4,
)
```

For more options, use the `solver_options` dict:

```python
prob.solve(
    solver=cp.CBC,
    solver_options={
        "timeLimit": 300,
        "threads": 4,
        "allowableGap": 1.0,
    }
)
```

### Large Model with cvxpy

```python
import cvxpy as cp
import numpy as np

n_vars = 1000
n_cons = 500
A = np.random.randn(n_cons, n_vars)
b = np.random.randn(n_cons)
c = np.random.randn(n_vars)

x = cp.Variable(n_vars, integer=True)
prob = cp.Problem(cp.Minimize(c @ x), [A @ x <= b, x >= 0])
prob.solve(solver=cp.CBC, timeLimit=600)
```

## Pyomo

Install: `pip install pyomo`

Pyomo uses Cbc as an external solver. Install Cbc separately or use PuLP's bundled version.

### Concrete Model

```python
from pyomo.environ import (
    ConcreteModel, Var, Objective, Constraint,
    Integers, Binary, Reals, minimize, SolverFactory
)

model = ConcreteModel()
model.I = range(5)
model.x = Var(model.I, domain=Integers, bounds=(0, None))

model.obj = Objective(
    expr=sum(model.x[i] for i in model.I),
    sense=minimize
)

model.c1 = Constraint(expr=model.x[0] + 2*model.x[1] <= 10)

# Solve
solver = SolverFactory('cbc')
results = solver.solve(
    model,
    tee=True,           # Print solver output to console
    logfile=None,       # Or "cbc.log" for file
    options={
        'timeLimit': '300',
        'threads': '4',
        'logLevel': '2',
    }
)

print(results)
print(f"Objective: {model.obj()}")
for i in model.I:
    print(f"x[{i}] = {model.x[i]()}")
```

### Abstract Model

```python
from pyomo.environ import (
    AbstractModel, Param, Var, Objective, Constraint,
    Integers, minimize, SolverFactory
)

model = AbstractModel()
model.I = range(5)
model.cost = Param(model.I)
model.x = Var(model.I, domain=Integers, bounds=(0, None))

model.obj = Objective(
    expr=sum(model.cost[i]*model.x[i] for i in model.I),
    sense=minimize
)

# Load data and solve
model.load("data.dat")
SolverFactory('cbc').solve(model, tee=True)
```

### Pyomo with Solution Pool

```python
solver = SolverFactory('cbc')
results = solver.solve(
    model,
    options={
        'solutionPool': 'on',
        'maximumSavedSolutions': '10',
    }
)

# Access alternative solutions via results
for sol in results.Solution:
    print(sol)
```

## Google OR-Tools

Install: `pip install ortools`

OR-Tools bundles its own Cbc. No separate installation needed.

### Basic MIP

```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver('CBC')

# Variables
x = [solver.IntVar(0, solver.infinity(), f'x{i}') for i in range(5)]
y = [solver.BoolVar(f'y{i}') for i in range(3)]

# Objective
solver.Minimize(sum(x))

# Constraints
solver.Add(x[0] + 2*x[1] <= 10)
solver.Add(sum(y) >= 1)

# Solve
solver.SetTimeLimit(300000)  # milliseconds (not seconds!)
status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print(f"Objective: {solver.Objective().Value()}")
    for i, var in enumerate(x):
        print(f"x[{i}] = {var.solution_value()}")
elif status == pywraplp.Solver.INFEASIBLE:
    print("Infeasible")
```

### OR-Tools with Parameters

```python
solver = pywraplp.Solver.CreateSolver('CBC')

# Set parameters via solver-specific options
solver.SetParameter('threads=4')
solver.SetParameter('logLevel=2')
solver.SetTimeLimit(300000)  # ms

# Or use solver-specific string
# solver.SetOptionString('threads=4;logLevel=2')
```

### Multiple Solutions with OR-Tools

OR-Tools doesn't expose Cbc's solution pool directly, but you can enumerate solutions:

```python
solver = pywraplp.Solver.CreateSolver('CBC')
# ... build model ...

# Get first solution
solver.Solve()
if solver.Status() == pywraplp.Solver.OPTIMAL:
    best_obj = solver.Objective().Value()

    # Add cutoff to find next-best
    if solver.Minimization:
        solver.Add(solver.Objective().Value() >= best_obj + 1)
    else:
        solver.Add(solver.Objective().Value() <= best_obj - 1)

    # Re-solve for second solution
    status = solver.Solve()
```

## python-mip

Install: `pip install mip`

Requires system Cbc installed (`apt install coinor-cbc` or `conda install coin-or-cbc`).

### Basic MIP

```python
from mip import Model, xsum, INTEGER, BINARY, CONTINUOUS, minimize

m = Model(name="my_mip")

# Variables
x = [m.add_var(name=f'x{i}', lb=0, type=INTEGER) for i in range(5)]
y = [m.add_var(name=f'y{i}', type=BINARY) for i in range(3)]
z = m.add_var(name='z', lb=0, ub=100, type=CONTINUOUS)

# Objective
m.objective = minimize(xsum(2*xi for xi in x) + z)

# Constraints
m += x[0] + 2*x[1] <= 10
m += xsum(y) >= 1

# Solve
m.optimize(max_time=300, max_nodes=1000000)

print(f"Status: {m.status}")
print(f"Objective: {m.obj_val}")
for var in x:
    print(f"{var.name} = {var.x}")
```

### python-mip Status Codes

- `MODEL_OPTIMAL` — optimal solution found
- `MODEL_FEASIBLE` — feasible but not proven optimal (gap/time limit)
- `MODEL_INFEASIBLE` — no feasible solution
- `MODEL_UNBOUNDED` — unbounded
- `MODEL_CUTOFF` — cutoff reached

### python-mip with Callbacks

```python
def my_callback(model, where):
    if where == mip.CALLBACK_MIP:
        print(f"Current best: {model.obj_bound}, Incumbent: {model.primal_objective}")

m.optimize(max_time=300, callback=my_callback)
```

## yaposib

Install: `pip install yaposib`

Unified API across multiple solvers (Cbc, Clp, HiGHS, GLPK).

### Basic MIP

```python
from yaposib import Model, MAXIMIZE, MINIMIZE

m = Model(solver="cbc")

# Variables
x = m.add_var(name="x", integrality="integer", lb=0)
y = m.add_var(name="y", integrality="binary")
z = m.add_var(name="z", lb=0, ub=100)

# Constraints
m.add_con(x + 2*y <= 10)

# Objective
m.set_obj(x + z, sense=MINIMIZE)

# Solve
m.solve(time_limit=300)

print(f"Status: {m.status}")
print(f"Objective: {m.primal_objective}")
print(f"x = {x.primal}, y = {y.primal}, z = {z.primal}")
```

### yaposib with Multiple Solvers

```python
# Same code, different solver
for solver_name in ["cbc", "highs", "glpk"]:
    m = Model(solver=solver_name)
    # ... build model ...
    m.solve(time_limit=300)
    print(f"{solver_name}: {m.primal_objective}")
```

## Direct Cbc via Subprocess

When you need full CLI control without a modeling library:

### Basic subprocess call

```python
import subprocess
import json

result = subprocess.run(
    ["cbc", "model.mps", "-solve", "-quit", "-logLevel", "0"],
    capture_output=True, text=True, timeout=600
)

print(result.stdout)
# Parse output for objective value, status, etc.
```

### Parsing Cbc output

```python
import subprocess
import re

result = subprocess.run(
    ["cbc", "model.mps", "-solve", "-quit"],
    capture_output=True, text=True
)

# Extract objective from output
match = re.search(r"Objective value: ([\d.e+-]+)", result.stdout)
if match:
    obj = float(match.group(1))

# Check status
if "Optimal" in result.stdout:
    print("Optimal solution found")
elif "Infeasible" in result.stdout:
    print("Model is infeasible")
```

### Writing MPS from Python, solving with Cbc

```python
import subprocess
from pulp import LpProblem, LpVariable, LpMinimize, lpSum

# Build model in PuLP
prob = LpProblem("test", LpMinimize)
x = [LpVariable(f'x{i}', lowBound=0, cat='Integer') for i in range(5)]
prob += lpSum(x)
prob += x[0] + 2*x[1] <= 10

# Write MPS
prob.writeMPS("model.mps")

# Solve with Cbc CLI (full parameter control)
result = subprocess.run(
    ["cbc", "model.mps", "-solve", "-quit",
     "-timeLimit", "300", "-threads", "4", "-logLevel", "2"],
    capture_output=True, text=True
)

# Write solution back
prob.writeMPS("model_solution.mps")
```

### Reading Cbc Solution File

Cbc can write solutions in MPS format with `solution` section:

```python
# Solve and write solution
subprocess.run([
    "cbc", "model.mps", "-solve", "-quit",
    "-writeMps", "solution.mps"
])

# Parse solution from MPS file (use a library like pypsa or custom parser)
```

## Common Patterns Across All Libraries

### Handling Infeasibility

```python
# PuLP
if pulp.LpStatus[prob.status] == "Infeasible":
    print("No feasible solution")

# cvxpy
if prob.status in ("infeasible", "infeasible_inaccurate"):
    print("No feasible solution")

# Pyomo
if results.solver.termination_condition == "infeasible":
    print("Infeasible")

# OR-Tools
if status == pywraplp.Solver.INFEASIBLE:
    print("Infeasible")

# python-mip
if m.status == mip.MODEL_INFEASIBLE:
    print("Infeasible")
```

### Time Limit Handling

| Library | Parameter | Unit |
|---|---|---|
| PuLP | `timeLimit=300` | seconds |
| cvxpy | `timeLimit=300` or `solver_options={"timeLimit": 300}` | seconds |
| Pyomo | `options={'timeLimit': '300'}` | seconds (string) |
| OR-Tools | `SetTimeLimit(300000)` | **milliseconds** |
| python-mip | `max_time=300` | seconds |
| yaposib | `time_limit=300` | seconds |

### Gap Tolerance

```python
# PuLP
pulp.PULP_CBC_CMD(gapRel=0.01)  # 1% relative gap

# cvxpy
prob.solve(solver=cp.CBC, solver_options={"allowableGap": 1.0})

# Pyomo
options={'allowableGap': '0.01'}

# python-mip
m.optimize(gap=0.01)
```

### MIP Start (Warm Start)

Provide an initial feasible solution to speed up solving:

```python
# PuLP
for var in prob.variables():
    var.setUB(my_initial_values[var.name])  # or set lower bound

# OR-Tools
var.SetInitialSolution(my_value)

# python-mip
var.x = my_value  # Set before optimizing

# Pyomo
model.x[i].value = my_value  # Set before solving
```

## Performance Tips

1. **Use PuLP for quick prototyping** — bundled Cbc, simple API
2. **Use OR-Tools for production** — robust, good callbacks, bundles Cbc
3. **Use Pyomo for large academic models** — abstract model support, rich constraint syntax
4. **Use python-mip for direct Cbc control** — closest to native Cbc features
5. **Avoid rebuilding the solver object per solve** — reuse when possible
6. **Set time limits** — prevents runaway solves on hard instances
7. **Use `msg=0` / `verbose=False`** in production to suppress output overhead
8. **For repeated solves of similar models**, provide MIP start from previous solution
