# Client Libraries

## Python — openmeteo-requests (Official)

**Install:** `pip install openmeteo-requests`
**Repo:** `github.com/open-meteo/python-requests`
**License:** MIT

### Key Features
- FlatBuffers data transfer (zero-copy)
- Direct integration with NumPy, Pandas, Polars
- Sync and async clients
- Caching via `requests-cache`
- Retry via `retry-requests`

### Client Setup

```python
import openmeteo_requests

# Basic client
openmeteo = openmeteo_requests.Client()

# Async client
openmeteo = openmeteo_requests.AsyncClient()

# With caching and retries
import requests_cache
from retry_requests import retry

cache = requests_cache.CachedSession('.cache', expire_after=3600)
session = retry(cache, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=session)
```

### Accessing Response Data

FlatBuffers use method calls (not attribute access):

```python
response = responses[0]

# Location info
response.Latitude()
response.Longitude()
response.Elevation()
response.UtcOffsetSeconds()
response.Timezone()
response.TimezoneAbbreviation()

# Current data
current = response.Current()
current.Time()
current.Variables(index).Value()
current.Variables(index).Variable()  # Variable enum
current.Variables(index).Altitude()   # Altitude in meters

# Hourly data
hourly = response.Hourly()
hourly.Time()          # Start timestamp (unix)
hourly.TimeEnd()       # End timestamp (unix)
hourly.Interval()      # Interval in seconds
hourly.VariablesLength()  # Number of variables
hourly.Variables(i).ValuesAsNumpy()  # NumPy array
hourly.Variables(i).Variable()       # Variable enum
hourly.Variables(i).Altitude()       # Altitude
```

### Converting to Pandas

```python
import pandas as pd

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

### Converting to Polars

```python
import polars as pl
from datetime import datetime, timedelta, timezone

start = datetime.fromtimestamp(hourly.Time(), timezone.utc)
end = datetime.fromtimestamp(hourly.TimeEnd(), timezone.utc)
freq = timedelta(seconds=hourly.Interval())

df = pl.select(
    date=pl.datetime_range(start, end, freq, closed="left"),
    temperature_2m=hourly_temp,
)
```

---

## Rust — open-meteo-rs

**Install:** `cargo add open-meteo-rs`
**Repo:** `github.com/angelodlfrtr/open-meteo-rs`

### Usage

```rust
#[tokio::main]
async fn main() {
    let client = open_meteo_rs::Client::new();
    let mut opts = open_meteo_rs::forecast::Options::default();

    opts.location = open_meteo_rs::Location {
        lat: 48.86,
        lng: 2.35,
    };
    opts.temperature_unit = Some(open_meteo_rs::forecast::TemperatureUnit::Celsius);
    opts.wind_speed_unit = Some(open_meteo_rs::forecast::WindSpeedUnit::Kmh);
    opts.precipitation_unit = Some(open_meteo_rs::forecast::PrecipitationUnit::Millimeters);
    opts.time_zone = Some("Europe/Paris".into());
    opts.forecast_days = Some(2);

    let response = client.forecast(opts).await.unwrap();
}
```

### Available Options
- `location` — latitude/longitude
- `elevation` — force elevation or `Nan`
- `temperature_unit` — Celsius / Fahrenheit
- `wind_speed_unit` — Kmh / Ms / Mph / Kn
- `precipitation_unit` — Millimeters / Inches
- `time_zone` — IANA timezone string
- `past_days` — 0–2 (exclusive with dates)
- `forecast_days` — 0–16 (exclusive with dates)
- `start_date` / `end_date` — date range
- `models` — model names
- `cell_selection` — Land / Sea / Nearest

---

## Go — omgo

**Install:** `go get github.com/hectormalot/omgo`
**Repo:** `github.com/HectorMalot/omgo`
**Requires:** Go 1.21+

### Usage

```go
package main

import (
    "context"
    "fmt"
    "log"
    "github.com/hectormalot/omgo"
)

func main() {
    client := omgo.NewClient()

    req, err := omgo.NewForecastRequest(52.3738, 4.8910)
    if err != nil { log.Fatal(err) }

    req.WithHourly(omgo.HourlyTemperature2m, omgo.HourlyPrecipitation).
        WithDaily(omgo.DailyTemperature2mMax, omgo.DailyTemperature2mMin).
        WithTimezone("Europe/Berlin")

    weather, err := client.Forecast(context.Background(), req)
    if err != nil { log.Fatal(err) }

    fmt.Printf("Temperature: %.1f%s\n",
        weather.Hourly.Temperature2m[0],
        weather.HourlyUnits.Temperature2m)
}
```

### Features
- Type-safe metric constants with autocomplete
- Builder pattern for fluent request construction
- 15-minutely data support
- Historical data endpoint
- Full unit control

---

## C# / .NET 8 — OpenMeteo.dotnet.client.sdk

**Install:** `dotnet add package OpenMeteo.dotnet.client.sdk`
**Repo:** `github.com/colinnuk/open-meteo-dotnet-client-sdk`
**License:** MIT

### Usage

```csharp
using OpenMeteo;

var client = new OpenMeteoClient();

// Query by city name
var weather = await client.QueryWeatherApiAsync("Tokyo");
Console.WriteLine($"Temperature: {weather.Current.Temperature}{weather.CurrentUnits.Temperature}");

// Query by coordinates
var weather2 = await client.QueryWeatherApiAsync(52.52, 13.41);

// With API key (commercial)
var clientKeyed = new OpenMeteoClient("YourApiKey");

// Custom URL (self-hosted)
var clientCustom = new OpenMeteoClient(baseUrl: "https://my-server.com");
```

### Features
- FlatBuffers support for large datasets
- Query by city name or coordinates
- API key support
- Custom base URL for self-hosted instances
- All classes are public for extension

---

## PHP — Laravel Weather

**Install:** `composer require michaelnabil230/laravel-weather`
**Repo:** `github.com/michaelnabil230/laravel-weather`

### Usage

```php
// Current weather
$weather = \MichaelNabil230\Weather\Weather::location(30.08, 31.25)
    ->current()
    ->get();

// With options
$weather = \MichaelNabil230\Weather\Weather::location(30.08, 31.25)
    ->temperatureUnit('fahrenheit')
    ->windSpeedUnit('mph')
    ->precipitationUnit('inch')
    ->timezone('America/New_York')
    ->currentWeather(true)
    ->pastDays(1)
    ->get();
```

### Config

Publish config: `php artisan vendor:publish --tag="laravel-weather-config"`

```php
return [
    'temperature_unit' => 'celsius',
    'wind_speed_unit' => 'kmh',
    'precipitation_unit' => 'mm',
    'time_format' => 'iso8601',
    'timezone' => 'GMT',
];
```

---

## PHP — Symfony (flibidi67/open-meteo)

**Install:** `composer require flibidi67/open-meteo`
**Repo:** `gitlab.com/flibidi67/open-meteo`

### Config

```yaml
# config/packages/flibidi67_open_meteo.yaml
flibidi67_open_meteo:
  default:
    temperature_unit: "celsius"
    wind_speed_unit: "kmh"
    precipitation_unit: "mm"
    timeformat: "iso8601"
    timezone: "GMT"
    past_days: 0
    forecast_days: 7
    current_weather: false
```

### Usage

```php
use Flibidi67\OpenMeteo\Service\OpenMeteoService;

// Via DI
public function __construct(OpenMeteoService $service) {
    $data = $service->getWeatherForecast(52.52, 13.41);
}

// Or standalone
$service = new OpenMeteoService();
$data = $service->getWeatherForecast(52.52, 13.41);
```

---

## PHP — Geocoding (flibidi67/open-meteo-geocoding)

**Install:** `composer require flibidi67/open-meteo-geocoding`
**Repo:** `gitlab.com/flibidi67/open-meteo-geocoding`

### Usage

```php
use Flibidi67\OpenMeteoGeocoding\Service\GeocodingService;

$service = new GeocodingService();
$service->setLanguage('en');
$service->setCount(5);
$results = $service->get('Berlin');
```

---

## Android — OmGeoDialog

**Install:** JitPack `com.github.woheller69:OmGeoDialog:V1.5`
**Repo:** `github.com/woheller69/OmGeoDialog`

### Usage

```java
public class MainActivity extends AppCompatActivity implements OmGeoDialog.OmGeoDialogResult {
    @Override
    public void onOmGeoDialogResult(City city) {
        String name = city.getCityName();
        String country = city.getCountryCode();
        float lat = city.getLatitude();
        float lon = city.getLongitude();
    }
}
```

Opens a search-as-you-type dialog, returns coordinates on selection.
