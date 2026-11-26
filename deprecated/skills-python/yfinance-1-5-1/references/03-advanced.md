# Advanced Topics — yfinance 1.5.1

## Table of Contents

- [WebSocket Streaming](#websocket-streaming)
- [Authentication](#authentication)
- [Sessions & Connection Reuse](#sessions--connection-reuse)
- [Error Handling](#error-handling)
- [Rate Limiting & Retries](#rate-limiting--retries)
- [Caching](#caching)
- [Price Repair](#price-repair)
- [ISIN Lookup](#isin-lookup)
- [FundsData](#fundsdata)
- [Calendars](#calendars)
- [Debug Mode](#debug-mode)

## WebSocket Streaming

yfinance supports real-time price streaming via Yahoo Finance's WebSocket endpoint (`wss://streamer.finance.yahoo.com/?version=2`). Messages are protobuf-encoded and decoded to dicts.

### Synchronous WebSocket

```python
import yfinance as yf

ws = yf.WebSocket()

# Subscribe to symbols
ws.subscribe(["AAPL", "MSFT"])

# Listen (blocks)
ws.listen(message_handler=lambda msg: print(msg))

# Unsubscribe
ws.unsubscribe(["AAPL"])
```

### Asynchronous WebSocket

```python
import asyncio
import yfinance as yf

async def stream():
    ws = yf.AsyncWebSocket()

    async def handler(msg):
        print(msg)

    await ws.subscribe(["AAPL", "MSFT"])
    await ws.listen(message_handler=handler)

asyncio.run(stream())
```

### Per-Ticker Streaming

```python
ticker = yf.Ticker("AAPL")
ticker.live(message_handler=lambda msg: print(msg))
```

### Message Format

Decoded messages contain pricing data with fields like `symbol`, `price`, `change`, `volume`, `timestamp`. The exact structure depends on Yahoo's protobuf schema.

### Heartbeat

The WebSocket client automatically re-sends subscribe messages every 15 seconds to maintain the connection.

## Authentication

Some Yahoo Finance endpoints require authentication. Use the `Auth` class to manage login cookies.

### Obtaining Cookies

1. Log in to https://finance.yahoo.com in a browser
2. Open Developer Tools → Application/Storage tab
3. Find cookies named `T` and `Y` under `https://finance.yahoo.com`
4. Copy their values

### Using Auth

```python
import yfinance as yf

auth = yf.Auth()

# Set cookies
auth.set_login_cookies(cookie_t="cookie_t_value", cookie_y="cookie_y_value")

# Check login status
if auth.check_login():
    print("Logged in")

# Check subscription tier
entitlement = auth.entitlement
```

### Cookie Expiry

Yahoo login cookies expire after a period of time. Re-check with `auth.check_login()` and re-authenticate as needed.

## Sessions & Connection Reuse

Pass a `requests.Session` to reuse TCP connections and cookies across calls:

```python
import requests
import yfinance as yf

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 ..."
})

# Reuse across multiple tickers
t1 = yf.Ticker("AAPL", session=session)
t2 = yf.Ticker("MSFT", session=session)

# Or with download
df = yf.download(["AAPL", "MSFT"], session=session)
```

### Proxy Configuration

```python
yf.config.network.proxy = "http://proxy:8080"
# or dict format:
yf.config.network.proxy = {"http": "http://proxy:8080", "https": "http://proxy:8080"}
```

## Error Handling

yfinance defines a hierarchy of exceptions:

| Exception | When Raised |
|---|---|
| `YFException` | Base exception class |
| `YFDataException` | Yahoo Finance is down or returned bad data |
| `YFNotImplementedError` | Method not yet implemented for this data type |
| `YFTickerMissingError` | Ticker not found (possibly delisted) |
| `YFTzMissingError` | No timezone found for ticker |
| `YFPricesMissingError` | No price data found for ticker |
| `YFEarningsDateMissing` | No earnings dates found |
| `YFInvalidPeriodError` | Invalid period parameter |
| `YFRateLimitError` | HTTP 429 — too many requests |

### Exception Handling Strategy

By default, `yf.config.debug.hide_exceptions = True`, which catches and logs exceptions silently, returning empty DataFrames or dicts. Set to `False` to propagate exceptions:

```python
yf.config.debug.hide_exceptions = False

try:
    df = ticker.history(period="1y")
except yf.exceptions.YFRateLimitError:
    # Wait and retry
    time.sleep(60)
except yf.exceptions.YFPricesMissingError:
    # Ticker may be delisted
    pass
```

## Rate Limiting & Retries

Yahoo Finance rate-limits requests. The library uses `requests_ratelimiter` internally.

```python
# Enable retries for transient failures
yf.config.network.retries = 3

# Set proxy if behind a firewall
yf.config.network.proxy = "http://proxy:8080"
```

### Best Practices

- Space out requests (sleep 1–2 seconds between calls)
- Use `download()` for batch operations instead of looping `Ticker().history()`
- Enable `threads=True` in `download()` for parallel fetching within rate limits
- Cache results when possible (built-in caching helps)

## Caching

yfinance caches timezone data and ISIN lookups locally using `platformdirs` and `peewee` (SQLite). Cache location follows OS conventions.

```python
# Change cache location
yf.set_tz_cache_location("/custom/path/to/cache")
```

HTTP responses are cached via `requests_cache`, reducing repeated API calls for the same data.

## Price Repair

Yahoo Finance sometimes has data quality issues:

- **100x errors**: Prices reported 100x too high or too low
- **Missing bars**: Gaps in daily data
- **Bad dividend adjustments**: Incorrect split/dividend adjustments

Enable repair:

```python
df = ticker.history(period="1y", repair=True)
```

Repair works by cross-referencing multiple data sources and intervals. It adds latency but improves data quality.

### Limitations

- `repair=True` is not supported with `interval="5d"`
- Repair requires timezone info; fails silently for unknown tickers
- Multi-day intervals (`1wk`, `1mo`, `3mo`) fetch 1d data internally, then resample

## ISIN Lookup

ISIN codes can be used directly as ticker symbols:

```python
ticker = yf.Ticker("US0378331005")  # AAPL's ISIN
print(ticker.ticker)  # "AAPL"
print(ticker.isin)    # "US0378331005"
```

The ISIN-to-ticker mapping is cached locally after first lookup.

## FundsData

For mutual funds and ETFs, `FundsData` provides fund-specific data:

```python
ticker = yf.Ticker("VFIAX")  # Vanguard 500 Index Fund
funds = ticker.funds_data

print(funds.asset_classes)       # Asset class allocation
print(funds.fund_overview)       # Overview dict
print(funds.fund_operations)     # Operations data
```

## Calendars

Exchange trading calendars:

```python
import yfinance as yf

cal = yf.Calendars()
# Get trading calendar for an exchange
calendar = cal.get_calendar("NYSE")
```

## Debug Mode

Enable verbose logging for troubleshooting:

```python
import yfinance as yf

yf.enable_debug_mode()

# Or manually:
yf.config.debug.logging = True
yf.config.debug.hide_exceptions = False
```

This logs all HTTP requests and responses, helpful for diagnosing API issues.
