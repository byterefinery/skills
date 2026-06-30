---
name: open-meteo-1-5-3
description: Query weather forecasts, historical data, air quality, marine conditions, elevation, climate projections, flood forecasts, seasonal outlooks, and geocoding via the Open-Meteo API. No API key required. Supports FlatBuffers for zero-copy data transfer with NumPy/Pandas/Polars. Use when you need weather data, forecasts, historical weather, air quality, marine forecasts, geocoding, elevation lookup, climate data, flood forecasts, or seasonal outlooks.
metadata:
  tags:
    - weather
    - api
    - data-science
    - geocoding
---

# open-meteo 1.5.3

## Overview

Open-Meteo is a free, open-source weather API requiring no API key. It aggregates data from national weather services (NOAA GFS/HRRR, DWD ICON, MeteoFrance Arome/Arpege, ECMWF IFS, JMA, GEM HRDPS, MET Norway) and exposes it through fast REST endpoints with response times under 10 ms. Data is licensed under CC BY 4.0 (free for non-commercial use).

The API provides nine endpoint groups:

| Endpoint | Base URL | Purpose |
|---|---|---|
| Forecast | `api.open-meteo.com/v1/forecast` | Hourly forecast up to 16 days |
| Historical | `archive-api.open-meteo.com/v1/archived-weather` | ERA5/ERA5-Land data from 1940 |
| Marine | `api.open-meteo.com/v1/marine-forecast` | Wave height, direction, period, swell, currents, SST |
| Air Quality | `air-quality-api.open-meteo.com/v1/air-quality` | PM2.5, PM10, ozone, NO₂, pollen (CAMS) |
| Climate | `climate-api.open-meteo.com/v1/climate` | CMIP6 downscaled data, 1950–2050 |
| Elevation | `api.open-meteo.com/v1/elevation` | 90m DEM terrain elevation |
| Geocoding | `geocoding-api.open-meteo.com/v1/search` | Place name → coordinates |
| Flood | `flood-api.open-meteo.com/v1/flood-forecast` | River discharge (GloFAS) |
| Seasonal | `https://seasonal-api.open-meteo.com/v1/seasonal` | ECMWF SEAS5, up to 9 months ahead |

Regional model variants exist for DWD, ECMWF, GEM, GFS/HRRR, JMA, MeteoFrance, and MET Norway (e.g., `https://dwd-api.open-meteo.com/v1/forecast`).

## Usage

### Direct HTTP

All endpoints accept `latitude` and `longitude` as required query parameters. Request only the variables you need — the API returns exactly what you ask for.

```bash
# Current weather in Berlin
curl "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m,relative_humidity_2m&timezone=auto"

# Hourly forecast with multiple variables
curl "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m,precipitation,wind_speed_10m&timezone=Europe/Berlin"

# Historical weather
curl "https://archive-api.open-meteo.com/v1/archived-weather?latitude=52.52&longitude=13.41&start_date=2023-01-01&end_date=2023-01-07&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"

# Geocoding
curl "https://geocoding-api.open-meteo.com/v1/search?name=Berlin&count=1"

# Elevation
curl "https://api.open-meteo.com/v1/elevation?latitude=52.52&longitude=13.41"

# Air quality
curl "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=52.52&longitude=13.41&hourly=pm10,pm2_5,nox&timezone=auto"

# Marine forecast
curl "https://api.open-meteo.com/v1/marine-forecast?latitude=52.52&longitude=13.41&hourly=wave_height&timezone=auto"
```

### Python (Official SDK — FlatBuffers)

The official Python client uses FlatBuffers instead of JSON, enabling zero-copy data transfer directly into NumPy, Pandas, or Polars. Ideal for data scientists processing large datasets.

```bash
pip install openmeteo-requests
```

```python
import openmeteo_requests

openmeteo = openmeteo_requests.Client()

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "hourly": ["temperature_2m", "precipitation", "wind_speed_10m"],
    "current": ["temperature_2m", "relative_humidity_2m"],
    "timezone": "auto",
}
responses = openmeteo.weather_api(url, params=params)

response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")

current = response.Current()
print(f"Temperature: {current.Variables(0).Value()}°C")
print(f"Humidity: {current.Variables(1).Value()}%")
```

Async variant:

```python
import asyncio, openmeteo_requests

async def main():
    openmeteo = openmeteo_requests.AsyncClient()
    responses = await openmeteo.weather_api(url, params=params)
    # ... same processing

asyncio.run(main())
```

Converting hourly data to a Pandas DataFrame:

```python
import pandas as pd, numpy as np

hourly = response.Hourly()
hourly_temp = next(
    filter(lambda x: x.Variable() == Variable.temperature and x.Altitude() == 2,
           [hourly.Variables(i) for i in range(hourly.VariablesLength())])
).ValuesAsNumpy()

df = pd.DataFrame({
    "date": pd.date_range(
        pd.to_datetime(hourly.Time(), unit="s"),
        pd.to_datetime(hourly.TimeEnd(), unit="s"),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    ),
    "temperature_2m": hourly_temp,
})
```

With caching and retries:

```python
import openmeteo_requests
import requests_cache
from retry_requests import retry

cache = requests_cache.CachedSession('.cache', expire_after=3600)
session = retry(cache, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=session)
```

### Language Libraries

Open-Meteo has community-maintained SDKs for several languages. All wrap the same REST API — choose based on your stack.

**Python** — `openmeteo-requests` (official)
- `pip install openmeteo-requests`
- FlatBuffers for zero-copy transfer into NumPy/Pandas/Polars
- Sync and async clients
- Best for data science and large historical datasets
- GitHub: `open-meteo/python-requests`

**Rust** — `open-meteo-rs`
- `cargo add open-meteo-rs`
- Async (tokio), typed enums for all parameters
- Supports forecast endpoint with full option types
- GitHub: `angelodlfrtr/open-meteo-rs`

**Go** — `omgo`
- `go get github.com/hectormalot/omgo`
- Requires Go 1.21+
- Builder pattern with type-safe metric constants
- Supports forecast, historical data, 15-minutely data, and units control
- GitHub: `HectorMalot/omgo`

**C# / .NET 8** — `OpenMeteo.dotnet.client.sdk`
- `dotnet add package OpenMeteo.dotnet.client.sdk`
- FlatBuffers support for large datasets
- Query by city name or coordinates
- API key support, custom URL for self-hosted instances
- GitHub: `colinnuk/open-meteo-dotnet-client-sdk`

**PHP (Laravel)** — `michaelnabil230/laravel-weather`
- `composer require michaelnabil230/laravel-weather`
- Fluent builder: `Weather::location(lat, lng)->current()->get()`
- Configurable units, timezone, time format
- Supports 15-minutely data, past days, all weather models
- GitHub: `michaelnabil230/laravel-weather`

**PHP (Symfony 6.2+)** — `flibidi67/open-meteo`
- `composer require flibidi67/open-meteo`
- Full Symfony bundle with YAML config per model (default, forecast, historical, ECMWF, GFS, MeteoFrance, DWD)
- Dependency injection via service container
- GitLab: `flibidi67/open-meteo`

**PHP (Geocoding)** — `flibidi67/open-meteo-geocoding`
- `composer require flibidi67/open-meteo-geocoding`
- Works standalone or with Symfony DI
- Methods: `setLanguage()`, `setCount()`, `setCountryCode()`, `get()`
- GitLab: `flibidi67/open-meteo-geocoding`

**Android (Geocoding)** — `OmGeoDialog`
- JitPack: `com.github.woheller69:OmGeoDialog:V1.5`
- Search-as-you-type DialogFragment for place lookup
- Returns coordinates with city name and country code
- Shows results on a map
- GitHub: `woheller69/OmGeoDialog`

### Without an SDK

For any language not listed above, use plain HTTP. All endpoints return JSON by default. The Python FlatBuffers mode is an optimization — the standard JSON response works universally.

```bash
# Universal pattern
curl "https://api.open-meteo.com/v1/forecast?latitude=LAT&longitude=LNG&current=temperature_2m&timezone=auto"
```

## Gotchas

- **Order matters** — variables in `hourly`/`daily`/`current` arrays must be processed in the same order they were requested. The response arrays are positional.
- **Timezone `auto`** — use `timezone=auto` to get local time. Without it, all timestamps default to UTC.
- **Comma-separated coordinates** — pass multiple locations as `latitude=52.52,50.11&longitude=13.41,8.68` to get an array of responses.
- **FlatBuffers require function calls** — in the Python SDK, every attribute is a method call (`response.Latitude()`, not `response.Latitude`). This is by design for zero-copy access.
- **No API key for free tier** — the free API requires no key. Commercial use requires a subscription at `customer-api.open-meteo.com`.
- **Regional model URLs differ** — DWD, ECMWF, GFS, MeteoFrance, etc. each have their own base URL (e.g., `dwd-api.open-meteo.com`).
- **Historical API is separate** — archived data uses `archive-api.open-meteo.com`, not `api.open-meteo.com`.
- **15-minutely data is regional** — only available where high-resolution models cover the area (Europe, North America).
- **`past_days` is mutually exclusive with date ranges** — you cannot use `past_days` together with `start_date`/`end_date` on the forecast endpoint.
- **Weather codes are WMO codes** — 0 = clear sky, 1–3 = partly/cloudy, 45–48 = fog, 51–67 = drain/rain, 71–77 = snow, 80–89 = showers, 95–99 = thunderstorm.

## References

- [01-api-endpoints](references/01-api-endpoints.md) — All API endpoints, parameters, and response formats
- [02-forecast-variables](references/02-forecast-variables.md) — Complete list of hourly/daily/current weather variables
- [03-regional-models](references/03-regional-models.md) — Regional weather model endpoints (DWD, ECMWF, GFS, MeteoFrance, etc.)
- [04-client-libraries](references/04-client-libraries.md) — Detailed usage for each language SDK
- [05-specialized-apis](references/05-specialized-apis.md) — Air quality, marine, climate, elevation, flood, seasonal, geocoding
