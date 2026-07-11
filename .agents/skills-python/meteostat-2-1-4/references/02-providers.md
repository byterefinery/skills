# Providers

Data providers available in Meteostat 2.1.4.

## Provider Categories

### Meteostat Default Providers
These aggregate data from multiple sources and are the default when no `providers` argument is given:

| Provider Enum | Description |
|---------------|-------------|
| `Provider.DAILY` | Default daily (aggregates GHCND, CLIMAT, DWD, ECCC, GSA) |
| `Provider.HOURLY` | Default hourly (aggregates ISD-Lite, METAR, DWD, ECCC, GSA) |
| `Provider.MONTHLY` | Default monthly (aggregates GHCND, CLIMAT, DWD, ECCC, GSA) |
| `Provider.DAILY_DERIVED` | Meteostat's derived daily data (model-enhanced) |
| `Provider.MONTHLY_DERIVED` | Meteostat's derived monthly data (model-enhanced) |

### National Weather Service Providers

#### NOAA (USA)
| Provider | Granularity | Notes |
|----------|-------------|-------|
| `Provider.ISD_LITE` | Hourly | Integrated Surface Database Lite |
| `Provider.METAR` | Hourly | Aviation routine weather reports |
| `Provider.GHCND` | Daily/Monthly | Global Historical Climatology Network Daily |

#### DWD (Germany)
| Provider | Granularity | Notes |
|----------|-------------|-------|
| `Provider.DWD_HOURLY` | Hourly | DWD hourly observations |
| `Provider.DWD_DAILY` | Daily | DWD daily climate data |
| `Provider.DWD_MONTHLY` | Monthly | DWD monthly climate data |
| `Provider.DWD_POI` | Hourly | DWD point observations |
| `Provider.DWD_MOSMIX` | Hourly | DWD MOSMIX forecasts |
| `Provider.CLIMAT` | Daily | DWD CLIMAT monthly reports |

#### ECCC (Canada)
| Provider | Granularity | Notes |
|----------|-------------|-------|
| `Provider.ECCC_HOURLY` | Hourly | Environment Canada hourly |
| `Provider.ECCC_DAILY` | Daily | Environment Canada daily |
| `Provider.ECCC_MONTHLY` | Monthly | Environment Canada monthly |

#### GSA (Austria)
| Provider | Granularity | Notes |
|----------|-------------|-------|
| `Provider.GSA_HOURLY` | Hourly | GeoSphere Austria hourly |
| `Provider.GSA_SYNOP` | Hourly | GeoSphere Austria synoptic |
| `Provider.GSA_DAILY` | Daily | GeoSphere Austria daily |
| `Provider.GSA_MONTHLY` | Monthly | GeoSphere Austria monthly |

#### Met.no (Norway)
| Provider | Granularity | Notes |
|----------|-------------|-------|
| `Provider.METNO_FORECAST` | Hourly | Norwegian Meteorological Institute forecasts |

## Provider Priority and Grade

Providers have a priority (25=highest to 0=none) and a quality grade:

- **Grade.RECORD (4)** — Official records (GHCND, CLIMAT, DWD monthly)
- **Grade.OBSERVATION (3)** — Direct observations (ISD-Lite, METAR, DWD hourly)
- **Grade.ANALYSIS (2)** — Analyzed/derived data (Meteostat derived)
- **Grade.FORECAST (1)** — Forecast data (MOSMIX, Met.no)

Higher priority providers are preferred when multiple providers have data for the same station/parameter.

## Using Providers

```python
import meteostat as ms

# Use default providers (aggregated)
ts = ms.daily("10637", start, end)

# Use specific provider
ts = ms.hourly("10637", start, end, providers=[ms.Provider.DWD_HOURLY])

# Use multiple providers
ts = ms.daily("10637", start, end, providers=[ms.Provider.GHCND, ms.Provider.CLIMAT])

# Specify parameters when using specific providers (important!)
ts = ms.hourly("10637", start, end,
    providers=[ms.Provider.DWD_HOURLY],
    parameters=[ms.Parameter.TEMP, ms.Parameter.RHUM])
```

## Provider Selection Strategy

- **For general use**: omit `providers` and let the default aggregation handle it
- **For a specific country**: use the national provider (DWD for Germany, ECCC for Canada, etc.)
- **For forecasts**: use `DWD_MOSMIX` or `METNO_FORECAST`
- **For highest quality**: use `GHCND` (daily/monthly) or `ISD_LITE` (hourly)
- **When using specific providers**: always specify `parameters` explicitly to avoid fetching unnecessary data

## License Information

Access `ts.licenses` after fetching to get the list of applicable licenses. Data is generally CC BY 4.0. Use `ts.attribution` for the proper attribution string and `ts.commercial` to check if commercial use is allowed.
