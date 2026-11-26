# Advanced — yfinance 1.8.0

## Table of Contents

- [WebSocket Internals](#websocket-internals)
- [Auth — Obtaining Cookies](#auth--obtaining-cookies)
- [Market Regions](#market-regions)
- [Config](#config)
- [Caching](#caching)
- [Logging](#logging)
- [Price Adjustment](#price-adjustment)
- [Price Repair](#price-repair)
- [Multi-Level Column Index](#multi-level-column-index)
- [Proxy](#proxy)
- [Installation Variants](#installation-variants)

## WebSocket Internals

`WebSocket` (synchronous) and `AsyncWebSocket` (asynchronous) stream live prices from Yahoo's streamer endpoint (`wss://streamer.finance.yahoo.com/?version=2` by default). Both support context managers and explicit `close()`.

### Synchronous

```python
import yfinance as yf

def message_handler(message):
    print("Received message:", message)

# With context manager
with yf.WebSocket() as ws:
    ws.subscribe(["AAPL", "BTC-USD"])
    ws.listen(message_handler)

# Without context manager
ws = yf.WebSocket()
ws.subscribe(["AAPL", "BTC-USD"])
ws.listen(message_handler)
ws.close()
```

Methods: `subscribe(symbols)`, `unsubscribe(symbols)`, `listen(message_handler=None)`, `close()`. Constructor: `WebSocket(url=..., verbose=True)`.

### Asynchronous

```python
import asyncio
import yfinance as yf

def message_handler(message):
    print("Received message:", message)

async def main():
    # With context manager
    async with yf.AsyncWebSocket() as ws:
        await ws.subscribe(["AAPL", "BTC-USD"])
        await ws.listen()

    # Without context manager
    ws = yf.AsyncWebSocket()
    await ws.subscribe(["AAPL", "BTC-USD"])
    await ws.listen()
    await ws.close()

asyncio.run(main())
```

> **Jupyter note** — running async code inside a Jupyter notebook can hit nested event-loop errors. Import and apply `nest_asyncio` before running async operations:
>
> ```python
> import nest_asyncio
> nest_asyncio.apply()
> ```

### Per-ticker / per-group streaming

`Ticker.live(message_handler=None, verbose=True)` and `Tickers.live(message_handler=None, verbose=True)` wrap a `WebSocket` that subscribes to the object's symbols and blocks on `listen()`.

## Auth — Obtaining Cookies

`Auth` **cannot automate login** — Yahoo Finance requires solving a reCAPTCHA, which blocks automation. You must manually obtain the cookies `T` and `Y` from a browser session:

1. Open your browser (Chrome, Firefox, ...).
2. Log in to <https://finance.yahoo.com>.
3. Open the browser's Developer Tools — `F12` / `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac).
4. Navigate to the **Application** tab (Chrome) or **Storage** tab (Firefox).
5. In the **Cookies** section, select `https://finance.yahoo.com`.
6. Locate the cookies named **T** and **Y**.
7. Copy the values and pass them to `auth.set_login_cookies(cookie_t, cookie_y)`.

`set_login_cookies` stores the cookies, validates them with a live login check, and returns `True`/`False`. Every subsequent yfinance request then runs under the logged-in user.

| Member | Returns | Notes |
|---|---|---|
| `set_login_cookies(t, y)` | `bool` | Store + validate cookies |
| `check_login()` | `bool` | Re-queried each call, never cached |
| `subscription_tier()` | `'gold'` / `'silver'` / `'bronze'` / `'free'` / `None` | Yahoo Finance subscription tier of the logged-in account |
| `user` | `{'guid': ...}` or `None` | Logged-in user info |

## Market Regions

`Market(region)` accepts a plain string or a `MarketRegion` enum member (members are plain strings, so `MarketRegion.EUROPE == "EUROPE"`). Available regions:

`US`, `GB`, `ASIA`, `EUROPE`, `RATES`, `COMMODITIES`, `CURRENCIES`, `CRYPTOCURRENCIES`

- `Market.summary` — regional market summary; the only member that returns regional data for all regions above.
- `Market.status` — backed by Yahoo's `markettime` endpoint, which currently **ignores the `market` parameter and only returns U.S. data**. For any non-`US` market, `status` is `None` and a warning is logged.

## Config

Global config object `yf.config` (a `YfConfig`):

```
yf.config
{
  "network": { "proxy": null, "retries": 0 },
  "debug":   { "hide_exceptions": true, "logging": false },
  ...
}
```

### Network

- `yf.config.network.proxy = "PROXY_SERVER"` — proxy for all yfinance data fetches.
- `yf.config.network.retries = 2` — automatic retry for transient network errors with exponential backoff (1s, 2s, 4s...).

### Debug

- `yf.config.debug.hide_exceptions = False` — stop yfinance hiding exceptions.
- `yf.config.debug.logging = True` — enable verbose debug logging.

### Locale

Localized fields (`longName`, `shortName`, ...) follow `yf.config.locale`. Default `en-US` / `US`. Set once at session start; every subsequent v7 / v10 endpoint call (`Ticker.info`, `Ticker.fast_info`, `Ticker.calendar`, `earnings_dates`, ...) inherits it:

```python
yf.config.locale.lang = "zh-Hant-HK"
yf.config.locale.region = "HK"
yf.Ticker("1810.HK").info["longName"]    # → '小米集團－Ｗ'

yf.config.locale.lang = "ja-JP"
yf.config.locale.region = "JP"
yf.Ticker("7203.T").info["longName"]     # → 'トヨタ自動車'
```

Yahoo only returns translated values for tickers **natively listed** in that locale; `Ticker("AAPL")` keeps returning `"Apple Inc."` under `ja-JP`.

The deprecated `yf.set_config(proxy=..., retries=...)` still works but raises a `DeprecationWarning` and forwards to `yf.config.network.*`.

## Caching

yfinance stores some data locally to reduce requests to Yahoo — timezones (to localize dates) and cookies. Default cache locations:

- Windows = `C:/Users/<USER>/AppData/Local/py-yfinance`
- Linux = `/home/<USER>/.cache/py-yfinance`
- MacOS = `/Users/<USER>/Library/Caches/py-yfinance`

Direct the cache elsewhere:

```python
import yfinance as yf
yf.set_tz_cache_location("custom/cache/location")
```

## Logging

yfinance uses Python's `logging` module; by default only errors are logged. For debugging:

```python
import yfinance as yf
yf.config.debug.logging = True
```

## Price Adjustment

By default, `Ticker.history()` and `yf.download()` return prices **adjusted for splits and dividends** (`auto_adjust=True`). The `Close` column is already the *adjusted* close — there is no separate `Adj Close` column in this mode.

Pass `auto_adjust=False` to get Yahoo's split-adjusted OHLC together with an `Adj Close` column that also includes dividends.

- `auto_adjust=True` (default): `Open`, `High`, `Low`, `Close` all adjusted for splits *and* dividends — the prices you want for total-return-consistent calculations such as backtesting.
- `auto_adjust=False`: Yahoo's OHLC as returned (already split-adjusted) plus an `Adj Close` column that additionally accounts for dividends.

## Price Repair

The `repair=True` argument in `history()` and `download()` attempts to fix a variety of price errors caused by Yahoo (only US market data appears consistently clean). The returned table gets a `Repaired?` column indicating which rows were repaired.

What it can fix:

- **Missing dividend adjustment** — if a dividend is in the data but the preceding `Adj Close` equals `Close`, the dividend adjustment is applied manually. (`Repaired?` is NOT set to `True` because the fix only changes `Adj Close`.)
- **Missing split adjustment** — if a stock split is in the data but preceding prices are not adjusted, the split is applied manually. Requires the date range to include 1 day *after* the split for calibration.
- **Unexplained split-like level shift** — Yahoo sometimes multiplies all prices before a date by a split-like ratio and divides Volume by it, without any split near that date. Measured against `1h` data (which doesn't have the error) and repaired like a bad stock split; only repaired within the last 2 years. A genuine crash also appears in `1h` data, so it is not repaired.
- **Missing / corrupt data** — if price data is clearly missing or corrupt, it is reconstructed from a smaller interval (e.g. `1h`) to fix `1d` data.
- **Currency mixups** — e.g. 100x unit errors. After repair, check `Ticker.history_metadata['currency']` for the true currency — **not** `Ticker.info`.

Requires the `repair` extra: `scipy` and `scikit-learn` (`pip install yfinance[repair]`).

## Multi-Level Column Index

`yf.download()` of multiple tickers returns a `pandas.DataFrame` with **multi-level column names** — one level for the ticker, one for the price fields (Open/High/Low/Close/Volume/...). `multi_level_index=True` (default in 1.8.0) keeps this structure. When saving to CSV or subsetting, address both levels:

```python
df = yf.download("AAPL MSFT", period="1mo")
df["AAPL"]["Close"]          # single ticker's Close series
```

`group_by='ticker'` vs `'column'` controls the ordering of the two levels. For single-ticker downloads the columns are flat (no ticker level).

## Proxy

Two ways to route yfinance through a proxy:

1. **Globally** — `yf.config.network.proxy = "PROXY_SERVER"` applies to all data fetches.
2. **Per call** — many fetchers accept `proxy=` directly:

```python
import yfinance as yf
msft = yf.Ticker("MSFT")
msft.history(..., proxy="PROXY_SERVER")
msft.get_actions(proxy="PROXY_SERVER")
msft.get_dividends(proxy="PROXY_SERVER")
msft.get_splits(proxy="PROXY_SERVER")
msft.get_capital_gains(proxy="PROXY_SERVER")
msft.get_balance_sheet(proxy="PROXY_SERVER")
msft.get_cashflow(proxy="PROXY_SERVER")
msft.option_chain(..., proxy="PROXY_SERVER")
```

## Installation Variants

Default: `pip install yfinance`.

To install **without `curl_cffi`** (uses plain `requests` fallback):

```bash
curl -fsSL https://raw.githubusercontent.com/ranaroussi/yfinance/main/requirements.txt \
  | grep -vi '^curl_cffi' | pip install -r /dev/stdin
pip install --no-deps yfinance
```
