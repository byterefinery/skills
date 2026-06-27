# C API Reference

The C API is declared in `<Cbc_C_Interface.h>`. All functions take a `Cbc_Model *` pointer.

## Model Lifecycle

```c
#include <Cbc_C_Interface.h>

// Create empty model
Cbc_Model *model = Cbc_newModel();

// Read from file
int err = Cbc_readMps(model, "model.mps");  // 0 on success
int err = Cbc_readLp(model, "model.lp");

// Write model
Cbc_writeMps(model, "out.mps");
Cbc_writeLp(model, "out.lp");

// Clone model (for re-solving)
Cbc_Model *copy = Cbc_clone(model);

// Destroy
Cbc_deleteModel(model);
```

## Building a Model Programmatically

```c
Cbc_Model *model = Cbc_newModel();
Cbc_setProblemName(model, "my_problem");
Cbc_setObjSense(model, 1.0);  // 1=minimize, -1=maximize

// Add variables (columns)
Cbc_addCol(model, "x1", 0.0, 10.0, 1.0, 1 /*integer*/, 2, rows, coefs);
Cbc_addCol(model, "x2", 0.0, COIN_DBL_MAX, 2.0, 0 /*continuous*/, 0, NULL, NULL);

// Add constraints (rows)
int cols[] = {0, 1};
double coefs[] = {1.0, 2.0};
Cbc_addRow(model, "c1", 2, cols, coefs, 'L', 100.0);  // <= constraint

// Modify existing
Cbc_setColLower(model, 0, 5.0);
Cbc_setColUpper(model, 0, 15.0);
Cbc_setObjCoeff(model, 0, 3.0);
Cbc_setInteger(model, 1);       // make continuous var integer
Cbc_setContinuous(model, 0);    // make integer var continuous

// Add SOS constraints
Cbc_addSOS(model, numRows, rowStarts, colIndices, weights, type);
// type: 1=SOS1 (at most one nonzero), 2=SOS2 (at most two consecutive nonzero)
```

## Solving Parameters

```c
// Time and node limits
Cbc_setMaximumSeconds(model, 300.0);
Cbc_setMaximumNodes(model, 1000000);
Cbc_setMaximumSolutions(model, 10);

// Gap tolerances
Cbc_setAllowableGap(model, 1.0);           // absolute gap
Cbc_setAllowableFractionGap(model, 0.01);  // relative fraction (1%)
Cbc_setAllowablePercentageGap(model, 1.0); // relative percentage (1%)

// Cutoff
Cbc_setCutoff(model, 50.0);

// Log level: 0=none, 1=final, 2=factorizations, 3=more, 4=verbose
Cbc_setLogLevel(model, 2);

// Set any CLI parameter
Cbc_setParameter(model, "probing", "root");
Cbc_setParameter(model, "heuristic", "off");
```

## Solving

```c
int status = Cbc_solve(model);
// Returns: -1=before solve, 0=finished, 1=stopped (limit hit), 2=numerical issues, 5=user interrupt
```

## Solution Retrieval

```c
// Optimization status
int isOptimal = Cbc_isProvenOptimal(model);           // 1 if optimal found
int isInfeasible = Cbc_isProvenInfeasible(model);     // 1 if proven infeasible
int isAbandoned = Cbc_isAbandoned(model);             // 1 if numerical issues
int mainStatus = Cbc_status(model);                   // -1, 0, 1, 2, or 5
int secondary = Cbc_secondaryStatus(model);           // 0=optimal, 1=infeasible LP, 2=gap, 3=nodes, 4=time, 5=event, 6=solutions, 7=unbounded, 8=iteration limit

// Objective
double objValue = Cbc_getObjValue(model);             // Best feasible objective
double bestBound = Cbc_getBestPossibleObjValue(model); // Lower bound (minimization)

// Solution vector
const double *sol = Cbc_getColSolution(model);        // Current column solution
double *bestSol = Cbc_bestSolution(model);            // Best integer solution (NULL if none)

// Reduced costs
const double *redCost = Cbc_getReducedCost(model);

// Statistics
int nodes = Cbc_getNodeCount(model);
int iterations = Cbc_getIterationCount(model);
double primalInfeas = Cbc_sumPrimalInfeasibilities(model);
int numPrimalInfeas = Cbc_numberPrimalInfeasibilities(model);

// Limits reached?
Cbc_isNodeLimitReached(model);
Cbc_isSecondsLimitReached(model);
Cbc_isSolutionLimitReached(model);

// Row activities (A*x)
const double *rowAct = Cbc_getRowActivity(model);
```

## Solution Pool

```c
int nSolutions = Cbc_numberSavedSolutions(model);
for (int i = 0; i < nSolutions; i++) {
    const double *sol = Cbc_savedSolution(model, i);
    double obj = Cbc_savedSolutionObj(model, i);
}
```

## MIP Start

```c
// By variable names
const char *names[] = {"x1", "x3"};
double values[] = {1.0, 3.0};
Cbc_setMIPStart(model, 2, names, values);

// By variable indices
int indices[] = {0, 2};
double values[] = {1.0, 3.0};
Cbc_setMIPStartI(model, 2, indices, values);

// Full solution vector
Cbc_setInitialSolution(model, fullSolVector);
```

## Querying Model Data

```c
int numCols = Cbc_getNumCols(model);
int numRows = Cbc_getNumRows(model);
int numIntegers = Cbc_getNumIntegers(model);
int numElements = Cbc_getNumElements(model);
double objSense = Cbc_getObjSense(model);

// Column info
Cbc_getColName(model, i, nameBuf, maxLength);
int colNz = Cbc_getColNz(model, i);
const int *colRows = Cbc_getColIndices(model, i);
const double *colCoefs = Cbc_getColCoeffs(model, i);
Cbc_isInteger(model, i);

// Row info
Cbc_getRowName(model, i, nameBuf, maxLength);
int rowNz = Cbc_getRowNz(model, i);
const int *rowCols = Cbc_getRowIndices(model, i);
const double *rowCoefs = Cbc_getRowCoeffs(model, i);
double rhs = Cbc_getRowRHS(model, i);
char sense = Cbc_getRowSense(model, i);  // 'E', 'L', 'G', 'R'

// Matrix in CSC format
const CoinBigIndex *starts = Cbc_getVectorStarts(model);
const int *indices = Cbc_getIndices(model);
const double *values = Cbc_getElements(model);

// Bounds
const double *colLower = Cbc_getColLower(model);
const double *colUpper = Cbc_getColUpper(model);
const double *rowLower = Cbc_getRowLower(model);
const double *rowUpper = Cbc_getRowUpper(model);
const double *objCoefs = Cbc_getObjCoefficients(model);
```

## Callbacks

### Message callback

```c
void myCallback(Cbc_Model *model, int messageNumber,
    int nDouble, const double *vDouble,
    int nInt, const int *vInt,
    int nString, char **vString)
{
    // Process messages
}

Cbc_registerCallBack(model, myCallback);
// ... solve ...
Cbc_clearCallBack(model);
```

### Cut callback (add custom cuts during solving)

```c
void cutCallback(void *osiSolver, void *osiCuts, void *appData)
{
    int m = Osi_getNumRows(osiSolver);
    int n = Osi_getNumCols(osiSolver);
    const double *sol = Osi_getColSolution(osiSolver);

    // Generate cuts and add them
    int nz = 3;
    int idx[] = {0, 1, 2};
    double coef[] = {1.0, 1.0, 1.0};
    OsiCuts_addRowCut(osiCuts, nz, idx, coef, 'L', 2.0);
}

Cbc_addCutCallback(model, cutCallback, "myCut", NULL);
```

Osi helper functions available in callbacks:
- `Osi_getNumCols`, `Osi_getNumRows`
- `Osi_getColSolution`, `Osi_isInteger`
- `Osi_getColLower`, `Osi_getColUpper`
- `Osi_getRowNz`, `Osi_getRowIndices`, `Osi_getRowCoeffs`, `Osi_getRowRHS`, `Osi_getRowSense`

## Printing

```c
Cbc_printModel(model, "-");
Cbc_printSolution(model);
```
