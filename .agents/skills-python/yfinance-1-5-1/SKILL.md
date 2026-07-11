---
name: yfinance-1-5-1
description: >
  yfinance 1.5.1 — download market data from Yahoo Finance API for Python. Use when
  fetching stock prices, historical OHLCV data, financial statements (income, balance
  sheet, cash flow), options chains, analyst estimates, earnings dates, dividends,
  splits, market screening, sector/industry data, market status, live WebSocket
  streaming, or ticker search/lookup. Covers Ticker, Tickers, download(), Market,
  Search, Lookup, Sector, Industry, Screener (EquityQuery/FundQuery/ETFQuery),
  WebSocket/AsyncWebSocket, and Auth. Trigger on: stock price, market data, Yahoo
  Finance, yfinance, yf.download, Ticker, OHLCV, financial statements, options chain,
  screener, market cap, earnings, dividends, WebSocket streaming quotes.
metadata:
  tags:
    - python
    - finance
    - market-data
    - yahoo-finance
---

# yfinance 1.5.1

## Overview

yfinance is the most popular Python library for downloading market data from Yahoo Finance. Version 1.5.1 provides a comprehensive API covering historical prices, financial statements, options, analyst data, screening, live streaming, and sector/industry browsing.

### Main Components

- **`Ticker(symbol)`** — single-instrument access to all data endpoints
- **`Tickers(symbols)`** — batch access to multiple instruments
- **`download()`** — multi-ticker historical data downloader with threading
- **`Market(region)`** — market status and summary (top gainers, losers, etc.)
- **`Search(query)`** — search for tickers and news
- **`Lookup(query)`** — fuzzy ticker lookup across types (equity, ETF, index, etc.)
- **`Sector(key)` / `Industry(key)`** — sector and industry data
- **`EquityQuery` / `FundQuery` / `ETFQuery`** — build screening queries
- **`screen(query)`** — execute a screener query
- **`WebSocket` / `AsyncWebSocket`** — live streaming price data
- **`Auth`** — manage Yahoo Finance login cookies for premium data

### Dependencies

Install via `pip install yfinance`. Core runtime dependencies: `pandas`, `numpy`, `requests`, `multitasking`, `platformdirs`, `pytz`, `beautifulsoup4`, `lxml`, `peewee`, `requests_cache`, `requests_ratelimiter`, `scipy`, `curl_cffi`, `protobuf`, `websockets`.

### Configuration

```python
import yfinance as yf

# Network settings
yf.config.network.proxy = "http://proxy:8080"
yf.config.network.retries = 3

# Debug settings
yf.config.debug.hide_exceptions = False  # raise exceptions instead of silencing
yf.config.debug.logging = True

# Locale
yf.config.locale.lang = "en-US"
yf.config.locale.region = "US"

# Enable debug mode (verbose logging)
yf.enable_debug_mode()

# Custom timezone cache location
yf.set_tz_cache_location("/path/to/cache")
```

## Usage

### Ticker — Single Instrument

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# Historical prices
df = ticker.history(period="1y", interval="1d")

# Quick info (faster than .info for common fields)
print(ticker.fast_info.last_price)
print(ticker.fast_info.market_cap)
print(ticker.fast_info.currency)

# Full info dict
info = ticker.info

# Financial statements (returns DataFrame)
income = ticker.income_stmt          # annual income statement
balance = ticker.balance_sheet       # annual balance sheet
cashflow = ticker.cash_flow          # annual cash flow

# Quarterly variants
q_income = ticker.quarterly_income_stmt
q_balance = ticker.quarterly_balance_sheet
q_cashflow = ticker.quarterly_cash_flow

# TTM (trailing twelve months)
ttm_income = ticker.ttm_income_stmt

# Dividends, splits, capital gains
dividends = ticker.dividends         # pd.Series
splits = ticker.splits               # pd.Series
actions = ticker.actions             # pd.DataFrame (dividends + splits)

# Analyst data
recommendations = ticker.recommendations
eps_trend = ticker.eps_trend
earnings_estimate = ticker.earnings_estimate
revenue_estimate = ticker.revenue_estimate
price_targets = ticker.analyst_price_targets

# Holders
major_holders = ticker.major_holders
institutional = ticker.institutional_holders
mutual_fund = ticker.mutualfund_holders

# Options
expirations = ticker.options          # tuple of expiration date strings
chain = ticker.option_chain(expirations[0])

# Earnings
earnings = ticker.earnings            # yearly earnings DataFrame
earnings_dates = ticker.earnings_dates # upcoming/past earnings dates

# Sustainability (ESG scores)
sustainability = ticker.sustainability

# News
news = ticker.news                    # list of news articles

# ISIN code
isin = ticker.isin

# Live streaming (synchronous)
ticker.live(message_handler=lambda msg: print(msg))
```

### Tickers — Batch Access

```python
tickers = yf.Tickers("AAPL MSFT GOOGL")

# Access individual Ticker objects
aapl = tickers.tickers["AAPL"]
print(aapl.info)

# Batch download history
df = tickers.download(period="1y", interval="1d")
```

### Download — Multi-Ticker History

```python
# Download multiple tickers at once
df = yf.download(["AAPL", "MSFT", "GOOGL"],
                  period="1y",
                  interval="1d",
                  prepost=True,        # include pre/post market
                  auto_adjust=True,    # adjust for splits/dividends
                  threads=True,        # parallel download
                  progress=True,       # show progress bar
                  group_by="ticker")   # MultiIndex by ticker

# With explicit date range
df = yf.download("AAPL",
                  start="2023-01-01",
                  end="2024-01-01",
                  interval="1wk")
```

### Search & Lookup

```python
# Search for tickers and news
results = yf.Search("apple", max_results=5, news_count=3)
print(results.quotes)   # list of quote dicts
print(results.news)     # list of news articles

# Fuzzy ticker lookup
lookup = yf.Lookup("appl")
equities = lookup.get_equity()   # list of matching equities
etfs = lookup.get_etf()          # list of matching ETFs
```

### Market Status

```python
import yfinance as yf

market = yf.Market("US")
# or yf.Market(yf.MarketRegion.EUROPE)

status = market.status           # {"US": {"is_open": True, ...}}
summary = market.summary         # DataFrame of top movers
gainers = market.gainers         # top gainers DataFrame
losers = market.losers           # top losers DataFrame
most_active = market.most_active # most active DataFrame
```

### Sector & Industry

```python
sector = yf.Sector("technology")
print(sector.name)
print(sector.top_etfs)
print(sector.top_mutual_funds)
print(sector.industries)          # DataFrame of industries

industry = yf.Industry("software-infrastructure")
print(industry.sector_name)
print(industry.top_performing_companies)
print(industry.top_growth_companies)
```

### Screener

```python
from yfinance.screener import EquityQuery, screen

# Build a custom query
q = EquityQuery("and", [
    EquityQuery("eq", ["region", "us"]),
    EquityQuery("gte", ["intradaymarketcap", 1000000000]),
    EquityQuery("gt", ["percentchange", 3]),
])

results = screen(q)

# Use predefined queries
results = screen("day_gainers")
results = screen("most_actives")

# Available predefined queries:
# day_gainers, day_losers, most_actives, most_shorted_stocks,
# aggressive_small_caps, growth_technology_stocks, small_cap_gainers,
# undervalued_growth_stocks, undervalued_large_caps,
# conservative_foreign_funds, high_yield_bond, portfolio_anchors,
# solid_large_growth_funds, solid_midcap_growth_funds, top_mutual_funds,
# top_etfs_us, top_performing_etfs, technology_etfs, bond_etfs
```

### Live WebSocket Streaming

```python
import yfinance as yf

# Synchronous
ws = yf.WebSocket()
ws.subscribe(["AAPL", "MSFT"])
ws.listen(message_handler=lambda msg: print(msg))
ws.unsubscribe(["AAPL"])

# Asynchronous
async def stream():
    ws = yf.AsyncWebSocket()
    await ws.subscribe(["AAPL"])
    await ws.listen(message_handler=lambda msg: print(msg))

# Per-ticker streaming (simpler API)
ticker = yf.Ticker("AAPL")
ticker.live(message_handler=lambda msg: print(msg))
```

### Auth (Premium Data)

```python
import yfinance as yf

auth = yf.Auth()

# Set login cookies obtained from browser
auth.set_login_cookies(cookie_t="...", cookie_y="...")

# Check login status
is_logged_in = auth.check_login()

# Check subscription tier
entitlement = auth.entitlement
```

## Gotchas

- **Yahoo Finance rate limits** — rapid repeated calls trigger HTTP 429. Use `yf.config.network.retries` for resilience and space out requests. The library has built-in caching via `requests_cache`, which helps with repeated calls.

- **`Ticker.info` is slow** — it fetches the full quote summary page. For common fields like price, volume, market cap, use `ticker.fast_info` which fetches from a lighter endpoint.

- **`history()` default period** — when neither `start`/`end` nor `period` is specified, defaults to `"1mo"`. Always be explicit about the time range.

- **Intraday data limit** — intraday intervals (1m, 5m, etc.) are limited to the last 60 days. For older intraday data, use `interval="1d"` and resample.

- **`auto_adjust=True` is default** — historical prices are adjusted for splits and dividends. Use `back_adjust=True` instead if you need prices adjusted relative to the oldest date, or both `False` for raw prices.

- **`repair=True` fixes Yahoo data errors** — Yahoo sometimes has 100x price errors or missing bars. Enable `repair=True` on `history()` to auto-fix, but it adds latency.

- **MultiIndex on `download()`** — with `group_by="ticker"`, columns are MultiIndex (ticker, OHLCV). With `group_by="column"` (default), tickers are column sub-labels. Know which you're getting.

- **`options` property returns expiration dates** — `ticker.options` is a tuple of date strings, not the chain itself. Pass one to `ticker.option_chain(date)` to get the actual options DataFrame.

- **Financial statement properties return annual data** — use `quarterly_` prefixed properties (e.g., `quarterly_income_stmt`) for quarterly data.

- **`screen()` predefined queries** — predefined queries have built-in defaults for count/offset/sort. Custom queries override these. Check `yf.PREDEFINED_SCREENER_QUERIES.keys()` for available names.

- **WebSocket requires `websockets` and `protobuf`** — these are dependencies but streaming only works during market hours or when Yahoo's streamer is available.

- **Auth cookies expire** — Yahoo login cookies have limited lifetime. Re-authenticate when `auth.check_login()` returns `False`.

- **`set_config()` is deprecated** — use `yf.config.network.proxy` and `yf.config.network.retries` directly instead of the old `yf.set_config()` function.

- **Empty DataFrames on missing data** — for delisted or invalid tickers, `history()` returns an empty DataFrame rather than raising. Check `len(df) == 0` to detect this.

- **Session reuse** — pass a `requests.Session` to `Ticker(session=sess)` or `download(session=sess)` to reuse connections and cookies across multiple calls.

## References

- [01-ticker-api](references/01-ticker-api.md) — Full Ticker property and method reference
- [02-screening](references/02-screening.md) — Screener query operators, fields, and examples
- [03-advanced](references/03-advanced.md) — WebSocket internals, Auth flow, sessions, error handling
