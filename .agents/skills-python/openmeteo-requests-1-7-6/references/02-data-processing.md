# Data Processing — openmeteo-requests 1.7.6

How to read `WeatherApiResponse` objects returned by `weather_api` and move the data into NumPy, Pandas, or Polars. All examples come from the v1.7.6 README and test suite.

## Response structure

Each `WeatherApiResponse` (from `openmeteo-sdk`) is a FlatBuffers message. Attributes are method calls — `response.Latitude()`, not `response.Latitude`:

- Location/metadata: `Latitude()`, `Longitude()`, `Elevation()`, `UtcOffsetSeconds()`, `Model()`
- Variable groups: `Current()`, `Hourly()`, `Daily()` — each has `Time()`, `TimeEnd()`, `Interval()`, `Variables(i)`, `VariablesLength()`
- A variable has `Variable()` (the `openmeteo_sdk.Variable.Variable` enum value), `Altitude()`, `Value()` (for current), and `ValuesAsNumpy()` for series data

Time values are Unix timestamps in seconds; `Interval()` is the step between values in seconds.

## Current data

Variable indexes match the request order:

```python
current = response.Current()
current_time = current.Time()
current_temperature_2m = current.Variables(0).Value()
current_relative_humidity_2m = current.Variables(1).Value()
```

## Hourly data as NumPy arrays

Iterate all variables, then select by `Variable()` enum value and `Altitude()`:

```python
import numpy as np
from openmeteo_sdk.Variable import Variable

hourly = response.Hourly()
hourly_time = range(hourly.Time(), hourly.TimeEnd(), hourly.Interval())
hourly_variables = list(map(lambda i: hourly.Variables(i), range(0, hourly.VariablesLength())))

hourly_temperature_2m = next(
    filter(
        lambda x: x.Variable() == Variable.temperature and x.Altitude() == 2,
        hourly_variables
    )
).ValuesAsNumpy()
hourly_precipitation = next(
    filter(
        lambda x: x.Variable() == Variable.precipitation,
        hourly_variables
    )
).ValuesAsNumpy()
hourly_wind_speed_10m = next(
    filter(
        lambda x: x.Variable() == Variable.wind_speed and x.Altitude() == 10,
        hourly_variables
    )
).ValuesAsNumpy()
```

Values arrays are float arrays; `ValuesLength()` gives the count (the v1.7.6 tests assert `ValuesLength() == 48` for a two-day hourly request).

## Pandas DataFrame

Build a `date_range` from the hourly time window (inclusive of start, exclusive of end) and attach the NumPy arrays:

```python
import pandas as pd

hourly_data = {"date": pd.date_range(
    start = pd.to_datetime(hourly.Time(), unit = "s"),
    end = pd.to_datetime(hourly.TimeEnd(), unit = "s"),
    freq = pd.Timedelta(seconds = hourly.Interval()),
    inclusive = "left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["precipitation"] = hourly_precipitation
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

hourly_dataframe_pd = pd.DataFrame(data = hourly_data)
```

## Polars DataFrame

Same idea with `pl.datetime_range`:

```python
import polars as pl
from datetime import datetime, timedelta, timezone

start = datetime.fromtimestamp(hourly.Time(), timezone.utc)
end = datetime.fromtimestamp(hourly.TimeEnd(), timezone.utc)
freq = timedelta(seconds = hourly.Interval())

hourly_dataframe_pl = pl.select(
    date = pl.datetime_range(start, end, freq, closed = "left"),
    temperature_2m = hourly_temperature_2m,
    precipitation = hourly_precipitation,
    wind_speed_10m = hourly_wind_speed_10m
)
```

## Multiple locations and models

With list-valued `latitude`/`longitude`/`models` parameters, iterate over every response:

```python
params = {
    "latitude": [52.52, 50.1155],
    "longitude": [13.41, 8.6842],
    "hourly": "temperature_2m",
    "models": ["icon_global", "icon_eu"],
}

for response in responses:
    print(f"\nCoordinates: {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation: {response.Elevation()} m asl")
    print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")
    print(f"Model Nº: {response.Model()}")
```

## Archive (historical) request pattern

The test suite exercises the archive endpoint with three locations, a date range, and the `era5_seamless` model:

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
responses = client.weather_api(url=url, params=params)
# len(responses) == 3 — one per location
```

The same processing applies: `responses[0].Hourly()`, filter variables by `Variable()` enum, `ValuesAsNumpy()`.
