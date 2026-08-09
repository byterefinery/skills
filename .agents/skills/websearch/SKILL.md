---
name: websearch
description: Searches the web via multiple search engines and returns LLM-optimized markdown, JSON, or YAML. Use this skill whenever the user wants to search the web, look up information online, find URLs, do web search, research a topic, or needs current/web-based answers. Searches all engines by default, deduplicates results, uses Safari impersonation and AI-targeted sanitization. Supports DuckDuckGo, Brave, Mojeek, Startpage, and Qwant.
license: Apache-2.0
compatibility: Requires uv installed. Script auto-resolves dependencies via PEP 723.
metadata:
  tags:
    - web
    - search
    - discovery
---

# websearch

## Overview

Search the web via multiple privacy-focused search engines and return LLM-optimized results.

**Defaults** (no flags needed):
- **DuckDuckGo HTML** — GET method, clean HTML, reliable results. DuckDuckGo Lite excluded (same index). Use `--engine duckduckgo-lite` explicitly.
- **Stealth fetching** — `scrapling.Fetcher` with `impersonate="safari"` + `stealthy_headers=True` (TLS fingerprint + browser-like headers), falls back to requests
- **1-hour result cache** — caches results in `$TMPDIR/websearch-cache/` by query hash. Same query within an hour returns cached results instantly, avoiding rate-limiting
- **AI-targeted markdown** — strips scripts, styles, hidden elements, zero-width chars; converts snippets via `markdownify`
- **Markdown output** — clean, structured, ready for LLM context

Output: **markdown** (default), use `--json` or `--yaml` for other formats.

## Usage

```bash
# Search all engines, markdown output
websearch.py "react hooks tutorial"

# Comma-separated engines with aliases
websearch.py "python async patterns" --engine ddg,brave
websearch.py "llm frameworks" --engine ddg-html,mojeek,startpage
websearch.py "web scraping" --engine ddg-lite,qwant --yaml

# JSON output
websearch.py "web scraping tools" --json

# YAML to file
websearch.py "rust async runtime" --yaml -o results.yaml

# Skip AI sanitization (rarely needed)
websearch.py "raw html content" --no-ai-targeted
```

### Engines

| Engine | Index | Reliability |
|---|---|---|
| `duckduckgo-html` | Google-backed | **High** — GET method, clean HTML, best results |
| `duckduckgo-lite` | Same | **High** — same index as HTML, excluded from default, use explicitly |

DuckDuckGo is the only reliable engine for automated scraping. Others (Brave, Mojeek, Startpage, Qwant, SearXNG) consistently return challenges, 403s, or empty results.

Uses `scrapling.Fetcher` with `impersonate="safari"` + `stealthy_headers=True`. Cache (1h) avoids re-hitting same query.

## Gotchas

- **DDG HTML uses POST** — `POST /html/` with `Content-Type: application/x-www-form-urlencoded` avoids CAPTCHAs that GET triggers. The Referer header is mandatory.
- **DDG Lite also uses POST** — GET returns only the search form. POST to `/lite/` with `q=query` body. Uses single-quoted class attributes (`class='result-link'`).
- **DDG rate-limits aggressively** — returns HTTP 202 + challenge page when blocked. The script silently skips challenged engines. Space requests 30+ seconds apart.
- **Only DDG engines reliably work** — Brave (429), Mojeek (403), Startpage (challenges), and Qwant (SPA) rarely return parseable results via simple HTTP. The multi-engine search is included for completeness; expect ~10 results from DDG.
- **All engines are searched by default** — results are deduplicated by normalized URL. Use `--engine` to target specific ones.
- **Engines that return challenges are silently skipped** — no error output, just fewer results. This keeps the output clean.
- **Brave and Qwant are JS-heavy** — the regex parser may return fewer results or miss results entirely on these engines.
- **These are public websites, not APIs** — heavy use will trigger rate limits or CAPTCHAs. The script adds stealth headers but cannot guarantee unlimited access.
- **Results limited to one page per engine** — no pagination. Use specific queries to surface relevant results.
- **`--no-ai-targeted` disables sanitization** — only use if you need raw HTML content in snippets. Default AI-targeted mode strips noise for LLM consumption.
