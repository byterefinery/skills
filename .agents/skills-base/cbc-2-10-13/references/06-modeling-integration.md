# Modeling Language Integration

Cbc integrates with many modeling systems. Below are the most common patterns.

## PuLP (Python)

```python
import pulp

prob = pulp.LpProblem("MyMIP", pulp.LpMinimize)
x = pulp.LpVariable.dicts("x", range(5), lowBound=0, cat=pulp.LpInteger)
prob += pulp.lpSum([x[i] for i in range(5)])
prob += x[0] + 2*x[1] <= 10

# Use Cbc solver
solver = pulp.PULP_CBC_CMD(msg=1, timeLimit=300, threads=4)
prob.solve(solver)

print(pulp.value(prob.objective))
for i in range(5):
    print(f"x[{i}] = {pulp.value(x[i])}")
```

Options: `msg` (0/1), `timeLimit`, `threads`, `gapRel` (relative gap), `gapAbs` (absolute gap).

## cvxpy (Python)

```python
import cvxpy as cp

x = cp.Variable(5, integer=True)
prob = cp.Problem(cp.Minimize(cp.sum(x)), [x[0] + 2*x[1] <= 10, x >= 0])
prob.solve(solver=cp.CBC, verbose=True, timeLimit=300)

print(x.value)
print(prob.optimal_value)
```

## Pyomo (Python)

```python
from pyomo.environ import *

model = ConcreteModel()
model.x = Var(range(5), domain=Integers, bounds=(0, None))
model.obj = Objective(expr=sum(model.x[i] for i in range(5)), sense=minimize)
model.c = Constraint(expr=model.x[0] + 2*model.x[1] <= 10)

solver = SolverFactory('cbc')
results = solver.solve(model, logfile=None, tee=True,
                       options={'timeLimit': '300', 'threads': '4'})

print(value(model.obj))
```

## JuMP (Julia)

```julia
using JuMP, Cbc

model = Model(Cbc.Optimizer)
set_attribute(model, "timeLimit", 300)
set_attribute(model, "threads", 4)

@variable(model, 0 <= x[1:5], Int)
@objective(model, Min, sum(x))
@constraint(model, x[1] + 2*x[2] <= 10)

optimize!(model)

println(objective_value(model))
println(value.(x))
```

## MiniZinc

Cbc is a native MiniZinc solver. Use from the MiniZinc IDE or CLI:

```bash
mzn-solving cbc model.mzn data.dzn
```

Or from Python with `minizinc` package:
```python
from minizinc import Instance, Solver

solver = Solver("cbc")
instance = Instance(solver, model="model.mzn")
result = instance.solve()
```

## AMPL

Cbc has a native AMPL interface. Requires the Ampl Solver Library (ASL).

```ampl
var x{1..5} integer >= 0;
minimize cost: sum{i in 1..5} x[i];
s.t. constraint: x[1] + 2*x[2] <= 10;
solve;
display x;
```

Run with: `ampl model.run` (with Cbc as the solver, or `option solver cbc;`)

## GAMS

Use the [GAMSlinks](https://github.com/coin-or/GAMSlinks) project:

```gams
Variables x(1..5) cost;
Positive Integer Variables x;
Equations obj constraint;

obj.. cost =e= sum(i, x(i));
constraint.. x('1') + 2*x('2') =l= 10;

Model m / all /;
Solve m using mip minimizing cost;
```

Set solver in GAMS: `option mip=cbc;`

## Google OR-Tools (Python)

```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver('CBC')
x = [solver.IntVar(0, solver.infinity(), f'x{i}') for i in range(5)]
solver.Minimize(sum(x))
solver.Add(x[0] + 2*x[1] <= 10)
solver.SetTimeLimit(300000)  # milliseconds

status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    print(f"Objective: {solver.Objective().Value()}")
    for i, var in enumerate(x):
        print(f"x[{i}] = {var.solution_value()}")
```

## python-mip

```python
from mip import Model, xsum, INTEGER

m = Model()
x = [m.add_var(name=f'x{i}', ub=0, type=INTEGER) for i in range(5)]
m += xsum(x)
m += x[0] + 2*x[1] <= 10
m.optimize(optimizer='cbc', max_time=300)

print(m.obj_val)
```

## Direct C/C++ Integration Pattern

When integrating Cbc into a larger application, the typical pattern is:

1. Build model using your modeling layer
2. Export to MPS/LP format or build via Osi API
3. Solve with Cbc
4. Read back solution and map to your variables

```cpp
// Build LP in Osi
OsiClpSolverInterface solver;
solver.readMps("model.mps");  // Or build programmatically

// Wrap in Cbc
CbcModel model(solver);
model.setDblParam(CbcModel::CbcMaximumSeconds, 300.0);
model.branchAndBound();

// Read solution
if (model.isProvenOptimal()) {
    const double *sol = model.bestSolution();
    // Map sol[i] back to your variable names
}
```

## yaposib

yaposib provides a unified Python interface to multiple solvers including Cbc:

```python
from yaposib import Model

m = Model(solver="cbc")
x = m.add_var(integrality="integer", lb=0)
y = m.add_var(integrality="integer", lb=0)
m.add_con(x + 2*y <= 10)
m.set_obj(x + y, sense="min")
m.solve(time_limit=300)

print(m.primal_objective)
```
