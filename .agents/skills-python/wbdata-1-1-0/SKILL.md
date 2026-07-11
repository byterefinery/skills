---
name: wbdata-1-1-0
description: Python library (wbdata 1.1.0) for querying World Bank development data via the World Bank API. Use when the user needs to fetch country-level economic, social, or demographic indicators from the World Bank, or when working with wbdata in Python code. Supports raw data as dicts, and pandas Series/DataFrame when pandas is installed.
metadata:
  tags:
    - python
    - data
    - world-bank
    - economics
---

# wbdata 1.1.0

## Overview

wbdata is a Python library that wraps the [World Bank API](https://data.worldbank.org/developers/api-overview) for retrieving development indicators. It provides module-level convenience functions backed by a cached `Client`, returning data as lists of dicts or (with pandas) as `Series`/`DataFrame`.

Key capabilities:

- Retrieve indicator values for countries and date ranges via `get_data()`
- Search and filter countries, indicators, sources, topics, income levels, and lending types
- Optional pandas integration via `get_series()` and `get_dataframe()`
- Persistent disk cache with configurable TTL and max size
- Flexible date parsing (year, month, quarter, natural language via `dateparser`)

## Usage

Install with pip (pandas is optional, needed only for `get_series`/`get_dataframe`):

```python
pip install wbdata
# or with pandas support:
pip install wbdata[pandas]
```

Core workflow — find an indicator, get data:

```python
import wbdata

# Search for indicators by keyword
wbdata.get_indicators(query="gdp per capita", source=2)

# Get raw data (list of dicts)
data = wbdata.get_data("NY.GDP.PCAP.CD", country="USA", date=("2015", "2020"))

# Get as pandas Series
series = wbdata.get_series("NY.GDP.PCAP.CD", country="USA", date=("2015", "2020"))

# Get multiple indicators as a merged DataFrame
indicators = {"NY.GDP.PCAP.CD": "gdp", "SP.POP.TOTL": "population"}
df = wbdata.get_dataframe(indicators, country=["USA", "GBR"], date=("2015", "2020"))
```

Find countries and filter by aggregate:

```python
# Search countries by name regex
wbdata.get_countries(query="united")

# Get all high-income countries
high_income = [c["id"] for c in wbdata.get_countries(incomelevel="HIC")]

# Get all income levels
wbdata.get_incomelevels()
```

Custom client with explicit cache settings:

```python
from wbdata.client import Client

client = Client(cache_path="/tmp/wbdata-cache", cache_ttl_days=14, cache_max_size=200)
data = client.get_data("NY.GDP.PCAP.CD", country="USA")
```

Cache can also be controlled via environment variables:

```bash
export WBDATA_CACHE_PATH=/tmp/wbdata-cache
export WBDATA_CACHE_TTL_DAYS=14
export WBDATA_CACHE_MAX_SIZE=200
```

## Gotchas

- **`get_series` and `get_dataframe` require pandas** — they raise `RuntimeError` if pandas is not installed. Install with `pip install wbdata[pandas]` or `pip install pandas` separately.
- **`get_countries` with `country_id` cannot be combined with `query`, `incomelevel`, or `lendingtype`** — this raises `ValueError`. Use one or the other.
- **`get_indicators` with `indicator` cannot be combined with `query`** — and you cannot specify more than one of `indicator`, `source`, `topic` at the same time.
- **`get_indicators(query=..., source=...)` works** — query filters the results from a given source. The restriction is only on `indicator` + `query`.
- **Date strings are flexible but `freq` matters** — when passing natural language dates or `datetime` objects, the `freq` parameter (`"Y"`, `"M"`, `"Q"`) determines how the date is formatted for the API. A monthly indicator queried with `freq="Y"` will be formatted as a year.
- **`parse_dates` converts in-place** — when `parse_dates=True`, the date strings in the returned data are replaced with `datetime.datetime` objects. Special values like `"MRV"` and `"-"` are left as strings.
- **`keep_levels=False` drops singleton index levels** — in `get_series`/`get_dataframe`, if only one country or one date is returned, the corresponding MultiIndex level is dropped by default. Use `keep_levels=True` to preserve the full MultiIndex structure.
- **Country codes are ISO 3-letter in responses but 2-letter in API URLs** — `get_data()` accepts either; responses contain both `country["id"]` (2-letter) and `countryiso3code` (3-letter).
- **Cache is persistent by default** — wbdata uses `shelved_cache` on disk. Use `skip_cache=True` to force a fresh fetch, or set `WBDATA_CACHE_TTL_DAYS=0` for no caching.
- **Module-level functions share a singleton client** — all top-level calls (`wbdata.get_data()`, etc.) use the same cached `Client`. Create a `Client` instance directly if you need separate cache configurations.
- **`SearchResult` is a list subclass** — metadata functions return `SearchResult` which pretty-prints as a table in interactive sessions but behaves as a regular list of dicts in code.
- **`Result` has a `last_updated` attribute** — `get_data()` returns a `Result` list with `last_updated` as a `datetime` or `None`, indicating when the World Bank last updated the data.

## References

- [01-api-reference](references/01-api-reference.md) — Full API reference for all functions, parameters, and return types
- [02-date-handling](references/02-date-handling.md) — Date format patterns, `parse_dates`, and date range examples
