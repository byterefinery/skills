# skills

Skills by ByteRefinery

## Install / Update
<!-- IMPORTANT: never change this section and code block -->

**Core Skills:**
```bash
mkdir -p .agents/skills && \
curl -L https://github.com/byterefinery/skills/archive/refs/heads/main.tar.gz | \
tar -xz --strip-components=3 -C .agents/skills skills-main/.agents/skills
```

**General Tools:**
```bash
mkdir -p .agents/skills-general && \
curl -L https://github.com/byterefinery/skills/archive/refs/heads/main.tar.gz | \
tar -xz --strip-components=3 -C .agents/skills-general skills-main/.agents/skills-base
```

**Python Libraries:**
```bash
mkdir -p .agents/skills-python && \
curl -L https://github.com/byterefinery/skills/archive/refs/heads/main.tar.gz | \
tar -xz --strip-components=3 -C .agents/skills-python skills-main/.agents/skills-python
```

**JavaScript Libraries:**
```bash
mkdir -p .agents/skills-javascript && \
curl -L https://github.com/byterefinery/skills/archive/refs/heads/main.tar.gz | \
tar -xz --strip-components=3 -C .agents/skills-javascript skills-main/.agents/skills-javascript
```

**All Skills:** (install every category into a single `.agents/skills/`):

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
| 2 | skman | Introduces the Agent Skills System — a standardized, lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows. Use for scaffolding, validating, and inspecting agent skills (SKILL.md files and other skill's files and directories). |
| 3 | tzip | Lightweight token-pruning communication mode that drops filler and hedging while keeping full sentences and professional tone. Follows guidelines for code quality. Default intensity is lite. Use when user requests tzip, prune tokens, be concise, or needs efficient communication without losing clarity. |
| 4 | webfetch | Fetches web pages as LLM-ready markdown. Use when the user wants to fetch, scrape, download, retrieve, grab, pull, or access any URL or webpage content. Defaults to Safari impersonation and AI-targeted markdown output optimized for LLM consumption. Falls back through browser → requests if needed. Supports --html, --file, --tool, --impersonate, --no-ai-targeted. Use this whenever the user asks to read a website, get page content, or fetch a URL. |
| 5 | websearch | Searches DuckDuckGo and returns LLM-optimized markdown, JSON, or YAML. Use this skill whenever the user wants to search the web, look up information online, find URLs, do web search, research a topic, or needs current/web-based answers. Uses Safari TLS impersonation and AI-targeted sanitization. Output can be markdown (default), --json, --yaml. |

## Statistics

- **Total Skills**: 5
