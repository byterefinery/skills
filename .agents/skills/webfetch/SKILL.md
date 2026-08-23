---
name: webfetch
description: Fetches web pages as LLM-ready markdown. Use when the user wants to fetch, scrape, download, retrieve, grab, pull, or access any URL or webpage content. Defaults to Safari impersonation and AI-targeted markdown output optimized for LLM consumption. Falls back through browser → requests if needed. Supports --html, --file, --tool, --impersonate, --no-ai-targeted. Use this whenever the user asks to read a website, get page content, or fetch a URL.
license: Apache-2.0
compatibility: Requires uv installed. Script auto-resolves dependencies via PEP 723.
metadata:
  tags:
    - web
    - scraping
    - fetch
---

# webfetch

## Overview

Fetches a web page and returns its content as clean markdown (default) or raw HTML, sanitized for LLM consumption.

One script does everything. You do not write any code — you run one bash command with the URL, and the command's stdout (or the file you named) is the page content.

## Usage

The script is `scripts/webfetch.py`, in the `scripts/` folder of this skill. The skill's directory is printed in the header above this text (the line `References are relative to <dir>`).

**Step 1 — Read the user's request, then pick the flags:**

- plain page content → no extra flags
- raw HTML or "HTML source" → add `--html`
- save to a file → add `--file <path>`
- "without sanitization" or unfiltered content → add `--no-ai-targeted`
- a specific fetcher (scrapling, browser, requests) → add `--tool <name>`
- impersonating chrome or firefox → add `--impersonate <name>`

Combine flags when the request needs several (e.g. `--html --file /abs/path.html`).

**Step 2 — Run exactly one bash command (no `cd`, from wherever you are):**

```bash
uv run --script /home/mtasic/projects-b/skills/.agents/skills/webfetch/scripts/webfetch.py <flags> https://example.com
```

The script path is the skill's directory from the header plus `scripts/webfetch.py` — copy that full path exactly into every command. Replace `<flags>` with the flags from step 1 (leave it out when none), and replace the URL.

**Step 3 — Get the content:**

- without `--file`: the bash tool result (stdout) is the content. Answer the user's question from it. Done — there is no output file and nothing else to do.
- with `--file`: the command prints nothing. That is normal, not an error — the content went into the file. `read` the file, then answer. The file is created in the current working directory (the user's project), not in the skill's directory: `--file ./tangled.md` lands in the project root.

Use `--file` (not a `>` redirect) when the user asks to save to a file.

## Gotchas

- **Do not read the script to learn how to use it** — the steps above are all you need. `read scripts/webfetch.py` wastes a turn; run it with the URL.
- **Do not run `python webfetch.py` or `python3 webfetch.py` directly** — the script needs packages (`scrapling`, `markdownify`, `requests`) that are not on the system Python. Plain python either crashes on import or silently falls back to a worse fetcher. Always use `uv run --script`; it resolves the dependencies declared in the file automatically.
- **Do not install anything** — no `pip install`, no venv, no `requirements.txt`. `uv run --script` handles dependencies.
- **Do not search for the script** — no `which webfetch.py`, no `find`. Its full path is the skill's directory (from the header) plus `scripts/webfetch.py`. If the command fails with a missing file, you mistyped the path — copy it exactly from the command example above and retry; do not search.
- **Fetch once, with the right flags** — do not run a default fetch first "to check" and then fetch again with flags. Pick the flags in step 1 and run the command once.
- **SPA auto-detection** — if the first fetcher returns an empty JavaScript shell, the script automatically retries with a real browser. Do not add `--tool browser` preemptively.
- **`--tool browser` needs system Chrome/Chromium** — if unavailable, auto-detect falls back to requests.
- **`--file` auto-detects format from the extension** — `.html`/`.htm` → HTML, everything else → markdown.
