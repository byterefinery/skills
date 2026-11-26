# 05 — Advanced Topics

## Sensitivity Analysis

After solving an LP (not MILP), retrieve dual values and reduced costs.

```python
from pulp import *

prob = LpProblem("Sensitivity", LpMinimize)
x = prob.add_variable("x", lowBound=0, upBound=4)
y = prob.add_variable("y", lowBound=-1, upBound=1)
z = prob.add_variable("z", lowBound=0)

prob += x + 4*y + 9*z
prob += x + y <= 5, "c1"
prob += x + z >= 10, "c2"
prob += -y + z == 7, "c3"

prob.solve()

# Reduced costs (how objective changes per unit increase in variable)
for v in prob.variables():
    print(f"{v.name}: value={v.varValue}, reduced_cost={v.dj}")

# Shadow prices and slack for constraints
print("Constraint | Shadow Price | Slack")
for name, c in prob.constraints():
    print(f"{name:12s} | pi={c.pi:.4f} | slack={c.slack:.4f}")
```

### Interpretation

- **Shadow price (`pi`)**: How much the objective improves per unit increase in RHS. Positive `pi` on a ≤ constraint means tightening it worsens the objective.
- **Reduced cost (`dj`)**: For non-basic variables, how much the coefficient must improve before the variable enters the basis. Zero for basic variables.
- **Slack**: Difference between LHS and RHS at optimum. Zero means the constraint is binding.

### Limitations

Dual values are only reliable for continuous LP problems. MILP solvers may return approximate or zero duals. Solve the LP relaxation first if you need exact shadow prices for a problem with integer variables.

## Resolve (Re-optimization)

Modify constraints or the objective and re-solve without rebuilding the model.

```python
from pulp import *

Warehouses = ["A", "B"]
Bars = ["1", "2", "3"]
x = prob.add_variable_dicts("Route", (Warehouses, Bars), lowBound=0, cat="Integer")

# Store constraint references for later modification
demand_constraints = {}
for b in Bars:
    c = lpSum([x[w][b] for w in Warehouses]) >= demand[b]
    prob += c, f"Demand_{b}"
    demand_constraints[b] = c

prob.solve()

# Modify demand and re-solve
demand_constraints["1"].constant = -800   # changes >= 500 to >= 800
prob.resolve()
```

### Key Point: Constant Storage

The constraint constant is stored as the **LHS constant**, which is negated relative to the RHS. For `x + y <= 10`, the constant is `-10`. For `x + y >= 5`, the constant is also `-5` (the sense determines direction).

```python
# x + y <= 10  → constraint.constant = -10
# To change to x + y <= 15:
constraint.constant = -15

# x + y >= 5  → constraint.constant = -5
# To change to x + y >= 8:
constraint.constant = -8
```

## Enumerating All Solutions

Find all feasible solutions by adding exclusion constraints after each solution.

```python
from pulp import *

# ... build model with binary variables ...

solutions = []
while True:
    prob.solve()
    if LpStatus[prob.status] != "Optimal":
        break

    # Record current solution
    sol = {v.name: v.varValue for v in prob.variables()}
    solutions.append(sol)

    # Exclude this solution: sum of matching binary vars <= n-1
    # If 81 binary variables are 1, force at most 80 to match next time
    prob += lpSum([v for v in prob.variables() if value(v) == 1]) <= len([v for v in prob.variables() if value(v) == 1]) - 1

print(f"Found {len(solutions)} solutions")
```

This pattern is used in Sudoku2 to find all valid solutions.

## Column Generation

Solve large problems by iteratively generating variables (columns). Classic use case: cutting stock.

### Workflow

1. **Restricted Master Problem (RMP)**: Start with a small set of columns
2. **Solve RMP as LP relaxation** → get dual values
3. **Pricing Subproblem**: Use duals to find a column with negative reduced cost
4. **Add new column to RMP** if found
5. **Repeat** until no improving column exists
6. **Final solve** with integer constraints

```python
from pulp import *

# Master problem
def master_solve(patterns, demand, relax=True):
    prob = LpProblem("Master", LpMinimize)
    cat = LpContinuous if relax else LpInteger

    x = prob.add_variable_dicts("Pattern", patterns, lowBound=0, cat=cat)
    s = prob.add_variable_dicts("Surplus", demand.keys(), lowBound=0, cat=cat)

    # Minimize rolls - surplus value
    prob += lpSum([x[p] for p in patterns]) - lpSum([s[l] * 0.04 for l in demand])

    # Demand constraints
    for length, req in demand.items():
        c = lpSum([x[p] * pattern_counts[p][length] for p in patterns]) - s[length] >= req
        prob += c, f"Min_{length}"

    prob.solve()
    prob.roundSolution()

    if relax:
        # Return dual values
        duals = {}
        for length in demand:
            c = prob.get_constraint_by_name(f"Min_{length}")
            duals[length] = c.pi
        return duals
    else:
        return value(prob.objective), {v.name: int(v.varValue or 0) for v in prob.variables()}


# Pricing subproblem
def pricing(duals, roll_length=20):
    prob = LpProblem("Pricing", LpMinimize)
    y = prob.add_variable_dicts("Count", ["5", "7", "9"], lowBound=0, cat="Integer")
    trim = prob.add_variable("Trim", lowBound=0, cat="Integer")

    # Minimize reduced cost
    prob += 1 - lpSum([y[l] * duals[l] for l in duals])

    # Length conservation
    prob += lpSum([y[l] * int(l) for l in duals]) + trim == roll_length

    prob.solve()
    prob.roundSolution()

    reduced_cost = value(prob.objective)
    if reduced_cost < -1e-5:
        new_pattern = {l: int(y[l].varValue or 0) for l in duals}
        return new_pattern, True
    return None, False


# Column generation loop
patterns = [{"5": 0, "7": 2, "9": 2}, {"5": 1, "7": 1, "9": 0}]
demand = {"5": 150, "7": 200, "9": 300}

while True:
    duals = master_solve(patterns, demand, relax=True)
    new_pat, has_improvement = pricing(duals)
    if not has_improvement:
        break
    patterns.append(new_pat)

# Final integer solve
obj, solution = master_solve(patterns, demand, relax=False)
```

## Warm Starting

Set initial variable values to guide the solver, useful for resolve scenarios.

```python
# After first solve, save values
initial = {v.name: v.varValue for v in prob.variables()}

# Modify problem, then warm start
for v in prob.variables():
    if v.name in initial and initial[v.name] is not None:
        v.setInitialValue(initial[v.name])

prob.solve()
```

Some solvers (Gurobi, CPLEX) use warm starts natively. CBC support varies.

## Fixing Variables

Lock a variable to its current value or a specific value.

```python
# Fix to current solved value
x.fixValue()     # Sets lowBound = upBound = varValue

# Fix to a specific value
x.varValue = 5.0
x.bounds(5.0, 5.0)

# Release
x.unfixValue()   # Restores original bounds
```

Useful for sensitivity analysis ("what if x must be exactly 5?").

## Model Cloning

Create a deep copy of the model for parallel exploration.

```python
base = LpProblem("Base", LpMinimize)
# ... build model ...

variant = base.clone()
# Modify variant independently
x = variant.variables()[0]
x.bounds(0, 5)
variant.solve()
```

## Reading Models from Files

```python
from pulp import LpProblem

# Read LP file
prob = LpProblem("MyModel")
prob.read("model.lp")

# Read MPS file
prob.readMPS("model.mps")

# Solve the loaded model
prob.solve()
```

## Time Limits and Callbacks

```python
# Set time limit on solver
solver = COIN_CMD(msg=False, timeLimit=300)   # 5 minutes
status = prob.solve(solver)

# Check if solved within time limit
if LpStatus[status] == "Optimal":
    print("Optimal solution found")
else:
    print(f"Status: {LpStatus[status]} (may be cutoff by time limit)")
```

## Large-Scale Tips

- Use `lpSum()` and `lpDot()` instead of Python's `sum()` for performance
- Name constraints only when you need to retrieve them later (unnamed constraints save memory)
- For very large models, consider building the model incrementally and solving periodically
- HiGHS significantly outperforms CBC on large problems — install it if available
