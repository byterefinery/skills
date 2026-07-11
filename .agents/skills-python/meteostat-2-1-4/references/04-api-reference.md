# API Reference

Detailed API signatures for Meteostat 2.1.4 public functions and classes.

## Time Series Functions

### `daily(station, start, end, parameters=None, providers=None)`

Fetch daily time series data.

- `station` — str, Station, Point, list thereof, or DataFrame (from `stations.nearby()`)
- `start` — date or datetime (or None for earliest available)
- `end` — date or datetime (or None for latest available)
- `parameters` — list of `Parameter` (defaults: TEMP, TMIN, TMAX, RHUM, PRCP, SNWD, WSPD, WPGT, PRES, TSUN, CLDC)
- `providers` — list of `Provider` (defaults: `[Provider.DAILY]`)

Returns: `TimeSeries`

### `hourly(station, start, end, timezone=None, parameters=None, providers=None)`

Fetch hourly time series data.

- `timezone` — IANA timezone string (e.g., `"Europe/Berlin"`). If None, UTC is used.

Returns: `TimeSeries`

### `monthly(station, start, end, parameters=None, providers=None)`

Fetch monthly time series data.

Returns: `TimeSeries`

### `normals(station, start=1961, end=1990, parameters=None, providers=None, max_missing=3)`

Compute climate normals (monthly averages over a year range).

- `start` — int (start year, default 1961)
- `end` — int (end year, default 1990)
- `max_missing` — max missing months allowed to compute a mean (default 3)

Returns: `TimeSeries` with month-indexed DataFrame (1-12).

## Interpolation

### `interpolate(ts, point, distance_threshold=5000, elevation_threshold=50, elevation_weight=10, power=2.0, lapse_rate=6.5, lapse_rate_threshold=50)`

Spatially interpolate time series data to a specific point.

- `ts` — TimeSeries (must contain data from multiple stations)
- `point` — Point (latitude, longitude, optional elevation)
- `distance_threshold` — max horizontal distance in meters for nearest-neighbor (default 5000)
- `elevation_threshold` — max elevation difference in meters for nearest-neighbor (default 50)
- `elevation_weight` — weight for elevation in effective distance calculation (default 10)
- `power` — IDW power parameter (default 2.0; higher = more weight to closer stations)
- `lapse_rate` — temperature correction in °C per 1000m (default 6.5)
- `lapse_rate_threshold` — min elevation difference to apply lapse rate (default 50m)

Returns: `TimeSeries` interpolated to the given point.

### `lapse_rate(ts, parameter=Parameter.TEMP)`

Calculate lapse rate from multiple station temperature data.

- `ts` — TimeSeries with data from 2+ stations
- `parameter` — Parameter to use (default TEMP)

Returns: float (°C per 1000m) or None if insufficient data.

## Merging

### `merge(objs)`

Merge multiple TimeSeries into one.

- `objs` — list of TimeSeries (must share same granularity and timezone)

Returns: `TimeSeries`

Raises `ValueError` if list is empty or granularities/timezones differ.

## Station Database

### `stations.meta(station)`

Get metadata for a station.

- `station` — station ID string

Returns: `Station` object or None.

### `stations.nearby(point, radius=50000, limit=100)`

Find stations near a point.

- `point` — Point (latitude, longitude, optional elevation)
- `radius` — search radius in meters (default 50000)
- `limit` — max results (default 100)

Returns: DataFrame with columns: name, country, region, latitude, longitude, elevation, timezone, distance.

### `stations.inventory(station, providers=None)`

Get data availability for a station.

- `station` — station ID string or list of IDs
- `providers` — optional list of Provider to filter

Returns: `Inventory` object.

## TimeSeries Class

### `TimeSeries.fetch(squash=True, fill=False, sources=False, location=False, clean=True, humanize=False, units=UnitSystem.METRIC)`

Fetch data as DataFrame.

- `squash` — merge multi-source rows (default True)
- `fill` — fill missing timestamps (default False)
- `sources` — include source columns (default False)
- `location` — include lat/lon/elevation columns (default False)
- `clean` — apply schema validators (default True)
- `humanize` — convert codes to readable strings (default False)
- `units` — UnitSystem.METRIC, SI, or IMPERIAL

Returns: DataFrame or None.

### `TimeSeries.count(parameter=None)`

Count non-NaN values. Returns int.

### `TimeSeries.completeness(parameter=None)`

Get completeness ratio (0-1). Returns float or None.

### `TimeSeries.validate()`

Run all parameter validators. Returns bool.

## Point Class

### `Point(latitude, longitude, elevation=None)`

Create a geographical point.

- `latitude` — -90 to 90
- `longitude` — -180 to 180
- `elevation` — optional, in meters

## Station Class

### `Station(id, name=None, country=None, region=None, identifiers=None, latitude=None, longitude=None, elevation=None, timezone=None)`

Create a station object. For performance with default providers, `Station(id='10637')` is sufficient.

## Inventory Class

### Properties

- `inventory.start` — earliest available date
- `inventory.end` — latest available date
- `inventory.parameters` — list of available Parameter enums
- `inventory.df` — raw DataFrame

## Config

### `config` — global configuration singleton

Access via `ms.config.<setting>`. See [Configuration](03-configuration.md) for full list.

### `purge()`

Clear all cached data.

## Enums

### `Parameter`

TEMP, TMIN, TMAX, TXMN, TXMX, DWPT, PRCP, PDAY, WDIR, WSPD, WPGT, RHUM, PRES, SNWD, SNOW, TSUN, SGHI, SDNI, SDHI, CLDC, VSBY, COCO

### `Provider`

ISD_LITE, METAR, GHCND, CLIMAT, DWD_HOURLY, DWD_POI, DWD_MOSMIX, DWD_DAILY, DWD_MONTHLY, ECCC_HOURLY, ECCC_DAILY, ECCC_MONTHLY, METNO_FORECAST, GSA_HOURLY, GSA_SYNOP, GSA_DAILY, GSA_MONTHLY, HOURLY, DAILY, DAILY_DERIVED, MONTHLY, MONTHLY_DERIVED

### `Granularity`

HOURLY, DAILY, MONTHLY, NORMALS

### `UnitSystem`

SI, METRIC, IMPERIAL
