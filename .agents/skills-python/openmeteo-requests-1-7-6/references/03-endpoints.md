# API Endpoints — openmeteo-requests 1.7.6

The client is endpoint-agnostic: `weather_api(url, params)` accepts any Open-Meteo API URL and forces `format=flatbuffers` on the request. The v1.7.6 repo documents two endpoints — forecast and archive (historical). For the full parameter reference of other Open-Meteo services (air quality, marine, etc.), consult the [Open-Meteo documentation](https://open-meteo.com); the v1.7.6 README lists documenting further endpoints as an open TODO.

## Forecast API

```
https://api.open-meteo.com/v1/forecast
```

Example parameters from the v1.7.6 README (Berlin, hourly forecast plus current conditions):

```python
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "hourly": ["temperature_2m", "precipitation", "wind_speed_10m"],
    "current": ["temperature_2m", "relative_humidity_2m"],
}
```

The same `params` mapping style applies to `daily` and other variable groups — the README notes the order of variables matters for assigning response indexes.

## Archive API (historical weather)

```
https://archive-api.open-meteo.com/v1/archive
```

Historical data from 1940 onward. Example parameters from the v1.7.6 test suite (three locations, two-day range, single model):

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
```

List-valued `latitude`/`longitude` request multiple locations in one call; `models` may be a string or a list.

## Reference links

- Open-Meteo Weather API: https://open-meteo.com
- Open-Meteo Historical Weather API docs: https://open-meteo.com/en/docs/historical-weather-api
- FlatBuffers schemas: https://github.com/open-meteo/sdk
- Library repository: https://github.com/open-meteo/python-requests
