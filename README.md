# skills

Skills by ByteRefinery

## Install / Update
<!-- IMPORTANT: never change this section and code block -->

**General Skills** (git, plan, skman, tzip, webfetch, websearch):
```bash
mkdir -p .agents/skills && \
curl -L https://github.com/byterefinery/skills/archive/refs/heads/main.tar.gz | \
tar -xz --strip-components=3 -C .agents/skills skills-main/.agents/skills
```

**General Tools** (cbc, duckdb, jq, pandoc, rqlite, yq):
```bash
mkdir -p .agents/skills-general && \
curl -L https://github.com/byterefinery/skills/archive/refs/heads/main.tar.gz | \
tar -xz --strip-components=3 -C .agents/skills-general skills-main/.agents/skills-base
```

**Python Libraries** (basedpyright, duckdb-python, formulas, matplotlib, networkx, numpy, pandas, pulp, pyomo, pytest, pytest-asyncio, requests, ruff, scikit-learn, scipy, sqlalchemy, sympy, ty, uv):
```bash
mkdir -p .agents/skills-python && \
curl -L https://github.com/byterefinery/skills/archive/refs/heads/main.tar.gz | \
tar -xz --strip-components=3 -C .agents/skills-python skills-main/.agents/skills-python
```

**JavaScript Libraries** (mermaid, vega-lite):
```bash
mkdir -p .agents/skills-javascript && \
curl -L https://github.com/byterefinery/skills/archive/refs/heads/main.tar.gz | \
tar -xz --strip-components=3 -C .agents/skills-javascript skills-main/.agents/skills-javascript
```

**All Skills** (install every category at once):
```bash
TMP=$(mktemp) && \
mkdir -p .agents/skills .agents/skills-general .agents/skills-python .agents/skills-javascript && \
curl -L https://github.com/byterefinery/skills/archive/refs/heads/main.tar.gz -o "$TMP" && \
tar -xz --strip-components=3 -C .agents/skills -f "$TMP" skills-main/.agents/skills && \
tar -xz --strip-components=3 -C .agents/skills-general -f "$TMP" skills-main/.agents/skills-base && \
tar -xz --strip-components=3 -C .agents/skills-python -f "$TMP" skills-main/.agents/skills-python && \
tar -xz --strip-components=3 -C .agents/skills-javascript -f "$TMP" skills-main/.agents/skills-javascript && \
rm -f "$TMP"
```



<!-- IMPORTANT: never change after this point because it is automatically generated -->

## Skills

### General

Agent workflow skills for coding tasks — version control, planning, skill management, communication, and web access.

| Skill | Description |
|-------|-------------|
| [git](.agents/skills/git/) | Git version control. Use when the user mentions git, commits, branches, pushing, pulling, merging, rebasing, stashing, worktrees, submodules, or any version control task. Covers straightforward workflows (add/commit/push) and advanced topics. |
| [plan](.agents/skills/plan/) | Phase/task based workflow system with PLAN.md as single source of truth. Use when tackling projects that require structured iteration through Planning, Analysis, Design, Implementation, Testing, Deployment, Maintenance, etc phases with clear dependency graphs. |
| [skman](.agents/skills/skman/) | Scaffold, validate, and inspect agent skills (SKILL.md files). Use when creating new skills, checking skill format compliance, or reviewing skill structure. |
| [tzip](.agents/skills/tzip/) | Lightweight token-pruning communication mode that drops filler and hedging while keeping full sentences and professional tone. Follows guidelines for code quality. Default intensity is lite. Use when user requests tzip, prune tokens, be concise, or needs efficient communication without losing clarity. |
| [webfetch](.agents/skills/webfetch/) | Fetches web pages as markdown or HTML for LLM consumption. Use when the user wants to fetch, scrape, download, retrieve, grab, pull, or access any URL or webpage content. Supports uvx, pipx, curl, wget, and python3 fallbacks. Always impersonates Safari to avoid blocks. Use this whenever the user asks to read a website, get page content, or fetch a URL. |
| [websearch](.agents/skills/websearch/) | Searches the web via DuckDuckGo and returns results as markdown, CSV, or JSON. Use this skill whenever the user wants to search the web, look up information online, find URLs, do web search, research a topic, or needs current/web-based answers. |

### General Tools

General-purpose CLI tools and programs — data processing, document conversion, querying, and solvers.

| Skill | Description |
|-------|-------------|
| [cbc-2-10-13](.agents/skills-general/cbc-2-10-13/) | COIN-OR Cbc (Coin-or Branch and Cut) 2.10.13 — open-source MILP solver.
Use this skill whenever the user needs to solve mixed-integer linear programs,
integer programming, MIP, branch-and-cut, branch-and-bound, or any optimization
problem with discrete/integer variables. Covers CLI usage (`cbc` executable),
C API (`Cbc_C_Interface.h`), and C++ API (`CbcModel`, `OsiCbcSolverInterface`).
Also covers cut generators, heuristics, custom branching, event handlers,
callbacks, SOS constraints, solution pools, parallel solving, AMPL interface,
and integration with modeling languages (PuLP, cvxpy, Pyomo, JuMP, MiniZinc).
Trigger on: MILP, MIP solver, branch-and-cut, integer programming, Cbc solver,
COIN-OR optimization, mixed-integer optimization. |
| [duckdb-1-5-3](.agents/skills-general/duckdb-1-5-3/) | DuckDB 1.5.3 — high-performance analytical OLAP database with embedded SQL engine. Use this skill whenever the user queries about DuckDB, needs to run SQL analytics on local files (CSV, Parquet, Excel/XLSX), wants to install or use extensions (excel, json, icu, parquet, httpfs, delta, iceberg, postgres_scanner, sqlite_scanner, fts, spatial, and others), needs data import/export workflows, or is comparing DuckDB against other analytical databases. Covers CLI usage, Python API, extension management, Excel file handling (read/write/formatting/metadata), and the full extension ecosystem available in v1.5.3. |
| [jq-1-8-2](.agents/skills-general/jq-1-8-2/) | jq 1.8.2 — lightweight command-line JSON processor. Use when the user needs to parse, query, transform, or manipulate JSON data from the command line, process API responses, extract fields from JSON, convert between formats (JSON-to-CSV, JSON-to-XML), validate JSON, or work with any structured data in JSON format. Covers filters, builtins, regex, modules, streaming, and all jq 1.8.2 features. |
| [pandoc-3-10](.agents/skills-general/pandoc-3-10/) | Convert documents between formats using Pandoc 3.10. Use when the user mentions pandoc, document conversion, format transformation, or needs to convert between Markdown, HTML, LaTeX, PDF, Word (docx), OpenDocument (odt), PowerPoint (pptx), Excel (xlsx), CSV, TSV, EPUB, reStructuredText, Org mode, AsciiDoc, RTF, Textile, CommonMark, GFM, or any markup/format conversion task. Also use when user asks about pandoc filters, templates, defaults files, citeproc, or Lua filters. |
| [rqlite-10-2-4](.agents/skills-general/rqlite-10-2-4/) | Operate rqlite 10.2.4 — distributed SQLite database with Raft consensus.
Use for deploying, configuring, querying, backing up, and managing rqlite clusters.
Covers rqlited server flags, HTTP API (/db/execute, /db/query, /db/request),
CLI (.status, .backup, .nodes), clustering (join, DNS, Consul, etcd, Kubernetes),
TLS/mTLS auth, queued writes, CDC, consistency levels, and SQLite extensions.
Use whenever the user mentions rqlite, distributed SQLite, Raft database,
or needs a lightweight fault-tolerant relational store. |
| [yq-4-53-3](.agents/skills-general/yq-4-53-3/) | Query, transform, and convert YAML, JSON, XML, INI, TOML, HCL, CSV, TSV, Properties, Lua, Shell variables, and Base64 data using jq-like expressions. Use when the user mentions yq, YAML processing, JSON-to-YAML conversion, config file manipulation, Kubernetes YAML editing, or any structured data transformation task. Supports multi-document YAML, anchors/aliases, comments, and in-place updates. |

### Python Libraries

Python packages for data science, testing, optimization, and development tooling.

| Skill | Description |
|-------|-------------|
| [basedpyright-1-39-8](.agents/skills-python/basedpyright-1-39-8/) | Static type checking for Python via basedpyright — a fork of pyright with stricter defaults, new diagnostic rules, baseline support, pylance features in open-source, and improved CI integration. Use when the user mentions basedpyright, pyright, type checking, static analysis, type stubs, pyrightconfig, or wants to configure/resolve Python type errors. |
| [duckdb-python-1-5-4](.agents/skills-python/duckdb-python-1-5-4/) | DuckDB Python client 1.5.4 API reference and usage patterns. Use when working with the `duckdb` Python package — in-process analytical SQL database. Covers connection management, relational API (lazy evaluation), data I/O (CSV/Parquet/JSON), Python UDFs, type system, pandas/PyArrow/Polars integration, fsspec filesystems, ADBC driver, profiling, and extensions. Trigger on: duckdb, DuckDBPyConnection, DuckDBPyRelation, read_parquet, from_df, create_function, fetch_arrow_table, register_filesystem. |
| [formulas-1-3-4](.agents/skills-python/formulas-1-3-4/) | Evaluate Excel formulas in Python without Excel. Use when the user needs to compute spreadsheet formulas, calculate xlsx files, convert formula-based spreadsheets to calculated values, export Excel to CSV/JSON, run batch scenarios, build JSON models from workbooks, or serve spreadsheets as a Flask API. Also triggers on mentions of formulas package, openpyxl calculation, or spreadsheet automation. |
| [matplotlib-3-11-0](.agents/skills-python/matplotlib-3-11-0/) | Matplotlib plotting library (v3.11). Use this skill whenever the user mentions
plots, charts, graphs, figures, data visualization, matplotlib, pyplot, or
needs to create any kind of visual output from Python data — line plots, scatter
plots, bar charts, histograms, heatmaps, contour plots, subplots, legends,
colormaps, saving figures, styling, animations, or interactive widgets. Covers
both the pyplot (state-based) and object-oriented APIs. |
| [networkx-3-6-1](.agents/skills-python/networkx-3-6-1/) | Python graph library (NetworkX 3.6.1) for creating, manipulating, and analyzing complex networks.
Use this skill whenever the user works with graphs, networks, nodes, edges, shortest paths, centrality,
community detection, spanning trees, flow networks, DAGs, topological sort, graph generators,
adjacency matrices, Laplacian spectra, isomorphism, bipartite matching, or any network science task.
Triggers on: graph algorithms, network analysis, node/edge operations, Dijkstra, BFS, DFS, PageRank,
Louvain communities, connected components, minimum spanning tree, max flow, transitive closure,
and anything involving NetworkX or the `nx` module. |
| [numpy-2-4-6](.agents/skills-python/numpy-2-4-6/) | "NumPy 2.4.6: array creation, manipulation, broadcasting, ufuncs, linear algebra, statistics, random sampling, structured arrays, and I/O. Use whenever working with numerical arrays, matrices, scientific computing, data analysis, or any task involving NumPy operations. Covers ndarrays, dtype system, einsum, stride tricks, masked arrays, FFT, polynomials, and the full NumPy 2.x API." |
| [pandas-3-0-3](.agents/skills-python/pandas-3-0-3/) | Pandas 3.0.3 data manipulation and analysis library for Python. Use when working
with DataFrames, Series, data wrangling, CSV/Excel/Parquet I/O, groupby aggregations,
merging/joining, time series, resampling, rolling windows, string operations, or any
tabular data processing in Python. Covers pandas 3.0 semantics including dedicated
string dtype by default, Copy-on-Write behavior, pd.col() expressions, Arrow PyCapsule
interface, and anti-joins. Trigger on: DataFrame, Series, read_csv, merge, groupby,
pivot_table, resample, rolling, time series analysis, ETL pipelines, data cleaning,
or any mention of pandas dataframes. |
| [pulp-3-3-2](.agents/skills-python/pulp-3-3-2/) | PuLP 3.3.2 — Python LP/MILP modeler for linear, mixed-integer, and binary programming.
Use this skill whenever the user mentions optimization, linear programming (LP),
mixed-integer programming (MIP), MILP, integer programming, solver selection,
transportation problems, assignment problems, blending, scheduling, cutting stock,
Sudoku solving via MIP, column generation, stochastic programming, sensitivity analysis,
or any problem that can be expressed as minimizing/maximizing a linear objective
subject to linear constraints. Covers PuLP 3.3.2 API including `prob.add_variable()`,
`prob.add_variable_dicts()`, `prob.add_variable_matrix()`, `lpSum`, `lpDot`, solver
configuration (CBC, HiGHS, GLPK, Gurobi, CPLEX, etc.), file I/O (LP/MPS), dual values,
resolve workflows, and common modeling patterns. Install via `pip install "pulp[cbc]==3.3.2"` (the `[cbc]` extra bundles the CBC solver). |
| [pyomo-6-10-1](.agents/skills-python/pyomo-6-10-1/) | Pyomo 6.10.1 — Python optimization modeling for LP, MIP, NLP, MINLP, DAE/optimal control,
GDP (disjunctive programming), MPEC (equilibrium/complementarity), piecewise functions,
network flow, stochastic programming, and more. Use this skill whenever the user mentions
Pyomo, optimization modeling, mathematical programming, linear/nonlinear/mixed-integer
programming, optimal control, differential equations optimization, disjunctive constraints,
complementarity conditions, solver interfaces (Gurobi, CPLEX, IPOPT, GLPK, CBC, etc.),
AMPL-style modeling in Python, or building optimization models with Python. Also use when
the user asks about formulating LP/MIP/NLP models, network flow problems, facility location,
lot sizing, transportation problems, diet/nutrition problems, parameter estimation, reactor
design, job shop scheduling, or any mathematical optimization task in Python. |
| [pytest-9-1-0](.agents/skills-python/pytest-9-1-0/) | Write, run, and debug Python tests with pytest 9.1.0. Use when the user mentions pytest, writing tests, test fixtures, parametrization, test discovery, conftest.py, pytest plugins, test marks, skip/xfail, monkeypatch, tmp_path, capsys, caplog, assertion rewriting, or any Python testing task. |
| [pytest-asyncio-1-4-0](.agents/skills-python/pytest-asyncio-1-4-0/) | Test async/await code with pytest using event loops, async fixtures, and loop scopes.
Use when writing async tests, configuring asyncio mode (auto/strict), managing event loop scopes,
using @pytest.mark.asyncio, @pytest_asyncio.fixture, custom loop factories via
pytest_asyncio_loop_factories hook, port fixtures (unused_tcp_port, unused_udp_port),
testing with uvloop or other custom event loops, integrating Hypothesis with async tests,
or migrating from older pytest-asyncio versions. Covers pytest-asyncio 1.4.0+ and Python 3.10+. |
| [requests-2-34-2](.agents/skills-python/requests-2-34-2/) | Python HTTP library (requests) version 2.34.2 — sends HTTP/1.1 requests via
the high-level API (requests.get, requests.post, etc.), Session objects for
cookie/auth persistence and connection pooling, PreparedRequest for low-level
control, streaming responses, file uploads, authentication (Basic/Digest),
proxies, TLS verification, retries, and hooks. Use this skill whenever the
user works with Python HTTP clients, needs to call REST APIs, upload files,
handle sessions or cookies, configure timeouts or retries, inspect response
headers/status codes, or debug HTTP requests in Python, even if they don't
name "requests" explicitly. |
| [ruff-0-15-18](.agents/skills-python/ruff-0-15-18/) | Ruff 0.15.18 — extremely fast Python linter and code formatter written in Rust.
Use this skill whenever the user mentions ruff, linting Python, formatting Python code,
ruff check, ruff format, pyproject.toml lint config, Flake8 replacement, Black replacement,
isort replacement, or any Python code quality task involving ruff configuration, rule selection,
or CI integration. Covers `ruff check`, `ruff format`, `ruff rule`, `ruff config`,
`ruff analyze graph`, and `ruff server` (LSP). |
| [scikit-learn-1-9-0](.agents/skills-python/scikit-learn-1-9-0/) | Comprehensive guide to scikit-learn 1.9.0 — the Python machine learning library.
Use when working with ML models, pipelines, preprocessing, model selection, metrics,
or any data science task using scikit-learn. Covers classification, regression,
clustering, dimensionality reduction, ensemble methods, hyperparameter tuning,
cross-validation, feature engineering, and more. Trigger on: sklearn, scikit-learn,
machine learning, ML pipeline, model training, cross-validation, GridSearchCV,
Random Forest, SVM, logistic regression, PCA, KMeans, train_test_split, metrics. |
| [scipy-1-17-1](.agents/skills-python/scipy-1-17-1/) | SciPy (scientific Python) library reference for mathematics, science, and engineering. Covers optimization, integration, linear algebra, statistics, signal processing, FFT, interpolation, sparse matrices, spatial algorithms, special functions, image processing, clustering, I/O, and physical constants. Use when the user needs scientific computing in Python, numerical methods, data analysis with scipy, solving equations, statistical tests, Fourier transforms, ODE systems, matrix operations, or any math-heavy computation. Also triggers on mentions of scipy, SciPy, scientific Python, numerical Python, or packages like numpy/scipy together. |
| [sqlalchemy-2-0-51](.agents/skills-python/sqlalchemy-2-0-51/) | SQLAlchemy 2.0 ORM and Core toolkit for Python database access. Use this skill whenever the user
mentions SQLAlchemy, ORM models, database queries, engine creation, session management, declarative
mappings, relationships (one-to-many, many-to-many), connection pooling, async database access,
SQL expression construction, or any Python database abstraction task. Covers both Core (expression
language) and ORM layers. Supports PostgreSQL, MySQL/MariaDB, SQLite, Oracle, Microsoft SQL Server,
and third-party dialects (CockroachDB, IBM DB2, Firebird, SAP HANA, etc.). |
| [sympy-1-14-0](.agents/skills-python/sympy-1-14-0/) | Symbolic mathematics with SymPy 1.14.0 — algebra, calculus, ODE/PDE solving, matrices,
number theory, geometry, special functions, transforms, and code generation. Use when
the user needs symbolic computation, equation solving, differentiation, integration,
series expansion, matrix operations, polynomial manipulation, simplification, or any
CAS (computer algebra system) task in Python. Also use for exact arithmetic with
rationals, symbolic constants (pi, E), or converting expressions to LaTeX/C/Fortran. |
| [ty-0-0-51](.agents/skills-python/ty-0-0-51/) | Run ty (Astral's Python type checker, v0.0.51) for type checking, rule diagnostics, and language server integration. Use when the user mentions ty type checking, Python type errors, ty check, ty rules, ty suppression, migrating from mypy or pyright to ty, configuring ty.toml or pyproject.toml type checking, or setting up a Python language server. ty is 10x-100x faster than mypy/Pyright and supports intersection types, redeclarations, and reachability-based analysis. |
| [uv-0-11-23](.agents/skills-python/uv-0-11-23/) | Manages Python packages, projects, scripts, tools, and Python versions with extreme speed.
Use when the user mentions uv, python packages, pip replacement, virtual environments, venv,
pyproject.toml, dependency management, python version switching, tool installation (uvx),
script dependencies, lockfiles, workspace management, or any Python packaging task.
Replaces pip, pip-tools, pipx, poetry, pyenv, twine, and virtualenv. |

### JavaScript Libraries

JavaScript/TypeScript libraries for diagrams and data visualization.

| Skill | Description |
|-------|-------------|
| [mermaid-11-15-0](.agents/skills-javascript/mermaid-11-15-0/) | Mermaid diagram syntax reference and validation. Use when writing, debugging,
or converting Mermaid diagrams: flowchart, sequenceDiagram, stateDiagram, classDiagram,
gantt, erDiagram, pie, gitgraph, journey, mindmap, timeline, xychart, radar-beta,
quadrantChart, sankey, block, architecture-beta, c4, packet, treemap-beta, venn-beta,
wardley-beta, ishikawa-beta, kanban, requirementDiagram. |
| [vega-lite-6-4-3](.agents/skills-javascript/vega-lite-6-4-3/) | Vega-Lite is a high-level grammar for interactive graphics — a concise JSON syntax for creating
data visualizations. Use this skill whenever the user mentions Vega-Lite, chart specifications,
JSON-based charts, declarative visualization, or wants to create bar charts, line charts, scatter
plots, heatmaps, pie charts, area charts, boxplots, trellis/facet charts, layered compositions,
geographic maps, or any data visualization using the Vega-Lite specification format (v6.4.3).
Also use when the user asks about encoding channels (x, y, color, size, shape, theta, radius),
mark types, transforms, aggregations, binning, time units, selections/interactions, or embedding
Vega-Lite charts in web applications. |

## Statistics

| Category | Count |
|----------|-------|
| Core Skills | 6 |
| General Tools | 6 |
| Python Libraries | 19 |
| JavaScript Libraries | 2 |
| **Total** | **33** |
