# CLI and Interactive Shell Reference

## Installation

```bash
# Shell extra (includes fetchers)
pip install "scrapling[shell]>=0.4.12"

# Download Chromium + system deps (mandatory for browser commands)
scrapling install
scrapling install --force   # re-download
```

## Extract Command

```
scrapling extract [OPTIONS] COMMAND [ARGS]...
```

Subcommands: `get`, `post`, `put`, `delete`, `fetch`, `stealthy-fetch`

### HTTP Commands (get, post, put, delete)

```bash
scrapling extract get URL OUTPUT_FILE [OPTIONS]
scrapling extract post URL OUTPUT_FILE [OPTIONS]
scrapling extract put URL OUTPUT_FILE [OPTIONS]
scrapling extract delete URL OUTPUT_FILE [OPTIONS]
```

#### Arguments

| Argument | Required | Description |
|---|---|---|
| `URL` | Yes | Target URL |
| `OUTPUT_FILE` | Yes | Output path; extension determines format (`.md`, `.html`, `.txt`) |

#### Options

| Option | Default | Description |
|---|---|---|
| `--ai-targeted` | False | Extract main content, sanitize hidden elements for AI |
| `--stealthy-headers` | True | Use browser-like request headers |
| `--no-stealthy-headers` | — | Use default curl_cffi headers |
| `--impersonate` | — | Browser fingerprint (`chrome`, `firefox`, or comma-separated for random) |
| `--verify` | True | Verify SSL certificates |
| `--no-verify` | — | Skip SSL verification |
| `--follow-redirects` | True | Follow HTTP redirects |
| `--no-follow-redirects` | — | Do not follow redirects |
| `-p, --params` | — | Query parameters, format `key=value` (repeatable) |
| `-s, --css-selector` | — | CSS selector to extract specific elements |
| `--proxy` | — | Proxy URL, format `http://user:pass@host:port` |
| `--timeout` | 30 | Request timeout in **seconds** |
| `--cookies` | — | Cookie string, format `name1=value1; name2=value2` |
| `-H, --headers` | — | HTTP headers, format `Key: Value` (repeatable) |

#### POST/PUT Data Options

| Option | Description |
|---|---|
| `-j, --json` | JSON body as string, e.g. `'{"key":"value"}'` |
| `-d, --data` | Form data, format `param1=value1&param2=value2` |

#### Examples

```bash
# Simple GET to Markdown
scrapling extract get 'https://example.com' page.md

# GET with impersonation and CSS selector
scrapling extract get 'https://example.com' articles.md --impersonate chrome -s '.article-body'

# POST with JSON body
scrapling extract post 'https://api.example.com/search' results.html -j '{"q":"scrapling"}'

# POST with form data and custom headers
scrapling extract post 'https://example.com/login' response.html \
    -d 'username=admin&password=secret' \
    -H 'X-Custom-Header: value'

# PUT with JSON
scrapling extract put 'https://api.example.com/item/1' result.html \
    -j '{"name":"updated"}' --impersonate firefox

# DELETE with auth header
scrapling extract delete 'https://api.example.com/item/1' result.txt \
    -H 'Authorization: Bearer token123'

# GET with AI targeting (sanitized for LLM input)
scrapling extract get 'https://docs.example.com' docs.md --ai-targeted

# GET with proxy and cookies
scrapling extract get 'https://example.com' page.html \
    --proxy 'http://user:pass@proxy:8080' \
    --cookies 'session=abc123; csrf=xyz789'

# GET with multiple query params
scrapling extract get 'https://api.example.com/data' result.txt \
    -p 'page=1' -p 'limit=50' -p 'sort=desc'
```

### Browser Commands (fetch, stealthy-fetch)

```bash
scrapling extract fetch URL OUTPUT_FILE [OPTIONS]
scrapling extract stealthy-fetch URL OUTPUT_FILE [OPTIONS]
```

#### Shared Browser Options

| Option | Default | Description |
|---|---|---|
| `--ai-targeted` | False | Main content extraction + sanitization |
| `--executable-path` | — | Custom Chromium executable path |
| `-H, --extra-headers` | — | Extra headers, format `Key: Value` (repeatable) |
| `--proxy` | — | Proxy URL |
| `--real-chrome` | False | Use installed Chrome instead of bundled Chromium |
| `--no-real-chrome` | — | Use bundled Chromium |
| `--locale` | System default | User locale setting |
| `--wait-selector` | — | CSS selector to wait for before extraction |
| `-s, --css-selector` | — | CSS selector to extract specific elements |
| `--wait` | 0 | Extra wait in milliseconds after page load |
| `--timeout` | 30000 | Timeout in **milliseconds** |
| `--network-idle` | False | Wait for network to be idle |
| `--no-network-idle` | — | Do not wait for network idle |
| `--disable-resources` | False | Block images, stylesheets, fonts for speed |
| `--enable-resources` | — | Load all resources |
| `--headless` | True | Run browser headlessly |
| `--no-headless` | — | Run browser in visible mode |
| `--dns-over-https` | False | Route DNS through Cloudflare DoH |
| `--no-dns-over-https` | — | Use system DNS |
| `--block-ads` | False | Block ~3,500 known ad/tracker domains |
| `--no-block-ads` | — | Allow all requests |

#### Stealthy-Only Options

| Option | Default | Description |
|---|---|---|
| `--solve-cloudflare` | False | Solve Cloudflare Turnstile/Interstitial challenges |
| `--no-solve-cloudflare` | — | Do not attempt Cloudflare solving |
| `--block-webrtc` | False | Block WebRTC to prevent IP leaks |
| `--allow-webrtc` | — | Allow WebRTC |
| `--allow-webgl` | True | Allow WebGL rendering |
| `--block-webgl` | — | Block WebGL |
| `--hide-canvas` | False | Add noise to canvas fingerprinting |
| `--show-canvas` | — | Show unmodified canvas |

#### Examples

```bash
# Fetch JavaScript-rendered page
scrapling extract fetch 'https://spa.example.com' page.md

# Fetch with network idle wait and CSS selector
scrapling extract fetch 'https://app.example.com' data.html \
    --network-idle -s '#app-content'

# Fetch with extra wait for lazy-loaded content
scrapling extract fetch 'https://example.com' page.md --wait 2000

# Fetch with headful mode (debugging)
scrapling extract fetch 'https://example.com' page.html --no-headless

# Fetch with ad blocking and resource disabling for speed
scrapling extract fetch 'https://news.example.com' articles.md \
    --disable-resources --block-ads

# Stealth fetch with Cloudflare solving
scrapling extract stealthy-fetch 'https://protected.example.com' page.md \
    --solve-cloudflare --ai-targeted

# Stealth fetch with full stealth profile
scrapling extract stealthy-fetch 'https://example.com' page.html \
    --solve-cloudflare --block-webrtc --hide-canvas --block-ads

# Fetch with custom Chrome
scrapling extract fetch 'https://example.com' page.md \
    --executable-path '/opt/google/chrome/google-chrome'

# Fetch with proxy and DNS-over-HTTPS
scrapling extract fetch 'https://example.com' page.md \
    --proxy 'http://proxy:8080' --dns-over-https
```

### Output Formats

| Extension | Format | Processing |
|---|---|---|
| `.md` | Markdown | HTML converted via `markdownify` |
| `.html` | HTML | Raw HTML content |
| `.txt` | Plain text | Text extracted with whitespace normalization |

With `--ai-targeted`:
- Only the `<body>` main content is extracted
- `<script>`, `<style>`, `<noscript>`, `<svg>` tags are stripped
- CSS-hidden elements, `aria-hidden` elements, and `<template>` tags are removed
- Zero-width Unicode characters and XML-incompatible control characters are stripped

## Interactive Shell

### Starting the Shell

```bash
scrapling shell                          # interactive mode
scrapling shell -c "code"                # one-shot execution
scrapling shell -L info                  # set log level
scrapling shell -c "code" -L warning     # one-shot with custom log level
```

Log levels: `debug`, `info`, `warning`, `error`, `critical`, `fatal`

### Pre-loaded Namespace

#### Fetcher Shortcuts

Auto-update `page`/`response` and `pages` history:

| Shortcut | Equivalent | Description |
|---|---|---|
| `get(url, **kwargs)` | `Fetcher.get(url, **kwargs)` | HTTP GET request |
| `post(url, **kwargs)` | `Fetcher.post(url, **kwargs)` | HTTP POST request |
| `put(url, **kwargs)` | `Fetcher.put(url, **kwargs)` | HTTP PUT request |
| `delete(url, **kwargs)` | `Fetcher.delete(url, **kwargs)` | HTTP DELETE request |
| `fetch(url, **kwargs)` | `DynamicFetcher.fetch(url, **kwargs)` | Browser-based fetch |
| `stealthy_fetch(url, **kwargs)` | `StealthyFetcher.fetch(url, **kwargs)` | Stealth browser fetch |

#### Available Classes

| Object | Description |
|---|---|
| `Fetcher` | HTTP fetcher (curl_cffi-based, TLS impersonation) |
| `AsyncFetcher` | Async version of Fetcher |
| `FetcherSession` | Persistent session with Fetcher |
| `DynamicFetcher` | Browser-based fetcher (Playwright/Chrome) |
| `DynamicSession` | Persistent session with DynamicFetcher |
| `AsyncDynamicSession` | Async persistent session with DynamicFetcher |
| `StealthyFetcher` | Stealth browser fetcher (anti-bot bypass) |
| `StealthySession` | Persistent session with StealthyFetcher |
| `AsyncStealthySession` | Async persistent session with StealthyFetcher |
| `Selector` | Scrapling's HTML selector/parser class |

#### Shell Variables

| Variable | Description |
|---|---|
| `page` | Last fetched page (Selector/Response) |
| `response` | Alias for `page` |
| `pages` | Selectors collection of last 5 fetched pages |

#### Utility Functions

| Function | Description |
|---|---|
| `view(page)` | Open a Selector page in the system browser |
| `uncurl(curl_string)` | Parse curl command into a Request namedtuple |
| `curl2fetcher(curl_string)` | Parse curl and execute with Fetcher, returns Response |
| `help()` | Print shell help banner |

### Curl Parsing

#### `uncurl()` — Parse Only

Returns a `Request` namedtuple: `method`, `url`, `params`, `data`, `json_data`, `headers`, `cookies`, `proxy`, `follow_redirects`.

```python
req = uncurl('curl -H "Authorization: Bearer token" -X POST https://api.example.com -d \'{"key":"val"}\'')
print(req.method)    # "post"
print(req.url)       # "https://api.example.com"
print(req.headers)   # {"Authorization": "Bearer token"}
print(req.json_data) # {"key": "val"}
```

#### `curl2fetcher()` — Parse and Execute

```python
page = curl2fetcher('curl -H "Cookie: session=abc" https://example.com')
print(page.css('h1::text').get())
```

#### Supported curl Flags

- `-X/--request` — HTTP method
- `-H/--header` — headers (repeatable)
- `-d/--data`, `--data-raw`, `--data-binary` — request body
- `--data-urlencode` — URL-encoded data
- `-G/--get` — force GET with data in URL
- `-b/--cookie` — cookie string
- `-x/--proxy` — proxy URL
- `-U/--proxy-user` — proxy authentication
- `-k/--insecure` — skip SSL verification
- `--compressed` — accept compressed responses

Multi-line curl commands (with `\` continuations) are handled automatically.

### One-Shot Execution

```bash
# Get title of a page
scrapling shell -c "print(get('https://example.com').css('title::text').get())"

# Extract all links
scrapling shell -c "print(fetch('https://spa.example.com').css('a::attr(href)').getall())"

# Convert curl and print status
scrapling shell -c "r = curl2fetcher('curl https://httpbin.org/get'); print(r.status_code)"
```

### Page History

```python
get('https://example.com/page1')
get('https://example.com/page2')
get('https://example.com/page3')

# pages[0] = page1, pages[1] = page2, pages[2] = page3
# page / response = page3 (most recent)

for p in pages:
    print(p.css('title::text').get())
```

### Session Usage in Shell

```python
# HTTP session
with FetcherSession(impersonate='chrome') as session:
    p1 = session.get('https://example.com/page1')
    p2 = session.get('https://example.com/page2')

# Stealth session (browser stays open)
with StealthySession(headless=True) as session:
    p1 = session.fetch('https://protected.com/page1')
    p2 = session.fetch('https://protected.com/page2')
    print(session.get_pool_stats())  # tab pool status
```

Note: Session methods do not auto-update `page`/`pages` — only the shortcut functions (`get`, `fetch`, etc.) do.

## Gotchas

- **`--ai-targeted` is critical for AI pipelines** — always use it when feeding scraped content to an LLM to strip hidden elements and prompt injection vectors
- **`--css-selector` returns all matches** — the `-s` flag extracts every element matching the selector
- **Output format is determined by file extension** — `.md`, `.html`, `.txt` only; no other extensions supported
- **Browser timeouts in milliseconds** — `fetch`/`stealthy-fetch` use ms (default 30000); HTTP commands use seconds (default 30)
- **`--impersonate` accepts comma-separated list** — pass `chrome,firefox,safari` for random browser selection
- **`scrapling install` is mandatory for browser commands** — without it, `fetch` and `stealthy-fetch` fail
- **Shell shortcuts auto-track `page`** — calling `get()`, `fetch()`, etc. automatically updates `page`/`response` and `pages` history
- **IPython magic commands work** — `%history`, `%save`, `%run script.py` all available in the shell
