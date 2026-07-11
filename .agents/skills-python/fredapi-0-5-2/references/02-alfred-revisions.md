# fredapi 0.5.2 — ALFRED Revisions & Point-in-Time Data

## ALFRED Overview

[ALFRED](http://research.stlouisfed.org/tips/alfred/) (Another FRED) is the point-in-time database behind FRED's revision tracking. Every observation in ALFRED has three dates:

| Date Field | Meaning |
|---|---|
| `date` | The observation period the value refers to (e.g., Q1 2014) |
| `realtime_start` | The first date this specific value was valid (when it was published) |
| `realtime_end` | The last date this value was valid (until it was superseded by a revision) |

## Example: GDP Revisions

US GDP for Q1 2014 went through three releases:

| `date` | `realtime_start` | `value` | Meaning |
|---|---|---|---|
| 2014-01-01 | 2014-04-30 | 17149.6 | Initial release (Advance estimate) |
| 2014-01-01 | 2014-05-29 | 17101.3 | Second estimate (revision) |
| 2014-01-01 | 2014-06-25 | 17016.0 | Third estimate (revision) |

Each row represents one "vintage" of the data — the value that was publicly available during the time window `[realtime_start, realtime_end)`.

## Method Comparison

| Method | Returns | Use Case |
|---|---|---|
| `get_series()` | `Series` | Latest/current data values |
| `get_series_latest_release()` | `Series` | Same as `get_series()` |
| `get_series_first_release()` | `Series` | Original values before any revisions |
| `get_series_all_releases()` | `DataFrame` | Complete revision history |
| `get_series_as_of_date()` | `DataFrame` | What data was known on a specific date |
| `get_series_vintage_dates()` | `list` | Dates when revisions occurred |

## Common Patterns

### Backtesting with Point-in-Time Data

To avoid look-ahead bias in backtests, use `get_series_as_of_date()` to get only the data that was actually known at each decision point:

```python
# What GDP data was available on June 1, 2014?
data_as_of = fred.get_series_as_of_date('GDP', '2014-06-01')

# To get the latest value per observation date as of that date:
latest_as_of = data_as_of.sort_values('realtime_start').groupby('date').last()
```

### Measuring Revision Magnitude

```python
all_releases = fred.get_series_all_releases('GDP')

# Group by observation date, compare first vs latest
def revision_stats(group):
    return pd.Series({
        'first_value': group.iloc[0]['value'],
        'latest_value': group.iloc[-1]['value'],
        'revision': group.iloc[-1]['value'] - group.iloc[0]['value'],
        'num_revisions': len(group) - 1,
    })

stats = all_releases.groupby('date').apply(revision_stats)
```

### First Release vs Latest Comparison

```python
first = fred.get_series_first_release('GDP')
latest = fred.get_series('GDP')

# Compare
comparison = pd.DataFrame({'first_release': first, 'latest': latest})
comparison['revision'] = comparison['latest'] - comparison['first_release']
comparison['revision_pct'] = comparison['revision'] / comparison['first_release'] * 100
```

### Vintage Date Analysis

```python
# Get all dates when GDP was revised or new data released
vintage_dates = fred.get_series_vintage_dates('GDP')

# Filter to a specific year
from datetime import date
vintage_2014 = [d for d in vintage_dates if d.year == 2014]
```

## Realtime Start/End Parameters

`get_series_all_releases()` accepts optional `realtime_start` and `realtime_end` to narrow the ALFRED time window:

```python
# Only get revisions that occurred in 2014
releases = fred.get_series_all_releases('GDP',
                                         realtime_start='2014-01-01',
                                         realtime_end='2014-12-31')
```

Defaults are `'1776-07-04'` (earliest) and `'9999-12-31'` (latest), which fetches all available revisions.

## Gotchas

- **`get_series_first_release()` calls `get_series_all_releases()` internally** — it makes one ALFRED API call and deduplicates by taking the first row per observation date. It does not make two separate calls.
- **`get_series_as_of_date()` returns a DataFrame, not a Series** — unlike `get_series()` which returns a Series, this returns a DataFrame because multiple revisions per observation date are possible. To get one value per date, use `groupby('date').last()` after filtering.
- **ALFRED calls are more expensive** — revision-aware methods hit the ALFRED endpoint which returns significantly more data. Be mindful of FRED API rate limits (12,000 requests per hour for free keys).
- **`get_series_all_releases()` index is integer-based** — the returned DataFrame uses a simple integer index (0, 1, 2, …), not dates. Use `set_index('date')` or `groupby('date')` for date-based operations.
- **Not all series have revision data** — some series (especially real-time or calculated series) may have no revisions. `get_series_first_release()` will still work but may return the same data as `get_series()`.
