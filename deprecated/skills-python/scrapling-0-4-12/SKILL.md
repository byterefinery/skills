---
name: scrapling-0-4-12
description: >
  Scrapling v0.4.12 — adaptive web scraping library with Python API and CLI.
  Fetchers are `Fetcher` (HTTP with TLS impersonation), `DynamicFetcher` (browser
  automation), `StealthyFetcher` (anti-bot bypass including Cloudflare). Sessions
  for persistent state. `Selector` parser with CSS/XPath/BS4 selection and adaptive
  element tracking. CLI — `scrapling extract` (save pages as .md/.html/.txt),
  `scrapling shell` (interactive IPython REPL with curl conversion). Use when the
  user needs to scrape websites from Python or the terminal, bypass anti-bot
  protections, extract content as Markdown or text, run browser automation,
  convert curl commands, or write scraping scripts.
metadata:
  tags:
    - python
    - cli
    - web-scraping
    - shell
    - browser-automation
---

# scrapling 0.4.12

## Overview

Scrapling is an adaptive web scraping framework with three layers:

1. **Fetchers** — `Fetcher` (HTTP), `DynamicFetcher` (browser), `StealthyFetcher` (anti-bot bypass)
2. **Parser** — `Selector` with CSS/XPath/BS4 selection, adaptive element tracking
3. **CLI** — `scrapling extract` (save to .md/.html/.txt), `scrapling shell` (interactive REPL)

Fetcher tiers:

| Fetcher | Best for |
|---|---|
| `Fetcher` | Static pages, fast HTTP with TLS impersonation |
| `DynamicFetcher` | JavaScript-rendered pages, SPAs, browser automation |
| `StealthyFetcher` | Anti-bot protected sites (Cloudflare Turnstile, etc.) |

Each fetcher has sync and async variants, plus session classes for persistent state.

## Usage

### Installation

```bash
# Parser only (no fetchers)
pip install "scrapling>=0.4.12"

# With fetchers (HTTP + browser)
pip install "scrapling[fetchers]>=0.4.12"

# With shell (CLI + interactive REPL, includes fetchers)
pip install "scrapling[shell]>=0.4.12"

# Everything (fetchers + shell + MCP server)
pip install "scrapling[all]>=0.4.12"

# Download Chromium + system deps (mandatory for browser fetchers)
scrapling install
scrapling install --force   # re-download
```

### Python API — Fetchers

#### HTTP Fetcher

```python
from scrapling.fetchers import Fetcher, AsyncFetcher, FetcherSession

# One-shot requests (class methods)
page = Fetcher.get('https://example.com')
page = Fetcher.post('https://api.example.com', json={'key': 'value'})
page = Fetcher.put('https://api.example.com/item/1', data={'name': 'updated'})
page = Fetcher.delete('https://api.example.com/item/1')

# With options
page = Fetcher.get(
    'https://example.com',
    impersonate='chrome',           # TLS fingerprint
    stealthy_headers=True,          # browser-like headers
    headers={'X-Custom': 'value'},
    cookies={'session': 'abc123'},
    params={'page': '1'},
    proxy='http://user:pass@proxy:8080',
    timeout=30,
    follow_redirects=True,
    verify=True,
)

# POST with data
page = Fetcher.post(url, data='key=value&foo=bar')
page = Fetcher.post(url, json={'key': 'value'})
```

#### Async Fetcher

```python
import asyncio
from scrapling.fetchers import AsyncFetcher

async def main():
    page = await AsyncFetcher.get('https://example.com')
    print(page.css('h1::text').get())

asyncio.run(main())
```

#### Browser Fetchers

```python
from scrapling.fetchers import DynamicFetcher, StealthyFetcher

# DynamicFetcher — JavaScript rendering
page = DynamicFetcher.fetch('https://spa.example.com')
page = DynamicFetcher.fetch(
    'https://example.com',
    headless=True,
    network_idle=True,             # wait for network quiet
    wait=2000,                     # extra wait in ms
    wait_selector='#content',      # wait for element
    disable_resources=True,        # block images/styles for speed
    block_ads=True,                # block ~3500 ad domains
)

# StealthyFetcher — anti-bot bypass
page = StealthyFetcher.fetch(
    'https://protected.example.com',
    solve_cloudflare=True,         # solve Cloudflare Turnstile
    headless=True,
    hide_canvas=True,              # noise canvas fingerprint
    block_webrtc=True,             # prevent IP leak
    allow_webgl=True,
)

# Async browser fetchers
page = await DynamicFetcher.async_fetch('https://example.com')
page = await StealthyFetcher.async_fetch('https://protected.com')
```

#### Sessions (persistent state)

```python
from scrapling.fetchers import FetcherSession, StealthySession, AsyncStealthySession

# HTTP session — shares cookies/headers across requests
with FetcherSession(impersonate='chrome', timeout=30) as session:
    page1 = session.get('https://example.com/login')
    page2 = session.post('https://example.com/api', json={'action': 'submit'})
    # Cookies persist automatically

# Stealth session — browser stays open across requests
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page1 = session.fetch('https://protected.com/page1')
    page2 = session.fetch('https://protected.com/page2')
    print(session.get_pool_stats())  # tab pool status

# Async session
async with AsyncStealthySession(max_pages=2) as session:
    results = await asyncio.gather(
        session.fetch('https://example.com/page1'),
        session.fetch('https://example.com/page2'),
    )
```

#### Response Object

```python
page = Fetcher.get('https://example.com')

# HTTP metadata
page.status_code    # int, e.g. 200
page.reason         # str, e.g. "OK"
page.url            # final URL (after redirects)
page.headers        # response headers (dict)
page.request_headers  # sent request headers
page.cookies        # response cookies
page.history        # list of redirect responses
page.body           # raw bytes
page.encoding       # detected encoding
page.captured_xhr   # XHR responses (when capture_xhr is set)

# Selector methods (inherited)
page.css('h1::text').get()
page.xpath('//title/text()').get()
page.html_content   # full HTML string
```

#### Configure Fetchers

```python
from scrapling.fetchers import Fetcher, StealthyFetcher

# Global parser config
Fetcher.configure(
    keep_comments=False,
    keep_cdata=False,
    huge_tree=True,
)

# Enable adaptive scraping globally
StealthyFetcher.adaptive = True

# Check current config
Fetcher.display_config()
```

### Python API — Selector (Parser)

```python
from scrapling import Selector
from scrapling.fetchers import Fetcher

# Create from HTML string
page = Selector('<html><body><h1>Hello</h1></body></html>')

# From fetcher (returns Response, which is Selector-compatible)
page = Fetcher.get('https://example.com')

# CSS selectors with pseudo-elements
page.css('h1::text').get()              # first match
page.css('.item::text').getall()        # all matches
page.css('a::attr(href)').getall()      # attribute values
page.css('div::html').get()             # inner HTML

# XPath
page.xpath('//div[@class="quote"]/span/text()').getall()
page.xpath('//a/@href').getall()

# BeautifulSoup-style
page.find_all('div', class_='quote')
page.find_all('a', href=True)
page.find_all(['div', 'p'], class_='text')

# Navigation
first = page.css('.item')[0]
first.parent
first.next_sibling
first.css('.child::text').get()

# Text extraction
page.get_all_text(strip=True, ignore_tags=('script', 'style'))

# Adaptive scraping — survive website changes
items = page.css('.product', auto_save=True)    # save fingerprints
items = page.css('.product', adaptive=True)     # relocate later
```

### Python API — Browser Automation

```python
# page_action — run JS automation after navigation
page = DynamicFetcher.fetch(
    'https://example.com',
    page_action=lambda p: p.click('#load-more-btn'),
)

# page_setup — setup before navigation
page = DynamicFetcher.fetch(
    'https://example.com',
    page_setup=lambda p: p.route('**/*', lambda route: route.abort()),
)

# capture_xhr — capture API responses the page makes
page = DynamicFetcher.fetch(
    'https://example.com',
    capture_xhr='**/api/**',
)
for xhr in page.captured_xhr:
    print(xhr.json)  # API response data

# Remote browser via CDP
page = DynamicFetcher.fetch(
    'https://example.com',
    cdp_url='http://localhost:9222',
)

# Custom Chrome executable
page = DynamicFetcher.fetch(
    'https://example.com',
    executable_path='/opt/google/chrome/google-chrome',
)
```

### Python API — Proxy Rotation

```python
from scrapling.fetchers import FetcherSession
from scrapling.engines.toolbelt import ProxyRotator

# Cyclic rotation across proxies
rotator = ProxyRotator(
    proxies=['http://proxy1:8080', 'http://proxy2:8080'],
    strategy='cyclic',  # or 'custom'
)

with FetcherSession(proxy_rotator=rotator) as session:
    for url in urls:
        page = session.get(url)  # rotates proxy automatically
```

### CLI — Extract Command

```bash
# GET — static page to Markdown
scrapling extract get 'https://example.com' page.md

# GET with CSS selector
scrapling extract get 'https://example.com' articles.md -s '.article'

# GET — raw HTML or plain text
scrapling extract get 'https://example.com' page.html
scrapling extract get 'https://example.com' content.txt

# POST with JSON body
scrapling extract post 'https://api.example.com/data' result.html -j '{"query":"test"}'

# Browser fetch (JavaScript-rendered pages)
scrapling extract fetch 'https://spa.example.com' page.md

# Stealth fetch (anti-bot bypass)
scrapling extract stealthy-fetch 'https://protected.example.com' page.md --solve-cloudflare

# AI-targeted extraction (sanitized for LLM input)
scrapling extract get 'https://docs.example.com' docs.md --ai-targeted
```

Key options: `-s` (CSS selector), `--ai-targeted`, `--impersonate`, `-H` (headers), `--cookies`, `-p` (params), `--proxy`, `--timeout`, `--headless`, `--wait`, `--network-idle`, `--disable-resources`, `--block-ads`, `--solve-cloudflare`. See references for full option lists.

### CLI — Interactive Shell

```bash
scrapling shell                              # interactive REPL
scrapling shell -c "print(page.css('h1::text').get())"   # one-shot
scrapling shell -L info                      # set log level
```

Shell shortcuts: `get`, `post`, `put`, `delete`, `fetch`, `stealthy_fetch` — pre-loaded and auto-track `page`/`pages`.

Shell utilities: `view(page)` (open in browser), `uncurl('curl ...')` (parse curl), `curl2fetcher('curl ...')` (execute curl).

## Gotchas

- **`scrapling install` is mandatory for browser fetchers** — after `pip install`, run `scrapling install` to download Chromium and system libraries. Without it, `DynamicFetcher` and `StealthyFetcher` fail.
- **`--ai-targeted` is critical for AI pipelines** — always use it when feeding scraped content to an LLM. It strips hidden elements, zero-width characters, and prompt injection vectors. For browser commands it also enables ad blocking.
- **Start with `Fetcher.get()`, escalate if needed** — HTTP fetcher is fastest. If content is empty (JavaScript-rendered), use `DynamicFetcher`. If blocked by anti-bot, use `StealthyFetcher`.
- **`Fetcher` methods are class methods** — call `Fetcher.get(url)`, not `Fetcher().get(url)`. Same for `DynamicFetcher.fetch()` and `StealthyFetcher.fetch()`.
- **Sessions require `with` blocks** — always use context managers: `with FetcherSession() as session:`. Sessions hold browser/HTTP resources open.
- **`get()` returns `None` on no match** — not an empty string. Use `get(default='fallback')` or check `if result:`.
- **Browser timeouts are in milliseconds** — `DynamicFetcher` and `StealthyFetcher` use ms (default 30000); `Fetcher` uses seconds (default 30).
- **`impersonate` accepts list for random selection** — pass `['chrome', 'firefox']` to randomly pick per request.
- **`find_all` uses underscore for reserved words** — `class_` not `class`, `for_` not `for`.
- **`::text` returns direct text only** — not text from child elements. Use `get_all_text()` for full extraction.
- **`auto_save` writes to SQLite** — default storage is `elements_storage.db` in the scrapling package directory.
- **Python 3.10+ required** — Scrapling does not support Python 3.9 or earlier.
- **`scrapling[shell]` includes `scrapling[fetchers]`** — one `pip install` covers both CLI and fetchers.
- **`scrapling[fetchers]` is separate from parser** — bare `pip install scrapling` only gives the parser. Importing fetchers without the extra raises `ModuleNotFoundError`.

## References

- [01-fetchers-api](references/01-fetchers-api.md) — Full Python API for Fetcher, DynamicFetcher, StealthyFetcher, sessions, async, proxy rotation, and configuration
- [02-selector-api](references/02-selector-api.md) — CSS/XPath/BS4 selection, pseudo-elements, navigation, text extraction, adaptive scraping, and Response object
- [03-cli-and-shell](references/03-cli-and-shell.md) — `scrapling extract` commands, interactive shell, curl parsing, one-shot execution, and output formats
- [04-browser-automation](references/04-browser-automation.md) — page_action, page_setup, capture_xhr, CDP mode, custom executables, and session pooling
