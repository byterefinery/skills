#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "scrapling[all]>=0.4.8",
#     "pyyaml>=6.0",
#     "requests>=2.31",
#     "markdownify>=1.2.3",
#     "beautifulsoup4>=4.15.0",
# ]
# ///

"""websearch — Multi-engine web search with LLM-optimized output.

Searches DuckDuckGo, Brave, Mojeek, Startpage, and Qwant.
Outputs results as markdown (default), JSON, or YAML.
Uses scrapling Fetcher with Safari TLS impersonation by default.
"""

from __future__ import annotations

import argparse
import html as html_mod
import json
import logging
import os
import random
import sys
import textwrap
import urllib.parse

# Silence scrapling info logs
logging.getLogger("scrapling").setLevel(logging.WARNING)


# ── Engine definitions ───────────────────────────────────────────────

class Engine:
    """Search engine configuration."""
    def __init__(self, name, url, method="GET", post_data=None, referer=None):
        self.name = name
        self.url = url
        self.method = method
        self.post_data = post_data
        self.referer = referer


ENGINES = {
    "duckduckgo-html": Engine(
        name="duckduckgo-html",
        url="https://html.duckduckgo.com/html/?q={query}",
        method="GET",
        referer="https://duckduckgo.com/",
    ),
    "duckduckgo-lite": Engine(
        name="duckduckgo-lite",
        url="https://lite.duckduckgo.com/lite/",
        method="POST",
        post_data="q={query}",
        referer="https://duckduckgo.com/",
    ),
}

ALL_ENGINES = ["duckduckgo-html"]

# duckduckgo-lite shares the same index as duckduckgo-html, so it's excluded
# from the default "all" set. Use --engine duckduckgo-lite explicitly if needed.

# Engine aliases (short names → canonical names)
ENGINE_ALIASES = {
    "ddg": "duckduckgo-html",
    "ddg-html": "duckduckgo-html",
    "ddg-lite": "duckduckgo-lite",
    "lite": "duckduckgo-lite",
}

def resolve_engines(engine_str: str | None) -> list[str]:
    """Parse comma-separated engine string, resolve aliases, validate."""
    if engine_str is None:
        return ALL_ENGINES

    raw = [e.strip().lower() for e in engine_str.split(",") if e.strip()]
    engines = []
    for name in raw:
        if name == "all":
            return ALL_ENGINES
        # Resolve alias
        canonical = ENGINE_ALIASES.get(name, name)
        if canonical not in ENGINES:
            print(f"Warning: unknown engine '{name}', skipping.", file=sys.stderr)
            continue
        if canonical not in engines:
            engines.append(canonical)
    return engines if engines else ALL_ENGINES


# ── AI-targeted HTML sanitization ────────────────────────────────────

def _ai_targeted_html(html_text: str) -> str:
    """Strip noise from HTML for AI/LLM consumption.

    Removes scripts, styles, noscript, svg, templates, aria-hidden,
    zero-width chars, control chars — same approach as webfetch.
    Lightweight regex — BeautifulSoup reserved for HTML→JSON/YAML parsing.
    """
    import re

    for tag in ("script", "style", "noscript", "svg", "template", "link", "meta"):
        html_text = re.sub(
            r"<" + tag + r"[^>]*>.*?</" + tag + r">", "", html_text,
            flags=re.DOTALL | re.I,
        )
        html_text = re.sub(r"<" + tag + r"[^>]*/>", "", html_text, flags=re.I)
    html_text = re.sub(
        r'<[^>]*aria-hidden="true"[^>]*>.*?</[^>]*>', "", html_text,
        flags=re.DOTALL | re.I,
    )
    html_text = re.sub(r"[\u200b\u200c\u200d\u2060\ufeff]", "", html_text)
    html_text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", html_text)
    return html_text


def html_to_md(html_text: str, *, ai_targeted: bool = True) -> str:
    """Convert HTML to clean markdown using markdownify."""
    from markdownify import markdownify as md
    if ai_targeted:
        html_text = _ai_targeted_html(html_text)
    return md(html_text, heading_style="atx", strip=["img"]).strip()


# ── Fetching: scrapling → requests fallback + cache ──────────────────

import hashlib
import tempfile
import time
from pathlib import Path

# Cache directory and TTL
_CACHE_DIR = Path(tempfile.gettempdir()) / "websearch-cache"
_CACHE_TTL = 3600  # 1 hour


def _cache_key(engine_name: str, query: str) -> str:
    """Generate a unique cache key for engine + query."""
    raw = f"{engine_name}:{query}".lower().strip()
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _cache_get(engine_name: str, query: str) -> str | None:
    """Get cached HTML if within TTL."""
    key = _cache_key(engine_name, query)
    cache_file = _CACHE_DIR / f"{key}.html"
    if not cache_file.exists():
        return None
    try:
        meta = cache_file.stat()
        if time.time() - meta.st_mtime > _CACHE_TTL:
            cache_file.unlink(missing_ok=True)  # Remove expired
            return None
        return cache_file.read_text(encoding="utf-8")
    except Exception:
        return None


def _cache_put(engine_name: str, query: str, html: str) -> None:
    """Cache HTML results."""
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = _cache_key(engine_name, query)
    cache_file = _CACHE_DIR / f"{key}.html"
    try:
        cache_file.write_text(html, encoding="utf-8")
    except Exception:
        pass


def _is_challenge(html_text: str) -> bool:
    """Detect CAPTCHA/challenge pages."""
    markers = [
        "anomaly-modal", "challenge-form", "bots use",
        "complete the following challenge", "select all squares",
        "captcha", "verify you are human", "robot check",
    ]
    lower = html_text.lower()
    return any(m in lower for m in markers)


def _has_results(html_text: str) -> bool:
    """Check if HTML contains any search results."""
    return any(marker in html_text for marker in [
        'result__a', 'result-link', 'data-title', 'class="r"',
        'searchResult', 'result-snippet', 'result__snippet',
    ])


def _fetch_with_scrapling(url: str, method: str, headers: dict, data: bytes | None) -> str | None:
    """Fetch with scrapling Fetcher (TLS impersonation + stealthy headers)."""
    from scrapling import Fetcher
    try:
        if method == "POST":
            resp = Fetcher.post(
                url, data=data, headers=headers,
                impersonate="safari", stealthy_headers=True,
            )
        else:
            resp = Fetcher.get(
                url, headers=headers,
                impersonate="safari", stealthy_headers=True,
            )
        if resp.status != 200:
            return None
        html = resp.html_content
        return html if not _is_challenge(html) else None
    except Exception:
        return None


def _fetch_with_requests(url: str, method: str, headers: dict, data: bytes | None) -> str | None:
    """Fetch with requests (stdlib fallback, no TLS impersonation)."""
    import requests
    try:
        if method == "POST":
            resp = requests.post(url, headers=headers, data=data, timeout=30, allow_redirects=True)
        else:
            resp = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        if resp.status_code != 200:
            return None
        html = resp.text
        return html if not _is_challenge(html) else None
    except Exception:
        return None


def fetch_engine(engine: Engine, query: str) -> str | None:
    """Fetch search results with cache: cache → scrapling → requests.

    Results cached per-engine for 1 hour to avoid rate-limiting.
    Returns HTML with results or None on failure/challenge.
    """
    # 1. Check cache first
    cached = _cache_get(engine.name, query)
    if cached:
        return cached

    encoded = urllib.parse.quote_plus(query)
    url = engine.url.format(query=encoded)

    headers = {}
    if engine.referer:
        headers["Referer"] = engine.referer

    data = None
    if engine.method == "POST":
        data = (engine.post_data.format(query=encoded) if engine.post_data else "q=" + query).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    # 2. Try scrapling (TLS fingerprint impersonation — best anti-bot)
    html = _fetch_with_scrapling(url, engine.method, headers, data)
    if html and _has_results(html):
        _cache_put(engine.name, query, html)
        return html

    # 3. Fallback: requests (no TLS impersonation, but sometimes works)
    html = _fetch_with_requests(url, engine.method, headers, data)
    if html and _has_results(html):
        _cache_put(engine.name, query, html)
        return html

    return None


from bs4 import BeautifulSoup


def _soup(html_text: str) -> BeautifulSoup:
    """Parse HTML string with BeautifulSoup."""
    return BeautifulSoup(html_text, "html.parser")


def extract_uddg(redirect_url: str) -> str:
    """Extract and decode the actual URL from DuckDuckGo redirect."""
    parsed = urllib.parse.urlparse(redirect_url)
    params = urllib.parse.parse_qs(parsed.query)
    uddg = params.get("uddg", [None])[0]
    if uddg:
        return urllib.parse.unquote(uddg)
    return redirect_url.replace("//duckduckgo.com/l/?uddg=", "")


def _parse_results(soup: BeautifulSoup, link_cls: str, snip_cls: str,
                   url_cls: str, engine: str, decode_url: bool = False) -> list[dict]:
    """Generic result parser using BeautifulSoup."""
    results = []
    seen = set()

    links = soup.find_all("a", class_=link_cls)
    snippets = soup.find_all(class_=snip_cls)
    urls = soup.find_all("a", class_=url_cls)

    for i, link in enumerate(links):
        href = link.get("href", "")
        if decode_url:
            href = extract_uddg(href)
        title = link.get_text(strip=True)
        if not title or not href:
            continue
        norm = href.rstrip("/").lower()
        if norm in seen:
            continue
        seen.add(norm)

        snippet = ""
        if i < len(snippets):
            snip_text = snippets[i].get_text(strip=True)
            if snip_text:
                snippet = html_to_md(snip_text)

        source = ""
        if i < len(urls):
            source = urls[i].get("href", "").strip()

        results.append({
            "title": title,
            "url": href,
            "snippet": snippet,
            "source": source or href,
            "engine": engine,
        })

    return results


def parse_ddg_html(html_text: str) -> list[dict]:
    """Parse DuckDuckGo HTML search results using BeautifulSoup."""
    soup = _soup(html_text)
    return _parse_results(soup, "result__a", "result__snippet",
                          "result__url", "duckduckgo-html")


def parse_ddg_lite(html_text: str) -> list[dict]:
    """Parse DuckDuckGo Lite search results using BeautifulSoup."""
    soup = _soup(html_text)
    return _parse_results(soup, "result-link", "result-snippet",
                          "link-text", "duckduckgo-lite", decode_url=True)


# Parser dispatch table
PARSERS = {
    "duckduckgo-html": parse_ddg_html,
    "duckduckgo-lite": parse_ddg_lite,
}


# ── Search orchestration ─────────────────────────────────────────────

def search(query: str, engines: list[str]) -> list[dict]:
    """Search one or more engines, merge and deduplicate results."""
    all_results = []
    seen_urls = set()

    for engine_name in engines:
        engine = ENGINES.get(engine_name)
        if not engine:
            print(f"Warning: unknown engine '{engine_name}', skipping.", file=sys.stderr)
            continue
        html_text = fetch_engine(engine, query)
        if html_text is None:
            continue
        parser = PARSERS.get(engine_name)
        if not parser:
            continue
        results = parser(html_text)
        for r in results:
            norm_url = r["url"].rstrip("/").lower()
            if norm_url in seen_urls:
                continue
            seen_urls.add(norm_url)
            all_results.append(r)
    return all_results


# ── Output formatters ────────────────────────────────────────────────

def format_markdown(results: list[dict], query: str) -> str:
    """Format results as LLM-optimized markdown."""
    if not results:
        return "No results found.\n"
    lines = [f"# Search results for: {query}\n", f"*{len(results)} results*\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"## {i}. {r['title']}\n")
        if r.get("snippet"):
            lines.append(f"{r['snippet']}\n")
        lines.append(f"- **URL**: {r['url']}")
        if r.get("source") and r["source"] != r["url"]:
            lines.append(f"- **Source**: {r['source']}")
        lines.append(f"- **Engine**: {r.get('engine', 'unknown')}")
        lines.append("")
    return "\n".join(lines)


def format_json(results: list[dict], query: str) -> str:
    """Format results as JSON."""
    return json.dumps({"query": query, "count": len(results), "results": results},
                      indent=2, ensure_ascii=False) + "\n"


def format_yaml(results: list[dict], query: str) -> str:
    """Format results as YAML."""
    import yaml
    return yaml.dump({"query": query, "count": len(results), "results": results},
                     default_flow_style=False, allow_unicode=True, sort_keys=False)


# ── CLI ──────────────────────────────────────────────────────────────

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="websearch.py",
        description="Search the web and output LLM-optimized results.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Engines: duckduckgo-html, duckduckgo-lite, brave, mojeek, startpage, qwant
            Aliases: ddg, ddg-html → duckduckgo-html | ddg-lite, lite → duckduckgo-lite

            By default, searches all engines (excludes duckduckgo-lite) and deduplicates.

            Examples:
              websearch.py "react hooks tutorial"
              websearch.py "python async" --engine ddg,brave
              websearch.py "llm frameworks" --engine ddg-html,mojeek,startpage
              websearch.py "web scraping" --engine ddg-lite,qwant --yaml
              websearch.py "rust vs go" --json -o results.json

            Output formats: markdown (default), --json, --yaml
        """),
    )
    parser.add_argument("query", help="Search query string")
    parser.add_argument("--engine", default=None, metavar="ENGINES",
                        help="Comma-separated engine(s). Default: all (excludes duckduckgo-lite).")
    parser.add_argument("--json", action="store_true", default=False,
                        help="Output results as JSON (default: markdown)")
    parser.add_argument("--yaml", action="store_true", default=False,
                        help="Output results as YAML")
    parser.add_argument("--output", "-o", default=None, metavar="FILE",
                        help="Write output to file instead of stdout")
    parser.add_argument("--no-ai-targeted", action="store_false", dest="ai_targeted",
                        default=True, help="Disable AI-targeted HTML sanitization")
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    engines = resolve_engines(args.engine)
    results = search(args.query, engines)

    if args.json and args.yaml:
        print("Error: --json and --yaml are mutually exclusive", file=sys.stderr)
        sys.exit(1)
    if args.json:
        output = format_json(results, args.query)
    elif args.yaml:
        output = format_yaml(results, args.query)
    else:
        output = format_markdown(results, args.query)

    if args.output:
        outdir = os.path.dirname(os.path.abspath(args.output))
        if outdir:
            os.makedirs(outdir, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(output)
        if not output.endswith("\n"):
            sys.stdout.write("\n")


if __name__ == "__main__":
    main()
