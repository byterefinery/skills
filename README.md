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
| 1 | a2a | Agent2Agent (A2A) Protocol v1.0 — enables communication and interoperability between opaque agentic applications. Use when building A2A servers (exposing agents), A2A clients (connecting to agents), agent cards, multi-agent orchestration, or understanding how A2A complements MCP. Covers protocol data model, operations, protocol bindings (JSON-RPC, gRPC, HTTP/REST), streaming (SSE), push notifications, security, and Python SDK patterns. |
| 2 | agent-plugins-spec | Agent Plugins Specification 1.0.0 — vendor-neutral standard for packaging AI agent extensions into distributable plugins. Use when creating, validating, or implementing Agent Plugins (plugin.json manifests, skills/ discovery, mcp.json MCP servers, client extensions, PLUGIN_ROOT/PLUGIN_DATA). Covers plugin package model, component discovery, manifest schema, MCP transports, placeholder expansion, and client conformance. |
| 3 | agentskills | Agent Skills specification — the open format for extending AI agent capabilities. Use when creating, validating, or working with Agent Skills (SKILL.md files, frontmatter, progressive disclosure, skills-ref library). Covers directory structure, frontmatter fields, naming rules, validation, and best practices for portable, version-controlled agent skills. |
| 4 | do | Meta skill for direct execution. Use when the user wants something done without analysis, assumptions, or extra output. It does exactly what is asked, nothing more, nothing less. |
| 5 | git | Git version control. Use when the user mentions git, commits, branches, pushing, pulling, merging, rebasing, stashing, worktrees, submodules, or any version control task. Covers straightforward workflows (add/commit/push) and advanced topics. |
| 6 | jump | Conditional branching — jump forward or backward to a named label and resume processing from that point. Deterministic conditions (math, logic) are evaluated via on-the-fly scripts. Only vague natural-language conditions fall back to LLM judgment. |
| 7 | label | Logical time marker. Use when you need a named point of reference in the conversation that other skills or messages can anchor to. Like a label in C/C++ — a place you can jump back to. |
| 8 | markdown | Converts documents to and from Markdown. Use when the user needs to convert PDF, Word (docx), PowerPoint (pptx), OpenDocument (odt), or Excel (xlsx) files to Markdown, or convert Markdown to PDF or standalone single-file HTML. Handles formula evaluation in Excel before conversion. Supports image-to-Markdown via docling. |
| 9 | mcp | Model Context Protocol (MCP) specification reference — protocol architecture, transports, tools, resources, prompts, extensions, and message patterns. Use when building, debugging, or integrating MCP clients, servers, or SDKs. |
| 10 | okf | Creates, validates, and manages Open Knowledge Format (OKF v0.2) bundles — directory trees of markdown concept documents with YAML frontmatter. Use with the `markdown` and `webfetch` skills to preprocess PDF, Office, and web sources into markdown; then OKF extracts concepts, writes linked documents with provenance/trust/freshness/lifecycle frontmatter, and enables querying by any frontmatter field. Uses okf.py for creating, validating, visiting, and searching OKF bundles. |
| 11 | plan | Phase/task based workflow system with PLAN.md as single source of truth. Use when tackling projects that require structured iteration through Planning, Analysis, Design, Implementation, Testing, Deployment, Maintenance, etc phases with clear dependency graphs. |
| 12 | skman | Introduces the Agent Skills System — a standardized, lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows. Use for scaffolding, validating, searching, and inspecting agent skills (SKILL.md files and other skill's files and directories). |
| 13 | spr | Compress text into Sparse Priming Representations (SPR) or decompress SPRs back to full text. Supports PDF/Office input via markdown conversion. Use when the user wants to compress content into SPR format, decompress/expand SPRs, or needs token-efficient knowledge representations for LLM context. |
| 14 | tzip | Lightweight token-pruning communication mode that drops filler and hedging while keeping full sentences and professional tone. Follows guidelines for code quality. Default intensity is lite. Use when user requests tzip, prune tokens, be concise, or needs efficient communication without losing clarity. |
| 15 | webfetch | Fetches web pages as LLM-ready markdown. Use when the user wants to fetch, scrape, download, retrieve, grab, pull, or access any URL or webpage content. Defaults to Safari impersonation and AI-targeted markdown output optimized for LLM consumption. Falls back through browser → requests if needed. Supports --html, --file, --tool, --impersonate, --no-ai-targeted. Use this whenever the user asks to read a website, get page content, or fetch a URL. |
| 16 | websearch | Searches DuckDuckGo and returns LLM-optimized markdown, JSON, or YAML. Use this skill whenever the user wants to search the web, look up information online, find URLs, do web search, research a topic, or needs current/web-based answers. Uses Safari TLS impersonation and AI-targeted sanitization. Output can be markdown (default), --json, --yaml. |

## Statistics

- **Total Skills**: 16
