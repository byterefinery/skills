# skills

Skills by ByteRefinery

## Install / Update
<!-- IMPORTANT: never change this section and code block -->

**Core Skills** (git, plan, skman, tzip, webfetch, websearch):
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

**JavaScript Libraries** (daisyui, mermaid, vega-lite):
```bash
mkdir -p .agents/skills-javascript && \
curl -L https://github.com/byterefinery/skills/archive/refs/heads/main.tar.gz | \
tar -xz --strip-components=3 -C .agents/skills-javascript skills-main/.agents/skills-javascript
```

**All Skills** (install every category into a single `.agents/skills/`):
All skill categories are extracted into the same `.agents/skills/` directory, blending
Core Skills, General Tools, Python Libraries, and JavaScript Libraries together.
```bash
TMP=$(mktemp) && \
mkdir -p .agents/skills && \
curl -L https://github.com/byterefinery/skills/archive/refs/heads/main.tar.gz -o "$TMP" && \
tar -xz --strip-components=3 -C .agents/skills -f "$TMP" skills-main/.agents/skills && \
tar -xz --strip-components=3 -C .agents/skills -f "$TMP" skills-main/.agents/skills-base && \
tar -xz --strip-components=3 -C .agents/skills -f "$TMP" skills-main/.agents/skills-python && \
tar -xz --strip-components=3 -C .agents/skills -f "$TMP" skills-main/.agents/skills-javascript && \
rm -f "$TMP"
```



<!-- IMPORTANT: never change after this point because it is automatically generated -->
## Skills Table

| No | Skill | Description |
|----|-------|-------------|
| 1 | git | Git version control. Use when the user mentions git, commits, branches, pushing, pulling, merging, rebasing, stashing, worktrees, submodules, or any version control task. Covers straightforward workflows (add/commit/push) and advanced topics. |
| 2 | plan | Phase/task based workflow system with PLAN.md as single source of truth. Use when tackling projects that require structured iteration through Planning, Analysis, Design, Implementation, Testing, Deployment, Maintenance, etc phases with clear dependency graphs. |
| 3 | skman | Scaffold, validate, and inspect agent skills (SKILL.md files). Use when creating new skills, checking skill format compliance, or reviewing skill structure. |
| 4 | tzip | Lightweight token-pruning communication mode that drops filler and hedging while keeping full sentences and professional tone. Follows guidelines for code quality. Default intensity is lite. Use when user requests tzip, prune tokens, be concise, or needs efficient communication without losing clarity. |
| 5 | webfetch | Fetches web pages as markdown or HTML for LLM consumption. Use when the user wants to fetch, scrape, download, retrieve, grab, pull, or access any URL or webpage content. Supports uvx, pipx, curl, wget, and python3 fallbacks. Always impersonates Safari to avoid blocks. Use this whenever the user asks to read a website, get page content, or fetch a URL. |
| 6 | websearch | Searches the web via DuckDuckGo and returns results as markdown, CSV, or JSON. Use this skill whenever the user wants to search the web, look up information online, find URLs, do web search, research a topic, or needs current/web-based answers. |

## Statistics

- **Total Skills**: 6
