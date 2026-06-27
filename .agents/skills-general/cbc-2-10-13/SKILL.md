---
name: cbc-2-10-13
description: >
  COIN-OR Cbc (Coin-or Branch and Cut) 2.10.13 — open-source MILP solver.
  Use this skill whenever the user needs to solve mixed-integer linear programs,
  integer programming, MIP, branch-and-cut, branch-and-bound, or any optimization
  problem with discrete/integer variables. Covers CLI usage (`cbc` executable),
  C API (`Cbc_C_Interface.h`), and C++ API (`CbcModel`, `OsiCbcSolverInterface`).
  Also covers cut generators, heuristics, custom branching, event handlers,
  callbacks, SOS constraints, solution pools, parallel solving, AMPL interface,
  and integration with modeling languages (PuLP, cvxpy, Pyomo, JuMP, MiniZinc).
  Trigger on: MILP, MIP solver, branch-and-cut, integer programming, Cbc solver,
  COIN-OR optimization, mixed-integer optimization.
metadata:
  tags:
    - optimization
    - milp
    - coin-or
    - c++
    - c
---

# cbc 2.10.13

## Overview

Cbc (Coin-or Branch and Cut) is an open-source mixed-integer linear programming (MILP) solver written in C++. It implements branch-and-cut with configurable cut generators, heuristics, branching rules, and node selection strategies. It can be used as:

1. **Standalone CLI tool** — `cbc` executable reads MPS/LP files and solves interactively
2. **C API** — `#include <Cbc_C_Interface.h>` for C programs
3. **C++ API** — `#include <CbcModel.hpp>` for full control
4. **OsiSolverInterface** — `#include <OsiCbcSolverInterface.hpp>` as a drop-in LP solver replacement

Key capabilities: branch-and-bound with cuts (Gomory, clique, cover, probing, MIR), primal heuristics (rounding, feasibility pump, diving), SOS1/SOS2 constraints, solution pools, MIP start, parallel solving (multi-threaded and multi-process), custom cut callbacks, event handlers, and AMPL/GAMS interfaces.

## Usage

### CLI

```bash
# Solve an MPS file
cbc model.mps

# Interactive mode with parameters
cbc model.mps -solve -quit

# With time limit and other options
cbc model.mps -timeLimit 300 -logLevel 2 -solve -quit

# Read from stdin
cat model.lp | cbc -stdin
```

### C API (minimal)

```c
#include <Cbc_C_Interface.h>

Cbc_Model *model = Cbc_newModel();
Cbc_readMps(model, "model.mps");
Cbc_setMaximumSeconds(model, 300);
Cbc_solve(model);

if (Cbc_isProvenOptimal(model)) {
    double obj = Cbc_getObjValue(model);
    const double *sol = Cbc_getColSolution(model);
}
Cbc_deleteModel(model);
```

### C++ API (minimal)

```cpp
#include <OsiClpSolverInterface.hpp>
#include <CbcModel.hpp>

OsiClpSolverInterface solver;
solver.readMps("model.mps");
CbcModel model(solver);
model.branchAndBound();

if (!model.status()) {  // 0 = finished
    double obj = model.getObjValue();
    const double *sol = model.bestSolution();
}
```

### C++ API with CbcMain (full standalone solver features)

```cpp
#include <OsiClpSolverInterface.hpp>
#include <CbcModel.hpp>
#include <CbcSolver.hpp>

OsiClpSolverInterface solver;
solver.readMps("model.mps");
CbcModel model(solver);
CbcMain0(model);  // Initialize with default parameters
const char *args[] = { "prog", "-solve", "-quit" };
CbcMain1(3, args, model);
```

### OsiCbcSolverInterface (drop-in solver)

```cpp
#include <OsiCbcSolverInterface.hpp>

OsiCbcSolverInterface solver;
solver.readMps("model.mps");
solver.initialSolve();
solver.branchAndBound();
```

## Gotchas

- **Do not reuse a `CbcModel` for multiple solves** — `Cbc_solve()` and `branchAndBound()` mutate internal state. Clone the model with `Cbc_clone()` or create a new one.
- **`CbcMain0` must be called before `CbcMain1`** — `CbcMain0` initializes default parameters; skipping it means no cut generators, heuristics, or strategy setup.
- **Model access methods are invalid after solving** — `getColLower()`, `setObjCoeff()`, etc. are not valid after `Cbc_solve()` or `branchAndBound()`. Read all data before solving, or clone first.
- **Solution from solver vs model** — After `CbcMain1`, the solver is cloned internally. Use `model.solver()->getColSolution()` (current solver) or `model.bestSolution()` (best integer solution found).
- **Preprocessing loses original variable mapping** — If using `CglPreProcess`, post-process with `process.postProcess(*solver)` to map solutions back to original variables.
- **`OsiCbcSolverInterface` wraps Cbc inside Osi** — It works as a drop-in replacement for any Osi-based code, but gives less fine-grained control than `CbcModel`.
- **Parallel solving requires `CBC_THREAD` define** — Multi-threaded branch-and-bound needs the library compiled with pthread support. Use `-threads N` CLI flag or `model.setNumberThreads(N)` in C++.
- **Status codes need secondary status check** — `status() == 0` means "finished" but could be optimal or infeasible. Check `isProvenOptimal()` or `secondaryStatus()` to distinguish.
- **Cut generators must outlive the model** — When adding cut generators with `model.addCutGenerator(&gen, ...)`, the pointer is stored. Do not let the generator go out of scope during solving. Use heap allocation (`new`) for safety.
- **AMPL interface needs ASL library** — The AMPL/GMPL interface requires the Ampl Solver Library (ASL). Build with `ThirdParty-ASL` via coinbrew or install separately.

## References

- [01-installation](references/01-installation.md) — Dependencies, building from source, package managers, coinbrew
- [02-cli-reference](references/02-cli-reference.md) — Full CLI parameter reference and interactive shell
- [03-c-api](references/03-c-api.md) — C API functions, model creation, solving, solution retrieval
- [04-cpp-api-basics](references/04-cpp-api-basics.md) — CbcModel, OsiCbcSolverInterface, basic solve patterns
- [05-cpp-api-advanced](references/05-cpp-api-advanced.md) — Cut generators, heuristics, branching, callbacks, event handlers
- [06-modeling-integration](references/06-modeling-integration.md) — PuLP, cvxpy, Pyomo, JuMP, MiniZinc, AMPL, GAMS
- [07-python-usage](references/07-python-usage.md) — Detailed Python usage: PuLP, cvxpy, Pyomo, OR-Tools, python-mip, yaposib, subprocess patterns
