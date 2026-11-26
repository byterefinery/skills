---
name: scrapling-0-5-1
description: >
  Scrapling 0.5.1 — adaptive web scraping framework with HTTP fetchers
  (curl_cffi with TLS impersonation) and a stealth browser fetcher
  (Patchright-based, bypasses anti-bot systems including Cloudflare
  Turnstile). CSS/XPath/BeautifulSoup-style parser with adaptive element
  tracking that survives website redesigns. Concurrent spiders with
  pause/resume checkpoints, development-mode caching, and proxy rotation.
  CLI — `scrapling extract` (save pages as .md/.html/.txt), `scrapling
  shell` (interactive IPython REPL with curl conversion). MCP server for
  agent-driven scraping. `RemoteSession`/`AsyncRemoteSession` connect to an
  existing browser over CDP. Use when the user needs to scrape websites
  from Python or the terminal, bypass anti-bot protections, extract content
  as Markdown or text, run browser automation, write spiders or crawlers,
  convert curl commands, or build RAG pipelines from web content.
license: BSD-3-Clause
compatibility: Python 3.10+
metadata:
  tags:
    - python
    - cli
    - web-scraping
    - browser-automation
    - mcp
---

# scrapling 0.5.1

## Overview

Scrapling is an adaptive web scraping framework covering single requests through full-scale crawls:

- **HTTP fetchers** — `Fetcher` / `AsyncFetcher` (curl_cffi engine, TLS browser impersonation, HTTP/3) and `FetcherSession` for persistent state
- **Browser fetcher** — `StealthyFetcher` / `StealthySession` (Patchright engine, the only browser backend since v0.5; JavaScript rendering, Cloudflare solving, shadow DOM piercing)
- **Remote sessions** — `RemoteSession` / `AsyncRemoteSession` connect to an already-running Chromium over CDP
- **Parser** — `Selector` with CSS/XPath/BeautifulSoup-style selection, navigation, and adaptive element tracking that relocates elements after site changes
- **Spiders** — Scrapy-like concurrent crawlers with pause/resume checkpoints, multiple session types, and automatic proxy rotation
- **CLI** — `scrapling extract` (get/post/put/delete/fetch to .md/.html/.txt) and `scrapling shell` (IPython REPL)
- **MCP server** — agent tools for browser workflows, screenshots, and network inspection

Escalation pattern: start with HTTP `get`/`Fetcher`; if JavaScript rendering or anti-bot blocking appears, use the browser `fetch`/`StealthyFetcher`; for multi-page crawls, use a `Spider`.

## Usage

### Installation

```bash
# Everything (fetchers + shell/CLI + MCP + markdown/RAG)
pip install "scrapling[all]>=0.5.1"

# Alternatives — parser only: pip install scrapling
# CLI + HTTP/browser:        pip install "scrapling[shell]>=0.5.1"
# Markdown/RAG extras:       pip install "scrapling[rag]>=0.5.1"

# Browser fetchers need Chromium + system deps (mandatory, once)
scrapling install --force

# Docker alternative (CLI only, no Python code)
docker pull pyd4vinci/scrapling
```

### CLI — extract

Output format is chosen by the file extension (`.md`, `.html`, `.txt`):

```bash
scrapling extract get "https://blog.example.com" article.md --ai-targeted
scrapling extract get "https://example.com" articles.md --css-selector "article" --ai-targeted
scrapling extract post "https://api.example.com" result.html -d "param1=value1&param2=value2"
scrapling extract fetch "https://spa.example.com" page.md --network-idle --ai-targeted
scrapling extract fetch "https://protected.example.com" data.txt --solve-cloudflare --ai-targeted
```

Use `get` for simple sites; `fetch` (StealthyFetcher) for JavaScript-rendered or protected pages. Request options: `-H` headers, `--cookies`, `-p` params, `--timeout` (seconds), `--proxy`, `--impersonate` (e.g. `chrome` or `chrome,firefox` list), `--stealthy-headers`, `--follow-redirects`, `--verify`. Browser options for `fetch`: `--headless`, `--timeout` (milliseconds), `--wait`, `--wait-selector`, `--network-idle`, `--disable-resources`, `--block-ads`, `--real-chrome`, `--pierce-shadow`, `--solve-cloudflare`, `--hide-canvas`, `--block-webrtc`, `--dns-over-https`, `--executable-path`, `--locale`. Run `scrapling extract <command> --help` for the full option list.

### CLI — interactive shell

```bash
scrapling shell                                        # IPython REPL
scrapling shell -c "get('https://quotes.toscrape.com'); print(len(page.css('.quote')))"
scrapling shell --loglevel info
```

Shortcuts: `get`, `post`, `put`, `delete`, `fetch` (stealth browser) — `page`/`response` auto-track the last fetch, `pages` holds the last five. `Fetcher`, `AsyncFetcher`, `StealthyFetcher`, `Selector` are preloaded; curl commands convert via the built-in curl utilities.

### Python — HTTP

```python
from scrapling.fetchers import Fetcher, AsyncFetcher, FetcherSession

# One-shot (class methods — do not instantiate)
page = Fetcher.get('https://example.com')
page = Fetcher.get('https://example.com/search', params={'q': 'query'}, impersonate='chrome')
page = Fetcher.post('https://example.com/api', json={'key': 'value'})

# Session — cookies and settings persist, ~10x faster than one-shot
with FetcherSession(impersonate='chrome', timeout=30) as session:
    page1 = session.get('https://example.com/page1')
    page2 = session.post('https://example.com/api', data={'key': 'value'})

# Async
async with FetcherSession(http3=True) as session:
    page = await session.get('https://example.com')
```

`Fetcher.configure(adaptive=True, ...)` sets parser config globally (`adaptive`, `adaptive_domain`, `huge_tree`, `keep_comments`, `storage`, `storage_args`); `display_config()` shows it. Per-request overrides go through `selector_config={...}`. `page.body` is always bytes since v0.4; `page.markdown(main_content_only=True)` produces LLM-ready Markdown (needs the `rag` extra).

### Python — browser

```python
from scrapling.fetchers import StealthyFetcher, StealthySession

# One-shot — opens the browser, fetches, closes it
page = StealthyFetcher.fetch('https://spa.example.com', network_idle=True)

# Session — browser stays open across fetches
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page1 = session.fetch('https://protected.example.com/page1')
    page2 = session.fetch('https://protected.example.com/page2')
    print(session.get_pool_stats())
```

Key options: `solve_cloudflare=True` (not default), `headless`, `network_idle`, `wait` (ms), `wait_selector`, `disable_resources`, `block_ads`, `pierce_shadow=True` for open shadow DOM, `real_chrome` to use an installed Chrome, `page_action`/`page_setup` lambdas for automation, `executable_path` for a custom browser.

**CDP to an existing browser** — only the remote session classes accept `cdp_url`:

```python
from scrapling.fetchers import RemoteSession, AsyncRemoteSession

with RemoteSession(cdp_url='http://localhost:9222', new_context=False) as session:
    page = session.fetch('https://example.com')
```

`new_context=False` reuses the browser's default context (login state, existing tabs stay open; `useragent`, `proxy`, `locale`, `timezone_id`, `additional_args` are ignored); `new_context=True` (default) creates a separate context closed on exit.

**Network history** — replaced the removed `capture_xhr`; enable at session creation:

```python
with StealthySession(record_requests=True) as session:
    page = session.fetch('https://example.com', network_idle=True)
for r in session.network.search(url_pattern=r'/api/', resource_type='xhr', limit=None):
    print(r.url, r.status, r.meta['network_id'])
```

History spans the whole session; `search()` returns at most 100 matches by default (`limit=None` for all retained); sessions retain at most 1,000 requests; bodies limited to text content types, 1 MiB each.

### Python — parsing

```python
from scrapling import Selector  # or use any Response object directly

page = Selector('<html><body><h1>Hello</h1></body></html>')

page.css('h1::text').get()                    # first match (None if absent)
page.css('.item::text').getall()              # all matches
page.css('a::attr(href)').getall()            # attributes
page.xpath('//div[@class="quote"]/span/text()').getall()
page.find_all('div', class_='quote')         # BeautifulSoup-style
page.find_by_text('Albert Einstein', first_match=False)

first = page.css('.quote')[0]
first.parent                                  # navigation
first.css('.text::text').get()               # chained selection
first.find_similar()                          # similarity
page.get_all_text(strip=True, ignore_tags=('script', 'style'))
page.markdown(main_content_only=True)         # LLM-ready Markdown (rag extra)
```

Adaptive scraping: `Selector(html, adaptive=True)` and `css('.product', auto_save=True)` save element fingerprints so elements relocate after site redesigns (storage defaults to a SQLite file in the package dir).

### Python — spiders

```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    name = 'quotes'
    start_urls = ['https://quotes.toscrape.com/']
    concurrent_requests = 10
    robots_txt_obey = True

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {'text': quote.css('.text::text').get()}
        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = QuotesSpider().start()
result.items.to_json('quotes.json')
```

- **Pause/resume** — `QuotesSpider(crawldir='./crawl_data').start()`; Ctrl+C checkpoints, restart with the same `crawldir` to resume
- **Development mode** — `development_mode = True` caches responses to disk (`.scrapling_cache/{name}/`) so re-runs replay without hitting the server; never ship it
- **Multiple sessions** — `configure_sessions(self, manager)`: `manager.add('fast', FetcherSession(impersonate='chrome'))`, `manager.add('stealth', AsyncStealthySession(headless=True), lazy=True)`; route with `response.follow(link, sid='stealth')`
- **Rules-based** — `CrawlSpider` with `rules()` returning `CrawlRule(LinkExtractor(allow=r'/posts/'), callback=...)`; `SitemapSpider` for sitemaps; `XMLFeedSpider`/`CSVFeedSpider` for feeds; `ShopifySpider` for Shopify stores — see [12-spiders-generic-templates](references/12-spiders-generic-templates.md) and [13-spiders-platform-templates](references/13-spiders-platform-templates.md)

Ready-to-run examples (quotes.toscrape.com, 100 quotes across 10 pages): `assets/examples/01_fetcher_session.py`, `02_browser_session.py`, `03_stealthy_session.py`, `04_spider.py`.

## Gotchas

- **v0.5 removed the dynamic browser classes** — `DynamicFetcher`, `DynamicSession`, `AsyncDynamicSession`, and the `scrapling.fetchers.chrome` module are gone; `StealthyFetcher`/`StealthySession` are the only browser classes. Import `patchright.sync_api`/`patchright.async_api` (not `playwright`) in callbacks.
- **`cdp_url` no longer accepted on fetchers or stealth sessions** — use `RemoteSession`/`AsyncRemoteSession` even for a single fetch.
- **`capture_xhr` and `Response.captured_xhr` are gone** — use a session with `record_requests=True` and `session.network.search(...)`; the old regex moves to `url_pattern`.
- **`keep_cdata` removed** from `Selector`, `Fetcher.configure`, and `display_config()` — no replacement; it had no effect on output.
- **CLI has one browser command** — `scrapling extract fetch` (was `stealthy-fetch`, removed). In the shell, `fetch()` now means stealth browser; `stealthy_fetch()` is gone.
- **Always pass `--ai-targeted` on CLI extract commands** — filters hidden elements and prompt-injection vectors for LLM consumption; on `fetch` it also enables ad blocking.
- **`scrapling install` is mandatory for browser fetchers** — downloads Chromium + system deps; HTTP fetching does not need it.
- **Timeouts differ by layer** — HTTP `Fetcher`/CLI `get` use seconds (default 30); browser `fetch` uses milliseconds (default 30000).
- **`.md` and `.txt` CLI output is always UTF-8** since v0.5 (`.html` still uses `page.encoding`).
- **`response.follow()` no longer inherits request data** — pass `method`, `params`, `data`, `json` explicitly again after a POST; a followed link is a plain GET otherwise.
- **`robots_txt_obey=True` blocks the domain** when the robots.txt fetch fails or returns neither 200 nor 4xx (cached for the whole crawl); default is `False`.
- **Fetcher methods are class methods** — `Fetcher.get(url)`, never `Fetcher().get(url)`.
- **`get()` returns `None` on no match**, not an empty string; use `get(default=...)` or check truthiness.
- **`find_all` reserves words use underscores** — `class_`, `for_`.
- **`::text` is direct text only** — use `get_all_text()` for full element text.
- **`auto_save`/adaptive storage writes to SQLite** by default (in the package directory); configure with `storage`/`storage_args`.
- **Escalate, don't default to the browser** — `Fetcher` is fastest; browser fetches cost ~10x and are only needed for JS rendering or anti-bot walls.
- **Guardrails** — scrape only authorized content; respect robots.txt and ToS (`robots_txt_obey = True`); add `download_delay` or `autothrottle_enabled = True`; never bypass paywalls or scrape personal data.

## References

- [01-fetching-overview](references/01-fetching-overview.md) — fetcher comparison, shared configuration, Response object
- [02-fetching-http](references/02-fetching-http.md) — Fetcher/AsyncFetcher methods, all arguments, sessions, proxy rotation, examples
- [03-fetching-stealthy](references/03-fetching-stealthy.md) — StealthyFetcher/StealthySession options, network history, CDP remote sessions, shadow DOM, v0.5 migration
- [04-parsing-main-classes](references/04-parsing-main-classes.md) — Selector/Selectors classes, attributes, methods, text extraction
- [05-parsing-selection](references/05-parsing-selection.md) — CSS/XPath/BeautifulSoup-style selection, pseudo-elements, navigation
- [06-parsing-adaptive](references/06-parsing-adaptive.md) — adaptive element tracking, fingerprint storage, relocation
- [07-spiders-getting-started](references/07-spiders-getting-started.md) — writing your first spider
- [08-spiders-architecture](references/08-spiders-architecture.md) — spider engine internals
- [09-spiders-requests-responses](references/09-spiders-requests-responses.md) — spider Request/Response objects
- [10-spiders-sessions](references/10-spiders-sessions.md) — session types inside spiders
- [11-spiders-advanced](references/11-spiders-advanced.md) — pause/resume, development mode, logging, settings
- [12-spiders-generic-templates](references/12-spiders-generic-templates.md) — CrawlSpider, SitemapSpider, XMLFeedSpider, CSVFeedSpider, LinkExtractor
- [13-spiders-platform-templates](references/13-spiders-platform-templates.md) — ShopifySpider and platform-specific spiders
- [14-spiders-proxy-blocking](references/14-spiders-proxy-blocking.md) — proxy rotation and blocking handling in spiders
- [15-mcp-server](references/15-mcp-server.md) — MCP server tools, sessions, remote browsers, CAPTCHA workflows
- [16-building-rag-systems](references/16-building-rag-systems.md) — LLM-ready Markdown, ContentSpider for RAG pipelines
- [17-integrations-scrapy](references/17-integrations-scrapy.md) — using Scrapling parsing inside Scrapy projects
- [18-migrating-from-beautifulsoup](references/18-migrating-from-beautifulsoup.md) — BeautifulSoup → Scrapling API comparison
- [examples](assets/examples/README.md) — ready-to-run demos against quotes.toscrape.com (HTTP, browser, stealth, spider)
