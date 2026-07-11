# Parameters

Full reference of all meteorological parameters supported by Meteostat 2.1.4.

## Parameter Enum

All parameters are accessed via `ms.Parameter.<NAME>`.

| Parameter | Description | Unit | Hourly | Daily | Monthly | Normals |
|-----------|-------------|------|--------|-------|---------|---------|
| `TEMP` | Air temperature (mean) | °C | ✓ | ✓ | ✓ | ✓ |
| `TMIN` | Minimum air temperature | °C | — | ✓ | ✓ | ✓ |
| `TMAX` | Maximum air temperature | °C | — | ✓ | ✓ | ✓ |
| `TXMN` | Absolute minimum temperature | °C | — | — | ✓ | ✓ |
| `TXMX` | Absolute maximum temperature | °C | — | — | ✓ | ✓ |
| `DWPT` | Dew point | °C | ✓ | — | — | — |
| `PRCP` | Total precipitation | mm | ✓ | ✓ | ✓ | ✓ |
| `PDAY` | Days with precipitation ≥ 1mm | count | — | — | ✓ | — |
| `WDIR` | Wind direction | ° | ✓ | — | — | — |
| `WSPD` | Wind speed (mean) | km/h | ✓ | ✓ | — | — |
| `WPGT` | Peak wind gust | km/h | ✓ | ✓ | — | — |
| `RHUM` | Relative humidity | % | ✓ | ✓ | ✓ | ✓ |
| `PRES` | Air pressure at MSL | hPa | ✓ | ✓ | ✓ | — |
| `SNWD` | Snow depth on ground | cm | ✓ | ✓ | — | — |
| `SNOW` | Snowfall | cm | ✓ | — | — | — |
| `TSUN` | Sunshine duration | min | ✓ | ✓ | ✓ | ✓ |
| `SGHI` | Global horizontal irradiance | — | ✓ | ✓ | — | — |
| `SDNI` | Direct normal irradiance | — | ✓ | ✓ | — | — |
| `SDHI` | Diffuse horizontal irradiance | — | ✓ | ✓ | — | — |
| `CLDC` | Cloud cover | okta | ✓ | ✓ | — | — |
| `VSBY` | Visibility | m | ✓ | — | — | — |
| `COCO` | Weather condition code | code | ✓ | — | — | — |

## Default Parameters by Granularity

When no `parameters` argument is given, each granularity uses these defaults:

### Hourly
`TEMP`, `RHUM`, `PRCP`, `SNWD`, `WDIR`, `WSPD`, `WPGT`, `PRES`, `TSUN`, `CLDC`, `COCO`

### Daily
`TEMP`, `TMIN`, `TMAX`, `RHUM`, `PRCP`, `SNWD`, `WSPD`, `WPGT`, `PRES`, `TSUN`, `CLDC`

### Monthly
`TEMP`, `TMIN`, `TMAX`, `TXMN`, `TXMX`, `PRCP`, `PRES`, `TSUN`

### Normals
Same as monthly defaults (normals is computed from monthly data).

## Aggregation Behavior

When computing normals or aggregating across time:

- **Mean**: `TEMP`, `TMIN`, `TMAX`, `RHUM`, `PRES`, `WSPD`, `CLDC`, `VSBY`
- **Sum**: `PRCP`, `SNOW`, `TSUN`
- **Max**: `WPGT`, `TXMX`
- **Min**: `TXMN`
- **No aggregation (point-in-time)**: `WDIR`, `SNWD`, `COCO`, `DWPT`

## Validation Ranges

Parameters are validated during `fetch(clean=True)` and `validate()`:

- Temperature (`TEMP`, `TMIN`, `TMAX`): -100 to 65 °C
- Humidity (`RHUM`): 0 to 100 %
- Precipitation: hourly 0-350mm, daily 0-2000mm, monthly 0-10000mm
- Pressure: 600 to 1200 hPa
- Wind speed: 0 to 750 km/h
- Visibility: 0 to 50000 m
- Snow depth: 0 to 1000 cm
- Sunshine: 0 to 1440 min (daily), 0 to 14400 min (monthly)
