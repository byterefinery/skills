---
name: meteostat-2-1-4
description: >
  Meteostat 2.1.4 — Python library for accessing open weather and climate data
  from global weather stations via Pandas DataFrames. Provides hourly, daily,
  monthly, and normals (climatological averages) time series; spatial
  interpolation to arbitrary points; station metadata lookup; and data merging.
  Backed by NOAA, DWD, ECCC, GSA, Met.no and Meteostat's own derived datasets.
  Use when the user needs historical weather data, climate normals, weather
  station lookups, spatial interpolation of meteorological data, or any
  weather/climate analysis in Python. Triggers on: weather data, climate data,
  weather stations, temperature/precipitation/wind data, meteostat,
  interpolation, normals, climate analysis.
metadata:
  tags:
    - python
    - weather
    - climate
    - data-analysis
    - time-series
---

# meteostat 2.1.4

## Overview

Meteostat is a Python library for accessing open weather and climate data from thousands of weather stations worldwide. Data is returned as Pandas DataFrames, making it a natural fit for analytics, visualization, and ML pipelines.

Install: `pip install meteostat==2.1.4`

Dependencies: `requests`, `pandas>=2.3.0,<4.0.0`, `pytz`. Optional: `matplotlib`, `metar`, `lxml`.
Python: 3.11+.

### Core Objects

- **`TimeSeries`** — container for fetched data; call `.fetch()` to get a DataFrame
- **`Point(lat, lon, elevation?)`** — geographical point for nearby-station lookups and interpolation
- **`Station(id, ...)`** — weather station metadata (id, name, country, lat, lon, elevation, timezone, identifiers)
- **`Inventory`** — data availability for a station (start/end dates, available parameters)
- **`stations`** — singleton for station database queries (`meta()`, `nearby()`, `inventory()`)
- **`config`** — global configuration (cache dir, network settings, provider endpoints)

### Key Enums

- **`Parameter`** — meteorological parameters: `TEMP`, `TMIN`, `TMAX`, `DWPT`, `PRCP`, `RHUM`, `PRES`, `SNWD`, `SNOW`, `WSPD`, `WPGT`, `WDIR`, `TSUN`, `CLDC`, `VSBY`, `COCO`, `TXMN`, `TXMX`, `PDAY`
- **`Provider`** — data sources: `DAILY`, `HOURLY`, `MONTHLY`, `DAILY_DERIVED`, `MONTHLY_DERIVED`, `ISD_LITE`, `GHCND`, `METAR`, `CLIMAT`, `DWD_*`, `ECCC_*`, `GSA_*`, `METNO_FORECAST`
- **`Granularity`** — `HOURLY`, `DAILY`, `MONTHLY`, `NORMALS`
- **`UnitSystem`** — `METRIC` (default), `SI`, `IMPERIAL`

## Usage

### Fetching daily data for a station

```python
from datetime import date
import meteostat as ms

ts = ms.daily("10637", date(2018, 1, 1), date(2018, 12, 31))
df = ts.fetch()  # DataFrame with date index, columns: temp, tmin, tmax, rhum, prcp, ...
```

### Fetching hourly data

```python
from datetime import datetime
import meteostat as ms

start = datetime(2018, 1, 1)
end = datetime(2018, 12, 31, 23, 59)

ts = ms.hourly("72219", start, end)
df = ts.fetch()
```

### Fetching monthly data

```python
ts = ms.monthly("10637", date(2000, 1, 1), date(2018, 12, 31))
df = ts.fetch()
```

### Climate normals (30-year averages)

```python
ts = ms.normals("10637", 1961, 1990)
df = ts.fetch()  # Index is month (1-12), columns are monthly averages
```

### Finding nearby stations and interpolating

```python
POINT = ms.Point(50.1155, 8.6842, 113)  # Frankfurt

stations = ms.stations.nearby(POINT, limit=4)
ts = ms.daily(stations, date(2018, 1, 1), date(2018, 12, 31))
df = ms.interpolate(ts, POINT).fetch()
```

### Custom parameters and providers

```python
# Specific parameters only
ts = ms.daily("10637", start, end, parameters=[ms.Parameter.TEMP, ms.Parameter.PRCP])

# Specific provider
ts = ms.hourly("10637", start, end, providers=[ms.Provider.DWD_HOURLY], parameters=[ms.Parameter.TEMP])
```

### Station metadata and inventory

```python
# Station metadata
station = ms.stations.meta("72503")  # Station object with id, name, lat, lon, elevation, identifiers

# Data inventory (availability)
inv = ms.stations.inventory("71624")
print(f"Data from {inv.start} to {inv.end}")
print(f"Parameters: {inv.parameters}")
```

### Merging time series

```python
ts1 = ms.daily("72503", date(2020, 1, 1), date(2020, 1, 10))
ts2 = ms.daily("72503", date(2020, 1, 11), date(2020, 1, 20))
ts = ms.merge([ts1, ts2])  # Same granularity required
df = ts.fetch()
```

### Lapse rate calculation

```python
stations = ms.stations.nearby(ms.Point(50.3167, 8.5, 320), limit=10)
ts = ms.hourly(stations, start, end, parameters=[ms.Parameter.TEMP])
lr = ms.lapse_rate(ts)  # °C per 1000m
```

### TimeSeries.fetch() options

```python
df = ts.fetch(
    squash=True,       # squash multi-source rows (default True)
    fill=False,        # fill missing timestamps (default False)
    sources=False,     # include source columns (default False)
    location=False,    # include lat/lon/elevation (default False)
    clean=True,        # apply schema validators (default True)
    humanize=False,    # convert wind direction/condition codes to strings
    units=ms.UnitSystem.METRIC,  # METRIC, SI, or IMPERIAL
)
```

### TimeSeries helper methods

```python
ts.completeness()                     # overall completeness ratio (0-1)
ts.completeness(ms.Parameter.TEMP)    # completeness for specific parameter
ts.count()                            # count of non-NaN values
ts.count(ms.Parameter.TEMP)           # count for specific parameter
ts.validate()                         # run all parameter validators
ts.parameters                         # list of Parameter enums
ts.providers                          # list of provider IDs used
ts.licenses                           # list of License objects
ts.attribution                        # attribution string
ts.commercial                         # bool: is commercial use allowed?
```

## Gotchas

- **`Station(id='...')` vs string** — use `ms.Station(id='10637')` instead of just `'10637'` when you want to avoid unnecessary metadata lookups. Both work, but `Station()` is faster for default providers.
- **Points only work with geo-location providers** — passing a `Point` to `daily()`/`hourly()`/`monthly()` only works with providers that accept lat/lon (e.g., `METNO_FORECAST`). For default providers, use `stations.nearby()` + `interpolate()` instead.
- **`normals()` returns month-indexed data** — the index is month number (1-12), not dates. The `freq` property is `None` for normals.
- **`merge()` requires matching granularity** — all merged TimeSeries must have the same granularity and timezone. Passing hourly + daily raises `ValueError`.
- **Cache is enabled by default** — data is cached in `~/.meteostat/cache/` with a 30-day TTL. Use `ms.config.cache_enable = False` or `ms.purge()` to disable/clear.
- **Stations database** — the SQLite station database is downloaded to `~/.meteostat/stations.db` and cached for a week. First call to `stations.meta()`/`nearby()`/`inventory()` triggers the download.
- **`start`/`end` can be `None`** — omitting start or end returns all available data. Use `date` for daily/monthly, `datetime` for hourly.
- **Hourly data needs `datetime`, not `date`** — for hourly queries, use `datetime(2018, 1, 1, 0, 0)` to `datetime(2018, 12, 31, 23, 59)`. Using `date` works but may give unexpected bounds.
- **Interpolation uses nearest-neighbor first** — if a station is within `distance_threshold` (default 5000m) and `elevation_threshold` (default 50m), nearest-neighbor is used. Otherwise IDW with power 2.0. Categorical parameters (WDIR, CLDC, COCO) always use nearest-neighbor.
- **Lapse rate applied to TEMP/TMIN/TMAX only** — the default `lapse_rate_parameters` config only includes temperature parameters. Set `ms.config.lapse_rate_parameters` to extend.
- **`ts.fetch()` returns `None` if no data** — always check `df is not None and not df.empty` before processing.
- **Multi-station queries return a MultiIndex** — the DataFrame index has `station` and `time` levels. Use `squash=True` (default) to merge sources.
- **Data is CC BY 4.0** — attribution is required. Use `ts.attribution` for the correct string.

## References

- [01-parameters](references/01-parameters.md) — Full parameter reference with units, granularities, and default sets
- [02-providers](references/02-providers.md) — Provider details, data sources, and selection strategies
- [03-configuration](references/03-configuration.md) — Cache, network, and provider-specific configuration options
- [04-api-reference](references/04-api-reference.md) — Detailed API signatures for all public functions and classes
