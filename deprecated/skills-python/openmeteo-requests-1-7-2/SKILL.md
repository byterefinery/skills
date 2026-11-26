---
name: openmeteo-requests-1-7-2
description: >
  Python client (openmeteo-requests) version 1.7.2 for the Open-Meteo Weather
  API — fetches weather forecast, historical, and air-quality data using
  FlatBuffers for zero-copy data transfer into NumPy, Pandas, or Polars.
  Provides sync Client and async AsyncClient built on niquests. Use this skill
  whenever the user needs weather data from Open-Meteo in Python, works with
  weather time-series, processes FlatBuffers weather responses, or integrates
  Open-Meteo API with caching (requests-cache) and retries (retry-requests).
metadata:
  tags:
    - python
    - weather
    - api-client
    - flatbuffers
---

# openmeteo-requests 1.7.2

## Overview

`openmeteo-requests` 1.7.2 is the official Python client for the [Open-Meteo Weather API](https://open-meteo.com). It uses FlatBuffers instead of JSON for data transfer, enabling zero-copy access to weather data directly in NumPy, Pandas, or Polars. The library provides both synchronous (`Client`) and asynchronous (`AsyncClient`) interfaces built on `niquests` (a `requests`-compatible HTTP library).

Key objects:

- **`Client`** — synchronous client; creates its own `niquests.Session` or accepts a custom one
- **`AsyncClient`** — asynchronous client; uses `niquests.AsyncSession` or per-request async calls
- **`OpenMeteoRequestsError`** — raised on API errors (400, 429) or request failures
- **`WeatherApiResponse`** — FlatBuffers-decoded response with `.Latitude()`, `.Longitude()`, `.Current()`, `.Hourly()`, `.Daily()`, etc.

Dependencies: `niquests>=3.15.2`, `openmeteo-sdk>=1.20.1`.

Install: `pip install openmeteo-requests==1.7.2`

## Usage

### Basic synchronous request

```python
import openmeteo_requests

openmeteo = openmeteo_requests.Client()

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "hourly": ["temperature_2m", "precipitation", "wind_speed_10m"],
    "current": ["temperature_2m", "relative_humidity_2m"],
}
responses = openmeteo.weather_api(url, params=params)

response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone offset: {response.UtcOffsetSeconds()}s")
```

### Basic asynchronous request

```python
import asyncio
import openmeteo_requests

async def main():
    openmeteo = openmeteo_requests.AsyncClient()

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 52.52,
        "longitude": 13.41,
        "current": ["temperature_2m", "relative_humidity_2m"],
    }
    responses = await openmeteo.weather_api(url, params=params)

    response = responses[0]
    current = response.Current()
    print(f"Temperature: {current.Variables(0).Value()}°C")
    print(f"Humidity: {current.Variables(1).Value()}%")

asyncio.run(main())
```

### Processing current data

The order of variables in the response matches the order requested in params:

```python
current = response.Current()
# Variables are indexed by request order
current_time = current.Time()
current_temperature = current.Variables(0).Value()
current_humidity = current.Variables(1).Value()
```

### Processing hourly data

```python
hourly = response.Hourly()

# Time range: start (unix), end (unix), interval (seconds)
hourly_time_start = hourly.Time()
hourly_time_end = hourly.TimeEnd()
hourly_interval = hourly.Interval()

# Iterate all variables
hourly_variables = [hourly.Variables(i) for i in range(hourly.VariablesLength())]

# Access a specific variable's values as NumPy array
temp_var = hourly_variables[0]
temperature_values = temp_var.ValuesAsNumpy()
```

### NumPy integration

Hourly and daily values are available as NumPy arrays via `.ValuesAsNumpy()`:

```python
import numpy as np
from openmeteo_sdk.Variable import Variable

hourly = response.Hourly()
hourly_variables = [hourly.Variables(i) for i in range(hourly.VariablesLength())]

# Find variable by type and altitude
hourly_temperature_2m = next(
    filter(
        lambda x: x.Variable() == Variable.temperature and x.Altitude() == 2,
        hourly_variables
    )
).ValuesAsNumpy()
```

### Pandas integration

```python
import pandas as np

hourly = response.Hourly()

hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s"),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )
}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["precipitation"] = hourly_precipitation

hourly_df = pd.DataFrame(data=hourly_data)
```

### Polars integration

```python
import polars as pl
from datetime import datetime, timedelta, timezone

hourly = response.Hourly()

start = datetime.fromtimestamp(hourly.Time(), timezone.utc)
end = datetime.fromtimestamp(hourly.TimeEnd(), timezone.utc)
freq = timedelta(seconds=hourly.Interval())

hourly_df = pl.select(
    date=pl.datetime_range(start, end, freq, closed="left"),
    temperature_2m=hourly_temperature_2m,
    precipitation=hourly_precipitation,
    wind_speed_10m=hourly_wind_speed_10m,
)
```

### Multiple locations and models

Pass lists for latitude, longitude, or models to get multiple responses:

```python
params = {
    "latitude": [52.52, 50.1155],
    "longitude": [13.41, 8.6842],
    "hourly": "temperature_2m",
    "models": ["icon_global", "icon_eu"],
}
responses = openmeteo.weather_api(url, params=params)

for response in responses:
    print(f"Location: {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Model: {response.Model()}")
```

The Cartesian product of locations and models is returned — 2 locations × 2 models = 4 responses.

### Caching with requests-cache

Cache weather data to avoid repeated API calls:

```python
import requests_cache
from retry_requests import retry

cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)
```

Cached data is stored in a local SQLite database (`.cache.sqlite`). `expire_after=3600` caches for one hour; use `expire_after=-1` for indefinite caching.

### Custom session

Pass any `niquests.Session` (or `niquests.AsyncSession` for AsyncClient) to the client:

```python
import niquests
import openmeteo_requests

session = niquests.Session()
session.headers.update({"User-Agent": "MyApp/1.0"})
openmeteo = openmeteo_requests.Client(session=session)
```

When a session is passed, the client does not own it and will not close it on deletion.

### POST method

Use POST for large parameter sets (e.g., many locations):

```python
responses = openmeteo.weather_api(url, params=params, method="POST")
```

### SSL verification

```python
responses = openmeteo.weather_api(url, params=params, verify="/path/to/ca-bundle.crt")
```

## Gotchas

- **FlatBuffers require `()` calls** — every attribute access is a method call, not a property. Use `response.Latitude()`, not `response.Latitude`. This is by design for zero-copy efficiency.
- **Variable order matters** — the index used with `.Variables(i)` must match the order you requested in params. If you request `["temperature_2m", "precipitation"]`, then `Variables(0)` is temperature and `Variables(1)` is precipitation.
- **Module creates its own session** — `Client()` creates and owns a `niquests.Session`, closing it on `__del__`. If you pass your own session, the client won't close it.
- **AsyncClient doesn't own sessions** — `AsyncClient` does not manage session lifecycle. Pass a session explicitly or it creates per-request connections.
- **`responses` is always a list** — even for a single location, the result is `list[WeatherApiResponse]`. Always index or iterate: `responses[0]`.
- **No built-in retry** — the client has no retry logic. Use `retry_requests` wrapper around the session for automatic retries on network errors.
- **No built-in caching** — the client has no caching. Use `requests-cache` to wrap the session.
- **`OpenMeteoRequestsError` wraps all failures** — both API errors (400, 429) and transport errors are wrapped. Check `__cause__` for the original exception.
- **Time values are Unix timestamps** — `.Time()`, `.TimeEnd()` return seconds since epoch. Convert with `pd.to_datetime(value, unit="s")` or `datetime.fromtimestamp(value, tz=timezone.utc)`.
- **Missing values are `NaN`** — in NumPy arrays, missing weather values appear as `NaN` (float), not `None`. Use `np.isnan()` to detect.
- **`openmeteo-sdk` is required** — the `WeatherApiResponse` and `Variable` enum come from `openmeteo-sdk`, installed as a dependency. Import `Variable` from `openmeteo_sdk.Variable` for filtering.

## References

- [01-api-reference](references/01-api-reference.md) — Full API surface: Client, AsyncClient, weather_api parameters, WeatherApiResponse methods
- [02-data-processing](references/02-data-processing.md) — Working with hourly/daily data, NumPy arrays, Pandas DataFrames, Polars DataFrames
- [03-endpoints](references/03-endpoints.md) — Supported API endpoints: forecast, historical, climate, air quality, marine
