# Browser Automation Reference

## page_action — Post-Navigation Automation

Run Playwright actions after the page loads:

```python
from scrapling.fetchers import DynamicFetcher

# Click a button
def click_load_more(page):
    page.click('#load-more-btn')
    page.wait_for_timeout(1000)

page = DynamicFetcher.fetch(
    'https://example.com',
    page_action=click_load_more,
)

# Fill form and submit
def fill_form(page):
    page.fill('#username', 'admin')
    page.fill('#password', 'secret')
    page.click('#login-btn')
    page.wait_for_selector('#dashboard')

page = DynamicFetcher.fetch(
    'https://example.com/login',
    page_action=fill_form,
)

# Scroll to bottom
def scroll_to_bottom(page):
    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    page.wait_for_timeout(500)

page = DynamicFetcher.fetch(
    'https://example.com',
    page_action=scroll_to_bottom,
)

# Take screenshot
def screenshot(page):
    page.screenshot(path='page.png')

page = DynamicFetcher.fetch(
    'https://example.com',
    page_action=screenshot,
)
```

The `page` parameter is Playwright's Page object with full API access: `click()`, `fill()`, `type()`, `select_option()`, `check()`, `uncheck()`, `hover()`, `drag_to()`, `evaluate()`, `wait_for_selector()`, `wait_for_timeout()`, `goto()`, `reload()`, `screenshot()`, etc.

## page_setup — Pre-Navigation Setup

Register listeners and routes before navigation:

```python
from scrapling.fetchers import DynamicFetcher

# Block ad requests
def block_ads(page):
    page.route('**/ads/**', lambda route: route.abort())
    page.route('**/tracking/**', lambda route: route.abort())

page = DynamicFetcher.fetch(
    'https://example.com',
    page_setup=block_ads,
)

# Intercept and modify responses
def intercept(page):
    page.route('**/api/**', lambda route: route.fulfill(
        status=200,
        content='{"mocked": true}',
        headers={'Content-Type': 'application/json'},
    ))

page = DynamicFetcher.fetch(
    'https://example.com',
    page_setup=intercept,
)

# Set extra HTTP headers for all requests
def set_headers(page):
    page.set_extra_http_headers({'X-Custom': 'value'})

page = DynamicFetcher.fetch(
    'https://example.com',
    page_setup=set_headers,
)
```

## capture_xhr — Capture API Responses

Capture XHR/fetch responses the page makes during loading:

```python
from scrapling.fetchers import DynamicFetcher

# Capture all API calls
page = DynamicFetcher.fetch(
    'https://example.com',
    capture_xhr='**/api/**',
)

for xhr in page.captured_xhr:
    print(f"URL: {xhr.url}")
    print(f"Status: {xhr.status_code}")
    print(f"Content: {xhr.html_content[:200]}")
    # If JSON response:
    # print(xhr.json)
```

URL patterns use glob-style matching:
- `'**/api/**'` — any URL containing `/api/`
- `'**/graphql'` — any URL ending with `/graphql`
- `'**/*.json'` — any URL ending with `.json`

## CDP Mode — Remote Browser Control

Connect to an already-running browser instead of launching a new one:

```python
from scrapling.fetchers import DynamicFetcher, StealthyFetcher

# Connect to local browser with remote debugging
page = DynamicFetcher.fetch(
    'https://example.com',
    cdp_url='http://localhost:9222',
)

# Connect to remote browser
page = StealthyFetcher.fetch(
    'https://protected.example.com',
    cdp_url='http://remote-host:9222',
    solve_cloudflare=True,
)

# Via CLI
# scrapling extract fetch 'https://example.com' page.md --executable-path /path/to/chrome
```

Start Chrome with remote debugging:
```bash
google-chrome --remote-debugging-port=9222
```

## Custom Browser Executable

Point to an installed Chrome/Chromium instead of the bundled version:

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch(
    'https://example.com',
    executable_path='/opt/google/chrome/google-chrome',
)

# Or via environment variable
import os
os.environ['SCRAPLING_EXECUTABLE_PATH'] = '/opt/google/chrome/google-chrome'
page = DynamicFetcher.fetch('https://example.com')
```

## User Data Directory — Persistent Browser State

Persist cookies, local storage, and login state across runs:

```python
from scrapling.fetchers import StealthyFetcher

# First run — login and save state
page = StealthyFetcher.fetch(
    'https://example.com/login',
    user_data_dir='./browser-profile',
    page_action=lambda p: (
        p.fill('#username', 'admin'),
        p.fill('#password', 'secret'),
        p.click('#login-btn'),
    ),
)

# Later runs — state persists, already logged in
page = StealthyFetcher.fetch(
    'https://example.com/dashboard',
    user_data_dir='./browser-profile',
)
```

## Session Pooling

Browser sessions maintain a pool of tabs for concurrent requests:

```python
from scrapling.fetchers import StealthySession

with StealthySession(headless=True, max_pages=5) as session:
    # Each fetch reuses an available tab
    page1 = session.fetch('https://example.com/page1')
    page2 = session.fetch('https://example.com/page2')
    
    # Check pool status
    stats = session.get_pool_stats()
    print(stats)  # {'busy': 2, 'free': 3, 'error': 0}
```

## Extra Browser Flags

Pass additional Chromium launch flags:

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch(
    'https://example.com',
    extra_flags=[
        '--disable-gpu',
        '--no-sandbox',
        '--disable-dev-shm-usage',
    ],
)
```

## Locale and Timezone

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch(
    'https://example.com',
    locale='de-DE',
    timezone_id='Europe/Berlin',
)

# Locale affects:
# - navigator.language
# - Accept-Language header
# - Number and date formatting
```

## init_script — JavaScript on Page Creation

Execute JavaScript immediately when the page is created:

```python
from scrapling.fetchers import DynamicFetcher

# Path to a JS file
page = DynamicFetcher.fetch(
    'https://example.com',
    init_script='/path/to/inject.js',
)
```

Example `inject.js`:
```javascript
// Override navigator properties
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3],
});
```

## Additional Playwright Args

Pass extra settings directly to Playwright's browser context:

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch(
    'https://example.com',
    additional_args={
        'color_scheme': 'dark',
        'reduced_motion': 'reduce',
        'forced_colors': 'none',
    },
)
```

These settings take higher priority than Scrapling's defaults.

## Blocked Domains

Block requests to specific domains (and their subdomains):

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch(
    'https://example.com',
    blocked_domains={'analytics.example.com', 'tracking.other.com'},
    block_ads=True,  # combine with built-in ad blocking
)
```

Blocking `'example.com'` also blocks `'sub.example.com'`.

## DNS-over-HTTPS

Route DNS queries through Cloudflare's DoH to prevent DNS leaks when using proxies:

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch(
    'https://example.com',
    proxy='http://proxy:8080',
    dns_over_https=True,
)
```

## Gotchas

- **`page_action` receives Playwright's Page, not Selector** — use Playwright API (`page.click()`, `page.fill()`), not Scrapling's CSS selectors
- **`page_setup` must register before navigation** — event listeners and `page.route()` calls must be in `page_setup`, not `page_action`
- **`capture_xhr` only captures during page load** — XHR/fetch calls made after `page_action` completes are not captured
- **`cdp_url` requires a running browser** — the browser must already be launched with remote debugging enabled
- **`user_data_dir` is per-session** — each unique path creates a separate browser profile; use the same path to reuse state
- **`max_pages` limits concurrent tabs** — exceeding the limit blocks until a tab is freed; default is unlimited
- **`extra_flags` are passed at launch** — they affect the entire browser instance, not individual pages
- **`additional_args` override Scrapling defaults** — use them to fine-tune Playwright context settings when needed
- **`block_ads` blocks ~3,500 domains** — it uses a built-in list; combine with `blocked_domains` for custom blocks
- **Browser fetchers are slower than HTTP** — `DynamicFetcher` and `StealthyFetcher` launch a real browser; use `Fetcher` when possible
