# Screening & Calendars — yfinance 1.8.0

## Table of Contents

- [Screener](#screener)
- [Query Classes](#query-classes)
- [Operators](#operators)
- [screen() Parameters](#screen-parameters)
- [Predefined Queries](#predefined-queries)
- [Calendars](#calendars)
- [Calendars Examples](#calendars-examples)

## Screener

yfinance's screener runs queries against Yahoo's screener endpoint. Three query classes target different asset universes:

- `EquityQuery` — stocks
- `FundQuery` — mutual funds
- `ETFQuery` — ETFs

```python
import yfinance as yf
from yfinance import EquityQuery, FundQuery, ETFQuery, screen
```

## Query Classes

Query classes build a nested tree of (operator, operands):

```python
q = EquityQuery("and", [
    EquityQuery("eq", ["region", "us"]),
    EquityQuery("gte", ["intradaymarketcap", 1_000_000_000]),
    EquityQuery("gt", ["percentchange", 3]),
])
results = screen(q)
```

- `QueryBase(operator, operand)` — `operand` is a list of sub-queries for `and`/`or`, or a list of field/value pairs for comparison operators
- `query.append(operand)` — add an operand to an existing query
- `query.to_dict()` — serialize to the JSON payload dict
- `query.is_empty()` — check for empty query

### Discovering valid fields & values

Documented attributes (see `yfinance.screener` reference):

- `EquityQuery.valid_fields` — supported operand values for the query (filter fields)
- `EquityQuery.valid_values` — supported `EQ` query operand parameters

Same attributes exist on `FundQuery` and `ETFQuery`. Print them in a REPL to list what Yahoo currently supports:

```python
print(EquityQuery.valid_fields)
print(EquityQuery.valid_values)
```

## Operators

Operators observed in the bundled predefined queries: `and`, `is-in`, `eq`, `gt`, `gte`, `lt`, `btwn`. A validator for `or` also exists in the query class. Operand shapes:

| Operator | Operand shape | Example |
|---|---|---|
| `and` / `or` | list of sub-queries | `EquityQuery("and", [q1, q2, q3])` |
| `eq` | `[field, value]` | `EquityQuery("eq", ["region", "us"])` |
| `gt` / `gte` / `lt` / `lte` | `[field, number]` | `EquityQuery("gt", ["percentchange", 3])` |
| `btwn` | `[field, low, high]` | `EquityQuery("btwn", ["peratio.lasttwelvemonths", 0, 20])` |
| `is-in` | `[field, value1, value2, ...]` | `EquityQuery("is-in", ["exchange", "NMS", "NYQ"])` |

## screen() Parameters

`screen(query, offset=None, size=None, count=None, sortField=None, sortAsc=None, userId=None, userIdType=None, session=None)`

| Parameter | Default | Notes |
|---|---|---|
| `query` | — | Name of a predefined query (str) or a `EquityQuery` / `FundQuery` / `ETFQuery` object |
| `offset` | `0` | Result offset |
| `size` | `100` | Number of results for **custom** queries. Max 250 (Yahoo). Do not use for predefined |
| `count` | `25` | Number of results for **predefined** queries. Max 250 (Yahoo). Do not use for custom |
| `sortField` | predefined-specific | Sort field name |
| `sortAsc` | predefined-specific | Sort direction |
| `userId` / `userIdType` | `""` / `"guid"` | Reserved for authenticated (premium) screens |
| `session` | `None` | `requests.Session` |

Predefined queries already carry their own `sortField` / `sortType` / `count` defaults; passing `count` overrides the result count. For custom queries the `offset`/`size` pair controls paging.

## Predefined Queries

19 built-in screens. List names programmatically: `yf.PREDEFINED_SCREENER_QUERIES.keys()`.

| Name | Universe | Query gist |
|---|---|---|
| `day_gainers` | Equity | US large-caps up > 3%, price ≥ 5, volume > 15k |
| `day_losers` | Equity | US large-caps down < -2.5%, price ≥ 5, volume > 20k |
| `most_actives` | Equity | US, market cap ≥ $2B, volume > 5M |
| `most_shorted_stocks` | Equity | US, price > 1, 3M avg daily vol > 200k |
| `aggressive_small_caps` | Equity | NMS/NYQ, EPS growth (TTM) < 15% |
| `growth_technology_stocks` | Equity | Tech sector, quarterly revenue growth ≥ 25%, EPS growth ≥ 25% |
| `small_cap_gainers` | Equity | NMS/NYQ, market cap < $2B |
| `undervalued_growth_stocks` | Equity | P/E (TTM) 0-20, PEG (5y) < 1, EPS growth ≥ 25% |
| `undervalued_large_caps` | Equity | Undervalued growth + market cap $10B-$100B |
| `conservative_foreign_funds` | Fund | Foreign Large/Small-Mid categories, rating 4-5, risk 1-3 |
| `high_yield_bond` | Fund | High Yield Bond category, rating 4-5, risk 1-3 |
| `portfolio_anchors` | Fund | Large Blend, rating 4-5, risk 1-3 |
| `solid_large_growth_funds` | Fund | Large Growth, rating 4-5, risk 1-3 |
| `solid_midcap_growth_funds` | Fund | Mid-Cap Growth, rating 4-5, risk 1-3 |
| `top_mutual_funds` | Fund | NAS, price > 15, rating 4-5, initial investment > 1k |
| `top_etfs_us` | ETF | US, price > 10, rating 4-5 |
| `top_performing_etfs` | ETF | US, price > 10, rating 4-5 (sorted by expense ratio) |
| `technology_etfs` | ETF | US, category Technology |
| `bond_etfs` | ETF | US, bond categories (short/long/inflation-protected/world/...) |

Usage:

```python
results = screen("day_gainers")
results = screen("most_actives", count=50)
```

## Calendars

The `Calendars` class (new top-level API in the 1.x line) fetches upcoming-event calendars from Yahoo: earnings, IPO, splits, economic events.

```python
import yfinance as yf

cal = yf.Calendars()                      # default: today → today + 7 days
cal = yf.Calendars(start, end)            # explicit window (str / date / datetime)
cal = yf.Calendars(end=tomorrow)          # only end → start defaults to today
cal = yf.Calendars(session=my_session)    # pass a requests.Session
```

Constructor signature: `Calendars(start=None, end=None, session=None)`.

### Properties (fetch on access)

| Property | Returns | Description |
|---|---|---|
| `earnings_calendar` | `pd.DataFrame` | Earnings events in the window |
| `ipo_info_calendar` | `pd.DataFrame` | Upcoming IPOs |
| `splits_calendar` | `pd.DataFrame` | Upcoming stock splits |
| `economic_events_calendar` | `pd.DataFrame` | Scheduled economic events (CPI, FOMC, ...) |

### Methods (explicit fetch)

`get_earnings_calendar(...)`, `get_ipo_info_calendar()`, `get_splits_calendar()`, `get_economic_events_calendar()` — same data as the properties but fetched on demand. `get_earnings_calendar` accepts filters:

| Parameter | Notes |
|---|---|
| `market_cap` | Filter out small-caps below this market cap |
| `filter_most_active` | Only actively-traded symbols (uses `screen("MOST_ACTIVES")` internally) |
| `limit` | Max rows to return |

### Calendars Examples

From the documented example (`calendars.py`):

```python
import yfinance as yf
from datetime import datetime, timedelta

# Default init (today + 7 days)
calendar = yf.Calendars()

# Today's events: calendar of 1 day
tomorrow = datetime.now() + timedelta(days=1)
calendar = yf.Calendars(end=tomorrow)

# Default calendar queries - accessing the properties will fetch the data from YF
calendar.earnings_calendar
calendar.ipo_info_calendar
calendar.splits_calendar
calendar.economic_events_calendar

# Manual queries
calendar.get_earnings_calendar()
calendar.get_ipo_info_calendar()
calendar.get_economic_events_calendar()

# Earnings calendar custom filters
calendar.get_earnings_calendar(
    market_cap=100_000_000,    # filter out small-cap
    filter_most_active=True,   # show only actively traded. Uses: `screen(query="MOST_ACTIVES")`
)

# Example of real use case:
# Get imminent unreported earnings events
today = datetime.now()
is_friday = today.weekday() == 4
day_after_tomorrow = today + timedelta(days=4 if is_friday else 2)

calendar = yf.Calendars(today, day_after_tomorrow)
df = calendar.get_earnings_calendar(limit=100)

unreported_df = df[df["Reported EPS"].isnull()]
```
