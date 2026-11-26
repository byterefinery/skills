---
name: openmeteo-requests-1-7-6
description: >
  Python client (openmeteo-requests) version 1.7.6 for the Open-Meteo Weather
  API — fetches weather forecast and historical archive data using FlatBuffers
  for zero-copy data transfer into NumPy, Pandas, or Polars. Provides sync
  Client and async AsyncClient built on niquests. Use this skill whenever the
  user needs weather data from Open-Meteo in Python, works with weather
  time-series, processes FlatBuffers weather responses, or integrates the
  Open-Meteo API with caching (requests-cache) and retries (retry-requests).
license: MIT
compatibility: Python 3.9+ per pyproject (CI-tested 3.11-3.15, PyPy 3.11); outbound HTTPS to Open-Meteo API hosts
metadata:
  tags:
    - python
    - weather
    - api-client
    - flatbuffers
---

# openmeteo-requests 1.7.6

## Overview

`openmeteo-requests` 1.7.6 is the official Python client for the [Open-Meteo Weather API](https://open-meteo.com), built on `niquests` (a `requests`-compatible HTTP library). It transfers data as FlatBuffers instead of JSON, which is efficient for large time-series volumes and supports zero-copy access — hourly and daily values can be analyzed directly in `numpy`, `pandas`, or `polars` without parsing overhead. FlatBuffers schema definitions live in the [open-meteo/sdk](https://github.com/open-meteo/sdk) repository.

The library is aimed at data scientists processing weather data, including historical data from 1940 onward via the [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api).

Key objects exported from the package:

- **`Client`** — synchronous client; creates its own `niquests.Session` or accepts a custom one
- **`AsyncClient`** — asynchronous client; uses a `niquests.AsyncSession` or per-request async calls
- **`OpenMeteoRequestsError`** — raised on API errors (HTTP 400, 429), stream errors, or request failures

Dependencies: `niquests>=3.15.2`, `openmeteo-sdk>=1.22.0`. The package ships a `py.typed` marker (typed per PEP 561).

Install: `pip install openmeteo-requests==1.7.6`

## Usage

### Basic synchronous request

Forecast plus current weather for Berlin; request only the variables you need.

```python
# pip install openmeteo-requests==1.7.6

import openmeteo_requests

openmeteo = openmeteo_requests.Client()

# The order of variables in hourly or daily matters — it assigns response indexes below
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "hourly": ["temperature_2m", "precipitation", "wind_speed_10m"],
    "current": ["temperature_2m", "relative_humidity_2m"],
}
responses = openmeteo.weather_api(url, params=params)

# First location; add a for-loop over `responses` for multiple locations or models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Current data — variable order must match the request order
current = response.Current()
current_temperature_2m = current.Variables(0).Value()
current_relative_humidity_2m = current.Variables(1).Value()
print(f"Current time: {current.Time()}")
```

### Asynchronous request

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

    current = responses[0].Current()
    print(f"Temperature: {current.Variables(0).Value()}")
    print(f"Humidity: {current.Variables(1).Value()}")

asyncio.run(main())
```

### Hourly data as NumPy arrays

Hourly and daily values are available as NumPy float arrays via `.ValuesAsNumpy()`. Variables are identified by the `Variable` enum and altitude.

```python
from openmeteo_sdk.Variable import Variable

hourly = response.Hourly()
hourly_variables = [hourly.Variables(i) for i in range(hourly.VariablesLength())]

hourly_temperature_2m = next(
    filter(
        lambda x: x.Variable() == Variable.temperature and x.Altitude() == 2,
        hourly_variables,
    )
).ValuesAsNumpy()
```

Full Pandas and Polars DataFrame construction from these arrays is in [02-data-processing](references/02-data-processing.md).

### Historical archive data

Historical weather comes from the archive API, with `start_date`/`end_date` and a model. Coordinate lists request several locations in one call.

```python
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": [52.54, 48.1, 48.4],
    "longitude": [13.41, 9.31, 8.5],
    "hourly": ["temperature_2m", "precipitation"],
    "start_date": "2023-08-01",
    "end_date": "2023-08-02",
    "models": "era5_seamless",
}
responses = openmeteo.weather_api(url, params=params)
```

### Multiple locations and models

Pass lists for `latitude`, `longitude`, or `models` to receive an array of results (one per location/model combination).

```python
params = {
    "latitude": [52.52, 50.1155],
    "longitude": [13.41, 8.6842],
    "hourly": "temperature_2m",
    "models": ["icon_global", "icon_eu"],
}
for response in responses:
    print(f"{response.Latitude()}°N {response.Longitude()}°E, model {response.Model()}")
```

### Caching and retries

Wrap a `requests-cache` session with `retry_requests` and pass it to the client — the client then caches all weather data and retries failed calls.

```python
# pip install requests-cache retry-requests

import openmeteo_requests
import requests_cache
from retry_requests import retry

cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)
```

Cached data is stored in a local SQLite database (`.cache` prefix). `expire_after=3600` caches for one hour; `expire_after=-1` caches indefinitely.

### Custom session, POST, SSL verification

```python
import niquests
import openmeteo_requests

session = niquests.Session()
session.headers.update({"User-Agent": "MyApp/1.0"})
openmeteo = openmeteo_requests.Client(session=session)

# POST sends params as the request body instead of query parameters
responses = openmeteo.weather_api(url, params=params, method="POST")

# verify is keyword-only: True, False, or a path to a CA bundle
responses = openmeteo.weather_api(url, params=params, verify="/path/to/ca-bundle.crt")
```

Any extra keyword argument is passed through to `niquests.Session.get()` / `.post()`.

## Gotchas

- **FlatBuffers require `()` calls** — every response attribute is a method, not a property: `response.Latitude()`, not `response.Latitude`. This is by design for zero-copy access without expensive parsing.
- **Variable order matters** — the index in `.Variables(i)` matches the order you requested in `params`. If you request `["temperature_2m", "precipitation"]`, then `Variables(0)` is temperature and `Variables(1)` is precipitation.
- **`responses` is always a list** — even a single location returns `list[WeatherApiResponse]`. Always index (`responses[0]`) or iterate.
- **`format=flatbuffers` is forced** — the client sets `params["format"] = "flatbuffers"` automatically. Do not pass a different format.
- **Errors are wrapped** — HTTP 400 and 429 raise `OpenMeteoRequestsError` whose message is the API's JSON error body. Every other failure is re-raised as `OpenMeteoRequestsError` with message `failed to request <url>: <error>`; the original exception is in `__cause__`. Stream errors (response body starting with `Unexpected`) also raise `OpenMeteoRequestsError`.
- **Session ownership** — `Client()` creates and owns a `niquests.Session`, closing it in `__del__`. If you pass your own session, the client will not close it. `AsyncClient` never creates a session; without one it uses per-request `niquests.aget()` / `apost()`.
- **Time values are Unix timestamps** — `.Time()`, `.TimeEnd()` return seconds since epoch; `.Interval()` is the step in seconds. Convert with `pd.to_datetime(value, unit="s")` or `datetime.fromtimestamp(value, tz=timezone.utc)`.

## References

- [01-api-reference](references/01-api-reference.md) — Full API surface: Client, AsyncClient, weather_api parameters, response framing, exceptions
- [02-data-processing](references/02-data-processing.md) — Processing current/hourly responses, variable filtering, NumPy arrays, Pandas and Polars DataFrames
- [03-endpoints](references/03-endpoints.md) — Endpoints demonstrated in the v1.7.6 repo: forecast and archive, with example parameters
