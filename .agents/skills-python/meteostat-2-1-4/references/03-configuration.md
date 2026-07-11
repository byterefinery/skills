# Configuration

Meteostat 2.1.4 configuration via `ms.config` and environment variables.

## Accessing Configuration

```python
import meteostat as ms

# Read config
print(ms.config.cache_directory)
print(ms.config.network_timeout)

# Modify config
ms.config.cache_directory = "/path/to/cache"
ms.config.cache_enable = False
ms.config.network_timeout = 60
```

## General Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `block_large_requests` | `True` | Block requests with too many stations |

## Cache Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `cache_enable` | `True` | Enable/disable HTTP response caching |
| `cache_directory` | `~/.meteostat/cache/` | Directory for cached data files |
| `cache_ttl` | `TTL.MONTH` (2592000s) | Cache time-to-live in seconds |
| `cache_autoclean` | `True` | Automatically remove stale cache entries |

### Cache TTL Constants

- `TTL.HOUR` — 3600 seconds
- `TTL.DAY` — 86400 seconds
- `TTL.WEEK` — 604800 seconds
- `TTL.MONTH` — 2592000 seconds

### Purging Cache

```python
import meteostat as ms
ms.purge()  # Clear all cached data
```

## Network Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `network_proxies` | `None` | Dict of proxy URLs by scheme |
| `network_timeout` | `30` | Request timeout in seconds |
| `network_max_retries` | `3` | Maximum retry attempts on failure |

## Station Database Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `stations_db_ttl` | `TTL.WEEK` | Cache TTL for the stations SQLite database |
| `stations_db_endpoints` | See below | List of URLs to fetch the database from |
| `stations_db_file` | `~/.meteostat/stations.db` | Local path for the cached database |

Default endpoints:
1. `https://data.meteostat.net/stations.db`
2. `https://raw.githubusercontent.com/meteostat/weather-stations/master/stations.db`

## Interpolation Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `lapse_rate_parameters` | `[TEMP, TMIN, TMAX]` | Parameters that receive lapse rate correction during interpolation |

## Provider-Specific Settings

### Meteostat Endpoints

| Setting | Default |
|---------|---------|
| `include_model_data` | `True` |
| `hourly_endpoint` | `https://data.meteostat.net/hourly/{year}/{station}.csv.gz` |
| `daily_endpoint` | `https://data.meteostat.net/daily/{year}/{station}.csv.gz` |
| `monthly_endpoint` | `https://data.meteostat.net/monthly/{station}.csv.gz` |

### DWD Settings

| Setting | Default |
|---------|---------|
| `dwd_ftp_host` | `opendata.dwd.de` |
| `dwd_hourly_modes` | `None` (auto) |
| `dwd_daily_modes` | `None` (auto) |
| `dwd_climat_modes` | `None` (auto) |
| `dwd_mosmix_staleness_threshold` | `43200` (12 hours) |

### NOAA Settings

| Setting | Default |
|---------|---------|
| `aviationweather_endpoint` | `https://aviationweather.gov/api/data/metar?...` |
| `aviationweather_user_agent` | `None` |

### Met.no Settings

| Setting | Default |
|---------|---------|
| `metno_forecast_endpoint` | `https://api.met.no/weatherapi/locationforecast/2.0/compact?...` |
| `metno_user_agent` | `None` (required by Met.no if set) |

### GSA Settings

| Setting | Default |
|---------|---------|
| `gsa_api_base_url` | `https://dataset.api.hub.geosphere.at/v1` |

## Environment Variables

All config settings can be set via environment variables with the `MS_` prefix:

```bash
export MS_CACHE_ENABLE=false
export MS_CACHE_TTL=86400
export MS_NETWORK_TIMEOUT=60
export MS_STATIONS_DB_FILE="/custom/path/stations.db"
export MS_METNO_USER_AGENT="my-app@example.com"
```

- String values are used directly (no JSON parsing)
- Non-string values (bool, int, list, dict) use JSON parsing
- Invalid values are logged and skipped (not raised as errors)

## Loading Custom Environment

```python
# Load from environment (default prefix: MS_)
ms.config.load_env()

# Get the env var name for a config key
ms.config.get_env_name("cache_directory")  # "MS_CACHE_DIRECTORY"
```
