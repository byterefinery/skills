# API Endpoints

## Weather Forecast API

**Base URL:** `https://api.open-meteo.com/v1/forecast`

### Required Parameters

| Parameter | Type | Description |
|---|---|---|
| `latitude` | float | WGS84 latitude, multiple values comma-separated |
| `longitude` | float | WGS84 longitude, multiple values comma-separated |

### Optional Parameters

| Parameter | Values | Description |
|---|---|---|
| `current` | comma-separated variables | Current weather conditions |
| `hourly` | comma-separated variables | Hourly forecast data |
| `daily` | comma-separated variables | Daily aggregates |
| `past_days` | 0–2 | Include past days in forecast |
| `forecast_days` | 0–16 | Number of forecast days |
| `start_date` | YYYY-MM-DD | Start date (exclusive with `past_days`) |
| `end_date` | YYYY-MM-DD | End date |
| `timezone` | IANA name / `auto` | Timezone for timestamps |
| `temperature_unit` | `celsius`, `fahrenheit` | Temperature unit |
| `wind_speed_unit` | `kmh`, `ms`, `mph`, `kn` | Wind speed unit |
| `precipitation_unit` | `mm`, `inch` | Precipitation unit |
| `models` | model name(s) | Specific weather model |
| `cell_selection` | `land`, `sea`, `nearest` | Cell type preference |
| `elevation` | float / `nan` | Force specific elevation |
| `forecast_run` | YYYY-MM-DDThh:mm | Specific forecast run time |
| `digitally_signed_data` | `true`, `false` | DSS signature for model data |

### Response Format

```json
{
  "latitude": 52.52,
  "longitude": 13.41,
  "generationtime_ms": 0.5,
  "utc_offset_seconds": 3600,
  "timezone": "Europe/Berlin",
  "timezone_abbreviation": "CET",
  "elevation": 44.0,
  "current_units": {
    "time": "unixtime",
    "temperature_2m": "°C",
    "relative_humidity_2m": "%"
  },
  "current": {
    "time": 1710000000,
    "temperature_2m": 18.5,
    "relative_humidity_2m": 65
  },
  "hourly_units": {
    "time": "iso8601",
    "temperature_2m": "°C",
    "precipitation": "mm"
  },
  "hourly": {
    "time": ["2024-03-09T00:00", "2024-03-09T01:00", ...],
    "temperature_2m": [17.4, 17.0, ...],
    "precipitation": [0.0, 0.0, ...]
  }
}
```

## Historical Weather API

**Base URL:** `https://archive-api.open-meteo.com/v1/archived-weather`

### Parameters

| Parameter | Values | Description |
|---|---|---|
| `latitude` | float | Required |
| `longitude` | float | Required |
| `start_date` | YYYY-MM-DD | Required, ≥ 1940-01-01 |
| `end_date` | YYYY-MM-DD | Required |
| `daily` | comma-separated | Daily aggregates |
| `hourly` | comma-separated | Hourly data |
| `timezone` | IANA / `auto` | Timezone |
| `temperature_unit` | `celsius`, `fahrenheit` | Temperature unit |
| `wind_speed_unit` | `kmh`, `ms`, `mph`, `kn` | Wind speed unit |
| `precipitation_unit` | `mm`, `inch` | Precipitation unit |

Data sources: ERA5 (1940–2021, 0.1° resolution) and ERA5-Land (1950–present, 0.1° resolution).

## Marine Weather Forecast API

**Base URL:** `https://api.open-meteo.com/v1/marine-forecast`

Same parameters as forecast API plus marine-specific variables: `wave_height`, `wave_direction`, `wave_period`, `swell_wave_height`, `swell_wave_direction`, `swell_wave_period`, `chop_wave_height`, `chop_wave_direction`, `sea_surface_temperature`, `sea_ice`, `current_speed`, `current_direction`.

## Elevation API

**Base URL:** `https://api.open-meteo.com/v1/elevation`

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `latitude` | float | Required |
| `longitude` | float | Required |
| `model` | `aster`, `copernicus`, `ecmwf` | DEM source |

### Response

```json
{
  "results": [
    {"elevation": 44.0, "latitude": 52.52, "longitude": 13.41, "unit": "m"}
  ]
}
```

## Geocoding API

**Base URL:** `https://geocoding-api.open-meteo.com/v1/search`

### Parameters

| Parameter | Values | Description |
|---|---|---|
| `name` | string | Required, ≥ 3 characters |
| `count` | 1–100 | Max results (default: 10) |
| `language` | `en`, `de`, `fr`, `es`, `it`, `pt`, `ru`, `tr`, `hi` | Language |
| `country_codes` | ISO 3166-1 alpha-2 | Filter by country |
| `boundingbox` | south,west,north,east | Bounding box filter |

### Response

```json
{
  "results": [
    {
      "id": 600001,
      "latitude": 52.52,
      "longitude": 13.41,
      "elevation": 44,
      "feature_code": "PPLC",
      "country_code": "DE",
      "admin1_id": 2953851,
      "admin2_id": 6547138,
      "name": "Berlin",
      "country": "Germany",
      "admin1": "Berlin",
      "population": 3426354
    }
  ]
}
```

## Air Quality API

**Base URL:** `https://air-quality-api.open-meteo.com/v1/air-quality`

Variables: `pm10`, `pm2_5`, `carbon_monoxide`, `nitrogen_dioxide`, `ozone`, `sulphur_dioxide`, `dust`, `pollen_olive`, `pollen_cypress`, `pollen_graminaceae`, `pollen_umbelliferae`, `pollen_betula`, `pollen_artemisia`, `uv_index`, `uv_index_clear_sky`.

## Climate Change API

**Base URL:** `https://climate-api.open-meteo.com/v1/climate`

CMIP6 downscaled models, bias-corrected to ERA5. Covers 1950–2050. Parameters include `climate_model` (e.g., `IPCC-Scenario-1-1-2-6`, `IPCC-Scenario-2-6`, `IPCC-Scenario-5-8-5`), `start_date`, `end_date`, `daily` variables.

## Flood Forecast API

**Base URL:** `https://flood-api.open-meteo.com/v1/flood-forecast`

GloFAS hydrological model. Parameters: `latitude`, `longitude`, `forecast_days` (1–20), `daily` (`river_discharge`).

## Seasonal Forecast API

**Base URL:** `https://seasonal-api.open-meteo.com/v1/seasonal`

ECMWF SEAS5 ensemble. Up to 9 months ahead. Parameters: `latitude`, `longitude`, `daily` (`temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, etc.), `seasonal` for probabilistic data.
