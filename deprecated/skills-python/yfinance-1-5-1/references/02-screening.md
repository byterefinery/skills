# Screening — yfinance 1.5.1

## Table of Contents

- [Overview](#overview)
- [Query Types](#query-types)
- [Operators](#operators)
- [EquityQuery Fields](#equityquery-fields)
- [FundQuery Fields](#fundquery-fields)
- [ETFQuery Fields](#etfquery-fields)
- [Examples](#examples)
- [Predefined Screeners](#predefined-screeners)

## Overview

yfinance's screener module lets you query Yahoo Finance for instruments matching specific criteria. Three query builders are available:

- **`EquityQuery`** — screen stocks (equities)
- **`FundQuery`** — screen mutual funds
- **`ETFQuery`** — screen exchange-traded funds

Queries are executed via `yf.screen(query)`, which returns a list of result dicts.

## Query Types

```python
from yfinance.screener import EquityQuery, FundQuery, ETFQuery, screen
```

Each query builder validates fields and values at construction time, raising `ValueError` for invalid inputs.

## Operators

| Operator | Operands | Description |
|---|---|---|
| `eq` | `[field, value]` | Field equals value |
| `is-in` | `[field, val1, val2, ...]` | Field is one of the values |
| `btwn` | `[field, low, high]` | Field between low and high (inclusive) |
| `gt` | `[field, value]` | Field greater than value |
| `lt` | `[field, value]` | Field less than value |
| `gte` | `[field, value]` | Field greater than or equal to value |
| `lte` | `[field, value]` | Field less than or equal to value |
| `and` | `[query1, query2, ...]` | Logical AND of sub-queries |
| `or` | `[query1, query2, ...]` | Logical OR of sub-queries |

### Building Queries

```python
# Simple query: P/E ratio between 0 and 20
q = EquityQuery("btwn", ["peratio.lasttwelvemonths", 0, 20])

# Compound query: AND of multiple conditions
q = EquityQuery("and", [
    EquityQuery("eq", ["region", "us"]),
    EquityQuery("gte", ["intradaymarketcap", 1000000000]),
    EquityQuery("gt", ["percentchange", 3]),
])

# Nested: OR within AND
q = EquityQuery("and", [
    EquityQuery("eq", ["region", "us"]),
    EquityQuery("or", [
        EquityQuery("gt", ["percentchange", 5]),
        EquityQuery("lt", ["peratio.lasttwelvemonths", 10]),
    ]),
])
```

## EquityQuery Fields

### Region & Exchange

| Field | Type | Values |
|---|---|---|
| `region` | string | `"us"`, `"uk"`, `"in"`, etc. |
| `exchange` | string | `"NMS"` (NASDAQ), `"NYQ"` (NYSE), `"ASE"` (AMEX), etc. |
| `isincode` | string | ISIN code |

### Price & Performance

| Field | Type | Description |
|---|---|---|
| `intradayprice` | float | Current intraday price |
| `percentchange` | float | Percent change |
| `regularmarketprice` | float | Regular market price |
| `regularmarketchange` | float | Regular market change |
| `regularmarketchangepercent` | float | Regular market change percent |
| `fiftytwoweeklow` | float | 52-week low |
| `fiftytwoweekhigh` | float | 52-week high |
| `fiftydayma` | float | 50-day moving average |
| `twohundreddayma` | float | 200-day moving average |

### Volume

| Field | Type | Description |
|---|---|---|
| `dayvolume` | int | Today's volume |
| `avgdailyvol3m` | int | 3-month average daily volume |
| `avgdailyvol1m` | int | 1-month average daily volume |

### Market Cap

| Field | Type | Description |
|---|---|---|
| `intradaymarketcap` | float | Current market cap |
| `marketcap` | float | Market cap |

### Valuation

| Field | Type | Description |
|---|---|---|
| `peratio.lasttwelvemonths` | float | Trailing P/E ratio |
| `peratio.nexttwelvemonths` | float | Forward P/E ratio |
| `peratio.nextfiveyears` | float | P/E ratio next 5 years |
| `pegratio_5y` | float | PEG ratio (5-year) |
| `priceovertime` | float | Price over time |
| `psratio.lasttwelvemonths` | float | Price-to-sales ratio |
| `pbratio` | float | Price-to-book ratio |
| `evarev` | float | EV/Revenue |
| `evarevebitda` | float | EV/EBITDA |

### Growth

| Field | Type | Description |
|---|---|---|
| `epsgrowth.lasttwelvemonths` | float | EPS growth (TTM) |
| `earningsgrowthquarterly` | float | Quarterly earnings growth |
| `quarterlyrevenuegrowth.quarterly` | float | Quarterly revenue growth % |
| `revenuegrowthquarterly` | float | Quarterly revenue growth |
| `salesgrowthquarterly` | float | Quarterly sales growth |

### Profitability

| Field | Type | Description |
|---|---|---|
| `returnonequity.quarterly` | float | ROE (quarterly) |
| `returnonassets.quarterly` | float | ROA (quarterly) |
| `operatingmargincontinuingoperations.quarterly` | float | Operating margin |
| `netprofitmargin.quarterly` | float | Net profit margin |
| `grossmargin.quarterly` | float | Gross margin |

### Sector & Industry

| Field | Type | Values |
|---|---|---|
| `sector` | string | `"Technology"`, `"Healthcare"`, `"Financial"`, `"Consumer Cyclical"`, `"Energy"`, `"Industrials"`, `"Consumer Defensive"`, `"Communication Services"`, `"Real Estate"`, `"Utilities"`, `"Basic Materials"` |
| `industry` | string | Industry name string |

### Dividends & Short Interest

| Field | Type | Description |
|---|---|---|
| `forwardfulldividendyield` | float | Forward dividend yield % |
| `trailingfulldividendyield` | float | Trailing dividend yield % |
| `shortpercentageofsharesoutstanding.value` | float | Short interest % of float |
| `shortinterest` | int | Short interest shares |

## FundQuery Fields

| Field | Type | Values/Description |
|---|---|---|
| `categoryname` | string | Fund category name |
| `performanceratingoverall` | int | 1–5 overall rating |
| `riskratingoverall` | int | 1–5 risk rating |
| `initialinvestment` | float | Minimum initial investment |
| `annualreturnnavy1categoryrank` | int | 1-year return category rank |
| `fundnetassets` | float | Net assets |
| `exchange` | string | `"NAS"` (NASDAQ), `"NYQ"` (NYSE), etc. |
| `intradayprice` | float | Current price |
| `percentchange` | float | Percent change |

### Common Category Names

`"Large Blend"`, `"Large Growth"`, `"Mid-Cap Growth"`, `"Foreign Large Value"`, `"Foreign Large Blend"`, `"Foreign Large Growth"`, `"Foreign Small/Mid Growth"`, `"Foreign Small/Mid Blend"`, `"Foreign Small/Mid Value"`, `"High Yield Bond"`.

## ETFQuery Fields

| Field | Type | Values/Description |
|---|---|---|
| `region` | string | `"us"`, `"uk"`, etc. |
| `categoryname` | string | ETF category |
| `performanceratingoverall` | int | 1–5 overall rating |
| `intradayprice` | float | Current price |
| `annualreportnetexpenseratio` | float | Expense ratio |
| `etfflows1month` | float | 1-month flows |
| `etfflowspct1month` | float | 1-month flows % |

## Examples

### Growth Technology Stocks

```python
q = EquityQuery("and", [
    EquityQuery("gte", ["quarterlyrevenuegrowth.quarterly", 25]),
    EquityQuery("gte", ["epsgrowth.lasttwelvemonths", 25]),
    EquityQuery("eq", ["sector", "Technology"]),
    EquityQuery("is-in", ["exchange", "NMS", "NYQ"]),
])
results = screen(q)
```

### Undervalued Large Caps

```python
q = EquityQuery("and", [
    EquityQuery("btwn", ["peratio.lasttwelvemonths", 0, 20]),
    EquityQuery("lt", ["pegratio_5y", 1]),
    EquityQuery("btwn", ["intradaymarketcap", 10000000000, 100000000000]),
    EquityQuery("is-in", ["exchange", "NMS", "NYQ"]),
])
results = screen(q)
```

### High-Volume Day Gainers

```python
q = EquityQuery("and", [
    EquityQuery("gt", ["percentchange", 3]),
    EquityQuery("eq", ["region", "us"]),
    EquityQuery("gte", ["intradaymarketcap", 2000000000]),
    EquityQuery("gte", ["intradayprice", 5]),
    EquityQuery("gt", ["dayvolume", 15000]),
])
results = screen(q)
```

### Top Mutual Funds

```python
q = FundQuery("and", [
    FundQuery("gt", ["intradayprice", 15]),
    FundQuery("is-in", ["performanceratingoverall", 4, 5]),
    FundQuery("gt", ["initialinvestment", 1000]),
    FundQuery("eq", ["exchange", "NAS"]),
])
results = screen(q)
```

### Bond ETFs

```python
q = ETFQuery("and", [
    ETFQuery("eq", ["region", "us"]),
    ETFQuery("is-in", ["categoryname",
        "Corporate Bond", "High Yield Bond",
        "Intermediate-Term Bond", "Short-Term Bond",
        "Ultrashort Bond", "World Bond"]),
])
results = screen(q)
```

## Predefined Screeners

Access via `yf.PREDEFINED_SCREENER_QUERIES` dict or pass the name string to `screen()`.

### Equity Screeners

| Name | Description |
|---|---|
| `day_gainers` | Stocks up >3%, market cap >$2B, price >$5, volume >15K |
| `day_losers` | Stocks down >2.5%, market cap >$2B, price >$5, volume >20K |
| `most_actives` | US stocks, market cap >$2B, volume >5M |
| `most_shorted_stocks` | US stocks, price >$1, avg volume >200K |
| `aggressive_small_caps` | NAS/NYQ, EPS growth <15% |
| `growth_technology_stocks` | Revenue growth >25%, EPS growth >25%, Technology sector |
| `small_cap_gainers` | Market cap <$2B, NAS/NYQ |
| `undervalued_growth_stocks` | P/E 0–20, PEG <1, EPS growth >25% |
| `undervalued_large_caps` | P/E 0–20, PEG <1, market cap $10B–$100B |

### Fund Screeners

| Name | Description |
|---|---|
| `top_mutual_funds` | Price >$15, rating 4–5, min investment >$1K |
| `conservative_foreign_funds` | Foreign categories, rating 4–5, risk 1–3 |
| `high_yield_bond` | High yield bond funds, rating 4–5 |
| `portfolio_anchors` | Large blend funds, rating 4–5 |
| `solid_large_growth_funds` | Large growth funds, rating 4–5 |
| `solid_midcap_growth_funds` | Mid-cap growth funds, rating 4–5 |

### ETF Screeners

| Name | Description |
|---|---|
| `top_etfs_us` | US ETFs, price >$10, rating 4–5 |
| `top_performing_etfs` | US ETFs, rating 4–5, price >$10 |
| `technology_etfs` | US Technology category ETFs |
| `bond_etfs` | US bond category ETFs |
