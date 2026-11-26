# Ticker & Tickers API Reference — yfinance 1.8.0

## Table of Contents

- [Ticker Properties](#ticker-properties)
- [Ticker Methods](#ticker-methods)
- [FastInfo Fields](#fastinfo-fields)
- [Options](#options)
- [FundsData](#fundsdata)
- [Tickers (Batch)](#tickers-batch)
- [history() Parameters](#history-parameters)
- [download() Parameters](#download-parameters)

## Ticker Properties

All properties on `Ticker` objects are lazily fetched on first access and cached on the object.

### Price & Market Data

| Property | Returns | Description |
|---|---|---|
| `history(...)` | `pd.DataFrame` | Historical OHLCV data (see [history() Parameters](#history-parameters)) |
| `history_metadata` | `dict` | Raw metadata from Yahoo's chart API (currency, trading periods, ...) |
| `fast_info` | `FastInfo` | Lightweight accessor for common quote fields (see below) |
| `info` | `dict` | Full quote summary dict (name, sector, industry, market cap, ratios, ...) |
| `valuation` | `pd.DataFrame` | Valuation snapshot |
| `calendar` | `dict` | Key dates (next earnings, ex-dividend, ...) |
| `sec_filings` | `dict` | SEC filings |
| `isin` | `str` | ISIN code |
| `dividends` | `pd.Series` | Dividend payments indexed by date |
| `splits` | `pd.Series` | Stock split ratios indexed by date |
| `capital_gains` | `pd.Series` | Capital gains distributions (mainly funds) |
| `actions` | `pd.DataFrame` | Combined dividends + splits + capital gains |
| `shares` | `pd.DataFrame` | Share count data (`get_shares_full` fetches it) |
| `options` | `tuple` | Tuple of expiration date strings (NOT the chain) |
| `news` | `list` | News article list |

### Financial Statements

| Property | Returns | Description |
|---|---|---|
| `income_stmt` | `pd.DataFrame` | Annual income statement |
| `quarterly_income_stmt` | `pd.DataFrame` | Quarterly income statement |
| `ttm_income_stmt` | `pd.DataFrame` | Trailing twelve months income statement |
| `incomestmt` / `quarterly_incomestmt` / `ttm_incomestmt` | `pd.DataFrame` | Aliases of the above |
| `financials` / `quarterly_financials` / `ttm_financials` | `pd.DataFrame` | Aliases of the income-statement statements |
| `balance_sheet` | `pd.DataFrame` | Annual balance sheet |
| `quarterly_balance_sheet` | `pd.DataFrame` | Quarterly balance sheet |
| `balancesheet` / `quarterly_balancesheet` | `pd.DataFrame` | Aliases |
| `cash_flow` | `pd.DataFrame` | Annual cash flow |
| `quarterly_cash_flow` | `pd.DataFrame` | Quarterly cash flow |
| `ttm_cash_flow` | `pd.DataFrame` | TTM cash flow |
| `cashflow` / `quarterly_cashflow` / `ttm_cashflow` | `pd.DataFrame` | Aliases |

### Analysis & Estimates

| Property | Returns | Description |
|---|---|---|
| `earnings` | `pd.DataFrame` | Yearly earnings |
| `quarterly_earnings` | `pd.DataFrame` | Quarterly earnings |
| `earnings_dates` | `pd.DataFrame` | Earnings announcement dates (past + upcoming) |
| `analyst_price_targets` | `dict` | Analyst price target summary |
| `earnings_estimate` | `pd.DataFrame` | EPS estimates |
| `revenue_estimate` | `pd.DataFrame` | Revenue estimates |
| `earnings_history` | `pd.DataFrame` | Beat/miss history |
| `eps_trend` | `pd.DataFrame` | EPS trend |
| `eps_revisions` | `pd.DataFrame` | EPS revisions |
| `growth_estimates` | `pd.DataFrame` | Growth estimates |
| `recommendations` | `pd.DataFrame` | Recommendation table |
| `recommendations_summary` | `pd.DataFrame` | Recommendation summary |
| `upgrades_downgrades` | `pd.DataFrame` | Upgrade/downgrade history |
| `sustainability` | `pd.DataFrame` | ESG / sustainability scores |

### Holdings

| Property | Returns | Description |
|---|---|---|
| `major_holders` | `pd.DataFrame` | Major holders |
| `institutional_holders` | `pd.DataFrame` | Institutional holders |
| `mutualfund_holders` | `pd.DataFrame` | Mutual fund holders |
| `insider_purchases` | `pd.DataFrame` | Insider purchase summary |
| `insider_transactions` | `pd.DataFrame` | Insider transaction detail |
| `insider_roster_holders` | `pd.DataFrame` | Insider roster |
| `funds_data` | `FundsData` | Fund data object for ETFs / mutual funds (see [FundsData](#fundsdata)) |

## Ticker Methods

The canonical getter `get_<name>(...)` and the property `<name>` are equivalent (property caches, method refetches). Methods accept a `proxy=` argument for per-call proxying (see [03-advanced](03-advanced.md)).

| Method | Notes |
|---|---|
| `history(...)` | Historical prices — see parameters below |
| `option_chain(date=None, tz=None)` | Returns `OptionsTuple(calls, puts, underlying)`; `date` must be one of `ticker.options` |
| `live(message_handler=None, verbose=True)` | Stream live quotes for this single ticker via WebSocket |
| `get_history_metadata()` | Raw chart API metadata |
| `get_isin()` / `get_info()` / `get_fast_info()` | Fetchers behind the `isin` / `info` / `fast_info` properties |
| `get_dividends()` / `get_splits()` / `get_actions()` / `get_capital_gains()` | Price-action fetchers |
| `get_shares_full()` | Share count fetcher |
| `get_news()` | News fetcher |
| `get_income_stmt()` / `get_balance_sheet()` / `get_cashflow()` | Statement fetchers |
| `get_earnings()` / `get_earnings_dates()` | Earnings fetchers |
| `get_sec_filings()` | SEC filings fetcher |

## FastInfo Fields

`Ticker.fast_info` imitates a dict and fetches faster than `.info` for common fields. Properties (snake_case; camelCase also accepted):

`currency`, `quote_type`, `exchange`, `timezone`, `shares`, `market_cap`, `last_price`, `previous_close`, `open`, `day_high`, `day_low`, `regular_market_previous_close`, `last_volume`, `fifty_day_average`, `two_hundred_day_average`, `ten_day_average_volume`, `three_month_average_volume`, `year_high`, `year_low`, `year_change`

`fast_info.keys()` lists the public keys.

## Options

```python
t = yf.Ticker("AAPL")
t.options                 # ('2025-01-17', '2025-02-21', ...) — expiration strings
chain = t.option_chain(t.options[0])
chain.calls               # pd.DataFrame
chain.puts                # pd.DataFrame
chain.underlying          # underlying quote
```

## FundsData

`Ticker.funds_data` (for ETFs / mutual funds). Holdings-related fields return `pd.DataFrame`.

| Field | Description |
|---|---|
| `description` | Fund description |
| `fund_overview` | Operational information |
| `fund_operations` | Operational information |
| `asset_classes` | Asset class breakdown |
| `top_holdings` | Top holdings table |
| `equity_holdings` | Equity holdings |
| `bond_holdings` | Bond holdings |
| `bond_ratings` | Bond ratings |
| `sector_weightings` | Sector weightings |

## Tickers (Batch)

`yf.Tickers('msft aapl goog')` — accepts a space- or comma-separated string or a list; symbols are uppercased.

| Member | Returns | Description |
|---|---|---|
| `tickers` | `dict` | symbol → `Ticker` object |
| `symbols` | `list` | Upper-cased symbols |
| `info` / `get_info(threads=True, progress=False)` | `dict` | symbol → info dict, fetched **in parallel** (new in 1.8.0) |
| `calendar` | `pd.DataFrame` | One row per ticker (new in 1.8.0) |
| `history(...)` / `download(...)` | `pd.DataFrame` | Multi-ticker history; groups by ticker internally, re-swap to column groups on request |
| `live(message_handler=None, verbose=True)` | — | Stream live quotes for all symbols in one WebSocket |

Passing `threads=2` (a smaller integer) is gentler on Yahoo's rate limit.

## history() Parameters

`Ticker.history(...)` / `PriceHistory.history(...)` signature:

| Parameter | Default | Notes |
|---|---|---|
| `period` | `'1mo'` if start & end None | Valid: `1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max`; can combine with start/end e.g. `end = start + period` |
| `interval` | `"1d"` | Valid: `1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo`. Intraday limited to last 60 days. `30m` fetched as `15m` and resampled (Yahoo API bug workaround) |
| `start` | 99 years ago | `YYYY-MM-DD` string or datetime, **inclusive** |
| `end` | now | `YYYY-MM-DD` string or datetime, **exclusive** |
| `prepost` | `False` | Include pre/post market data |
| `actions` | `True` | Include dividend/split/capital-gain action columns |
| `auto_adjust` | `True` | Adjust all OHLC (see [03-advanced: Price Adjustment](03-advanced.md#price-adjustment)) |
| `back_adjust` | `False` | Back-adjusted data to mimic true historical prices |
| `repair` | `False` | Detect & repair Yahoo price errors (see [03-advanced: Price Repair](03-advanced.md#price-repair)) |
| `keepna` | `False` | Keep NaN rows returned by Yahoo |
| `rounding` | `False` | Round prices to Yahoo-suggested precision (dividends/splits/capital gains are not rounded) |
| `timeout` | `10` | Timeout fetches after N seconds |
| `raise_errors` | `False` | Raise exceptions on error |

## download() Parameters

`yf.download(tickers, ...)` full signature (1.8.0):

| Parameter | Default | Notes |
|---|---|---|
| `tickers` | — | str (space-separated) or list |
| `start` | 99 years ago | Inclusive |
| `end` | now | Exclusive |
| `actions` | `False` | Download dividend + stock split data |
| `threads` | `True` | Parallel download; in 1.8.0 `threads=N` is a hard concurrency cap |
| `ignore_tz` | `None` | Ignore timezone handling |
| `group_by` | `'column'` | `'ticker'` or `'column'` |
| `auto_adjust` | `True` | Adjust OHLC automatically |
| `back_adjust` | `False` | Back-adjusted data |
| `repair` | `False` | Detect currency unit 100x mixups and attempt repair (see [03-advanced](03-advanced.md#price-repair)) |
| `keepna` | `False` | Keep NaN rows |
| `progress` | `True` | Show progress bar |
| `period` | `'1mo'` if start & end None | Same valid values as `history()` |
| `interval` | `"1d"` | Same valid values as `history()` |
| `prepost` | `False` | Include pre/post market data |
| `rounding` | `False` | Round prices (only price columns) |
| `timeout` | `10` | Per-request timeout |
| `session` | `None` | `requests.Session` for connection reuse |
| `multi_level_index` | `True` | Multi-level column index for multi-ticker results |
