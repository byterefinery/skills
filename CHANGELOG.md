# Changelog

All notable changes to this project will be documented in this file.

## 2026-06-28 — skman: Remove Trigger Terminology, README Cleanup

### Changed
- **skman** SKILL.md removed all references to "trigger terms" and "under-triggering"
  from description writing guidelines. Replaced with neutral guidance: descriptions
  should be specific and include relevant context (file extensions, tool names,
  task types) so the agent knows when to apply the skill
- Progressive Disclosure section rewritten to avoid implementation details about
  how skills are triggered; metadata is now described as "always visible to the
  agent" and SKILL.md body as "loaded on demand"
- **README** install section cleaned up: removed inline skill name lists from
  category headers (e.g. `Core Skills (git, plan, …)` → `Core Skills:`), added
  clarifying prose for the All Skills installation method, and trimmed trailing
  blank lines

## 2026-06-27 — README and Install Fixes

### Changed
- Renamed **Base Tools** category to **General Tools** (directory: `skills-base` → `skills-general`)
- Install commands: each category now extracts to its own directory matching repo
  structure (`skills`, `skills-general`, `skills-python`, `skills-javascript`) instead
  of all extracting into flat `.agents/skills/`
- Skills table regenerated from SKILL.md frontmatter with full descriptions (proper
  YAML block scalar parsing) and category description paragraphs
- Skill links updated to use correct category paths

### Fixed
- Install command mkdir/tar mismatch: `mkdir` created category directory but `tar`
  extracted into `.agents/skills/` (non-existent for that category), causing failures
- YAML block scalar descriptions (`>` multiline) showing as literal `"\>"` in table
- Stale skill table links pointing to wrong directories

## 2026-06-27 — Initial Release

### Added

#### General Skills
- **git** — Git version control with conventional commits, worktrees, submodules, and advanced workflows
- **plan** — Phase/task based workflow system with PLAN.md as single source of truth
- **skman** — Scaffold, validate, and inspect agent skills (SKILL.md files)
- **tzip** — Lightweight token-pruning communication mode for concise agent responses
- **webfetch** — Fetch web pages as markdown or HTML for LLM consumption
- **websearch** — Web search via DuckDuckGo returning markdown, CSV, or JSON

#### Base Tools
- **cbc-2-10-13** — COIN-OR Cbc open-source MILP solver (branch-and-cut)
- **duckdb-1-5-3** — High-performance analytical OLAP database with embedded SQL engine
- **jq-1-8-2** — Lightweight command-line JSON processor
- **pandoc-3-10** — Universal document converter (Markdown, HTML, LaTeX, PDF, Word, etc.)
- **rqlite-10-2-4** — Distributed SQLite database with Raft consensus
- **yq-4-53-3** — YAML/JSON/XML/TOML/INI processor using jq-like expressions

#### Python Libraries
- **basedpyright-1-39-8** — Static type checking for Python (stricter fork of pyright)
- **duckdb-python-1-5-4** — DuckDB Python client API reference and usage patterns
- **formulas-1-3-4** — Evaluate Excel formulas in Python without Excel
- **matplotlib-3-11-0** — Plotting library for data visualization (pyplot and OOP APIs)
- **networkx-3-6-1** — Graph library for creating, manipulating, and analyzing complex networks
- **numpy-2-4-6** — Core library for numerical computing in Python (ndarrays, broadcasting, linear algebra)
- **pandas-3-0-3** — Data manipulation and analysis library (DataFrames, Series, time series)
- **pulp-3-3-2** — Python LP/MILP modeler for linear and mixed-integer programming
- **pyomo-6-10-1** — Python optimization modeling (LP, MIP, NLP, MINLP, DAE, GDP)
- **pytest-9-1-0** — Write, run, and debug Python tests with fixtures and parametrization
- **pytest-asyncio-1-4-0** — Test async/await code with pytest using event loops and async fixtures
- **requests-2-34-2** — Python HTTP client library (REST APIs, sessions, streaming)
- **ruff-0-15-18** — Extremely fast Python linter and code formatter written in Rust
- **scikit-learn-1-9-0** — Machine learning library (classification, regression, clustering, pipelines)
- **scipy-1-17-1** — Scientific Python library (optimization, integration, statistics, signal processing)
- **sqlalchemy-2-0-51** — ORM and Core toolkit for Python database access
- **sympy-1-14-0** — Symbolic mathematics (algebra, calculus, ODE/PDE solving, CAS)
- **ty-0-0-51** — Astral's fast Python type checker (10x-100x faster than mypy/Pyright)
- **uv-0-11-23** — Manages Python packages, projects, scripts, tools, and versions with extreme speed

#### JavaScript Libraries
- **mermaid-11-15-0** — Diagram syntax reference (flowchart, sequence, state, class, gantt, ER, etc.)
- **vega-lite-6-4-3** — High-level grammar for interactive data visualizations

### Statistics
- **General Skills**: 6
- **Base Tools**: 6
- **JavaScript Libraries**: 2
- **Python Libraries**: 19
- **Total Skills**: 33
