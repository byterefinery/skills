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

**Base Tools** (cbc, duckdb, jq, pandoc, rqlite, yq):
```bash
mkdir -p .agents/skills-base && \
curl -L https://github.com/byterefinery/skills/archive/refs/heads/main.tar.gz | \
tar -xz --strip-components=3 -C .agents/skills-base skills-main/.agents/skills-base
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
mkdir -p .agents/skills .agents/skills-base .agents/skills-python .agents/skills-javascript && \
curl -L https://github.com/byterefinery/skills/archive/refs/heads/main.tar.gz -o "$TMP" && \
tar -xz --strip-components=2 -C .agents -f "$TMP" skills-main/.agents/skills && \
tar -xz --strip-components=2 -C .agents -f "$TMP" skills-main/.agents/skills-base && \
tar -xz --strip-components=2 -C .agents -f "$TMP" skills-main/.agents/skills-python && \
tar -xz --strip-components=2 -C .agents -f "$TMP" skills-main/.agents/skills-javascript && \
rm -f "$TMP"
```

<!-- IMPORTANT: never change after this point because it is automatically generated -->

## Skills

### General

| Skill | Description |
|-------|-------------|
| [git](.agents/skills/git/) | Git version control — commits, branches, pushing, pulling, merging, rebasing, stashing, worktrees, submodules |
| [plan](.agents/skills/plan/) | Phase/task based workflow system with PLAN.md as single source of truth |
| [skman](.agents/skills/skman/) | Scaffold, validate, and inspect agent skills (SKILL.md files) |
| [tzip](.agents/skills/tzip/) | Lightweight token-pruning communication mode that drops filler and hedging |
| [webfetch](.agents/skills/webfetch/) | Fetch web pages as markdown or HTML for LLM consumption |
| [websearch](.agents/skills/websearch/) | Search the web via DuckDuckGo and return results as markdown, CSV, or JSON |

### Base Tools

| Skill | Description |
|-------|-------------|
| [cbc-2-10-13](.agents/skills-base/cbc-2-10-13/) | COIN-OR Cbc — open-source MILP solver (branch-and-cut) |
| [duckdb-1-5-3](.agents/skills-base/duckdb-1-5-3/) | DuckDB — high-performance analytical OLAP database with embedded SQL engine |
| [jq-1-8-2](.agents/skills-base/jq-1-8-2/) | jq — lightweight command-line JSON processor |
| [pandoc-3-10](.agents/skills-base/pandoc-3-10/) | Pandoc — convert documents between formats (Markdown, HTML, LaTeX, PDF, Word, etc.) |
| [rqlite-10-2-4](.agents/skills-base/rqlite-10-2-4/) | rqlite — distributed SQLite database with Raft consensus |
| [yq-4-53-3](.agents/skills-base/yq-4-53-3/) | yq — query, transform, and convert YAML, JSON, XML, INI, TOML, HCL, CSV, TSV |

### Python Libraries

| Skill | Description |
|-------|-------------|
| [basedpyright-1-39-8](.agents/skills-python/basedpyright-1-39-8/) | basedpyright — static type checking for Python (stricter fork of pyright) |
| [duckdb-python-1-5-4](.agents/skills-python/duckdb-python-1-5-4/) | DuckDB Python client — in-process analytical SQL database API |
| [formulas-1-3-4](.agents/skills-python/formulas-1-3-4/) | formulas — evaluate Excel formulas in Python without Excel |
| [matplotlib-3-11-0](.agents/skills-python/matplotlib-3-11-0/) | Matplotlib — plotting library for data visualization |
| [networkx-3-6-1](.agents/skills-python/networkx-3-6-1/) | NetworkX — graph library for creating and analyzing complex networks |
| [numpy-2-4-6](.agents/skills-python/numpy-2-4-6/) | NumPy — core library for numerical computing (arrays, broadcasting, linear algebra) |
| [pandas-3-0-3](.agents/skills-python/pandas-3-0-3/) | Pandas — data manipulation and analysis (DataFrames, Series, time series) |
| [pulp-3-3-2](.agents/skills-python/pulp-3-3-2/) | PuLP — Python LP/MILP modeler for linear and mixed-integer programming |
| [pyomo-6-10-1](.agents/skills-python/pyomo-6-10-1/) | Pyomo — Python optimization modeling (LP, MIP, NLP, MINLP, DAE, GDP) |
| [pytest-9-1-0](.agents/skills-python/pytest-9-1-0/) | pytest — write, run, and debug Python tests with fixtures and parametrization |
| [pytest-asyncio-1-4-0](.agents/skills-python/pytest-asyncio-1-4-0/) | pytest-asyncio — test async/await code with event loops and async fixtures |
| [requests-2-34-2](.agents/skills-python/requests-2-34-2/) | requests — Python HTTP client library (REST APIs, sessions, streaming) |
| [ruff-0-15-18](.agents/skills-python/ruff-0-15-18/) | Ruff — extremely fast Python linter and code formatter written in Rust |
| [scikit-learn-1-9-0](.agents/skills-python/scikit-learn-1-9-0/) | scikit-learn — machine learning (classification, regression, clustering, pipelines) |
| [scipy-1-17-1](.agents/skills-python/scipy-1-17-1/) | SciPy — scientific Python (optimization, integration, statistics, signal processing) |
| [sqlalchemy-2-0-51](.agents/skills-python/sqlalchemy-2-0-51/) | SQLAlchemy — ORM and Core toolkit for Python database access |
| [sympy-1-14-0](.agents/skills-python/sympy-1-14-0/) | SymPy — symbolic mathematics (algebra, calculus, ODE/PDE solving, CAS) |
| [ty-0-0-51](.agents/skills-python/ty-0-0-51/) | ty — Astral's fast Python type checker (10x-100x faster than mypy/Pyright) |
| [uv-0-11-23](.agents/skills-python/uv-0-11-23/) | uv — manage Python packages, projects, scripts, tools, and versions |

### JavaScript Libraries

| Skill | Description |
|-------|-------------|
| [mermaid-11-15-0](.agents/skills-javascript/mermaid-11-15-0/) | Mermaid — diagram syntax (flowchart, sequence, state, class, gantt, ER, etc.) |
| [vega-lite-6-4-3](.agents/skills-javascript/vega-lite-6-4-3/) | Vega-Lite — high-level grammar for interactive data visualizations |

## Statistics

| Category | Count |
|----------|-------|
| General Skills | 6 |
| Base Tools | 6 |
| Python Libraries | 19 |
| JavaScript Libraries | 2 |
| **Total** | **33** |
