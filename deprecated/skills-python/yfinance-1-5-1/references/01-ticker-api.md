# Ticker API Reference — yfinance 1.5.1

## Table of Contents

- [Properties](#properties)
- [Methods](#methods)
- [FastInfo](#fastinfo)
- [History Parameters](#history-parameters)
- [Download Parameters](#download-parameters)
- [Data Shapes](#data-shapes)

## Properties

All properties on `Ticker` objects are lazily fetched on first access and cached.

### Price & Market Data

| Property | Returns | Description |
|---|---|---|
| `history(...)` | `pd.DataFrame` | Historical OHLCV data (see [History Parameters](#history-parameters)) |
| `history_metadata` | `dict` | Raw metadata from Yahoo's chart API |
| `fast_info` | `FastInfo` | Lightweight accessor for common fields |
| `info` | `dict` | Full quote summary (company name, sector, market cap, ratios, etc.) |
| `dividends` | `pd.Series` | Dividend payments indexed by date |
| `splits` | `pd.Series` | Stock split ratios indexed by date |
| `capital_gains` | `pd.Series` | Capital gains distributions (mainly for ETFs/mutual funds) |
| `actions` | `pd.DataFrame` | Combined dividends + splits + capital gains |
| `shares` | `pd.DataFrame` | Share count history |

### Financial Statements

| Property | Returns | Description |
|---|---|---|
| `income_stmt` | `pd.DataFrame` | Annual income statement |
| `quarterly_income_stmt` | `pd.DataFrame` | Quarterly income statement |
| `ttm_income_stmt` | `pd.DataFrame` | Trailing twelve months income statement |
| `incomestmt` | `pd.DataFrame` | Alias for `income_stmt` |
| `quarterly_incomestmt` | `pd.DataFrame` | Alias for `quarterly_income_stmt` |
| `ttm_incomestmt` | `pd.DataFrame` | Alias for `ttm_income_stmt` |
| `financials` | `pd.DataFrame` | Alias for `income_stmt` |
| `quarterly_financials` | `pd.DataFrame` | Alias for `quarterly_income_stmt` |
| `ttm_financials` | `pd.DataFrame` | Alias for `ttm_income_stmt` |
| `balance_sheet` | `pd.DataFrame` | Annual balance sheet |
| `quarterly_balance_sheet` | `pd.DataFrame` | Quarterly balance sheet |
| `balancesheet` | `pd.DataFrame` | Alias for `balance_sheet` |
| `quarterly_balancesheet` | `pd.DataFrame` | Alias for `quarterly_balance_sheet` |
| `cash_flow` | `pd.DataFrame` | Annual cash flow statement |
| `quarterly_cash_flow` | `pd.DataFrame` | Quarterly cash flow statement |
| `cashflow` | `pd.DataFrame` | Alias for `cash_flow` |
| `quarterly_cashflow` | `pd.DataFrame` | Alias for `quarterly_cash_flow` |
| `ttm_cash_flow` | `pd.DataFrame` | TTM cash flow statement |
| `ttm_cashflow` | `pd.DataFrame` | Alias for `ttm_cash_flow` |
| `earnings` | `pd.DataFrame` | Yearly earnings (Revenue, Earnings) |
| `quarterly_earnings` | `pd.DataFrame` | Quarterly earnings |
| `valuation` | `pd.DataFrame` | Valuation measures (Market Cap, P/E, P/S, P/B, EV/Revenue, EV/EBITDA) |

### Analyst & Estimates

| Property | Returns | Description |
|---|---|---|
| `recommendations` | `pd.DataFrame` | Analyst recommendations (firm, toGrade, fromGrade, action, date) |
| `recommendations_summary` | `pd.DataFrame` | Summary of recommendation counts over time |
| `upgrades_downgrades` | `pd.DataFrame` | Recent upgrades and downgrades |
| `analyst_price_targets` | `dict` | Current/target/low/high/mean/median price targets |
| `earnings_estimate` | `pd.DataFrame` | EPS estimates by period |
| `revenue_estimate` | `pd.DataFrame` | Revenue estimates by period |
| `earnings_history` | `pd.DataFrame` | Past earnings surprises |
| `eps_trend` | `pd.DataFrame` | EPS trend and revisions |
| `eps_revisions` | `pd.DataFrame` | Up/down EPS revisions |
| `growth_estimates` | `pd.DataFrame` | Growth rate estimates |

### Holdings & Ownership

| Property | Returns | Description |
|---|---|---|
| `major_holders` | `pd.DataFrame` | Major holder percentages |
| `institutional_holders` | `pd.DataFrame` | Institutional ownership details |
| `mutualfund_holders` | `pd.DataFrame` | Mutual fund ownership details |
| `insider_purchases` | `pd.DataFrame` | Recent insider purchases |
| `insider_transactions` | `pd.DataFrame` | All insider transactions |
| `insider_roster_holders` | `pd.DataFrame` | Insider roster with shares held |

### Options

| Property | Returns | Description |
|---|---|---|
| `options` | `tuple[str]` | Available option expiration dates |
| `option_chain(date)` | `dict` | Calls and Puts DataFrames for given expiration |

### Other

| Property | Returns | Description |
|---|---|---|
| `earnings_dates` | `pd.DataFrame` | Upcoming and past earnings dates with surprises |
| `sustainability` | `pd.DataFrame` | ESG scores and social responsibility ratings |
| `news` | `list[dict]` | Recent news articles |
| `isin` | `str` | ISIN code for the instrument |
| `calendar` | `dict` | Earnings calendar events |
| `sec_filings` | `dict` | SEC filing URLs and descriptions |
| `funds_data` | `FundsData` | Fund-specific data (for mutual funds/ETFs) |

## Methods

### `history(period, interval, start, end, ...)`

Fetch historical price data. See [History Parameters](#history-parameters).

### `live(message_handler=None, verbose=True)`

Start live WebSocket streaming for this ticker. Blocks until disconnected.

### `get_*` Methods

All properties have corresponding `get_*` methods that accept `as_dict=True/False`:

- `get_history_metadata()`
- `get_recommendations(as_dict=False)`
- `get_recommendations_summary(as_dict=False)`
- `get_upgrades_downgrades(as_dict=False)`
- `get_calendar()`
- `get_sec_filings()`
- `get_major_holders(as_dict=False)`
- `get_institutional_holders(as_dict=False)`
- `get_mutualfund_holders(as_dict=False)`
- `get_insider_purchases(as_dict=False)`
- `get_insider_transactions(as_dict=False)`
- `get_insider_roster_holders(as_dict=False)`
- `get_info()`
- `get_fast_info()`
- `get_valuation_measures(freq="quarterly", periods=5)`
- `get_sustainability(as_dict=False)`
- `get_analyst_price_targets()`
- `get_earnings_estimate(as_dict=False)`
- `get_revenue_estimate(as_dict=False)`
- `get_earnings_history(as_dict=False)`
- `get_eps_trend(as_dict=False)`
- `get_eps_revisions(as_dict=False)`
- `get_growth_estimates(as_dict=False)`
- `get_earnings(as_dict=False, freq="yearly")`
- `get_income_stmt(as_dict=False, pretty=False, freq="yearly")`
- `get_balance_sheet(as_dict=False, pretty=False, freq="yearly")`
- `get_cash_flow(as_dict=False, pretty=False, freq="yearly")`
- `get_dividends(period="max")`
- `get_capital_gains(period="max")`
- `get_splits(period="max")`
- `get_actions(period="max")`
- `get_shares(as_dict=False)`
- `get_shares_full(start=None, end=None)` — extended share count history
- `get_isin()`
- `get_news(count=10, tab="news")`
- `get_earnings_dates(limit=12, offset=0)`
- `get_funds_data()`

## FastInfo

`FastInfo` is a lightweight dict-like accessor that fetches common fields from a fast endpoint instead of the full quote summary page.

| Attribute | Description |
|---|---|
| `currency` | Trading currency (e.g., "USD") |
| `quote_type` | Type (e.g., "EQUITY", "MUTUALFUND", "ETF") |
| `exchange` | Exchange identifier |
| `timezone` | Exchange timezone |
| `shares` | Shares outstanding |
| `market_cap` | Market capitalization |
| `last_price` | Last trade price |
| `previous_close` | Previous day close |
| `open` | Today's open |
| `day_high` | Today's high |
| `day_low` | Today's low |
| `last_volume` | Today's volume |
| `regular_market_previous_close` | Regular market previous close |
| `fifty_day_average` | 50-day moving average |
| `two_hundred_day_average` | 200-day moving average |
| `ten_day_average_volume` | 10-day average volume |
| `three_month_average_volume` | 3-month average volume |
| `year_high` | 52-week high |
| `year_low` | 52-week low |
| `year_change` | Year-to-date price change |

Both snake_case and camelCase keys are supported (e.g., `fast_info.market_cap` and `fast_info["marketCap"]`).

## History Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `period` | `str` | `"1mo"` | Valid: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max` |
| `interval` | `str` | `"1d"` | Valid: `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h`, `1d`, `5d`, `1wk`, `1mo`, `3mo` |
| `start` | `str`/`datetime` | `None` | Start date (YYYY-MM-DD), inclusive |
| `end` | `str`/`datetime` | `None` | End date (YYYY-MM-DD), exclusive |
| `prepost` | `bool` | `False` | Include pre/post market data |
| `actions` | `bool` | `True` | Include dividends and splits in DataFrame |
| `auto_adjust` | `bool` | `True` | Adjust OHLC for splits/dividends (forward) |
| `back_adjust` | `bool` | `False` | Back-adjust prices to mimic historical values |
| `repair` | `bool` | `False` | Auto-fix known Yahoo data errors (100x, missing bars) |
| `keepna` | `bool` | `False` | Keep NaN rows from Yahoo |
| `rounding` | `bool` | `False` | Round to 2 decimal places |
| `timeout` | `int` | `10` | Request timeout in seconds |

### Interval Compatibility

- **Intraday** (`1m`–`1h`): max 60 days of data
- **Daily** (`1d`): full history available
- **Weekly** (`1wk`): full history available
- **Monthly** (`1mo`, `3mo`): full history available
- **`5d`**: special interval, not supported with `repair=True`

## Download Parameters

`yf.download()` accepts all `history()` parameters plus:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `tickers` | `str`/`list` | — | Ticker symbol(s) |
| `threads` | `bool` | `True` | Download tickers in parallel |
| `group_by` | `str` | `"column"` | `"column"` (columns per ticker) or `"ticker"` (MultiIndex) |
| `progress` | `bool` | `True` | Show progress bar |
| `ignore_tz` | `bool` | `None` | Ignore timezone differences |
| `session` | `Session` | `None` | Custom requests session |
| `multi_level_index` | `bool` | `True` | Use MultiIndex columns when multiple tickers |

## Data Shapes

### `history()` Return

```
                           Open        High  ...     Volume  Dividends
Date                                         ...
2024-01-02  187.150006  188.449997  ...  82488200          0
2024-01-03  186.549988  187.059998  ...  58414460          0
```

Columns: `Open`, `High`, `Low`, `Close`, `Volume`, `Dividends`, `Stock Splits`

### `download()` with `group_by="column"`

```
             AAPL                 MSFT
             Open   High   ... Volume  Open   High   ... Volume
Date
2024-01-02  187.15 188.45  ... 82488200  373.50 375.20  ... 25000000
```

### `download()` with `group_by="ticker"`

MultiIndex columns: `(ticker, OHLCV_field)`.

### Financial Statements

```
                           2023      2022      2021
Total Revenue       383285000  394328000  365817000
Cost Of Revenue     214139000  223546000  201144000
Gross Profit        169146000  170782000  164673000
```

Index is the fiscal period (year or quarter), columns are line items.
