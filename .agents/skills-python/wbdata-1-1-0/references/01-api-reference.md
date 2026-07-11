# API Reference

## Data Retrieval

### `get_data(indicator, country="all", date=None, freq="Y", source=None, parse_dates=False, skip_cache=False)`

Retrieve indicator observations as a list of dicts.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `indicator` | `str` | — | Indicator code (e.g., `"NY.GDP.PCAP.CD"`) |
| `country` | `str \| Sequence[str]` | `"all"` | Country code(s) or `"all"` |
| `date` | `str \| datetime \| tuple \| None` | `None` | Single date or `(start, end)` tuple. Strings can be `"2020"`, `"2020M06"`, `"2020Q1"`, or any format `dateparser` handles |
| `freq` | `str` | `"Y"` | Periodicity: `"Y"` (yearly), `"M"` (monthly), `"Q"` (quarterly) |
| `source` | `int \| str \| Sequence \| None` | `None` | Source ID; defaults to 2 (World Development Indicators) |
| `parse_dates` | `bool` | `False` | Convert date strings to `datetime.datetime` objects |
| `skip_cache` | `bool` | `False` | Bypass the cache |

Returns a `Result` (list of dicts) with a `last_updated` attribute.

### `get_series(indicator, country="all", ..., name="value", keep_levels=False, skip_cache=False)`

Retrieve data as a `pandas.Series` with MultiIndex (country, date). Requires pandas.

Extra parameters beyond `get_data`:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | `"value"` | Name of the resulting Series |
| `keep_levels` | `bool` | `False` | If `False`, drop index levels with only one unique value |

### `get_dataframe(indicators, country="all", ..., keep_levels=False, skip_cache=False)`

Retrieve multiple indicators merged into a `pandas.DataFrame`. Requires pandas.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `indicators` | `dict[str, str]` | — | Mapping of indicator code → column name, e.g. `{"NY.GDP.PCAP.CD": "gdp", "SP.POP.TOTL": "population"}` |

## Metadata Retrieval

All return `SearchResult` (a list of dicts that pretty-prints as a table in interactive sessions).

### `get_countries(country_id=None, query=None, incomelevel=None, lendingtype=None, skip_cache=False)`

Retrieve country or regional aggregates.

- `country_id`: specific country code(s)
- `query`: regex to filter by country name (case-insensitive)
- `incomelevel` / `lendingtype`: filter by aggregate category
- Cannot combine `country_id` with `query`/`incomelevel`/`lendingtype`

### `get_indicators(indicator=None, query=None, source=None, topic=None, skip_cache=False)`

Retrieve indicator metadata.

- `indicator`: specific indicator code(s)
- `query`: regex to filter by indicator name (case-insensitive)
- `source` / `topic`: list all indicators for a given source or topic
- Cannot specify more than one of `indicator`, `source`, `topic`
- Cannot combine `query` with `indicator`

### `get_sources(source_id=None, skip_cache=False)`

List data sources. Returns all if `source_id` is `None`.

### `get_topics(topic_id=None, skip_cache=False)`

List topics. Returns all if `topic_id` is `None`.

### `get_incomelevels(level_id=None, skip_cache=False)`

List income level aggregates (HIC, LIC, MIC, etc.).

### `get_lendingtypes(type_id=None, skip_cache=False)`

List lending type aggregates.

## Client

### `Client(cache_path=None, cache_ttl_days=None, cache_max_size=None, session=None)`

Create a custom client with explicit cache configuration or a custom `requests.Session`.

All methods above are available on the `Client` instance. The module-level functions use a singleton default client.

## Cache Configuration

Control default caching via environment variables:

| Variable | Default | Description |
|---|---|---|
| `WBDATA_CACHE_PATH` | System cache dir | Path to the cache file |
| `WBDATA_CACHE_TTL_DAYS` | `7` | Days to retain cached results |
| `WBDATA_CACHE_MAX_SIZE` | `100` | Maximum number of cached items |

## Return Types

- `Result` — list of dicts with `last_updated` attribute (used by `get_data`)
- `SearchResult` — list of dicts that pretty-prints as a table (metadata functions)
- `Series` — `pandas.Series` subclass with `last_updated` attribute
- `DataFrame` — `pandas.DataFrame` subclass with per-column `last_updated` dict
