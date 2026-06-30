# Specialized APIs

## Air Quality API

**Base URL:** `https://air-quality-api.open-meteo.com/v1/air-quality`

Hourly air quality forecasts from the Copernicus Atmosphere Monitoring Service (CAMS).

### Variables

| Variable | Unit | Description |
|---|---|---|
| `pm10` | μg/m³ | Particulate matter ≤ 10μm |
| `pm2_5` | μg/m³ | Particulate matter ≤ 2.5μm |
| `carbon_monoxide` | μg/m³ | Carbon monoxide |
| `nitrogen_dioxide` | μg/m³ | Nitrogen dioxide |
| `ozone` | μg/m³ | Ozone |
| `sulphur_dioxide` | μg/m³ | Sulphur dioxide |
| `dust` | μg/m³ | Dust |
| `pollen_olive` | — | Olive pollen (low/medium/high/very high) |
| `pollen_cypress` | — | Cypress pollen |
| `pollen_graminaceae` | — | Grass pollen |
| `pollen_umbelliferae` | — | Umbelliferae pollen |
| `pollen_betula` | — | Birch pollen |
| `pollen_artemisia` | — | Mugwort pollen |
| `uv_index` | — | UV index |
| `uv_index_clear_sky` | — | UV index if clear sky |
| `fire_danger_index` | — | Fire danger (0–100) |

### Example

```bash
curl "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=52.52&longitude=13.41&hourly=pm10,pm2_5,nox,ozone&current=pm10,pm2_5&timezone=auto"
```

---

## Marine Weather API

**Base URL:** `https://api.open-meteo.com/v1/marine-forecast`

Hourly marine weather forecasts for oceans and seas.

### Variables

| Variable | Unit | Description |
|---|---|---|
| `wave_height` | m | Significant wave height |
| `wave_direction` | ° | Dominant wave direction |
| `wave_period` | s | Dominant wave period |
| `swell_wave_height` | m | Swell wave height |
| `swell_wave_direction` | ° | Swell direction |
| `swell_wave_period` | s | Swell period |
| `swell_wave_direction_degrees` | ° | Swell direction (degrees) |
| `chop_wave_height` | m | Wind chop wave height |
| `chop_wave_direction` | ° | Wind chop direction |
| `sea_surface_temperature` | °C / °F | Sea surface temp |
| `sea_ice` | kg/m² | Sea ice mass concentration |
| `current_speed` | cm/s | Ocean current speed |
| `current_direction` | ° | Ocean current direction |

### Example

```bash
curl "https://api.open-meteo.com/v1/marine-forecast?latitude=40.0&longitude=-30.0&hourly=wave_height,swell_wave_height,sea_surface_temperature&timezone=auto"
```

---

## Climate Change API

**Base URL:** `https://climate-api.open-meteo.com/v1/climate`

Downscaled CMIP6 models, bias-corrected to ERA5. Covers 1950–2050.

### Climate Models (Scenarios)

| Model | Description |
|---|---|
| `IPCC-Scenario-1-1-2-6` | SSP1-2.6 (low emissions, strong mitigation) |
| `IPCC-Scenario-1-2-6` | SSP1-2.6 (alternative notation) |
| `IPCC-Scenario-2-6` | SSP2-6 (intermediate) |
| `IPCC-Scenario-5-8-5` | SSP5-8.5 (high emissions, no mitigation) |

### Parameters

| Parameter | Values | Description |
|---|---|---|
| `climate_model` | model name | Required |
| `start_date` | YYYY-MM-DD | Required, 1950–2050 |
| `end_date` | YYYY-MM-DD | Required |
| `daily` | comma-separated | Daily variables (same as forecast API) |
| `hourly` | comma-separated | Hourly variables |

### Example

```bash
curl "https://climate-api.open-meteo.com/v1/climate?latitude=52.52&longitude=13.41&start_date=2050-01-01&end_date=2050-12-31&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&climate_model=IPCC-Scenario-5-8-5"
```

---

## Elevation API

**Base URL:** `https://api.open-meteo.com/v1/elevation`

Terrain elevation lookup using 90m resolution DEM.

### Parameters

| Parameter | Values | Description |
|---|---|---|
| `latitude` | float | Required |
| `longitude` | float | Required |
| `model` | `aster`, `copernicus`, `ecmwf` | DEM source (default: auto) |

### Example

```bash
# Single point
curl "https://api.open-meteo.com/v1/elevation?latitude=52.52&longitude=13.41"

# Multiple points
curl "https://api.open-meteo.com/v1/elevation?latitude=52.52,48.86&longitude=13.41,2.35"
```

### Response

```json
{
  "results": [
    {"elevation": 44.0, "latitude": 52.52, "longitude": 13.41, "unit": "m"}
  ]
}
```

---

## Flood Forecast API

**Base URL:** `https://flood-api.open-meteo.com/v1/flood-forecast`

River discharge forecasts using the Copernicus GloFAS hydrological model.

### Parameters

| Parameter | Values | Description |
|---|---|---|
| `latitude` | float | Required |
| `longitude` | float | Required |
| `forecast_days` | 1–20 | Number of forecast days |
| `daily` | `river_discharge` | River discharge variable |

### Example

```bash
curl "https://flood-api.open-meteo.com/v1/flood-forecast?latitude=52.52&longitude=13.41&forecast_days=7&daily=river_discharge"
```

---

## Seasonal Forecast API

**Base URL:** `https://seasonal-api.open-meteo.com/v1/seasonal`

ECMWF SEAS5 ensemble forecasts, up to 9 months ahead.

### Parameters

| Parameter | Values | Description |
|---|---|---|
| `latitude` | float | Required |
| `longitude` | float | Required |
| `daily` | comma-separated | Daily variables |
| `seasonal` | comma-separated | Seasonal probabilistic data |

### Daily Variables

`temperature_2m_max`, `temperature_2m_min`, `temperature_2m_mean`, `precipitation_sum`, `shortwave_radiation_sum`, `wind_speed_10m_max`.

### Seasonal Variables

`temperature_2m_max`, `temperature_2m_min`, `precipitation_sum` — returns ensemble spread (min, max, median, percentiles).

### Example

```bash
curl "https://seasonal-api.open-meteo.com/v1/seasonal?latitude=52.52&longitude=13.41&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
```

---

## Geocoding API

**Base URL:** `https://geocoding-api.open-meteo.com/v1/search`

Convert place names to coordinates.

### Parameters

| Parameter | Values | Description |
|---|---|---|
| `name` | string | Required, ≥ 3 characters |
| `count` | 1–100 | Max results (default: 10) |
| `language` | `en`, `de`, `fr`, `es`, `it`, `pt`, `ru`, `tr`, `hi` | Language |
| `country_codes` | ISO 3166-1 alpha-2 | Filter by country |
| `boundingbox` | south,west,north,east | Bounding box |

### Feature Codes

| Code | Type |
|---|---|
| `PPL` | Populated place |
| `PPLC` | Capital |
| `PPLA` | Admin center |
| `PPLX` | Seat of a government entity |
| `ADM1` | Admin division 1 |
| `ADM2` | Admin division 2 |
| `ST` | State/province |
| `CTR` | Country |
| `STR` | Street |

### Example

```bash
# Search by name
curl "https://geocoding-api.open-meteo.com/v1/search?name=Berlin&count=1&language=en"

# Search with country filter
curl "https://geocoding-api.open-meteo.com/v1/search?name=Paris&country_codes=FR&count=5"

# Search with bounding box
curl "https://geocoding-api.open-meteo.com/v1/search?name=Springfield&boundingbox=39.7,-89.7,40.0,-89.5"
```

### Reverse Geocoding

**Base URL:** `https://geocoding-api.open-meteo.com/v1/reverse`

```bash
curl "https://geocoding-api.open-meteo.com/v1/reverse?latitude=52.52&longitude=13.41&count=1"
```
