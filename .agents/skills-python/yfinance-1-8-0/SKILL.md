---
name: yfinance-1-8-0
description: >
  yfinance 1.8.0 — Python library to download market data from the Yahoo Finance
  API. Use when fetching stock prices, historical OHLCV data, financial statements
  (income, balance sheet, cash flow), options chains, analyst estimates, earnings
  dates, dividends, splits, capital gains, market screening, sector/industry data
  with region scoping, event calendars (earnings, IPOs, splits, economic events),
  market summaries, live WebSocket price streaming, fund holdings for ETFs and
  mutual funds, or ticker search and lookup. Covers Ticker, Tickers, download(),
  Market, MarketRegion, Search, Lookup, Sector, Industry, Calendars, Auth,
  EquityQuery/FundQuery/ETFQuery with screen(), and WebSocket/AsyncWebSocket.
  Triggers on stock price, market data, Yahoo Finance, yfinance, yf.download,
  Ticker, OHLCV, financial statements, options chain, screener, earnings calendar,
  dividends, WebSocket streaming quotes.
metadata:
  tags:
    - python
    - finance
    - market-data
    - yahoo-finance
---

# yfinance 1.8.0

## Overview

yfinance downloads market data from Yahoo Finance's API. Version 1.8.0 covers historical prices (with price repair), financial statements, options, analysis and holdings, market screening, sector/industry browsing with region scoping, upcoming-event calendars, live WebSocket streaming, and `Auth` for logged-in (premium) data.

### Main Components

All importable from `yfinance` directly:

- **`Ticker(symbol)` / `Tickers(symbols)`** — single and batch instrument access to every data endpoint
- **`download()`** — multi-ticker historical data downloader
- **`Market(region)`** + `MarketRegion` enum — market status and summary (8 regions)
- **`Search(query)`** — quotes, news, research reports
- **`Lookup(query)`** — ticker lookup by asset type (stock, etf, index, future, currency, cryptocurrency)
- **`Sector(key)` / `Industry(key)`** — sector/industry data, optionally scoped to a region
- **`EquityQuery` / `FundQuery` / `ETFQuery`** + **`screen(query)`** — market screening (custom or predefined queries)
- **`Calendars(start, end)`** — earnings, IPO, splits, and economic-events calendars
- **`WebSocket` / `AsyncWebSocket`** — live price streaming
- **`Auth`** — Yahoo Finance login cookies for premium data
- **`config`**, `enable_debug_mode()`, `set_tz_cache_location()` — global network/debug/locale settings

### Install & Dependencies

Install with `pip install yfinance`. Runtime dependencies (from `pyproject.toml`): `beautifulsoup4`, `curl_cffi>=0.17`, `lxml`, `numpy`, `pandas`, `peewee`, `platformdirs`, `protobuf`, `pytz`, `requests`, `websockets`. Price repair additionally needs `scipy` and `scikit-learn` (extra `yfinance[repair]`). Version 1.8.0 dropped the `multitasking` dependency and honors `download(threads=N)` as a hard concurrency cap.

To install without `curl_cffi` (requests fallback), see [03-advanced](references/03-advanced.md).

### Global Config

```python
import yfinance as yf
yf.config.network.proxy = "http://proxy:8080"
yf.config.network.retries = 2      # exponential backoff (1s, 2s, 4s...)
yf.config.debug.hide_exceptions = False  # raise instead of silencing
yf.config.debug.logging = True           # verbose debug logging
# Locale — applies to subsequent Ticker.info, fast_info, calendar, earnings_dates, ...
yf.config.locale.lang = "en-US"
yf.config.locale.region = "US"
```

`yf.set_config()` is deprecated; set `yf.config.network.*` directly.

## Usage

### Ticker — Single Instrument

```python
import yfinance as yf

dat = yf.Ticker("MSFT")

# Historical market data
dat.history(period="1mo")

# Options — .options is a tuple of expiration dates; pass one to option_chain()
dat.option_chain(dat.options[0]).calls

# Financial statements
dat.balance_sheet
dat.quarterly_income_stmt

# Dates / general info
dat.calendar        # dict of key dates (next earnings, etc.)
dat.info            # full quote summary dict

# Analysis
dat.analyst_price_targets

# Live streaming for this single ticker
dat.live()
```

Properties return lazily-fetched DataFrames/series/dicts — full list in [01-ticker-api](references/01-ticker-api.md).

### Tickers — Batch Access

```python
import yfinance as yf

tickers = yf.Tickers('msft aapl goog')   # space/comma string or list; symbols uppercased

# Access each Ticker object
tickers.tickers['MSFT'].info
tickers.tickers['AAPL'].history(period="1mo")
tickers.tickers['GOOG'].actions

# Parallel fetch for all tickers (new in 1.8.0)
tickers.info      # dict: symbol -> info dict
tickers.calendar  # DataFrame: one row per ticker

# Fewer threads are gentler on Yahoo's rate limit
tickers.get_info(threads=2, progress=True)

# Live streaming for all tickers
tickers.live()
```

### download — Multi-Ticker History

```python
import yfinance as yf

data = yf.download("SPY AAPL", period="1mo")
```

Key parameters: `tickers` (space-separated string or list), `period` (`1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max`; default `1mo`), `interval` (`1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo`; intraday max 60 days back), `start` inclusive / `end` exclusive, `group_by` (`'column'`/`'ticker'`), `auto_adjust`, `back_adjust`, `repair`, `prepost`, `keepna`, `rounding`, `threads`, `progress`, `timeout`, `session`, `multi_level_index`. Full table in [01-ticker-api](references/01-ticker-api.md).

### Search & Lookup

```python
import yfinance as yf

# Quotes, news, and research
quotes = yf.Search("AAPL", max_results=10).quotes
news = yf.Search("Google", news_count=10).news
research = yf.Search("apple", include_research=True).research

# Fuzzy lookup by asset type (default count=25; pass count=100 etc.)
all = yf.Lookup("AAPL").all
stocks = yf.Lookup("AAPL").get_stock(count=100)
etfs = yf.Lookup("AAPL").etf
indices = yf.Lookup("AAPL").index
futures = yf.Lookup("AAPL").future
```

### Market Status & Summary

```python
import yfinance as yf

EUROPE = yf.Market("EUROPE")   # or yf.Market(yf.MarketRegion.EUROPE)

status = EUROPE.status     # NOTE: US data only — see Gotchas
summary = EUROPE.summary
```

Regions (plain strings or `MarketRegion` members): `US`, `GB`, `ASIA`, `EUROPE`, `RATES`, `COMMODITIES`, `CURRENCIES`, `CRYPTOCURRENCIES`. Only `Market.summary` is regional; `Market.status` is US-only.

### Sector & Industry

```python
import yfinance as yf

tech = yf.Sector('technology')
software = yf.Industry('software-infrastructure')

tech.key; tech.name; tech.symbol; tech.ticker
tech.overview; tech.top_companies; tech.research_reports
tech.top_etfs; tech.top_mutual_funds; tech.industries

software.sector_key; software.sector_name
software.top_performing_companies; software.top_growth_companies
```

Sector/Industry can be chained with Ticker in both directions:

```python
msft = yf.Ticker('MSFT')
tech = yf.Sector(msft.info.get('sectorKey'))
software = yf.Industry(msft.info.get('industryKey'))

tech_ticker = tech.ticker
tech_ticker.info
software_ticker.history()
```

Default data is US. Scope top lists to another region with an ISO 3166-1 alpha-2 country code (case-insensitive):

```python
yf.Sector("technology", region="GB").top_companies        # UK
yf.Sector("technology", region="DE").top_companies        # Germany
yf.Industry("software-infrastructure", region="JP")       # Japan
```

Region scoping applies to `top_companies`, `top_etfs`, `top_mutual_funds`, and the industry top performing/growth lists.

### Fund Data (ETFs / Mutual Funds)

```python
import yfinance as yf

spy = yf.Ticker('SPY')
data = spy.funds_data

data.description          # fund description
data.fund_overview        # operational information
data.fund_operations
data.asset_classes        # holdings
data.top_holdings
data.equity_holdings
data.bond_holdings
data.bond_ratings
data.sector_weightings
```

Holdings fields (e.g. `top_holdings`) are `pd.DataFrame`.

### Calendars — Upcoming Events

```python
import yfinance as yf
from datetime import datetime, timedelta

# Default init = today + 7 days (also accepts explicit start/end)
calendar = yf.Calendars()

# Properties fetch on access: earnings, IPO, splits, economic events
# (calendar.earnings_calendar / .ipo_info_calendar / .splits_calendar / .economic_events_calendar)

# Manual queries with filters
df = calendar.get_earnings_calendar(
    market_cap=100_000_000,    # filter out small-caps
    filter_most_active=True,   # only actively traded
    limit=100,
)

# Imminent UNREPORTED earnings:
today = datetime.now()
is_friday = today.weekday() == 4
day_after_tomorrow = today + timedelta(days=4 if is_friday else 2)

cal = yf.Calendars(today, day_after_tomorrow)
df = cal.get_earnings_calendar(limit=100)
unreported_df = df[df["Reported EPS"].isnull()]
```

### Screener

```python
import yfinance as yf
from yfinance import EquityQuery, FundQuery, ETFQuery, screen

# Predefined query by name (19 built-ins, e.g. day_gainers, most_actives, bond_etfs)
results = screen("day_gainers")

# Custom query — operators: and, eq, gt, gte, lt, btwn, is-in
q = EquityQuery("and", [
    EquityQuery("eq", ["region", "us"]),
    EquityQuery("gte", ["intradaymarketcap", 1_000_000_000]),
    EquityQuery("gt", ["percentchange", 3]),
])
results = screen(q)
```

`screen(query, offset, size, count, sortField, sortAsc, ...)` — `count` for predefined queries (default 25), `size` for custom (default 100), max 250. Check `EquityQuery.valid_fields` / `EquityQuery.valid_values` for supported fields (same on `FundQuery`/`ETFQuery`). Full details in [02-screening-calendars](references/02-screening-calendars.md).

### Live WebSocket Streaming

```python
import yfinance as yf

def message_handler(message):
    print("Received message:", message)

# With context manager (or plain WebSocket() + subscribe + listen + close)
with yf.WebSocket() as ws:
    ws.subscribe(["AAPL", "BTC-USD"])
    ws.listen(message_handler)

# Per-ticker / per-group streaming
yf.Ticker("AAPL").live(message_handler)
yf.Tickers("AAPL MSFT").live(message_handler)
```

Async version: `AsyncWebSocket` with `async with` / `await` (see [03-advanced](references/03-advanced.md)); in Jupyter apply `nest_asyncio` first.

### Auth — Premium Data

```python
import yfinance as yf
import os

auth = yf.Auth()
# Stores the browser cookies, validates with a live login check, returns bool.
if auth.set_login_cookies(os.getenv("COOKIE_T"), os.getenv("COOKIE_Y")):
    print("Logged in")

# Every subsequent request now runs under the logged-in user.
auth.check_login()        # True / False (re-queried each call, never cached)
auth.subscription_tier()  # 'gold' / 'silver' / 'bronze' / 'free' / None
auth.user                 # {'guid': ...} or None
```

`Auth` **cannot automate login** — Yahoo requires a reCAPTCHA. Cookies `T` and `Y` must be copied manually from the browser (steps in [03-advanced](references/03-advanced.md)).

### Proxy

Per-call `proxy=` argument on `history` and the `get_*` fetchers:

```python
msft = yf.Ticker("MSFT")
msft.history(..., proxy="PROXY_SERVER")
msft.get_balance_sheet(proxy="PROXY_SERVER")
msft.option_chain(..., proxy="PROXY_SERVER")
```

Or globally via `yf.config.network.proxy`.

## Gotchas

- **`auto_adjust=True` is the default** — `Open/High/Low/Close` are all adjusted for splits *and* dividends, and there is **no `Adj Close` column** in this mode. Pass `auto_adjust=False` to get split-adjusted OHLC plus an `Adj Close` that additionally accounts for dividends.

- **Intraday data is limited to the last 60 days** — for older data use `interval="1d"` (or coarser) and resample yourself. Note `30m` is fetched from Yahoo as `15m` and resampled, to work around a Yahoo API bug.

- **Date semantics** — `start` is inclusive, `end` is exclusive (`end="2023-01-01"` gives last row `2022-12-31`). With no `start`/`end`/`period` given, `period="1mo"` is used.

- **`Market.status` is US-only** — it is backed by Yahoo's `markettime` endpoint, which ignores the market parameter. For non-`US` regions, `status` is `None` and a warning is logged; `Market.summary` is the regional one.

- **`Auth` cannot automate login** — reCAPTCHA blocks it. Copy the browser cookies `T` and `Y` from `https://finance.yahoo.com` and pass them to `set_login_cookies`. `check_login()` re-queries live each call.

- **`repair=True` adds a `Repaired?` column** and fixes Yahoo price errors (100x unit mixups, missing rows, bad dividend/split adjustments, split-like level shifts). After a repair, read the true currency from `Ticker.history_metadata['currency']`, **not** `Ticker.info`. Repair needs the `repair` extra (`scipy`, `scikit-learn`).

- **Locale translation is narrow** — `yf.config.locale` only changes names for tickers *natively listed* in that locale; `Ticker("AAPL")` keeps returning `"Apple Inc."` under `ja-JP`.

- **`Calendars()` default window** — no-arg construction covers *today → today + 7 days*. Pass explicit `start`/`end` (`str`/`date`/`datetime`) for other windows; only `start` adds 7 days, only `end` uses today as start.

- **`screen()` count vs size** — predefined queries use `count` (default 25), custom queries use `size` (default 100); both cap at 250 results.

- **Multi-ticker `download()` returns a MultiIndex DataFrame** — columns are multi-level (ticker × OHLCV) by default (`multi_level_index=True` in 1.8.0). Address both levels before saving to CSV.

- **`Ticker.options` is not the chain** — it is a tuple of expiration date strings; pass one to `option_chain(date)` to get calls/puts/underlying DataFrames.

- **`yf.set_config()` is deprecated** — set `yf.config.network.proxy` / `yf.config.network.retries` directly.

- **Yahoo Finance data is for personal use only** — yfinance is not affiliated with Yahoo; respect Yahoo's terms of use for the downloaded data.

- **Async WebSocket in Jupyter** — apply `nest_asyncio` before running async streaming code, or nested event loops will error.

## References

- [01-ticker-api](references/01-ticker-api.md) — Full `Ticker`/`Tickers` property & method reference, `FastInfo` fields, `history()`/`download()` parameter tables
- [02-screening-calendars](references/02-screening-calendars.md) — Screener query operators, predefined queries, `screen()` params; `Calendars` API and recipes
- [03-advanced](references/03-advanced.md) — WebSocket internals, Auth cookie procedure, Market regions, config/caching/logging, price adjustment & repair, install variants
