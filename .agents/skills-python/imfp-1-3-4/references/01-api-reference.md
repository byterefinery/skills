# API Reference

## Discovery Functions

### `imf_databases(times=3) -> DataFrame`

List all IMF database IDs and descriptions available through the API.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `times` | `int` | `3` | Maximum number of API request attempts |

Returns a DataFrame with columns:

| Column | Type | Description |
|---|---|---|
| `database_id` | `str` | Short ID code (e.g., `"PPI"`, `"BOP"`, `"IFS"`) |
| `description` | `str` | Human-readable name of the database |

Typically returns ~71 databases.

### `imf_parameters(database_id, times=2) -> dict[str, DataFrame]`

Get all filter parameters and their valid input codes for a database.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `database_id` | `str` | — | Database ID from `imf_databases()` |
| `times` | `int` | `2` | Maximum number of API request attempts per parameter |

Returns a dict mapping parameter names to DataFrames. Each DataFrame has:

| Column | Type | Description |
|---|---|---|
| `input_code` | `str` | The code to use in API requests |
| `description` | `str` | Human-readable description of the code |

Raises `ValueError` if `database_id` is invalid.

### `imf_parameter_defs(database_id, times=3, inputs_only=True) -> DataFrame`

Get text descriptions of input parameters for a database.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `database_id` | `str` | — | Database ID from `imf_databases()` |
| `times` | `int` | `3` | Maximum number of API request attempts |
| `inputs_only` | `bool` | `True` | If `False`, also include output variables and time dimensions |

Returns a DataFrame with columns:

| Column | Type | Description |
|---|---|---|
| `parameter` | `str` | Lowercased parameter name |
| `description` | `str \| None` | Text description of the parameter |

## Data Retrieval

### `imf_dataset(database_id, parameters=None, start_year=None, end_year=None, return_raw=False, print_url=False, times=3, include_metadata=False, **kwargs) -> DataFrame | dict | tuple`

Download a data series from the IMF.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `database_id` | `str` | — | Database ID from `imf_databases()` |
| `parameters` | `dict[str, DataFrame] \| None` | `None` | Pre-filtered parameters dict from `imf_parameters()`. Mutually exclusive with `**kwargs` dimension filters |
| `start_year` | `int \| str \| None` | `None` | Four-digit start year (e.g., `2000` or `"2000"`) |
| `end_year` | `int \| str \| None` | `None` | Four-digit end year |
| `return_raw` | `bool` | `False` | Return raw JSON dict instead of parsed DataFrame |
| `print_url` | `bool` | `False` | Print the full API URL used (useful for debugging) |
| `times` | `int` | `3` | Maximum number of API request attempts |
| `include_metadata` | `bool` | `False` | Return `(metadata_dict, data)` tuple |
| `**kwargs` | `str \| list[str]` | — | Dimension filters. Key = parameter name (e.g., `frequency`, `country`), value = code or list of codes |

Return types depend on flags:

| `return_raw` | `include_metadata` | Return type |
|---|---|---|
| `False` | `False` | `DataFrame` |
| `False` | `True` | `tuple[dict, DataFrame]` |
| `True` | `False` | `dict` (raw JSON) |
| `True` | `True` | `tuple[dict, dict]` |

DataFrame columns (lowercased):

| Column | Type | Description |
|---|---|---|
| `time_period` | `str` | Period in format `YYYY-FF` (e.g., `"2020-Q1"`, `"2020-M06"`) |
| `obs_value` | `float \| None` | Observation value; `None` for missing/flagged data |
| *dimension columns* | `str` | One column per series dimension (e.g., `frequency`, `country`, `indicator`) |

Raises `ValueError` if no data matches the filters.

## Admin Functions

### `set_imf_app_name(name="imfp") -> None`

Set the IMF application name (stored as `IMF_APP_NAME` environment variable).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | `"imfp"` | Unique application name, max 255 chars, no control characters |

Raises `ValueError` if name is >255 chars or contains control characters. Warns if name is `"imfp"` or empty.

### `set_imf_wait_time(wait_time=1.5) -> None`

Set minimum wait time between API requests (stored as `IMF_WAIT_TIME` environment variable).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `wait_time` | `int \| float` | `1.5` | Wait time in seconds, must be >= 0 |

Raises `ValueError` if `wait_time < 0`.

## Dimension Filter Aliases

imfp auto-maps these common aliases to dataset-specific keys:

| Alias | Maps to |
|---|---|
| `freq`, `frequency` | `frequency` or `freq` (whichever the dataset uses) |
| `ref_area`, `refarea`, `ref-area`, `country`, `geo` | `country` or `ref_area` (whichever the dataset uses) |

## Internal Utilities (prefixed with `_`, not for direct use)

- `_imf_get(url, headers, timeout)` — rate-limited GET request wrapper
- `_min_wait_time_limited(default_wait_time)` — decorator for rate-limited functions
- `_download_parse(resource_or_url, times, base_url, query_params)` — download + parse JSON with retries
- `_imf_metadata(database_id, times)` — fetch metadata for a dataset
- `_imf_dimensions(database_id, times, inputs_only)` — fetch dimension codes for a database
