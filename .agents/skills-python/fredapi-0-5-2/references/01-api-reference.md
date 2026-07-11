# fredapi 0.5.2 — API Reference

## Fred Class

### Constructor

```python
Fred(api_key=None, api_key_file=None, proxies=None)
```

| Parameter | Type | Description |
|---|---|---|
| `api_key` | `str` | FRED API key string. Obtained free from [api.stlouisfed.org](http://api.stlouisfed.org/api_key.html) |
| `api_key_file` | `str` | Path to file containing the API key (first line) |
| `proxies` | `dict` | Protocol-to-URL mapping, e.g. `{'http': 'http://proxy:8080', 'https': 'http://proxy:8080'}`. Falls back to `HTTP_PROXY`/`HTTPS_PROXY` env vars |

Raises `ValueError` if no API key is available through any method.

### Class Attributes

| Attribute | Value | Description |
|---|---|---|
| `root_url` | `'https://api.stlouisfed.org/fred'` | Base URL for all API calls |
| `earliest_realtime_start` | `'1776-07-04'` | Default earliest ALFRED realtime_start |
| `latest_realtime_end` | `'9999-12-31'` | Default latest ALFRED realtime_end |
| `max_results_per_request` | `1000` | Max results per FRED API request (pagination boundary) |
| `nan_char` | `'.'` | FRED's missing-value marker in XML responses |

---

## Data Retrieval Methods

### `get_series(series_id, observation_start=None, observation_end=None, **kwargs)`

Fetch latest data for a series. Equivalent to `get_series_latest_release()`.

| Parameter | Type | Description |
|---|---|---|
| `series_id` | `str` | FRED series ID, e.g. `'GDP'`, `'CPIAUCSL'`, `'SP500'` |
| `observation_start` | `str` or `datetime` | Earliest observation date (pandas-parseable) |
| `observation_end` | `str` or `datetime` | Latest observation date (pandas-parseable) |
| `**kwargs` | — | Extra FRED API parameters (e.g. `transform='pcap'`, `sort_order='desc'`) |

**Returns:** `pd.Series` — index is observation date (`datetime`), values are `float` (NaN for missing).

**Raises:** `ValueError` on invalid series ID or unparseable dates.

```python
# Basic usage
data = fred.get_series('GDP')

# Date range
data = fred.get_series('CPIAUCSL', observation_start='2000-01-01')

# With transform (percent change from a year ago)
data = fred.get_series('GDP', transform='pcap')
```

### `get_series_latest_release(series_id)`

Identical to `get_series(series_id)` — fetches the most current data. Exists for API clarity when contrasted with `get_series_first_release()`.

| Parameter | Type | Description |
|---|---|---|
| `series_id` | `str` | FRED series ID |

**Returns:** `pd.Series` — same format as `get_series()`.

### `get_series_info(series_id)`

Get metadata about a series.

| Parameter | Type | Description |
|---|---|---|
| `series_id` | `str` | FRED series ID |

**Returns:** `pd.Series` — attributes include:

| Attribute | Description |
|---|---|
| `id` | Series ID |
| `title` | Full series title |
| `units` | Data units (e.g. `"Billions of Dollars"`) |
| `units_short` | Abbreviated units |
| `frequency` | Frequency (`"Monthly"`, `"Quarterly"`, `"Annual"`, `"Daily"`) |
| `frequency_short` | Abbreviated frequency (`"M"`, `"Q"`, `"A"`, `"D"`) |
| `seasonal_adjustment` | Seasonal adjustment status |
| `seasonal_adjustment_short` | Abbreviated (`"SA"`, `"NSA"`, `"SAARD"`) |
| `observation_start` | First observation date |
| `observation_end` | Last observation date |
| `realtime_start` | ALFRED realtime_start |
| `realtime_end` | ALFRED realtime_end |
| `last_updated` | Last update timestamp |
| `popularity` | Popularity score (integer) |
| `notes` | Series notes |

```python
info = fred.get_series_info('PAYEMS')
print(info['title'])        # "All Employees: Total Nonfarm Payrolls"
print(info['frequency'])    # "Monthly"
print(info['units'])        # "Thousands of Persons"
```

---

## ALFRED / Revision Methods

### `get_series_first_release(series_id)`

Get only the first-release values, ignoring all subsequent revisions.

| Parameter | Type | Description |
|---|---|---|
| `series_id` | `str` | FRED series ID |

**Returns:** `pd.Series` — index is observation date, values are `float`. Internally calls `get_series_all_releases()` and takes `head(1)` per date group.

### `get_series_all_releases(series_id, realtime_start=None, realtime_end=None)`

Get all observations including every revision.

| Parameter | Type | Description |
|---|---|---|
| `series_id` | `str` | FRED series ID |
| `realtime_start` | `str` | Earliest realtime_start date (default: `'1776-07-04'`) |
| `realtime_end` | `str` | Latest realtime_end date (default: `'9999-12-31'`) |

**Returns:** `pd.DataFrame` with columns:

| Column | Type | Description |
|---|---|---|
| `date` | `datetime` | The observation period the value refers to |
| `realtime_start` | `datetime` | When this value (first release or revision) was reported |
| `value` | `float` | The data value (NaN for missing) |

The DataFrame index is an integer row number (0, 1, 2, …), not dates.

### `get_series_as_of_date(series_id, as_of_date)`

Get the latest known data as of a specific date. Includes all revisions on or before `as_of_date`.

| Parameter | Type | Description |
|---|---|---|
| `series_id` | `str` | FRED series ID |
| `as_of_date` | `str` or `datetime` | Include revisions on or before this date |

**Returns:** `pd.DataFrame` — subset of `get_series_all_releases()` filtered to `realtime_start <= as_of_date`. Has columns `date`, `realtime_start`, `value`.

### `get_series_vintage_dates(series_id)`

Get the list of dates when the series had new data released or existing data revised.

| Parameter | Type | Description |
|---|---|---|
| `series_id` | `str` | FRED series ID |

**Returns:** `list` of `datetime` objects — the vintage dates in chronological order.

---

## Search Methods

### `search(text, limit=1000, order_by=None, sort_order=None, filter=None)`

Full-text search for series.

| Parameter | Type | Description |
|---|---|---|
| `text` | `str` | Search query, e.g. `'real gdp'`, `'unemployment rate'` |
| `limit` | `int` | Max results. `0` means no limit (fetch all). Default: 1000 |
| `order_by` | `str` | Sort criterion. Valid: `'search_rank'`, `'series_id'`, `'title'`, `'units'`, `'frequency'`, `'seasonal_adjustment'`, `'realtime_start'`, `'realtime_end'`, `'last_updated'`, `'observation_start'`, `'observation_end'`, `'popularity'` |
| `sort_order` | `str` | `'asc'` or `'desc'` |
| `filter` | `tuple` | `(filter_variable, filter_value)`. Valid variables: `'frequency'`, `'units'`, `'seasonal_adjustment'` |

**Returns:** `pd.DataFrame` or `None`. DataFrame index is `'series id'`, columns include: `id`, `title`, `units`, `units_short`, `frequency`, `frequency_short`, `seasonal_adjustment`, `seasonal_adjustment_short`, `observation_start`, `observation_end`, `realtime_start`, `realtime_end`, `last_updated`, `popularity`, `notes`.

```python
# Basic search
results = fred.search('inflation')

# Top 10 by popularity
results = fred.search('gdp', limit=10, order_by='popularity', sort_order='desc')

# Filter to monthly series
results = fred.search('interest rates', filter=('frequency', 'Monthly'))
```

### `search_by_release(release_id, limit=0, order_by=None, sort_order=None, filter=None)`

Get series belonging to a FRED release (e.g., a specific report).

| Parameter | Type | Description |
|---|---|---|
| `release_id` | `int` | FRED release ID, e.g. `151` (G.18 Financial Services) |
| `limit` | `int` | Max results (`0` = all) |
| `order_by` | `str` | Same options as `search()` |
| `sort_order` | `str` | `'asc'` or `'desc'` |
| `filter` | `tuple` | Same as `search()` |

**Returns:** `pd.DataFrame` — same format as `search()`.

**Raises:** `ValueError` if no series exist for the release ID.

### `search_by_category(category_id, limit=0, order_by=None, sort_order=None, filter=None)`

Get series belonging to a FRED category.

| Parameter | Type | Description |
|---|---|---|
| `category_id` | `int` | FRED category ID, e.g. `32145` |
| `limit` | `int` | Max results (`0` = all) |
| `order_by` | `str` | Same options as `search()` |
| `sort_order` | `str` | `'asc'` or `'desc'` |
| `filter` | `tuple` | Same as `search()` |

**Returns:** `pd.DataFrame` — same format as `search()`.

**Raises:** `ValueError` if no series exist for the category ID.
