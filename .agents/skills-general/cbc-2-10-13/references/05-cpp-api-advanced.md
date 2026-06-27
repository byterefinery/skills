# C++ API Advanced Features

## Cut Generators

Cut generators are from the Cgl library. Add them to the model:

```cpp
#include <CglProbing.hpp>
#include <CglGomory.hpp>
#include <CglKnapsackCover.hpp>
#include <CglRedSplit.hpp>
#include <CglClique.hpp>
#include <CglFlowCover.hpp>
#include <CglMixedIntegerRounding2.hpp>

// Probing cuts (tighten bounds from constraint propagation)
CglProbing probe;
probe.setUsingObjective(true);
probe.setMaxPass(1);
probe.setMaxPassRoot(5);
probe.setMaxProbe(10);
probe.setMaxProbeRoot(1000);
probe.setMaxLook(50);
probe.setMaxLookRoot(500);
model.addCutGenerator(&probe, -1, "Probing");

// Gomory fractional cuts
CglGomory gomory;
gomory.setLimit(300);
model.addCutGenerator(&gomory, -1, "Gomory");

// Knapsack cover cuts
CglKnapsackCover knapsack;
model.addCutGenerator(&knapsack, -1, "Knapsack");

// Clique cuts (from set-packing constraints)
CglClique clique;
clique.setStarCliqueReport(false);
model.addCutGenerator(&clique, -1, "Clique");

// Mixed-integer rounding cuts
CglMixedIntegerRounding2 mir;
model.addCutGenerator(&mir, -1, "MIR");

// Flow cover cuts
CglFlowCover flow;
model.addCutGenerator(&flow, -1, "FlowCover");

// Reduce-and-split cuts
CglRedSplit redsplit;
redsplit.setLimit(200);
model.addCutGenerator(&redsplit, -1, "RedSplit");
```

The frequency parameter (second arg) controls when cuts are generated:
- `-1` — every node
- `-99` — only at root
- `N` — every N nodes

**Important:** Cut generator pointers are stored by reference. Allocate on heap if they must outlive the local scope:

```cpp
model.addCutGenerator(new CglProbing(), -1, "Probing");
// Model takes ownership; do not delete separately
```

## Heuristics

Primal heuristics find feasible integer solutions during search:

```cpp
#include <CbcHeuristic.hpp>
#include <CbcHeuristicLocal.hpp>
#include <CbcHeuristicRound.hpp>
#include <CbcHeuristicDiveCoefficient.hpp>
#include <CbcHeuristicDiveFractional.hpp>
#include <CbcHeuristicDiveGuided.hpp>
#include <CbcHeuristicDiveVectorLength.hpp>
#include <CbcHeuristicDivePseudoCost.hpp>
#include <CbcHeuristicDiveLineSearch.hpp>

// Rounding heuristic (simple round-to-nearest)
CbcRounding rounding(model);
model.addHeuristic(&rounding);

// Local search around incumbent
CbcHeuristicLocal local(model);
model.addHeuristic(&local);

// Feasibility pump
CbcFeasibilityPump fp(model);
fp.setWhen(3);  // Run when no solution found
model.addHeuristic(&fp);

// Diving heuristics
CbcHeuristicDiveCoefficient diveCoeff(model);
diveCoeff.setWhen(3);           // 1=always, 2=at root, 3=no solution
diveCoeff.setMaxIterations(150);
model.addHeuristic(&diveCoeff);

CbcHeuristicDiveFractional diveFrac(model);
diveFrac.setWhen(3);
model.addHeuristic(&diveFrac);

CbcHeuristicDiveGuided diveGuided(model);
diveGuided.setWhen(3);
model.addHeuristic(&diveGuided);
```

`setWhen()` values: `1`=always, `2`=at root only, `3`=when no incumbent exists.

## Branching Methods

### Default Branching

Default uses pseudo-costs and reduced costs to select branching variables. Customize:

```cpp
model.setNumberStrong(10);       // Strong-branch 10 variables
model.setNumberBeforeTrust(5);   // Trust pseudo-costs after 5 branches
model.setMinimumDrop(1e-4);      // Minimum dual reduction to consider
```

### User Branching Comparison

Control node selection order:

```cpp
#include <CbcCompareUser.hpp>

CbcCompareUser compare;
model.setNodeComparison(compare);
```

Or implement custom comparison by subclassing `CbcCompareActual`:

```cpp
class MyCompare : public CbcCompareActual {
public:
    virtual int operator()(const CbcNode *first, const CbcNode *second) const {
        // Return >0 if first is better, <0 if second is better
        // Use first->objectiveValue(), first->numberInfeasible() etc.
    }
};
```

### Custom Branching Rule

Subclass `CbcBranchUserBase` to implement custom branching logic:

```cpp
#include <CbcBranchUser.hpp>

class MyBranchingRule : public CbcBranchUserBase {
public:
    // Required overrides
    virtual int wayToBranch(const OsiBranchingInformation *info) const;
    virtual double estimateInfeasibility(const OsiBranchingInformation *info,
                                          CbcObject **bestObjects,
                                          int &numberInfeasibleIntegers) const;
    virtual void setupStrongInfo(const CbcModel *model,
                                  const OsiBranchingInformation *info);
    virtual void strongBranch(CbcModel *model,
                               const OsiBranchingInformation *info,
                               CbcObject **bestObjects,
                               int &numberInfeasibleIntegers) const;
};
```

Register with model:
```cpp
MyBranchingRule branch;
model.setBranchingMethod(&branch);
```

## Custom Objects

Create custom branching objects by subclassing `CbcObject`:

```cpp
#include <CbcObject.hpp>
#include <CbcSimpleInteger.hpp>

class MyInteger : public CbcSimpleInteger {
public:
    MyInteger(CbcModel *model, int sequence)
        : CbcSimpleInteger(model, sequence) {}

    virtual double infeasibility(const OsiBranchingInformation *info,
                                  int &preferredWay) const;
    virtual CbcBranchingObject *createCbcBranch(
        OsiSolverInterface *solver,
        const OsiBranchingInformation *info,
        int way);
};

// Add to model
MyInteger obj(&model, columnSequence);
model.addObject(&obj);
```

## SOS Constraints

```cpp
#include <CbcSOS.hpp>

int members[] = {0, 1, 2, 3, 4};
double weights[] = {1.0, 2.0, 3.0, 4.0, 5.0};
int priority = 0;  // Branching priority (lower = higher priority)

// SOS1: at most one nonzero
CbcSOS sos1(&model, 5, members, weights, priority, 1);
model.addObject(&sos1);

// SOS2: at most two consecutive nonzero
CbcSOS sos2(&model, 5, members, weights, priority, 2);
model.addObject(&sos2);
```

## Callbacks (C++ style)

### Node Callback

Called at each phase of solving:

```cpp
static int myCallback(CbcModel *model, int whereFrom)
{
    // whereFrom:
    //   1 = after initial LP solve
    //   2 = after preprocessing
    //   3 = just before branchAndBound (override settings)
    //   4 = just after branchAndBound (before postprocessing)
    //   5 = after postprocessing
    return 0;  // Return non-zero to abort early
}

CbcMain1(argc, argv, model, myCallback);
```

Use callback at phase 3 to add heuristics or modify strategy:
```cpp
case 3: {
    CbcHeuristicDiveCoefficient heuristic(*model);
    heuristic.setWhen(3);
    model->addHeuristic(&heuristic);
} break;
```

## Event Handlers

Trap events during solving (new solutions, cuts generated, etc.):

```cpp
#include <CbcEventHandler.hpp>

class MyEventHandler : public CbcEventHandler {
public:
    virtual CbcAction event(CbcEvent whichEvent) {
        if (!model_->parentModel()) {  // Only in main tree
            switch (whichEvent) {
                case solution:
                    printf("New incumbent: obj = %g\n", model_->getObjValue());
                    break;
                case heuristicSolution:
                    printf("Heuristic solution: obj = %g\n", model_->getObjValue());
                    break;
                case generatedCuts:
                    // Cuts were added
                    break;
                case nodeFactorization:
                    // Node LP was factorized
                    break;
                default:
                    break;
            }
        }
        return noAction;  // Continue solving
        // Return stop to abort, skipNode to prune current node
    }

    virtual CbcEventHandler *clone() const {
        return new MyEventHandler(*this);
    }
};

// Register
MyEventHandler handler;
model.passInEventHandler(&handler);
```

CbcAction values: `noAction` (continue), `stop` (abort solving), `skipNode` (prune node).

## Preprocessing

```cpp
#include <CglPreProcess.hpp>

CglPreProcess process;
OsiSolverInterface *reduced = process.preProcess(solver, false, 5);
// false = don't find equality cliques, 5 = max passes

if (!reduced) {
    // Preprocessing detected infeasibility
}
reduced->resolve();

// ... solve with CbcModel(*reduced) ...

// Post-process to map solution back
process.postProcess(*model.solver());
```

## Parallel Solving

### Multi-threaded (within single CbcModel)

Requires library compiled with `CBC_THREAD`:

```cpp
model.setNumberThreads(4);
model.branchAndBound();
```

Or via CLI: `cbc model.mps -threads 4`

### Multi-process (multiple CbcModels)

Run multiple models in parallel using threads or processes:

```cpp
#include <pthread.h>

typedef struct {
    CbcModel *model;
    CbcSolverUsefulData *data;
} threadInfo;

void *solveThread(void *arg) {
    threadInfo *info = (threadInfo *)arg;
    CbcMain0(*info->model, *info->data);
    CbcMain1(argc, argv, *info->model, callback, *info->data);
    return NULL;
}

// Create multiple models and solve in parallel
CbcModel models[3];
pthread_t threads[3];
for (int i = 0; i < 3; i++) {
    pthread_create(&threads[i], NULL, solveThread, &info[i]);
}
for (int i = 0; i < 3; i++) {
    pthread_join(threads[i], NULL);
}
```

## CbcMain Interface

`CbcMain0` and `CbcMain1` replicate the standalone solver behavior:

```cpp
#include <CbcSolver.hpp>

CbcSolverUsefulData cbcData;
cbcData.noPrinting_ = false;
#ifndef CBC_NO_INTERRUPT
cbcData.useSignalHandler_ = true;
#endif

// Initialize defaults
CbcMain0(model, cbcData);

// Solve with CLI-style arguments
const char *args[] = { "prog", "-timeLimit", "300", "-solve", "-quit" };
CbcMain1(5, args, model, callback, cbcData);
```

`CbcMain1` supports all the same parameters as the CLI. Add `-quit` to ensure it exits after solving.

## ClpEventHandler (for LP-level events)

When using Clp as the LP solver, trap LP-level events:

```cpp
#include <ClpEventHandler.hpp>

class MyClpHandler : public ClpEventHandler {
public:
    virtual int event(Event whichEvent) {
        if (whichEvent == presolveAfterFirstSolve)
            return -2;  // Skip cleanup after postsolve
        return -1;  // Continue
    }
};

ClpSimplex *clp = solver.getModelPtr();
MyClpHandler handler(clp);
clp->passInEventHandler(&handler);
```
