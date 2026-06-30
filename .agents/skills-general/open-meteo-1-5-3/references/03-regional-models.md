# Regional Weather Models

Each regional model has its own base URL and coverage area. Use the regional endpoint when you need data from a specific model rather than the auto-selected best model.

## DWD ICON (Germany)

**URL:** `https://dwd-api.open-meteo.com/v1/forecast`

**Coverage:** Europe and Africa

**Models:**
- `icon_global` — 0.11° / 13 km global resolution
- `icon_eu` — 0.025° / 2.2 km regional (Europe)
- `icon_d2` — 0.025° / 2.2 km regional (Germany)
- `icon_uve` — 0.025° / 2.2 km regional (Germany, UV)

**Parameters:** Same as standard forecast API.

## ECMWF IFS (Europe)

**URL:** `https://ecmwf-api.open-meteo.com/v1/forecast`

**Coverage:** Global

**Models:**
- `ifs` — 0.1° / 11 km global resolution

**Parameters:** Same as standard forecast API.

## NOAA GFS / HRRR (North America)

**URL:** `https://gfs-api.open-meteo.com/v1/forecast`

**Coverage:** Global (GFS), North America (HRRR)

**Models:**
- `gfs` — 0.25° / 25 km global resolution
- `hrrr` — 0.03° / 3 km regional (North America)

**Parameters:** Same as standard forecast API.

## MeteoFrance AROME / ARPEGE (France)

**URL:** `https://meteofrance-api.open-meteo.com/v1/forecast`

**Coverage:** Europe (AROMÉ), France (ARPEGE)

**Models:**
- `arome_france` — 1.3 km regional (France)
- `arome_europe` — 1.3 km regional (Europe)
- `arpege` — 10 km regional (France)
- `arome_france_marine` — 1.3 km marine (France)
- `arome_france_marine_2` — 1.3 km marine (France, alt)
- `arome_europe_marine` — 1.3 km marine (Europe)

**Parameters:** Same as standard forecast API.

## JMA (Japan)

**URL:** `https://jma-api.open-meteo.com/v1/forecast`

**Coverage:** Global

**Models:**
- `gsm` — 0.2° / 22 km global spectral model

**Parameters:** Same as standard forecast API.

## GEM / HRDPS (Canada)

**URL:** `https://gem-api.open-meteo.com/v1/forecast`

**Coverage:** Global (GEM), North America (HRDPS)

**Models:**
- `gem` — 0.15° / 15 km global resolution
- `hrdps` — 2.5 km regional (North America)

**Parameters:** Same as standard forecast API.

## MET Norway (Norway)

**URL:** `https://metno-api.open-meteo.com/v1/forecast`

**Coverage:** Global

**Models:**
- `arome` — 2.5 km regional (Norway)
- `arome_arktik` — 2.5 km regional (Arctic)
- `rr` — 2.5 km regional (Norway, radar)
- `rr_arktik` — 2.5 km regional (Arctic, radar)
- `aladin` — 2.5 km regional (Europe)
- `ara` — 2.5 km regional (Arctic)

**Parameters:** Same as standard forecast API.

## Model Selection

Use the `models` parameter on any forecast endpoint to request specific models:

```
https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m&models=icon_eu,gfs
```

When multiple models are requested, the response contains separate data for each model. Use the `model` field in the response to identify which model each data block came from.

## Auto-Selection

The default `api.open-meteo.com` endpoint automatically selects the best available model for the given location. The selection logic prioritizes:
1. Highest resolution model covering the location
2. Most recent forecast run
3. Model with best historical accuracy for the region
