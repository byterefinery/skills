# Solvers in PuLP 4.3.1

How to find, install, and configure solvers. Source: PuLP 4.3.1 docs (`guides/how_to_configure_solvers.rst`, README).

## On this page

- [Querying available solvers](#querying-available-solvers)
- [Solver catalog](#solver-catalog)
- [Command-line vs Python API](#command-line-vs-python-api)
- [COIN_CMD (CBC)](#coin_cmd-cbc)
- [CMD solver paths and temp files](#cmd-solver-paths-and-temp-files)
- [Python API solvers](#python-api-solvers)
- [The `LpSolver_API` three-step](#the-lpsolver_api-three-step)
- [Solver-specific notes](#solver-specific-notes)
- [Environment variables](#environment-variables)
- [Exporting and importing solvers](#exporting-and-importing-solvers)

## Querying available solvers

```python
import pulp as pl

pl.listSolvers()                    # every solver PuLP knows about
pl.listSolvers(onlyAvailable=True)  # only the ones installed on this machine

solver = pl.getSolver("CPLEX_CMD")
solver = pl.getSolver("CPLEX_CMD", timeLimit=10)   # kwargs go to the constructor
```

## Solver catalog

| Solver | PuLP API(s) | Problems | How to get it |
|---|---|---|---|
| COIN-OR CBC | `COIN_CMD` | LP, MIP | `pip install pulp[cbc]` or `cbc` on PATH |
| COIN-OR Clp / Cbc | `CYLP` | LP, MIP | `pip install pulp[cylp]` (not on Windows) |
| GLPK | `GLPK_CMD`, `PYGLPK` | LP, MIP | `glpsol` on PATH / `pip install pulp[glpk]` |
| HiGHS | `HiGHS`, `HiGHS_CMD` | LP, MIP | `pip install pulp[highs]` / `pip install pulp[highs_cmd]` or `highs` on PATH |
| SCIP / FSCIP | `SCIP_PY`, `SCIP_CMD`, `FSCIP_CMD` | LP, MIP | `pip install pulp[scip]` / `scip` or `fscip` on PATH |
| OR-Tools CP-SAT | `CPSAT` | bounded integer models | `pip install pulp[ortools]` |
| OR-Tools GLOP | `GLOP` | LP | `pip install pulp[ortools]` |
| Clarabel | `CLARABEL` | LP | `pip install pulp[clarabel]` |
| CHOCO | `CHOCO_CMD` | MIP (constraint programming) | `choco-parsers-with-dependencies.jar` on PATH |
| MIPCL | `MIPCL_CMD` | LP, MIP | `mps_mipcl` on PATH |
| NVIDIA cuOpt | `CUOPT` | LP, MIP (GPU) | the `cuopt` Python package from NVIDIA |
| Gurobi | `GUROBI`, `GUROBI_CMD` | LP, MIP | `pip install pulp[gurobi]` (license needed for large models) |
| CPLEX | `CPLEX_PY`, `CPLEX_CMD` | LP, MIP | `pip install pulp[cplex]` (license needed for large models) |
| FICO Xpress | `XPRESS_PY`, `XPRESS_CMD` | LP, MIP | `pip install pulp[xpress]` (license needed for large models) |
| COPT | `COPT`, `COPT_DLL`, `COPT_CMD` | LP, MIP | `pip install pulp[copt]` (license needed for large models) |
| MOSEK | `MOSEK` | LP, MIP | `pip install pulp[mosek]` (license required) |
| SAS | `SAS94`, `SASCAS` | LP, MIP | `saspy` / `swat` and access to a SAS installation |

Convenience extras: `pulp[open_py]` installs HiGHS, SCIP, CBC, GLPK and Clarabel at once; `pulp[public_py]` installs the PyPI packages of Gurobi, COPT, Xpress and CPLEX.

## Command-line vs Python API

An API name ending in `CMD` (such as `COIN_CMD`, `CPLEX_CMD`, `GUROBI_CMD`) runs the solver's command-line interface via a temporary file. Any other name uses the solver's Python library — usually faster to initialize (no files on disk) and exposing more functionality (duals, reduced costs, extreme rays).

## COIN_CMD (CBC)

CBC is no longer bundled with PuLP. `COIN_CMD` resolves the `cbc` / `cbc.exe` binary in this order:

1. If the `cbcbox` package is installed (`python -m pip install pulp[cbc]`), the CBC binary bundled in that wheel is used.
2. Otherwise PuLP looks for `cbc` / `cbc.exe` on `PATH`.

An explicit path always works: `pl.COIN_CMD(path=r"C:\path\to\cbc.exe")`. `COIN_CMD` accepts the same arguments `PULP_CBC_CMD` did (e.g. `msg`, `timeLimit`, `keepFiles`, and `randomSeed` for reproducible solves since 4.0.1).

`HiGHS_CMD` runs the `highs` executable on `PATH` (or `path=`); the `pulp[highs_cmd]` extra provides one via `highsbox`. For HiGHS without an executable, install `pulp[highs]` and use the `HiGHS` API.

## CMD solver paths and temp files

- By default PuLP writes intermediate files (`.mps`, `.lp`, `.sol`, ...) to the OS temp directory (from `TEMP`, `TMP`, `TMPDIR`, in that order) and deletes them afterwards.
- `COIN_CMD(keepFiles=True)` writes the files in the current directory and keeps them.
- `solver.tmpDir = "/some/path"` overrides the temp directory manually.

## Python API solvers

Solvers with an official Python interface: `MOSEK`, `GUROBI`, `CPLEX_PY`, `XPRESS_PY`, `HiGHS`, `SCIP_PY`, `COPT`, `CPSAT`, `GLOP`, `CLARABEL`, `PYGLPK`, `CYLP`, `CUOPT`.

Keyword arguments a solver does not name itself (like `msg`, `path`, `timeLimit`, `keepFiles`) are handed to the solver as its own parameters. A parameter the solver does not accept raises the solver library's own error (`PulpSolverError` for `HiGHS`, whose library reports it only by status).

### CPSAT (OR-Tools CP-SAT)

Bounded integer models only:

- Every variable must have **finite** bounds (unbounded variables raise `PulpSolverError`).
- Variable names must be **unique** within the problem.
- `LpContinuous` variables are converted to integers on `[ceil(lowBound), floor(upBound)]`.
- After solving, the underlying `CpModel` is available as `prob.solverModel`.

```python
stats = prob.solve(pl.CPSAT(msg=False, timeLimit=60))
```

Optional: `warmStart=True` (pass current `varValue`s as hints), any `CpSolver.parameters` name as a keyword (e.g. `num_search_workers=8`).

### GLOP (OR-Tools GLOP)

LP only: a problem with integer variables (or SOS groups) raises `PulpSolverError` unless created with `mip=False`, which solves the LP relaxation. A solve sets `constraint.pi`, `constraint.slack`, and `variable.dj`. GLOP keeps the model between solves, so `prob.resolve()` updates it with the edits since the last solve and restarts from the previous basis — column generation and cutting planes need few pivots per round. `prob.solverModel` holds the MathOpt `Model` (`.model`), incremental solver (`.solver`), next parameters (`.params`) and last `SolveResult` (`.result`).

Optional: `timeLimit`, `threads`, `logPath`, `interrupter` (an ortools `SolveInterrupter`; `interrupt()` stops the solve with status `Interrupted`), or any MathOpt `SolveParameters` / `GlopParameters` field (e.g. `iteration_limit=1000`, `presolve=False`, `lp_algorithm="dual_simplex"`, `use_dual_simplex=True`).

Note: OR-Tools ships its own HiGHS library under the same name as `highspy`'s; when versions differ only the first loaded in a process works (PuLP loads `highspy` first, so `GLOP` may be unavailable alongside a differently built `highspy`).

### CLARABEL

LP only; integer variables raise `PulpSolverError` unless `mip=False` solves the LP relaxation. A solve sets `pi`, `slack`, `dj`. Being an interior point method it returns a point inside the optimal face (not a vertex) when the optimum is not unique; it has no warm start, so `prob.resolve()` builds the model again. `prob.solverModel` holds the Clarabel `DefaultSolver`.

Optional: `timeLimit`, `threads`, `logPath`, or any Clarabel `DefaultSettings` field (e.g. `max_iter=500`, `tol_gap_rel=1e-6`, `presolve_enable=False`). `prob.solve(solver, callback=...)` calls the callback with Clarabel's `DefaultInfo` every iteration; returning `True` stops the solve with status `Interrupted`.

### CYLP

Drives COIN-OR Clp (LP) and Cbc (MIP) through the CyLP cython bindings, without files on disk (not on Windows). Integer problems go to Cbc; `mip=False` solves the LP relaxation with Clp. After the solve, `prob.solverModel` holds a `CyCbcModel` (MIP) or `CyClpSimplex` (LP). For LPs, Clp keeps the model between solves so `prob.resolve()` only applies changes and starts from the previous basis; MIPs are built again.

Optional: `gapRel`, `gapAbs`, `threads`, `timeLimit`, `maxNodes`, `maxSolutions` (Cbc); `maxIterations`, `presolve` (Clp); `logPath`; any Clp/Cbc model attribute (e.g. `primalTolerance=1e-9`, `allowableGap=0.1`); `resolveMethod="primal"|"dual"`; `perturbation`.

### CUOPT (NVIDIA)

GPU-accelerated LP and MIP. Needs an NVIDIA GPU and the `cuopt` Python package from NVIDIA (not a PuLP extra) plus `numpy`. Optional: `timeLimit`, `gapRel`, `warmStart=True`, `logPath`, any cuOpt solver setting.

### PYGLPK

Uses the `swiglpk` package (bundles the GLPK library), so no separate GLPK install or executable: `pip install pulp[glpk]`. Talks to GLPK directly through its C API, avoiding file round-trips (unlike `GLPK_CMD`, which shells out to `glpsol`).

### GUROBI

Requires the `gurobipy` package (the `pulp[gurobi]` extra provides it from PyPI with a size-limited license). To build large models faster, also install SciPy (`pip install scipy`): with SciPy, `GUROBI` adds all constraints to the Gurobi model in a single call; without it they are added one by one (slower, same model).

### XPRESS_PY

Works with the `xpress` Python package (PyPI: `pip install xpress`; includes a runtime distribution and a free Community License with size limits). For larger models, set `XPAUTH_PATH` to the license file. Updated and tested for Xpress 9.8 (works on 9.0+). License tokens: `XPRESS` (CMD) acquires/releases a token per `model.solve()` call; `XPRESS_PY` holds a token from the moment `xpress` is imported — in batch environments use `xp.init()` as a context manager to scope it.

### SAS94 / SASCAS

Send the model to SAS Optimization procedures on a SAS 9.4 server (`saspy`) or SAS Viya/CAS (`swat`). Both need a licensed SAS installation; configure the connection as usual (`cfgname`/`cfgfile` for `SAS94`; `hostname`, `port`, `username`, `password` for `SASCAS`).

## The `LpSolver_API` three-step

Every solver with an official Python interface (subclasses of `LpSolver_API`) can be driven manually in three steps:

```python
solver = pl.CPLEX_PY()
solver.buildSolverModel(prob)          # build the native model; edit prob.solverModel here
result = solver.callSolver(prob)       # run it
status, has_solution = solver.findSolutionValues(prob, result)
```

`prob.solverModel` is set when the model is built, both after a normal `prob.solve(...)` and after a manual `buildSolverModel(prob)`.

## Solver-specific notes

- **HiGHS** — since 4.3, `createAndConfigureSolver` is part of `buildSolverModel`; `logPath` works; model is built with a single `addCols`/`addRows` call (4.0.1).
- **SCIP** — returns duals since 4.3.0.
- **MOSEK** — has a `callSolver`; its task lives in `lp.solverModel`.
- **CPSAT / CUOPT / MOSEK** — pass the `result` of `callSolver` to `findSolutionValues`.
- **PYGLPK** — `callSolver` takes `changes` instead of `warm`.
- **XPRESS_PY** — `prepare` is a keyword argument of `callSolver`.
- **CPLEX_PY** — the log file is closed after solving; LP problem type when there are no integer variables.
- Warm start (`warmStart=True`) is supported by `CPLEX_CMD`, `GUROBI_CMD`, `COIN_CMD`, `CPLEX_PY`, `GUROBI`, `XPRESS`, `XPRESS_PY` (see [03-export-and-warm-start](03-export-and-warm-start.md)).

## Environment variables

| Variable | Solver | Purpose |
|---|---|---|
| `CPLEX_HOME`, `CPO_HOME`, `LD_LIBRARY_PATH`, `PYTHONPATH` | CPLEX | where the CPLEX install, libraries and Python package live |
| `GUROBI_HOME`, `PATH`, `LD_LIBRARY_PATH` | Gurobi | where the Gurobi install and libraries live |
| `XPRESSDIR`, `PATH`, `XPAUTH_PATH` | Xpress | Xpress bin directory and license file location |

General pattern for CMD solvers: either pass an absolute `path=` to the solver constructor, or add the executable's directory to `PATH` once per machine.

## Exporting and importing solvers

A solver object exports to a dict or JSON and back — useful to back up or share a configuration:

```python
solver = pl.COIN_CMD()
solver_dict = solver.toDict()
solver.toJson("solver.json")

solver = pl.getSolverFromDict(solver_dict)
solver = pl.getSolverFromJson("solver.json")
```

The dict shape (COIN_CMD): `{'keepFiles': 0, 'mip': True, 'msg': True, 'options': [], 'solver': 'COIN_CMD', 'timeLimit': None, 'warmStart': False}`.
