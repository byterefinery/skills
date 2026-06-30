# API Endpoints — openmeteo-requests 1.7.2

The `openmeteo_requests.Client` works with any Open-Meteo API endpoint. Set the `url` parameter to the appropriate endpoint.

## Forecast API

```
https://api.open-meteo.com/v1/forecast
```

Weather forecast data. Supports `current`, `hourly`, and `daily` variable groups.

```python
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "current": ["temperature_2m", "relative_humidity_2m"],
    "hourly": ["temperature_2m", "precipitation", "wind_speed_10m"],
    "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
    "forecast_days": 7,
}
```

### Available parameters

| Parameter | Description |
|---|---|
| `latitude`, `longitude` | Coordinates (single value or list) |
| `current` | Variables for current conditions |
| `hourly` | Variables for hourly data |
| `daily` | Variables for daily aggregates |
| `forecast_days` | Number of forecast days (1-16, default 7) |
| `past_days` | Number of past days to include |
| `timezone` | Timezone (IANA name, default UTC) |
| `models` | Weather models to use (list) |
| `temperature_unit` | `celsius` (default) or `fahrenheit` |
| `wind_speed_unit` | `kmh`, `mph`, `ms`, `kn` |
| `precipitation_unit` | `mm` or `inch` |

## Historical Weather API

```
https://archive-api.open-meteo.com/v1/archive
```

Historical weather data from 1940 onward. Same response format as forecast.

```python
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
}
```

## Climate Consent API

```
https://climate-api.open-meteo.com/v1/climate
```

Climate normals and projections (e.g., CMIP6 models).

```python
url = "https://climate-api.open-meteo.com/v1/climate"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "elevation": 50,
    "monthly": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
    "climate_period": "1991-2020",
}
```

## Air Quality API

```
https://air-quality-api.open-meteo.com/v1/air-quality
```

Air quality data (PM2.5, PM10, ozone, nitrogen dioxide, etc.).

```python
url = "https://air-quality-api.open-meteo.com/v1/air-quality"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "current": ["pm2_5", "pm10", "ozone", "nitrogen_dioxide"],
    "hourly": ["pm2_5", "pm10", "ozone"],
}
```

## Marine API

```
https://marine-api.open-meteo.com/v1/marine
```

Marine and ocean data (wave height, sea surface temperature, currents).

```python
url = "https://marine-api.open-meteo.com/v1/marine"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "current": ["sea_surface_temperature", "wave_height"],
    "hourly": ["wave_height", "wave_direction", "wave_period"],
}
```

## Snow API

```
https://snow-api.open-meteo.com/v1/snow-depth
```

Snow depth data.

```python
url = "https://snow-api.open-meteo.com/v1/snow-depth"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "daily": ["snowfall_sum", "snowfall_probability", "snow_depth"],
}
```

## Weather Alerts API

```
https://weather-api.open-meteo.com/v1/alerts
```

Current weather warnings and alerts.

```python
url = "https://weather-api.open-meteo.com/v1/alerts"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
}
```

## Endpoint Selection

Choose the endpoint based on the data needed:

| Need | Endpoint |
|---|---|
| Current/forecast weather | `api.open-meteo.com/v1/forecast` |
| Historical weather (1940+) | `archive-api.open-meteo.com/v1/archive` |
| Climate normals/projections | `climate-api.open-meteo.com/v1/climate` |
| Air quality (PM2.5, ozone) | `air-quality-api.open-meteo.com/v1/air-quality` |
| Ocean/marine data | `marine-api.open-meteo.com/v1/marine` |
| Snow depth | `snow-api.open-meteo.com/v1/snow-depth` |
| Weather warnings | `weather-api.open-meteo.com/v1/alerts` |

All endpoints return FlatBuffers data and are processed identically by `Client.weather_api()`.
