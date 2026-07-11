---
name: fredapi-0-5-2
description: >
  fredapi 0.5.2 — Python wrapper for the Federal Reserve Economic Data (FRED) API
  from the St. Louis Fed. Use when fetching US macroeconomic time series (GDP, CPI,
  unemployment, interest rates, etc.), searching FRED series by keyword, browsing
  series by release or category, or working with data revisions via ALFRED
  (point-in-time / vintage data). Returns pandas Series/DataFrame. Requires a free
  FRED API key. Trigger on: FRED, Federal Reserve Economic Data, St. Louis Fed,
  fredapi, macroeconomic data, US economic indicators, vintage data, data revisions.
metadata:
  tags:
    - python
    - data
    - economics
    - macro
    - fred
---

# fredapi 0.5.2

## Overview

fredapi is a Python wrapper around the [FRED API](https://api.stlouisfed.org/docs/fred/) from the Federal Reserve Bank of St. Louis. It provides convenient access to thousands of US and international economic time series, returning data as `pandas` `Series` or `DataFrame`.

### Key Capabilities

- **Time series retrieval** — `get_series()` fetches latest data for any FRED series ID
- **Series metadata** — `get_series_info()` returns title, frequency, units, date range
- **Full-text search** — `search()` finds series by keyword with sorting and filtering
- **Browse by release or category** — `search_by_release()` / `search_by_category()`
- **Data revisions (ALFRED)** — `get_series_first_release()`, `get_series_all_releases()`, `get_series_as_of_date()`, `get_series_vintage_dates()` for point-in-time analysis

### Dependencies

Install via `pip install fredapi`. Runtime dependency: `pandas`.

### Authentication

A free FRED API key is required. Obtain one at [api.stlouisfed.org/api_key.html](http://api.stlouisfed.org/api_key.html). Set it via:

- Environment variable: `FRED_API_KEY`
- Direct parameter: `Fred(api_key='your_key')`
- Key file: `Fred(api_key_file='/path/to/keyfile')`

## Usage

### Basic Setup

```python
from fredapi import Fred

# Via environment variable (recommended)
fred = Fred()

# Or pass directly
fred = Fred(api_key='your_api_key')

# Via key file (first line of file)
fred = Fred(api_key_file='.fred_api_key')

# With proxies
fred = Fred(proxies={'http': 'http://proxy:8080', 'https': 'http://proxy:8080'})
```

### Fetching Time Series

```python
# Latest data for a series
data = fred.get_series('SP500')  # S&P 500

# With date range
data = fred.get_series('GDP', observation_start='2000-01-01', observation_end='2020-12-31')

# Date strings are parsed by pandas (flexible formats)
data = fred.get_series('CPIAUCSL', observation_start='1/1/2010')

# Extra FRED parameters (e.g. transform, sort order)
data = fred.get_series('GDP', transform='pcap')  # percent change from a year ago
```

### Series Metadata

```python
# Get info about a series (title, frequency, units, notes, etc.)
info = fred.get_series_info('PAYEMS')
print(info['title'])          # "All Employees: Total Nonfarm Payrolls"
print(info['frequency'])      # "Monthly"
print(info['units'])          # "Thousands of Persons"
print(info['observation_start'])
print(info['observation_end'])
```

### Searching

```python
# Full-text search
results = fred.search('real gdp')
print(results[['title', 'frequency', 'units']])

# With limit, ordering, and sorting
results = fred.search('unemployment', limit=10, order_by='popularity', sort_order='desc')

# Filter by frequency
results = fred.search('inflation', filter=('frequency', 'Monthly'))

# Filter by units
results = fred.search('gdp', filter=('units', 'Billions of Dollars'))

# Filter by seasonal adjustment
results = fred.search('retail sales', filter=('seasonal_adjustment', 'Seasonally Adjusted'))
```

### Browse by Release or Category

```python
# Series in a specific release (e.g. release 151 = G.18 Financial Services)
series = fred.search_by_release(151, limit=20)

# Series in a specific category
series = fred.search_by_category(32145, limit=50)

# With ordering
series = fred.search_by_release(175, order_by='series_id', sort_order='asc')
```

### Data Revisions (ALFRED / Point-in-Time)

```python
# First release only (ignores all revisions)
first = fred.get_series_first_release('GDP')

# All releases and revisions (DataFrame with date, realtime_start, value)
all_releases = fred.get_series_all_releases('GDP')

# Data as known on a specific date
as_of = fred.get_series_as_of_date('GDP', '2014-06-01')

# Vintage dates (dates when revisions occurred)
vintage_dates = fred.get_series_vintage_dates('GDP')
```

## Gotchas

- **API key is mandatory** — `Fred()` raises `ValueError` if no key is found via `api_key`, `api_key_file`, or `FRED_API_KEY` environment variable.
- **`get_series()` and `get_series_latest_release()` are identical** — they call the same underlying path. Use whichever name is clearer in context.
- **NaN values are `float('NaN')`** — FRED returns `.` for missing observations; fredapi converts these to Python `NaN` (float). Use `dropna()` or `fillna()` as needed.
- **`get_series_all_releases()` returns a DataFrame, not a Series** — it has columns `date` (observation period), `realtime_start` (when the value was reported), and `value`. The index is an integer row number, not dates.
- **`get_series_first_release()` deduplicates by `date`** — it takes the first row per observation date from `get_series_all_releases()`, returning a Series indexed by date.
- **`get_series_as_of_date()` returns a DataFrame** — it filters `get_series_all_releases()` to revisions on or before the given date. Multiple rows per observation date are possible if revisions occurred before that date.
- **Date parsing is flexible** — `observation_start`/`observation_end` accept any string pandas `to_datetime` can parse (e.g., `'1/1/2020'`, `'2020-01-01'`, `'jan 2020'`). Invalid strings raise `ValueError`.
- **Search results are paginated internally** — FRED returns max 1000 results per request. fredapi automatically paginates when `limit > 1000` or `limit=0` (all results). Be mindful of API rate limits with large queries.
- **`search()` can return `None`** — if no results match, `search()` returns `None`, not an empty DataFrame. Check for `None` before accessing columns.
- **`search_by_release()` / `search_by_category()` raise on invalid ID** — they raise `ValueError` if no series exist for the given release or category ID.
- **Proxy support via environment or dict** — proxies can be passed as a dict to `Fred(proxies=...)` or set via `HTTP_PROXY`/`HTTPS_PROXY` environment variables. The latter are auto-detected.
- **No built-in retry logic** — fredapi does not retry failed requests. Wrap calls in retry logic if needed for production use.
- **Version 0.5.2 uses `urllib` directly** — it does not use `requests` or `aiohttp`. All calls are synchronous blocking I/O.

## References

- [01-api-reference](references/01-api-reference.md) — Full method reference with parameters and return types
- [02-alfred-revisions](references/02-alfred-revisions.md) — ALFRED point-in-time data, vintage dates, and revision analysis patterns
