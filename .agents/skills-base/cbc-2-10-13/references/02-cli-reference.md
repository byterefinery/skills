# CLI Reference

## Basic Usage

```bash
cbc [options] <file.mps|file.lp>
```

Reads MPS or LP files. Compressed files (`.gz`, `.bz2`) are supported. LP files can also be read from stdin with `-stdin`.

## Interactive Shell

Without arguments, `cbc` starts an interactive shell with readline support (if compiled with `--enable-gnu-packages`). Type parameters directly:

```
cbc
cbc> timeLimit 300
cbc> logLevel 2
cbc> model mymodel.mps
cbc> solve
cbc> quit
```

## Key Parameters

### Solving control
| Parameter | Type | Description |
|---|---|---|
| `timeLimit <secs>` | double | Maximum solving time in seconds |
| `maxNodes <n>` | int | Maximum B&B nodes to explore |
| `maxSolutions <n>` | int | Stop after finding n solutions |
| `allowableGap <g>` | double | Absolute optimality gap tolerance |
| `allowableFractionGap <f>` | double | Relative gap tolerance (fraction) |
| `allowablePercentageGap <p>` | double | Relative gap tolerance (%) |
| `cutoff <v>` | double | Stop if no solution better than this |
| `threads <n>` | int | Number of threads for parallel solving |

### Logging
| Parameter | Type | Description |
|---|---|---|
| `logLevel <n>` | int | 0=none, 1=final only, 2=factorizations, 3=more, 4=verbose |
| `printFrequency <n>` | int | Print status every n nodes |

### Preprocessing
| Parameter | Type | Description |
|---|---|---|
| `preprocess on\|off` | keyword | Enable/disable preprocessing |
| `dualReduceOn on\|off` | keyword | Dual reduction in preprocessing |
| `sosPrioritize <n>` | int | SOS prioritization mode |

### Cut generators
Each cut can be set to: `off`, `root`, `ifmove`, `forceOn`, `onglobal`

| Parameter | Description |
|---|---|
| `probing <mode>` | Probing cuts (tightens bounds) |
| `gomory <mode>` | Gomory fractional cuts |
| `gmi <mode>` | Safe Gomory mixed-integer cuts |
| `clique <mode>` | Clique cuts from set packing |
| `bkClique <mode>` | Bron-Kerbosch clique separator |
| `oddWheel <mode>` | Odd-cycle cuts with lifting |
| `twoMirc <mode>` | Two-var MIR cuts |
| `knapsackCover <mode>` | Knapsack cover cuts |
| `mirc <mode>` | Mixed-integer rounding cuts |
| `flowCover <mode>` | Flow cover cuts |
| `zeroHalfCuts <mode>` | {0, 1/2} embedding cuts |
| `reduceAndSplit <mode>` | Reduce-and-split cuts |
| `liftAndProject <mode>` | Lift-and-project cuts |
| `cgraph on\|off` | Conflict graph-based routines |
| `clqstr off\|before\|after` | Clique strengthening preprocessing |

### Heuristics
| Parameter | Description |
|---|---|
| `heuristic on\|off` | Enable/disable all heuristics |
| `feasibilityPump <mode>` | Feasibility pump heuristic |
| `rounding <mode>` | Simple rounding heuristic |
| `reduction <mode>` | Reduction-based heuristic |
| `divingCoefficient <mode>` | Dive by objective coefficient |
| `divingFractional <mode>` | Dive by fractional part |
| `divingGuided <mode>` | Guided diving heuristic |
| `divingVectorLength <mode>` | Dive by reduced cost vector length |
| `divingPseudoCost <mode>` | Dive using pseudo costs |
| `divingLineSearch <mode>` | Line search diving |
| `localSearch <mode>` | Local search around incumbent |
| `proximity on\|off` | Proximity search (0-1 MIP refinement) |
| `pseudoCost <mode>` | Pseudo-cost branching heuristic |
| `fathom <mode>` | Fathom-on-heuristic solution |

### Branching
| Parameter | Description |
|---|---|
| `numberStrong <n>` | Variables to strong-branch (0=off) |
| `pseudoCostRatio <r>` | Pseudo-cost vs reduced cost weight (0-1) |
| `largeScale <n>` | Large-scale branching threshold |
| `bigMBranching on\|off` | Specialized branching for big-M constraints |

### Miscellaneous
| Parameter | Description |
|---|---|
| `mipStart <file>` | Read initial feasible solution from file |
| `writeMps <file>` | Write model to MPS file |
| `writeLp <file>` | Write model to LP file |
| `solutionPool on\|off` | Enable solution pool |
| `maximumSavedSolutions <n>` | Number of solutions to save (default 1) |
| `randomSeed <n>` | Set random seed (0=time-based) |
| `multipleRootPasses <n>` | Multiple root solves with different seeds |
| `constraint conflict\|off` | Enable conflict cuts |
| `guess` | Auto-tune LP parameters for model properties |
| `slowCutPasses <n>` | Passes for expensive cut generators (default 10) |

## Actions

| Action | Description |
|---|---|
| `model <file>` | Load MPS/LP file |
| `solve` | Solve the loaded model |
| `quit` | Exit interactive mode |
| `help` | Show available parameters and actions |
| `display` | Display current parameter values |

## Example Commands

```bash
# Quick solve with defaults
cbc model.mps -solve -quit

# 5-minute time limit, verbose output
cbc model.mps -timeLimit 300 -logLevel 4 -solve -quit

# Disable heuristics, enable all cuts at root
cbc model.mps -heuristic off -probing root -gomory root -clique root -solve -quit

# Parallel solving with 8 threads
cbc model.mps -threads 8 -timeLimit 600 -solve -quit

# Use MIP start file
cbc model.mps -mipStart start.sol -solve -quit

# Save solution pool
cbc model.mps -solutionPool on -maximumSavedSolutions 10 -solve -quit
```
