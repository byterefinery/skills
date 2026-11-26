# Data Processing — openmeteo-requests 1.7.2

## Working with Hourly Data

Hourly data is returned as a FlatBuffers `Hourly` block. Access patterns:

```python
hourly = response.Hourly()

# Time metadata
start = hourly.Time()        # Unix timestamp
end = hourly.TimeEnd()       # Unix timestamp
interval = hourly.Interval() # seconds (typically 3600)

# All variables
num_vars = hourly.VariablesLength()
variables = [hourly.Variables(i) for i in range(num_vars)]

# Single variable
var = hourly.Variables(0)
values = var.ValuesAsNumpy()  # NumPy array
single_value = var.Values(0)  # float at index 0
```

### Finding variables by type

Use `openmeteo_sdk.Variable` enum to identify variable types:

```python
from openmeteo_sdk.Variable import Variable

hourly = response.Hourly()
variables = [hourly.Variables(i) for i in range(hourly.VariablesLength())]

# Find temperature at 2m altitude
temp_2m = next(
    v for v in variables
    if v.Variable() == Variable.temperature and v.Altitude() == 2
)
values = temp_2m.ValuesAsNumpy()

# Find precipitation (no altitude)
precip = next(
    v for v in variables
    if v.Variable() == Variable.precipitation
)
```

### Building a time index

```python
# As list of Unix timestamps
timestamps = list(range(hourly.Time(), hourly.TimeEnd(), hourly.Interval()))

# As Python datetimes
from datetime import datetime, timedelta, timezone
start = datetime.fromtimestamp(hourly.Time(), timezone.utc)
step = timedelta(seconds=hourly.Interval())
times = [start + i * step for i in range(len(timestamps))]
```

---

## NumPy Integration

`.ValuesAsNumpy()` returns a `numpy.ndarray` of float32 values. Missing data appears as `NaN`.

```python
import numpy as np

values = var.ValuesAsNumpy()

# Check for missing values
mask = np.isnan(values)
valid_count = np.count_nonzero(~mask)

# Statistical operations
mean_temp = np.nanmean(values)
max_temp = np.nanmax(values)
min_temp = np.nanmin(values)

# Rolling average (3-hour window)
from numpy.lib.stride_tricks import sliding_window_view
windows = sliding_window_view(values, window_shape=3)
rolling_mean = np.nanmean(windows, axis=1)
```

---

## Pandas Integration

Build a DataFrame from hourly data:

```python
import pandas as pd

hourly = response.Hourly()

# Build time index
date_range = pd.date_range(
    start=pd.to_datetime(hourly.Time(), unit="s"),
    end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
    freq=pd.Timedelta(seconds=hourly.Interval()),
    inclusive="left"
)

# Build DataFrame
data = {"date": date_range}
data["temperature_2m"] = temp_var.ValuesAsNumpy()
data["precipitation"] = precip_var.ValuesAsNumpy()
data["wind_speed_10m"] = wind_var.ValuesAsNumpy()

df = pd.DataFrame(data).set_index("date")
```

### Daily data

Same pattern with `response.Daily()`:

```python
daily = response.Daily()

date_range = pd.date_range(
    start=pd.to_datetime(daily.Time(), unit="s"),
    end=pd.to_datetime(daily.TimeEnd(), unit="s"),
    freq=pd.Timedelta(seconds=daily.Interval()),
    inclusive="left"
)
```

---

## Polars Integration

Build a Polars DataFrame:

```python
import polars as pl
from datetime import datetime, timedelta, timezone

hourly = response.Hourly()

start = datetime.fromtimestamp(hourly.Time(), timezone.utc)
end = datetime.fromtimestamp(hourly.TimeEnd(), timezone.utc)
freq = timedelta(seconds=hourly.Interval())

df = pl.select(
    date=pl.datetime_range(start, end, freq, closed="left"),
    temperature_2m=temp_var.ValuesAsNumpy(),
    precipitation=precip_var.ValuesAsNumpy(),
    wind_speed_10m=wind_var.ValuesAsNumpy(),
)
```

---

## Multiple Locations

When requesting multiple locations, iterate the responses list:

```python
params = {
    "latitude": [52.52, 48.8566, 41.9028],
    "longitude": [13.41, 2.3522, 12.4964],
    "current": "temperature_2m",
}
responses = openmeteo.weather_api(url, params=params)

for i, response in enumerate(responses):
    current = response.Current()
    print(f"Location {i}: {response.Latitude()}, {response.Longitude()}")
    print(f"  Temperature: {current.Variables(0).Value()}°C")
```

---

## Multiple Models

Request multiple weather models:

```python
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "hourly": "temperature_2m",
    "models": ["icon_global", "icon_eu", "ecmwf_ifs04"],
}
responses = openmeteo.weather_api(url, params=params)

for response in responses:
    print(f"Model: {response.Model()}")
    hourly = response.Hourly()
    temp = hourly.Variables(0).ValuesAsNumpy()
    print(f"  Mean temp: {np.nanmean(temp):.1f}°C")
```

The Cartesian product of locations × models is returned. For 3 locations and 3 models, you get 9 responses.

---

## Handling Missing Values

Missing values in weather data appear as `NaN` in NumPy arrays:

```python
import numpy as np

values = var.ValuesAsNumpy()

# Count missing
missing_count = np.isnan(values).sum()

# Fill with forward fill (pandas)
import pandas as pd
series = pd.Series(values).ffill()

# Interpolate
interpolated = pd.Series(values).interpolate(method="linear")

# Drop rows with any NaN (pandas DataFrame)
df = df.dropna()

# Replace NaN with a sentinel
filled = np.nan_to_num(values, nan=-999)
```
