# C++ API Basics

## CbcModel — Primary Interface

`CbcModel` wraps an `OsiSolverInterface` (typically `OsiClpSolverInterface`) and adds branch-and-cut.

### Construction

```cpp
#include <OsiClpSolverInterface.hpp>
#include <CbcModel.hpp>

// From solver (clones the solver internally)
OsiClpSolverInterface solver;
solver.readMps("model.mps");
CbcModel model(solver);

// Default constructor (build model manually)
CbcModel model;
```

### Solving

```cpp
// Simple solve with defaults
model.branchAndBound();

// With initial solve to continuous first
model.initialSolve();
model.branchAndBound();

// Using CbcMain (full standalone solver features)
#include <CbcSolver.hpp>
CbcMain0(model);           // Initialize default parameters
CbcMain1(argc, argv, model);  // Parse CLI args and solve
```

### Parameters

```cpp
// Double parameters
model.setDblParam(CbcModel::CbcMaximumSeconds, 300.0);
model.setDblParam(CbcModel::CbcAllowableGap, 1.0);
model.setDblParam(CbcModel::CbcIntegerTolerance, 1e-5);
model.setDblParam(CbcModel::CbcMinimumDrop, 1e-4);

// Integer parameters
model.setIntParam(CbcModel::CbcMaximumNodes, 1000000);
model.setIntParam(CbcModel::CbcMaximumSolutions, 10);
model.setIntParam(CbcModel::CbcNumberStrong, 5);
model.setIntParam(CbcModel::CbcLogLevel, 2);

// Query
double val = model.getDblParam(CbcModel::CbcMaximumSeconds);
int nodes = model.getIntParam(CbcModel::CbcMaximumNodes);
```

### Results

```cpp
// Status: -1=before solve, 0=finished, 1=stopped, 2=abandoned, 5=event
int status = model.status();

// Secondary status: 0=optimal, 1=infeasible LP, 2=gap, 3=nodes, 4=time, 5=event, 6=solutions, 7=unbounded, 8=iteration limit
int secondary = model.secondaryStatus();

// Boolean checks
bool optimal = model.isProvenOptimal();
bool infeasible = model.isProvenInfeasible();

// Objective values
double objValue = model.getObjValue();              // Best feasible objective (sign depends on sense)
double minObj = model.getMinimizationObjValue();    // Always positive for minimization
double continuousObj = model.getContinuousObjective();  // LP relaxation objective
double rootAfterCuts = model.rootObjectiveAfterCuts();  // After root-node cuts

// Solution
const double *sol = model.bestSolution();  // NULL if no integer solution found
const double *colSol = model.solver()->getColSolution();  // Current LP solution

// Statistics
int nodes = model.getNodeCount();
int iterations = model.getIterationCount();
```

### Model Info

```cpp
int numCols = model.getNumCols();
int numRows = model.getNumRows();
int numIntegers = model.numberIntegers();
int numObjects = model.numberObjects();

// Access underlying solver
OsiSolverInterface *solver = model.solver();
const double *colLower = solver->getColLower();
const double *colUpper = solver->getColUpper();
const double *objCoefs = solver->getObjCoefficients();

// Post-processed solver (after presolve)
const OsiSolverInterface *pps = model.postProcessedSolver(1);
```

## OsiCbcSolverInterface — Drop-in Solver

Use when you want Cbc as a transparent replacement for any Osi-based code:

```cpp
#include <OsiCbcSolverInterface.hpp>

// Basic usage (cuts at root only)
OsiCbcSolverInterface solver;
solver.readMps("model.mps");
solver.initialSolve();
solver.branchAndBound();

// With custom strategy (cuts in tree)
CbcStrategyDefault strategy(false);  // false = cuts everywhere
OsiCbcSolverInterface solver(NULL, &strategy);
solver.readMps("model.mps");
solver.branchAndBound();

// Access results
double obj = solver.getObjValue();
int nodes = solver.getNodeCount();
const double *sol = solver.getColSolution();
```

## CbcStrategyDefault

Controls default setup of cut generators, heuristics, and branching:

```cpp
// Constructor: cutsOnlyAtRoot, numberStrong, numberBeforeTrust
CbcStrategyDefault strategy(true, 5, 0);

// Preprocessing
strategy.setupPreProcessing(2);  // 0=off, 1=basic, 2=SOS detection

model.setStrategy(strategy);
```

Parameters:
- `cutsOnlyAtRoot` — if true, cuts only at root node
- `numberStrong` — variables to strong-branch (default 5)
- `numberBeforeTrust` — nodes before trusting pseudo-costs (default 0)

## File I/O

```cpp
// Read
solver.readMps("model.mps", "");    // Second arg: file extension override
solver.readLp("model.lp", 1e-10);   // Second arg: zero tolerance

// Write
solver.writeMps("out.mps");
solver.writeLp("out.lp");
```

## MIP Start

```cpp
// Set initial feasible solution
int count = 3;
const char *names[] = {"x1", "x2", "x3"};
double values[] = {1.0, 0.0, 3.0};
model.setMIPStart(count, names, values);

// By indices
int indices[] = {0, 1, 2};
model.setMIPStartI(count, indices, values);

// Full solution vector
model.setInitialSolution(fullSolVector);
```

## Solution Pool

```cpp
model.setMaximumSavedSolutions(10);
model.branchAndBound();

int nSolutions = model.numberSavedSolutions();
for (int i = 0; i < nSolutions; i++) {
    const double *sol = model.savedSolution(i);
    double obj = model.savedObjective(i);
}
```

## Logging

```cpp
model.messageHandler()->setLogLevel(2);
model.solver()->messageHandler()->setLogLevel(0);  // Suppress LP solver output
```

Log levels: 0=none, 1=final only, 2=factorizations, 3=more detail, 4=verbose.
