# Fetchers API Reference

## Fetcher (HTTP)

### Class Methods

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get(url, **kwargs)
page = Fetcher.post(url, **kwargs)
page = Fetcher.put(url, **kwargs)
page = Fetcher.delete(url, **kwargs)
```

All return a `Response` object (Selector + HTTP metadata).

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `impersonate` | str/list/None | `'chrome'` | Browser TLS fingerprint; list for random selection |
| `http3` | bool | `False` | Enable HTTP/3 |
| `stealthy_headers` | bool | `True` | Use browser-like request headers |
| `headers` | dict | `{}` | Custom headers |
| `params` | dict/list/tuple | — | Query parameters |
| `data` | str/dict/bytes | — | Request body (POST/PUT) |
| `json` | dict/list | — | JSON body (POST/PUT) |
| `cookies` | dict | — | Request cookies |
| `proxy` | str | — | Proxy URL, format `http://user:pass@host:port` |
| `proxies` | dict | — | Proxy dict `{'http': url, 'https': url}` |
| `proxy_auth` | tuple | — | Proxy auth `(username, password)` |
| `timeout` | int/float | `30` | Timeout in **seconds** |
| `follow_redirects` | bool/str | `'safe'` | `'safe'` follows but rejects internal IP redirects |
| `max_redirects` | int | `30` | Maximum redirect count |
| `verify` | bool | `True` | Verify SSL certificates |
| `cert` | str/tuple | — | Client certificate path or `(cert, key)` |
| `retries` | int | `3` | Retry count on failure |
| `retry_delay` | int | `1` | Delay between retries in seconds |
| `selector_config` | dict | — | Parser arguments override |

### Examples

```python
# Basic GET
page = Fetcher.get('https://example.com')

# GET with query params
page = Fetcher.get('https://api.example.com/search', params={'q': 'python', 'page': 1})

# POST with JSON
page = Fetcher.post('https://api.example.com/data', json={'key': 'value'})

# POST with form data
page = Fetcher.post('https://example.com/login', data='username=admin&password=secret')

# With impersonation and headers
page = Fetcher.get(
    'https://example.com',
    impersonate='firefox135',
    headers={'X-API-Key': 'secret'},
    cookies={'session': 'abc123'},
)

# With proxy
page = Fetcher.get('https://example.com', proxy='http://user:pass@proxy:8080')

# With multiple random impersonation
page = Fetcher.get('https://example.com', impersonate=['chrome', 'firefox', 'safari'])

# Skip SSL verification
page = Fetcher.get('https://self-signed.example.com', verify=False)

# HTTP/3
page = Fetcher.get('https://example.com', http3=True)
```

## AsyncFetcher

```python
import asyncio
from scrapling.fetchers import AsyncFetcher

async def main():
    page = await AsyncFetcher.get('https://example.com')
    page = await AsyncFetcher.post('https://api.example.com', json={'key': 'value'})

asyncio.run(main())
```

Same parameters as `Fetcher`. All methods return coroutines.

## FetcherSession

Persistent HTTP session — shares cookies, headers, and connection pool across requests.

```python
from scrapling.fetchers import FetcherSession

# Constructor parameters
with FetcherSession(
    impersonate='chrome',
    http3=False,
    stealthy_headers=True,
    headers={'User-Agent': 'custom'},
    proxy='http://proxy:8080',
    proxy_rotator=None,
    timeout=30,
    retries=3,
    retry_delay=1,
    follow_redirects='safe',
    max_redirects=30,
    verify=True,
    cert=None,
    selector_config={},
) as session:
    page1 = session.get('https://example.com')
    page2 = session.post('https://example.com/api', json={'action': 'submit'})
    # Cookies persist automatically between requests
```

### Session Methods

| Method | Description |
|---|---|
| `session.get(url, **kwargs)` | HTTP GET |
| `session.post(url, **kwargs)` | HTTP POST |
| `session.put(url, **kwargs)` | HTTP PUT |
| `session.delete(url, **kwargs)` | HTTP DELETE |

Per-request kwargs override session defaults.

## DynamicFetcher (Browser)

### Class Methods

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch(url, **kwargs)
page = await DynamicFetcher.async_fetch(url, **kwargs)
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `headless` | bool | `True` | Run browser headlessly |
| `disable_resources` | bool | `False` | Block images, fonts, stylesheets, etc. |
| `blocked_domains` | set | — | Domain names to block (subdomains matched too) |
| `block_ads` | bool | `False` | Block ~3,500 known ad/tracker domains |
| `dns_over_https` | bool | `False` | Route DNS through Cloudflare DoH |
| `useragent` | str | auto-generated | Custom user agent string |
| `cookies` | list | — | Cookies as list of `{'name': '', 'value': '', 'domain': ''}` |
| `network_idle` | bool | `False` | Wait for network quiet (500ms no connections) |
| `load_dom` | bool | `True` | Wait for JavaScript to fully execute |
| `timeout` | int/float | `30000` | Timeout in **milliseconds** |
| `wait` | int/float | `0` | Extra wait after page load (ms) |
| `page_action` | callable | — | Function taking Playwright `page`, runs after navigation |
| `page_setup` | callable | — | Function taking Playwright `page`, runs before navigation |
| `wait_selector` | str | — | CSS selector to wait for |
| `wait_selector_state` | str | `'attached'` | State: `attached`, `visible`, `hidden`, `disabled` |
| `init_script` | str | — | Path to JS file executed on page creation |
| `locale` | str | system default | Locale, e.g. `'en-GB'`, `'de-DE'` |
| `timezone_id` | str | system default | Timezone, e.g. `'America/New_York'` |
| `real_chrome` | bool | `False` | Use installed Chrome instead of bundled Chromium |
| `cdp_url` | str | — | Connect to remote browser via CDP |
| `executable_path` | str | — | Path to custom Chromium executable |
| `google_search` | bool | `True` | Set Google referer header |
| `extra_headers` | dict | — | Extra headers to add |
| `proxy` | str/dict | — | Proxy URL or `{'server': '', 'username': '', 'password': ''}` |
| `proxy_rotator` | ProxyRotator | — | Proxy rotation object |
| `extra_flags` | list | — | Additional browser launch flags |
| `max_pages` | int | — | Max concurrent pages (for sessions) |
| `capture_xhr` | str | — | URL pattern to capture XHR/fetch responses |
| `selector_config` | dict | — | Parser arguments override |
| `additional_args` | dict | — | Extra Playwright context settings |
| `retries` | int | — | Retry count |
| `retry_delay` | int/float | — | Retry delay |

### Examples

```python
# Basic browser fetch
page = DynamicFetcher.fetch('https://spa.example.com')

# Wait for network idle
page = DynamicFetcher.fetch('https://example.com', network_idle=True)

# Wait for specific element
page = DynamicFetcher.fetch('https://example.com', wait_selector='#content')

# Block resources for speed
page = DynamicFetcher.fetch('https://example.com', disable_resources=True, block_ads=True)

# Click button after load
def click_load_more(page):
    page.click('#load-more-btn')
    page.wait_for_timeout(1000)

page = DynamicFetcher.fetch('https://example.com', page_action=click_load_more)

# Setup route interception before navigation
def setup_routes(page):
    page.route('**/ads/**', lambda route: route.abort())

page = DynamicFetcher.fetch('https://example.com', page_setup=setup_routes)

# Capture API calls the page makes
page = DynamicFetcher.fetch('https://example.com', capture_xhr='**/api/**')
for xhr in page.captured_xhr:
    print(xhr.status, xhr.url)

# Remote browser via CDP
page = DynamicFetcher.fetch('https://example.com', cdp_url='http://localhost:9222')

# Custom Chrome
page = DynamicFetcher.fetch('https://example.com', executable_path='/opt/google/chrome/google-chrome')

# With proxy and DNS-over-HTTPS
page = DynamicFetcher.fetch(
    'https://example.com',
    proxy='http://proxy:8080',
    dns_over_https=True,
)

# Async
page = await DynamicFetcher.async_fetch('https://example.com', network_idle=True)
```

## StealthyFetcher (Anti-Bot)

### Class Methods

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(url, **kwargs)
page = await StealthyFetcher.async_fetch(url, **kwargs)
```

### All DynamicFetcher Parameters Plus

| Parameter | Type | Default | Description |
|---|---|---|---|
| `solve_cloudflare` | bool | `False` | Solve Cloudflare Turnstile/Interstitial |
| `hide_canvas` | bool | `False` | Add noise to canvas fingerprinting |
| `block_webrtc` | bool | `False` | Block WebRTC to prevent IP leak |
| `allow_webgl` | bool | `True` | Enable WebGL (disabling may trigger WAFs) |
| `user_data_dir` | str | temp dir | Path to persist browser session data |

### Examples

```python
# Basic stealth fetch
page = StealthyFetcher.fetch('https://protected.example.com')

# Solve Cloudflare
page = StealthyFetcher.fetch(
    'https://protected.example.com',
    solve_cloudflare=True,
    headless=True,
)

# Full stealth profile
page = StealthyFetcher.fetch(
    'https://protected.example.com',
    solve_cloudflare=True,
    hide_canvas=True,
    block_webrtc=True,
    allow_webgl=True,
    block_ads=True,
    dns_over_https=True,
)

# Persist session data (cookies, storage)
page = StealthyFetcher.fetch(
    'https://protected.example.com',
    user_data_dir='./browser-data',
)

# Async
page = await StealthyFetcher.async_fetch(
    'https://protected.example.com',
    solve_cloudflare=True,
)
```

## Browser Sessions

### DynamicSession

```python
from scrapling.fetchers import DynamicSession

with DynamicSession(
    headless=True,
    disable_resources=True,
    network_idle=False,
    timeout=30000,
    locale='en-US',
    proxy='http://proxy:8080',
    max_pages=5,
) as session:
    page1 = session.fetch('https://example.com/page1')
    page2 = session.fetch('https://example.com/page2')
    # Browser stays open, cookies persist
```

### StealthySession

```python
from scrapling.fetchers import StealthySession

with StealthySession(
    headless=True,
    solve_cloudflare=True,
    hide_canvas=True,
    block_webrtc=True,
    user_data_dir='./stealth-data',
) as session:
    page1 = session.fetch('https://protected.com/page1')
    page2 = session.fetch('https://protected.com/page2')
    print(session.get_pool_stats())  # tab pool status
```

### AsyncStealthySession

```python
import asyncio
from scrapling.fetchers import AsyncStealthySession

async def main():
    async with AsyncStealthySession(max_pages=2) as session:
        results = await asyncio.gather(
            session.fetch('https://example.com/page1'),
            session.fetch('https://example.com/page2'),
        )
        print(session.get_pool_stats())

asyncio.run(main())
```

## Proxy Rotation

```python
from scrapling.fetchers import FetcherSession
from scrapling.engines.toolbelt import ProxyRotator

# Cyclic rotation
rotator = ProxyRotator(
    proxies=['http://proxy1:8080', 'http://proxy2:8080', 'http://proxy3:8080'],
    strategy='cyclic',
)

with FetcherSession(proxy_rotator=rotator) as session:
    for url in urls:
        page = session.get(url)  # rotates proxy each request
```

Works with all session types: `FetcherSession`, `DynamicSession`, `StealthySession`.

## Configure and Display

```python
from scrapling.fetchers import Fetcher, StealthyFetcher

# Global parser configuration
Fetcher.configure(
    keep_comments=False,
    keep_cdata=False,
    huge_tree=True,
    adaptive=False,
)

# Enable adaptive element tracking
StealthyFetcher.adaptive = True

# Check current configuration
print(Fetcher.display_config())
# {'huge_tree': True, 'keep_comments': False, 'keep_cdata': False, 'adaptive': False, ...}
```

## Gotchas

- **`Fetcher` methods are class methods** — call `Fetcher.get(url)`, not `Fetcher().get(url)`
- **Browser timeouts in milliseconds** — `DynamicFetcher`/`StealthyFetcher` use ms (default 30000); `Fetcher` uses seconds (default 30)
- **`page_action` receives Playwright's page object** — not Scrapling's Selector. Use Playwright API: `page.click()`, `page.fill()`, `page.wait_for_selector()`
- **`page_setup` runs before navigation** — use it for `page.route()` and event listeners that must be registered before page load
- **`capture_xhr` uses URL pattern matching** — glob-style patterns like `'**/api/**'` or `'**/graphql'`
- **`solve_cloudflare` requires browser automation** — it works by actually solving the challenge in the browser, no API keys needed
- **`user_data_dir` persists across runs** — cookies, local storage, and login state survive between script runs
- **`cdp_url` connects to existing browser** — the browser must already be running with remote debugging enabled
- **`blocked_domains` matches subdomains** — blocking `'example.com'` also blocks `'sub.example.com'`
- **`impersonate` list picks randomly** — pass `['chrome', 'firefox']` for random browser selection per request
- **Sessions must use `with` blocks** — always use context managers to ensure proper cleanup of browser/HTTP resources
