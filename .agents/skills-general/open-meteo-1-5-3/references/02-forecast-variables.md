# Forecast Variables

## Current Weather Variables

| Variable | Unit | Description |
|---|---|---|
| `temperature_2m` | °C / °F | Air temperature at 2m |
| `relative_humidity_2m` | % | Relative humidity at 2m |
| `dew_point_2m` | °C / °F | Dew point at 2m |
| `apparent_temperature` | °C / °F | Perceived temperature |
| `precipitation` | mm / inch | Total precipitation |
| `rain` | mm / inch | Rain only |
| `showers` | mm / inch | Showers only |
| `snowfall` | cm / inch | Snow depth equivalent |
| `weather_code` | WMO code | Weather condition (0–99) |
| `cloud_cover` | % | Total cloud cover |
| `cloud_cover_low` | % | Low-level clouds |
| `cloud_cover_mid` | % | Mid-level clouds |
| `cloud_cover_high` | % | High-level clouds |
| `pressure_msl` | hPa | Mean sea level pressure |
| `surface_pressure` | hPa | Surface pressure |
| `wind_speed_10m` | km/h, m/s, mph, kn | Wind speed at 10m |
| `wind_direction_10m` | ° | Wind direction at 10m |
| `wind_gusts_10m` | km/h, m/s, mph, kn | Wind gusts at 10m |
| `shortwave_radiation` | W/m² | Incoming shortwave radiation |
| `direct_radiation` | W/m² | Direct solar radiation |
| `diffuse_radiation` | W/m² | Diffuse solar radiation |
| `direct_normal_irradiance` | W/m² | DNI |
| `diffuse_horizontal_radiation` | W/m² | DHI |
| `global_tilted_irradiance` | W/m² | GHI on tilted surface |
| `uv_index` | — | UV index |
| `uv_index_clear_sky` | — | UV index if clear sky |
| `is_day` | 0/1 | Daytime indicator |
| `visibility` | m | Visibility distance |
| `evapotranspiration` | mm | Evapotranspiration |
| `et0_fao_evapotranspiration` | mm | Reference evapotranspiration |
| `vapour_pressure_deficit` | kPa | VPD |
| `soil_temperature_0cm` | °C / °F | Soil temperature at surface |
| `soil_temperature_6cm` | °C / °F | Soil temperature at 6cm |
| `soil_temperature_18cm` | °C / °F | Soil temperature at 18cm |
| `soil_temperature_54cm` | °C / °F | Soil temperature at 54cm |
| `soil_moisture_0_to_1cm` | % | Volumetric soil moisture 0–1cm |
| `soil_moisture_1_to_3cm` | % | Volumetric soil moisture 1–3cm |
| `soil_moisture_3_to_9cm` | % | Volumetric soil moisture 3–9cm |
| `soil_moisture_9_to_27cm` | % | Volumetric soil moisture 9–27cm |
| `soil_moisture_27_to_81cm` | % | Volumetric soil moisture 27–81cm |
| `soil_moisture_81_to_189cm` | % | Volumetric soil moisture 81–189cm |
| `snow_depth` | cm / inch | Snow depth on ground |
| `freezing_rain` | mm / inch | Freezing rain |
| `ice_pellets` | mm / inch | Ice pellets |
| `runoff` | mm / inch | Surface runoff |
| `precipitation_type` | 0/1/2 | 0=liquid, 1=mixed, 2=solid |

## Hourly Variables (Extended)

All current variables plus:

| Variable | Unit | Description |
|---|---|---|
| `temperature_2m_min` | °C / °F | Minimum temperature in hour |
| `temperature_2m_max` | °C / °F | Maximum temperature in hour |
| `precipitation_probability` | % | Probability of precipitation |
| `rain_probability` | % | Probability of rain |
| `snowfall_probability` | % | Probability of snowfall |
| `freezing_rain_probability` | % | Probability of freezing rain |
| `ice_pellets_probability` | % | Probability of ice pellets |
| `thunderstorm_probability` | % | Probability of thunderstorm |
| `wind_speed_20m` through `wind_speed_200m` | km/h, m/s, mph, kn | Wind at various heights |
| `wind_direction_20m` through `wind_direction_200m` | ° | Wind direction at various heights |
| `temperature_20m` through `temperature_200m` | °C / °F | Temperature at various heights |

## Daily Aggregate Variables

| Variable | Unit | Description |
|---|---|---|
| `temperature_2m_max` | °C / °F | Daily maximum |
| `temperature_2m_min` | °C / °F | Daily minimum |
| `temperature_2m_mean` | °C / °F | Daily mean |
| `apparent_temperature_max` | °C / °F | Max apparent temp |
| `apparent_temperature_min` | °C / °F | Min apparent temp |
| `apparent_temperature_mean` | °C / °F | Mean apparent temp |
| `sunrise` | ISO 8601 | Sunrise time |
| `sunset` | ISO 8601 | Sunset time |
| `uv_index_max` | — | Max UV index |
| `uv_index_clear_sky_max` | — | Max UV if clear |
| `precipitation_sum` | mm / inch | Daily total precipitation |
| `rain_sum` | mm / inch | Daily rain total |
| `showers_sum` | mm / inch | Daily showers total |
| `snowfall_sum` | cm / inch | Daily snowfall total |
| `precipitation_hours` | h | Hours with precipitation |
| `precipitation_probability_max` | % | Max hourly precip probability |
| `weather_code_max` | WMO code | Dominant weather code |
| `wind_speed_10m_max` | km/h, m/s, mph, kn | Max wind speed |
| `wind_gusts_10m_max` | km/h, m/s, mph, kn | Max wind gusts |
| `wind_direction_10m_dominant` | ° | Dominant wind direction |
| `shortwave_radiation_sum` | Wh/m² | Daily radiation total |
| `et0_fao_evapotranspiration` | mm | Daily reference ET |
| `cloud_cover_mean` | % | Mean cloud cover |
| `pressure_msl_mean` | hPa | Mean sea level pressure |
| `visibility_mean` | m | Mean visibility |

## WMO Weather Codes

| Code | Condition |
|---|---|
| 0 | Clear sky |
| 1 | Mainly clear |
| 2 | Partly cloudy |
| 3 | Overcast |
| 45 | Fog |
| 48 | Depositing rime fog |
| 51–55 | Light/moderate/heavy drizzle |
| 61–65 | Light/moderate/heavy rain |
| 66–67 | Freezing rain |
| 71–75 | Light/moderate/heavy snowfall |
| 77 | Snow grains |
| 80–82 | Light/moderate/heavy rain showers |
| 85–86 | Light/heavy snow showers |
| 95 | Thunderstorm |
| 96–99 | Thunderstorm with hail |

## 15-Minutely Variables

Available for supported regions (Europe, North America). Same variable names with `_15min` suffix: `temperature_2m_15min`, `relative_humidity_2m_15min`, `wind_speed_10m_15min`, `shortwave_radiation_15min`, `direct_radiation_15min`, `direct_normal_irradiance_15min`, `diffuse_radiation_15min`, `global_tilted_irradiance_15min`, `sunshine_duration_15min`, `precipitation_15min`, `snowfall_15min`, `weather_code_15min`, `wind_gusts_10m_15min`, `wind_speed_80m_15min`, `wind_direction_10m_15min`, `wind_direction_80m_15min`, `apparent_temperature_15min`, `dew_point_2m_15min`.
